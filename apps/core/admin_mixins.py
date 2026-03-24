"""
Mixins reutilizáveis para Django Admin.

AutoExportAdminMixin — dispara export do seed após save.
BitemporalAdminMixin — fluxo de confirmação bitemporal (sobrescrever / nova vigência).
BitemporalInactiveReadOnlyMixin — somente leitura para registros inativos + rota de reativação.
BitemporalDateFormatMixin — formatação de datas bitemporais (dd/mm/yyyy).
CoreChangeSaveFormSubmitMixin — tela de edição com apenas Salvar e Cancelar.
"""
import re
import logging
import unicodedata
from datetime import date
from pathlib import Path
from typing import Any, Callable, Dict

from django.contrib import admin
from django.contrib import messages
from django.db import models as django_models
from django.db.models import Max
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import path, reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters

from apps.core.admin_widgets import ForeignKeySemanticDisplayRawIdWidget
from apps.core.exporter import export_resource
from apps.core.bitemporal_registry import get_resource_for_model
from apps.core.models import TRANSACTION_TIME_SENTINEL, VALID_TIME_SENTINEL

ID_HELP_EXAMPLES = {
    "serieclassificacao": "SERIE-RECEITA-UNIAO",
    "classificacao": "CLASSIFICACAO-EXEMPLO",
    "nivelhierarquico": "NIVEL-EXEMPLO",
    "itemclassificacao": "ITEM-EXEMPLO",
    "versaoclassificacao": "VERSAO-2024",
    "varianteclassificacao": "VARIANTE-EXEMPLO",
    "baselegaltecnica": "CR-88-PLANALTO",
}

#---------------------------------------------------------------------------------------------------
# Filtro para registros ativos (correntes, históricos e futuros) e inativos em termos de registro/vigência
class RegistroAtivoFilter(admin.SimpleListFilter):
    """
    Filtro genérico para registros ativos (correntes, históricos e futuros)
    e inativos em termos de registro/vigência em models bitemporais.
    """

    title = "Status do Registro"
    parameter_name = "registro_ativo"

    def lookups(self, request, model_admin):
        return (
            ("ativo_corrente", "Ativos (Ano Corrente)"),
            ("ativo_futuro", "Ativos (Futuro)"),
            ("ativo_historico", "Ativos (Histórico)"),
            ("inativo", "Inativos"),
        )

    def queryset(self, request, queryset):
        today = date.today()
        ano_corrente = today.year
        primeiro_dia_ano = date(ano_corrente, 1, 1)
        ultimo_dia_ano = date(ano_corrente, 12, 31)

        if self.value() == "ativo_corrente":
            return queryset.filter(
                data_registro_fim=TRANSACTION_TIME_SENTINEL,
                data_vigencia_inicio__lte=ultimo_dia_ano,
                data_vigencia_fim__gte=primeiro_dia_ano,
            )
        if self.value() == "ativo_futuro":
            return queryset.filter(
                data_registro_fim=TRANSACTION_TIME_SENTINEL,
                data_vigencia_fim__gt=ultimo_dia_ano,
            )
        if self.value() == "ativo_historico":
            return queryset.filter(
                data_registro_fim=TRANSACTION_TIME_SENTINEL,
            )
        if self.value() == "inativo":
            return queryset.exclude(data_registro_fim=TRANSACTION_TIME_SENTINEL)
        return queryset

#---------------------------------------------------------------------------------------------------
# Filtros de sidebar (changelist): id local vs ForeignKey
def make_filter_local_id(field_name, *, title=None, parameter_name=None):
    """
    Fábrica de ``SimpleListFilter`` para um campo **na própria tabela** do modelo
    da changelist (ex.: ``CharField`` de id de negócio / id semântico).

    O texto exibido nas opções e o valor enviado na query string são **o mesmo**
    valor armazenado em ``field_name``. O filtro aplica ``queryset.filter(**{field_name: value})``.

    As opções são os valores distintos desse campo em ``Model._default_manager``
    (não restringe ao ``get_queryset`` da changelist).

    Instâncias prontas para este projeto: ``apps.core.admin_filters``.
    Exemplo genérico:
        MeuFiltro = make_filter_local_id('meu_campo_id', title='Identificador')
        list_filter = [MeuFiltro, ...]
    """

    # Resolvidos aqui para evitar NameError dentro do corpo da classe
    resolved_title = title or field_name.replace('_', ' ').title()
    resolved_parameter_name = parameter_name or field_name

    class IdFilter(admin.SimpleListFilter):
        _field_name = field_name
        title = resolved_title
        parameter_name = resolved_parameter_name

        def lookups(self, request, model_admin):
            Model = model_admin.model
            values = (
                Model._default_manager.values_list(self._field_name, flat=True)
                .distinct()
                .order_by(self._field_name)
            )
            return [(value, value) for value in values if value not in (None, "")]

        def queryset(self, request, queryset):
            value = self.value()
            if value:
                return queryset.filter(**{self._field_name: value})
            return queryset

    return IdFilter


