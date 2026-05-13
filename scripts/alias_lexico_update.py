#!/usr/bin/env python3
"""
Acrescenta registros em ``docs/assets/seed_lista_abreviacoes.csv`` por inferência **conservadora**
a partir de ``docs/assets/seed_item_classificacao.csv`` (arestas **pai → filho direto**).

A lógica de regras vive em ``apps/core/alias_lexico_infer.py`` (sem Django).

Desempenho (**v1**): cada execução faz *full scan* das linhas relevantes do CSV de itens e do seed
de abreviações; otimizações incrementais (watermark, ``updated_at``, filas de alterações) ficam para
evolução futura se o volume o justificar — ver ``_dev/spec_lista_abreviacoes.md`` (secção *Evolução*).

**Comportamento obrigatório:** não remove linhas por ``termo_nome`` já existentes; apenas **adiciona** termos
novos. Conteúdo de ``abreviacao`` / datas de linhas já presentes não é alterado por este script.

Para inferência a partir do PostgreSQL, flags ``(F)`` com efeito no BD e export do seed, use::

  python manage.py atualizar_lista_abreviacoes

Uso (CSV):
  python scripts/alias_lexico_update.py
  poetry run task atualizar-abreviacoes-resolve
"""

from __future__ import annotations

import argparse
import csv
import logging
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.core.alias_lexico_infer import (  # noqa: E402
    _SEED_WRITER_KW,
    _assign_refs_to_new_rows,
    _atomic_derivations,
    _infer_candidate_sort_key,
    _infer_pairs,
    _interactive_pick_conflict_abbrev,
    _is_compositional_redundant,
    _max_alias_lexico_ref,
    _merge_abbrev_map_from_pair,
    _sort_rows_alias_lexico_registry,
)

ITEM_CSV = ROOT / "docs/assets/seed_item_classificacao.csv"
OUT_CSV = ROOT / "docs/assets/seed_lista_abreviacoes.csv"

logger = logging.getLogger(__name__)


def _default_seed_registro_inicio() -> str:
    """``data_registro_inicio`` por omissão: 1 de janeiro do ano civil corrente, 00:00:00."""
    return f"{date.today().year}-01-01 00:00:00"


_SEED_FIELDNAMES = (
    "termo_nome",
    "alias_lexico_ref",
    "abreviacao",
    "data_registro_inicio",
    "data_registro_fim",
)


def _write_sorted_seed(path: Path, rows: list[dict[str, str]]) -> None:
    sorted_rows = _sort_rows_alias_lexico_registry(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(_SEED_FIELDNAMES), **_SEED_WRITER_KW)
        w.writeheader()
        for row in sorted_rows:
            w.writerow({k: row[k] for k in _SEED_FIELDNAMES})


def _load_existing_seed(path: Path) -> tuple[list[dict[str, str]], set[str]]:
    if not path.is_file():
        return [], set()
    rows_out: list[dict[str, str]] = []
    termos: set[str] = set()
    termos_ci: set[str] = set()
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            return [], set()
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
            if tl in termos_ci:
                continue
            termos_ci.add(tl)
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
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    parser = argparse.ArgumentParser(
        description=(
            "Acrescenta ao seed_lista_abreviacoes.csv inferências a partir do item_classificacao "
            "(não altera linhas já existentes)."
        )
    )
    parser.add_argument(
        "--registro-inicio",
        default=None,
        metavar="TS",
        help=(
            "data_registro_inicio para linhas novas (YYYY-MM-DD HH:MM:SS). "
            "Por omissão: 1 de janeiro do ano civil corrente à data de execução, 00:00:00."
        ),
    )
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
    registro_inicio = args.registro_inicio or _default_seed_registro_inicio()

    with ITEM_CSV.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    good, conflicts = _infer_pairs(rows)
    logger.info(
        "infer_csv: infer_pairs concluído — candidatos únicos=%s conflitos=%s",
        len(good),
        len(conflicts),
    )

    out_path = args.output
    out_path.parent.mkdir(parents=True, exist_ok=True)
    existing_rows, existing_termos = _load_existing_seed(out_path)
    blocked_ci = {t.lower() for t in existing_termos}

    abbrev_by_termo: dict[str, str] = {r["termo_nome"]: r["abreviacao"] for r in existing_rows}

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

    known_terms_ci = {t.lower() for t in existing_termos}
    known_terms_ci.update(t.lower() for t, _ in additions)

    phrase_pairs_for_atoms: list[tuple[str, str]] = [
        (r["termo_nome"], r["abreviacao"]) for r in existing_rows
    ]
    phrase_pairs_for_atoms.extend(additions)

    derived = _atomic_derivations(phrase_pairs_for_atoms, known_terms_ci.copy())

    new_row_dicts: list[dict[str, str]] = []
    for termo, abrev in additions:
        new_row_dicts.append(
            {
                "termo_nome": termo,
                "alias_lexico_ref": "0",
                "abreviacao": abrev,
                "data_registro_inicio": registro_inicio,
                "data_registro_fim": args.registro_fim,
            }
        )
    for termo, abrev in derived:
        new_row_dicts.append(
            {
                "termo_nome": termo,
                "alias_lexico_ref": "0",
                "abreviacao": abrev,
                "data_registro_inicio": registro_inicio,
                "data_registro_fim": args.registro_fim,
            }
        )

    max_ref = _max_alias_lexico_ref(existing_rows)
    last_ref = _assign_refs_to_new_rows(new_row_dicts, max_ref)

    combined = existing_rows + new_row_dicts
    _write_sorted_seed(out_path, combined)

    n_derived = len(derived)
    n_new_rows = n_inferred_only + n_derived
    n_skip_comp = n_skip_comp_inf

    logger.info(
        "infer_csv: gravado — existentes=%s novas_inferência=%s derivadas=%s omitidas_comp=%s",
        len(existing_rows),
        n_inferred_only,
        n_derived,
        n_skip_comp,
    )

    print()
    print("Lista de abreviações atualizada.")
    print()
    print(f"  Linhas já existentes preservadas: {len(existing_rows)}")
    print(f"  Novas por inferência: {n_inferred_only}")
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
        logger.info("infer_csv: conflitos silenciosos=%s", len(conflicts))
        print(
            f"Aviso: {len(conflicts)} termo(s) com conflito de abreviação — "
            "omitidos na inferência automática."
        )
        print()
        if args.print_conflicts_resolve:
            _, termos_after_write = _load_existing_seed(out_path)
            termos_after_ci = {t.lower() for t in termos_after_write}
            eligible = sorted(
                [(t, ab) for t, ab in conflicts if t.lower() not in termos_after_ci],
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
                                    "data_registro_inicio": registro_inicio,
                                    "data_registro_fim": args.registro_fim,
                                }
                            )
                        max_r = _max_alias_lexico_ref(existing_reload)
                        _assign_refs_to_new_rows(extra_rows, max_r)
                        _write_sorted_seed(out_path, existing_reload + extra_rows)
                        logger.info(
                            "infer_csv: resolução interativa — %s nova(s) linha(s) no CSV",
                            len(resolved_pairs),
                        )
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
