"""Testes de validação de salto de nível e zeros canônicos intermédios."""

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from apps.core.code_parent_item_validation import (
    derive_nivel_numero_from_receita_cod_digits,
    intermediate_levels_canonical_zero_error_message,
    nivel_id_receita_cod_derivation_error_message,
    validate_item_nivel_id_receita_cod_derivation,
)


class IntermediateCanonicalZeroMessageTests(SimpleTestCase):
    def test_message_uses_child_and_parent_level_numbers(self):
        msg = intermediate_levels_canonical_zero_error_message(7, 5)
        self.assertIn("nível 7", msg)
        self.assertIn("nível 5", msg)
        self.assertIn("zeros canônicos", msg)


class DeriveNivelNumeroFromReceitaCodTests(SimpleTestCase):
    def test_derives_deepest_non_zero_segment(self):
        mask = [1, 1, 1, 1, 2, 1, 1, 2, 2, 3]
        cod = "1112500200000"
        derived, err = derive_nivel_numero_from_receita_cod_digits(cod, mask)
        self.assertIsNone(err)
        self.assertEqual(derived, 7)

    def test_rejects_detail_after_derived_level(self):
        mask = [1, 1, 1, 1, 2, 1, 1, 2, 2, 3]
        cod = "1112500200001"
        derived, err = derive_nivel_numero_from_receita_cod_digits(cod, mask)
        self.assertIsNone(derived)
        self.assertIn("detalhamento após o nível derivado", err or "")


class NivelIdReceitaCodDerivationMessageTests(SimpleTestCase):
    def test_message_mentions_selected_and_derived_levels(self):
        msg = nivel_id_receita_cod_derivation_error_message(3, 7)
        self.assertIn("nível 3", msg)
        self.assertIn("nível 7", msg)


class ValidateItemNivelIdReceitaCodDerivationTests(SimpleTestCase):
    def _instance_stub(self, *, nivel_numero, receita_cod, mask=None):
        class Nivel:
            nivel_numero = nivel_numero

        class Classificacao:
            pk = 1

        class Instance:
            nivel_id = Nivel()
            receita_cod = receita_cod
            classificacao_id = Classificacao()
            data_vigencia_inicio = None
            data_vigencia_fim = None

        inst = Instance()
        if mask is not None:
            from unittest.mock import patch

            return inst, patch(
                "apps.core.code_parent_item_validation.digit_mask_for_classificacao_vigencia",
                return_value=mask,
            )
        return inst, None

    def test_raises_on_nivel_mismatch(self):
        inst, patcher = self._instance_stub(
            nivel_numero=3,
            receita_cod="1112500200000",
            mask=[1, 1, 1, 1, 2, 1, 1, 2, 2, 3],
        )
        with patcher:
            with self.assertRaises(ValidationError) as ctx:
                validate_item_nivel_id_receita_cod_derivation(inst)
        self.assertIn("nivel_id", ctx.exception.message_dict)

    def test_passes_when_nivel_matches_derivation(self):
        inst, patcher = self._instance_stub(
            nivel_numero=7,
            receita_cod="1112500200000",
            mask=[1, 1, 1, 1, 2, 1, 1, 2, 2, 3],
        )
        with patcher:
            validate_item_nivel_id_receita_cod_derivation(inst)
