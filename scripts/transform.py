#!/usr/bin/env python3
"""Forma um CSV de item no schema, no mesmo arquivo.

Preenche item_id, nivel_id e parent_item_id a partir da máscara aberta de
classificacao_id. Com ``--classificacao``, toda essa coluna recebe o valor
informado. Não preenche item_ref. Não grava as colunas de registro.

Uso:
    python scripts/transform.py <arquivo.csv> [--classificacao <valor>]
    poetry run task transform -- <arquivo.csv> [--classificacao <valor>]
"""

from __future__ import annotations

import sys
from pathlib import Path

_USAGE = "Uso: python scripts/transform.py <arquivo.csv> [--classificacao <valor>]"


def _parse_args(args: list[str]) -> tuple[Path, str | None]:
    positionals: list[str] = []
    classification: str | None = None
    index = 1
    while index < len(args):
        token = args[index]
        if token == "--classificacao":
            if index + 1 >= len(args) or args[index + 1].startswith("--"):
                raise ValueError("A opção '--classificacao' precisa do valor.")
            if classification is not None:
                raise ValueError("A opção '--classificacao' foi informada duas vezes.")
            classification = args[index + 1]
            index += 2
            continue
        if token.startswith("--"):
            raise ValueError(f"Opção desconhecida '{token}'.")
        positionals.append(token)
        index += 1
    if len(positionals) != 1:
        raise ValueError(_USAGE)
    return Path(positionals[0]), classification


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv if argv is None else argv)
    try:
        path, classification = _parse_args(args)
    except ValueError as exc:
        message = str(exc)
        print(message, file=sys.stderr)
        if message != _USAGE:
            print(_USAGE, file=sys.stderr)
        return 2

    root = Path(__file__).resolve().parents[1]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    from apps.core.item_transform import ItemTransformError, transform_csv

    try:
        transform_csv(path, classification=classification)
    except ItemTransformError as exc:
        print(exc, file=sys.stderr)
        return 1
    print(f"Arquivo formado em {path}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
