"""Testes da sugestão de código filho (spec itemClassificacao_criar_filho)."""

from types import SimpleNamespace

from django.test import SimpleTestCase

from apps.core.item_classificacao_suggest_child_code import (
    _assemble_child_receita_cod,
    _choose_segment_value,
    _level_capacity,
    _radical_digits,
    _resolved_level_and_classificacao_payloads,
    _segment_int_at_level,
)


class SuggestChildCodeAlgorithmTests(SimpleTestCase):
    def test_level_capacity_width_one(self) -> None:
        self.assertEqual(_level_capacity([1, 1, 2], 1), 9)
        self.assertEqual(_level_capacity([1, 1, 2], 3), 99)

    def test_choose_first_when_empty(self) -> None:
        value, strategy = _choose_segment_value(set(), 9)
        self.assertEqual(value, 1)
        self.assertEqual(strategy, "first")

    def test_choose_expansion(self) -> None:
        value, strategy = _choose_segment_value({1, 2}, 9)
        self.assertEqual(value, 3)
        self.assertEqual(strategy, "expansion")

    def test_choose_gap_when_expansion_overflows(self) -> None:
        occupied = {1, 2, 3, 4, 7, 8, 9}
        value, strategy = _choose_segment_value(occupied, 9)
        self.assertEqual(value, 5)
        self.assertEqual(strategy, "gap")

    def test_choose_none_when_exhausted(self) -> None:
        value, strategy = _choose_segment_value(set(range(1, 10)), 9)
        self.assertIsNone(value)
        self.assertEqual(strategy, "")

    def test_assemble_child_cod_iptu_example(self) -> None:
        mask = [1, 1, 1, 1, 2, 1, 2, 3]
        parent_parts = ["1", "1", "1", "2", "50", "0", "00", "000"]
        cod = _assemble_child_receita_cod(mask, parent_parts, 6, 3)
        self.assertEqual(cod, "111250300000")

    def test_assemble_first_child(self) -> None:
        mask = [1, 1, 1, 1, 2, 1, 2, 3]
        parent_parts = ["1", "1", "1", "2", "50", "0", "00", "000"]
        cod = _assemble_child_receita_cod(mask, parent_parts, 6, 1)
        self.assertEqual(cod, "111250100000")

    def test_radical_digits_nm_five(self) -> None:
        mask = [1, 1, 1, 1, 2, 1, 1, 2, 3]
        parent_cod = "1112500000000"
        self.assertEqual(_radical_digits(mask, parent_cod, 5), "111250")

    def test_segment_int_at_level_nine(self) -> None:
        mask = [1, 1, 1, 1, 2, 1, 1, 2, 3]
        parts = ["1", "1", "1", "2", "50", "0", "0", "00", "001"]
        self.assertEqual(_segment_int_at_level(parts, 9), 1)
        self.assertIsNone(_segment_int_at_level(parts, 6))

    def test_assemble_deep_level_nine(self) -> None:
        mask = [1, 1, 1, 1, 2, 1, 1, 2, 3]
        parent_parts = ["1", "1", "1", "2", "50", "0", "0", "00", "000"]
        cod = _assemble_child_receita_cod(mask, parent_parts, 9, 2)
        self.assertEqual(cod, "1112500000002")

    def test_assemble_first_detail_at_level_eight(self) -> None:
        mask = [1, 1, 1, 1, 2, 1, 1, 2, 3]
        parent_parts = ["1", "1", "1", "2", "50", "0", "0", "00", "000"]
        cod = _assemble_child_receita_cod(mask, parent_parts, 8, 2)
        self.assertEqual(cod, "1112500002000")

    def test_classificacao_payload_comes_from_resolved_level(self) -> None:
        class_from_level = SimpleNamespace(
            pk=42,
            classificacao_id="CLASS-NIVEL",
            classificacao_nome="Classificação do nível",
        )
        nivel = SimpleNamespace(
            pk=7,
            nivel_id="NIVEL-6",
            nivel_nome="Sexto nível",
            classificacao_id=class_from_level,
        )

        derived_level, classificacao = _resolved_level_and_classificacao_payloads(nivel, 6)

        self.assertEqual(derived_level["pk"], "7")
        self.assertEqual(derived_level["number"], 6)
        self.assertIsNotNone(classificacao)
        self.assertEqual(classificacao["pk"], "42")
        self.assertEqual(classificacao["classificacao_id"], "CLASS-NIVEL")
