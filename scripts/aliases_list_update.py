#!/usr/bin/env python3
"""
Acrescenta registros em ``docs/assets/seed_lista_abreviacoes.csv`` por inferência **conservadora**
a partir de ``docs/assets/seed_item_classificacao.csv`` (arestas **pai → filho direto**).

**Comportamento obrigatório:** não remove linhas por ``termo_nome`` já existentes; apenas **adiciona** termos
novos. Conteúdo de ``abreviacao`` / datas de linhas já presentes não é alterado por este script.

Ao gravar: **ordena** todo o corpo conforme ``order_by_sql`` de ``lista_abreviacoes`` em
``apps/core/bitemporal_registry.py``: ``LOWER(termo) ASC``, ``data_registro_inicio ASC``; desempate estável
pelo próprio ``termo_nome``. Linhas já presentes **mantêm** o ``alias_lexico_ref`` do arquivo; só as **novas**
recebem ref **sequencial** a partir de ``max(alias_lexico_ref) + 1`` (ordem entre novas = mesma chave de
ordenação), sem reescrever refs antigos.

**Curadoria manual:** pares em ``_MANUAL_SEED_TERM_ABBREV`` são acrescentados se o ``termo_nome`` ainda não
existir no seed nem tiver sido inferido nesta execução (não sobrescreve linhas existentes).

Para criar o CSV inicial vazio (só cabeçalho), crie o arquivo manualmente ou com uma primeira linha;
na primeira execução todas as inferências válidas serão acrescentadas.

Para cada linha **ativa em registro** (``data_registro_fim`` sentinela) com ``parent_item_id`` definido,
resolve-se o pai na própria tabela de itens: entre linhas com ``item_id`` igual ao pai, ficam só as **ativas
em registro**; exige-se **vigência compatível** com o filho (intervalo do filho contido no do pai,
``data_vigencia_*``), espelhando ``resolve_active_compatible_fk`` / ``temporal_fk_resolution.py``. Se nenhuma
linha encaixa na vigência, usa-se fallback: mesma ``item_id``, ativa em registro, escolhendo a mais recente
por ``data_vigencia_inicio``, ``data_registro_inicio``, ``item_ref``. Depois aplicam-se as regras abaixo
entre ``receita_nome`` do pai resolvido e do filho.

Regras (por ordem de tentativa):

**Regra A — pai com um segmento; filho ``SIGLA - …`` (somente A–Z na cabeça)**  
  Igual à versão anterior (ex.: IPVA, ICMS, ITCD).

**Regra A′ — primeiro segmento do pai (nome longo) → sigla ASCII; cauda lexical consistente**  
  Pai com **≥2** segmentos; filho com **≥2**; primeira parte do filho ``[A-Z]{2,15}``;
  ``termo =`` primeiro segmento do pai; ``len(termo) > len(sigla) + 15``;
  palavras significativas na cauda do pai (após o 1º segmento) devem estar contidas nas palavras
  da cauda do filho (conectivos ignorados). Ex.: IR / Imposto sobre a Renda.

**Regra A″ — ``PrimeiraPalavra Abbrev.`` no filho vs pai de uma frase**  
  Pai com **um** segmento e **≥2** palavras significativas; cabeça do filho ``Word Abbrev.``
  (``Abbrev`` sem ponto é prefixo da **última** palavra significativa do pai, comprimento ≥3).
  Ex.: Dedução das Receitas → Dedução Rec.

**Regra A‴ — cabeça alinhada ao pai (≥2 tokens)**  
  Pai com um segmento; cabeça do filho com **≥2** tokens separados por espaço; ao menos um token no formato
  ``Xxx.`` / ``X.``; demais tokens podem repetir a palavra do pai por extenso (ex.: ``Civil``, ``Ativo``).
  Mesma quantidade de palavras significativas no pai; cada token pontilhado validado como nas outras regras.
  Ex.: ``Tx. Prest. Serv. G.``; ``Contrib. Serv. Civil Ativo``.

**Regra B — mesmo prefixo; 2º segmento abreviado**  
  Igual à versão anterior (DA, MJM, Princ.).

**Derivação atômica (pós-processamento)**  
  Para cada linha (existente ou nova) cuja ``abreviacao`` seja uma cabeça Regra A‴ (só pontilhados ou mista),
  acrescenta ``palavra → token.`` **apenas** para tokens pontilhados; literais iguais ao pai não geram linha.
  Só quando ``palavra`` ainda não existe no seed. Frases de uma só palavra significativa não geram derivação.

**Redundância composicional**  
  Não registra um par frase → cabeça abreviada se houver **≥2** palavras significativas no termo, o mesmo número
  de tokens na abreviação (separados por espaço) e, para cada palavra na ordem, já existir no mapa vigente
  (seed + inferências/manuais aceitas antes nesta execução, atualizado com átomos da Regra A‴ ao aceitar um par)
  o mapeamento **exato** ``palavra → token`` que reproduz a abreviação ao juntar os tokens com espaço.

Conflitos (na inferência): mesmo ``termo_nome`` com mais de uma ``abreviacao`` candidata → esse termo não
entra nas novidades. Use ``--print-conflicts`` para listar. Use ``--print-conflicts-resolve`` após gravar o
restante: para cada conflito cujo ``termo_nome`` ainda não existir no CSV, pergunta qual abreviação registrar
(``n`` pula).

Uso:
  python scripts/aliases_list_update.py
  poetry run task atualizar-abreviacoes
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ITEM_CSV = ROOT / "docs/assets/seed_item_classificacao.csv"
OUT_CSV = ROOT / "docs/assets/seed_lista_abreviacoes.csv"

# Pares (termo_nome, abreviacao) curados; omitidos se o termo já está no CSV ou foi inferido no mesmo run.
_MANUAL_SEED_TERM_ABBREV: tuple[tuple[str, str], ...] = (
    ("Contribuição", "Contrib."),
    ("Contribuições", "Contrib."),
    ("Fundo de Erradicação da Miséria", "FEM"),
    (
        "Fundo de Manutenção e Desenvolvimento da Educação Básica e de Valorização dos Profissionais da Educação",
        "FUNDEB",
    ),
    (
        "Fundo Estadual Combate Pobreza - Fundo de Erradicação da Miséria",
        "FEM",
    ),
    ("Dívida Ativa - Multas e Juros de Mora", "DA-MJM"),
    (
        "Transferências de Recursos de Complementação da União ao FUNDEB",
        "Transf. Complem. União FUNDEB",
    ),
    ("Transferências", "Transf."),
    ("Financeiras", "Financ."),
    ("Imposto sobre a Propriedade Territorial Rural", "ITR"),
    ("Imposto sobre a Renda das Pessoas Físicas", "IRPF"),
    ("Imposto de Renda Retido na Fonte", "IRRF"),
    ("Contribuição para Financiamento da Seguridade Social", "COFINS"),
    ("Programa de Integração Social", "PIS"),
    ("Regime Geral de Previdência Social", "RGPS"),
)


def _merge_manual_seed_entries(
    additions: list[tuple[str, str]],
    existing_termos: set[str],
    abbrev_by_termo: dict[str, str],
) -> tuple[int, int]:
    """
    Acrescenta entradas manuais não colidentes e não redundantes composicionalmente.

    Retorna (quantas acrescentadas, quantas omitidas só por redundância composicional).
    """
    claimed = {t for t, _ in additions}
    n = 0
    n_skip_comp = 0
    for termo, abrev in _MANUAL_SEED_TERM_ABBREV:
        if termo in existing_termos or termo in claimed:
            continue
        if _is_compositional_redundant(termo, abrev, abbrev_by_termo):
            n_skip_comp += 1
            continue
        additions.append((termo, abrev))
        claimed.add(termo)
        _merge_abbrev_map_from_pair(termo, abrev, abbrev_by_termo)
        n += 1
    return n, n_skip_comp


# Valores aceitos para registro ainda válido (alinhar a imports/carregamento do projeto).
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
        "um",
        "uma",
        "uns",
        "umas",
    }
)

_RE_HEAD_ASCII = re.compile(r"^[A-Z]{2,15}$")
_RE_SHORT_SEG = re.compile(r"^[A-Z]{2,8}$")
# Permite token de 1 letra + ponto (ex.: ``G.`` para ``Geral`` em ``Tx. Prest. Serv. G.``).
_RE_DOTTED_TOKEN = re.compile(r"^[A-Za-zÀ-ÿ]{1,8}\.$")
_RE_HEAD_FIRST_ABBREV_DOT = re.compile(
    r"^([A-Za-zÀ-ÿ]+)\s+([A-Za-zÀ-ÿ]{2,12})\.$"
)


def _split_segments(name: str) -> list[str]:
    return [p.strip() for p in re.split(r"\s*-\s*", name.strip()) if p.strip()]


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


def _vigencia_compatible_parent_child(parent: dict, child: dict) -> bool:
    """Filho contido no pai: pai_ini <= filho_ini e filho_fim <= pai_fim (como no ORM)."""
    pi = _parse_iso_date(parent.get("data_vigencia_inicio"))
    pf = _parse_iso_date(parent.get("data_vigencia_fim"))
    ci = _parse_iso_date(child.get("data_vigencia_inicio"))
    cf = _parse_iso_date(child.get("data_vigencia_fim"))
    if pi and pf and ci and cf:
        return pi <= ci and cf <= pf
    return True


def _pick_latest_parent_row(candidates: list[dict]) -> dict | None:
    """Desempate igual a ``order_by('-data_vigencia_inicio', '-data_registro_inicio', '-pk')``."""

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
    compatible = [r for r in active if _vigencia_compatible_parent_child(r, child)]
    pool = compatible if compatible else active
    return _pick_latest_parent_row(pool)


def _significant_words_ordered(text: str) -> list[str]:
    words = re.findall(r"[A-Za-zÀ-ÿ]+", text)
    return [w for w in words if w.lower() not in _CONNECTIVES]


def _sig_word_set(text: str) -> set[str]:
    return {w.lower() for w in _significant_words_ordered(text)}


def _initials_acronym(phrase: str) -> str:
    words = re.findall(r"[A-Za-zÀ-ÿ]+", phrase)
    sig = [w for w in words if w.lower() not in _CONNECTIVES]
    return "".join(w[0].upper() for w in sig)


def _tail_child_covers_parent(parent_name: str, child_name: str) -> bool:
    """Palavras significativas da cauda do pai estão na cauda do filho (após 1º segmento)."""
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
    """Prefixo da palavra, inicial única (``G.`` → ``Geral``), ou par nas posições 0 e 2 (ex.: Taxas → Tx)."""
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
    """Token da cabeça do filho: abreviação pontilhada ou palavra literal igual à do pai."""
    if _RE_DOTTED_TOKEN.match(token):
        return _abbr_matches_word(token[:-1], word)
    return token.casefold() == word.casefold()


def _align_parent_words_to_head_tokens(parent_segment: str, head: str) -> list[tuple[str, str]] | None:
    """
    Alinha palavras significativas do pai aos tokens da cabeça do filho.
    Exige ≥2 tokens, ≥2 palavras, mesmo comprimento e ao menos um token ``…``.
    Retorna lista (palavra_pai, token_cabeça) ou None.
    """
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
    """Primeiro segmento longo → sigla ASCII; cauda do filho contém vocabulário da cauda do pai."""
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
    """Ex.: Dedução das Receitas → cabeça ``Dedução Rec.``"""
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
    """Só tokens ``Xxx.`` ou mistura ``Xxx.`` + palavras literais (ex.: ``Contrib. Serv. Civil Ativo``)."""
    pp = _split_segments(parent_name)
    pc = _split_segments(child_name)
    if len(pp) != 1 or len(pc) < 2:
        return None
    head = pc[0].strip()
    if _align_parent_words_to_head_tokens(pp[0], head) is None:
        return None
    return (pp[0], head)


def _derive_atomic_from_dotted_phrase(termo: str, abreviacao: str) -> list[tuple[str, str]] | None:
    """
    Pares atômicos a partir da abreviação alinhada ao pai (Regra A‴).
    Se a cabeça for só tokens pontilhados, devolve todos; se for mista, só os tokens com ``.``.
    """
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
    """
    Verdadeiro se o termo tem ≥2 palavras significativas e a abreviação coincide exatamente com a junção,
    na mesma ordem, dos tokens já registrados para cada palavra em ``abbrev_by_termo``.
    """
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
    """Atualiza o mapa para checagens composicionais posteriores (frase inteira + átomos A‴)."""
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
    known_terms: set[str],
) -> list[tuple[str, str]]:
    """
    Para cada (termo completo, abreviacao), propõe pares atômicos. Só inclui termos ainda ausentes em
    ``known_terms``; atualiza ``known_terms`` a cada inclusão para evitar duplicata na mesma execução.

    **Conflito com linhas já no seed:** a presença do ``termo_nome`` atômico (ex.: ``Taxa``) bloqueia nova
    linha **sem olhar** ``data_registro_fim`` nem se o registro seria “ativo” no modelo — qualquer linha no
    CSV com esse termo conta. **Não altera** ``abreviacao`` de linhas existentes; apenas omite o par novo.
    """
    out: list[tuple[str, str]] = []
    for termo, abrev in phrase_pairs:
        atoms = _derive_atomic_from_dotted_phrase(termo, abrev)
        if not atoms:
            continue
        for w, abbrev_token in atoms:
            if w in known_terms:
                continue
            known_terms.add(w)
            out.append((w, abbrev_token))
    return out


def _try_rule_b(parent_name: str, child_name: str) -> tuple[str, str] | None:
    pp = _split_segments(parent_name)
    pc = _split_segments(child_name)
    if len(pp) != 2 or len(pc) < 3:
        return None
    if pp[0] != pc[0]:
        return None
    long_seg, short_seg = pp[1], pc[1]
    if long_seg == "Principal" and short_seg == "Princ.":
        return (long_seg, short_seg)
    if not _RE_SHORT_SEG.match(short_seg):
        return None
    if _initials_acronym(long_seg) != short_seg:
        return None
    return (long_seg, short_seg)


_RULE_FUNCS = (
    _try_rule_a,
    _try_rule_a_multi_first,
    _try_rule_a_first_word_dot_abbrev,
    _try_rule_a_dotted_chain,
    _try_rule_b,
)


def _infer_pairs(rows: list[dict]) -> tuple[dict[str, str], list[tuple[str, set[str]]]]:
    rows_by_item_id: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        iid = (r.get("item_id") or "").strip()
        if iid:
            rows_by_item_id[iid].append(r)

    cand: dict[str, set[str]] = defaultdict(set)
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
        for rule_fn in _RULE_FUNCS:
            got = rule_fn(pname, cname)
            if got:
                termo, abrev = got
                cand[termo].add(abrev)
                break

    good: dict[str, str] = {}
    conflicts: list[tuple[str, set[str]]] = []
    for termo, abrevs in sorted(cand.items(), key=lambda x: x[0].lower()):
        if len(abrevs) == 1:
            good[termo] = next(iter(abrevs))
        else:
            conflicts.append((termo, abrevs))
    return good, conflicts


_SEED_FIELDNAMES = (
    "termo_nome",
    "alias_lexico_ref",
    "abreviacao",
    "data_registro_inicio",
    "data_registro_fim",
)

# Vírgula como separador (compatível com previews CSV que assumem RFC 4180); QUOTE_MINIMAL para termos com vírgula.
_SEED_WRITER_KW = {"quoting": csv.QUOTE_MINIMAL}


def _sort_rows_lista_abreviacoes_registry(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """
    Espelha ``RESOURCES['lista_abreviacoes']['order_by_sql']``: LOWER(termo), data_registro_inicio ASC.
    O campo no CSV é ``termo_nome`` (export_as do model ``termo``). ``alias_lexico_ref`` não entra na chave.
    """

    def sort_key(r: dict[str, str]) -> tuple[str, str, str]:
        termo_lower = (r.get("termo_nome") or "").lower()
        dr_ini = (r.get("data_registro_inicio") or "").strip()
        termo_raw = r.get("termo_nome") or ""
        return (termo_lower, dr_ini, termo_raw)

    return sorted(rows, key=sort_key)


def _max_alias_lexico_ref(rows: list[dict[str, str]]) -> int:
    """Maior ``alias_lexico_ref`` numérico nas linhas (0 se vazio ou inválido)."""
    m = 0
    for r in rows:
        try:
            m = max(m, int((r.get("alias_lexico_ref") or "").strip()))
        except ValueError:
            continue
    return m


def _assign_refs_to_new_rows(new_rows: list[dict[str, str]], max_existing_ref: int) -> int:
    """
    Atribui ``alias_lexico_ref`` às linhas novas (mutação in-place), na ordem de ordenação do registry.
    Retorna o novo máximo de ref após a atribuição (igual a ``max_existing_ref`` se ``new_rows`` vazio).
    """
    if not new_rows:
        return max_existing_ref
    ordered = _sort_rows_lista_abreviacoes_registry(new_rows)
    next_ref = max_existing_ref
    for row in ordered:
        next_ref += 1
        row["alias_lexico_ref"] = str(next_ref)
    return next_ref


def _write_sorted_seed(path: Path, rows: list[dict[str, str]]) -> None:
    sorted_rows = _sort_rows_lista_abreviacoes_registry(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(_SEED_FIELDNAMES), **_SEED_WRITER_KW)
        w.writeheader()
        for row in sorted_rows:
            w.writerow({k: row[k] for k in _SEED_FIELDNAMES})


def _interactive_pick_conflict_abbrev(termo: str, abbrev_options: list[str]) -> str | None:
    """
    Exibe opções numeradas; retorna a abreviação escolhida ou None se o usuário pular (``n``).
    """
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


def _load_existing_seed(path: Path) -> tuple[list[dict[str, str]], set[str]]:
    """
    Lê o CSV existente. Retorna (linhas como dicts na ordem do arquivo), conjunto de ``termo_nome``.

    ``termos`` inclui **todas** as linhas válidas do arquivo, **sem** filtrar por sentinela em
    ``data_registro_fim`` (o script não distingue ativo/inativo no CSV). Se o mesmo ``termo_nome``
    aparecer mais de uma vez, só a **primeira** ocorrência entra em ``rows_out``; o termo permanece em
    ``termos`` e bloqueia inferência/derivação como duplicata.
    """
    if not path.is_file():
        return [], set()
    rows_out: list[dict[str, str]] = []
    termos: set[str] = set()
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            return [], set()
        # normaliza nomes de coluna esperadas
        for raw in reader:
            termo = (raw.get("termo_nome") or raw.get("termo") or "").strip()
            if not termo:
                continue
            ref_s = (raw.get("alias_lexico_ref") or "").strip()
            try:
                int(ref_s)
            except ValueError:
                continue
            if termo in termos:
                continue
            termos.add(termo)
            rows_out.append(
                {
                    "termo_nome": termo,
                    "alias_lexico_ref": ref_s,
                    "abreviacao": (raw.get("abreviacao") or "").strip(),
                    "data_registro_inicio": (raw.get("data_registro_inicio") or "").strip(),
                    "data_registro_fim": (raw.get("data_registro_fim") or "").strip(),
                }
            )
    return rows_out, termos


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Acrescenta ao seed_lista_abreviacoes.csv inferências a partir do item_classificacao "
            "(não altera linhas já existentes)."
        )
    )
    parser.add_argument("--registro-inicio", default="2018-01-01 00:00:00")
    parser.add_argument("--registro-fim", default="9999-12-31 00:00:00")
    parser.add_argument("--output", type=Path, default=OUT_CSV)
    parser.add_argument(
        "--print-conflicts",
        action="store_true",
        help="Lista termos com mais de uma abreviação candidata (descartados).",
    )
    parser.add_argument(
        "--print-conflicts-resolve",
        action="store_true",
        help=(
            "Após gravar o CSV, pergunta termo a termo (só os sem linha no seed) qual abreviação registrar; "
            "n pula. Exige terminal interativo."
        ),
    )
    args = parser.parse_args()

    with ITEM_CSV.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    good, conflicts = _infer_pairs(rows)

    out_path = args.output
    out_path.parent.mkdir(parents=True, exist_ok=True)
    existing_rows, existing_termos = _load_existing_seed(out_path)

    abbrev_by_termo: dict[str, str] = {r["termo_nome"]: r["abreviacao"] for r in existing_rows}

    inferred_candidates = [
        (t, a)
        for t, a in sorted(good.items(), key=lambda kv: kv[0].lower())
        if t not in existing_termos
    ]
    inferred_candidates.sort(key=_infer_candidate_sort_key)

    additions: list[tuple[str, str]] = []
    n_skip_comp_inf = 0
    for termo, abrev in inferred_candidates:
        if _is_compositional_redundant(termo, abrev, abbrev_by_termo):
            n_skip_comp_inf += 1
            continue
        additions.append((termo, abrev))
        _merge_abbrev_map_from_pair(termo, abrev, abbrev_by_termo)

    n_inferred_only = len(additions)
    n_manual, n_skip_comp_manual = _merge_manual_seed_entries(
        additions, existing_termos, abbrev_by_termo
    )

    known_after_inference = set(existing_termos)
    known_after_inference.update(t for t, _ in additions)

    phrase_pairs_for_atoms: list[tuple[str, str]] = [
        (r["termo_nome"], r["abreviacao"]) for r in existing_rows
    ]
    phrase_pairs_for_atoms.extend(additions)

    derived = _atomic_derivations(phrase_pairs_for_atoms, known_after_inference.copy())

    new_row_dicts: list[dict[str, str]] = []
    for termo, abrev in additions:
        new_row_dicts.append(
            {
                "termo_nome": termo,
                "alias_lexico_ref": "0",
                "abreviacao": abrev,
                "data_registro_inicio": args.registro_inicio,
                "data_registro_fim": args.registro_fim,
            }
        )
    for termo, abrev in derived:
        new_row_dicts.append(
            {
                "termo_nome": termo,
                "alias_lexico_ref": "0",
                "abreviacao": abrev,
                "data_registro_inicio": args.registro_inicio,
                "data_registro_fim": args.registro_fim,
            }
        )

    max_ref = _max_alias_lexico_ref(existing_rows)
    last_ref = _assign_refs_to_new_rows(new_row_dicts, max_ref)

    combined = existing_rows + new_row_dicts
    _write_sorted_seed(out_path, combined)

    n_derived = len(derived)
    n_new_rows = n_inferred_only + n_manual + n_derived
    n_skip_comp = n_skip_comp_inf + n_skip_comp_manual

    print()
    print("Lista de abreviações atualizada.")
    print()
    print(f"  Linhas já existentes preservadas: {len(existing_rows)}")
    print(f"  Novas por inferência: {n_inferred_only}")
    print(f"  Novas entradas manuais: {n_manual}")
    print(f"  Novas por derivação atômica: {n_derived}")
    print(f"  Total de linhas novas nesta execução: {n_new_rows}")
    print()
    if n_new_rows > 0:
        lo, hi = max_ref + 1, last_ref
        ref_rng = f"{lo}" if lo == hi else f"{lo} a {hi}"
        print(f"  Novos refs (alias_lexico_ref): {ref_rng}.")
    else:
        print("  Nenhuma nova abreviação encontrada!")
    if n_skip_comp:
        print()
        print(f"  Omitidas por redundância composicional: {n_skip_comp}.")
    print()
    if conflicts:
        print(
            f"Aviso: {len(conflicts)} termo(s) com conflito de abreviação — "
            "omitidos na inferência automática."
        )
        print()
        if args.print_conflicts_resolve:
            _, termos_after_write = _load_existing_seed(out_path)
            eligible = sorted(
                [(t, ab) for t, ab in conflicts if t not in termos_after_write],
                key=lambda x: x[0].lower(),
            )
            n_already_seeded = len(conflicts) - len(eligible)
            if n_already_seeded:
                print(
                    f"  {n_already_seeded} termo(s) já possuem linha no seed "
                    "(após esta execução) — sem prompt interativo."
                )
            if eligible:
                if not sys.stdin.isatty():
                    print(
                        "  Resolução interativa ignorada: stdin não é um terminal "
                        "(use um terminal interativo para --print-conflicts-resolve)."
                    )
                else:
                    print(
                        f"  {len(eligible)} termo(s) sem linha no seed — "
                        "escolha uma abreviação por termo (n = pular)."
                    )
                    resolved_pairs: list[tuple[str, str]] = []
                    for termo_c, abrevs in eligible:
                        opts = sorted(abrevs)
                        picked = _interactive_pick_conflict_abbrev(termo_c, opts)
                        if picked is not None:
                            resolved_pairs.append((termo_c, picked))
                    if resolved_pairs:
                        existing_reload, _ = _load_existing_seed(out_path)
                        extra_rows: list[dict[str, str]] = []
                        for termo_c, abrev_c in resolved_pairs:
                            extra_rows.append(
                                {
                                    "termo_nome": termo_c,
                                    "alias_lexico_ref": "0",
                                    "abreviacao": abrev_c,
                                    "data_registro_inicio": args.registro_inicio,
                                    "data_registro_fim": args.registro_fim,
                                }
                            )
                        max_r = _max_alias_lexico_ref(existing_reload)
                        _assign_refs_to_new_rows(extra_rows, max_r)
                        _write_sorted_seed(out_path, existing_reload + extra_rows)
                        print()
                        print(
                            f"  Resolução de conflitos: {len(resolved_pairs)} nova(s) linha(s) gravada(s)."
                        )
            print()
        elif args.print_conflicts:
            for t, ab in conflicts[:80]:
                print(f"  {t!r}: {sorted(ab)}")
            if len(conflicts) > 80:
                print(f"  ... e mais {len(conflicts) - 80}")
            print()


if __name__ == "__main__":
    main()
