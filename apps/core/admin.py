from django.contrib import admin
from apps.core.models import (
    SerieClassificacao,
    Classificacao,
    NivelHierarquico,
    ItemClassificacao,
    VersaoClassificacao,
    VarianteClassificacao,
)
from apps.core.models_base_legal import BaseLegalTecnica
from apps.core.exporter import export_resource
import threading
import logging
from apps.core.bitemporal_registry import get_resource_for_model
from pathlib import Path


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


@admin.register(SerieClassificacao)
class SerieClassificacaoAdmin(AutoExportAdminMixin, admin.ModelAdmin):
    list_display = ['serie_id', 'serie_nome', 'orgao_responsavel_both', 'data_vigencia_inicio', 'data_vigencia_fim', 'data_registro_inicio']
    list_filter = ['data_vigencia_inicio', 'data_registro_inicio']
    search_fields = ['serie_id', 'serie_nome', 'descricao']
    readonly_fields = ['data_registro_inicio', 'data_registro_fim']
    date_hierarchy = 'data_vigencia_inicio'
    def orgao_responsavel_both(self, obj):
        """
        Mostrar código armazenado (value) e rótulo (label) das choices, ex: "STN-BRA — Secretaria do Tesouro Nacional".
        """
        try:
            label = obj.get_orgao_responsavel_display()
        except Exception:
            label = ''
        if label:
            return f"{obj.orgao_responsavel} — {label}"
        return obj.orgao_responsavel
    orgao_responsavel_both.short_description = 'Órgão Responsável'


@admin.register(Classificacao)
class ClassificacaoAdmin(AutoExportAdminMixin, admin.ModelAdmin):
    list_display = ['classificacao_id', 'classificacao_nome', 'serie_id', 'tipo_classificacao', 'numero_niveis', 'data_vigencia_inicio']
    list_filter = ['tipo_classificacao', 'numero_niveis', 'serie_id', 'data_vigencia_inicio']
    search_fields = ['classificacao_id', 'classificacao_nome', 'descricao']
    readonly_fields = ['data_registro_inicio', 'data_registro_fim']
    date_hierarchy = 'data_vigencia_inicio'
    raw_id_fields = ['serie_id', 'base_legal_tecnica_id']


@admin.register(NivelHierarquico)
class NivelHierarquicoAdmin(AutoExportAdminMixin, admin.ModelAdmin):
    list_display = ['nivel_id', 'nivel_numero', 'nivel_nome', 'classificacao_id', 'tipo_codigo', 'data_vigencia_inicio']
    list_filter = ['nivel_numero', 'tipo_codigo', 'classificacao_id', 'data_vigencia_inicio']
    search_fields = ['nivel_id', 'nivel_nome', 'descricao']
    readonly_fields = ['data_registro_inicio', 'data_registro_fim']
    date_hierarchy = 'data_vigencia_inicio'
    raw_id_fields = ['classificacao_id']


@admin.register(ItemClassificacao)
class ItemClassificacaoAdmin(AutoExportAdminMixin, admin.ModelAdmin):
    list_display = ['receita_cod', 'item_id', 'receita_nome', 'nivel_id', 'matriz', 'item_gerado', 'data_vigencia_inicio']
    list_filter = ['matriz', 'item_gerado', 'nivel_id', 'data_vigencia_inicio']
    search_fields = ['receita_cod', 'receita_nome', 'item_id']
    readonly_fields = ['data_registro_inicio', 'data_registro_fim']
    date_hierarchy = 'data_vigencia_inicio'
    raw_id_fields = ['classificacao_id', 'nivel_id', 'parent_item_id', 'base_legal_tecnica_id']


@admin.register(VersaoClassificacao)
class VersaoClassificacaoAdmin(AutoExportAdminMixin, admin.ModelAdmin):
    list_display = ['versao_id', 'versao_numero', 'versao_nome', 'classificacao', 'data_lancamento', 'data_vigencia_inicio']
    list_filter = ['classificacao', 'data_lancamento', 'data_vigencia_inicio']
    search_fields = ['versao_id', 'versao_numero', 'versao_nome', 'descricao']
    readonly_fields = ['data_registro_inicio', 'data_registro_fim']
    date_hierarchy = 'data_vigencia_inicio'
    raw_id_fields = ['classificacao']


@admin.register(VarianteClassificacao)
class VarianteClassificacaoAdmin(AutoExportAdminMixin, admin.ModelAdmin):
    list_display = ['variante_id', 'variante_nome', 'tipo_variante', 'classificacao', 'versao', 'data_vigencia_inicio']
    list_filter = ['tipo_variante', 'classificacao', 'versao', 'data_vigencia_inicio']
    search_fields = ['variante_id', 'variante_nome', 'descricao', 'proposito']
    readonly_fields = ['data_registro_inicio', 'data_registro_fim']
    date_hierarchy = 'data_vigencia_inicio'
    raw_id_fields = ['classificacao', 'versao']


@admin.register(BaseLegalTecnica)
class BaseLegalTecnicaAdmin(AutoExportAdminMixin, admin.ModelAdmin):
    list_display = ['base_legal_tecnica_id', 'titulo_norma', 'tipo_legal', 'esfera_federativa', 'data_edicao']
    list_filter = ['tipo_legal', 'esfera_federativa', 'data_edicao']
    search_fields = ['base_legal_tecnica_id', 'titulo_norma', 'ementa']
    date_hierarchy = 'data_edicao'
