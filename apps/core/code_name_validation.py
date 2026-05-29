"""
Validação **G0** / **G1.2** de ``receita_nome`` na criação no admin (spec **I4**).

**G1.2** (novo): predicado **único** de bloqueio — ``trim(receita_nome)`` termina
com um separador flexível **(N7)** (`-`, `–`, `—`), opcionalmente seguido apenas
de espaços em branco. Vale em **todos** os modos do **add** (`base_pai_completo`,
`base_pai_abrev`, `sem_base` e modo vazio). Não consulta o radical efetivo ``b``.

**G1.5**: a mensagem do bloqueio é escolhida em duas variantes:
  * **G1.5.a** (``receita_nome_submit_sugestao_literal_error``) — quando ``n`` casa
    com ``b_completo + (N5)`` **ou** ``b_abreviado + (N5)`` (com (N7) flexível e
    espaços ASCII opcionais ao redor do traço);
  * **G1.5.b** (``receita_nome_submit_traco_final_error``) — caso contrário,
    inclusive em ``sem_base`` (onde ``b`` é indefinido).
"""

from __future__ import annotations

import re

from apps.core.code_name_abbrev import (
    calcular_radical_abreviado,
    normalize_receita_nome_base_mode,
)
from apps.core.code_name_messages import (
    MENSAGEM_SUGESTAO_LITERAL_KEY,
    MENSAGEM_TRACO_FINAL_KEY,
)

_HYPHEN_CLASS = r"[\-\u2013\u2014]"

_TRAILING_HYPHEN_RE = re.compile(
    r".*" + _HYPHEN_CLASS + r"\s*\Z",
    re.UNICODE | re.DOTALL,
)


def receita_nome_vazio_no_add(nome: str) -> bool:
    """**G0.1:** True se ``trim(receita_nome)`` estiver vazio."""
    return not (nome or "").strip()


def validar_receita_nome_guardrail_g0(*, receita_nome: str) -> bool:
    """True se **G0** deve bloquear (nome vazio no add)."""
    return receita_nome_vazio_no_add(receita_nome)


def receita_nome_termina_com_traco(nome: str) -> bool:
    """
    **G1.2** (predicado único): True quando ``trim(nome)`` termina com **(N7)**
    (hífen ASCII, en dash ou em dash), opcionalmente seguido apenas de espaços.

    Independente do modo e do radical efetivo ``b``.
    """
    n = (nome or "").strip()
    if not n:
        return False
    return bool(_TRAILING_HYPHEN_RE.match(n))


def receita_nome_eh_sugestao_literal(nome: str, radical: str) -> bool:
    """
    True quando ``n`` casa com ``b + (N7)`` (com (N7) flexível e espaços ASCII
    opcionais ao redor do traço, em qualquer ortografia: `-`, `–`, `—`).

    Usado **somente** para selecionar entre **G1.5.a** (literal) e **G1.5.b**
    (traço final pendurado). Não é predicado de bloqueio — o bloqueio é dado
    por :func:`receita_nome_termina_com_traco`.
    """
    n = (nome or "").strip()
    b = (radical or "").strip()
    if not n or not b:
        return False
    pattern = re.compile(
        r"^" + re.escape(b) + r"\s*" + _HYPHEN_CLASS + r"\s*\Z",
        re.UNICODE,
    )
    return bool(pattern.match(n))


def radical_efetivo_para_guardrail(
    receita_nome_base_mode: str | None,
    nome_mae: str,
    radical_abreviado: str | None = None,
) -> str | None:
    """
    Retorna ``b`` (radical efetivo) conforme o modo.

    Sob a nova **G1.2**, o predicado de bloqueio **não** depende deste valor —
    ele é mantido apenas como auxiliar para a seleção de mensagem em fluxos
    legados (modo-aware). Para o servidor, a seleção entre G1.5.a / G1.5.b é
    feita por :func:`validar_receita_nome_guardrail_g1`, que considera tanto
    ``b_completo`` quanto ``b_abreviado`` independentemente do modo selecionado.
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
    nome_mae: str = "",
    radical_abreviado: str | None = None,
) -> tuple[bool, str | None]:
    """
    **G1.2 + G1.5:** retorna ``(bloquear, chave_mensagem)``.

    * ``bloquear = True`` quando ``trim(receita_nome)`` termina com **(N7)**.
    * ``chave_mensagem`` é:
        - ``"receita_nome_submit_sugestao_literal_error"`` (**G1.5.a**)
          quando ``n`` coincide com ``b_completo + (N5)`` **ou** ``b_abreviado + (N5)``
          (com (N7) flexível e espaços ASCII opcionais ao redor do traço);
        - ``"receita_nome_submit_traco_final_error"`` (**G1.5.b**) caso contrário,
          inclusive em ``sem_base`` (onde ``b`` é indefinido).

    O predicado de bloqueio **não** depende de ``receita_nome_base_mode``; os
    radicais (``nome_mae`` e ``radical_abreviado``) só são consultados para a
    seleção da mensagem. Quando ``nome_mae`` está vazio (item mãe ausente) e
    ``radical_abreviado`` é ``None``, devolve ``G1.5.b`` por padrão.
    """
    if not receita_nome_termina_com_traco(receita_nome):
        return False, None

    b_completo = (nome_mae or "").strip()
    if radical_abreviado is not None:
        b_abreviado = (radical_abreviado or "").strip()
    elif b_completo:
        b_abreviado = calcular_radical_abreviado(b_completo).radical.strip()
    else:
        b_abreviado = ""

    if b_completo and receita_nome_eh_sugestao_literal(receita_nome, b_completo):
        return True, MENSAGEM_SUGESTAO_LITERAL_KEY
    if b_abreviado and receita_nome_eh_sugestao_literal(receita_nome, b_abreviado):
        return True, MENSAGEM_SUGESTAO_LITERAL_KEY

    return True, MENSAGEM_TRACO_FINAL_KEY
