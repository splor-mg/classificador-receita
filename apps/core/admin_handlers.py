"""
Handlers para fluxos de Admin.

BitemporalChangeHandler — coordena fluxo de confirmação bitemporal (sobrescrever / nova vigência).
"""
from datetime import date, timedelta
from typing import Any, Dict, List, Tuple
import logging

from django.template.response import TemplateResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages

from apps.core.bitemporal_registry import get_sentinela_date
from apps.core.domain_choices import ORGAOS_ENTIDADES_GROUPED_CHOICES

VIGENCIA_FIELDS = {"data_vigencia_inicio", "data_vigencia_fim"}


class BitemporalChangeHandler:
    """
    Handler que gerencia o fluxo de confirmação bitemporal no Admin.

    Responsabilidades:
    - Detectar se houve alteração no form.
    - Renderizar página de confirmação com diffs separados (Atributos Gerais vs Vigência).
    - Calcular preview de como ficarão os registros em cada estratégia.
    - Chamar bitemporal_update para aplicar a atualização.
    - Não realiza export — isso é responsabilidade do AutoExportAdminMixin.
    """

    def __init__(self, admin_instance):
        self.admin = admin_instance
        self.model = admin_instance.model
        self.logger = logging.getLogger(__name__)

    def _get_business_id_and_name(self, obj: Any, form) -> Dict[str, Any]:
        """
        Tenta identificar automaticamente campos de ID e Nome de negócio
        seguindo o padrão <recurso>_id e <recurso>_nome, para exibição
        de um resumo do registro na tela de confirmação.
        """
        id_field = None
        name_field = None

        for field in self.model._meta.get_fields():
            # Ignora relacionamentos reversos e many-to-many implícitos.
            if not hasattr(field, "name"):
                continue
            if getattr(field, "many_to_many", False) or getattr(field, "one_to_many", False):
                continue
            fname = field.name
            if fname.endswith("_id") and id_field is None:
                id_field = field
            if fname.endswith("_nome") and name_field is None:
                name_field = field

        def field_info(f):
            if not f:
                return None, None
            label = getattr(f, "verbose_name", f.name).capitalize()
            if hasattr(form, "initial") and f.name in form.initial:
                value = form.initial.get(f.name)
            else:
                value = getattr(obj, f.name, None)
            return label, value

        id_label, id_value = field_info(id_field)
        name_label, name_value = field_info(name_field)

        return {
            "resource_id_label": id_label,
            "resource_id_value": id_value,
            "resource_name_label": name_label,
            "resource_name_value": name_value,
        }

    def _build_diffs(self, form, changed_data: List[str]) -> Tuple[List[Dict], List[Dict]]:
        """Separa diffs em atributos gerais e vigência."""
        general_diffs = []
        vigencia_diffs = []

        for field in changed_data:
            field_meta = self.model._meta.get_field(field)
            label = field_meta.verbose_name.capitalize()
            old = form.initial.get(field)
            new = form.cleaned_data.get(field)

            choices = None
            grouped_choices = None
            if hasattr(field_meta, 'choices') and field_meta.choices:
                choices = list(field_meta.choices)
                # Para orgao_responsavel, aproveitar metadado de agrupamento
                # para exibir um select mais informativo na tela de confirmação.
                if field == "orgao_responsavel":
                    grouped_choices = ORGAOS_ENTIDADES_GROUPED_CHOICES
            if choices:
                choices_dict = dict(choices)
                label_display = choices_dict.get(old, old)
                if old is not None and label_display is not None and old != label_display:
                    old_display = f"{old} - {label_display}"
                else:
                    old_display = label_display
            else:
                old_display = old

            diff_entry = {
                "field": label,
                "field_name": field,
                "old": old,
                "old_display": old_display,
                "new": new,
                "choices": choices,
                "grouped_choices": grouped_choices,
            }

            if field in VIGENCIA_FIELDS:
                vigencia_diffs.append(diff_entry)
            else:
                general_diffs.append(diff_entry)

        return general_diffs, vigencia_diffs

    def _apply_user_edits(self, request, form) -> Dict[str, Any]:
        """
        Captura valores editados pelo usuário na tela de confirmação.
        
        Prioriza valores editados (edit_field_*, edit_vig_*) sobre os valores
        originais do form.cleaned_data.
        """
        from datetime import datetime

        new_values: Dict[str, Any] = {}

        # Percorre TODOS os campos do form; para aqueles que não têm
        # override edit_field_* usamos o cleaned_data original.
        for field in form.fields.keys():
            if field not in form.cleaned_data:
                continue
            edit_key = f"edit_field_{field}"
            cleaned_val = form.cleaned_data[field]
            if edit_key in request.POST:
                raw_val = request.POST.get(edit_key)
                try:
                    field_obj = self.model._meta.get_field(field)
                except Exception:
                    new_val = raw_val
                else:
                    if hasattr(field_obj, "to_python"):
                        try:
                            new_val = field_obj.to_python(raw_val)
                        except Exception:
                            new_val = raw_val
                    else:
                        new_val = raw_val
                new_values[field] = new_val
                try:
                    self.logger.debug(
                        "BitemporalChangeHandler-apply_user_edits field=%s cleaned=%r raw_post=%r final=%r",
                        field,
                        cleaned_val,
                        raw_val,
                        new_val,
                    )
                except Exception:
                    pass
            else:
                new_values[field] = cleaned_val
        
        for i in range(10):
            inicio_key = f"edit_vig_inicio_{i}"
            fim_key = f"edit_vig_fim_{i}"
            
            if inicio_key in request.POST:
                inicio_str = request.POST.get(inicio_key)
                if inicio_str:
                    try:
                        new_values["data_vigencia_inicio"] = datetime.strptime(
                            inicio_str, "%Y-%m-%d"
                        ).date()
                    except ValueError:
                        pass
            
            if fim_key in request.POST:
                fim_str = request.POST.get(fim_key)
                if fim_str:
                    try:
                        new_values["data_vigencia_fim"] = datetime.strptime(
                            fim_str, "%Y-%m-%d"
                        ).date()
                    except ValueError:
                        pass

        return new_values

    def _compute_vigencia_preview(
        self, obj: Any, form, changed_data: List[str]
    ) -> Dict[str, Any]:
        """
        Calcula preview das vigências para ambas estratégias.

        Retorna dict com:
        - current_vig_inicio: data_vigencia_inicio atual do objeto
        - current_vig_fim: data_vigencia_fim atual do objeto
        - new_vig_inicio: nova data_vigencia_inicio (do form ou 1º jan do ano atual)
        - new_vig_fim: nova data_vigencia_fim (do form ou sentinela)
        - nova_vigencia_preview: lista de registros para estratégia "nova_vigencia"
        - sobrescrever_preview: lista de registros para estratégia "sobrescrever"
        """
        sentinela = get_sentinela_date()
        today = date.today()
        # Padrão histórico: 1º de janeiro do ano corrente para nova vigência.
        first_jan_current_year = date(today.year, 1, 1)

        current_vig_inicio = getattr(obj, "data_vigencia_inicio", None)
        current_vig_fim = getattr(obj, "data_vigencia_fim", None)

        # Se a vigência atual já começa no ano corrente, entender que é
        # mais natural ajustar essa própria vigência (sobrescrever) e,
        # caso o usuário opte mesmo por "Registrar nova vigência", usar
        # o dia atual como sugestão para o início da nova versão.
        current_inicio_year = None
        if current_vig_inicio is not None:
            current_inicio_date = (
                current_vig_inicio.date()
                if hasattr(current_vig_inicio, "date")
                else current_vig_inicio
            )
            current_inicio_year = current_inicio_date.year
        current_vig_inicio_in_current_year = current_inicio_year == today.year

        has_vig_inicio_change = "data_vigencia_inicio" in changed_data
        has_vig_fim_change = "data_vigencia_fim" in changed_data

        # Para a estratégia de nova vigência:
        # - regra geral: propor 1º de janeiro do ano corrente como início da nova versão;
        # - exceção: quando a versão atual já começou no ano corrente,
        #   propor o dia atual como data de início da nova versão.
        if current_vig_inicio_in_current_year:
            new_vig_inicio = today
        else:
            new_vig_inicio = first_jan_current_year

        if has_vig_fim_change:
            new_vig_fim = form.cleaned_data.get("data_vigencia_fim")
        else:
            new_vig_fim = sentinela

        prev_vig_fim_closed = new_vig_inicio - timedelta(days=1)

        nova_vigencia_preview = [
            {
                "version": "Versão 1",
                "vig_inicio": current_vig_inicio,
                "vig_fim": prev_vig_fim_closed,
                "strikethrough": False,
            },
            {
                "version": "Versão 2",
                "vig_inicio": new_vig_inicio,
                "vig_fim": sentinela,
                "strikethrough": False,
            },
        ]

        if has_vig_inicio_change or has_vig_fim_change:
            # Quando já houve alteração explícita de vigência no formulário
            # original, mostramos a versão atual riscada e a nova vigência
            # como segunda linha editável.
            sobrescrever_preview = [
                {
                    "version": "Versão 1",
                    "vig_inicio": current_vig_inicio,
                    "vig_fim": current_vig_fim,
                    "strikethrough": True,
                },
                {
                    "version": "Versão 2",
                    "vig_inicio": form.cleaned_data.get(
                        "data_vigencia_inicio", current_vig_inicio
                    ),
                    "vig_fim": form.cleaned_data.get(
                        "data_vigencia_fim", current_vig_fim
                    ),
                    "strikethrough": False,
                },
            ]
        else:
            # Mesmo que a vigência não tenha sido alterada ainda no
            # formulário inicial, ao escolher "Sobrescrever/ajustar
            # vigência atual" queremos permitir o ajuste direto na tela
            # de confirmação. Por isso exibimos sempre duas linhas:
            # - Versão 1 (atual) riscada, com vigência corrente;
            # - Versão 2 (nova vigência) com os mesmos valores de início
            #   e fim, porém editáveis na confirmação.
            sobrescrever_preview = [
                {
                    "version": "Versão 1",
                    "vig_inicio": current_vig_inicio,
                    "vig_fim": current_vig_fim,
                    "strikethrough": True,
                },
                {
                    "version": "Versão 2",
                    "vig_inicio": current_vig_inicio,
                    "vig_fim": current_vig_fim,
                    "strikethrough": False,
                },
            ]

        return {
            "current_vig_inicio": current_vig_inicio,
            "current_vig_fim": current_vig_fim,
            "new_vig_inicio": new_vig_inicio,
            "new_vig_fim": new_vig_fim,
            "nova_vigencia_preview": nova_vigencia_preview,
            "sobrescrever_preview": sobrescrever_preview,
            "current_vig_inicio_in_current_year": current_vig_inicio_in_current_year,
        }

    def _render_change_form_with_data(self, request, obj, form, object_id):
        """
        Renderiza o formulário de edição com os dados do POST preservados,
        sem salvar no banco. Usado quando usuário clica em Cancel na confirmação.
        """
        from django.contrib.admin.options import IS_POPUP_VAR
        
        opts = self.model._meta
        
        adminform = self.admin.get_changeform_initial_data(request) if hasattr(self.admin, 'get_changeform_initial_data') else {}
        
        fieldsets = self.admin.get_fieldsets(request, obj)
        readonly_fields = self.admin.get_readonly_fields(request, obj)
        
        from django.contrib.admin.helpers import AdminForm
        adminform = AdminForm(
            form,
            list(fieldsets),
            self.admin.get_prepopulated_fields(request, obj) if hasattr(self.admin, 'get_prepopulated_fields') else {},
            readonly_fields,
            model_admin=self.admin,
        )
        
        media = self.admin.media + adminform.media
        
        inline_formsets = []
        
        context = {
            **self.admin.admin_site.each_context(request),
            'title': f'Alterar {opts.verbose_name}',
            'subtitle': str(obj),
            'adminform': adminform,
            'object_id': object_id,
            'original': obj,
            'is_popup': IS_POPUP_VAR in request.POST or IS_POPUP_VAR in request.GET,
            'media': media,
            'inline_admin_formsets': inline_formsets,
            'errors': form.errors,
            'preserved_filters': self.admin.get_preserved_filters(request),
            'add': False,
            'change': True,
            'has_view_permission': self.admin.has_view_permission(request, obj),
            'has_add_permission': self.admin.has_add_permission(request),
            'has_change_permission': self.admin.has_change_permission(request, obj),
            'has_delete_permission': self.admin.has_delete_permission(request, obj),
            'has_editable_inline_admin_formsets': False,
            'has_file_field': True,
            'has_absolute_url': hasattr(obj, 'get_absolute_url'),
            'form_url': '',
            'opts': opts,
            'content_type_id': None,
            'save_as': self.admin.save_as,
            'save_on_top': self.admin.save_on_top,
            'to_field_var': None,
            'is_popup_var': IS_POPUP_VAR,
            'app_label': opts.app_label,
        }
        
        return TemplateResponse(
            request,
            self.admin.change_form_template or [
                f'admin/{opts.app_label}/{opts.model_name}/change_form.html',
                f'admin/{opts.app_label}/change_form.html',
                'admin/change_form.html',
            ],
            context,
        )

    def handle(self, request, object_id, form_url, extra_context):
        """
        Processa o fluxo de confirmação bitemporal.

        Retorna:
        - TemplateResponse se deve mostrar página de confirmação.
        - HttpResponseRedirect após aplicar atualização bitemporal.
        - None se deve seguir fluxo normal do Admin.
        """
        if not object_id or request.method != "POST":
            return None

        obj = self.admin.get_object(request, object_id)
        # Se o usuário não tem permissão de alteração para este objeto
        # (por exemplo, registro inativo tratado pelo mixin de somente leitura),
        # delegamos para o fluxo padrão do Admin, que irá bloquear o POST.
        if not self.admin.has_change_permission(request, obj):
            return None

        form_class = self.admin.get_form(request, obj)
        form = form_class(request.POST, request.FILES, instance=obj)

        if not form.is_valid():
            return None

        edit_vigencia_flag = bool(request.POST.get("_edit_vigencia"))

        # Em fluxos normais, sem alterações não há o que confirmar.
        # Porém, quando o usuário clica em "Editar vigência", queremos
        # abrir a tela de confirmação mesmo que apenas as datas sejam
        # ajustadas na próxima etapa.
        if not form.has_changed() and not edit_vigencia_flag:
            return None

        # Se usuário clicou em Cancel na tela de confirmação, volta para edição
        if request.POST.get("_cancel_confirm"):
            return self._render_change_form_with_data(request, obj, form, object_id)

        strategy = request.POST.get("edit_strategy")

        if not strategy:
            changed_fields: List[str] = list(form.changed_data)

            # Quando o usuário clica no botão "Editar vigência", forçamos
            # a inclusão dos campos de vigência na comparação, mesmo que
            # ainda não tenham sido alterados no formulário inicial. Isso
            # permite que a tela de confirmação apresente o preview e os
            # inputs de data, onde a vigência será de fato ajustada.
            if edit_vigencia_flag:
                for field in VIGENCIA_FIELDS:
                    if field in form.fields and field not in changed_fields:
                        changed_fields.append(field)

            general_diffs, vigencia_diffs = self._build_diffs(form, changed_fields)
            vigencia_preview = self._compute_vigencia_preview(obj, form, changed_fields)

            post_items: List[Tuple[str, str]] = []
            for k in request.POST.keys():
                for v in request.POST.getlist(k):
                    post_items.append((k, v))

            # Persistir snapshot dos valores originais (antes da edição)
            # para comparação na etapa de confirmação. Usamos o prefixo
            # "orig_field_" para não conflitar com outros campos.
            for d in general_diffs + vigencia_diffs:
                field_name = d.get("field_name")
                if not field_name:
                    continue
                orig_key = f"orig_field_{field_name}"
                orig_val = d.get("old")
                # Garantir que o snapshot esteja presente mesmo que já
                # exista alguma chave homônima no POST original.
                post_items.append((orig_key, "" if orig_val is None else str(orig_val)))

            import json
            nova_vigencia_preview_json = json.dumps(
                [
                    {
                        "version": r["version"],
                        "vig_inicio": r["vig_inicio"].isoformat() if r["vig_inicio"] else None,
                        "vig_fim": r["vig_fim"].isoformat() if r["vig_fim"] else None,
                        "strikethrough": r["strikethrough"],
                    }
                    for r in vigencia_preview["nova_vigencia_preview"]
                ]
            )
            sobrescrever_preview_json = json.dumps(
                [
                    {
                        "version": r["version"],
                        "vig_inicio": r["vig_inicio"].isoformat() if r["vig_inicio"] else None,
                        "vig_fim": r["vig_fim"].isoformat() if r["vig_fim"] else None,
                        "strikethrough": r["strikethrough"],
                    }
                    for r in vigencia_preview["sobrescrever_preview"]
                ]
            )

            change_url = reverse(
                f'admin:{self.model._meta.app_label}_{self.model._meta.model_name}_change',
                args=[object_id]
            )

            only_vigencia_changes = not general_diffs
            prefer_sobrescrever_default = bool(
                vigencia_preview.get("current_vig_inicio_in_current_year")
            )

            context = {
                **self.admin.admin_site.each_context(request),
                "title": "Confirmar atualização",
                "opts": self.model._meta,
                "original": obj,
                "object": obj,
                "general_diffs": general_diffs,
                "vigencia_diffs": vigencia_diffs,
                "vigencia_preview": vigencia_preview,
                "nova_vigencia_preview_json": nova_vigencia_preview_json,
                "sobrescrever_preview_json": sobrescrever_preview_json,
                "post_items": post_items,
                "changed_data": form.changed_data,
                "form": form,
                "change_url": change_url,
                "only_vigencia_changes": only_vigencia_changes,
                "prefer_sobrescrever_default": prefer_sobrescrever_default,
                "has_changes_from_initial_form": bool(form.changed_data),
            }
            context.update(self._get_business_id_and_name(obj, form))
            return TemplateResponse(request, "admin/core/bitemporal_confirm.html", context)

        # Segunda etapa: usuário escolheu estratégia e confirmou.
        # Reaplicamos os edits feitos na tela de confirmação e
        # comparamos os valores finais com o snapshot ORIGINAL dos
        # campos (antes de iniciar a edição), não apenas com o estado
        # atual do banco. Isso garante que:
        # - Se o usuário desfizer manualmente as alterações na tela de
        #   confirmação, nenhum registro bitemporal novo será criado;
        # - Se mantiver qualquer alteração em relação ao estado
        #   original, a atualização bitemporal será aplicada.

        # Reconstruir snapshot de valores originais a partir dos
        # campos ocultos "orig_field_*" enviados pela tela de
        # confirmação.
        original_values: Dict[str, Any] = {}
        prefix = "orig_field_"
        for key, value in request.POST.items():
            if not key.startswith(prefix):
                continue
            field_name = key[len(prefix) :]
            try:
                field_obj = self.model._meta.get_field(field_name)
            except Exception:
                original_values[field_name] = value
                continue
            if hasattr(field_obj, "to_python"):
                try:
                    original_values[field_name] = field_obj.to_python(value)
                except Exception:
                    original_values[field_name] = value
            else:
                original_values[field_name] = value

        new_values = self._apply_user_edits(request, form)

        attr_changes: Dict[str, Any] = {}
        debug_snapshot: Dict[str, Any] = {
            "model": self.model.__name__,
            "pk": getattr(obj, "pk", None),
            "strategy": strategy,
            "old_values": {},
            "new_values": new_values,
            "attr_changes": {},
            "vigencia_in_new_values": {k: v for k, v in new_values.items() if k in VIGENCIA_FIELDS},
            "post_keys": list(request.POST.keys()),
        }

        for field_name, new_val in new_values.items():
            if field_name in VIGENCIA_FIELDS:
                continue
            # Preferir snapshot original; se ausente, cair para valor
            # atual do objeto (situações legadas/edge cases).
            if field_name in original_values:
                old_val = original_values[field_name]
            else:
                old_val = getattr(obj, field_name, None)
            old_comp = getattr(old_val, "pk", old_val)
            new_comp = getattr(new_val, "pk", new_val)
            debug_snapshot["old_values"][field_name] = old_val
            if old_comp != new_comp:
                attr_changes[field_name] = new_val

        # Verifica se houve alteração real em campos de negócio (não-vigência)
        debug_snapshot["attr_changes"] = attr_changes

        # Verifica se houve alteração real em campos de vigência
        vigencia_changed = False
        for field_name in VIGENCIA_FIELDS:
            if field_name not in new_values:
                continue
            if field_name in original_values:
                old_val = original_values[field_name]
            else:
                old_val = getattr(obj, field_name, None)
            if old_val != new_values[field_name]:
                vigencia_changed = True
                break

        debug_snapshot["vigencia_changed"] = vigencia_changed

        try:
            self.logger.warning("BitemporalChangeHandler-debug %s", debug_snapshot)
        except Exception:
            pass

        # Regras para decidir se há alterações efetivas, considerando a estratégia:
        # - "nova_vigencia": só faz sentido abrir uma nova versão se houver alteração
        #   em atributos de negócio (não-vigência). Diferenças apenas de vigência
        #   não contam como alteração.
        # - "sobrescrever": tanto atributos gerais quanto datas de vigência podem
        #   caracterizar alteração.
        if strategy == "nova_vigencia":
            if not attr_changes:
                self.admin.message_user(
                    request,
                    "Nenhuma alteração detectada — atualização bitemporal não aplicada.",
                )
                changelist_url = reverse(
                    f'admin:{self.model._meta.app_label}_{self.model._meta.model_name}_changelist'
                )
                return HttpResponseRedirect(changelist_url)
        else:
            # Se não houver alterações nem em atributos gerais nem nas datas de vigência,
            # não há motivo para aplicar atualização bitemporal.
            if not attr_changes and not vigencia_changed:
                self.admin.message_user(
                    request,
                    "Nenhuma alteração detectada — atualização bitemporal não aplicada.",
                )
                changelist_url = reverse(
                    f'admin:{self.model._meta.app_label}_{self.model._meta.model_name}_changelist'
                )
                return HttpResponseRedirect(changelist_url)

            # Se o usuário reverteu todos os atributos na tela de confirmação (attr_changes
            # vazio) e a única “mudança” são as datas de vigência padrão do formulário,
            # não aplicar: ele chegou à confirmação por ter alterado um campo e depois
            # desfez na própria tela. Só aplicar mudança só de vigência quando a confirmação
            # foi aberta explicitamente pelo botão "Editar vigência" (_edit_vigencia no POST).
            if not attr_changes and vigencia_changed and not request.POST.get("_edit_vigencia"):
                self.admin.message_user(
                    request,
                    "Nenhuma alteração detectada — atualização bitemporal não aplicada.",
                )
                changelist_url = reverse(
                    f'admin:{self.model._meta.app_label}_{self.model._meta.model_name}_changelist'
                )
                return HttpResponseRedirect(changelist_url)

        effective_new_values: Dict[str, Any] = dict(attr_changes)
        for field_name in VIGENCIA_FIELDS:
            if field_name in new_values:
                effective_new_values[field_name] = new_values[field_name]

        # Validação de consistência temporal antes de aplicar a atualização.
        # Regra: data_vigencia_fim não pode ser anterior a data_vigencia_inicio.
        vig_inicio = effective_new_values.get(
            "data_vigencia_inicio", getattr(obj, "data_vigencia_inicio", None)
        )
        vig_fim = effective_new_values.get(
            "data_vigencia_fim", getattr(obj, "data_vigencia_fim", None)
        )
        if vig_inicio and vig_fim and vig_fim < vig_inicio:
            change_url = reverse(
                f'admin:{self.model._meta.app_label}_{self.model._meta.model_name}_change',
                args=[object_id]
            )
            messages.error(
                request,
                "Data de Início de Vigência não pode ser anterior à Data de Fim de Vigência.",
            )
            return HttpResponseRedirect(change_url)

        # Em "nova_vigencia", a versão atual será fechada com fim = novo_início - 1 dia.
        # Esse fim não pode ser anterior ao início da versão atual.
        if strategy == "nova_vigencia" and vig_inicio:
            current_vig_inicio = getattr(obj, "data_vigencia_inicio", None)
            if current_vig_inicio:
                vig_inicio_date = vig_inicio.date() if hasattr(vig_inicio, "date") else vig_inicio
                current_inicio_date = current_vig_inicio.date() if hasattr(current_vig_inicio, "date") else current_vig_inicio
                prev_vig_fim = vig_inicio_date - timedelta(days=1)
                if prev_vig_fim < current_inicio_date:
                    change_url = reverse(
                        f'admin:{self.model._meta.app_label}_{self.model._meta.model_name}_change',
                        args=[object_id]
                    )
                    messages.error(
                        request,
                        "Data de Início de Vigência não pode ser anterior à Data de Fim de Vigência.",
                    )
                    return HttpResponseRedirect(change_url)

        try:
            self.logger.warning(
                "BitemporalChangeHandler-apply | model=%s pk=%s strategy=%s effective_new_values=%s",
                self.model.__name__,
                getattr(obj, "pk", None),
                strategy,
                effective_new_values,
            )
        except Exception:
            pass

        from apps.core.bitemporal_update import apply_bitemporal_update

        apply_bitemporal_update(
            model=self.model,
            prev_obj=obj,
            new_values=effective_new_values,
            strategy=strategy,
        )

        self.admin.message_user(
            request,
            "Atualização bitemporal aplicada com sucesso.",
            level=messages.SUCCESS,
        )

        if hasattr(self.admin, 'trigger_export'):
            self.admin.trigger_export(request, self.model)

        changelist_url = reverse(
            f'admin:{self.model._meta.app_label}_{self.model._meta.model_name}_changelist'
        )
        return HttpResponseRedirect(changelist_url)
