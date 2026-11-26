#!/usr/bin/env python3
"""Normaliza colunas de um CSV, no mesmo arquivo.

Sem flag, ou com ``--title``, a coluna é sobrescrita pela leitura em caixa de
título. Com ``--compare``, a origem permanece e a leitura entra em
``<coluna>_normalized``. Com ``--text``, aspas duplas da coluna, retas ou curvas,
viram aspas simples na própria célula. As opções podem vir juntas.
O separador de entrada é o do cabeçalho. Ponto e vírgula na entrada vira vírgula na gravação.

Uso:
    python scripts/normalize.py <arquivo.csv> [<coluna>] [--compare]
    python scripts/normalize.py <arquivo.csv> [--title <coluna>] [--text <coluna>] [--compare]
    poetry run task normalize -- <arquivo.csv> [<coluna>] [--compare]
    poetry run task normalize -- <arquivo.csv> [--title <coluna>] [--text <coluna>] [--compare]
"""

from __future__ import annotations

import sys
from pathlib import Path

_USAGE = (
    "Uso: python scripts/normalize.py <arquivo.csv> [<coluna>] [--compare]\n"
    "     python scripts/normalize.py <arquivo.csv> [--title <coluna>] [--text <coluna>] [--compare]"
)


class _UsageError(Exception):
    """O pedido não nomeia arquivo e coluna na forma esperada."""


def _parse_args(args: list[str]) -> tuple[Path, str | None, str | None, bool]:
    """Devolve caminho, coluna de título, coluna de texto e se a origem do título fica."""
    positionals: list[str] = []
    title: str | None = None
    text: str | None = None
    compare = False
    index = 1
    while index < len(args):
        token = args[index]
        if token == "--compare":
            if compare:
                raise _UsageError("A opção '--compare' foi informada duas vezes.")
            compare = True
            index += 1
            continue
        if token in ("--title", "--text"):
            if index + 1 >= len(args) or args[index + 1].startswith("--"):
                raise _UsageError(f"A opção '{token}' precisa do nome da coluna.")
            value = args[index + 1]
            if token == "--title":
                if title is not None:
                    raise _UsageError("A opção '--title' foi informada duas vezes.")
                title = value
            else:
                if text is not None:
                    raise _UsageError("A opção '--text' foi informada duas vezes.")
                text = value
            index += 2
            continue
        if token.startswith("--"):
            raise _UsageError(f"Opção desconhecida '{token}'.")
        positionals.append(token)
        index += 1

    if len(positionals) < 1 or len(positionals) > 2:
        raise _UsageError(_USAGE)
    positional_title = positionals[1] if len(positionals) == 2 else None
    if positional_title is not None and title is not None and positional_title != title:
        raise _UsageError("A coluna de título foi informada duas vezes.")
    title = title if title is not None else positional_title
    if title is None and text is None:
        raise _UsageError("Informe a coluna de título ou a coluna de texto.")
    return Path(positionals[0]), title, text, compare


def main(argv: list[str] | None = None, *, abbreviations_path: Path | None = None) -> int:
    args = list(sys.argv if argv is None else argv)
    try:
        path, title_column, text_column, compare = _parse_args(args)
    except _UsageError as exc:
        message = str(exc)
        if message == _USAGE:
            print(message, file=sys.stderr)
        else:
            print(message, file=sys.stderr)
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

    abbreviations: list[str] = []
    if title_column is not None:
        list_path = (
            default_abbreviation_list_path()
            if abbreviations_path is None
            else Path(abbreviations_path)
        )
        try:
            abbreviations = load_abbreviations(list_path)
        except ColumnNormalizeError as exc:
            print(exc, file=sys.stderr)
            return 1
    try:
        sibling = normalize_file(
            path,
            abbreviations,
            title_column=title_column,
            text_column=text_column,
            compare=compare,
        )
    except ColumnNormalizeError as exc:
        print(exc, file=sys.stderr)
        return 1
    if sibling is not None:
        print(f"Coluna '{sibling}' gravada em {path}.")
    elif title_column is not None:
        print(f"Coluna '{title_column}' atualizada em {path}.")
    if text_column is not None and text_column != title_column:
        print(f"Coluna '{text_column}' atualizada em {path}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
