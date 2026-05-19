"""Testes para ``apps.core.admin_formatters``.

Foco: política de apresentação de ``receita_cod`` em telas do admin de
``ItemClassificacao`` (changelist e ``semantic_value_resolver`` de FKs
semânticas) — resolução em dois níveis (estrita + secundária).
Ver ``_dev/spec_itemClassificacao_mascara_apresentacao.md``.
"""

import datetime

from django.test import SimpleTestCase, TestCase

from apps.core.admin_formatters import (
    _apply_digit_mask,
    _resolve_secondary_digit_mask_for_admin_display,
    format_receita_cod_by_vigencia,
    format_receita_cod_for_admin_display,
)
from apps.core.models import (
    Classificacao,
    NivelHierarquico,
    SerieClassificacao,
    TRANSACTION_TIME_SENTINEL,
)


SENTINEL = TRANSACTION_TIME_SENTINEL
SENTINEL_DATE = datetime.date(9999, 12, 31)


class ApplyDigitMaskTests(SimpleTestCase):
    """``_apply_digit_mask`` é puro; testa compatibilidade e formatação."""

    def test_mascara_compativel_formata_codigo(self):
        self.assertEqual(
            _apply_digit_mask("1100000000000", [1, 1, 1, 1, 2, 1, 1, 2, 3]),
            "1.1.0.0.00.0.0.00.000",
        )

    def test_mascara_vazia_retorna_none(self):
        self.assertIsNone(_apply_digit_mask("1100000000000", []))
        self.assertIsNone(_apply_digit_mask("1100000000000", None))

    def test_mascara_com_zero_retorna_none(self):
        self.assertIsNone(_apply_digit_mask("1100000000000", [1, 1, 0, 1]))

    def test_soma_diferente_de_len_codigo_retorna_none(self):
        self.assertIsNone(_apply_digit_mask("1100000000000", [1, 1, 1]))
        self.assertIsNone(_apply_digit_mask("1100", [1, 1, 1, 1, 1]))


def _make_serie() -> SerieClassificacao:
    return SerieClassificacao.objects.create(
        serie_id="SERIE-TEST",
        serie_ref=1,
        serie_nome="Série de teste",
        data_vigencia_inicio=datetime.date(2000, 1, 1),
        data_vigencia_fim=SENTINEL_DATE,
        data_registro_inicio=datetime.datetime(2000, 1, 1, 0, 0, 0),
        data_registro_fim=SENTINEL,
    )


def _make_classificacao(serie: SerieClassificacao) -> Classificacao:
    return Classificacao.objects.create(
        classificacao_id="CLASS-TEST",
        classificacao_ref=1,
        serie_id=serie,
        classificacao_nome="Classificação de teste",
        numero_niveis=9,
        data_vigencia_inicio=datetime.date(2000, 1, 1),
        data_vigencia_fim=SENTINEL_DATE,
        data_registro_inicio=datetime.datetime(2000, 1, 1, 0, 0, 0),
        data_registro_fim=SENTINEL,
    )


def _make_nivel(
    classificacao: Classificacao,
    *,
    nivel_ref: int,
    numero_digitos: int,
    data_vigencia_inicio: datetime.date,
    data_vigencia_fim: datetime.date,
    data_registro_inicio: datetime.datetime = datetime.datetime(2000, 1, 1, 0, 0, 0),
    data_registro_fim: datetime.datetime = SENTINEL,
) -> NivelHierarquico:
    return NivelHierarquico.objects.create(
        nivel_id=f"NIVEL-{nivel_ref}",
        nivel_ref=nivel_ref,
        classificacao_id=classificacao,
        nivel_numero=nivel_ref,
        nivel_nome=f"Nivel {nivel_ref}",
        numero_digitos=numero_digitos,
        data_vigencia_inicio=data_vigencia_inicio,
        data_vigencia_fim=data_vigencia_fim,
        data_registro_inicio=data_registro_inicio,
        data_registro_fim=data_registro_fim,
    )


