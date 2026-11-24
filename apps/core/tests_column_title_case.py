"""Leitura em caixa de título de uma coluna CSV."""

import csv
import io
import tempfile
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from django.test import SimpleTestCase

from apps.core.column_title_case import (
    ColumnNormalizeError,
    default_abbreviation_list_path,
    load_abbreviations,
    normalize_csv,
    title_case_reading,
)
from scripts.normalize import main

ABBREVIATIONS = (
    "RGPS",
    "Assist.",
    "Assist. Farmacêutica",
    "Adm.",
    "Adm. MAC",
)


def _csv_bytes(rows: list[list[str]]) -> bytes:
    buffer = io.StringIO()
    csv.writer(buffer, lineterminator="\n").writerows(rows)
    return buffer.getvalue().encode("utf-8")


class TitleCaseReadingTests(SimpleTestCase):
    def test_worked_readings(self):
        readings = {
            "receita tributária": "Receita Tributária",
            "RECEITA TRIBUTÁRIA": "Receita Tributária",
            "imposto de renda": "Imposto de Renda",
            "receita do regime próprio Rgps": "Receita do Regime Próprio RGPS",
            "assist. farmacêutica": "Assist. Farmacêutica",
        }
        for source, expected in readings.items():
            with self.subTest(source=source):
                self.assertEqual(title_case_reading(source, ABBREVIATIONS), expected)

    def test_longer_span_wins_when_casing_would_differ(self):
        self.assertEqual(title_case_reading("adm. mac", ABBREVIATIONS), "Adm. MAC")

    def test_abbreviation_casing_overrides_a_function_word(self):
        self.assertEqual(title_case_reading("taxa de selo", ("DE",)), "Taxa DE Selo")

    def test_empty_cell_stays_empty(self):
        self.assertEqual(title_case_reading("", ABBREVIATIONS), "")

    def test_function_word_stays_lowercase(self):
        self.assertEqual(title_case_reading("de renda", ()), "de Renda")

    def test_hyphen_splits_letter_runs(self):
        self.assertEqual(title_case_reading("meio-ambiente", ()), "Meio-Ambiente")

    def test_double_quotes_become_single_quotes(self):
        self.assertEqual(
            title_case_reading('receita "tributária"', ()),
            "Receita 'Tributária'",
        )
        self.assertEqual(title_case_reading('"cota-parte"', ()), "'Cota-Parte'")
        self.assertEqual(title_case_reading('"Rgps"', ABBREVIATIONS), "'RGPS'")
        self.assertEqual(
            title_case_reading(
                "Imposto sobre Transmissão “Causa Mortis” e Doação de Bens e Direitos",
                (),
            ),
            "Imposto sobre Transmissão 'Causa Mortis' e Doação de Bens e Direitos",
        )

    def test_first_casing_wins_when_the_same_abbreviation_repeats(self):
        self.assertEqual(title_case_reading("rgps", ("RGPS", "rgps")), "RGPS")
        self.assertEqual(title_case_reading("rgps", ("rgps", "RGPS")), "rgps")


