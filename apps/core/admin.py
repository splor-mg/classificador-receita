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
from apps.core.forms import SerieClassificacaoForm
from apps.core.admin_mixins import (
    AutoExportAdminMixin,
    BitemporalAdminMixin,
    BitemporalDateFormatMixin,
)


class RegistroAtivoFilter(admin.SimpleListFilter):
    """Filtro para registros ativos (correntes, históricos e futuros) e inativos em termos de registro/vigência."""
    title = 'Status do Registro'
    parameter_name = 'registro_ativo'

    def lookups(self, request, model_admin):
        return (
            ('ativo_corrente', 'Ativos (Ano Corrente)'),
            ('ativo_futuro', 'Ativos (Futuro)'),
            ('ativo_historico', 'Ativos (Histórico)'),
            ('inativo', 'Inativos'),
        )

    def queryset(self, request, queryset):
        ano_corrente = date.today().year
        primeiro_dia_ano = date(ano_corrente, 1, 1)

        ultimo_dia_ano = date(ano_corrente, 12, 31)

        if self.value() == 'ativo_corrente':
            return queryset.filter(
                data_registro_fim=TRANSACTION_TIME_SENTINEL,
                data_vigencia_inicio__lte=ultimo_dia_ano,
                data_vigencia_fim__gte=primeiro_dia_ano,
            )
        if self.value() == 'ativo_futuro':
            return queryset.filter(
                data_registro_fim=TRANSACTION_TIME_SENTINEL,
                data_vigencia_fim__gt=primeiro_dia_ano,
            )
        if self.value() == 'ativo_historico':
            return queryset.filter(
                data_registro_fim=TRANSACTION_TIME_SENTINEL,
            )
        if self.value() == 'inativo':
            return queryset.exclude(data_registro_fim=TRANSACTION_TIME_SENTINEL)
        return queryset


@admin.register(SerieClassificacao)
class SerieClassificacaoAdmin(
    BitemporalAdminMixin,
    BitemporalDateFormatMixin,
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
        'data_vigencia_inicio',
        'data_registro_inicio',
    ]
    search_fields = [
        'serie_id',
        'serie_nome',
        'descricao',
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
        'descricao',
        'orgao_responsavel',
        'data_vigencia_inicio',
        'data_vigencia_fim',
        'data_registro_inicio_fmt',
        'data_registro_fim_fmt',
    ]
    form = SerieClassificacaoForm

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
