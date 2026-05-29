"""Testes CE / CE★ e entrega E2 (spec itemClassificacao_criar_codigo_existente)."""

from datetime import date
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import RequestFactory, SimpleTestCase

from apps.core.forms import ItemClassificacaoForm
from apps.core.models import ItemClassificacao
from apps.core.classification_item_existing_code import (
    ExistingCodeConflict,
    existing_code_conflict_message_html,
    existing_code_conflict_plain_message,
    existing_code_conflict_to_dict,
    lookup_existing_code_conflict_response_data,
    resolve_existing_code_conflict,
    vigencia_intervals_overlap,
)


def _item_stub(
    *,
    pk: int = 1,
    receita_cod: str = "111250100000",
    receita_nome: str = "Receita teste",
    vigencia_inicio: date = date(2018, 1, 1),
    vigencia_fim: date = date(9999, 12, 31),
):
    from apps.core.models import ItemClassificacao

    return SimpleNamespace(
        pk=pk,
        receita_cod=receita_cod,
        receita_nome=receita_nome,
        item_id=f"IT-{receita_cod}",
        data_vigencia_inicio=vigencia_inicio,
        data_vigencia_fim=vigencia_fim,
        _meta=ItemClassificacao._meta,
    )


class VigenciaIntervalsOverlapTests(SimpleTestCase):
    def test_partial_overlap(self) -> None:
        self.assertTrue(
            vigencia_intervals_overlap(
                date(2026, 1, 1),
                date(2026, 12, 31),
                date(2018, 1, 1),
                date(9999, 12, 31),
            )
        )

    def test_no_overlap(self) -> None:
        self.assertFalse(
            vigencia_intervals_overlap(
                date(2026, 1, 1),
                date(2026, 12, 31),
                date(2018, 1, 1),
                date(2025, 12, 31),
            )
        )

    def test_touching_endpoints_count_as_overlap(self) -> None:
        self.assertTrue(
            vigencia_intervals_overlap(
                date(2026, 1, 1),
                date(2026, 12, 31),
                date(2026, 12, 31),
                date(9999, 12, 31),
            )
        )


