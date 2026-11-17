"""Settled validity-window cases. The current year in the conception is 2026."""

from datetime import date

from django.test import SimpleTestCase

from apps.core.admin import (
    ClassificacaoAdmin,
    ItemClassificacaoAdmin,
    NivelHierarquicoAdmin,
    SerieClassificacaoAdmin,
)
from apps.core.validity_search import VigenciaSearchMixin
from apps.core.validity_window import (
    PREFIX_LDO,
    RECORD_ASOF,
    RECORD_SENTINEL,
    STATUS_OK,
    STATUS_REFUSED,
    STATUS_UNRESOLVED,
    resolve_vigencia_window,
)

TODAY = date(2026, 11, 17)


def resolve(**kwargs):
    return resolve_vigencia_window(today=TODAY, **kwargs)


class VigenciaWindowTests(SimpleTestCase):
    def test_empty_is_end_of_current_year(self):
        window = resolve()
        self.assertEqual(window.status, STATUS_OK)
        self.assertEqual(window.start, date(2026, 12, 31))
        self.assertEqual(window.end, date(2026, 12, 31))
        self.assertIsNone(window.version)
        self.assertEqual(window.record_mode, RECORD_SENTINEL)

    def test_month_only(self):
        window = resolve(mes="03")
        self.assertEqual((window.start, window.end), (date(2026, 3, 31), date(2026, 3, 31)))

    def test_year_only(self):
        window = resolve(ano="2024")
        self.assertEqual(window.start, date(2024, 12, 31))

    def test_year_and_month(self):
        window = resolve(ano="2024", mes="03")
        self.assertEqual(window.start, date(2024, 3, 31))

    def test_full_point(self):
        window = resolve(ano="2024", mes="03", dia="15")
        self.assertEqual(window.start, date(2024, 3, 15))

    def test_month_and_day_use_current_year(self):
        window = resolve(mes="03", dia="15")
        self.assertEqual(window.start, date(2026, 3, 15))

    def test_day_only_is_december(self):
        window = resolve(dia="15")
        self.assertEqual(window.start, date(2026, 12, 15))

    def test_year_and_day_is_december(self):
        window = resolve(ano="2024", dia="15")
        self.assertEqual(window.start, date(2024, 12, 15))

    def test_february_non_leap(self):
        window = resolve(ano="2026", mes="02")
        self.assertEqual(window.start, date(2026, 2, 28))

    def test_february_leap(self):
        window = resolve(ano="2024", mes="02")
        self.assertEqual(window.start, date(2024, 2, 29))

    def test_impossible_day_refuses(self):
        window = resolve(ano="2026", mes="04", dia="31")
        self.assertEqual(window.status, STATUS_REFUSED)
        self.assertFalse(window.searches)
        self.assertIn("esq_dia", window.field_errors)

    def test_full_period_must_cover_the_whole_span(self):
        window = resolve(ano="2024", mes="01", dia="01", ano2="2024", mes2="06", dia2="30")
        self.assertEqual(window.start, date(2024, 1, 1))
        self.assertEqual(window.end, date(2024, 6, 30))

    def test_months_on_both_sides(self):
        window = resolve(mes="01", mes2="06")
        self.assertEqual(window.start, date(2026, 1, 31))
        self.assertEqual(window.end, date(2026, 6, 30))

    def test_right_side_only_is_a_point(self):
        window = resolve(mes2="06")
        self.assertEqual(window.start, date(2026, 6, 30))
        self.assertEqual(window.end, date(2026, 6, 30))

    def test_inverted_period_is_reordered_and_told(self):
        window = resolve(ano="2026", mes="08", ano2="2026", mes2="03")
        self.assertEqual(window.start, date(2026, 3, 31))
        self.assertEqual(window.end, date(2026, 8, 31))
        self.assertTrue(window.reordered)
        self.assertIn("31/08/2026", window.reorder_note)
        self.assertIn("31/03/2026", window.reorder_note)

    def test_record_day_is_as_of_that_day(self):
        window = resolve(mes="03", registro="2024-05-15")
        self.assertEqual(window.start, date(2026, 3, 31))
        self.assertEqual(window.record_mode, RECORD_ASOF)
        self.assertEqual(window.record_day, date(2024, 5, 15))

    def test_record_only_keeps_end_of_year(self):
        window = resolve(registro="15/05/2024")
        self.assertEqual(window.start, date(2026, 12, 31))
        self.assertEqual(window.record_day, date(2024, 5, 15))

    def test_registered_version_alone_does_not_invent_a_span(self):
        window = resolve(versao="VERSAO-BRA-2018")
        self.assertEqual(window.status, STATUS_UNRESOLVED)
        self.assertIsNone(window.start)
        self.assertEqual(window.version, "VERSAO-BRA-2018")

    def test_ldo_empty_year(self):
        window = resolve(versao="LDO")
        self.assertEqual(window.status, STATUS_OK)
        self.assertEqual(window.start, date(2026, 5, 15))
        self.assertEqual(window.version, PREFIX_LDO)
        self.assertEqual(window.record_day, date(2026, 5, 15))

    def test_ldo_overwrites_month_and_day(self):
        window = resolve(ano="2025", mes="03", dia="01", versao="LDO")
        self.assertEqual(window.start, date(2025, 5, 15))
        self.assertEqual(window.record_day, date(2025, 5, 15))

    def test_loa_does_not_invent_a_calendar_day(self):
        window = resolve(ano="2025", versao="LOA-PPAG")
        self.assertEqual(window.status, STATUS_UNRESOLVED)
        self.assertIsNone(window.start)
        self.assertIn("LOA-PPAG", window.messages[0])

    def test_ldo_ignores_a_typed_record_day(self):
        window = resolve(ano="2025", versao="LDO", registro="2025-01-01")
        self.assertEqual(window.record_day, date(2025, 5, 15))

    def test_four_changelists_share_the_search(self):
        for admin in (
            SerieClassificacaoAdmin,
            ClassificacaoAdmin,
            NivelHierarquicoAdmin,
            ItemClassificacaoAdmin,
        ):
            self.assertTrue(issubclass(admin, VigenciaSearchMixin))

    def test_date_and_registered_version_refuse(self):
        window = resolve(mes="03", versao="VERSAO-BRA-2018")
        self.assertEqual(window.status, STATUS_REFUSED)
        self.assertFalse(window.searches)
        self.assertIn("versao", window.field_errors)
