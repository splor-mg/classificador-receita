#!/usr/bin/env python3
"""Forma um CSV de item no schema, no mesmo arquivo.

Preenche item_id, nivel_id e parent_item_id a partir da máscara aberta de
classificacao_id. Com ``--classificacao``, toda essa coluna recebe o valor
informado. Com ``--matriz``, toda a coluna ``matriz`` recebe ``true`` ou
``false`` em caixa baixa. ``--title`` e ``--text`` aplicam a normalização
antes da formação, na mesma conclusão. Não preenche item_ref. Não grava as
colunas de registro.

Uso:
    python scripts/transform.py <arquivo.csv> [--classificacao <valor>] [--matriz true]
    poetry run task transform -- <arquivo.csv> --title <coluna> --text <coluna> --classificacao <valor> --matriz true
"""

from __future__ import annotations

import os
import shutil
import sys
import tempfile
from pathlib import Path

_USAGE = (
    "Uso: python scripts/transform.py <arquivo.csv> "
    "[--title <coluna>] [--text <coluna>] [--classificacao <valor>] [--matriz true|false]"
)


def _parse_args(
    args: list[str],
) -> tuple[Path, str | None, str | None, str | None, str | None]:
    positionals: list[str] = []
    title: str | None = None
    text: str | None = None
    classification: str | None = None
    matriz: str | None = None
    index = 1
    while index < len(args):
        token = args[index]
        if token in ("--classificacao", "--matriz", "--title", "--text"):
            if index + 1 >= len(args) or args[index + 1].startswith("--"):
                raise ValueError(f"A opção '{token}' precisa do valor.")
            value = args[index + 1]
            if token == "--classificacao":
                if classification is not None:
                    raise ValueError("A opção '--classificacao' foi informada duas vezes.")
                classification = value
            elif token == "--matriz":
                if matriz is not None:
                    raise ValueError("A opção '--matriz' foi informada duas vezes.")
                matriz = value
            elif token == "--title":
                if title is not None:
                    raise ValueError("A opção '--title' foi informada duas vezes.")
                title = value
            else:
                if text is not None:
                    raise ValueError("A opção '--text' foi informada duas vezes.")
                text = value
            index += 2
            continue
        if token.startswith("--"):
            raise ValueError(f"Opção desconhecida '{token}'.")
        positionals.append(token)
        index += 1
    if len(positionals) != 1:
        raise ValueError(_USAGE)
    return Path(positionals[0]), title, text, classification, matriz


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv if argv is None else argv)
    try:
        path, title, text, classification, matriz = _parse_args(args)
    except ValueError as exc:
        message = str(exc)
        print(message, file=sys.stderr)
        if message != _USAGE:
            print(_USAGE, file=sys.stderr)
        return 2

    root = Path(__file__).resolve().parents[1]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    from apps.core.column_title_case import (
        ColumnNormalizeError,
        default_abbreviation_list_path,
        load_abbreviations,
        normalize_file,
    )
    from apps.core.item_transform import ItemTransformError, transform_csv

    work = path
    temporary: Path | None = None
    try:
        if title is not None or text is not None:
            handle, name = tempfile.mkstemp(prefix=".transform-", suffix=".csv", dir=path.parent)
            os.close(handle)
            temporary = Path(name)
            shutil.copyfile(path, temporary)
            abbreviations = load_abbreviations(default_abbreviation_list_path()) if title else []
            normalize_file(
                temporary,
                abbreviations,
                title_column=title,
                text_column=text,
                classification=classification,
                matriz=matriz,
            )
            work = temporary
        transform_csv(work, classification=classification, matriz=matriz)
        if temporary is not None:
            os.replace(temporary, path)
            temporary = None
    except (ItemTransformError, ColumnNormalizeError) as exc:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
        print(exc, file=sys.stderr)
        return 1
    print(f"Arquivo formado em {path}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
