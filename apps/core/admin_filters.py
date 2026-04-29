"""
Filtros de listagem do Django Admin específicos do app ``core``.

As fábricas genéricas ficam em ``admin_mixins``; aqui ficam apenas as classes
instanciadas para este domínio (IDs de negócio e FKs com rótulo semântico).
"""

from django.contrib import admin

from apps.core.admin_mixins import make_filter_fk_id, make_filter_local_id
from apps.core.models import BaseLegalTecnica, Classificacao, ItemClassificacao, NivelHierarquico, TRANSACTION_TIME_SENTINEL


#---------------------------------------------------------------------------------------------------
# make_filter_local_id: campo de id na própria tabela da changelist

SerieIdFilter = make_filter_local_id("serie_id", title="Identificador da Série")
ClassificacaoIdFilter = make_filter_local_id("classificacao_id", title="Identificador da Classificação")
NivelIdFilter = make_filter_local_id("nivel_id", title="Identificador do Nível")
ItemIdFilter = make_filter_local_id("item_id", title="Identificador do Item")
VersaoIdFilter = make_filter_local_id("versao_id", title="Identificador da Versão")
VarianteIdFilter = make_filter_local_id("variante_id", title="Identificador da Variante")
BaseLegalTecnicaIdFilter = make_filter_local_id("base_legal_tecnica_id", title="Identificador da Base Legal/Técnica")

#---------------------------------------------------------------------------------------------------
# make_filter_fk_id: FK com rótulo semântico na sidebar (valor na URL = PK relacionada)

SerieIdFKFilter = make_filter_fk_id(Classificacao, "serie_id")
NivelIdFKFilter = make_filter_fk_id(NivelHierarquico, "classificacao_id"
)


def make_item_prefix_filter(*, title: str, prefix_len: int, nivel_numero: int):
    """
    Filtro lateral para ItemClassificacao baseado em prefixo de `receita_cod`.

    - opções: itens ativos (`data_registro_fim` sentinela) no nível informado;
    - rótulo: `receita_nome` mais recente por prefixo (opção B).
    """
    if prefix_len <= 0:
        raise ValueError("prefix_len deve ser maior que zero")

    class ItemPrefixFilter(admin.SimpleListFilter):
        title = ""
        parameter_name = ""

        def lookups(self, request, model_admin):
            qs = (
                ItemClassificacao.objects.filter(
                    data_registro_fim=TRANSACTION_TIME_SENTINEL,
                    nivel_id__nivel_numero=nivel_numero,
                )
                .exclude(receita_cod__isnull=True)
                .exclude(receita_cod__exact="")
                .order_by("-data_vigencia_inicio", "-data_registro_inicio", "-pk")
                .values_list("receita_cod", "receita_nome")
            )
            by_prefix = {}
            for receita_cod, receita_nome in qs:
                prefix = str(receita_cod)[:prefix_len]
                if len(prefix) < prefix_len:
                    continue
                if prefix in by_prefix:
                    continue
                label = (receita_nome or "").strip() or prefix
                by_prefix[prefix] = label
            return [(p, f"{p} - {by_prefix[p]}") for p in sorted(by_prefix.keys())]

        def queryset(self, request, queryset):
            value = self.value()
            if value:
                return queryset.filter(
                    data_registro_fim=TRANSACTION_TIME_SENTINEL,
                    receita_cod__startswith=value,
                )
            return queryset

    ItemPrefixFilter.title = title
    ItemPrefixFilter.parameter_name = f"prefix_{prefix_len}_nivel_{nivel_numero}"
    return ItemPrefixFilter


CategoriaPrefixFilter = make_item_prefix_filter(
    title="Por Categoria",
    prefix_len=1,
    nivel_numero=1,
)

CategoriaOrigemPrefixFilter = make_item_prefix_filter(
    title="Por Categoria-Origem",
    prefix_len=2,
    nivel_numero=2,
)


class NivelHierarquicoRecenteFilter(admin.SimpleListFilter):
    """
    Filtro deduplicado por número do nível hierárquico.

    Exibe apenas a descrição mais recente por `nivel_numero`, evitando repetição
    de versões históricas no painel lateral.
    """

    title = "Por Nível Hierárquico"
    parameter_name = "nivel_numero_recente"

    def lookups(self, request, model_admin):
        qs = (
            NivelHierarquico.objects.filter(data_registro_fim=TRANSACTION_TIME_SENTINEL)
            .order_by("-data_vigencia_inicio", "-data_registro_inicio", "-pk")
            .values_list("nivel_numero", "nivel_nome")
        )
        by_nivel = {}
        for nivel_numero, nivel_nome in qs:
            if nivel_numero in by_nivel:
                continue
            label = f"Nível {nivel_numero}: {(nivel_nome or '').strip()}".strip()
            by_nivel[nivel_numero] = label
        return [(str(n), by_nivel[n]) for n in sorted(by_nivel.keys())]

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            try:
                nivel_num = int(value)
            except (TypeError, ValueError):
                return queryset
            return queryset.filter(nivel_id__nivel_numero=nivel_num)
        return queryset


class BaseLegalTecnicaSemanticFilter(admin.SimpleListFilter):
    """
    Filtro deduplicado por identificador semântico de base legal/técnica.

    Evita repetição por edições/títulos distintos do mesmo identificador.
    """

    title = "Por Base Legal/Técnica de Referência"
    parameter_name = "base_legal_tecnica_semantic_id"

    def lookups(self, request, model_admin):
        values = BaseLegalTecnica.objects.exclude(base_legal_tecnica_id__isnull=True).exclude(
            base_legal_tecnica_id__exact=""
        ).values_list("base_legal_tecnica_id", flat=True).distinct().order_by("base_legal_tecnica_id")
        return [(v, v) for v in values if v not in (None, "")]

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(base_legal_tecnica_id__base_legal_tecnica_id=value)
        return queryset
