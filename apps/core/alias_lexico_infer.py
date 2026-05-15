"""
Inferência conservadora de pares (termo, abreviação) a partir de linhas de item (dict compatível com CSV).

Regras PF (mãe–filho), ordem na passagem primária (``_RULE_FUNCS_PRIMARY``):

- **Regra 1** (``_try_rule_a*``): mãe monossegmento → primeiro segmento do filho abrevia nome integral da mãe.
- **Regra 1.2** (``_try_rule_1_2_pf``): mãe e filho com ≥2 segmentos major; omitida quando nome integral
  mãe=filho coincide após **1.2.9**; caminho A eco literal ou caminho **B.1**/**B.2**, vetando **B** se cauda
  alinhada for abreviação **Regra 4** (**1.2.4.5.5**, ``_rule_12_path_b_blocked_parallel_tail``).
- **Regra 4** (``_try_rule_4_pf_pairs``): alinhamento posicional (filho X+1); incl. cabeça + sigla da cauda (ex. ``Atenção MAC``).

Regras ND sobre o próprio ``receita_nome``:

- **Regra 2 (ND):** exactamente dois segmentos; segundo é sigla (v), incl. ``IOF-Ouro``; omissão 2.4 se sigla já mapeada.
- **Regra 3 (ND):** um segmento major e sufixo ``(SIGLA)`` → par base → sigla.

**Omissão (M) — junção já decomposta:** antes de devolver candidatos únicos ou persistir, omite-se o
par cujo ``termo`` (após **1.2.9.1**) coincide com ``T + ' - ' + A`` de outro par já no mapa ou no
mesmo lote ``good`` (ver ``_filter_good_dict_junction_m``, ``termo_suppressed_by_junction_m``).

Sem dependências Django: pode ser importado pelo script CSV na raiz do projeto (ver ``scripts/``).
"""

from __future__ import annotations

import csv
import re
from collections import defaultdict
from collections.abc import Set as AbstractSet
from datetime import date, datetime

_REGISTRO_FIM_SENTINELS = frozenset(
    {
        "9999-12-31 00:00:00",
        "9999-12-31T00:00:00",
        "9999-12-31 00:00:00.000000",
    }
)