class NormalizeCsvTests(SimpleTestCase):
    def test_sibling_column_is_inserted_immediately_to_the_right(self):
        original = _csv_bytes(
            [
                ["id", "nome", "extra"],
                ["7", "receita tributária", "1"],
                ["8", "receita, tributária", "2"],
                ["9", "", "3"],
            ]
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nomes.csv"
            path.write_bytes(original)
            sibling = normalize_csv(path, "nome", ABBREVIATIONS)
            rows = list(csv.reader(path.open(encoding="utf-8", newline="")))

        self.assertEqual(sibling, "nome_normalized")
        self.assertEqual(rows[0], ["id", "nome", "nome_normalized", "extra"])
        self.assertEqual(rows[1], ["7", "receita tributária", "Receita Tributária", "1"])
        self.assertEqual(rows[2], ["8", "receita, tributária", "Receita, Tributária", "2"])
        self.assertEqual(rows[3], ["9", "", "", "3"])

    def test_source_keeps_double_quotes_and_the_reading_uses_single_quotes(self):
        original = _csv_bytes([["nome"], ['receita "tributária"']])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nomes.csv"
            path.write_bytes(original)
            normalize_csv(path, "nome", ())
            rows = list(csv.reader(path.open(encoding="utf-8", newline="")))

        self.assertEqual(rows[1], ['receita "tributária"', "Receita 'Tributária'"])

    def test_semicolon_file_finds_the_column_and_keeps_the_separator(self):
        original = (
            "rec_cod;rec_nome;rec_especificacao\n"
            "10000000;receitas correntes;"
            "Registra o total das receitas tributária, de contribuições.\n"
        ).encode()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "receitas.csv"
            path.write_bytes(original)
            sibling = normalize_csv(path, "rec_nome", ())
            text = path.read_text(encoding="utf-8")
            rows = list(csv.reader(io.StringIO(text), delimiter=";"))

        self.assertEqual(sibling, "rec_nome_normalized")
        self.assertTrue(text.startswith("rec_cod;rec_nome;rec_nome_normalized;rec_especificacao\n"))
        self.assertEqual(rows[1][1], "receitas correntes")
        self.assertEqual(rows[1][2], "Receitas Correntes")
        self.assertEqual(
            rows[1][3],
            "Registra o total das receitas tributária, de contribuições.",
        )

    def test_missing_column_leaves_the_file_unchanged(self):
        self._assert_refused(
            _csv_bytes([["outra"], ["a"]]),
            "nome",
            "A coluna 'nome' não está no arquivo.",
        )

    def test_existing_sibling_leaves_the_file_unchanged(self):
        self._assert_refused(
            _csv_bytes([["nome", "nome_normalized"], ["a", "b"]]),
            "nome",
            "A coluna 'nome_normalized' já existe. O arquivo não foi alterado.",
        )

    def test_non_text_cell_leaves_the_file_unchanged(self):
        self._assert_refused(
            b"nome,extra\nreceita\x00,1\n",
            "nome",
            "A linha 2, coluna 'nome', não é texto.",
        )

    def test_short_row_leaves_the_file_unchanged(self):
        self._assert_refused(
            b"nome,extra\nso-a-primeira\n",
            "extra",
            "A linha 2, coluna 'extra', não é texto.",
        )

    def test_non_utf8_leaves_the_file_unchanged(self):
        self._assert_refused(
            b"nome\n\xff\n",
            "nome",
            "não é texto UTF-8",
        )

    def test_non_csv_leaves_the_file_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nomes.txt"
            original = b"nome\nreceita\n"
            path.write_bytes(original)
            with self.assertRaises(ColumnNormalizeError) as caught:
                normalize_csv(path, "nome", ABBREVIATIONS)
            self.assertIn("não é CSV", str(caught.exception))
            self.assertEqual(path.read_bytes(), original)

    def _assert_refused(self, original: bytes, column: str, message: str):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nomes.csv"
            path.write_bytes(original)
            with self.assertRaises(ColumnNormalizeError) as caught:
                normalize_csv(path, column, ABBREVIATIONS)
            self.assertIn(message, str(caught.exception))
            self.assertEqual(path.read_bytes(), original)


class AbbreviationListTests(SimpleTestCase):
    def test_seed_list_supplies_rgps_and_the_longer_assist_span(self):
        path = default_abbreviation_list_path()
        before = path.read_bytes()
        abbreviations = load_abbreviations(path)
        self.assertEqual(
            title_case_reading("receita do regime próprio Rgps", abbreviations),
            "Receita do Regime Próprio RGPS",
        )
        self.assertEqual(
            title_case_reading("assist. farmacêutica", abbreviations),
            "Assist. Farmacêutica",
        )
        self.assertEqual(path.read_bytes(), before)

    def test_first_row_wins_and_record_end_is_not_a_filter(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "lista.csv"
            path.write_text(
                "termo_nome,abreviacao,data_registro_fim\n"
                "Regime,Rgps,2000-01-01\n"
                "Regime,RGPS,9999-12-31\n",
                encoding="utf-8",
            )
            abbreviations = load_abbreviations(path)
        self.assertEqual(abbreviations, ["Rgps"])
        self.assertEqual(title_case_reading("rgps", abbreviations), "Rgps")


class NormalizeCommandTests(SimpleTestCase):
    def test_command_writes_the_sibling_column(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nomes.csv"
            path.write_bytes(
                _csv_bytes(
                    [
                        ["nome"],
                        ["receita tributária"],
                        ["RECEITA TRIBUTÁRIA"],
                        ["imposto de renda"],
                        ["receita do regime próprio Rgps"],
                        ["assist. farmacêutica"],
                    ]
                )
            )
            with redirect_stdout(io.StringIO()):
                code = main(["normalize.py", str(path), "nome"])
            rows = list(csv.reader(path.open(encoding="utf-8", newline="")))

        self.assertEqual(code, 0)
        self.assertEqual(rows[0], ["nome", "nome_normalized"])
        self.assertEqual(
            [row[0] for row in rows[1:]],
            [
                "receita tributária",
                "RECEITA TRIBUTÁRIA",
                "imposto de renda",
                "receita do regime próprio Rgps",
                "assist. farmacêutica",
            ],
        )
        self.assertEqual(
            [row[1] for row in rows[1:]],
            [
                "Receita Tributária",
                "Receita Tributária",
                "Imposto de Renda",
                "Receita do Regime Próprio RGPS",
                "Assist. Farmacêutica",
            ],
        )

    def test_command_refusal_names_the_column_and_does_not_write(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nomes.csv"
            original = _csv_bytes([["outra"], ["a"]])
            path.write_bytes(original)
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                code = main(["normalize.py", str(path), "nome"])
            self.assertEqual(code, 1)
            self.assertIn("A coluna 'nome' não está no arquivo.", stderr.getvalue())
            self.assertEqual(path.read_bytes(), original)
