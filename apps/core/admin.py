from django.contrib import admin
from .models import (
    SerieClassificacao,
    ClassificacaoReceita,
    NivelHierarquico,
    ItemClassificacao,
    VersaoClassificacao,
    VarianteClassificacao,
)


@admin.register(SerieClassificacao)
class SerieClassificacaoAdmin(admin.ModelAdmin):
    list_display = ['serie_id', 'serie_nome', 'orgao_responsavel', 'data_vigencia_inicio', 'data_vigencia_fim', 'data_registro_inicio']
    list_filter = ['data_vigencia_inicio', 'data_registro_inicio']
    search_fields = ['serie_id', 'serie_nome', 'descricao']
    readonly_fields = ['data_registro_inicio', 'data_registro_fim']
    date_hierarchy = 'data_vigencia_inicio'


@admin.register(ClassificacaoReceita)
class ClassificacaoReceitaAdmin(admin.ModelAdmin):
    list_display = ['classificacao_id', 'classificacao_nome', 'serie', 'tipo_classificacao', 'numero_niveis', 'data_vigencia_inicio']
    list_filter = ['tipo_classificacao', 'numero_niveis', 'serie', 'data_vigencia_inicio']
    search_fields = ['classificacao_id', 'classificacao_nome', 'descricao']
    readonly_fields = ['data_registro_inicio', 'data_registro_fim']
    date_hierarchy = 'data_vigencia_inicio'
    raw_id_fields = ['serie']


@admin.register(NivelHierarquico)
class NivelHierarquicoAdmin(admin.ModelAdmin):
    list_display = ['nivel_id', 'nivel_numero', 'nivel_nome', 'classificacao', 'tipo_codigo', 'data_vigencia_inicio']
    list_filter = ['nivel_numero', 'tipo_codigo', 'classificacao', 'data_vigencia_inicio']
    search_fields = ['nivel_id', 'nivel_nome', 'descricao']
    readonly_fields = ['data_registro_inicio', 'data_registro_fim']
    date_hierarchy = 'data_vigencia_inicio'
    raw_id_fields = ['classificacao']


@admin.register(ItemClassificacao)
class ItemClassificacaoAdmin(admin.ModelAdmin):
    list_display = ['codigo_completo', 'codigo_numerico', 'nome_oficial', 'nivel', 'valido_atualmente', 'data_vigencia_inicio']
    list_filter = ['valido_atualmente', 'item_gerado', 'nivel', 'data_vigencia_inicio']
    search_fields = ['codigo_completo', 'codigo_numerico', 'nome_oficial', 'item_id']
    readonly_fields = ['data_registro_inicio', 'data_registro_fim']
    date_hierarchy = 'data_vigencia_inicio'
    raw_id_fields = ['nivel', 'parent_item']


@admin.register(VersaoClassificacao)
class VersaoClassificacaoAdmin(admin.ModelAdmin):
    list_display = ['versao_id', 'versao_numero', 'versao_nome', 'classificacao', 'data_lancamento', 'data_vigencia_inicio']
    list_filter = ['classificacao', 'data_lancamento', 'data_vigencia_inicio']
    search_fields = ['versao_id', 'versao_numero', 'versao_nome', 'descricao']
    readonly_fields = ['data_registro_inicio', 'data_registro_fim']
    date_hierarchy = 'data_vigencia_inicio'
    raw_id_fields = ['classificacao']


@admin.register(VarianteClassificacao)
class VarianteClassificacaoAdmin(admin.ModelAdmin):
    list_display = ['variante_id', 'variante_nome', 'tipo_variante', 'classificacao', 'versao', 'data_vigencia_inicio']
    list_filter = ['tipo_variante', 'classificacao', 'versao', 'data_vigencia_inicio']
    search_fields = ['variante_id', 'variante_nome', 'descricao', 'proposito']
    readonly_fields = ['data_registro_inicio', 'data_registro_fim']
    date_hierarchy = 'data_vigencia_inicio'
    raw_id_fields = ['classificacao', 'versao']
