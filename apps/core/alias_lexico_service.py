"""
Serviços para abreviação léxica do radical de nomenclatura (evolução nas etapas 3–4).

Por ora expõe apenas acesso às entradas ativas de ``AliasLexico`` e a lista de conectivos.
A pipeline (frases longas → palavras → remoção de conectivos) será implementada quando
houver dados curados e integração com o admin de ItemClassificacao.
"""

from __future__ import annotations

from typing import Iterable, Tuple

from django.db.models import QuerySet
from django.utils import timezone

from apps.core.classification_naming_connectives import NOME_CLASSIFICACAO_CONNECTIVOS_FIXOS
from apps.core.models import TRANSACTION_TIME_SENTINEL
from apps.core.models_alias_lexico import AliasLexico


def _transaction_sentinel_orm():
    s = TRANSACTION_TIME_SENTINEL
    if timezone.is_naive(s):
        return timezone.make_aware(s, timezone.get_current_timezone())
    return s


def connectivos_fixos_nome_classificacao() -> frozenset[str]:
    """Lista fixa de conectivos/palavras funcionais usados na compactação."""
    return NOME_CLASSIFICACAO_CONNECTIVOS_FIXOS


def queryset_alias_lexico_ativos() -> QuerySet[AliasLexico]:
    """Entradas cuja vigência de registro ainda é a sentinela (ativo)."""
    return AliasLexico.objects.filter(data_registro_fim=_transaction_sentinel_orm())


def iter_alias_lexico_ativos_ordenados() -> Iterable[Tuple[str, str]]:
    """
    Pares (termo, abreviação) ativos, ordenados para uso futuro na pipeline:

    1. Termos com mais de uma palavra, por comprimento do termo decrescente.
    2. Termos de uma palavra, por comprimento decrescente.
    """
    qs = list(queryset_alias_lexico_ativos().values_list("termo", "abreviacao"))

    def sort_key(item: Tuple[str, str]) -> Tuple[int, int, str]:
        termo, _ = item
        t = (termo or "").strip()
        palavras = len(t.split())
        fase = 0 if palavras > 1 else 1
        return (fase, -len(t), t)

    return sorted(qs, key=sort_key)
