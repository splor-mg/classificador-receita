#!/usr/bin/env python3
"""
Converte CSV com separador ';' para separador ',' de forma segura.

Campos cujo texto contém vírgulas são escritos entre aspas (comportamento
padrão de csv.writer com QUOTE_MINIMAL).

Uso (a partir da raiz do repositório):
  python _dev/csv_semicolon_to_comma.py
  python _dev/csv_semicolon_to_comma.py -i docs/assets/seed_item_classificacao_new.csv -o docs/assets/seed_item_classificacao_new.csv
  python _dev/csv_semicolon_to_comma.py -i entrada.csv -o saida.csv --encoding-in utf-8
  python _dev/csv_semicolon_to_comma.py --in-place
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


def convert(
    path_in: Path,
    path_out: Path,
    encoding_in: str,
    encoding_out: str,
) -> int:
    if not path_in.is_file():
        print(f"Arquivo não encontrado: {path_in}", file=sys.stderr)
        return 1

    rows_read = 0
    path_out.parent.mkdir(parents=True, exist_ok=True)

    with path_in.open("r", encoding=encoding_in, newline="") as fin:
        reader = csv.reader(fin, delimiter=";")
        with path_out.open("w", encoding=encoding_out, newline="") as fout:
            writer = csv.writer(
                fout,
                delimiter=",",
                quoting=csv.QUOTE_MINIMAL,
                lineterminator="\n",
            )
            for row in reader:
                writer.writerow(row)
                rows_read += 1

    print(f"Linhas escritas: {rows_read} -> {path_out}")
    return 0


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    default_in = root / "docs" / "assets" / "seed_item_classificacao_new.csv"
    parser = argparse.ArgumentParser(
        description="Converte CSV separado por ';' para ',' (.quote campos com vírgula).",
    )
    parser.add_argument(
        "-i",
        "--input",
        type=Path,
        default=default_in,
        help=f"Caminho do CSV de entrada (default: {default_in})",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Caminho de saída. Se omitido, sobrescreve o entrada com sufixo .tmp e substitui.",
    )
    parser.add_argument(
        "--encoding-in",
        default="cp1252",
        help=(
            "Encoding do arquivo de entrada (default: cp1252, típico de Excel em Windows PT-BR). "
            "Use utf-8 se o arquivo já for UTF-8."
        ),
    )
    parser.add_argument(
        "--encoding-out",
        default="utf-8",
        help="Encoding do arquivo de saída (default: utf-8)",
    )
    parser.add_argument(
        "--in-place",
        action="store_true",
        help="Escreve em arquivo temporário e substitui o -i ao final (mais seguro que sobrescrever direto).",
    )
    args = parser.parse_args()
    path_in = args.input if args.input.is_absolute() else root / args.input

    if args.output is not None:
        path_out = args.output if args.output.is_absolute() else root / args.output
    elif args.in_place:
        path_out = path_in.with_suffix(path_in.suffix + ".comma.tmp")
    else:
        # default: escrever ao lado com sufixo _comma.csv
        path_out = path_in.with_name(path_in.stem + "_comma" + path_in.suffix)

    rc = convert(path_in, path_out, args.encoding_in, args.encoding_out)
    if rc != 0:
        return rc

    if args.in_place and path_out != path_in:
        path_out.replace(path_in)
        print(f"Substituído: {path_in}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