def fk_semantic_filter_lookups(qs, fk_id_attname, related_model, semantic_attr):
    """[(pk, id semântico), …] para sidebar do admin (evita ``__str__`` do relacionado)."""
    pks = list(qs.values_list(fk_id_attname, flat=True).distinct().order_by(fk_id_attname))
    pks = [p for p in pks if p is not None]
    if not pks:
        return []
    rows = related_model.objects.filter(pk__in=pks).order_by(semantic_attr)
    return [(str(o.pk), str(getattr(o, semantic_attr))) for o in rows]


def make_filter_fk_id(host_model, fk_name, semantic_attr=None):
    """
    Fábrica de ``SimpleListFilter`` para um **ForeignKey** no modelo da changelist.

    **Query string:** usa o mesmo parâmetro que o ``RelatedFieldListFilter`` do Django
    (``<fk>__<pk_do_relacionado>__exact``), com o **PK da linha relacionada** — não o id
    semântico. O filtro aplica ``queryset.filter(**{esse_lookup: valor})``.

    **Rótulos na sidebar:** leem o id semântico (ou outro atributo) no **modelo
    relacionado**, via ``semantic_attr``, em vez de usar ``__str__`` do relacionado
    (que costuma ser longo). Default de ``semantic_attr``: ``fk_name``, quando o campo
    semântico no relacionado tem o mesmo nome que o FK.

    **Opções do filtro:** PKs distintas observadas em ``model_admin.get_queryset(request)``
    na coluna da FK, enriquecidas com o valor de ``semantic_attr`` para exibição.
    """
    field = host_model._meta.get_field(fk_name)
    related_model = field.remote_field.model
    attname = field.attname
    lookup_kwarg = f"{fk_name}__{field.target_field.name}__exact"
    sem = semantic_attr if semantic_attr is not None else fk_name
    resolved_title = field.verbose_name

    class SemanticFkSidebarFilter(admin.SimpleListFilter):
        title = resolved_title
        parameter_name = lookup_kwarg

        def lookups(self, request, model_admin):
            return fk_semantic_filter_lookups(
                model_admin.get_queryset(request), attname, related_model, sem
            )

        def queryset(self, request, queryset):
            v = self.value()
            if v:
                return queryset.filter(**{lookup_kwarg: v})
            return queryset

    return SemanticFkSidebarFilter


#---------------------------------------------------------------------------------------------------
# Tela de edição: apenas Salvar e Cancelar (sem Salvar e adicionar outro / Salvar e continuar)
class CoreChangeSaveFormSubmitMixin:
    """
    Usa o template admin/core/change_form.html, que exibe apenas os botões
    Salvar e Cancelar (volta para a changelist), sem "Salvar e adicionar outro"
    nem "Salvar e continuar editando".
    """
    change_form_template = "admin/core/change_form.html"

