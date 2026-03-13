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

from django.contrib import admin
from django.contrib import messages
from django.db import models as django_models
from django.db.models import Max
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters

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
# Filtro por ID de negócio
def make_id_filter(field_name, *, title=None, parameter_name=None):
    """
    Fábrica de filtros genéricos para campos de ID de negócio.

    Exemplo de uso em um ModelAdmin:
        SerieIdFilter = make_id_filter('serie_id', title='Identificador da Série')
        list_filter = [SerieIdFilter, ...]
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

SerieIdFilter = make_id_filter('serie_id', title='Identificador da Série')
ClassificacaoIdFilter = make_id_filter('classificacao_id', title='Identificador da Classificação')
NivelIdFilter = make_id_filter('nivel_id', title='Identificador do Nível')
ItemIdFilter = make_id_filter('item_id', title='Identificador do Item')
VersaoIdFilter = make_id_filter('versao_id', title='Identificador da Versão')
VarianteIdFilter = make_id_filter('variante_id', title='Identificador da Variante')
BaseLegalTecnicaIdFilter = make_id_filter('base_legal_tecnica_id', title='Identificador da Base Legal/Técnica')

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