class AdminDisplayMaskResolutionTests(TestCase):
    """Resolução de máscara em dois níveis para apresentação no admin.

    Cobre os contextos consumidores de ``format_receita_cod_for_admin_display``:
    a coluna ``receita_cod_formatado`` da changelist e o
    ``semantic_value_resolver`` do campo ``parent_item_id`` no formulário.
    Reproduz o cenário do split bitemporal de ``NivelHierarquico`` que motivou
    a criação do tier secundário (print histórico de 2026-05-19).
    """

    DIGITS = [1, 1, 1, 1, 2, 1, 1, 2, 3]  # soma = 13

    @classmethod
    def setUpTestData(cls):
        cls.serie = _make_serie()
        cls.classificacao = _make_classificacao(cls.serie)
        for nivel_ref, n_digitos in enumerate(cls.DIGITS, start=1):
            _make_nivel(
                cls.classificacao,
                nivel_ref=nivel_ref,
                numero_digitos=n_digitos,
                data_vigencia_inicio=datetime.date(2018, 1, 1),
                data_vigencia_fim=SENTINEL_DATE,
            )

    def test_tier1_estrito_sucede_para_janela_contida_em_unica_linha(self):
        cache = {}
        out = format_receita_cod_for_admin_display(
            "1100000000000",
            datetime.date(2026, 1, 1),
            SENTINEL_DATE,
            cache,
        )
        self.assertEqual(out, "1.1.0.0.00.0.0.00.000")

    def test_split_bitemporal_nivel3_aciona_tier2_para_janela_2026_01_01_a_sentinela(self):
        # Reproduz o cenário do print: NIVEL-3 é dividido em duas faixas
        # ativas. A janela [2026-01-01, 9999-12-31] não está contida em
        # nenhuma linha individual de NIVEL-3 → tier 1 falha.
        nivel3_original = NivelHierarquico.objects.get(
            nivel_ref=3, classificacao_id=self.classificacao
        )
        ts_split = datetime.datetime(2026, 5, 19, 12, 10, 7)
        NivelHierarquico.objects.filter(pk=nivel3_original.pk).update(
            data_registro_fim=ts_split,
        )
        _make_nivel(
            self.classificacao,
            nivel_ref=3,
            numero_digitos=1,
            data_vigencia_inicio=datetime.date(2018, 1, 1),
            data_vigencia_fim=datetime.date(2026, 1, 31),
            data_registro_inicio=ts_split,
        )
        _make_nivel(
            self.classificacao,
            nivel_ref=3,
            numero_digitos=1,
            data_vigencia_inicio=datetime.date(2026, 2, 1),
            data_vigencia_fim=SENTINEL_DATE,
            data_registro_inicio=ts_split,
        )

        # Tier 1 sozinho não consegue: confere com o helper antigo.
        cache_tier1 = {}
        out_tier1 = format_receita_cod_by_vigencia(
            "1100000000000",
            datetime.date(2026, 1, 1),
            SENTINEL_DATE,
            cache_tier1,
        )
        self.assertEqual(out_tier1, "1100000000000")

        # Tier 1 + tier 2 (admin display) resolve: NIVEL-3 v2
        # ([2026-02-01, sent]) contém data_vigencia_fim = sentinela do registro.
        cache_admin = {}
        out_admin = format_receita_cod_for_admin_display(
            "1100000000000",
            datetime.date(2026, 1, 1),
            SENTINEL_DATE,
            cache_admin,
        )
        self.assertEqual(out_admin, "1.1.0.0.00.0.0.00.000")

    def test_tier2_desempate_por_data_vigencia_fim_maior(self):
        # Cria, para NIVEL-3, duas linhas ativas elegíveis na Etapa S1, com
        # data_vigencia_fim distintos. Deve vencer a maior.
        nivel3_original = NivelHierarquico.objects.get(
            nivel_ref=3, classificacao_id=self.classificacao
        )
        NivelHierarquico.objects.filter(pk=nivel3_original.pk).update(
            data_registro_fim=datetime.datetime(2026, 5, 19, 12, 0, 0),
        )
        _make_nivel(
            self.classificacao,
            nivel_ref=3,
            numero_digitos=2,
            data_vigencia_inicio=datetime.date(2024, 1, 1),
            data_vigencia_fim=datetime.date(2030, 12, 31),
            data_registro_inicio=datetime.datetime(2026, 5, 19, 12, 0, 0),
        )
        _make_nivel(
            self.classificacao,
            nivel_ref=3,
            numero_digitos=1,
            data_vigencia_inicio=datetime.date(2024, 6, 1),
            data_vigencia_fim=SENTINEL_DATE,
            data_registro_inicio=datetime.datetime(2026, 5, 19, 12, 0, 0),
        )

        cache = {}
        record_vigencia_fim = datetime.date(2027, 6, 30)
        digit_mask = _resolve_secondary_digit_mask_for_admin_display(
            record_vigencia_fim, cache
        )
        # numero_digitos do NIVEL-3 escolhido deve ser 1 (vence quem tem
        # data_vigencia_fim maior, no caso a sentinela vs 2030-12-31).
        nivel3_index = 2  # nivel_ref = 3 → posição 2 em ordem
        self.assertEqual(digit_mask[nivel3_index], 1)

    def test_tier2_desempate_por_data_registro_inicio_mais_recente(self):
        nivel3_original = NivelHierarquico.objects.get(
            nivel_ref=3, classificacao_id=self.classificacao
        )
        NivelHierarquico.objects.filter(pk=nivel3_original.pk).update(
            data_registro_fim=datetime.datetime(2026, 5, 19, 12, 0, 0),
        )
        ts_antigo = datetime.datetime(2018, 1, 1, 0, 0, 0)
        ts_recente = datetime.datetime(2026, 5, 19, 12, 0, 0)
        _make_nivel(
            self.classificacao,
            nivel_ref=3,
            numero_digitos=2,
            data_vigencia_inicio=datetime.date(2017, 1, 1),
            data_vigencia_fim=SENTINEL_DATE,
            data_registro_inicio=ts_antigo,
        )
        _make_nivel(
            self.classificacao,
            nivel_ref=3,
            numero_digitos=1,
            data_vigencia_inicio=datetime.date(2018, 1, 1),
            data_vigencia_fim=SENTINEL_DATE,
            data_registro_inicio=ts_recente,
        )

        cache = {}
        digit_mask = _resolve_secondary_digit_mask_for_admin_display(
            SENTINEL_DATE, cache
        )
        nivel3_index = 2
        # data_vigencia_fim igual (sentinela) → desempate por
        # data_registro_inicio mais recente → numero_digitos = 1.
        self.assertEqual(digit_mask[nivel3_index], 1)

    def test_linhas_em_transacao_encerrada_nao_entram_em_nenhum_tier(self):
        # Encerra TODAS as linhas ativas de NIVEL-3 em transação. Nenhuma
        # candidata permanece elegível em nenhum dos dois tiers.
        ts = datetime.datetime(2026, 5, 19, 12, 0, 0)
        NivelHierarquico.objects.filter(
            nivel_ref=3, classificacao_id=self.classificacao
        ).update(data_registro_fim=ts)

        cache = {}
        out = format_receita_cod_for_admin_display(
            "1100000000000",
            datetime.date(2026, 1, 1),
            SENTINEL_DATE,
            cache,
        )
        # Sem NIVEL-3 ativo: soma da máscara não bate com 13 → bruto.
        self.assertEqual(out, "1100000000000")

    def test_codigo_vazio_devolve_string_vazia(self):
        cache = {}
        out = format_receita_cod_for_admin_display(
            "",
            datetime.date(2026, 1, 1),
            SENTINEL_DATE,
            cache,
        )
        self.assertEqual(out, "")
        # Não deve ter populado cache (nem invocado consulta).
        self.assertEqual(cache, {})