#---------------------------------------------------------------------------------------------------
# Reutiliza rotas/handlers de ações bitemporais por objeto (ex.: block/delete)
class BitemporalObjectActionsMixin:
    """
    Mixin para reduzir duplicação de URLs/handlers de ações por objeto no Admin.

    Exemplo:
        bitemporal_object_actions = ("block", "delete")
    """

    bitemporal_object_actions = ("block", "delete")

    def _get_bitemporal_action_handler(self, action: str):
        from apps.core.admin_handlers import BlockHandler, DeleteHandler

        handlers = {
            "block": BlockHandler,
            "delete": DeleteHandler,
        }
        return handlers.get(action)

    def _get_bitemporal_action_url_name(self, action: str) -> str:
        return f"{self.model._meta.app_label}_{self.model._meta.model_name}_{action}"

    def _build_bitemporal_action_urls(self):
        custom = []
        for action in self.bitemporal_object_actions:
            view_method = getattr(self, f"{action}_view", None)
            if view_method is None:
                continue
            custom.append(
                path(
                    f"<path:object_id>/{action}/",
                    self.admin_site.admin_view(view_method),
                    name=self._get_bitemporal_action_url_name(action),
                )
            )
        return custom

    def get_urls(self):
        urls = super().get_urls()
        custom = self._build_bitemporal_action_urls()
        return custom + urls

    def _handle_bitemporal_action(self, request, object_id, action: str):
        handler_cls = self._get_bitemporal_action_handler(action)
        if handler_cls is None:
            from django.http import HttpResponseNotFound

            return HttpResponseNotFound()
        handler = handler_cls(self)
        return handler.handle(request, object_id)

    def block_view(self, request, object_id):
        return self._handle_bitemporal_action(request, object_id, "block")

    def delete_view(self, request, object_id):
        return self._handle_bitemporal_action(request, object_id, "delete")

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        extra_context = extra_context or {}
        if object_id:
            for action in self.bitemporal_object_actions:
                extra_context[f"{action}_url"] = reverse(
                    f"admin:{self._get_bitemporal_action_url_name(action)}",
                    args=[object_id],
                )
        return super().changeform_view(request, object_id, form_url, extra_context)


