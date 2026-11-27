"""Preparo ocasional de um xlsx de classificação para CSV."""

import csv
import io
import tempfile
from contextlib import redirect_stderr
from pathlib import Path

from django.test import SimpleTestCase
from openpyxl import Workbook

from scripts.prepare import PrepareError, main, prepare_xlsx

_HEADER = [
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
    "OUTRA",
]


def _workbook(path: Path, rows: list[list[object]]) -> None:
    book = Workbook()
    sheet = book.active
    sheet.append(_HEADER)
    for row in rows:
        sheet.append(row)
    book.save(path)
    book.close()


class PrepareModeTests(SimpleTestCase):
    def test_mode1_builds_the_code_and_keeps_four_columns(self):
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            source = directory_path / "ementario.xlsx"
            _workbook(
                source,
                [
                    [1.0, 1.0, 1.0, 3.0, 0.0, 0.0, 1.0, "d", "Outra rubrica", None],
                    [1, 1, 1, 2, 5, 0, 0, "M", "Imposto sobre Veículos", "Registra o IPVA"],
                ],
            )
            destination = prepare_xlsx(source, "1", directory_path / "saida")
            rows = list(csv.reader(destination.open(encoding="utf-8", newline="")))
        self.assertEqual(destination.name, "ementario.csv")
        self.assertEqual(
            rows,
            [
                ["receita_cod", "receita_nome", "matriz", "receita_descricao"],
                ["1112050000", "Imposto sobre Veículos", "true", "Registra o IPVA"],
                ["1113000001", "Outra rubrica", "false", ""],
            ],
        )

    def test_mode1_refuses_a_missing_column_and_a_foreign_level(self):
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            source = directory_path / "ementario.xlsx"
            book = Workbook()
            sheet = book.active
            sheet.append(["CD_CATEGORIA"])
            book.save(source)
            book.close()
            with self.assertRaises(PrepareError) as missing:
                prepare_xlsx(source, "1", directory_path)
            self.assertIn("CD_SUBCATEGORIA", str(missing.exception))
            self.assertEqual(list(directory_path.glob("*.csv")), [])

            _workbook(source, [[1, 1, 1, 2, 5, 0, 0, "X", "Nome", "Texto"]])
            with self.assertRaises(PrepareError) as level:
                prepare_xlsx(source, "1", directory_path)
            self.assertIn("aceita apenas M ou D", str(level.exception))
            self.assertEqual(list(directory_path.glob("*.csv")), [])

    def test_command_rejects_an_unknown_mode(self):
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            code = main(["prepare.py", "arquivo.xlsx", "--mode", "2"])
        self.assertEqual(code, 1)
        self.assertIn("ainda não está definido", stderr.getvalue())

    def test_command_requires_a_mode(self):
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            code = main(["prepare.py", "arquivo.xlsx"])
        self.assertEqual(code, 2)
        self.assertIn("--mode", stderr.getvalue())