_CONNECTIVES = frozenset(
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

_RE_HEAD_ASCII = re.compile(r"^[A-Z]{2,15}$")
_RE_SHORT_SEG = re.compile(r"^[A-Z]{2,8}$")
_RE_DOTTED_TOKEN = re.compile(r"^[A-Za-zÀ-ÿ]{1,8}\.$")
_RE_HEAD_FIRST_ABBREV_DOT = re.compile(
    r"^([A-Za-zÀ-ÿ]+)\s+([A-Za-zÀ-ÿ]{2,12})\.$"
)
_RE_RULE3_SUFFIX = re.compile(
    r"^(?P<base>.*)\s*\(\s*(?P<sigla>[A-Z]{2,15})\s*\)\s*$"
)

# Corpo de sigla só com maiúsculas/dígitos e separadores internos (spec (v): ICMS, DA-MJM, I.T.D.M, JF_ED).
_RE_SIGLA_BODY_FULL = re.compile(r"^[A-Z0-9]+(?:[.\-_][A-Z0-9]+)*$")


def _is_acronym_hyphen_title_word_tail(segment: str) -> bool:
    """
    Caso ``IOF-Ouro`` da Regra 2: ``<SIGLA>-<NomePróprio>`` com um único hífen,
    cabeça só em maiúsculas (corpo sigla) e cauda com inicial maiúscula e resto em minúsculas.
    """
    s = (segment or "").strip()
    if s.count("-") != 1:
        return False
    head, tail = s.split("-", 1)
    if len(head) < 2 or not tail:
        return False
    if not _RE_SIGLA_BODY_FULL.match(head) or head != head.upper():
        return False
    if not tail[0].isalpha() or not tail[0].isupper():
        return False
    if len(tail) == 1:
        return True
    return all((not ch.isalpha()) or ch.islower() for ch in tail[1:])


def _split_segments(name: str) -> list[str]:
    return [p.strip() for p in re.split(r"\s*-\s*", name.strip()) if p.strip()]


def _split_segments_major(name: str) -> list[str]:
    """
    Segmentos para Regra 5 (PF): delimitador ``' - '`` (um ou mais espaços, traço, um ou mais espaços).

    Evita partir siglas compostas com traço interno (ex.: ``DA-MJM``) como se fossem dois segmentos.
    """
    return [p.strip() for p in re.split(r"\s+-\s+", name.strip()) if p.strip()]


def _norm_receita_nome_rule12_duplicate_guard(name: str) -> str:
    """
    Chave de comparação para **1.2.9** (duplicados mãe/filho): ``strip``, colapsar blocos Unicode
    whitespace a um espaço ASCII, ``casefold``.
    """
    s = (name or "").strip()
    return re.sub(r"\s+", " ", s).casefold()


def _junction_join_norm_m(t: str, a: str) -> str:
    """Chave (M.1) para a junção canónica ``T.strip() + ' - ' + A.strip()``."""
    return _norm_receita_nome_rule12_duplicate_guard(f"{t.strip()} - {a.strip()}")


def termo_suppressed_by_junction_m(termo: str, abbrev_map: dict[str, str]) -> bool:
    """
    Spec **(M)**: ``True`` se ``norm(termo)`` (1.2.9.1) coincide com a junção de algum
    ``(T, A)`` em *abbrev_map* (``norm(T + ' - ' + A)``), com ``T`` e ``A`` não vazios após *strip*.
    """
    if not (termo or "").strip():
        return False
    n_t = _norm_receita_nome_rule12_duplicate_guard(termo)
    for T_raw, A_raw in abbrev_map.items():
        T = (T_raw or "").strip()
        A = (A_raw or "").strip()
        if not T or not A:
            continue
        if _junction_join_norm_m(T, A) == n_t:
            return True
    return False


def _filter_good_dict_junction_m(good: dict[str, str]) -> dict[str, str]:
    """
    Remove entradas de *good* cujo ``termo`` é reduntante por **(M)** face à junção de outro par
    presente no mesmo dicionário (mesma corrida de inferência).
    """
    if len(good) < 2:
        return good
    join_norms: set[str] = set()
    for T, A_raw in good.items():
        T_s = (T or "").strip()
        A = (A_raw or "").strip()
        if not T_s or not A:
            continue
        join_norms.add(_junction_join_norm_m(T_s, A))
    out: dict[str, str] = {}
    for termo, abrev in good.items():
        n_t = _norm_receita_nome_rule12_duplicate_guard(termo)
        if n_t in join_norms:
            continue
        out[termo] = abrev
    return out


def _rule12_skip_duplicate_mother_child_labels(parent_name: str, child_name: str) -> bool:
    """True se nome integral da mãe coincide com o do filho após 1.2.9 → Regra **1.2** omitida."""
    return _norm_receita_nome_rule12_duplicate_guard(
        parent_name
    ) == _norm_receita_nome_rule12_duplicate_guard(child_name)


def _norm_name(raw: str | None) -> str | None:
    if raw is None:
        return None
    s = raw.strip()
    if not s or s.upper() == "NULL":
        return None
    return s


def _norm_parent_item_id(raw: str | None) -> str | None:
    s = (raw or "").strip()
    if not s or s.upper() == "NULL" or s == "-":
        return None
    return s


def _parse_iso_date(value: str | None) -> date | None:
    s = (value or "").strip()
    if not s or s.upper() == "NULL":
        return None
    try:
        return datetime.strptime(s[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def _parse_iso_datetime(value: str | None) -> datetime | None:
    s = (value or "").strip()
    if not s or s.upper() == "NULL":
        return None
    s = s.replace("T", " ", 1)
    if len(s) == 10:
        s += " 00:00:00"
    try:
        return datetime.strptime(s[:19], "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None


def _is_transaction_active_row(row: dict) -> bool:
    fin = (row.get("data_registro_fim") or "").strip()
    return fin in _REGISTRO_FIM_SENTINELS


def _budget_period_compatible_parent_child(parent: dict, child: dict) -> bool:
    pi = _parse_iso_date(parent.get("data_vigencia_inicio"))
    pf = _parse_iso_date(parent.get("data_vigencia_fim"))
    ci = _parse_iso_date(child.get("data_vigencia_inicio"))
    cf = _parse_iso_date(child.get("data_vigencia_fim"))
    if pi and pf and ci and cf:
        return pi <= ci and cf <= pf
    return True


def _pick_latest_parent_row(candidates: list[dict]) -> dict | None:
    def sort_key(r: dict) -> tuple[date, datetime, int]:
        vd = _parse_iso_date(r.get("data_vigencia_inicio")) or date.min
        rd = _parse_iso_datetime(r.get("data_registro_inicio")) or datetime.min
        try:
            ref = int((r.get("item_ref") or "0").strip() or "0")
        except ValueError:
            ref = 0
        return (vd, rd, ref)

    if not candidates:
        return None
    return max(candidates, key=sort_key)


def _resolve_parent_row(child: dict, rows_by_item_id: dict[str, list[dict]]) -> dict | None:
    pid = _norm_parent_item_id(child.get("parent_item_id"))
    if not pid:
        return None
    bucket = rows_by_item_id.get(pid)
    if not bucket:
        return None
    active = [r for r in bucket if _is_transaction_active_row(r)]
    if not active:
        return None
    compatible = [r for r in active if _budget_period_compatible_parent_child(r, child)]
    pool = compatible if compatible else active
    return _pick_latest_parent_row(pool)


def _significant_words_ordered(text: str) -> list[str]:
    words = re.findall(r"[A-Za-zÀ-ÿ]+", text)
    return [w for w in words if w.lower() not in _CONNECTIVES]


def _significant_word_keys_major_segment(segment: str) -> set[str]:
    """
    Palavras significativas de um segmento major (Regra 1.2 caminho B / spec 1.2.8).

    Vírgulas → espaço; tokens por espaço; subdivisão por hífen ASCII; exclusão de conectivos;
    chaves *casefold* para comparação.
    """
    s = re.sub(r",\s*", " ", (segment or "").strip())
    s = re.sub(r"\s+", " ", s).strip()
    if not s:
        return set()
    keys: set[str] = set()
    for token in s.split():
        for part in re.split(r"-+", token):
            if not part or not re.search(r"[A-Za-zÀ-ÿ]", part):
                continue
            for word in re.findall(r"[A-Za-zÀ-ÿ]+", part):
                if word.lower() not in _CONNECTIVES:
                    keys.add(word.casefold())
    return keys


def _is_simple_abbrev_connectives_only(long_seg: str, short_seg: str) -> bool:
    """
    Abreviação simples (spec (iii)): a única diferença é remoção de conectivos —
    mesma sequência de palavras significativas nos dois segmentos.
    """
    wl = _significant_words_ordered(long_seg)
    ws = _significant_words_ordered(short_seg)
    if not wl or wl != ws:
        return False
    return long_seg.strip().casefold() != short_seg.strip().casefold()


def _sig_word_set(text: str) -> set[str]:
    return {w.lower() for w in _significant_words_ordered(text)}


def _initials_acronym(phrase: str) -> str:
    words = re.findall(r"[A-Za-zÀ-ÿ]+", phrase)
    sig = [w for w in words if w.lower() not in _CONNECTIVES]
    return "".join(w[0].upper() for w in sig)


def _tail_child_covers_parent(parent_name: str, child_name: str) -> bool:
    pp = _split_segments(parent_name)
    pc = _split_segments(child_name)
    if len(pp) < 2 or len(pc) < 2:
        return False
    tail_p = " ".join(pp[1:])
    tail_c = " ".join(pc[1:])
    sp = _sig_word_set(tail_p)
    sc = _sig_word_set(tail_c)
    if not sp:
        return True
    return sp <= sc


def _abbr_matches_word(abbr: str, word: str) -> bool:
    if not abbr or not word:
        return False
    wl = word.lower()
    al = abbr.lower()
    if len(abbr) == 1:
        return wl.startswith(al)
    if len(abbr) < 2 or len(word) < 2:
        return False
    if wl.startswith(al):
        return True
    if len(abbr) == 2 and len(word) >= 3:
        return word[0].lower() == al[0] and word[2].lower() == al[1]
    return False


def _words_ordered_from_parent_phrase(segment: str) -> list[str]:
    s = re.sub(r",\s*", " ", segment)
    return _significant_words_ordered(s)


def _token_matches_parent_word(token: str, word: str) -> bool:
    if _RE_DOTTED_TOKEN.match(token):
        return _abbr_matches_word(token[:-1], word)
    return token.casefold() == word.casefold()


def _align_parent_words_to_head_tokens(parent_segment: str, head: str) -> list[tuple[str, str]] | None:
    tokens = head.split()
    if len(tokens) < 2:
        return None
    words = _words_ordered_from_parent_phrase(parent_segment)
    if len(words) < 2:
        return None
    if len(tokens) != len(words):
        return None
    if not any(_RE_DOTTED_TOKEN.match(t) for t in tokens):
        return None
    pairs: list[tuple[str, str]] = []
    for tok, w in zip(tokens, words, strict=True):
        if not _token_matches_parent_word(tok, w):
            return None
        pairs.append((w, tok))
    return pairs


def _try_rule_a(parent_name: str, child_name: str) -> tuple[str, str] | None:
    pp = _split_segments(parent_name)
    pc = _split_segments(child_name)
    if len(pp) != 1 or len(pc) < 2:
        return None
    head = pc[0]
    if not _RE_HEAD_ASCII.match(head):
        return None
    full = pp[0]
    if len(full) <= len(head) + 15:
        return None
    return (full, head)


def _try_rule_a_multi_first(parent_name: str, child_name: str) -> tuple[str, str] | None:
    pp = _split_segments(parent_name)
    pc = _split_segments(child_name)
    if len(pp) < 2 or len(pc) < 2:
        return None
    head = pc[0]
    if not _RE_HEAD_ASCII.match(head):
        return None
    termo = pp[0]
    if len(termo) <= len(head) + 15:
        return None
    if not _tail_child_covers_parent(parent_name, child_name):
        return None
    return (termo, head)


def _try_rule_a_first_word_dot_abbrev(parent_name: str, child_name: str) -> tuple[str, str] | None:
    pp = _split_segments(parent_name)
    pc = _split_segments(child_name)
    if len(pp) != 1 or len(pc) < 2:
        return None
    head = pc[0].strip()
    m = _RE_HEAD_FIRST_ABBREV_DOT.match(head)
    if not m:
        return None
    first_w, abbrev_body = m.group(1), m.group(2)
    words = _significant_words_ordered(pp[0])
    if len(words) < 2:
        return None
    if words[0] != first_w:
        return None
    last_w = words[-1]
    if len(abbrev_body) < 3:
        return None
    if not last_w.lower().startswith(abbrev_body.lower()):
        return None
    return (pp[0], head)


def _try_rule_a_dotted_chain(parent_name: str, child_name: str) -> tuple[str, str] | None:
    pp = _split_segments(parent_name)
    pc = _split_segments(child_name)
    if len(pp) != 1 or len(pc) < 2:
        return None
    head = pc[0].strip()
    if _align_parent_words_to_head_tokens(pp[0], head) is None:
        return None
    return (pp[0], head)


def _derive_atomic_from_dotted_phrase(termo: str, abreviacao: str) -> list[tuple[str, str]] | None:
    ab = (abreviacao or "").strip()
    if not ab:
        return None
    aligned = _align_parent_words_to_head_tokens(termo, ab)
    if aligned is None:
        return None
    if all(_RE_DOTTED_TOKEN.match(tok) for _, tok in aligned):
        return aligned
    return [(w, tok) for w, tok in aligned if _RE_DOTTED_TOKEN.match(tok)]


def _phrase_sig_words(termo: str) -> list[str]:
    phrase = re.sub(r",\s*", " ", (termo or "").strip())
    return _significant_words_ordered(phrase)


def _is_compositional_redundant(termo: str, abrev: str, abbrev_by_termo: dict[str, str]) -> bool:
    words = _phrase_sig_words(termo)
    if len(words) < 2:
        return False
    ab = (abrev or "").strip()
    if not ab:
        return False
    parts: list[str] = []
    for w in words:
        tok = abbrev_by_termo.get(w)
        if tok is None:
            return False
        parts.append(tok)
    return " ".join(parts) == ab


def _merge_abbrev_map_from_pair(termo: str, abrev: str, abbrev_by_termo: dict[str, str]) -> None:
    abbrev_by_termo[termo] = abrev
    atoms = _derive_atomic_from_dotted_phrase(termo, abrev)
    if not atoms:
        return
    for w, tok in atoms:
        abbrev_by_termo.setdefault(w, tok)


def _infer_candidate_sort_key(kv: tuple[str, str]) -> tuple[int, int, str]:
    termo, _ = kv
    return (len(_phrase_sig_words(termo)), len(termo), termo.lower())


def _atomic_derivations(
    phrase_pairs: list[tuple[str, str]],
    known_terms_ci: set[str],
) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    seen = set(known_terms_ci)
    for termo, abrev in phrase_pairs:
        atoms = _derive_atomic_from_dotted_phrase(termo, abrev)
        if not atoms:
            continue
        for w, abbrev_token in atoms:
            wl = w.lower()
            if wl in seen:
                continue
            seen.add(wl)
            out.append((w, abbrev_token))
    return out


def _is_sigla_second_segment_rule2(segment: str) -> bool:
    """
    Segundo segmento da Regra 2 (ND): sigla conforme spec (v), mais o caso ``IOF-Ouro`` da própria Regra 2.
    """
    s = (segment or "").strip()
    if len(s) < 2:
        return False
    if any(ch.isspace() for ch in s):
        return False
    if "(" in s or ")" in s:
        return False
    if not any(ch.isalpha() for ch in s):
        return False
    if _RE_SIGLA_BODY_FULL.match(s) and s == s.upper():
        return True
    return _is_acronym_hyphen_title_word_tail(s)


def _try_rule_nd_two_segment_sigla(name: str) -> tuple[str, str] | None:
    """
    Regra 2 (ND): nome com exactamente dois segmentos **major** (``_split_segments_major``,
    alinhado à spec e à Regra 5: só separa em ``' - '`` com espaços, não parte ``IOF-Ouro``);
    o segundo segmento é sigla; candidato ``(segmento_1, segmento_2)``.
    """
    s = (name or "").strip()
    if not s:
        return None
    parts = _split_segments_major(s)
    if len(parts) != 2:
        return None
    left, right = parts[0].strip(), parts[1].strip()
    if not left or not right:
        return None
    if not _is_sigla_second_segment_rule2(right):
        return None
    return (left, right)


def _try_rule_nd_parenthetical_suffix(name: str) -> tuple[str, str] | None:
    """
    Regra 3 (ND): nome com **um** segmento major (``' - '``), terminado em ``(SIGLA)``;
    a sigla é a abreviação do texto antes dos parêntesis finais.
    """
    s = (name or "").strip()
    if not s:
        return None
    if len(_split_segments_major(s)) != 1:
        return None
    m = _RE_RULE3_SUFFIX.match(s)
    if not m:
        return None
    base = m.group("base").strip()
    sigla = m.group("sigla").strip()
    if not base:
        return None
    return (base, sigla)


_EDGE_STRIP_SEGMENT_TOKEN = ',;:!?()[]{}"\'«»'


def _lexical_tokens_by_space(segment: str) -> list[str]:
    """Tokens lexicais de um segmento major (espaços); remove pontuação de fronteira comum."""
    s = re.sub(r",\s*", " ", (segment or "").strip())
    s = re.sub(r"\s+", " ", s).strip()
    out: list[str] = []
    for raw in s.split():
        tok = raw.strip(_EDGE_STRIP_SEGMENT_TOKEN)
        if tok:
            out.append(tok)
    return out


def _is_head_plus_tail_sigla_rule4(parent_seg: str, child_seg: str) -> bool:
    """
    Regra 4 — cabeça preservada + sigla (v) das palavras significativas restantes da mãe
    (spec: refinamento 4.3, ex. ``Atenção MAC`` ← ``Atenção de Média e Alta Complexidade``).
    """
    parent_words = _significant_words_ordered(parent_seg)
    if len(parent_words) < 3:
        return False
    child_tokens = _lexical_tokens_by_space(child_seg)
    if len(child_tokens) != 2:
        return False
    head_c, sigla_c = child_tokens[0], child_tokens[1]
    if head_c.casefold() != parent_words[0].casefold():
        return False
    if len(sigla_c) < 2 or sigla_c != sigla_c.upper():
        return False
    if not _RE_SIGLA_BODY_FULL.match(sigla_c):
        return False
    tail_phrase = " ".join(parent_words[1:])
    return _initials_acronym(tail_phrase) == sigla_c


def _is_segment_abbrev_rule4(parent_seg: str, child_seg: str) -> bool:
    """
    O segmento do filho é abreviação do segmento do mãe (Regra 4 / PF), excluindo
    igualdade literal e abreviação simples (tratadas antes).
    """
    p = parent_seg.strip()
    c = child_seg.strip()
    if p == "Principal" and c == "Princ.":
        return True
    if _RE_SHORT_SEG.match(c) and _initials_acronym(p) == c:
        return True
    if _align_parent_words_to_head_tokens(p, c) is not None:
        return True
    if _is_head_plus_tail_sigla_rule4(p, c):
        return True
    return False


def _rule_12_path_b_blocked_parallel_tail(pp: list[str], pc: list[str]) -> bool:
    """
    Spec 1.2.4.5.5 — exclusão do **caminho B**: para algum índice 1-based ``i`` em
    ``2 … min(N, N_f)``, o segmento ``S_{f,i}`` abrevia ``S_{m,i}`` no mesmo sentido da **Regra 4**,
    ignorando igualdade literal e abreviação só por conectivos (alinhado ao laço de ``_try_rule_4_pf_pairs``).
    """
    upto = min(len(pp), len(pc))
    for idx in range(1, upto):
        p_seg = pp[idx].strip()
        c_seg = pc[idx].strip()
        if not p_seg or not c_seg:
            continue
        if p_seg.casefold() == c_seg.casefold():
            continue
        if _is_simple_abbrev_connectives_only(p_seg, c_seg):
            continue
        if _is_segment_abbrev_rule4(p_seg, c_seg):
            return True
    return False


def _try_rule_1_2_pf_tail_echo(parent_name: str, child_name: str) -> tuple[str, str] | None:
    """
    Regra 1.2 caminho A (PF): último segmento major da mãe = primeiro do filho (*casefold*).
    """
    pp = _split_segments_major(parent_name)
    pc = _split_segments_major(child_name)
    if len(pp) < 2 or len(pc) < 2:
        return None
    last_parent = pp[-1].strip()
    first_child = pc[0].strip()
    if not last_parent or not first_child:
        return None
    if last_parent.casefold() != first_child.casefold():
        return None
    termo = parent_name.strip()
    if not termo:
        return None
    return (termo, first_child)


def _try_rule_1_2_pf_segment_coverage(parent_name: str, child_name: str) -> tuple[str, str] | None:
    """
    Regra 1.2 caminho B (PF): **B.1** — intersecção lexical (1.2.8) com **cada** segmento major da mãe;
    se falhar, **B.2** — no máximo **um** segmento sem intersecção, apenas no **primeiro** ou **último**
    da mãe, e **apenas** se o filho **não** tiver **mais** segmentos major do que a mãe
    (``len(pc) <= len(pp)``; spec 1.2.4.5.3); **1.2.4.5.5** vetado por caudas alinhadas tipo Regra 4.
    """
    pp = _split_segments_major(parent_name)
    pc = _split_segments_major(child_name)
    if len(pp) < 2 or len(pc) < 2:
        return None
    first_child = pc[0].strip()
    if not first_child:
        return None
    if _rule_12_path_b_blocked_parallel_tail(pp, pc):
        return None
    w_child = _significant_word_keys_major_segment(first_child)
    if not w_child:
        return None
    misses: list[int] = []
    for i, parent_seg in enumerate(pp):
        w_parent = _significant_word_keys_major_segment(parent_seg)
        if not w_child.intersection(w_parent):
            misses.append(i)
    if misses:
        if len(pc) > len(pp):
            return None
        if len(misses) != 1:
            return None
        (idx,) = misses
        n = len(pp)
        if idx != 0 and idx != n - 1:
            return None
    termo = parent_name.strip()
    if not termo:
        return None
    return (termo, first_child)


def _try_rule_1_2_pf(parent_name: str, child_name: str) -> tuple[str, str] | None:
    """Regra 1.2 (PF): **1.2.9**; caminho A; se falhar, caminho B (spec 1.2.7)."""
    if _rule12_skip_duplicate_mother_child_labels(parent_name, child_name):
        return None
    return _try_rule_1_2_pf_tail_echo(parent_name, child_name) or _try_rule_1_2_pf_segment_coverage(
        parent_name, child_name
    )


def _try_rule_4_pf_pairs(parent_name: str, child_name: str) -> list[tuple[str, str]]:
    """
    Regra 4 (PF): mãe com X segmentos (``_split_segments_major``, X ≥ 2), filho com X+1;
    para cada posição i < X, se o segmento do filho abrevia o do pai, não é igual nem
    abreviação simples, candidato ``(segmento_pai_i, segmento_filho_i)``.
    """
    pp = _split_segments_major(parent_name)
    pc = _split_segments_major(child_name)
    if len(pp) < 2 or len(pc) != len(pp) + 1:
        return []
    out: list[tuple[str, str]] = []
    for i in range(len(pp)):
        p_seg = pp[i].strip()
        c_seg = pc[i].strip()
        if not p_seg or not c_seg:
            return []
        if p_seg.casefold() == c_seg.casefold():
            continue
        if _is_simple_abbrev_connectives_only(p_seg, c_seg):
            continue
        if not _is_segment_abbrev_rule4(p_seg, c_seg):
            continue
        out.append((p_seg, c_seg))
    return out


def _join_two_parent_segments(seg_a: str, seg_b: str) -> str:
    """Junção canónica A e B (Regra 5 / PF), alinhada a ``_split_segments`` com `` - ``."""
    return f"{seg_a.strip()} - {seg_b.strip()}"


def _try_rule_pf(
    parent_name: str,
    child_name: str,
    abbrev_map: dict[str, str],
) -> tuple[str, str] | None:
    """
    Regra 5 (PF): mesmo número de segmentos (≥ 2); um segmento Y do filho iguala a junção
    (com ou sem traço) das abreviações já conhecidas de dois segmentos consecutivos A, B do pai;
    regista ``(A - B, Y)`` com Y tal como no nome do filho.

    Usa ``_split_segments_major`` para contar segmentos como na spec (``' - '``), não ``_split_segments``.
    """
    pp = _split_segments_major(parent_name)
    pc = _split_segments_major(child_name)
    if len(pp) != len(pc) or len(pp) < 2:
        return None
    for y in range(0, len(pp) - 1):
        if any(pp[j].strip() != pc[j].strip() for j in range(y)):
            continue
        seg_a = pp[y].strip()
        seg_b = pp[y + 1].strip()
        ab_a = abbrev_map.get(seg_a)
        ab_b = abbrev_map.get(seg_b)
        if not ab_a or not ab_b:
            continue
        pc_y = pc[y].strip()
        if pc_y.casefold() == seg_a.casefold() or pc_y.casefold() == seg_b.casefold():
            continue
        for glue in (f"{ab_a}-{ab_b}", f"{ab_a}{ab_b}"):
            if glue.casefold() == pc_y.casefold():
                return (_join_two_parent_segments(seg_a, seg_b), pc_y)
    return None


_RULE_FUNCS_PRIMARY = (
    _try_rule_a,
    _try_rule_a_multi_first,
    _try_rule_a_first_word_dot_abbrev,
    _try_rule_a_dotted_chain,
    _try_rule_1_2_pf,
)


def _unambiguous_abbrev_map(cand: dict[str, set[str]]) -> dict[str, str]:
    return {t: next(iter(ab)) for t, ab in cand.items() if len(ab) == 1}


def _infer_pairs(
    rows: list[dict],
    *,
    abbrev_siglas_mapeadas_ci: AbstractSet[str] | None = None,
) -> tuple[dict[str, str], list[tuple[str, set[str]]], frozenset[str]]:
    rows_by_item_id: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        iid = (r.get("item_id") or "").strip()
        if iid:
            rows_by_item_id[iid].append(r)

    cand: dict[str, set[str]] = defaultdict(set)
    matched_item_ids: set[str] = set()
    termos_viii_exempt: set[str] = set()

    for r in rows:
        if not _is_transaction_active_row(r):
            continue
        nm = _norm_name(r.get("receita_nome"))
        if not nm:
            continue
        got_r2 = _try_rule_nd_two_segment_sigla(nm)
        if got_r2:
            sigla = got_r2[1].strip()
            if (
                abbrev_siglas_mapeadas_ci is not None
                and sigla.lower() in abbrev_siglas_mapeadas_ci
            ):
                continue
            cand[got_r2[0]].add(sigla)
            continue
        got_r3 = _try_rule_nd_parenthetical_suffix(nm)
        if got_r3:
            cand[got_r3[0]].add(got_r3[1])

    for ch in rows:
        if not _is_transaction_active_row(ch):
            continue
        parent_row = _resolve_parent_row(ch, rows_by_item_id)
        if parent_row is None:
            continue
        pname = _norm_name(parent_row.get("receita_nome"))
        cname = _norm_name(ch.get("receita_nome"))
        if not pname or not cname:
            continue
        cid = (ch.get("item_id") or "").strip()
        matched_pf = False
        for rule_fn in _RULE_FUNCS_PRIMARY:
            got = rule_fn(pname, cname)
            if got:
                termo, abrev = got
                cand[termo].add(abrev)
                if rule_fn is _try_rule_1_2_pf:
                    termos_viii_exempt.add(termo)
                if cid:
                    matched_item_ids.add(cid)
                matched_pf = True
                break
        if not matched_pf:
            r4_pairs = _try_rule_4_pf_pairs(pname, cname)
            if r4_pairs:
                for termo, abrev in r4_pairs:
                    cand[termo].add(abrev)
                if cid:
                    matched_item_ids.add(cid)

    abbrev_map = _unambiguous_abbrev_map(cand)
    for ch in rows:
        if not _is_transaction_active_row(ch):
            continue
        parent_row = _resolve_parent_row(ch, rows_by_item_id)
        if parent_row is None:
            continue
        pname = _norm_name(parent_row.get("receita_nome"))
        cname = _norm_name(ch.get("receita_nome"))
        if not pname or not cname:
            continue
        cid = (ch.get("item_id") or "").strip()
        if cid and cid in matched_item_ids:
            continue
        got_pf = _try_rule_pf(pname, cname, abbrev_map)
        if got_pf:
            termo, abrev = got_pf
            cand[termo].add(abrev)

    good: dict[str, str] = {}
    conflicts: list[tuple[str, set[str]]] = []
    for termo, abrevs in sorted(cand.items(), key=lambda x: x[0].lower()):
        if len(abrevs) == 1:
            good[termo] = next(iter(abrevs))
        else:
            conflicts.append((termo, abrevs))
    good = _filter_good_dict_junction_m(good)
    return good, conflicts, frozenset(termos_viii_exempt)


_SEED_WRITER_KW = {"quoting": csv.QUOTE_MINIMAL}


def _sort_rows_alias_lexico_registry(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    def sort_key(r: dict[str, str]) -> tuple[str, str, str]:
        termo_lower = (r.get("termo_nome") or "").lower()
        dr_ini = (r.get("data_registro_inicio") or "").strip()
        termo_raw = r.get("termo_nome") or ""
        return (termo_lower, dr_ini, termo_raw)

    return sorted(rows, key=sort_key)


def sort_pairs_like_registry_order(
    pairs: list[tuple[str, str]],
    data_registro_inicio: str,
    data_registro_fim: str,
) -> list[tuple[str, str]]:
    """Ordena pares como ``order_by_sql`` do recurso ``lista_abreviacoes`` (LOWER(termo), data_registro_inicio)."""
    rows: list[dict[str, str]] = [
        {
            "termo_nome": t,
            "alias_lexico_ref": "0",
            "abreviacao": a,
            "data_registro_inicio": data_registro_inicio,
            "data_registro_fim": data_registro_fim,
        }
        for t, a in pairs
    ]
    sorted_rows = _sort_rows_alias_lexico_registry(rows)
    return [(r["termo_nome"], r["abreviacao"]) for r in sorted_rows]


def _max_alias_lexico_ref(rows: list[dict[str, str]]) -> int:
    m = 0
    for r in rows:
        try:
            m = max(m, int((r.get("alias_lexico_ref") or "").strip()))
        except ValueError:
            continue
    return m


def _assign_refs_to_new_rows(new_rows: list[dict[str, str]], max_existing_ref: int) -> int:
    if not new_rows:
        return max_existing_ref
    ordered = _sort_rows_alias_lexico_registry(new_rows)
    next_ref = max_existing_ref
    for row in ordered:
        next_ref += 1
        row["alias_lexico_ref"] = str(next_ref)
    return next_ref


def _interactive_pick_conflict_abbrev(termo: str, abbrev_options: list[str]) -> str | None:
    print()
    print(f"Termo em conflito: {termo!r}")
    for i, ab in enumerate(abbrev_options, start=1):
        print(f"  {i}) {ab}")
    print("  n) Nenhuma — pular este termo")
    while True:
        raw = input("Escolha (número ou n): ").strip().lower()
        if raw in ("n", "no", "nao", "não"):
            return None
        try:
            k = int(raw)
            if 1 <= k <= len(abbrev_options):
                return abbrev_options[k - 1]
        except ValueError:
            pass
        print(f"  Inválido. Digite de 1 a {len(abbrev_options)} ou n.")
