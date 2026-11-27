"""Formação do CSV de item pela máscara da classificação."""

import csv
import datetime
import io
import tempfile
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from django.test import SimpleTestCase

from apps.core.item_transform import (
    OUTPUT_COLUMNS,
    ItemTransformError,
    default_level_seed_path,
    load_masks,
    transform_csv,
)
from scripts.transform import main

CLASS_10 = "CLASS-RECEITA-UNIAO-2001"
CLASS_13 = "CLASS-RECEITA-UNIAO-2018"


def _csv_bytes(rows: list[list[str]], delimiter: str = ",") -> bytes:
    buffer = io.StringIO()
    csv.writer(buffer, delimiter=delimiter, lineterminator="\n").writerows(rows)
    return buffer.getvalue().encode("utf-8")


def _level_seed() -> list[list[str]]:
    header = [
        "nivel_id",
        "classificacao_id",
        "nivel_numero",
        "estrutura_codigo",
        "numero_digitos",
        "data_registro_fim",
    ]
    rows = [header]
    ten = [
        ("NIVEL-1", CLASS_10, "1", "X.0.0.0.00.00.00", "1"),
        ("NIVEL-2", CLASS_10, "2", "X.X.0.0.00.00.00", "1"),
        ("NIVEL-2", CLASS_10, "2", "X.X.0.0.00.00.00", "1"),
        ("NIVEL-3", CLASS_10, "3", "X.X.X.0.00.00.00", "1"),
        ("NIVEL-4", CLASS_10, "4", "X.X.X.X.00.00.00", "1"),
        ("NIVEL-5", CLASS_10, "5", "X.X.X.X.XX.00.00", "2"),
        ("NIVEL-6", CLASS_10, "6", "X.X.X.X.XX.XX.00", "2"),
        ("NIVEL-7", "CLASS-RECEITA-MG-2001", "7", "X.X.X.X.XX.XX.XX", "2"),
        ("NIVEL-1", CLASS_10, "1", "X.0.0.0.00.0.0.00.000", "1"),
    ]
    for nivel_id, classification, numero, estrutura, digits in ten:
        record_end = "2017-12-31 00:00:00" if estrutura.endswith("000") else "9999-12-31 00:00:00"
        rows.append([nivel_id, classification, numero, estrutura, digits, record_end])
    thirteen = [
        ("NIVEL-1", "1", "X.0.0.0.00.0.0.00.000", "1"),
        ("NIVEL-2", "2", "X.X.0.0.00.0.0.00.000", "1"),
        ("NIVEL-3", "3", "X.X.X.0.00.0.0.00.000", "1"),
        ("NIVEL-4", "4", "X.X.X.X.00.0.0.00.000", "1"),
        ("NIVEL-5", "5", "X.X.X.X.XX.0.0.00.000", "2"),
        ("NIVEL-6", "6", "X.X.X.X.XX.X.0.00.000", "1"),
        ("NIVEL-7", "7", "X.X.X.X.XX.X.X.00.000", "1"),
        ("NIVEL-8", "8", "X.X.X.X.XX.X.X.XX.000", "2"),
        ("NIVEL-9", "9", "X.X.X.X.XX.X.X.XX.XXX", "3"),
    ]
    for nivel_id, numero, estrutura, digits in thirteen:
        classification = CLASS_13 if numero < "8" else "CLASS-RECEITA-MG-2018"
        rows.append([nivel_id, classification, numero, estrutura, digits, "9999-12-31 00:00:00"])
    return rows


def _item(code: str, classification: str = CLASS_10, nome: str = "Nome") -> list[str]:
    return [classification, code, nome]


