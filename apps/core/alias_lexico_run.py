"""
Orquestração da inferência da lista de abreviações (BD + opcional fallback CSV).

Usado pelo comando ``manage.py atualizar_lista_abreviacoes`` e pelo admin de
``ItemClassificacao`` (protocolo após save + export condicional).

**Export (ii)** — após save de item: ``maybe_export_seed_after_item_save_protocol`` usa
``AliasLexicoPersistResult.n_inserted`` (INSERTs reais do protocolo automático,
alinhado a ``insert_alias_lexico_if_new``).

**Export (iii)** — fim do comando em lote: ``maybe_export_seed_after_management_batch``
exporta uma vez se houve qualquer escrita na lista (auto + resolve interactivo).

**v1:** *full scan* de ``ItemClassificacao`` em cada execução; evolução incremental
documentada na spec (*Evolução — desempenho*).
"""

from __future__ import annotations

import csv
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from django.db import transaction
from django.db.models import Max
from django.utils import timezone

from apps.core.admin_mixins import transaction_time_sentinel_for_query
from apps.core.alias_lexico_infer import (
    _atomic_derivations,
    _infer_candidate_sort_key,
    _infer_pairs,
    _is_compositional_redundant,
    _is_transaction_active_row,
    _merge_abbrev_map_from_pair,
    _parse_iso_date,
    sort_pairs_like_registry_order,
)
from apps.core.alias_lexico_protocol import (
    budget_period_contains_instant,
    insert_alias_lexico_if_new,
)
from apps.core.exporter import export_resource
from apps.core.models import ItemClassificacao
from apps.core.models_alias_lexico import AliasLexico

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent.parent
ITEM_CSV = ROOT / "docs/assets/seed_item_classificacao.csv"
SEED_LISTA = ROOT / "docs/assets/seed_lista_abreviacoes.csv"


@dataclass
class AliasLexicoPersistResult:
    """
    Resultado da fase automática (inferência + INSERTs), sem resolução interativa.

    ``n_inserted`` é o contador usado na spec para *Export* **(ii)** (≥1 INSERT real
    do protocolo automático; duplicata CI não incrementa).
    """

    n_inserted: int
    n_skipped_duplicate: int
    n_item_rows_at_t: int
    n_inferred_only: int
    n_derived: int
    n_skip_comp_inf: int
    conflicts: list[tuple[str, set[str]]]


def _fmt_transaction_end_local(dt) -> str:
    if dt is None:
        return ""
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone.get_current_timezone())
    return timezone.localtime(dt).strftime("%Y-%m-%d %H:%M:%S")


def _fmt_budget_period_date(d) -> str:
    if d is None:
        return ""
    return d.strftime("%Y-%m-%d")


def item_instance_to_row_dict(obj: ItemClassificacao) -> dict[str, str]:
    parent_key = ""
    if obj.parent_item_id_id:
        parent_key = obj.parent_item_id.item_id
    sent_q = transaction_time_sentinel_for_query()
    reg_fim = obj.data_registro_fim
    active = reg_fim == sent_q
    fin_s = "9999-12-31 00:00:00" if active else _fmt_transaction_end_local(reg_fim)
    return {
        "item_id": (obj.item_id or "").strip(),
        "item_ref": str(obj.item_ref) if obj.item_ref is not None else "",
        "parent_item_id": parent_key,
        "receita_nome": obj.receita_nome or "",
        "data_vigencia_inicio": _fmt_budget_period_date(obj.data_vigencia_inicio),
        "data_vigencia_fim": _fmt_budget_period_date(obj.data_vigencia_fim),
        "data_registro_inicio": _fmt_transaction_end_local(obj.data_registro_inicio),
        "data_registro_fim": fin_s,
    }


