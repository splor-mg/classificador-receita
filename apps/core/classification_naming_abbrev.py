"""
Protocolo A1–A8 — radical abreviado a partir de ``nome_mae`` e léxico ativo.

Spec: ``_dev/spec_itemClassificacao_criar_nome.md`` (modo Abreviado).
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field

from apps.core.alias_lexico_service import (
    connectivos_fixos_nome_classificacao,
    iter_alias_lexico_ativos_ordenados,
)

SUFIXO_CANONICO = " - "


def norm(s: str) -> str:
    """(N6) trim + casefold; sem colapsar espaços internos."""
    return (s or "").strip().casefold()


def norm_colapso_espacos(s: str) -> str:
    """(N8) (N6) + colapsar espaços internos."""
    return re.sub(r"\s+", " ", norm(s))


def normalize_receita_nome_base_mode(mode: str | None) -> str:
    """Normaliza POST legado ``base_pai`` → ``base_pai_completo``."""
    m = (mode or "").strip()
    if m == "base_pai":
        return "base_pai_completo"
    return m


@dataclass
class AbbrevRadicalResult:
    radical: str
    lexico_termo_duplicado: list[str] = field(default_factory=list)


@dataclass
class _Interval:
    start: int
    end: int
    abrev: str
    term_order: int


def _load_lexicon() -> tuple[list[tuple[str, str]], list[str]]:
    """A1 + A1.3: léxico ativo e alertas de duplicidade."""
    entries: list[tuple[str, str]] = []
    alertas: list[str] = []
    seen_alertas: set[str] = set()

    by_norm: dict[str, list[str]] = defaultdict(list)
    by_colapso: dict[str, list[str]] = defaultdict(list)

    for termo_raw, abrev_raw in iter_alias_lexico_ativos_ordenados():
        termo = (termo_raw or "").strip()
        abrev = (abrev_raw or "").strip()
        if not termo or not abrev:
            continue
        entries.append((termo, abrev))
        by_norm[norm(termo)].append(termo)
        by_colapso[norm_colapso_espacos(termo)].append(termo)

    for grupos in (by_norm, by_colapso):
        for termos in grupos.values():
            if len(termos) >= 2:
                t = termos[0]
                if t not in seen_alertas:
                    seen_alertas.add(t)
                    alertas.append(t)

    return entries, alertas


def _find_substring_intervals_strict(termo: str, nome_mae: str) -> list[tuple[int, int]]:
    """A4.1a: substring contígua, case-insensitive, sem colapsar espaços."""
    termo = (termo or "").strip()
    if not termo or not nome_mae:
        return []
    pattern = re.compile(re.escape(termo), re.IGNORECASE)
    return [(m.start(), m.end()) for m in pattern.finditer(nome_mae)]


def _collapse_with_span_map(text: str) -> tuple[str, list[tuple[int, int]]]:
    """
    (N8) sobre ``text`` já trimado; retorna string colapsada (casefold por caractere)
    e mapa índice colapsado → (start, end) no texto original trimado.
    """
    text = (text or "").strip()
    if not text:
        return "", []

    folded = text.casefold()
    collapsed: list[str] = []
    spans: list[tuple[int, int]] = []
    i = 0
    n = len(text)
    while i < n:
        if text[i].isspace():
            j = i
            while j < n and text[j].isspace():
                j += 1
            if collapsed and collapsed[-1] != " ":
                collapsed.append(" ")
                spans.append((i, j))
            i = j
        else:
            collapsed.append(folded[i])
            spans.append((i, i + 1))
            i += 1

    while collapsed and collapsed[-1] == " ":
        collapsed.pop()
        spans.pop()

    return "".join(collapsed), spans


def _find_substring_intervals_colapso(termo: str, nome_mae: str) -> list[tuple[int, int]]:
    """A4.1b: match em (N8) com mapeamento para índices do ``nome_mae`` original."""
    termo = (termo or "").strip()
    nome_mae = (nome_mae or "").strip()
    if not termo or not nome_mae:
        return []

    term_c = norm_colapso_espacos(termo)
    nome_c, span_map = _collapse_with_span_map(nome_mae)
    if not term_c or not nome_c or len(span_map) != len(nome_c):
        return []

    intervals: list[tuple[int, int]] = []
    start = 0
    while True:
        idx = nome_c.find(term_c, start)
        if idx < 0:
            break
        end_c = idx + len(term_c)
        orig_start = span_map[idx][0]
        orig_end = span_map[end_c - 1][1]
        intervals.append((orig_start, orig_end))
        start = idx + 1

    return intervals


def _greedy_non_overlapping(candidates: list[_Interval]) -> list[_Interval]:
    """A4.2–A4.3: maior comprimento, menor start, ordem A2 (term_order)."""
    candidates.sort(key=lambda iv: (-(iv.end - iv.start), iv.start, iv.term_order))
    selected: list[_Interval] = []
    for iv in candidates:
        overlap = False
        for s in selected:
            if not (iv.end <= s.start or iv.start >= s.end):
                overlap = True
                break
        if not overlap:
            selected.append(iv)
    return sorted(selected, key=lambda iv: iv.start)


def _apply_interval_substitutions(nome_mae: str, selected: list[_Interval]) -> str:
    """A4.4 + A5.1: substitui intervalos; trechos restantes permanecem literais."""
    if not selected:
        return nome_mae
    parts: list[str] = []
    last = 0
    for iv in selected:
        parts.append(nome_mae[last : iv.start])
        parts.append(iv.abrev)
        last = iv.end
    parts.append(nome_mae[last:])
    return "".join(parts)


def _remove_connectivos(texto: str) -> str:
    """A6: remove tokens em NOME_CLASSIFICACAO_CONNECTIVOS_FIXOS."""
    connectivos = connectivos_fixos_nome_classificacao()
    tokens = (texto or "").split()
    kept = [t for t in tokens if t.casefold() not in connectivos]
    return " ".join(kept)


def _a3_exact_match(
    nome_mae: str,
    lexicon: list[tuple[str, str]],
    alertas: list[str],
) -> str | None:
    """A3.1 / A3.3 / A3.2 — match exato; retorna abreviação ou None."""
    nome_n = norm(nome_mae)
    nome_c = norm_colapso_espacos(nome_mae)

    def pick_unique(matches: list[tuple[str, str]]) -> str | None:
        if len(matches) == 1:
            return matches[0][1]
        if len(matches) >= 2:
            alertas.append(matches[0][0])
        return None

    strict_matches = [(t, a) for t, a in lexicon if norm(t) == nome_n]
    abrev = pick_unique(strict_matches)
    if abrev is not None:
        return abrev

    colapso_matches = [(t, a) for t, a in lexicon if norm_colapso_espacos(t) == nome_c]
    return pick_unique(colapso_matches)


def calcular_radical_abreviado(nome_mae: str) -> AbbrevRadicalResult:
    """Calcula radical interno (A1–A8, sem sufixo canônico **(N5)**)."""
    nome_mae = (nome_mae or "").strip()
    lexicon, alertas_lexico = _load_lexicon()
    alertas: list[str] = list(alertas_lexico)

    if not nome_mae:
        return AbbrevRadicalResult(radical="", lexico_termo_duplicado=alertas)

    abrev_a3 = _a3_exact_match(nome_mae, lexicon, alertas)
    if abrev_a3 is not None:
        return AbbrevRadicalResult(radical=abrev_a3.strip(), lexico_termo_duplicado=_uniq(alertas))

    candidates: list[_Interval] = []
    for order, (termo, abrev) in enumerate(lexicon):
        for start, end in _find_substring_intervals_strict(termo, nome_mae):
            candidates.append(_Interval(start, end, abrev, order))

    if not candidates:
        for order, (termo, abrev) in enumerate(lexicon):
            for start, end in _find_substring_intervals_colapso(termo, nome_mae):
                candidates.append(_Interval(start, end, abrev, order))

    if candidates:
        selected = _greedy_non_overlapping(candidates)
        substituido = _apply_interval_substitutions(nome_mae, selected)
        radical = _remove_connectivos(substituido).strip()
        return AbbrevRadicalResult(radical=radical, lexico_termo_duplicado=_uniq(alertas))

    return AbbrevRadicalResult(radical=nome_mae, lexico_termo_duplicado=_uniq(alertas))


def radical_com_sufixo_canonico(radical: str) -> str:
    """A7 / (N5): radical não vazio → radical + ``" - "``."""
    r = (radical or "").strip()
    if not r:
        return ""
    return r + SUFIXO_CANONICO


def _uniq(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out