class ResolveExistingCodeConflictTests(SimpleTestCase):
    def test_returns_none_when_code_empty(self) -> None:
        self.assertIsNone(
            resolve_existing_code_conflict(
                "",
                date(2026, 1, 1),
                date(2026, 12, 31),
            )
        )

    def test_returns_none_when_vigencia_incomplete(self) -> None:
        self.assertIsNone(
            resolve_existing_code_conflict("111250100000", date(2026, 1, 1), None)
        )

    def test_returns_none_when_vigencia_invalid(self) -> None:
        self.assertIsNone(
            resolve_existing_code_conflict(
                "111250100000",
                date(2026, 12, 31),
                date(2026, 1, 1),
            )
        )

    def test_normalizes_masked_code(self) -> None:
        with patch(
            "apps.core.classification_item_existing_code.queryset_active_receita_cod_overlapping_vigencia"
        ) as mock_qs_fn:
            mock_qs = MagicMock()
            mock_qs_fn.return_value = mock_qs
            mock_qs.first.return_value = None

            resolve_existing_code_conflict(
                "1.1.1.2.50.1.0.00.000",
                date(2026, 1, 1),
                date(2026, 12, 31),
            )

            mock_qs_fn.assert_called_once_with(
                "1112501000000",
                date(2026, 1, 1),
                date(2026, 12, 31),
            )

    @patch(
        "apps.core.classification_item_existing_code.queryset_active_receita_cod_overlapping_vigencia"
    )
    def test_returns_conflict_payload(self, mock_qs_fn: MagicMock) -> None:
        item = _item_stub(pk=42)
        mock_qs = MagicMock()
        mock_qs_fn.return_value = mock_qs
        mock_qs.first.return_value = item

        with (
            patch(
                "apps.core.classification_item_existing_code.reverse",
                return_value="/admin/core/itemclassificacao/42/change/",
            ),
            patch(
                "apps.core.classification_item_existing_code.format_receita_cod_by_vigencia",
                return_value="1.1.1.2.50.1.0.00.000",
            ),
        ):
            result = resolve_existing_code_conflict(
                "111250100000",
                date(2026, 1, 1),
                date(2026, 12, 31),
            )

        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.pk, "42")
        self.assertEqual(result.receita_cod, "111250100000")
        self.assertIn("42", result.link_url)
        self.assertEqual(result.vigencia_inicio, date(2018, 1, 1))
        self.assertEqual(result.vigencia_fim, date(9999, 12, 31))

    @patch(
        "apps.core.classification_item_existing_code.queryset_active_receita_cod_overlapping_vigencia"
    )
    def test_queryset_uses_ce_star_ordering(self, mock_qs_fn: MagicMock) -> None:
        mock_qs_fn.return_value.first.return_value = None
        resolve_existing_code_conflict(
            "111250100000",
            date(2026, 1, 1),
            date(2026, 12, 31),
        )
        mock_qs_fn.assert_called_once()

    @patch("apps.core.classification_item_existing_code.ItemClassificacao.objects")
    def test_filter_uses_overlap_not_containment(self, mock_objects: MagicMock) -> None:
        from apps.core.classification_item_existing_code import (
            queryset_active_receita_cod_overlapping_vigencia,
        )

        mock_qs = MagicMock()
        mock_objects.filter.return_value = mock_qs
        mock_qs.order_by.return_value = mock_qs

        queryset_active_receita_cod_overlapping_vigencia(
            "111250100000",
            date(2026, 1, 1),
            date(2026, 12, 31),
        )

        mock_objects.filter.assert_called_once()
        kwargs = mock_objects.filter.call_args[1]
        self.assertEqual(kwargs["receita_cod"], "111250100000")
        self.assertEqual(kwargs["data_vigencia_inicio__lte"], date(2026, 12, 31))
        self.assertEqual(kwargs["data_vigencia_fim__gte"], date(2026, 1, 1))
        mock_qs.order_by.assert_called_once_with(
            "-data_vigencia_inicio",
            "-data_registro_inicio",
            "-pk",
        )


class ExistingCodeConflictMessageHtmlTests(SimpleTestCase):
    def test_html_includes_link_and_next_action_class(self) -> None:
        conflict = ExistingCodeConflict(
            pk="1",
            receita_cod="111250100000",
            receita_cod_display="1.1.1.2.50.1.0.00.000",
            display_label="x",
            link_url="/admin/core/itemclassificacao/1/change/",
            vigencia_inicio=date(2018, 1, 1),
            vigencia_fim=date(9999, 12, 31),
        )
        html = str(existing_code_conflict_message_html(conflict))
        self.assertIn('target="_blank"', html)
        self.assertIn("/admin/core/itemclassificacao/1/change/", html)
        self.assertIn("js-existing-code-conflict-next", html)
        self.assertIn("01/01/2018", html)
        self.assertIn("31/12/9999", html)


class ExistingCodeConflictPlainMessageTests(SimpleTestCase):
    def test_message_includes_code_and_vigencia_br(self) -> None:
        conflict = ExistingCodeConflict(
            pk="1",
            receita_cod="111250100000",
            receita_cod_display="1.1.1.2.50.1.0.00.000",
            display_label="x",
            link_url="/admin/1/change/",
            vigencia_inicio=date(2018, 1, 1),
            vigencia_fim=date(9999, 12, 31),
        )
        msg = existing_code_conflict_plain_message(conflict)
        self.assertIn("1.1.1.2.50.1.0.00.000", msg)
        self.assertIn("01/01/2018", msg)
        self.assertIn("31/12/9999", msg)