def filter_item_dict_rows_at_t(rows: list[dict], t_instant: datetime) -> list[dict]:
    out: list[dict] = []
    for r in rows:
        if not _is_transaction_active_row(r):
            continue
        vi = _parse_iso_date(r.get("data_vigencia_inicio"))
        vf = _parse_iso_date(r.get("data_vigencia_fim"))
        if budget_period_contains_instant(vi, vf, t_instant):
            out.append(r)
    return out


def load_items_from_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def load_seed_alias_terms_if_fallback(path: Path) -> tuple[dict[str, str], set[str]]:
    abbrev_by_termo: dict[str, str] = {}
    blocked_ci: set[str] = set()
    if not path.is_file():
        return abbrev_by_termo, blocked_ci
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            return abbrev_by_termo, blocked_ci
        seen_ci: set[str] = set()
        for raw in reader:
            termo = (raw.get("termo_nome") or raw.get("termo") or "").strip()
            if not termo:
                continue
            ref_s = (raw.get("alias_lexico_ref") or "").strip()
            try:
                int(ref_s)
            except ValueError:
                continue
            tl = termo.lower()
            if tl in seen_ci:
                continue
            seen_ci.add(tl)
            blocked_ci.add(tl)
            abbrev_by_termo[termo] = (raw.get("abreviacao") or "").strip()
    return abbrev_by_termo, blocked_ci


def run_alias_lexico_infer_persist(
    *,
    t_instant: datetime,
    items_csv_fallback: bool = True,
    alias_seed_fallback: bool = True,
) -> AliasLexicoPersistResult:
    """
    Carrega itens (BD e opcionalmente CSV), aplica inferência, grava novos ``AliasLexico``.

    O campo ``n_inserted`` do resultado é o critério oficial para *Export* **(ii)**.
    Não exporta CSV (quem chama usa ``maybe_export_*`` ou ``export_alias_lexico_seed``).
    """
    rows_raw: list[dict] = []
    n_db = ItemClassificacao.objects.count()
    if n_db > 0:
        qs = ItemClassificacao.objects.select_related("parent_item_id").all()
        rows_raw = [item_instance_to_row_dict(o) for o in qs.iterator(chunk_size=4000)]
        logger.info("%s: ORM item_classificacao %s linhas", __name__, len(rows_raw))

    rows = filter_item_dict_rows_at_t(rows_raw, t_instant)
    if not rows and items_csv_fallback and ITEM_CSV.is_file():
        logger.info("%s: 0 itens em T na BD — fallback %s", __name__, ITEM_CSV)
        rows = filter_item_dict_rows_at_t(load_items_from_csv(ITEM_CSV), t_instant)

    logger.info("%s: linhas item após filtro em T: %s", __name__, len(rows))

    good, conflicts = _infer_pairs(rows)

    abbrev_by_termo: dict[str, str] = {}
    blocked_ci: set[str] = set()
    n_alias = AliasLexico.objects.count()
    if n_alias > 0:
        for al in AliasLexico.objects.all().iterator(chunk_size=2000):
            t = (al.termo or "").strip()
            if not t:
                continue
            blocked_ci.add(t.lower())
            abbrev_by_termo[t] = (al.abreviacao or "").strip()
    elif alias_seed_fallback and SEED_LISTA.is_file():
        logger.info("%s: lista_abreviacoes vazia — fallback %s", __name__, SEED_LISTA)
        abbrev_by_termo, blocked_ci = load_seed_alias_terms_if_fallback(SEED_LISTA)

    initial_blocked_ci = set(blocked_ci)
    initial_pairs: list[tuple[str, str]] = list(abbrev_by_termo.items())

    inferred_candidates = [
        (t, a)
        for t, a in sorted(good.items(), key=lambda kv: kv[0].lower())
        if t.lower() not in blocked_ci
    ]
    inferred_candidates.sort(key=_infer_candidate_sort_key)

    additions: list[tuple[str, str]] = []
    n_skip_comp_inf = 0
    for termo, abrev in inferred_candidates:
        if _is_compositional_redundant(termo, abrev, abbrev_by_termo):
            n_skip_comp_inf += 1
            continue
        additions.append((termo, abrev))
        blocked_ci.add(termo.lower())
        _merge_abbrev_map_from_pair(termo, abrev, abbrev_by_termo)

    n_inferred_only = len(additions)

    known_terms_ci = set(initial_blocked_ci)
    known_terms_ci.update(t.lower() for t, _ in additions)

    phrase_pairs_for_atoms: list[tuple[str, str]] = list(initial_pairs)
    phrase_pairs_for_atoms.extend(additions)
    derived = _atomic_derivations(phrase_pairs_for_atoms, known_terms_ci.copy())

    reg_ini = timezone.now()
    reg_ini_s = timezone.localtime(reg_ini).strftime("%Y-%m-%d %H:%M:%S")
    reg_fim_s = "9999-12-31 00:00:00"
    sent_orm = transaction_time_sentinel_for_query()

    all_new_pairs: list[tuple[str, str]] = list(additions)
    all_new_pairs.extend(derived)
    ordered_pairs = sort_pairs_like_registry_order(all_new_pairs, reg_ini_s, reg_fim_s)

    n_inserted = 0
    n_skipped_dup = 0
    with transaction.atomic():
        mx = AliasLexico.objects.aggregate(m=Max("alias_lexico_ref"))["m"] or 0
        for termo, abrev in ordered_pairs:
            next_ref = mx + 1
            inserted, _ = insert_alias_lexico_if_new(
                termo=termo,
                abreviacao=abrev,
                alias_lexico_ref=next_ref,
                data_registro_inicio=reg_ini,
                data_registro_fim=sent_orm,
            )
            if inserted:
                mx = next_ref
                n_inserted += 1
            else:
                n_skipped_dup += 1

    logger.info(
        "%s: persistência — inseridos=%s duplicados=%s conflitos=%s",
        __name__,
        n_inserted,
        n_skipped_dup,
        len(conflicts),
    )

    return AliasLexicoPersistResult(
        n_inserted=n_inserted,
        n_skipped_duplicate=n_skipped_dup,
        n_item_rows_at_t=len(rows),
        n_inferred_only=n_inferred_only,
        n_derived=len(derived),
        n_skip_comp_inf=n_skip_comp_inf,
        conflicts=conflicts,
    )


