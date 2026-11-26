#!/usr/bin/env python3
"""Forma um CSV de item no schema, no mesmo arquivo.

Preenche item_id, nivel_id e parent_item_id a partir da máscara aberta de
classificacao_id. Não preenche item_ref. Não grava as colunas de registro.

Uso:
    python scripts/transform.py <arquivo.csv>
    poetry run task transform -- <arquivo.csv>
"""

from __future__ import annotations

import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv if argv is None else argv)
    if len(args) != 2:
        print(
            "Uso: python scripts/transform.py <arquivo.csv>",
            file=sys.stderr,
        )
        return 2

    root = Path(__file__).resolve().parents[1]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    from apps.core.item_transform import ItemTransformError, transform_csv

    path = Path(args[1])
    try:
        transform_csv(path)
    except ItemTransformError as exc:
        print(exc, file=sys.stderr)
        return 1
    print(f"Arquivo formado em {path}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
