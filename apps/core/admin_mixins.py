"""
Mixins reutilizáveis para Django Admin.

AutoExportAdminMixin — dispara export do seed após save.
BitemporalAdminMixin — fluxo de confirmação bitemporal (sobrescrever / nova vigência).
BitemporalDateFormatMixin — formatação de datas bitemporais (dd/mm/yyyy).
"""
import logging
import threading
from pathlib import Path

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters

from apps.core.exporter import export_resource
from apps.core.bitemporal_registry import get_resource_for_model


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


class BitemporalAdminMixin:
    """Mixin que intercepta changeform_view para aplicar fluxo de confirmação bitemporal."""

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        from apps.core.admin_handlers import BitemporalChangeHandler

        handler = BitemporalChangeHandler(self)
        response = handler.handle(request, object_id, form_url, extra_context)

        if response:
            return response

        return super().changeform_view(request, object_id, form_url, extra_context)