#---------------------------------------------------------------------------------------------------
# Reutiliza lookup semântico para ForeignKeys (lupa + *_id em vez de PK)
class SemanticForeignKeyAdminMixin:
    """
    Mixin para padronizar:
    - rota semantic-lookup/<kind>/<pk>/
    - endpoint JSON de lookup semântico
    - aplicação do ForeignKeySemanticDisplayRawIdWidget
    - colunas de changelist ``{campo_fk}_raw`` (id semântico da FK), geradas a partir de
      ``semantic_fk_config`` (salvo sobrescrita manual no Admin)

    Configure no Admin:
        semantic_fk_config = {
            "serie_id": {
                "kind": "serie",
                "model": SerieClassificacao,
                "semantic_field": "serie_id",
                "display_label": lambda obj: f"{obj.serie_id} - {obj.serie_nome}",
                # opcionais para a coluna *_raw:
                # "list_column": False,  # não registrar método
                # "list_column_method": "serie_id_raw",  # nome do método (default: {fk}_raw)
                # "list_column_description": "Série",  # default: verbose_name do FK em model
            },
        }

    Para usar o verbose_name do campo FK como rótulo da coluna, defina ``model = SeuModel``
    no corpo do ModelAdmin (o ``@admin.register`` também preenche ``model``, mas só depois
    da criação da classe; sem ``model`` no corpo, o título da coluna cai no fallback).
    """

    semantic_fk_config: Dict[str, Dict[str, Any]] = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        config = getattr(cls, "semantic_fk_config", None) or {}
        if not config:
            return
        Model = getattr(cls, "model", None)
        for fk_name, cfg in config.items():
            if cfg.get("list_column") is False:
                continue
            semantic_field = cfg.get("semantic_field")
            if not semantic_field:
                continue
            method_name = cfg.get("list_column_method") or f"{fk_name}_raw"
            if method_name in cls.__dict__:
                continue
            fk_id_attr = f"{fk_name}_id"
            description = cfg.get("list_column_description")
            if description is None and Model is not None:
                try:
                    description = Model._meta.get_field(fk_name).verbose_name
                except Exception:
                    description = None
            if not description:
                description = fk_name.replace("_", " ").title()

            def _make_semantic_fk_raw_display(fk, sem, fid):
                def raw(self, obj):
                    if getattr(obj, fid, None) is None:
                        return ""
                    related = getattr(obj, fk, None)
                    if related is None:
                        return getattr(obj, fid, "")
                    val = getattr(related, sem, "")
                    return val if val is not None else ""

                return raw

            fn = admin.display(description=str(description))(
                _make_semantic_fk_raw_display(fk_name, semantic_field, fk_id_attr)
            )
            setattr(cls, method_name, fn)

    def _get_semantic_lookup_url_name(self) -> str:
        return f"{self.model._meta.app_label}_{self.model._meta.model_name}_semantic_lookup"

    def _iter_semantic_kinds(self):
        config = getattr(self, "semantic_fk_config", {}) or {}
        for field_name, cfg in config.items():
            kind = cfg.get("kind")
            if kind:
                yield field_name, kind, cfg

    def _get_semantic_cfg_by_kind(self, kind: str):
        for _, cfg_kind, cfg in self._iter_semantic_kinds():
            if cfg_kind == kind:
                return cfg
        return None

    def _build_semantic_lookup_urls(self):
        config = getattr(self, "semantic_fk_config", {}) or {}
        if not config:
            return []
        return [
            path(
                "semantic-lookup/<str:kind>/<int:pk>/",
                self.admin_site.admin_view(self.semantic_lookup_view),
                name=self._get_semantic_lookup_url_name(),
            )
        ]

    def get_urls(self):
        urls = super().get_urls()
        custom = self._build_semantic_lookup_urls()
        return custom + urls

    def semantic_lookup_view(self, request, kind: str, pk: int):
        cfg = self._get_semantic_cfg_by_kind(kind)
        if not cfg:
            return JsonResponse({"semantic_value": "", "display_label": "", "link_url": ""})

        model = cfg.get("model")
        semantic_field = cfg.get("semantic_field")
        display_label_cfg = cfg.get("display_label")

        if not model or not semantic_field:
            return JsonResponse({"semantic_value": "", "display_label": "", "link_url": ""})

        try:
            obj = model.objects.get(pk=pk)
            link_url = reverse(
                f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change",
                args=[obj.pk],
            )

            semantic_value = getattr(obj, semantic_field, "") or ""

            if callable(display_label_cfg):
                display_label = display_label_cfg(obj)
            elif isinstance(display_label_cfg, str) and display_label_cfg:
                display_label = getattr(obj, display_label_cfg, "") or semantic_value
            else:
                display_label = semantic_value

            return JsonResponse(
                {
                    "semantic_value": semantic_value,
                    "display_label": display_label,
                    "link_url": link_url,
                }
            )
        except Exception:
            return JsonResponse({"semantic_value": "", "display_label": "", "link_url": ""})

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        config = getattr(self, "semantic_fk_config", {}) or {}
        cfg = config.get(db_field.name)
        if not cfg or formfield is None:
            return formfield

        kind = cfg.get("kind")
        semantic_field = cfg.get("semantic_field")
        if not kind or not semantic_field:
            return formfield

        lookup_url = reverse(
            f"admin:{self._get_semantic_lookup_url_name()}",
            kwargs={"kind": kind, "pk": 0},
        ).replace("/0/", "/{pk}/")

        using_db = kwargs.get("using") or getattr(formfield.widget, "db", None)
        formfield.widget = ForeignKeySemanticDisplayRawIdWidget(
            db_field.remote_field,
            self.admin_site,
            semantic_field=semantic_field,
            semantic_lookup_url=lookup_url,
            attrs=getattr(formfield.widget, "attrs", None),
            using=using_db,
        )
        return formfield

