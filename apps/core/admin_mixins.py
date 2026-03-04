"""
Mixins reutilizáveis para Django Admin.

AutoExportAdminMixin — dispara export do seed após save.
BitemporalAdminMixin — fluxo de confirmação bitemporal (sobrescrever / nova vigência).
BitemporalDateFormatMixin — formatação de datas bitemporais (dd/mm/yyyy).
"""
import logging
from datetime import date
from pathlib import Path

from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters

from apps.core.exporter import export_resource
from apps.core.bitemporal_registry import get_resource_for_model
from apps.core.models import TRANSACTION_TIME_SENTINEL

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
        ano_corrente = date.today().year
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
                data_vigencia_fim__gt=primeiro_dia_ano,
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
                self.message_user(request, f"Export completed for {out}.{backup_msg}")
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