class ItemTransformTests(SimpleTestCase):
    def _transform(self, rows: list[list[str]], delimiter: str = ",") -> list[list[str]]:
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            seed = directory_path / "niveis.csv"
            item = directory_path / "itens.csv"
            seed.write_bytes(_csv_bytes(_level_seed()))
            item.write_bytes(_csv_bytes(rows, delimiter))
            transform_csv(item, seed)
            text = item.read_text(encoding="utf-8")
        self.assertIn(delimiter, text.splitlines()[0])
        return list(csv.reader(io.StringIO(text), delimiter=delimiter))

    def _cell(self, rows: list[list[str]], line: int, column: str) -> str:
        return rows[line][rows[0].index(column)]

    def test_third_level_code(self):
        rows = self._transform(
            [
                ["classificacao_id", "receita_cod", "receita_nome"],
                _item("1000000000"),
                _item("1100000000"),
                _item("1110000000"),
            ]
        )
        self.assertEqual(rows[0], list(OUTPUT_COLUMNS))
        self.assertEqual(self._cell(rows, 3, "item_id"), "IT-1110000000")
        self.assertEqual(self._cell(rows, 3, "nivel_id"), "NIVEL-3")
        self.assertEqual(self._cell(rows, 3, "parent_item_id"), "IT-1100000000")

    def test_first_level_parent_is_missing_mark(self):
        rows = self._transform(
            [
                ["classificacao_id", "receita_cod"],
                _item("1000000000"),
            ]
        )
        self.assertEqual(self._cell(rows, 1, "item_id"), "IT-1000000000")
        self.assertEqual(self._cell(rows, 1, "nivel_id"), "NIVEL-1")
        self.assertEqual(self._cell(rows, 1, "parent_item_id"), "-")
        self.assertEqual(self._cell(rows, 1, "item_ref"), "")

    def test_seventh_level_on_the_ten_digit_mask(self):
        rows = self._transform(
            [
                ["classificacao_id", "receita_cod"],
                _item("1000000000"),
                _item("1100000000"),
                _item("1110000000"),
                _item("1110000015"),
            ]
        )
        self.assertEqual(self._cell(rows, 4, "nivel_id"), "NIVEL-7")
        self.assertEqual(self._cell(rows, 4, "parent_item_id"), "IT-1110000000")

    def test_eight_digits_on_the_ten_digit_mask_leaves_the_file(self):
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            seed = directory_path / "niveis.csv"
            item = directory_path / "itens.csv"
            seed.write_bytes(_csv_bytes(_level_seed()))
            original = _csv_bytes(
                [
                    ["classificacao_id", "receita_cod"],
                    _item("11100000"),
                ]
            )
            item.write_bytes(original)
            with self.assertRaises(ItemTransformError) as caught:
                transform_csv(item, seed)
            self.assertIn("tem 8 dígitos e a máscara tem 10", str(caught.exception))
            self.assertEqual(item.read_bytes(), original)

    def test_thirteen_digit_mask(self):
        rows = self._transform(
            [
                ["classificacao_id", "receita_cod"],
                ["CLASS-RECEITA-UNIAO-2018", "1000000000000"],
                ["CLASS-RECEITA-UNIAO-2018", "1100000000000"],
                ["CLASS-RECEITA-UNIAO-2018", "1110000000000"],
                ["CLASS-RECEITA-UNIAO-2018", "1112000000000"],
            ]
        )
        self.assertEqual(self._cell(rows, 4, "nivel_id"), "NIVEL-4")
        self.assertEqual(self._cell(rows, 4, "parent_item_id"), "IT-1110000000000")

    def test_sixth_level_parent_on_the_thirteen_digit_mask(self):
        rows = self._transform(
            [
                ["classificacao_id", "receita_cod"],
                ["CLASS-RECEITA-UNIAO-2018", "1000000000000"],
                ["CLASS-RECEITA-UNIAO-2018", "1100000000000"],
                ["CLASS-RECEITA-UNIAO-2018", "1110000000000"],
                ["CLASS-RECEITA-UNIAO-2018", "1112000000000"],
                ["CLASS-RECEITA-UNIAO-2018", "1112120000000"],
                ["CLASS-RECEITA-UNIAO-2018", "1112121000000"],
            ]
        )
        self.assertEqual(self._cell(rows, 6, "nivel_id"), "NIVEL-6")
        self.assertEqual(self._cell(rows, 6, "parent_item_id"), "IT-1112120000000")

    def test_missing_parent_keeps_the_row_and_reports_every_gap(self):
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            seed = directory_path / "niveis.csv"
            item = directory_path / "itens.csv"
            seed.write_bytes(_csv_bytes(_level_seed()))
            item.write_bytes(
                _csv_bytes(
                    [
                        ["classificacao_id", "receita_cod", "receita_nome"],
                        _item("1000000000", nome="Receitas Correntes"),
                        _item("1110000000", nome="Imposto sobre a Renda"),
                        _item("1111000000", nome="Imposto"),
                        _item("9721010000", nome="Dedução"),
                    ]
                )
            )
            gaps = transform_csv(item, seed)
            rows = list(csv.reader(item.open(encoding="utf-8", newline="")))
        self.assertEqual(
            [(gap.code, gap.parent_code) for gap in gaps],
            [
                ("1110000000", "1100000000"),
                ("9721010000", "9721000000"),
            ],
        )
        self.assertIn("1110000000", gaps[0].source)
        self.assertEqual(self._cell(rows, 1, "parent_item_id"), "-")
        self.assertEqual(self._cell(rows, 1, "nivel_id"), "NIVEL-1")
        self.assertEqual(self._cell(rows, 2, "item_id"), "IT-1110000000")
        self.assertEqual(self._cell(rows, 2, "nivel_id"), "NIVEL-3")
        self.assertEqual(self._cell(rows, 2, "parent_item_id"), "")
        self.assertEqual(self._cell(rows, 2, "receita_nome"), "Imposto sobre a Renda")
        self.assertEqual(self._cell(rows, 3, "parent_item_id"), "IT-1110000000")
        self.assertEqual(self._cell(rows, 3, "nivel_id"), "NIVEL-4")
        self.assertEqual(self._cell(rows, 4, "parent_item_id"), "")
        self.assertEqual(self._cell(rows, 4, "nivel_id"), "NIVEL-5")

    def test_vintage_flags_fill_generated_validity_and_record(self):
        moment = datetime.datetime(2026, 11, 27, 10, 42, 5)
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            seed = directory_path / "niveis.csv"
            item = directory_path / "itens.csv"
            seed.write_bytes(_csv_bytes(_level_seed()))
            original = _csv_bytes(
                [
                    ["receita_cod", "receita_nome", "item_gerado", "data_vigencia_fim"],
                    ["1000000000", "Receitas Correntes", "true", "2010-06-15"],
                ]
            )
            item.write_bytes(original)
            with self.assertRaises(ItemTransformError) as caught:
                transform_csv(item, seed, gerado="sim", valid_init="2004-01-01")
            self.assertIn("'--gerado'", str(caught.exception))
            self.assertEqual(item.read_bytes(), original)
            with self.assertRaises(ItemTransformError) as bad_date:
                transform_csv(item, seed, valid_init="2004-13-01")
            self.assertIn("'--valid-init'", str(bad_date.exception))
            self.assertEqual(item.read_bytes(), original)
            transform_csv(
                item,
                seed,
                classification=CLASS_10,
                matriz="TRUE",
                gerado="FALSE",
                valid_init="01-01-2004",
                valid_end="SENTINEL",
                system_init="9999-12-31",
                system_end=True,
                recorded_at=moment,
            )
            rows = list(csv.reader(item.open(encoding="utf-8", newline="")))
        self.assertEqual(self._cell(rows, 1, "matriz"), "true")
        self.assertEqual(self._cell(rows, 1, "item_gerado"), "false")
        self.assertEqual(self._cell(rows, 1, "data_vigencia_inicio"), "2004-01-01")
        self.assertEqual(self._cell(rows, 1, "data_vigencia_fim"), "9999-12-31")
        self.assertEqual(self._cell(rows, 1, "data_registro_inicio"), "9999-12-31 10:42:05")
        self.assertEqual(self._cell(rows, 1, "data_registro_fim"), "9999-12-31 00:00:00")
        self.assertEqual(self._cell(rows, 1, "nivel_id"), "NIVEL-1")

    def test_prose_quotes_keep_every_physical_line(self):
        original = (
            "receita_cod;receita_nome;receita_descricao\n"
            '10000000;Receitas Correntes;Registra tributária," de contribuições"," patrimonial"\n'
            '"11120400;Imposto sobre a Renda;""Registra a renda; b) de proventos."""\n'
        ).encode("utf-8")
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            seed = directory_path / "niveis.csv"
            item = directory_path / "itens.csv"
            seed.write_bytes(_csv_bytes(_level_seed()))
            item.write_bytes(original)
            transform_csv(item, seed)
            rows = list(csv.reader(item.open(encoding="utf-8", newline=""), delimiter=";"))
            raw = item.read_text(encoding="utf-8")
        self.assertEqual(len(rows), 3)
        self.assertEqual(self._cell(rows, 1, "receita_cod"), "10000000")
        self.assertIn("de contribuições", self._cell(rows, 1, "receita_descricao"))
        self.assertEqual(self._cell(rows, 2, "item_id"), "IT-11120400")
        self.assertIn("b) de proventos", self._cell(rows, 2, "receita_descricao"))
        self.assertFalse(self._cell(rows, 2, "receita_descricao").startswith('"'))
        self.assertIn("Registra a renda; b) de proventos.", raw)

    def test_missing_classification_column_is_created_empty(self):
        rows = self._transform(
            [
                ["receita_cod", "receita_nome"],
                ["10000000", "Receitas Correntes"],
            ]
        )
        self.assertEqual(rows[0], list(OUTPUT_COLUMNS))
        self.assertEqual(self._cell(rows, 1, "item_id"), "IT-10000000")
        self.assertEqual(self._cell(rows, 1, "classificacao_id"), "")
        self.assertEqual(self._cell(rows, 1, "nivel_id"), "")
        self.assertEqual(self._cell(rows, 1, "parent_item_id"), "")
        self.assertEqual(self._cell(rows, 1, "receita_nome"), "Receitas Correntes")

    def test_record_columns_stay_and_empty_valid_end_becomes_the_sentinel(self):
        rows = self._transform(
            [
                [
                    "receita_nome",
                    "receita_cod",
                    "classificacao_id",
                    "data_registro_inicio",
                    "data_vigencia_fim",
                ],
                ["Receitas Correntes", "1000000000", CLASS_10, "2002-01-01 00:00:00", ""],
                ["Receita Tributária", "1100000000", CLASS_10, "2002-01-01 00:00:00", "2010-06-15"],
            ]
        )
        self.assertEqual(rows[0], list(OUTPUT_COLUMNS))
        self.assertEqual(self._cell(rows, 1, "data_registro_inicio"), "2002-01-01 00:00:00")
        self.assertEqual(self._cell(rows, 1, "data_registro_fim"), "")
        self.assertEqual(self._cell(rows, 1, "data_vigencia_fim"), "9999-12-31")
        self.assertEqual(self._cell(rows, 2, "data_vigencia_fim"), "2010-06-15")
        self.assertEqual(self._cell(rows, 1, "receita_nome"), "Receitas Correntes")
        self.assertEqual(self._cell(rows, 1, "item_ref"), "")

    def test_foreign_header_leaves_the_file(self):
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            seed = directory_path / "niveis.csv"
            item = directory_path / "itens.csv"
            seed.write_bytes(_csv_bytes(_level_seed()))
            original = _csv_bytes([["rec_cod", "classificacao_id"], ["1000000000", CLASS_10]])
            item.write_bytes(original)
            with self.assertRaises(ItemTransformError) as caught:
                transform_csv(item, seed)
            self.assertIn("A coluna 'rec_cod' não pertence ao schema", str(caught.exception))
            self.assertEqual(item.read_bytes(), original)

    def test_ten_digit_code_on_the_thirteen_digit_mask_is_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            seed = directory_path / "niveis.csv"
            item = directory_path / "itens.csv"
            seed.write_bytes(_csv_bytes(_level_seed()))
            item.write_bytes(
                _csv_bytes(
                    [
                        ["classificacao_id", "receita_cod"],
                        [CLASS_13, "1110000000"],
                    ]
                )
            )
            with self.assertRaises(ItemTransformError) as caught:
                transform_csv(item, seed)
            self.assertIn("a máscara tem 13", str(caught.exception))

    def test_mask_conflict_leaves_the_file(self):
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            seed = directory_path / "niveis.csv"
            item = directory_path / "itens.csv"
            seed.write_bytes(
                _csv_bytes(
                    [
                        [
                            "nivel_id",
                            "classificacao_id",
                            "nivel_numero",
                            "estrutura_codigo",
                            "numero_digitos",
                            "data_registro_fim",
                        ],
                        ["NIVEL-1", "CLASS-X", "1", "X.0.0.0.00.00.00", "1", "9999-12-31 00:00:00"],
                        [
                            "NIVEL-1",
                            "CLASS-X",
                            "1",
                            "X.0.0.0.00.0.0.00.000",
                            "1",
                            "9999-12-31 00:00:00",
                        ],
                    ]
                )
            )
            original = _csv_bytes([["classificacao_id", "receita_cod"], ["CLASS-X", "1000000000"]])
            item.write_bytes(original)
            with self.assertRaises(ItemTransformError) as caught:
                transform_csv(item, seed)
            self.assertIn("mais de uma máscara aberta", str(caught.exception))
            self.assertEqual(item.read_bytes(), original)

    def test_duplicated_code_leaves_the_file(self):
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            seed = directory_path / "niveis.csv"
            item = directory_path / "itens.csv"
            seed.write_bytes(_csv_bytes(_level_seed()))
            original = _csv_bytes(
                [
                    ["classificacao_id", "receita_cod"],
                    _item("1100000000"),
                    _item("1100000000"),
                    _item("1110000000"),
                ]
            )
            item.write_bytes(original)
            with self.assertRaises(ItemTransformError) as caught:
                transform_csv(item, seed)
            self.assertIn("aparece mais de uma vez", str(caught.exception))
            self.assertEqual(item.read_bytes(), original)

    def test_zero_code_leaves_the_file(self):
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            seed = directory_path / "niveis.csv"
            item = directory_path / "itens.csv"
            seed.write_bytes(_csv_bytes(_level_seed()))
            original = _csv_bytes([["classificacao_id", "receita_cod"], _item("0000000000")])
            item.write_bytes(original)
            with self.assertRaises(ItemTransformError) as caught:
                transform_csv(item, seed)
            self.assertIn("não tem nível", str(caught.exception))
            self.assertEqual(item.read_bytes(), original)

    def test_real_level_seed_joins_the_two_families(self):
        masks = load_masks(default_level_seed_path())
        ten = masks[CLASS_10]
        thirteen = masks[CLASS_13]
        self.assertEqual(
            [segment.numero_digitos for segment in ten.segments], [1, 1, 1, 1, 2, 2, 2]
        )
        self.assertEqual(ten.segments[-1].nivel_id, "NIVEL-7")
        self.assertEqual(
            [segment.numero_digitos for segment in thirteen.segments],
            [1, 1, 1, 1, 2, 1, 1, 2, 3],
        )
        self.assertEqual(thirteen.segments[-1].nivel_id, "NIVEL-9")