#---------------------------------------------------------------------------------------------------
# Torna registros bitemporais inativos somente leitura
class BitemporalInactiveReadOnlyMixin:
    """
    Mixin que torna registros bitemporais inativos somente leitura no Admin.

    Considera inativo quando data_registro_fim é diferente de TRANSACTION_TIME_SENTINEL.
    Nesses casos:
    - o usuário vê o formulário apenas para consulta (view-only);
    - botões de salvar são ocultados (sem permissão de change);
    - uma mensagem informativa é exibida no topo do formulário.
    """

    inactive_message = (
        "Registro inativo — apenas consulta histórica; edição desabilitada."
    )

    _REGISTRO_FIELDS = frozenset({
        "data_registro_inicio", "data_registro_fim",
        "data_registro_inicio_fmt", "data_registro_fim_fmt",
    })

    def get_changeform_initial_data(self, request):
        """Pre-preenche campos no formulário de adição (add view)."""
        initial = super().get_changeform_initial_data(request)

        for f in self.model._meta.concrete_fields:
            if f.name.endswith("_ref"):
                max_val = self.model.objects.aggregate(Max(f.name))[f"{f.name}__max"]
                initial[f.name] = (max_val or 0) + 1
                break

        initial.setdefault("data_vigencia_inicio", date(date.today().year, 1, 1))
        initial.setdefault("data_vigencia_fim", VALID_TIME_SENTINEL)

        return initial

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if obj is None:
            fields = [f for f in fields if f not in self._REGISTRO_FIELDS]
        return fields

    def get_readonly_fields(self, request, obj=None):
        fields = list(super().get_readonly_fields(request, obj))
        if obj is None:
            ref_names = {
                f.name
                for f in self.model._meta.concrete_fields
                if f.name.endswith("_ref")
            }
            exclude = self._REGISTRO_FIELDS | ref_names
            fields = [f for f in fields if f not in exclude]
        return fields

    @staticmethod
    def _is_identifier_field(db_field):
        return (
            db_field.name.endswith("_id")
            and not db_field.is_relation
            and isinstance(db_field, django_models.CharField)
        )

    def _get_identifier_field_name(self):
        for f in self.model._meta.concrete_fields:
            if self._is_identifier_field(f):
                return f.name
        return None

    def get_form(self, request, obj=None, **kwargs):
        FormClass = super().get_form(request, obj, **kwargs)
        if obj is not None:
            return FormClass

        id_field_name = self._get_identifier_field_name()
        if not id_field_name:
            return FormClass

        model = self.model
        sentinel = TRANSACTION_TIME_SENTINEL

        admin_instance = self

        class FormWithIdValidation(FormClass):
            def clean(form_self):
                cleaned = super().clean()
                value = cleaned.get(id_field_name)
                if value:
                    existing = model._default_manager.filter(
                        **{id_field_name: value, "data_registro_fim": sentinel}
                    ).first()
                    if existing:
                        from django.core.exceptions import ValidationError
                        from django.utils.safestring import mark_safe
                        change_url = reverse(
                            f"admin:{model._meta.app_label}_{model._meta.model_name}_change",
                            args=[existing.pk],
                        )
                        msg = mark_safe(
                            f'Já existe um registro ativo com o identificador "{value}". '
                            f'<a href="{change_url}" target="_blank" '
                            f'style="text-decoration:underline;">Abrir registro</a>'
                        )
                        form_self.add_error(
                            id_field_name,
                            ValidationError(msg, code='duplicate_active_id'),
                        )
                return cleaned

        return FormWithIdValidation

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name.endswith("_ref") and formfield is not None:
            formfield.widget.attrs["readonly"] = True
            formfield.widget.attrs["style"] = (
                "background-color:#f4f4f4; color:#555;"
            )
        if self._is_identifier_field(db_field) and formfield is not None:
            # Exemplo dinâmico/estático no help_text apenas na tela de adição
            try:
                is_add_view = (
                    request is not None
                    and request.resolver_match is not None
                    and request.resolver_match.url_name.endswith("_add")
                )
            except Exception:
                is_add_view = False

            if is_add_view:
                model = self.model
                id_field_name = db_field.name
                latest = (
                    model._default_manager.filter(
                        data_registro_fim=TRANSACTION_TIME_SENTINEL
                    )
                    .order_by("-pk")
                    .values_list(id_field_name, flat=True)
                    .first()
                )
                if latest:
                    example = latest
                else:
                    example = ID_HELP_EXAMPLES.get(model._meta.model_name)

                if example:
                    base_help = formfield.help_text or ""
                    extra = f' Ex.: <code>{example}</code>'
                    formfield.help_text = mark_safe(base_help + extra)

            original_clean = formfield.clean

            def normalizing_clean(value):
                if value and isinstance(value, str):
                    value = unicodedata.normalize('NFD', value)
                    value = ''.join(c for c in value if unicodedata.category(c) != 'Mn')
                    value = value.strip().upper()
                    value = re.sub(r'[\s_]+', '-', value)
                    value = re.sub(r'-+', '-', value)
                    value = value.strip('-')
                return original_clean(value)

            formfield.clean = normalizing_clean
        return formfield

    def _is_inactive_record(self, obj) -> bool:
        """
        Determina se o registro é inativo consultando o banco, para
        evitar problemas de comparação entre datetimes (naive/aware).

        Consideramos ATIVO se existe uma linha com pk e data_registro_fim
        exatamente igual ao sentinela; caso contrário, é inativo.
        """
        if not obj:
            return False
        Model = obj.__class__
        is_active = Model._default_manager.filter(
            pk=obj.pk, data_registro_fim=TRANSACTION_TIME_SENTINEL
        ).exists()
        return not is_active

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "check-id-exists/",
                self.admin_site.admin_view(self._check_id_exists_view),
                name=f"{self.model._meta.app_label}_{self.model._meta.model_name}_check_id_exists",
            ),
            path(
                "<path:object_id>/reactivate/",
                self.admin_site.admin_view(self.reactivate_view),
                name=f"{self.model._meta.app_label}_{self.model._meta.model_name}_reactivate",
            ),
        ]
        return custom + urls

    def _check_id_exists_view(self, request):
        from django.http import JsonResponse
        value = request.GET.get("value", "").strip()
        id_field_name = self._get_identifier_field_name()
        if not value or not id_field_name:
            return JsonResponse({"exists": False})
        qs = self.model._default_manager.filter(
            **{id_field_name: value, "data_registro_fim": TRANSACTION_TIME_SENTINEL}
        )
        obj = qs.first()
        if not obj:
            return JsonResponse({"exists": False})
        change_url = reverse(
            f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_change",
            args=[obj.pk],
        )
        return JsonResponse({"exists": True, "change_url": change_url})

    def reactivate_view(self, request, object_id):
        from apps.core.admin_handlers import ReactivateHandler

        handler = ReactivateHandler(self)
        return handler.handle(request, object_id)

    def has_change_permission(self, request, obj=None):
        """
        Remove permissão de alteração apenas para objetos inativos,
        preservando o comportamento padrão para demais casos.
        """
        has_perm = super().has_change_permission(request, obj)
        if not has_perm:
            return False
        if obj is not None and self._is_inactive_record(obj):
            return False
        return has_perm

    def render_change_form(
        self, request, context, add=False, change=False, form_url="", obj=None
    ):
        """
        Exibe mensagem informativa quando o objeto é inativo e sinaliza
        ao template via flag 'is_inactive_record' + URL de reativação.
        Injeta URL de verificação de ID duplicado para o JS do frontend.
        """
        if add:
            id_field = self._get_identifier_field_name()
            if id_field:
                context["check_id_url"] = reverse(
                    f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_check_id_exists"
                )
                context["id_field_name"] = id_field
        if obj is not None and self._is_inactive_record(obj):
            context["is_inactive_record"] = True
            context["reactivate_url"] = reverse(
                f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_reactivate",
                args=[obj.pk],
            )
            try:
                messages.info(
                    request,
                    getattr(self, "inactive_message", self.inactive_message),
                )
            except Exception:
                pass
        return super().render_change_form(request, context, add, change, form_url, obj)

    def save_model(self, request, obj, form, change):
        if not change:
            now = timezone.now()
            obj.data_registro_inicio = now
            obj.data_registro_fim = TRANSACTION_TIME_SENTINEL
        super().save_model(request, obj, form, change)

