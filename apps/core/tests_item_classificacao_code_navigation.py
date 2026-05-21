"""Testes para resolve-code-navigation (spec editar_codigo)."""

from datetime import date

from django.test import RequestFactory, TestCase

from apps.core.item_classificacao_code_lookup import (
    normalize_receita_cod_digits,
    receita_cod_changed_vs_instance,
    resolve_code_navigation_response_data,
)
from apps.core.models import TRANSACTION_TIME_SENTINEL, ItemClassificacao


class ReceitaCodChangeDetectionTests(TestCase):
    def test_unchanged_when_equal_digits(self):
        inst = ItemClassificacao(receita_cod="12345678")
        self.assertFalse(receita_cod_changed_vs_instance("12345678", inst))
        self.assertFalse(receita_cod_changed_vs_instance("12.34.56.78", inst))

    def test_changed_when_different_digits(self):
        inst = ItemClassificacao(receita_cod="12345678")
        self.assertTrue(receita_cod_changed_vs_instance("12345679", inst))

    def test_not_changed_when_post_empty(self):
        inst = ItemClassificacao(receita_cod="12345678")
        self.assertFalse(receita_cod_changed_vs_instance("", inst))


class ResolveCodeNavigationTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.v1_inicio = date(2020, 1, 1)
        self.v1_fim = date(9999, 12, 31)
        self.sentinel = TRANSACTION_TIME_SENTINEL

    def _get(self, **params):
        request = self.factory.get("/admin/resolve/", params)
        return resolve_code_navigation_response_data(request)

    def test_c4_when_code_not_in_database(self):
        data = self._get(
            code="99999999",
            vigencia_inicio="2020-01-01",
            vigencia_fim="9999-12-31",
        )
        self.assertTrue(data["ok"])
        self.assertEqual(data["scenario"], "C4")
        self.assertEqual(data["target"]["view"], "add")
        self.assertIn("receita_cod=99999999", data["target"]["add_url"])

    def test_c1_when_mask_incompatible(self):
        data = self._get(
            code="123",
            vigencia_inicio="2020-01-01",
            vigencia_fim="9999-12-31",
        )
        self.assertFalse(data["ok"])
        self.assertEqual(data["scenario"], "C1")