class TransformCommandTests(SimpleTestCase):
    def test_command_writes_the_file(self):
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            item = directory_path / "itens.csv"
            item.write_bytes(
                _csv_bytes(
                    [
                        ["classificacao_id", "receita_cod"],
                        [CLASS_10, "1000000000"],
                    ]
                )
            )
            with redirect_stdout(io.StringIO()):
                code = main(["transform.py", str(item)])
            rows = list(csv.reader(item.open(encoding="utf-8", newline="")))
        self.assertEqual(code, 0)
        self.assertEqual(rows[1][rows[0].index("nivel_id")], "NIVEL-1")
        self.assertEqual(rows[1][rows[0].index("parent_item_id")], "-")

    def test_command_refusal_does_not_write(self):
        with tempfile.TemporaryDirectory() as directory:
            item = Path(directory) / "itens.csv"
            original = _csv_bytes([["rec_cod"], ["1000000000"]])
            item.write_bytes(original)
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                code = main(["transform.py", str(item)])
            self.assertEqual(code, 1)
            self.assertIn("não pertence ao schema", stderr.getvalue())
            self.assertEqual(item.read_bytes(), original)

    def test_classification_flag_fills_the_column_and_derives_the_level(self):
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            seed = directory_path / "niveis.csv"
            item = directory_path / "itens.csv"
            seed.write_bytes(_csv_bytes(_level_seed()))
            item.write_bytes(
                _csv_bytes(
                    [
                        ["receita_cod", "receita_nome"],
                        ["1000000000", "Receitas Correntes"],
                        ["1100000000", "Receita Tributária"],
                    ]
                )
            )
            with redirect_stdout(io.StringIO()):
                code = main(
                    [
                        "transform.py",
                        str(item),
                        "--classificacao",
                        CLASS_10,
                    ]
                )
            rows = list(csv.reader(item.open(encoding="utf-8", newline="")))
        self.assertEqual(code, 0)
        header = rows[0]

        def cell(row_index: int, name: str) -> str:
            return rows[row_index][header.index(name)]

        self.assertEqual(cell(1, "classificacao_id"), CLASS_10)
        self.assertEqual(cell(2, "classificacao_id"), CLASS_10)
        self.assertEqual(cell(1, "nivel_id"), "NIVEL-1")
        self.assertEqual(cell(1, "parent_item_id"), "-")
        self.assertEqual(cell(2, "parent_item_id"), "IT-1000000000")

    def test_matriz_flag_stores_lowercase_and_rejects_other_values(self):
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            seed = directory_path / "niveis.csv"
            item = directory_path / "itens.csv"
            seed.write_bytes(_csv_bytes(_level_seed()))
            original = _csv_bytes(
                [
                    ["receita_cod", "receita_nome"],
                    ["1000000000", "Receitas Correntes"],
                ]
            )
            item.write_bytes(original)
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                refused = main(
                    ["transform.py", str(item), "--classificacao", CLASS_10, "--matriz", "sim"]
                )
            self.assertEqual(refused, 1)
            self.assertIn("aceita apenas", stderr.getvalue())
            self.assertEqual(item.read_bytes(), original)
            with redirect_stdout(io.StringIO()):
                code = main(
                    [
                        "transform.py",
                        str(item),
                        "--title",
                        "receita_nome",
                        "--classificacao",
                        CLASS_10,
                        "--matriz",
                        "False",
                    ]
                )
            rows = list(csv.reader(item.open(encoding="utf-8", newline="")))
        self.assertEqual(code, 0)
        header = rows[0]

        def cell(row_index: int, name: str) -> str:
            return rows[row_index][header.index(name)]

        self.assertEqual(cell(1, "matriz"), "false")
        self.assertEqual(cell(1, "classificacao_id"), CLASS_10)
        self.assertEqual(cell(1, "receita_nome"), "Receitas Correntes")
        self.assertEqual(cell(1, "nivel_id"), "NIVEL-1")

    def test_command_logs_missing_parents_and_drops_a_stale_log(self):
        log_path = Path(__file__).resolve().parents[2] / ".log" / "lacunas.csv"
        with tempfile.TemporaryDirectory() as directory:
            item = Path(directory) / "lacunas.csv"
            item.write_bytes(
                _csv_bytes(
                    [
                        ["receita_cod", "receita_nome"],
                        ["1000000000", "Receitas Correntes"],
                        ["1110000000", "Imposto sobre a Renda"],
                        ["1111000000", "Imposto"],
                    ]
                )
            )
            stderr = io.StringIO()
            try:
                with redirect_stdout(io.StringIO()), redirect_stderr(stderr):
                    code = main(["transform.py", str(item), "--classificacao", CLASS_10])
                rows = list(csv.reader(item.open(encoding="utf-8", newline="")))
                self.assertEqual(code, 1)
                self.assertIn("Linhas com pai ausente em .log/lacunas.csv.", stderr.getvalue())
                log = log_path.read_text(encoding="utf-8")
                self.assertIn("Linha 3, código '1110000000', não encontra o pai '1100000000'.", log)
                self.assertIn("1110000000,Imposto sobre a Renda", log)
                self.assertNotIn("9721010000", log)
                header = rows[0]
                self.assertEqual(rows[2][header.index("parent_item_id")], "")
                self.assertEqual(rows[2][header.index("nivel_id")], "NIVEL-3")
                self.assertEqual(rows[3][header.index("parent_item_id")], "IT-1110000000")

                item.write_bytes(
                    _csv_bytes(
                        [
                            ["receita_cod"],
                            ["1000000000"],
                            ["1100000000"],
                            ["1110000000"],
                        ]
                    )
                )
                with redirect_stdout(io.StringIO()):
                    clean = main(["transform.py", str(item), "--classificacao", CLASS_10])
                self.assertEqual(clean, 0)
                self.assertFalse(log_path.exists())
            finally:
                log_path.unlink(missing_ok=True)

    def test_command_accepts_system_end_without_a_value(self):
        with tempfile.TemporaryDirectory() as directory:
            item = Path(directory) / "vigencia.csv"
            item.write_bytes(
                _csv_bytes(
                    [
                        ["receita_cod", "receita_nome"],
                        ["1000000000", "receitas correntes"],
                    ]
                )
            )
            with redirect_stdout(io.StringIO()):
                code = main(
                    [
                        "transform.py",
                        str(item),
                        "--title",
                        "receita_nome",
                        "--classificacao",
                        CLASS_10,
                        "--matriz",
                        "true",
                        "--gerado",
                        "false",
                        "--valid-init",
                        "2004-01-01",
                        "--valid-end",
                        "sentinel",
                        "--system-init",
                        "27-11-2026",
                        "--system-end",
                    ]
                )
            rows = list(csv.reader(item.open(encoding="utf-8", newline="")))
        self.assertEqual(code, 0)
        header = rows[0]
        self.assertEqual(rows[1][header.index("receita_nome")], "Receitas Correntes")
        self.assertEqual(rows[1][header.index("item_gerado")], "false")
        self.assertEqual(rows[1][header.index("data_vigencia_inicio")], "2004-01-01")
        self.assertEqual(rows[1][header.index("data_vigencia_fim")], "9999-12-31")
        self.assertTrue(rows[1][header.index("data_registro_inicio")].startswith("2026-11-27 "))
        self.assertEqual(rows[1][header.index("data_registro_fim")], "9999-12-31 00:00:00")