#---------------------------------------------------------------------------------------------------
# Verifica se houve alteração no form e aplica fluxo de confirmação bitemporal.
class BitemporalAdminMixin:
    """Mixin que intercepta changeform_view para aplicar fluxo de confirmação bitemporal."""

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        from apps.core.admin_handlers import BitemporalChangeHandler

        handler = BitemporalChangeHandler(self)
        response = handler.handle(request, object_id, form_url, extra_context)

        if response:
            return response

        return super().changeform_view(request, object_id, form_url, extra_context)

#---------------------------------------------------------------------------------------------------
# Formata registros de datas no banco para formato yyyy-mm-dd hh:mm:ss no timezone local
class BitemporalDateFormatMixin:
    """Mixin que fornece métodos formatados para campos de data bitemporal.
    
    Formata datas de vigência (DateField) como yyyy-mm-dd (ISO 8601)
    e datas de registro (DateTimeField) como yyyy-mm-dd hh:mm:ss no timezone local.
    
    Para usar, inclua os métodos desejados em list_display e readonly_fields:
        list_display = [..., 'data_vigencia_inicio_fmt', 'data_registro_inicio_fmt', ...]
    """

    def data_vigencia_inicio_fmt(self, obj):
        if obj.data_vigencia_inicio:
            return obj.data_vigencia_inicio.strftime('%Y-%m-%d')
        return '-'
    data_vigencia_inicio_fmt.short_description = 'Data de Início da Vigência'
    data_vigencia_inicio_fmt.admin_order_field = 'data_vigencia_inicio'

    def data_vigencia_fim_fmt(self, obj):
        if obj.data_vigencia_fim:
            return obj.data_vigencia_fim.strftime('%Y-%m-%d')
        return '-'
    data_vigencia_fim_fmt.short_description = 'Data de Fim da Vigência'
    data_vigencia_fim_fmt.admin_order_field = 'data_vigencia_fim'

    def data_registro_inicio_fmt(self, obj):
        if obj.data_registro_inicio:
            local_dt = timezone.localtime(obj.data_registro_inicio)
            return local_dt.strftime('%Y-%m-%d %H:%M:%S')
        return '-'
    data_registro_inicio_fmt.short_description = 'Data do Início do Registro'
    data_registro_inicio_fmt.admin_order_field = 'data_registro_inicio'

    def data_registro_fim_fmt(self, obj):
        if obj.data_registro_fim:
            local_dt = timezone.localtime(obj.data_registro_fim)
            return local_dt.strftime('%Y-%m-%d %H:%M:%S')
        return '-'
    data_registro_fim_fmt.short_description = 'Data do Fim do Registro'
    data_registro_fim_fmt.admin_order_field = 'data_registro_fim'

