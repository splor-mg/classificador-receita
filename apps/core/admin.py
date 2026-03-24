from datetime import date

from django.contrib import admin

from apps.core.models import (
    SerieClassificacao,
    Classificacao,
    NivelHierarquico,
    ItemClassificacao,
    VersaoClassificacao,
    VarianteClassificacao,
    TRANSACTION_TIME_SENTINEL,
)
from apps.core.models_base_legal import BaseLegalTecnica
from apps.core.forms import (
    SerieClassificacaoForm,
    ClassificacaoForm,
    NivelHierarquicoForm,
)
from django.urls import reverse

from apps.core.admin_mixins import (
    RegistroAtivoFilter,
    SerieIdFilter,
    ClassificacaoIdFilter,
    NivelIdFilter,
    ItemIdFilter,
    VersaoIdFilter,
    VarianteIdFilter,
    BaseLegalTecnicaIdFilter,
    CoreChangeSaveFormSubmitMixin,
    BitemporalInactiveReadOnlyMixin,
    BitemporalAdminMixin,
    BitemporalDateFormatMixin,
    AutoExportAdminMixin,
    SemanticForeignKeyAdminMixin,
    BitemporalObjectActionsMixin,
)


@admin.register(SerieClassificacao)
class SerieClassificacaoAdmin(
    BitemporalObjectActionsMixin,
    BitemporalAdminMixin,
    BitemporalInactiveReadOnlyMixin,
    BitemporalDateFormatMixin,
    CoreChangeSaveFormSubmitMixin,
    AutoExportAdminMixin,
    admin.ModelAdmin,
):
    list_display = [
        'serie_id',
        'serie_nome',
        'orgao_responsavel_both',
        'data_vigencia_inicio_fmt',
        'data_vigencia_fim_fmt',
        'data_registro_inicio_fmt',
        'data_registro_fim_fmt',
    ]
    ordering = [
        'serie_ref',
        'data_vigencia_inicio',
        'data_registro_inicio',
    ]
    list_filter = [
        RegistroAtivoFilter,
        SerieIdFilter,
        'data_vigencia_inicio',
        'data_registro_inicio',
    ]
    search_fields = [
        'serie_id',
        'serie_nome',
        'serie_descricao',
    ]
    readonly_fields = [
        'serie_ref',
        'data_registro_inicio_fmt',
        'data_registro_fim_fmt',
    ]
    date_hierarchy = 'data_vigencia_inicio'
    fields = [
        ('serie_id', 'serie_ref'),
        'serie_nome',
        'serie_descricao',
        'orgao_responsavel',
        'data_vigencia_inicio',
        'data_vigencia_fim',
        'data_registro_inicio_fmt',
        'data_registro_fim_fmt',
    ]
    form = SerieClassificacaoForm

    class Media:
        js = ("core/admin_bitemporal_date_shortcuts.js",)

    def orgao_responsavel_both(self, obj):
        """
        Mostrar código armazenado (value) e rótulo (label) das choices.
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
class ClassificacaoAdmin(
    SemanticForeignKeyAdminMixin,
    BitemporalObjectActionsMixin,
    BitemporalAdminMixin,
    BitemporalInactiveReadOnlyMixin,
    BitemporalDateFormatMixin,
    CoreChangeSaveFormSubmitMixin,
    AutoExportAdminMixin,
    admin.ModelAdmin,
):
    # Garante verbose_name do FK nas colunas *_raw geradas pelo mixin (__init_subclass__).
    model = Classificacao
    list_display = [
        "classificacao_id",
        "classificacao_nome",
        "serie_id_raw",
        "tipo_classificacao",
        "numero_niveis",
        "numero_digitos",
        "data_vigencia_inicio_fmt",
        "data_vigencia_fim_fmt",
        "data_registro_inicio_fmt",
        "data_registro_fim_fmt",
    ]
    ordering = [
        'classificacao_ref',
        'data_vigencia_inicio',
        'data_registro_inicio',
    ]
    list_filter = [
        RegistroAtivoFilter,
        ClassificacaoIdFilter,
        "tipo_classificacao",
        "numero_niveis",
        "serie_id",
        "data_vigencia_inicio",
        "data_registro_inicio",
    ]
    search_fields = ["classificacao_id", "classificacao_nome", "classificacao_descricao"]
    readonly_fields = ["data_registro_inicio_fmt", "data_registro_fim_fmt"]
    date_hierarchy = "data_vigencia_inicio"
    raw_id_fields = ["serie_id", "base_legal_tecnica_id"]
    fields = [
        ("classificacao_id", "classificacao_ref"),
        "classificacao_nome",
        "serie_id",
        "classificacao_descricao",
        "tipo_classificacao",
        "numero_niveis",
        "numero_digitos",
        "base_legal_tecnica_id",
        "data_vigencia_inicio",
        "data_vigencia_fim",
        "data_registro_inicio_fmt",
        "data_registro_fim_fmt",
    ]
    form = ClassificacaoForm
    semantic_fk_config = {
        "serie_id": {
            "kind": "serie",
            "model": SerieClassificacao,
            "semantic_field": "serie_id",
            "display_label": lambda obj: f"{obj.serie_id} - {obj.serie_nome}",
        },
        "base_legal_tecnica_id": {
            "kind": "base_legal_tecnica",
            "model": BaseLegalTecnica,
            "semantic_field": "base_legal_tecnica_id",
            "display_label": lambda obj: str(obj),
        },
    }

    class Media:
        js = ("core/admin_bitemporal_date_shortcuts.js",)


@admin.register(NivelHierarquico)
class NivelHierarquicoAdmin(
    SemanticForeignKeyAdminMixin,
    BitemporalAdminMixin,
    BitemporalInactiveReadOnlyMixin,
    BitemporalDateFormatMixin,
    CoreChangeSaveFormSubmitMixin,
    AutoExportAdminMixin,
    admin.ModelAdmin,
):
    model = NivelHierarquico
    list_display = [
        'nivel_id',
        'nivel_nome',
        'classificacao_id_raw',
        'data_vigencia_inicio_fmt',
        'data_vigencia_fim_fmt',
        'data_registro_inicio_fmt',
        'data_registro_fim_fmt',
    ]
    ordering = [
        'nivel_ref',
        'data_vigencia_inicio',
        'data_registro_inicio',
    ]
    list_filter = [
        RegistroAtivoFilter,
        NivelIdFilter,
        'nivel_numero',
        'tipo_codigo',
        'classificacao_id',
        'data_vigencia_inicio',
        'data_registro_inicio',
    ]
    search_fields = ['nivel_id', 'nivel_nome', 'nivel_descricao']
    readonly_fields = ['data_registro_inicio_fmt', 'data_registro_fim_fmt']
    date_hierarchy = 'data_vigencia_inicio'
    raw_id_fields = ['classificacao_id']
    fields = [
        ('nivel_id', 'nivel_ref'),
        'classificacao_id',
        'nivel_numero',
        'nivel_nome',
        'nivel_descricao',
        'estrutura_codigo',
        'numero_digitos',
        'tipo_codigo',
        'data_vigencia_inicio',
        'data_vigencia_fim',
        'data_registro_inicio_fmt',
        'data_registro_fim_fmt',
    ]
    form = NivelHierarquicoForm
    semantic_fk_config = {
        "classificacao_id": {
            "kind": "classificacao",
            "model": Classificacao,
            "semantic_field": "classificacao_id",
            "display_label": lambda obj: f"{obj.classificacao_id} - {obj.classificacao_nome}",
        },
    }

    class Media:
        js = ("core/admin_bitemporal_date_shortcuts.js",)


@admin.register(ItemClassificacao)
class ItemClassificacaoAdmin(CoreChangeSaveFormSubmitMixin, BitemporalInactiveReadOnlyMixin, AutoExportAdminMixin, admin.ModelAdmin):
    list_display = ['receita_cod', 'item_id', 'receita_nome', 'nivel_id', 'matriz', 'item_gerado', 'data_vigencia_inicio']
    list_filter = [RegistroAtivoFilter, ItemIdFilter, 'matriz', 'item_gerado', 'nivel_id', 'data_vigencia_inicio']
    search_fields = ['receita_cod', 'receita_nome', 'item_id']
    readonly_fields = ['data_registro_inicio', 'data_registro_fim']
    date_hierarchy = 'data_vigencia_inicio'
    raw_id_fields = ['classificacao_id', 'nivel_id', 'parent_item_id', 'base_legal_tecnica_id']


@admin.register(VersaoClassificacao)
class VersaoClassificacaoAdmin(CoreChangeSaveFormSubmitMixin, BitemporalInactiveReadOnlyMixin, AutoExportAdminMixin, admin.ModelAdmin):
    list_display = ['versao_id', 'versao_numero', 'versao_nome', 'classificacao', 'data_lancamento', 'data_vigencia_inicio']
    list_filter = [RegistroAtivoFilter, VersaoIdFilter, 'classificacao', 'data_lancamento', 'data_vigencia_inicio']
    search_fields = ['versao_id', 'versao_numero', 'versao_nome', 'versao_descricao']
    readonly_fields = ['data_registro_inicio', 'data_registro_fim']
    date_hierarchy = 'data_vigencia_inicio'
    raw_id_fields = ['classificacao']


@admin.register(VarianteClassificacao)
class VarianteClassificacaoAdmin(CoreChangeSaveFormSubmitMixin, BitemporalInactiveReadOnlyMixin, AutoExportAdminMixin, admin.ModelAdmin):
    list_display = ['variante_id', 'variante_nome', 'tipo_variante', 'classificacao', 'versao', 'data_vigencia_inicio']
    list_filter = [RegistroAtivoFilter, VarianteIdFilter, 'tipo_variante', 'classificacao', 'versao', 'data_vigencia_inicio']
    search_fields = ['variante_id', 'variante_nome', 'variante_descricao', 'proposito']
    readonly_fields = ['data_registro_inicio', 'data_registro_fim']
    date_hierarchy = 'data_vigencia_inicio'
    raw_id_fields = ['classificacao', 'versao']


@admin.register(BaseLegalTecnica)
class BaseLegalTecnicaAdmin(CoreChangeSaveFormSubmitMixin, AutoExportAdminMixin, admin.ModelAdmin):
    list_display = ['base_legal_tecnica_id', 'titulo_norma', 'tipo_legal', 'esfera_federativa', 'data_edicao']
    list_filter = [BaseLegalTecnicaIdFilter, 'tipo_legal', 'esfera_federativa', 'data_edicao']
    search_fields = ['base_legal_tecnica_id', 'titulo_norma', 'ementa']
    date_hierarchy = 'data_edicao'