class LookupExistingCodeConflictEndpointTests(SimpleTestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()

    def _get(self, **params: str):
        return lookup_existing_code_conflict_response_data(
            self.factory.get("/admin/lookup-existing-code-conflict/", params)
        )

    def test_missing_code_returns_error(self) -> None:
        data = self._get(vigencia_inicio="2026-01-01", vigencia_fim="2026-12-31")
        self.assertFalse(data["ok"])

    @patch(
        "apps.core.classification_item_existing_code.resolve_existing_code_conflict",
        return_value=None,
    )
    def test_no_conflict(self, _mock_resolve: MagicMock) -> None:
        data = self._get(
            code="111250100000",
            vigencia_inicio="2026-01-01",
            vigencia_fim="2026-12-31",
        )
        self.assertTrue(data["ok"])
        self.assertFalse(data["has_conflict"])

    @patch("apps.core.classification_item_existing_code.resolve_existing_code_conflict")
    def test_with_conflict(self, mock_resolve: MagicMock) -> None:
        conflict = ExistingCodeConflict(
            pk="9",
            receita_cod="111250100000",
            receita_cod_display="1.1.1.2.50.1.0.00.000",
            display_label="111250100000 - Nome",
            link_url="/admin/core/itemclassificacao/9/change/",
            vigencia_inicio=date(2018, 1, 1),
            vigencia_fim=date(2025, 12, 31),
        )
        mock_resolve.return_value = conflict
        data = self._get(
            code="111250100000",
            vigencia_inicio="2026-01-01",
            vigencia_fim="2026-12-31",
        )
        self.assertTrue(data["ok"])
        self.assertTrue(data["has_conflict"])
        self.assertEqual(data["conflict"]["pk"], "9")
        self.assertIn("Já existe o", data["message"])
        self.assertIn("message_html", data)
        self.assertIn("js-existing-code-conflict-next", data["message_html"])
        self.assertIn('target="_blank"', data["message_html"])


class ItemClassificacaoFormExistingCodeConflictTests(SimpleTestCase):
    @patch.object(ItemClassificacao, "full_clean")
    @patch("apps.core.forms.validar_receita_nome_guardrail_g1", return_value=(False, None))
    @patch("apps.core.forms.validar_receita_nome_guardrail_g0", return_value=False)
    @patch.object(ItemClassificacaoForm, "_get_receita_cod_digit_rule", return_value=(12, "TEST"))
    @patch("apps.core.classification_item_existing_code.resolve_existing_code_conflict")
    def test_add_blocks_submit_on_conflict(
        self,
        mock_resolve: MagicMock,
        _mock_digits: MagicMock,
        _mock_g0: MagicMock,
        _mock_g1: MagicMock,
        _mock_model_clean: MagicMock,
    ) -> None:
        mock_resolve.return_value = ExistingCodeConflict(
            pk="1",
            receita_cod="111250100000",
            receita_cod_display="1.1.1.2.50.1.0.00.000",
            display_label="x",
            link_url="/admin/1/change/",
            vigencia_inicio=date(2018, 1, 1),
            vigencia_fim=date(9999, 12, 31),
        )
        form = ItemClassificacaoForm(
            data={
                "receita_cod": "111250100000",
                "data_vigencia_inicio": "2026-01-01",
                "data_vigencia_fim": "2026-12-31",
                "matriz": "matriz",
                "item_gerado": "nao",
                "receita_nome": "Nome de teste",
                "receita_nome_base_mode": "sem_base",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("receita_cod", form.errors)
        error_html = str(form.errors["receita_cod"][0])
        self.assertIn("js-existing-code-conflict-next", error_html)
        self.assertIn('target="_blank"', error_html)
        mock_resolve.assert_called_once()


class ExistingCodeConflictDictTests(SimpleTestCase):
    def test_serializes_iso_dates(self) -> None:
        conflict = ExistingCodeConflict(
            pk="1",
            receita_cod="111250100000",
            receita_cod_display="1.1.1.2.50.1.0.00.000",
            display_label="111250100000 - Nome",
            link_url="/admin/change/1/",
            vigencia_inicio=date(2018, 1, 1),
            vigencia_fim=date(9999, 12, 31),
        )
        data = existing_code_conflict_to_dict(conflict)
        self.assertEqual(data["vigencia_inicio"], "2018-01-01")
        self.assertEqual(data["vigencia_fim"], "9999-12-31")
        self.assertEqual(data["vigencia_inicio_display"], "01/01/2018")
        self.assertEqual(data["vigencia_fim_display"], "31/12/9999")
        self.assertEqual(data["pk"], "1")