#---------------------------------------------------------------------------------------------------
# Dispara exportação para o seed correspondente após save/confirm
class AutoExportAdminMixin:
    """Mixin para disparar exportação do seed correspondente após save no Admin.
    Dispara export_resource(resource, output=docs/assets/seed_<resource>.csv) em background.
    """
    export_backup_default = False
    export_backup_dir = None

    def trigger_export(self, request, model_class):
        """
        Dispara exportação do seed para o model especificado.
        Pode ser chamado externamente (ex: após atualização bitemporal).
        """
        recurso = get_resource_for_model(model_class)
        if not recurso:
            return
        out = str(Path("docs/assets") / f"seed_{recurso}.csv")
        logging.getLogger(__name__).info("Starting export for %s", out)

        try:
            result = export_resource(recurso, output=out, scope="all", do_backup=self.export_backup_default, backup_dir=self.export_backup_dir)
            backup_msg = f" Backup: {result['backup']}" if result.get("backup") else ""
            try:
                self.message_user(
                    request,
                    f"Export completed for {out}.{backup_msg}",
                    level=messages.SUCCESS,
                )
            except Exception:
                logging.getLogger(__name__).info("Export completed for %s -> %s", recurso, out)
        except Exception:
            logging.getLogger(__name__).exception("Export failed for %s", recurso)
            try:
                self.message_user(request, f"Export failed for {out} (see logs).")
            except Exception:
                pass

    def save_model(self, request, obj, form, change):
        """
        Save and schedule export of the corresponding seed in background.
        """
        super().save_model(request, obj, form, change)
        try:
            if change and hasattr(form, "has_changed") and not form.has_changed():
                try:
                    setattr(request, "_autoexport_no_changes", True)
                    self.message_user(request, "Nenhuma alteração detectada — export pulado.")
                except Exception:
                    pass
                return
        except Exception:
            pass
        self.trigger_export(request, obj.__class__)

    def response_change(self, request, obj):
        """
        Customize Django's default change response to avoid showing a
        contradictory "was changed successfully" message when no changes
        were actually detected.
        """
        if getattr(request, "_autoexport_no_changes", False):
            opts = self.opts
            preserved_filters = self.get_preserved_filters(request)
            preserved_qsl = self._get_preserved_qsl(request, preserved_filters)

            if "_continue" in request.POST:
                redirect_url = request.path
                redirect_url = add_preserved_filters(
                    {
                        "preserved_filters": preserved_filters,
                        "preserved_qsl": preserved_qsl,
                        "opts": opts,
                    },
                    redirect_url,
                )
                return HttpResponseRedirect(redirect_url)

            if "_addanother" in request.POST:
                redirect_url = reverse(
                    "admin:%s_%s_add" % (opts.app_label, opts.model_name),
                    current_app=self.admin_site.name,
                )
                redirect_url = add_preserved_filters(
                    {
                        "preserved_filters": preserved_filters,
                        "preserved_qsl": preserved_qsl,
                        "opts": opts,
                    },
                    redirect_url,
                )
                return HttpResponseRedirect(redirect_url)

            return self.response_post_save_change(request, obj)

        return super().response_change(request, obj)
