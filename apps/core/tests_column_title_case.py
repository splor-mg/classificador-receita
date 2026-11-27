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
    normalize_file,
    plain_text_reading,
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

    def test_connective_abbreviation_stays_a_function_word(self):
        self.assertEqual(title_case_reading("taxa de selo", ("DE",)), "Taxa de Selo")
        self.assertEqual(
            title_case_reading("receita da dívida ativa", ("DA", "IR", "DA-MJM")),
            "Receita da Dívida Ativa",
        )
        self.assertEqual(title_case_reading("ir", ("DA", "IR")), "IR")
        self.assertEqual(title_case_reading("da-mjm", ("DA", "DA-MJM")), "DA-MJM")

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
            sibling = normalize_csv(path, "nome", ABBREVIATIONS, compare=True)
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
            normalize_csv(path, "nome", (), compare=True)
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
            sibling = normalize_csv(path, "rec_nome", (), compare=True)
            text = path.read_text(encoding="utf-8")
            rows = list(csv.reader(io.StringIO(text)))

        self.assertEqual(sibling, "rec_nome_normalized")
        self.assertTrue(text.startswith("rec_cod,rec_nome,rec_nome_normalized,rec_especificacao\n"))
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
            compare=True,
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

    def test_unknown_encoding_leaves_the_file_unchanged(self):
        self._assert_refused(
            b"nome\n\x81\n",
            "nome",
            "não é UTF-8 nem Windows-1252",
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

    def _assert_refused(self, original: bytes, column: str, message: str, *, compare: bool = False):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nomes.csv"
            path.write_bytes(original)
            with self.assertRaises(ColumnNormalizeError) as caught:
                normalize_csv(path, column, ABBREVIATIONS, compare=compare)
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
        self.assertNotIn("DA", abbreviations)
        self.assertIn("IR", abbreviations)
        self.assertIn("DA-MJM", abbreviations)
        self.assertEqual(
            title_case_reading("receita da dívida ativa", abbreviations),
            "Receita da Dívida Ativa",
        )
        self.assertEqual(title_case_reading("ir", abbreviations), "IR")
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
    def test_command_overwrites_the_title_column(self):
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
        self.assertEqual(rows[0], ["nome"])
        self.assertEqual(
            [row[0] for row in rows[1:]],
            [
                "Receita Tributária",
                "Receita Tributária",
                "Imposto de Renda",
                "Receita do Regime Próprio RGPS",
                "Assist. Farmacêutica",
            ],
        )

    def test_compare_flag_keeps_the_source_and_writes_the_sibling(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nomes.csv"
            path.write_bytes(_csv_bytes([["nome"], ["receita tributária"]]))
            with redirect_stdout(io.StringIO()):
                code = main(["normalize.py", str(path), "--title", "nome", "--compare"])
            rows = list(csv.reader(path.open(encoding="utf-8", newline="")))

        self.assertEqual(code, 0)
        self.assertEqual(rows[1], ["receita tributária", "Receita Tributária"])

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

    def test_title_flag_matches_the_positional_column(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nomes.csv"
            path.write_bytes(_csv_bytes([["nome"], ["receita tributária"]]))
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = main(["normalize.py", str(path), "--title", "nome"])
            rows = list(csv.reader(path.open(encoding="utf-8", newline="")))

        self.assertEqual(code, 0)
        self.assertIn("Coluna 'nome' atualizada", stdout.getvalue())
        self.assertEqual(rows[0], ["nome"])
        self.assertEqual(rows[1], ["Receita Tributária"])

    def test_text_flag_overwrites_double_quotes_and_skips_title_case(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nomes.csv"
            path.write_bytes(_csv_bytes([["nome", "texto"], ["1", 'receita "tributária"']]))
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = main(["normalize.py", str(path), "--text", "texto"])
            rows = list(csv.reader(path.open(encoding="utf-8", newline="")))

        self.assertEqual(code, 0)
        self.assertIn("Coluna 'texto' atualizada", stdout.getvalue())
        self.assertNotIn("_normalized", stdout.getvalue())
        self.assertEqual(rows[0], ["nome", "texto"])
        self.assertEqual(rows[1], ["1", "receita 'tributária'"])

    def test_title_and_text_flags_name_different_columns(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nomes.csv"
            path.write_bytes(_csv_bytes([["nome", "texto"], ["receita tributária", 'disse "oi"']]))
            with redirect_stdout(io.StringIO()):
                code = main(["normalize.py", str(path), "--title", "nome", "--text", "texto"])
            rows = list(csv.reader(path.open(encoding="utf-8", newline="")))

        self.assertEqual(code, 0)
        self.assertEqual(rows[0], ["nome", "texto"])
        self.assertEqual(rows[1], ["Receita Tributária", "disse 'oi'"])

    def test_compare_keeps_the_title_source_beside_the_text_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nomes.csv"
            path.write_bytes(_csv_bytes([["nome", "texto"], ["receita tributária", 'disse "oi"']]))
            with redirect_stdout(io.StringIO()):
                code = main(
                    [
                        "normalize.py",
                        str(path),
                        "--title",
                        "nome",
                        "--text",
                        "texto",
                        "--compare",
                    ]
                )
            rows = list(csv.reader(path.open(encoding="utf-8", newline="")))

        self.assertEqual(code, 0)
        self.assertEqual(rows[0], ["nome", "nome_normalized", "texto"])
        self.assertEqual(rows[1], ["receita tributária", "Receita Tributária", "disse 'oi'"])

    def test_positional_title_and_text_flag_can_share_the_command(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nomes.csv"
            path.write_bytes(_csv_bytes([["nome", "texto"], ["imposto de renda", 'cota "parte"']]))
            with redirect_stdout(io.StringIO()):
                code = main(["normalize.py", str(path), "nome", "--text", "texto"])
            rows = list(csv.reader(path.open(encoding="utf-8", newline="")))

        self.assertEqual(code, 0)
        self.assertEqual(rows[0], ["nome", "texto"])
        self.assertEqual(rows[1], ["Imposto de Renda", "cota 'parte'"])

    def test_path_only_converts_windows_1252_and_semicolons(self):
        original = 'nome;texto\nReceita Tributária;disse "oi"\n'.encode("cp1252")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "receitas.csv"
            path.write_bytes(original)
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = main(["normalize.py", str(path)])
            raw = path.read_bytes()
            rows = list(csv.reader(path.open(encoding="utf-8", newline="")))
        self.assertEqual(code, 0)
        self.assertIn("gravado em UTF-8, separado por vírgula", stdout.getvalue())
        raw.decode("utf-8")
        self.assertEqual(rows, [["nome", "texto"], ["Receita Tributária", 'disse "oi"']])

    def test_path_only_keeps_a_utf8_comma_file(self):
        original = "nome,texto\nReceita Tributária,ok\n".encode("utf-8")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "receitas.csv"
            path.write_bytes(original)
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = main(["normalize.py", str(path)])
            kept = path.read_bytes()
        self.assertEqual(code, 0)
        self.assertIn("já está em UTF-8", stdout.getvalue())
        self.assertEqual(kept, original)

    def test_windows_1252_title_is_written_as_utf8(self):
        original = "nome\nreceita tributária\n".encode("cp1252")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nomes.csv"
            path.write_bytes(original)
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = main(["normalize.py", str(path), "--title", "nome"])
            rows = list(csv.reader(path.open(encoding="utf-8", newline="")))
        self.assertEqual(code, 0)
        self.assertEqual(rows[1], ["Receita Tributária"])
        self.assertIn("Windows-1252", stdout.getvalue())

    def test_two_different_title_names_are_refused(self):
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            code = main(["normalize.py", "arquivo.csv", "nome", "--title", "outra"])
        self.assertEqual(code, 2)
        self.assertIn("A coluna de título foi informada duas vezes.", stderr.getvalue())


class PlainTextNormalizeTests(SimpleTestCase):
    def test_straight_and_curly_quotes_become_single_quotes(self):
        self.assertEqual(plain_text_reading('disse "oi"'), "disse 'oi'")
        self.assertEqual(plain_text_reading("“Causa Mortis”"), "'Causa Mortis'")
        self.assertEqual(plain_text_reading("receita tributária"), "receita tributária")

    def test_text_column_is_overwritten_and_no_sibling_is_created(self):
        original = _csv_bytes(
            [["id", "texto"], ["7", 'Registra a renda "tributária", de contribuições.']]
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "receitas.csv"
            path.write_bytes(original)
            sibling = normalize_file(path, (), text_column="texto").sibling
            rows = list(csv.reader(path.open(encoding="utf-8", newline="")))

        self.assertIsNone(sibling)
        self.assertEqual(rows[0], ["id", "texto"])
        self.assertEqual(
            rows[1],
            ["7", "Registra a renda 'tributária', de contribuições."],
        )

    def test_same_column_overwrites_with_the_title_reading(self):
        original = _csv_bytes([["nome"], ['receita "tributária"']])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nomes.csv"
            path.write_bytes(original)
            sibling = normalize_file(path, (), title_column="nome", text_column="nome").sibling
            rows = list(csv.reader(path.open(encoding="utf-8", newline="")))

        self.assertIsNone(sibling)
        self.assertEqual(rows[0], ["nome"])
        self.assertEqual(rows[1], ["Receita 'Tributária'"])

    def test_compare_on_the_same_column_keeps_the_source(self):
        original = _csv_bytes([["nome"], ['receita "tributária"']])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nomes.csv"
            path.write_bytes(original)
            sibling = normalize_file(
                path, (), title_column="nome", text_column="nome", compare=True
            ).sibling
            rows = list(csv.reader(path.open(encoding="utf-8", newline="")))

        self.assertEqual(sibling, "nome_normalized")
        self.assertEqual(rows[1], ['receita "tributária"', "Receita 'Tributária'"])

    def test_semicolon_text_column_keeps_the_separator(self):
        buffer = io.StringIO()
        csv.writer(buffer, delimiter=";", lineterminator="\n").writerows(
            [
                ["receita_cod", "receita_descricao"],
                ["11120400", 'Registra a renda "tributária"; b) de proventos.'],
            ]
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "receitas.csv"
            path.write_bytes(buffer.getvalue().encode())
            normalize_file(path, (), text_column="receita_descricao")
            text = path.read_text(encoding="utf-8")
            rows = list(csv.reader(io.StringIO(text)))

        self.assertTrue(text.startswith("receita_cod,receita_descricao\n"))
        self.assertEqual(rows[1][1], "Registra a renda 'tributária'; b) de proventos.")

    def test_last_column_keeps_a_semicolon_and_replaces_quotes_to_the_end_of_the_line(self):
        original = (
            "receita_cod;receita_nome;receita_descricao\n"
            '10000000;Receitas Correntes;Registra a renda tributária," de contribuições."\n'
            '"11120400;Imposto sobre a Renda;""Registra a renda; b) de proventos."""\n'
        ).encode()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "receitas.csv"
            path.write_bytes(original)
            sibling = normalize_file(path, (), text_column="receita_descricao").sibling
            text = path.read_text(encoding="utf-8")
            rows = list(csv.reader(io.StringIO(text)))

        self.assertIsNone(sibling)
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[1][0], "10000000")
        self.assertEqual(rows[1][1], "Receitas Correntes")
        self.assertEqual(rows[1][2], "Registra a renda tributária,' de contribuições.'")
        self.assertTrue(text.splitlines()[1].startswith('10000000,Receitas Correntes,"Registra'))
        self.assertTrue(text.splitlines()[1].endswith('"'))
        self.assertNotIn(' "de', text.splitlines()[1])
        self.assertIn(",' de contribuições.'", text.splitlines()[1])
        self.assertEqual(rows[2][0], "11120400")
        self.assertEqual(rows[2][1], "Imposto sobre a Renda")
        self.assertEqual(rows[2][2], "Registra a renda; b) de proventos.")
        self.assertTrue(text.splitlines()[2].startswith('11120400,Imposto sobre a Renda,"'))
        self.assertEqual(text.splitlines()[2].count('"'), 2)

    def test_middle_text_column_ends_at_the_next_separator(self):
        original = (
            "id;texto;extra\n" '1;disse "oi";fim da "frase"\n' '"9;""dentro""; resto"\n'
        ).encode()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "receitas.csv"
            path.write_bytes(original)
            normalize_file(path, (), text_column="texto")
            rows = list(csv.reader(path.open(encoding="utf-8", newline="")))

        self.assertEqual(rows[1], ["1", "disse 'oi'", 'fim da "frase"'])
        self.assertEqual(rows[2][1], "dentro")
        self.assertEqual(rows[2][2], " resto")

    def test_missing_text_column_leaves_the_file_unchanged(self):
        original = _csv_bytes([["outra"], ["a"]])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nomes.csv"
            path.write_bytes(original)
            with self.assertRaises(ColumnNormalizeError) as caught:
                normalize_file(path, (), text_column="texto")
            self.assertIn("A coluna 'texto' não está no arquivo.", str(caught.exception))
            self.assertEqual(path.read_bytes(), original)

    def test_existing_sibling_blocks_the_text_overwrite_too(self):
        original = _csv_bytes([["nome", "nome_normalized", "texto"], ["a", "b", 'disse "oi"']])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nomes.csv"
            path.write_bytes(original)
            with self.assertRaises(ColumnNormalizeError) as caught:
                normalize_file(path, (), title_column="nome", text_column="texto", compare=True)
            self.assertIn("já existe", str(caught.exception))
            self.assertEqual(path.read_bytes(), original)

    def test_classification_flag_fills_every_row(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "receitas.csv"
            path.write_bytes(
                _csv_bytes(
                    [
                        ["receita_cod", "receita_nome", "receita_descricao"],
                        ["1000000000", "Receitas Correntes", "Registra o total."],
                        ["1100000000", "Receita Tributária", "Outra"],
                    ]
                )
            )
            with redirect_stdout(io.StringIO()):
                code = main(
                    [
                        "normalize.py",
                        str(path),
                        "--classificacao",
                        "CLASS-RECEITA-UNIAO-2001",
                    ]
                )
            rows = list(csv.reader(path.open(encoding="utf-8", newline="")))

        self.assertEqual(code, 0)
        self.assertEqual(
            rows[0],
            ["classificacao_id", "receita_cod", "receita_nome", "receita_descricao"],
        )
        self.assertEqual(rows[1][0], "CLASS-RECEITA-UNIAO-2001")
        self.assertEqual(rows[2][0], "CLASS-RECEITA-UNIAO-2001")
        self.assertEqual(rows[1][2], "Receitas Correntes")

    def test_classification_flag_overwrites_and_keeps_title_and_text(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "receitas.csv"
            path.write_bytes(
                _csv_bytes(
                    [
                        ["receita_nome", "receita_descricao", "classificacao_id"],
                        ["receita tributária", 'disse "oi"', "OUTRA"],
                    ]
                )
            )
            with redirect_stdout(io.StringIO()):
                code = main(
                    [
                        "normalize.py",
                        str(path),
                        "--title",
                        "receita_nome",
                        "--text",
                        "receita_descricao",
                        "--classificacao",
                        "CLASS-RECEITA-UNIAO-2001",
                    ]
                )
            rows = list(csv.reader(path.open(encoding="utf-8", newline="")))

        self.assertEqual(code, 0)
        self.assertEqual(rows[0], ["receita_nome", "receita_descricao", "classificacao_id"])
        self.assertEqual(rows[1][0], "Receita Tributária")
        self.assertEqual(rows[1][1], "disse 'oi'")
        self.assertEqual(rows[1][2], "CLASS-RECEITA-UNIAO-2001")

    def test_matriz_flag_stores_lowercase_true_or_false(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "receitas.csv"
            path.write_bytes(
                _csv_bytes(
                    [
                        ["receita_cod", "receita_nome"],
                        ["1000000000", "Receitas Correntes"],
                        ["1100000000", "Receita Tributária"],
                    ]
                )
            )
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                refused = main(["normalize.py", str(path), "--matriz", "sim"])
            self.assertEqual(refused, 1)
            self.assertIn("aceita apenas", stderr.getvalue())
            with redirect_stdout(io.StringIO()):
                code = main(["normalize.py", str(path), "--matriz", "TRUE"])
            rows = list(csv.reader(path.open(encoding="utf-8", newline="")))

        self.assertEqual(code, 0)
        self.assertEqual(rows[0], ["receita_cod", "matriz", "receita_nome"])
        self.assertEqual([row[1] for row in rows[1:]], ["true", "true"])
