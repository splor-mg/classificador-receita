"""Testes do atalho change → add e vigência **(V3′)**."""

from datetime import date, datetime

from django.test import SimpleTestCase
from django.utils import timezone

from apps.core.item_classificacao_child_from_change import vigencia_filho_from_item_mae
from apps.core.models import ItemClassificacao


def _parent(inicio, fim) -> ItemClassificacao:
    return ItemClassificacao(
        data_vigencia_inicio=inicio,
        data_vigencia_fim=fim,
    )


class VigenciaFilhoFromItemMaeTests(SimpleTestCase):
    def test_fim_filho_sempre_igual_fim_mae(self) -> None:
        ano = date.today().year
        parent = _parent(date(ano, 6, 1), date(ano + 2, 12, 31))
        ini, fim = vigencia_filho_from_item_mae(parent)
        self.assertEqual(fim, date(ano + 2, 12, 31))

    def test_inicio_mae_apos_ano_corrente(self) -> None:
        ano = date.today().year
        parent = _parent(date(ano + 1, 3, 1), date(ano + 5, 12, 31))
        ini, fim = vigencia_filho_from_item_mae(parent)
        self.assertEqual(ini, date(ano + 1, 3, 1))

    def test_fim_mae_antes_ou_igual_1_janeiro_ano_corrente(self) -> None:
        ano = date.today().year
        parent = _parent(date(ano - 2, 1, 1), date(ano - 1, 12, 31))
        ini, _fim = vigencia_filho_from_item_mae(parent)
        self.assertEqual(ini, date(ano - 2, 1, 1))

        parent_eq = _parent(date(ano - 1, 6, 1), date(ano, 1, 1))
        ini_eq, _ = vigencia_filho_from_item_mae(parent_eq)
        self.assertEqual(ini_eq, date(ano - 1, 6, 1))

    def test_mae_cobre_ano_corrente_inicio_1_janeiro(self) -> None:
        ano = date.today().year
        parent = _parent(date(ano - 1, 6, 1), date(ano + 1, 12, 31))
        ini, _ = vigencia_filho_from_item_mae(parent)
        self.assertEqual(ini, date(ano, 1, 1))

    def test_datetime_aware_converte_para_data_local(self) -> None:
        ano = date.today().year
        aware = timezone.make_aware(datetime(ano, 3, 15, 10, 0, 0))
        parent = _parent(aware, date(ano + 1, 12, 31))
        ini, _ = vigencia_filho_from_item_mae(parent)
        self.assertEqual(ini, date(ano, 3, 15))
