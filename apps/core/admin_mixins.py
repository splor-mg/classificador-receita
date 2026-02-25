"""
Mixins reutilizáveis para Django Admin.

AutoExportAdminMixin — dispara export do seed após save.
BitemporalAdminMixin — fluxo de confirmação bitemporal (sobrescrever / nova vigência).
"""
import logging
import threading
from pathlib import Path

from apps.core.exporter import export_resource
from apps.core.bitemporal_registry import get_resource_for_model


class AutoExportAdminMixin:
    """Mixin para disparar exportação do seed correspondente após save no Admin.
    Dispara export_resource(resource, output=docs/assets/seed_<resource>.csv) em background.
    """
    export_backup_default = False
    export_backup_dir = None

    def save_model(self, request, obj, form, change):
        """
        Save and schedule export of the corresponding seed in background.
        """
        super().save_model(request, obj, form, change)
        # If this was an edit and no fields changed, skip export.
        try:
            if change and hasattr(form, "has_changed") and not form.has_changed():
                try:
                    self.message_user(request, "Nenhuma alteração detectada — export pulado.")
                except Exception:
                    pass
                return
        except Exception:
            # if any issue determining change state, continue with export to be safe
            pass
        recurso = get_resource_for_model(obj.__class__)
        if not recurso:
            return
        out = str(Path("docs/assets") / f"seed_{recurso}.csv")
        # log start of export (do not notify 'scheduled' message)
        logging.getLogger(__name__).info("Starting export for %s", out)

        def _bg():
            try:
                export_resource(recurso, output=out, scope="all", do_backup=self.export_backup_default, backup_dir=self.export_backup_dir)
                logging.getLogger(__name__).info("Export completed for %s -> %s", recurso, out)
            except Exception:
                logging.getLogger(__name__).exception("Export failed for %s", recurso)

        t = threading.Thread(target=_bg, daemon=True)
        # Execute synchronously in the request thread (blocking). Intended by explicit request.
        try:
            result = export_resource(recurso, output=out, scope="all", do_backup=self.export_backup_default, backup_dir=self.export_backup_dir)
            # Inform the admin user of completion
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


class BitemporalAdminMixin:
    """Mixin que intercepta changeform_view para aplicar fluxo de confirmação bitemporal."""

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        from apps.core.admin_handlers import BitemporalChangeHandler

        handler = BitemporalChangeHandler(self)
        response = handler.handle(request, object_id, form_url, extra_context)

        if response:
            return response

        return super().changeform_view(request, object_id, form_url, extra_context)
