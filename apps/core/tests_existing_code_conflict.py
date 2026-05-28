"""Testes de detecção CE / CE★ (spec itemClassificacao_criar_codigo_existente, entrega E1)."""

from datetime import date
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from apps.core.item_classificacao_existing_code import (
    ExistingCodeConflict,
    existing_code_conflict_to_dict,
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
            "apps.core.item_classificacao_existing_code.queryset_active_receita_cod_overlapping_vigencia"
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
        "apps.core.item_classificacao_existing_code.queryset_active_receita_cod_overlapping_vigencia"
    )
    def test_returns_conflict_payload(self, mock_qs_fn: MagicMock) -> None:
        item = _item_stub(pk=42)
        mock_qs = MagicMock()
        mock_qs_fn.return_value = mock_qs
        mock_qs.first.return_value = item

        with (
            patch(
                "apps.core.item_classificacao_existing_code.reverse",
                return_value="/admin/core/itemclassificacao/42/change/",
            ),
            patch(
                "apps.core.item_classificacao_existing_code.format_receita_cod_by_vigencia",
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
        "apps.core.item_classificacao_existing_code.queryset_active_receita_cod_overlapping_vigencia"
    )
    def test_queryset_uses_ce_star_ordering(self, mock_qs_fn: MagicMock) -> None:
        mock_qs_fn.return_value.first.return_value = None
        resolve_existing_code_conflict(
            "111250100000",
            date(2026, 1, 1),
            date(2026, 12, 31),
        )
        mock_qs_fn.assert_called_once()

    @patch("apps.core.item_classificacao_existing_code.ItemClassificacao.objects")
    def test_filter_uses_overlap_not_containment(self, mock_objects: MagicMock) -> None:
        from apps.core.item_classificacao_existing_code import (
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
        self.assertEqual(data["pk"], "1")
