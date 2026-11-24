#!/usr/bin/env python3
"""Grava a leitura em caixa de título de uma coluna, no mesmo CSV.

Aspas duplas encontradas no texto da coluna, retas ou curvas, viram aspas simples na leitura.
O separador do arquivo, vírgula ou ponto e vírgula, é o do cabeçalho.

Uso:
    python scripts/normalize.py <arquivo.csv> <coluna>
    poetry run task normalize -- <arquivo.csv> <coluna>
"""

from __future__ import annotations

import sys
from pathlib import Path


def main(argv: list[str] | None = None, *, abbreviations_path: Path | None = None) -> int:
    args = list(sys.argv if argv is None else argv)
    if len(args) != 3:
        print(
            "Uso: python scripts/normalize.py <arquivo.csv> <coluna>",
            file=sys.stderr,
        )
        return 2

    root = Path(__file__).resolve().parents[1]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    from apps.core.column_title_case import (
        ColumnNormalizeError,
        default_abbreviation_list_path,
        load_abbreviations,
        normalize_csv,
    )

    list_path = (
        default_abbreviation_list_path() if abbreviations_path is None else Path(abbreviations_path)
    )
    try:
        abbreviations = load_abbreviations(list_path)
        sibling = normalize_csv(Path(args[1]), args[2], abbreviations)
    except ColumnNormalizeError as exc:
        print(exc, file=sys.stderr)
        return 1
    print(f"Coluna '{sibling}' gravada em {Path(args[1])}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
