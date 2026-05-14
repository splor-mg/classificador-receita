"""
Validação do ``termo`` / ``termo_nome`` alinhada a ``_dev/spec_lista_abreviacoes.md`` (vii)–(viii).

Aplica-se **apenas** a **abreviação por encurtamento** no sentido (iv): token lexical que é
``<letras>`` imediatas a um ponto final (ex.: ``Contrib.``, ``Princ.``). Siglas (v) sem esse
padrão **não** invalidam o termo.
"""

from __future__ import annotations

import re

# Alinhado a (iv) e a ``_RE_DOTTED_TOKEN`` em ``alias_lexico_infer``: corpo + ponto, sem espaço.
_RE_ENCURTAMENTO_IV_COMO_TOKEN = re.compile(r"^[A-Za-zÀ-ÿ]{1,8}\.$")

# Fronteira lexical comum; **não** incluir ``.`` — o ponto terminal integra o token (iv).
_EDGE_STRIP = ',;:!?()[]{}"\'«»'


def _trim_lexical_token_edges(raw: str) -> str:
    s = raw.strip()
    while s and s[0] in _EDGE_STRIP:
        s = s[1:].lstrip()
    while s and s[-1] in _EDGE_STRIP:
        s = s[:-1].rstrip()
    return s


def termo_nome_rejeitado_encurtamento_iv(termo: str) -> bool:
    """
    True se o ``termo`` **não** pode ser persistido: contém pelo menos um token (separado por
    espaços em branco) classificável como encurtamento (iv) no papel de forma curta.
    """
    s = (termo or "").strip()
    if not s:
        return True
    for raw in s.split():
        tok = _trim_lexical_token_edges(raw)
        if not tok:
            continue
        if _RE_ENCURTAMENTO_IV_COMO_TOKEN.fullmatch(tok):
            return True
    return False
