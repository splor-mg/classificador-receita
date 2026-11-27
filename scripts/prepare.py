#!/usr/bin/env python3
"""Prepara um xlsx ocasional e grava um CSV em ``_dev/.archive``.

O modo 1 junta o código da receita, troca ``M``/``D`` por ``true``/``false`` e
deixa só ``receita_cod``, ``receita_nome``, ``matriz`` e ``receita_descricao``.
As linhas saem em ordem crescente de ``receita_cod``.

Uso:
    python scripts/prepare.py <arquivo.xlsx> --mode 1
    poetry run task prepare -- <arquivo.xlsx> --mode 1
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

_USAGE = "Uso: python scripts/prepare.py <arquivo.xlsx> --mode <número>"
_MODE1_COLUMNS = (
    "CD_CATEGORIA",
    "CD_SUBCATEGORIA",
    "CD_FONTE_CLAS",
    "CD_RUBRICA",
    "CD_ALINEA",
    "CD_SUBALINEA",
    "CD_ITEM",
    "NIVEL_CLAS_RECEITA",
    "DS_CLAS_RECEITA",
    "DS_INTERPRETACAO_RECEITA",
)
_CODE_PARTS = (
    ("CD_CATEGORIA", None),
    ("CD_SUBCATEGORIA", None),
    ("CD_FONTE_CLAS", None),
    ("CD_RUBRICA", None),
    ("CD_ALINEA", 2),
    ("CD_SUBALINEA", 2),
    ("CD_ITEM", 2),
)
_OUTPUT_COLUMNS = ("receita_cod", "receita_nome", "matriz", "receita_descricao")


class PrepareError(Exception):
    """O pedido parou. O CSV de destino não foi gravado."""


def default_archive_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "_dev" / ".archive"


def prepare_xlsx(path: Path, mode: str, archive_dir: Path | None = None) -> Path:
    """Grava o CSV do modo pedido. Devolve o caminho gravado."""
    if mode != "1":
        raise PrepareError(f"O modo '{mode}' ainda não está definido.")
    path = Path(path)
    if path.suffix.lower() != ".xlsx":
        raise PrepareError(f"O arquivo '{path}' não é xlsx.")
    if not path.is_file():
        raise PrepareError(f"O arquivo '{path}' não foi encontrado.")

    from openpyxl import load_workbook

    workbook = load_workbook(path, read_only=True, data_only=True)
    try:
        sheet = workbook.worksheets[0]
        grid = [tuple(row) for row in sheet.iter_rows(values_only=True)]
    finally:
        workbook.close()
    if not grid:
        raise PrepareError(f"O arquivo '{path}' não tem cabeçalho.")
    header = [_header_name(cell) for cell in grid[0]]
    missing = [name for name in _MODE1_COLUMNS if name not in header]
    if missing:
        raise PrepareError(f"O arquivo não tem a coluna '{missing[0]}'.")
    indexes = {name: header.index(name) for name in _MODE1_COLUMNS}
    prepared: list[list[str]] = []
    for line, row in enumerate(grid[1:], start=2):
        if not any(cell is not None and str(cell).strip() for cell in row):
            continue
        values = {name: row[index] if index < len(row) else None for name, index in indexes.items()}
        code = _receita_cod(values, line)
        prepared.append(
            [
                str(code),
                _text(values["DS_CLAS_RECEITA"]),
                _matriz(values["NIVEL_CLAS_RECEITA"], line),
                _text(values["DS_INTERPRETACAO_RECEITA"]),
            ]
        )
    prepared.sort(key=lambda row: int(row[0]))

    destination_dir = default_archive_dir() if archive_dir is None else Path(archive_dir)
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / f"{path.stem}.csv"
    with destination.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(_OUTPUT_COLUMNS)
        writer.writerows(prepared)
    return destination


def _header_name(cell: object) -> str:
    if cell is None:
        return ""
    return str(cell).strip()


def _text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _matriz(value: object, line: int) -> str:
    text = _text(value).casefold()
    if text == "m":
        return "true"
    if text == "d":
        return "false"
    raise PrepareError(
        f"A linha {line}, coluna 'NIVEL_CLAS_RECEITA', tem '{_text(value)}'. "
        "O modo 1 aceita apenas M ou D."
    )


def _receita_cod(values: dict[str, object], line: int) -> int:
    parts = [_digits(values[name], line, name, width) for name, width in _CODE_PARTS]
    return int("".join(parts))


def _digits(value: object, line: int, column: str, width: int | None) -> str:
    if isinstance(value, bool) or value is None or _text(value) == "":
        raise PrepareError(f"A linha {line}, coluna '{column}', está vazia.")
    if isinstance(value, float):
        if not value.is_integer():
            raise PrepareError(f"A linha {line}, coluna '{column}', não é um inteiro.")
        value = int(value)
    if isinstance(value, int):
        if value < 0:
            raise PrepareError(f"A linha {line}, coluna '{column}', não é um inteiro.")
        text = str(value)
    else:
        text = _text(value)
        if not text.isdigit():
            raise PrepareError(f"A linha {line}, coluna '{column}', não é um inteiro.")
    if width is not None:
        text = text.zfill(width)
    return text


def _parse_args(args: list[str]) -> tuple[Path, str]:
    positionals: list[str] = []
    mode: str | None = None
    index = 1
    while index < len(args):
        token = args[index]
        if token == "--mode":
            if index + 1 >= len(args) or args[index + 1].startswith("--"):
                raise ValueError("A opção '--mode' precisa do valor.")
            if mode is not None:
                raise ValueError("A opção '--mode' foi informada duas vezes.")
            mode = args[index + 1]
            index += 2
            continue
        if token.startswith("--"):
            raise ValueError(f"Opção desconhecida '{token}'.")
        positionals.append(token)
        index += 1
    if len(positionals) != 1 or mode is None:
        raise ValueError(_USAGE)
    return Path(positionals[0]), mode


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv if argv is None else argv)
    try:
        path, mode = _parse_args(args)
    except ValueError as exc:
        message = str(exc)
        print(message, file=sys.stderr)
        if message != _USAGE:
            print(_USAGE, file=sys.stderr)
        return 2
    try:
        destination = prepare_xlsx(path, mode)
    except PrepareError as exc:
        print(exc, file=sys.stderr)
        return 1
    print(f"Arquivo gravado em {destination}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
