"""
Validação **G0** / **G1.2** de ``receita_nome`` na criação no admin (spec **I4**).
"""

from __future__ import annotations

import re

from apps.core.classification_naming_abbrev import (
    calcular_radical_abreviado,
    normalize_receita_nome_base_mode,
)

_HYPHEN_CLASS = r"[\-\u2013\u2014]"


def receita_nome_vazio_no_add(nome: str) -> bool:
    """**G0.1:** True se ``trim(receita_nome)`` estiver vazio."""
    return not (nome or "").strip()


def validar_receita_nome_guardrail_g0(*, receita_nome: str) -> bool:
    """True se **G0** deve bloquear (nome vazio no add)."""
    return receita_nome_vazio_no_add(receita_nome)


def receita_nome_eh_sugestao_incompleta(nome: str, radical: str) -> bool:
    """
    **G1.2:** ``n == b`` ou ``n == b + (N7)`` sem complemento após o traço.
    """
    n = (nome or "").strip()
    b = (radical or "").strip()
    if not n or not b:
        return False
    if n == b:
        return True
    pattern = re.compile(
        r"^" + re.escape(b) + r"\s*" + _HYPHEN_CLASS + r"\s*$",
        re.UNICODE,
    )
    return bool(pattern.match(n))


def radical_efetivo_para_guardrail(
    receita_nome_base_mode: str | None,
    nome_mae: str,
    radical_abreviado: str | None = None,
) -> str | None:
    """
    **G1.2:** retorna ``b`` ou ``None`` se modo **sem_base** / vazio.
    """
    mode = normalize_receita_nome_base_mode(receita_nome_base_mode)
    if mode in ("", "sem_base"):
        return None
    if mode == "base_pai_completo":
        b = (nome_mae or "").strip()
        return b or None
    if mode == "base_pai_abrev":
        if radical_abreviado is not None:
            b = (radical_abreviado or "").strip()
        else:
            b = calcular_radical_abreviado(nome_mae).radical.strip()
        return b or None
    return None


def validar_receita_nome_guardrail_g1(
    *,
    receita_nome: str,
    receita_nome_base_mode: str | None,
    nome_mae: str,
    radical_abreviado: str | None = None,
) -> bool:
    """True se **G1** deve bloquear (sugestão incompleta)."""
    b = radical_efetivo_para_guardrail(
        receita_nome_base_mode, nome_mae, radical_abreviado=radical_abreviado
    )
    if b is None:
        return False
    return receita_nome_eh_sugestao_incompleta(receita_nome, b)