def export_alias_lexico_seed() -> dict:
    """Exporta recurso ``lista_abreviacoes`` para ``docs/assets/seed_lista_abreviacoes.csv``."""
    return export_resource(
        "lista_abreviacoes",
        output=str(SEED_LISTA),
        scope="all",
        do_backup=False,
    )


def maybe_export_seed_after_item_save_protocol(n_protocol_auto_inserts: int) -> dict | None:
    """
    *Export* **(ii)** após ``save_model`` em ``ItemClassificacao``: exporta o seed só se
    o protocolo automático produziu pelo menos um INSERT real
    (``n_protocol_auto_inserts >= 1``, critério equivalente a ``insert_alias_lexico_if_new``).
    """
    if n_protocol_auto_inserts < 1:
        logger.info(
            "%s: export (ii) omitido — n_inserted=%s",
            __name__,
            n_protocol_auto_inserts,
        )
        return None
    return export_alias_lexico_seed()


def maybe_export_seed_after_management_batch(
    *,
    n_auto_insert: int,
    n_resolve_insert: int,
    n_resolve_update: int,
) -> dict | None:
    """
    *Export* **(iii)**: uma exportação consolidada ao fim do comando quando a execução
    alterou ``lista_abreviacoes`` (INSERTs do protocolo automático e/ou fase resolve).
    """
    total = n_auto_insert + n_resolve_insert + n_resolve_update
    if total < 1:
        logger.info(
            "%s: export (iii) omitido — auto_insert=%s resolve_insert=%s resolve_update=%s",
            __name__,
            n_auto_insert,
            n_resolve_insert,
            n_resolve_update,
        )
        return None
    return export_alias_lexico_seed()
