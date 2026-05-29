"""Testes do protocolo B1 (entrada e submit de receita_cod no formulário).

Spec: `_dev/spec_itemClassificacao_mascara_apresentacao.md` (B1.5, B1.8; casos T-B1.5, T-B1.8 no backend).
"""

from unittest.mock import patch

from django.test import SimpleTestCase

from apps.core.forms import ItemClassificacaoForm
from apps.core.models import ItemClassificacao


class ReceitaCodInputSanitizationTests(SimpleTestCase):
    """Contrato de caracteres permitidos no POST (B1.5/B1.8)."""

    def test_dots_allowed_before_digit_normalization(self):
        raw = "1.1.1.2"
        self.assertTrue(raw.replace(".", "").isdigit())
        self.assertEqual(raw.replace(".", ""), "1112")

    def test_hyphen_not_allowed(self):
        raw = "1.1.1-2"
        self.assertFalse(raw.replace(".", "").isdigit())


class ItemClassificacaoFormReceitaCodInputTests(SimpleTestCase):
    _BASE_DATA = {
        "data_vigencia_inicio": "2026-01-01",
        "data_vigencia_fim": "2026-12-31",
        "matriz": "matriz",
        "item_gerado": "nao",
        "receita_nome": "Nome de teste",
        "receita_nome_base_mode": "sem_base",
    }

    @patch.object(ItemClassificacao, "full_clean")
    @patch("apps.core.forms.validar_receita_nome_guardrail_g1", return_value=(False, None))
    @patch("apps.core.forms.validar_receita_nome_guardrail_g0", return_value=False)
    @patch.object(ItemClassificacaoForm, "_get_receita_cod_digit_rule", return_value=(13, "TEST"))
    @patch("apps.core.classification_item_existing_code.resolve_existing_code_conflict", return_value=None)
    def test_clean_rejects_invalid_separator(
        self,
        _mock_conflict,
        _mock_digits,
        _mock_g0,
        _mock_g1,
        _mock_model_clean,
    ):
        data = {**self._BASE_DATA, "receita_cod": "1.1.1-2"}
        form = ItemClassificacaoForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("receita_cod", form.errors)
