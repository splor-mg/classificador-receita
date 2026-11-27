#!/usr/bin/env python3
"""Forma um CSV de item no schema, no mesmo arquivo.

Preenche item_id, nivel_id e parent_item_id a partir da máscara aberta de
classificacao_id. Com ``--classificacao``, toda essa coluna recebe o valor
informado. Com ``--matriz``, toda a coluna ``matriz`` recebe ``true`` ou
``false`` em caixa baixa. ``--title`` e ``--text`` aplicam a normalização
antes da formação, na mesma conclusão. ``--gerado`` preenche ``item_gerado``.
``--valid-init`` e ``--valid-end`` preenchem a vigência. ``--system-init`` e
``--system-end`` preenchem o registro. Pai ausente deixa ``parent_item_id``
vazio, grava o restante e registra a linha em ``.log/<arquivo>``. Não preenche
item_ref.

Uso:
    python scripts/transform.py <arquivo.csv> [--classificacao <valor>] [--matriz true]
    poetry run task transform -- <arquivo.csv> --title <coluna> --text <coluna> --classificacao <valor> --matriz true
"""

from __future__ import annotations

import os
import shutil
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

_USAGE = (
    "Uso: python scripts/transform.py <arquivo.csv> "
    "[--title <coluna>] [--text <coluna>] [--classificacao <valor>] "
    "[--matriz true|false] [--gerado true|false] "
    "[--valid-init <data>] [--valid-end <data|sentinel>] "
    "[--system-init <data>] [--system-end]"
)
_VALUE_FLAGS = (
    "--classificacao",
    "--matriz",
    "--title",
    "--text",
    "--gerado",
    "--valid-init",
    "--valid-end",
    "--system-init",
)


@dataclass
class _Request:
    path: Path
    title: str | None = None
    text: str | None = None
    classification: str | None = None
    matriz: str | None = None
    gerado: str | None = None
    valid_init: str | None = None
    valid_end: str | None = None
    system_init: str | None = None
    system_end: bool = False


def _parse_args(args: list[str]) -> _Request:
    request = _Request(path=Path())
    positionals: list[str] = []
    index = 1
    while index < len(args):
        token = args[index]
        if token == "--system-end":
            if request.system_end:
                raise ValueError("A opção '--system-end' foi informada duas vezes.")
            request.system_end = True
            index += 1
            continue
        if token in _VALUE_FLAGS:
            if index + 1 >= len(args) or args[index + 1].startswith("--"):
                raise ValueError(f"A opção '{token}' precisa do valor.")
            _store_flag(request, token, args[index + 1])
            index += 2
            continue
        if token.startswith("--"):
            raise ValueError(f"Opção desconhecida '{token}'.")
        positionals.append(token)
        index += 1
    if len(positionals) != 1:
        raise ValueError(_USAGE)
    request.path = Path(positionals[0])
    return request


def _store_flag(request: _Request, token: str, value: str) -> None:
    field = {
        "--classificacao": "classification",
        "--matriz": "matriz",
        "--title": "title",
        "--text": "text",
        "--gerado": "gerado",
        "--valid-init": "valid_init",
        "--valid-end": "valid_end",
        "--system-init": "system_init",
    }[token]
    if getattr(request, field) is not None:
        raise ValueError(f"A opção '{token}' foi informada duas vezes.")
    setattr(request, field, value)


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv if argv is None else argv)
    try:
        request = _parse_args(args)
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
    from apps.core.item_transform import ItemTransformError, ParentGap, transform_csv

    path = request.path
    work = path
    temporary: Path | None = None
    try:
        if request.title is not None or request.text is not None:
            handle, name = tempfile.mkstemp(prefix=".transform-", suffix=".csv", dir=path.parent)
            os.close(handle)
            temporary = Path(name)
            shutil.copyfile(path, temporary)
            abbreviations = (
                load_abbreviations(default_abbreviation_list_path()) if request.title else []
            )
            normalize_file(
                temporary,
                abbreviations,
                title_column=request.title,
                text_column=request.text,
                classification=request.classification,
                matriz=request.matriz,
            )
            work = temporary
        gaps = transform_csv(
            work,
            classification=request.classification,
            matriz=request.matriz,
            gerado=request.gerado,
            valid_init=request.valid_init,
            valid_end=request.valid_end,
            system_init=request.system_init,
            system_end=request.system_end,
        )
        if temporary is not None:
            os.replace(temporary, path)
            temporary = None
    except (ItemTransformError, ColumnNormalizeError) as exc:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
        print(exc, file=sys.stderr)
        return 1
    log_path = root / ".log" / path.name
    print(f"Arquivo formado em {path}.")
    if gaps:
        _write_parent_log(log_path, gaps)
        print(f"Linhas com pai ausente em .log/{path.name}.", file=sys.stderr)
        return 1
    log_path.unlink(missing_ok=True)
    return 0


def _write_parent_log(path: Path, gaps: list[ParentGap]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    blocks = [
        f"Linha {gap.line}, código '{gap.code}', não encontra o pai '{gap.parent_code}'.\n{gap.source}"
        for gap in gaps
    ]
    path.write_text("\n\n".join(blocks) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
