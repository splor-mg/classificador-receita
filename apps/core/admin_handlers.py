"""
Handlers para fluxos de Admin.

BitemporalChangeHandler — coordena fluxo de confirmação bitemporal (sobrescrever / nova vigência).
BlockHandler — coordena fluxo de confirmação de bloqueio (encerrar vigência com data específica).
DeleteHandler — coordena fluxo de confirmação de exclusão (inativar registro via data_registro_fim).
ReactivateHandler — coordena fluxo de confirmação de reativação (criar nova linha ativa a partir de registro inativo).
"""
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Tuple
import logging

from django.template.response import TemplateResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.utils.html import format_html

from django.db import models as django_models
from django.utils import timezone

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
            old_display = old
            fk_lookup_url = None
            fk_semantic_lookup_url = None
            fk_kind = None
            fk_link_url = None
            new_display = None
            input_type = "text"
            input_step = None

            # Para campos numéricos, renderizar input como `type="number"` para manter
            # o comportamento de setas e restringir a entrada ao tipo numérico.
            try:
                from django.db import models as dj_models

                if isinstance(
                    field_meta,
                    (
                        dj_models.IntegerField,
                        dj_models.PositiveIntegerField,
                        dj_models.PositiveSmallIntegerField,
                        dj_models.SmallIntegerField,
                        dj_models.BigIntegerField,
                    ),
                ):
                    input_type = "number"
                    input_step = "1"
                elif isinstance(field_meta, (dj_models.DecimalField, dj_models.FloatField)):
                    input_type = "number"
                    input_step = "any"
            except Exception:
                # Caso não identifiquemos o tipo com segurança, mantemos fallback `text`.
                pass

            # ForeignKey: renderizar pela chave semântica (*_id) e, se possível,
            # exibir como select (para não ficar "livre" como input texto).
            if getattr(field_meta, "is_relation", False) and getattr(field_meta, "many_to_one", False):
                related_model = field_meta.remote_field.model
                semantic_attr = field_meta.name  # ex.: serie_id, base_legal_tecnica_id
                if field_meta.name == "serie_id":
                    fk_kind = "serie"
                elif field_meta.name == "base_legal_tecnica_id":
                    fk_kind = "base_legal_tecnica"

                def resolve_obj(val):
                    if val is None or val == "":
                        return None
                    if isinstance(val, related_model):
                        return val
                    try:
                        return related_model._default_manager.filter(pk=val).first()
                    except Exception:
                        return None

                old_obj = resolve_obj(old)
                new_obj = resolve_obj(new)

                old_pk = getattr(old_obj, "pk", old)
                new_pk = getattr(new_obj, "pk", new)

                old_display = getattr(old_obj, semantic_attr, old_pk)
                new_display = getattr(new_obj, semantic_attr, new_pk)

                old = old_pk
                new = new_pk

                # Link direto para abrir o registro relacionado (tela de change).
                fk_link_url = None
                try:
                    if new_obj is not None:
                        fk_link_url = reverse(
                            f"admin:{related_model._meta.app_label}_{related_model._meta.model_name}_change",
                            args=[new_obj.pk],
                        )
                except Exception:
                    fk_link_url = None

                # Usar "lupa" (lookup popup) em vez de dropdown.
                fk_lookup_url = None
                fk_semantic_lookup_url = None
                if fk_kind:
                    from django.contrib.admin.widgets import ForeignKeyRawIdWidget as DRFWidget

                    lookup_widget = DRFWidget(field_meta.remote_field, self.admin.admin_site)
                    # Para obter related_url, o nome/attrs não precisam refletir o input final,
                    # pois a URL vem da configuração do widget.
                    fk_lookup_url = lookup_widget.get_context(
                        f"edit_field_{field}",
                        new_pk,
                        attrs={"id": f"id_edit_field_{field}"},
                    ).get("related_url")

                    # Endpoint para converter pk -> *_id semântico.
                    fk_semantic_lookup_url = reverse(
                        f"admin:core_classificacao_semantic_lookup",
                        kwargs={"kind": fk_kind, "pk": 0},
                    )
                    fk_semantic_lookup_url = fk_semantic_lookup_url.replace("/0/", "/{pk}/")

                # Impede renderização como select no template.
                choices = None
                grouped_choices = None

            else:
                if hasattr(field_meta, "choices") and field_meta.choices:
                    choices = list(field_meta.choices)
                    # Para orgao_responsavel, aproveitar metadado de agrupamento
                    # para exibir um select mais informativo na tela de confirmação.
                    if field == "orgao_responsavel":
                        grouped_choices = ORGAOS_ENTIDADES_GROUPED_CHOICES

                if choices:
                    choices_dict = dict(choices)
                    # Para evitar duplicação "valor - label", exibir somente o label.
                    label_display = choices_dict.get(old, old)
                    old_display = label_display

            diff_entry = {
                "field": label,
                "field_name": field,
                "old": old,
                "old_display": old_display,
                "new": new,
                "choices": choices,
                "grouped_choices": grouped_choices,
                "fk_lookup_url": fk_lookup_url,
                "fk_semantic_lookup_url": fk_semantic_lookup_url,
                "fk_kind": fk_kind,
                "fk_link_url": fk_link_url,
                "new_display": new_display,
                "input_type": input_type,
                "input_step": input_step,
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
                            # Para ForeignKey, `to_python()` nem sempre retorna
                            # instância do relacionado quando o valor vem do
                            # hidden/raw_id. Garantimos conversão para
                            # instância para evitar erro de atribuição no ORM.
                            if getattr(field_obj, "is_relation", False) and getattr(field_obj, "many_to_one", False):
                                rel_model = field_obj.remote_field.model
                                if raw_val in (None, ""):
                                    new_val = None
                                else:
                                    new_val = rel_model._default_manager.filter(pk=raw_val).first()
                            else:
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
        current_year = today.year
        first_jan_current_year = date(current_year, 1, 1)

        current_vig_inicio = getattr(obj, "data_vigencia_inicio", None)
        current_vig_fim = getattr(obj, "data_vigencia_fim", None)

        # Normaliza datas atuais para comparações por ano.
        current_inicio_year = None
        current_inicio_date = None
        if current_vig_inicio is not None:
            current_inicio_date = (
                current_vig_inicio.date()
                if hasattr(current_vig_inicio, "date")
                else current_vig_inicio
            )
            current_inicio_year = current_inicio_date.year

        current_fim_year = None
        current_fim_date = None
        if current_vig_fim is not None:
            current_fim_date = (
                current_vig_fim.date()
                if hasattr(current_vig_fim, "date")
                else current_vig_fim
            )
            current_fim_year = current_fim_date.year

        # Marcadores auxiliares para regras temporais.
        inicio_ano_anterior = (
            current_inicio_year is not None and current_inicio_year < current_year
        )
        inicio_ano_corrente = current_inicio_year == current_year
        inicio_ano_futuro = (
            current_inicio_year is not None and current_inicio_year > current_year
        )

        fim_is_sentinela = bool(current_fim_date and current_fim_date == sentinela)
        fim_no_ano_corrente = current_fim_year == current_year
        fim_antes_ano_corrente = bool(
            current_fim_date and current_fim_date < first_jan_current_year
        )
        fim_a_partir_ano_corrente = bool(
            current_fim_date and current_fim_date >= first_jan_current_year
        )

        # Regra completa para início da nova versão (Registrar nova vigência),
        # sempre baseada na versão atual e na data corrente, independentemente
        # de ter vindo de lápis ou Salvar.
        if inicio_ano_corrente and current_inicio_date:
            if current_inicio_date < today:
                # Início no ano corrente, mas antes de hoje -> nova começa hoje.
                new_vig_inicio = today
            elif current_inicio_date == today:
                # Início igual a hoje -> nova começa amanhã.
                new_vig_inicio = today + timedelta(days=1)
            else:
                # Início no ano corrente, em data futura -> nova começa no dia seguinte.
                new_vig_inicio = current_inicio_date + timedelta(days=1)
        elif inicio_ano_futuro and current_inicio_year is not None:
            # Versão atual ainda não começou (vigência futura) ->
            # nova versão sugerida a partir de 1º jan do ano seguinte.
            new_vig_inicio = date(current_inicio_year + 1, 1, 1)
        elif inicio_ano_anterior and current_inicio_date:
            # Versão atual começou em ano anterior ao corrente.
            if fim_is_sentinela or fim_a_partir_ano_corrente:
                # Vigência que alcança ou ultrapassa o ano corrente (ou é aberta).
                new_vig_inicio = first_jan_current_year
            elif fim_antes_ano_corrente:
                # Vigência inteiramente no passado -> nova começa no dia seguinte ao início.
                new_vig_inicio = current_inicio_date + timedelta(days=1)
            else:
                # Fallback seguro: usar 1º jan do ano corrente.
                new_vig_inicio = first_jan_current_year
        else:
            # Sem informações suficientes de início -> padrão 1º jan ano corrente.
            new_vig_inicio = first_jan_current_year

        # Regra para fim da nova versão:
        # - Casos "originais" (início no ano corrente ou ano futuro) -> sentinela.
        # - Casos de início em ano anterior:
        #   - fim sentinela -> nova também com sentinela;
        #   - fim em qualquer ano específico -> copiar fim da versão atual.
        if inicio_ano_anterior:
            if current_fim_date is None:
                new_vig_fim = sentinela
            elif fim_is_sentinela:
                new_vig_fim = sentinela
            else:
                new_vig_fim = current_vig_fim
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
                "vig_fim": new_vig_fim,
                "strikethrough": False,
            },
        ]

        has_vig_inicio_change = "data_vigencia_inicio" in changed_data
        has_vig_fim_change = "data_vigencia_fim" in changed_data

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
            "current_vig_inicio": current_vig_inicio,
            "current_vig_fim": current_vig_fim,
            # Estratégia padrão: Registrar nova vigência apenas quando
            # a versão atual começou em ano anterior ao corrente e
            # (fim é sentinela ou fim está no ano corrente). Em todos
            # os demais casos, preferimos Sobrescrever.
            "prefer_nova_vigencia_default": bool(
                inicio_ano_anterior and (fim_is_sentinela or fim_no_ano_corrente)
            ),
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

        # Propaga snapshot dos valores originais (orig_field_*) para a tela de edição,
        # permitindo que o JavaScript compare o estado atual dos campos com esse snapshot
        # em vez de depender apenas de flags de alteração.
        orig_field_items = []
        prefix = "orig_field_"
        for key, value in request.POST.items():
            if key.startswith(prefix):
                orig_field_items.append((key, value))
        context["orig_field_items"] = orig_field_items
        
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

        # Se usuário clicou em Voltar na tela de confirmação, volta para edição.
        # Precisa vir antes de has_changed() porque o usuário pode ter desfeito
        # manualmente as alterações na tela de confirmação.
        if request.POST.get("_cancel_confirm"):
            return self._render_change_form_with_data(request, obj, form, object_id)

        edit_vigencia_flag = bool(request.POST.get("_edit_vigencia"))

        # Em fluxos normais, sem alterações não há o que confirmar.
        # Porém, quando o usuário clica em "Editar vigência", queremos
        # abrir a tela de confirmação mesmo que apenas as datas sejam
        # ajustadas na próxima etapa.
        if not form.has_changed() and not edit_vigencia_flag:
            return None

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
            prefer_nova_vigencia_default = bool(
                vigencia_preview.get("prefer_nova_vigencia_default")
            )
            prefer_sobrescrever_default = not prefer_nova_vigencia_default

            context = {
                **self.admin.admin_site.each_context(request),
                "title": "",
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

        from apps.core.bitemporal_update import apply_bitemporal_update, BitemporalOverlapError

        try:
            apply_bitemporal_update(
                model=self.model,
                prev_obj=obj,
                new_values=effective_new_values,
                strategy=strategy,
            )
        except BitemporalOverlapError as exc:
            # Em caso de conflito de vigência, permanecemos na tela de
            # confirmação, exibindo a mensagem de erro e permitindo que
            # o usuário ajuste as datas.
            try:
                overlap_start = getattr(exc, "overlap_start", None)
                overlap_end = getattr(exc, "overlap_end", None)
                entity_descr = getattr(exc, "entity_descr", "")
                conflicting_pk = getattr(exc, "conflicting_pk", None)
                semantic_label = None
                if entity_descr:
                    parts = entity_descr.split("=", 1)
                    if len(parts) == 2:
                        semantic_label = parts[1].strip()

                if conflicting_pk is not None:
                    conflict_url = reverse(
                        f'admin:{self.model._meta.app_label}_{self.model._meta.model_name}_change',
                        args=[conflicting_pk],
                    )
                else:
                    conflict_url = "#"

                series_label = semantic_label or entity_descr or getattr(obj, "pk", "")
                period_label = f"{overlap_start} a {overlap_end}"

                msg = format_html(
                    'Conflito de vigência: já existe registro ativo para '
                    '<strong>{}</strong> com período de vigência de <strong>{}</strong>. '
                    'Esse período é sobreposto pela vigência informada para a nova atualização - '
                    '<a href="{}" target="_blank" rel="noopener noreferrer">'
                    'clique aqui para editar a vigência desse outro registro</a>.',
                    series_label,
                    period_label,
                    conflict_url,
                )
            except Exception:
                msg = "Atualização bloqueada por conflito de vigência em registro ativo."

            messages.error(request, msg)

            changed_fields: List[str] = list(form.changed_data)
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

            for d in general_diffs + vigencia_diffs:
                field_name = d.get("field_name")
                if not field_name:
                    continue
                orig_key = f"orig_field_{field_name}"
                orig_val = d.get("old")
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
            prefer_nova_vigencia_default = bool(
                vigencia_preview.get("prefer_nova_vigencia_default")
            )
            prefer_sobrescrever_default = not prefer_nova_vigencia_default

            context = {
                **self.admin.admin_site.each_context(request),
                "title": "",
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


class BlockHandler:
    """
    Handler que gerencia o fluxo de confirmação de bloqueio no Admin.

    Bloqueio = encerrar a vigência do respectivo registro ao definir uma data específica
    para data_vigencia_fim. O registro permanece vigente no período entre a data de início e fim informados,
    mas não produz efeitos após a data estabelecida.
    """

    def __init__(self, admin_instance):
        self.admin = admin_instance
        self.model = admin_instance.model
        self.logger = logging.getLogger(__name__)

    def _parse_date_dmy_or_iso(self, value: str):
        """Parse data em dd/mm/aaaa ou aaaa-mm-dd. Retorna date ou None."""
        from datetime import datetime

        value = (value or "").strip()
        if not value:
            return None
        for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
            try:
                dt = datetime.strptime(value, fmt)
                return dt.date() if hasattr(dt, "date") else dt
            except (ValueError, TypeError):
                continue
        return None

    def _get_business_id_and_name(self, obj: Any) -> Dict[str, Any]:
        """Identifica campos de ID e Nome para exibição na tela de confirmação."""
        id_field = None
        name_field = None
        for field in self.model._meta.get_fields():
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

    def handle(self, request, object_id):
        """
        Processa o fluxo de bloqueio.

        GET: exibe tela de confirmação.
        POST (SCD-2): altera apenas data_registro_fim do registro existente; cria nova
        linha com as datas de vigência informadas na tela.
        """
        obj = self.admin.get_object(request, object_id)
        if not obj:
            from django.http import HttpResponseNotFound
            return HttpResponseNotFound()

        if not self.admin.has_change_permission(request, obj):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied()

        change_url = reverse(
            f'admin:{self.model._meta.app_label}_{self.model._meta.model_name}_change',
            args=[object_id],
        )

        if request.method == "POST" and request.POST.get("_save"):
            # Aplicar bloqueio
            fim_key = "edit_vig_fim_1"
            fim_str = (request.POST.get(fim_key) or "").strip()
            if not fim_str:
                messages.error(
                    request,
                    "Informe a data de fim de vigência para o bloqueio.",
                )
                return self._render_block_confirm(request, obj, object_id, change_url)

            new_fim = self._parse_date_dmy_or_iso(fim_str)
            if not new_fim:
                messages.error(
                    request,
                    "Data inválida. Use o formato dd/mm/aaaa.",
                )
                return self._render_block_confirm(request, obj, object_id, change_url)

            from apps.core.bitemporal_registry import get_sentinela_date

            if new_fim == get_sentinela_date():
                messages.error(
                    request,
                    "Para registrar um bloqueio de um registro, a Data de Fim de Vigência deve ser diferente do valor sentinela (31/12/9999).",
                )
                return self._render_block_confirm(request, obj, object_id, change_url)

            current_inicio = getattr(obj, "data_vigencia_inicio", None)
            current_fim = getattr(obj, "data_vigencia_fim", None)

            if current_inicio and new_fim < current_inicio:
                messages.error(
                    request,
                    "Data de Fim de Vigência não pode ser anterior à Data de Início de Vigência.",
                )
                return self._render_block_confirm(request, obj, object_id, change_url)

            # Se não houve alteração de vigência (fim informado igual ao atual),
            # não aplicamos nenhuma operação bitemporal: apenas informamos o
            # usuário e redirecionamos para a lista.
            if current_fim and new_fim == current_fim:
                messages.info(
                    request,
                    "Nenhuma alteração de vigência foi identificada. Nenhum registro foi modificado.",
                )
                changelist_url = reverse(
                    f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_changelist"
                )
                return HttpResponseRedirect(changelist_url)

            from apps.core.bitemporal_update import apply_bitemporal_update

            # Bloqueio (SCD-2): o registro existente permanece imutável; alteramos apenas
            # data_registro_fim (encerra em transaction time). A nova linha recebe as datas
            # de vigência conforme informadas na tela.
            try:
                apply_bitemporal_update(
                    model=self.model,
                    prev_obj=obj,
                    new_values={
                        "data_vigencia_inicio": current_inicio,
                        "data_vigencia_fim": new_fim,
                    },
                    strategy="sobrescrever",
                )
            except Exception as exc:
                self.logger.exception("BlockHandler apply_bitemporal_update failed")
                messages.error(request, str(exc))
                return self._render_block_confirm(request, obj, object_id, change_url)

            messages.success(request, "Bloqueio aplicado com sucesso.")

            if hasattr(self.admin, "trigger_export"):
                self.admin.trigger_export(request, self.model)

            changelist_url = reverse(
                f'admin:{self.model._meta.app_label}_{self.model._meta.model_name}_changelist'
            )
            return HttpResponseRedirect(changelist_url)

        return self._render_block_confirm(request, obj, object_id, change_url)

    def _render_block_confirm(self, request, obj, object_id, change_url):
        """Renderiza a tela de confirmação de bloqueio."""
        current_inicio = getattr(obj, "data_vigencia_inicio", None)
        current_fim = getattr(obj, "data_vigencia_fim", None)
        today = date.today()

        vigencia_inicio_iso = current_inicio.isoformat() if current_inicio else ""
        vigencia_fim_iso = current_fim.isoformat() if current_fim else ""

        block_preview = [
            {
                "version": "Versão 1",
                "vig_inicio": current_inicio.isoformat() if current_inicio else None,
                "vig_fim": current_fim.isoformat() if current_fim else None,
                "strikethrough": True,
            },
            {
                "version": "Versão 2",
                "vig_inicio": current_inicio.isoformat() if current_inicio else None,
                "vig_fim": today.isoformat(),
                "strikethrough": False,
            },
        ]

        import json
        block_preview_json = json.dumps(block_preview)

        block_url = reverse(
            f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_block",
            args=[object_id],
        )

        context = {
            **self.admin.admin_site.each_context(request),
            "title": "",
            "opts": self.model._meta,
            "original": obj,
            "object": obj,
            "change_url": change_url,
            "block_url": block_url,
            "vigencia_inicio_iso": vigencia_inicio_iso,
            "vigencia_fim_iso": vigencia_fim_iso,
            "nova_vigencia_fim_iso": today.isoformat(),
            "block_preview_json": block_preview_json,
        }
        context.update(self._get_business_id_and_name(obj))

        return TemplateResponse(
            request,
            "admin/core/block_confirm.html",
            context,
        )


class DeleteHandler:
    """
    Handler que gerencia o fluxo de confirmação de exclusão no Admin.

    Exclusão = remover integralmente a vigência do respectivo registro, inativando-o
    via data_registro_fim (transaction time). O registro deixa de produzir
    efeitos em qualquer período e passa a ser tratado como inexistente no
    histórico de vigências. Não há exclusão física, apenas lógica.
    """

    def __init__(self, admin_instance):
        self.admin = admin_instance
        self.model = admin_instance.model
        self.logger = logging.getLogger(__name__)

    def _get_business_id_and_name(self, obj: Any) -> Dict[str, Any]:
        """Identifica campos de ID e Nome para exibição na tela de confirmação."""
        id_field = None
        name_field = None
        for field in self.model._meta.get_fields():
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

    def handle(self, request, object_id):
        """
        Processa o fluxo de exclusão.

        GET: exibe tela de confirmação.
        POST: altera data_registro_fim do registro para a data/hora atual (inativa).
        """
        obj = self.admin.get_object(request, object_id)
        if not obj:
            from django.http import HttpResponseNotFound
            return HttpResponseNotFound()

        if not self.admin.has_delete_permission(request, obj):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied()

        change_url = reverse(
            f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_change",
            args=[object_id],
        )

        if request.method == "POST" and request.POST.get("_save"):
            from apps.core.models import TRANSACTION_TIME_SENTINEL

            # Usa consulta ao banco para evitar problemas de comparação naive/aware (USE_TZ)
            is_active = self.model._default_manager.filter(
                pk=obj.pk, data_registro_fim=TRANSACTION_TIME_SENTINEL
            ).exists()
            if not is_active:
                messages.info(
                    request,
                    "Este registro já está inativo (Data do Fim do Registro já definida).",
                )
                changelist_url = reverse(
                    f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_changelist"
                )
                return HttpResponseRedirect(changelist_url)

            try:
                obj.data_registro_fim = timezone.now()
                obj.save(update_fields=["data_registro_fim"])
            except Exception as exc:
                self.logger.exception("DeleteHandler save failed")
                messages.error(request, str(exc))
                return self._render_delete_confirm(request, obj, object_id, change_url)

            messages.success(request, "Exclusão aplicada com sucesso.")

            if hasattr(self.admin, "trigger_export"):
                self.admin.trigger_export(request, self.model)

            changelist_url = reverse(
                f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_changelist"
            )
            return HttpResponseRedirect(changelist_url)

        return self._render_delete_confirm(request, obj, object_id, change_url)

    def _render_delete_confirm(self, request, obj, object_id, change_url):
        """Renderiza a tela de confirmação de exclusão."""
        current_inicio = getattr(obj, "data_vigencia_inicio", None)
        current_fim = getattr(obj, "data_vigencia_fim", None)

        delete_preview = [
            {
                "vig_inicio": current_inicio.isoformat() if current_inicio else None,
                "vig_fim": current_fim.isoformat() if current_fim else None,
                "strikethrough": True,
            },
        ]

        import json
        delete_preview_json = json.dumps(delete_preview)

        delete_url = reverse(
            f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_delete",
            args=[object_id],
        )

        context = {
            **self.admin.admin_site.each_context(request),
            "title": "",
            "opts": self.model._meta,
            "original": obj,
            "object": obj,
            "change_url": change_url,
            "delete_url": delete_url,
            "delete_preview_json": delete_preview_json,
        }
        context.update(self._get_business_id_and_name(obj))

        return TemplateResponse(
            request,
            "admin/core/delete_confirm.html",
            context,
        )


class ReactivateHandler:
    """
    Handler que gerencia o fluxo de confirmação de reativação no Admin.

    Reativação = criar uma nova linha ativa (data_registro_fim = sentinela) a
    partir dos dados de um registro inativo, permitindo que o usuário edite
    atributos e vigência antes de confirmar. O registro inativo original
    permanece inalterado (append-only / SCD-2).
    """

    SYSTEM_FIELDS = {"data_registro_inicio", "data_registro_fim"}
    VIGENCIA_FIELDS = {"data_vigencia_inicio", "data_vigencia_fim"}

    def __init__(self, admin_instance):
        self.admin = admin_instance
        self.model = admin_instance.model
        self.logger = logging.getLogger(__name__)

    def _get_business_id_and_name(self, obj: Any) -> Dict[str, Any]:
        id_field = None
        name_field = None
        for field in self.model._meta.get_fields():
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

    def _get_form_choices(self, obj) -> Dict[str, list]:
        """
        Obtém as choices do formulário do admin (que pode ter grouped choices),
        retornando um mapa {field_name: choices_list}.
        """
        form_choices: Dict[str, list] = {}
        try:
            form_class = self.admin.get_form(None, obj)
            for fname, form_field in form_class.base_fields.items():
                if hasattr(form_field, "choices") and form_field.choices:
                    form_choices[fname] = list(form_field.choices)
        except Exception:
            pass
        return form_choices

    @staticmethod
    def _is_grouped_choices(choices: list) -> bool:
        """Verifica se a lista de choices usa o formato agrupado do Django."""
        if not choices:
            return False
        for _label, value in choices:
            if isinstance(value, (list, tuple)):
                return True
        return False

    def _build_field_metadata(self, obj) -> List[Dict[str, Any]]:
        """Constrói metadados dos campos de negócio para renderização no template."""
        fields = []
        pk_name = self.model._meta.pk.name
        form_choices = self._get_form_choices(obj)

        for f in self.model._meta.concrete_fields:
            name = f.name
            if name == pk_name:
                continue
            if name in self.SYSTEM_FIELDS or name in self.VIGENCIA_FIELDS:
                continue
            is_ref_field = name.endswith("_ref")

            label = getattr(f, "verbose_name", name).capitalize()
            is_fk = f.is_relation

            if is_fk:
                raw_value = getattr(obj, f.attname)
                related_obj = getattr(obj, f.name, None)
                display_value = str(related_obj) if related_obj else ""
                field_type = "fk"
                choices = None
                is_grouped = False
            elif name in form_choices:
                raw_value = getattr(obj, name)
                display_value = raw_value
                choices = form_choices[name]
                is_grouped = self._is_grouped_choices(choices)
                if is_grouped:
                    choices = [
                        (gl, gc) for gl, gc in choices
                        if isinstance(gc, (list, tuple))
                    ]
                field_type = "select_grouped" if is_grouped else "select"
            elif hasattr(f, "choices") and f.choices:
                raw_value = getattr(obj, name)
                display_value = raw_value
                field_type = "select"
                choices = list(f.choices)
                is_grouped = False
            elif isinstance(f, django_models.TextField):
                raw_value = getattr(obj, name)
                display_value = raw_value
                field_type = "textarea"
                choices = None
                is_grouped = False
            else:
                raw_value = getattr(obj, name)
                display_value = raw_value
                field_type = "text"
                choices = None
                is_grouped = False

            fields.append({
                "name": name,
                "attname": f.attname if is_fk else name,
                "label": label,
                "value": raw_value,
                "display_value": display_value,
                "field_type": field_type,
                "choices": choices,
                "is_fk": is_fk,
                "is_grouped": is_grouped,
                "readonly": is_ref_field,
            })

        return fields

    def handle(self, request, object_id):
        """
        Processa o fluxo de reativação.

        GET: exibe tela de confirmação com campos editáveis.
        POST: valida, verifica conflitos de vigência e cria nova linha ativa.
        """
        obj = self.admin.get_object(request, object_id)
        if not obj:
            from django.http import HttpResponseNotFound
            return HttpResponseNotFound()

        change_url = reverse(
            f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_change",
            args=[object_id],
        )

        if request.method == "POST" and request.POST.get("_save"):
            return self._process_reactivation(request, obj, object_id, change_url)

        return self._render_reactivate_confirm(request, obj, object_id, change_url)

    def _process_reactivation(self, request, obj, object_id, change_url):
        from apps.core.bitemporal_registry import (
            get_sentinela_datetime,
            get_resource_for_model,
            get_resource,
        )
        from django.db import transaction as db_transaction

        sentinela = get_sentinela_datetime()
        now = timezone.now()
        pk_name = self.model._meta.pk.name

        # Copiar todos os campos do registro inativo como base.
        base_data: Dict[str, Any] = {}
        for f in self.model._meta.concrete_fields:
            if f.name == pk_name:
                continue
            if f.is_relation:
                base_data[f.attname] = getattr(obj, f.attname)
            else:
                base_data[f.name] = getattr(obj, f.name)

        # Aplicar edições do usuário (campos de negócio).
        for f in self.model._meta.concrete_fields:
            name = f.name
            if name == pk_name or name in self.SYSTEM_FIELDS:
                continue
            edit_key = f"edit_field_{name}"
            if edit_key not in request.POST:
                continue
            raw_val = request.POST.get(edit_key)
            try:
                val = f.to_python(raw_val) if hasattr(f, "to_python") else raw_val
            except Exception:
                val = raw_val
            if f.is_relation:
                base_data[f.attname] = val
            else:
                base_data[name] = val

        # Aplicar datas de vigência editadas.
        vig_inicio_str = (request.POST.get("edit_vig_inicio_1") or "").strip()
        vig_fim_str = (request.POST.get("edit_vig_fim_1") or "").strip()

        if vig_inicio_str:
            try:
                base_data["data_vigencia_inicio"] = datetime.strptime(vig_inicio_str, "%Y-%m-%d").date()
            except ValueError:
                pass
        if vig_fim_str:
            try:
                base_data["data_vigencia_fim"] = datetime.strptime(vig_fim_str, "%Y-%m-%d").date()
            except ValueError:
                pass

        # Definir transaction time da nova linha.
        base_data["data_registro_inicio"] = now
        base_data["data_registro_fim"] = sentinela

        vig_inicio = base_data.get("data_vigencia_inicio")
        vig_fim = base_data.get("data_vigencia_fim")

        if vig_inicio and vig_fim and vig_fim < vig_inicio:
            messages.error(
                request,
                "Data de Fim de Vigência não pode ser anterior à Data de Início de Vigência.",
            )
            return self._render_reactivate_confirm(request, obj, object_id, change_url)

        # Verificar conflito de vigência com registros ativos da mesma entidade.
        # Usa entity_key (chave surrogate *_ref) para o filtro e
        # semantic_id_field (chave semântica *_id) para mensagens de erro.
        entity_filter: Dict[str, Any] = {}
        res: Dict[str, Any] = {}
        try:
            resource_name = get_resource_for_model(self.model)
        except Exception:
            resource_name = None
        if resource_name:
            try:
                res = get_resource(resource_name)
            except Exception:
                res = {}
            for ek in res.get("entity_key", []):
                lookup = ek.get("lookup")
                if not lookup:
                    continue
                val = getattr(obj, lookup, None)
                entity_filter[lookup] = val

        semantic_field = res.get("semantic_id_field")

        if entity_filter and vig_inicio and vig_fim:
            active_qs = (
                self.model.objects
                .filter(**entity_filter, data_registro_fim=sentinela)
            )
            conflicts = []
            for other in active_qs:
                e_inicio = getattr(other, "data_vigencia_inicio", None)
                e_fim = getattr(other, "data_vigencia_fim", None)
                if e_inicio is None or e_fim is None:
                    continue
                if vig_inicio <= e_fim and e_inicio <= vig_fim:
                    conflict_url = reverse(
                        f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_change",
                        args=[other.pk],
                    )
                    if semantic_field:
                        series_label = getattr(other, semantic_field, None) or str(obj.pk)
                    else:
                        series_label = str(obj.pk)
                    period_label = f"{e_inicio} a {e_fim}"
                    conflicts.append((e_inicio, series_label, period_label, conflict_url))

            if conflicts:
                # Ordena conflitos pela data de início de vigência (crescente)
                conflicts.sort(key=lambda c: c[0])
                for _e_inicio, series_label, period_label, conflict_url in conflicts[:3]:
                    messages.error(
                        request,
                        format_html(
                            'Conflito de vigência: já existe registro ativo para '
                            '<strong>{}</strong> com período de vigência de <strong>{}</strong>. '
                            'Esse período é sobreposto pela vigência informada para a nova reativação — '
                            '<a href="{}" target="_blank" rel="noopener noreferrer">'
                            'clique aqui para editar a vigência desse outro registro</a>.',
                            series_label,
                            period_label,
                            conflict_url,
                        ),
                    )

                extra_count = len(conflicts) - 3
                if extra_count > 0:
                    messages.error(
                        request,
                        format_html(
                            'Há mais <strong>{}</strong> conflito(s) de vigência não listado(s) aqui. '
                            'Ajuste as vigências ou refine o período da nova reativação.',
                            extra_count,
                        ),
                    )

                return self._render_reactivate_confirm(request, obj, object_id, change_url)

        try:
            with db_transaction.atomic():
                self.model.objects.create(**base_data)
        except Exception as exc:
            self.logger.exception("ReactivateHandler create failed")
            messages.error(request, str(exc))
            return self._render_reactivate_confirm(request, obj, object_id, change_url)

        messages.success(request, "Reativação aplicada com sucesso.")

        if hasattr(self.admin, "trigger_export"):
            self.admin.trigger_export(request, self.model)

        changelist_url = reverse(
            f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_changelist"
        )
        return HttpResponseRedirect(changelist_url)

    def _render_reactivate_confirm(self, request, obj, object_id, change_url):
        business_fields = self._build_field_metadata(obj)

        current_inicio = getattr(obj, "data_vigencia_inicio", None)
        current_fim = getattr(obj, "data_vigencia_fim", None)

        # Quando houver POST com erros de validação, preservar os valores
        # editados pelo usuário (atributos gerais e vigência) na reexibição.
        if request.method == "POST":
            post = request.POST
            for field in business_fields:
                name = field.get("name")
                if not name:
                    continue
                key = f"edit_field_{name}"
                if key in post:
                    raw_val = post.get(key)
                    field["value"] = raw_val
                    field["display_value"] = raw_val

            vig_inicio_str = (post.get("edit_vig_inicio_1") or "").strip()
            vig_fim_str = (post.get("edit_vig_fim_1") or "").strip()

            vigencia_inicio_iso = vig_inicio_str or (
                current_inicio.isoformat() if current_inicio else ""
            )
            vigencia_fim_iso = vig_fim_str or (
                current_fim.isoformat() if current_fim else ""
            )
        else:
            vigencia_inicio_iso = current_inicio.isoformat() if current_inicio else ""
            vigencia_fim_iso = current_fim.isoformat() if current_fim else ""

        import json
        reactivate_preview = [{
            "vig_inicio": vigencia_inicio_iso or None,
            "vig_fim": vigencia_fim_iso or None,
        }]
        reactivate_preview_json = json.dumps(reactivate_preview)

        context = {
            **self.admin.admin_site.each_context(request),
            "title": "",
            "opts": self.model._meta,
            "original": obj,
            "object": obj,
            "change_url": change_url,
            "business_fields": business_fields,
            "vigencia_inicio_iso": vigencia_inicio_iso,
            "vigencia_fim_iso": vigencia_fim_iso,
            "reactivate_preview_json": reactivate_preview_json,
        }
        context.update(self._get_business_id_and_name(obj))

        return TemplateResponse(
            request,
            "admin/core/reactivate_confirm.html",
            context,
        )
