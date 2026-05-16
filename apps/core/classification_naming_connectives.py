"""
Lista canónica de conectivos omitíveis e regras de pontuação na compactação (**A6**).

Usada por:
- modo **Abreviado** na criação de item (``classification_naming_abbrev``);
- inferência da lista de abreviações (só ``LEXICO_CONNECTIVOS_FIXOS`` em ``alias_lexico_infer``).

Comparar tokens lexicais com ``casefold()`` (acentos preservados como nos dados).
"""

from __future__ import annotations

import re

# Fonte única de verdade — não duplicar noutros módulos.
LEXICO_CONNECTIVOS_FIXOS = frozenset(
    {
        "a",
        "o",
        "as",
        "os",
        "e",
        "ou",
        "de",
        "da",
        "do",
        "das",
        "dos",
        "em",
        "na",
        "no",
        "nas",
        "nos",
        "por",
        "para",
        "com",
        "sem",
        "ao",
        "aos",
        "à",
        "às",
        "pelo",
        "pela",
        "pelos",
        "pelas",
        "sobre",
        "um",
        "uma",
        "uns",
        "umas",
    }
)

# Alias histórico (spec criar nome / ``alias_lexico_service``).
NOME_CLASSIFICACAO_CONNECTIVOS_FIXOS = LEXICO_CONNECTIVOS_FIXOS

# **A6.1** — retirar das extremidades de cada token (sozinhos ou colados à palavra).
LEXICO_PONTUACAO_OMITIR_NAS_EXTREMIDADES = frozenset(",;!:!")

# **A6.3** — preservar ponto só em abreviação por encurtamento **(iv)** (spec lista abreviações).
RE_TOKEN_ABREVIVACAO_IV = re.compile(r"^[A-Za-zÀ-ÿ]{1,8}\.$", re.IGNORECASE)


def token_e_abreviacao_encurtamento_iv(token: str) -> bool:
    """True se o token integral casa com o padrão **(iv)** (ex.: ``Princ.``, ``Contrib.``)."""
    return bool(RE_TOKEN_ABREVIVACAO_IV.fullmatch((token or "").strip()))


def normalizar_token_pontuacao_a6(token: str) -> str:
    """
    **A6.1** + **A6.3** — limpa pontuação nas extremidades do token.

    Preserva tokens **(iv)** intactos. Remove ``,;!:!`` das extremidades; remove ``.`` das
    extremidades quando o token **não** é **(iv)**.
    """
    s = (token or "").strip()
    if not s:
        return ""
    if token_e_abreviacao_encurtamento_iv(s):
        return s

    changed = True
    while changed and s:
        changed = False
        while s and s[0] in LEXICO_PONTUACAO_OMITIR_NAS_EXTREMIDADES:
            s = s[1:].lstrip()
            changed = True
        while s and s[-1] in LEXICO_PONTUACAO_OMITIR_NAS_EXTREMIDADES:
            s = s[:-1].rstrip()
            changed = True
        if token_e_abreviacao_encurtamento_iv(s):
            return s

    while s and s[0] == ".":
        s = s[1:].lstrip()
    while s and s[-1] == ".":
        s = s[:-1].rstrip()

    return s.strip()


def compactar_texto_radical_a6(
    texto: str,
    connectivos: frozenset[str] | None = None,
) -> str:
    """
    **A6** completo: normaliza pontuação por token, omite tokens vazios / só pontuação,
    remove conectivos lexicais, junta com um espaço.
    """
    conn = connectivos if connectivos is not None else LEXICO_CONNECTIVOS_FIXOS
    kept: list[str] = []
    for raw in (texto or "").split():
        t = normalizar_token_pontuacao_a6(raw)
        if not t:
            continue
        if all(ch in LEXICO_PONTUACAO_OMITIR_NAS_EXTREMIDADES or ch == "." for ch in t):
            continue
        if t.casefold() in conn:
            continue
        kept.append(t)
    return " ".join(kept)
