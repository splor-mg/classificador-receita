"""Testes de navegação estrutural (spec navegacao)."""

from datetime import date

from django.test import TestCase

from apps.core.classification_item_structural_navigation import (
    DIRECTIONS,
    _NavContext,
    _effective_nv_target,
    _normalize_code_for_mask,
    _resolve_next_code,
    _resolve_next_level,
    _resolve_prev_code,
    _resolve_prev_level,
    _segment_code,
)
from apps.core.code_parent_item_validation import derive_nivel_numero_from_receita_cod_digits

# Máscara da base fictícia da spec (9 níveis).
MASK_FICT = [1, 1, 1, 1, 2, 1, 1, 2, 3]


def _dotted_to_digits(value: str) -> str:
    return value.replace(".", "")


FICTITIOUS_CODES = [
    _dotted_to_digits(x)
    for x in [
        "1.0.0.0.00.0.0.00.000",
        "1.1.0.0.00.0.0.00.000",
        "1.1.1.0.00.0.0.00.000",
        "1.1.1.1.00.0.0.00.000",
        "1.1.1.1.01.0.0.00.000",
        "1.1.1.1.02.0.0.00.000",
        "1.1.1.2.00.0.0.00.000",
        "1.1.1.2.00.0.0.00.001",
        "1.1.1.2.00.0.0.00.002",
        "1.1.1.2.00.0.0.00.003",
        "1.1.1.2.52.0.0.00.000",
        "1.1.1.2.52.0.1.00.000",
        "1.1.1.2.52.0.1.01.000",
        "1.1.1.2.52.0.1.02.000",
        "1.1.1.2.52.0.2.00.000",
        "1.1.1.2.52.0.2.01.000",
        "1.1.1.2.52.0.2.02.000",
        "1.1.1.2.52.0.3.00.000",
        "1.1.1.2.52.0.3.01.000",
        "1.1.1.2.52.0.3.02.000",
        "1.1.1.2.52.0.4.00.000",
        "1.1.1.2.52.0.4.01.000",
        "1.1.1.2.52.0.4.02.000",
        "1.1.1.2.53.0.0.00.000",
        "1.1.1.3.00.0.0.00.000",
        "1.1.1.3.00.0.0.03.000",
        "1.1.1.3.00.0.0.03.001",
        "1.1.1.4.00.0.0.00.000",
        "1.1.1.5.00.0.0.00.000",
    ]
    ]


IRPJ_IPI_EXTRA_CODES = [
    _dotted_to_digits(x)
    for x in [
        "1.1.1.3.02.0.0.00.000",
        "1.1.1.3.03.0.0.00.000",
        "1.1.1.3.03.1.0.00.000",
        "1.1.1.3.03.2.0.00.000",
        "1.1.1.3.03.3.0.00.000",
        "1.1.1.3.03.4.0.00.000",
        "1.1.1.4.01.0.0.00.000",
        "1.1.1.4.01.1.0.00.000",
        "1.1.1.4.01.2.0.00.000",
        "1.1.1.4.01.3.0.00.000",
        "1.1.1.4.01.4.0.00.000",
        "1.1.1.4.01.5.0.00.000",
        "1.1.1.4.50.0.0.00.000",
        "1.1.2.0.00.0.0.00.000",
        "1.2.0.0.00.0.0.00.000",
        "2.0.0.0.00.0.0.00.000",
    ]
]


def _make_ctx(cod_dotted: str, *, extra_codes=None) -> _NavContext:
    cod = _normalize_code_for_mask(_dotted_to_digits(cod_dotted), MASK_FICT)
    assert cod is not None
    nv, err = derive_nivel_numero_from_receita_cod_digits(cod, MASK_FICT)
    assert err is None and nv
    codes = set(FICTITIOUS_CODES)
    if extra_codes:
        codes.update(extra_codes)
    return _NavContext(
        cod_edit=cod,
        segments=_segment_code(cod, MASK_FICT),
        mask=MASK_FICT,
        nv_edit=nv,
        v1_inicio=date(2020, 1, 1),
        v1_fim=date(9999, 12, 31),
        origin_pk=1,
        origin_classificacao_semantic="",
        origin_classificacao_nome="",
        codes=codes,
    )


def _nv_target_for(ctx: _NavContext) -> int:
    return _effective_nv_target(ctx, None)


class StructuralNavigationLogicTests(TestCase):
    def test_next_code_ex_1_1(self):
        ctx = _make_ctx("1.1.1.2.00.0.0.00.000")
        self.assertEqual(_resolve_next_code(ctx), _dotted_to_digits("1.1.1.2.00.0.0.00.001"))

    def test_next_code_ex_1_2(self):
        ctx = _make_ctx("1.1.1.3.00.0.0.00.000")
        found = _resolve_next_code(ctx)
        self.assertEqual(found, _dotted_to_digits("1.1.1.3.00.0.0.03.000"))
        self.assertNotEqual(found, _dotted_to_digits("1.1.1.3.00.0.0.03.001"))

    def test_next_code_ex_2_1(self):
        ctx = _make_ctx("1.1.1.4.00.0.0.00.000")
        self.assertEqual(_resolve_next_code(ctx), _dotted_to_digits("1.1.1.5.00.0.0.00.000"))

    def test_next_code_ex_3_1(self):
        ctx = _make_ctx("1.1.1.2.52.0.4.02.000")
        self.assertEqual(_resolve_next_code(ctx), _dotted_to_digits("1.1.1.2.53.0.0.00.000"))

    def test_next_level_ex_1_1(self):
        ctx = _make_ctx("1.1.1.2.52.0.0.00.000")
        nv = _nv_target_for(ctx)
        self.assertEqual(_resolve_next_level(ctx, nv_target=nv), _dotted_to_digits("1.1.1.2.53.0.0.00.000"))

    def test_next_level_ex_1_2(self):
        ctx = _make_ctx("1.1.1.1.00.0.0.00.000")
        nv = _nv_target_for(ctx)
        self.assertEqual(_resolve_next_level(ctx, nv_target=nv), _dotted_to_digits("1.1.1.2.00.0.0.00.000"))

    def test_prev_code_ex_1_1(self):
        ctx = _make_ctx("1.1.1.2.00.0.0.00.003")
        self.assertEqual(_resolve_prev_code(ctx), _dotted_to_digits("1.1.1.2.00.0.0.00.002"))

    def test_prev_code_ex_1_2(self):
        ctx = _make_ctx("1.1.1.2.52.0.2.00.000")
        self.assertEqual(_resolve_prev_code(ctx), _dotted_to_digits("1.1.1.2.52.0.1.02.000"))

    def test_prev_code_ex_2_1(self):
        ctx = _make_ctx("1.1.1.5.00.0.0.00.000")
        self.assertEqual(_resolve_prev_code(ctx), _dotted_to_digits("1.1.1.4.00.0.0.00.000"))

    def test_prev_code_ex_2_2(self):
        ctx = _make_ctx("1.1.1.2.53.0.0.00.000")
        self.assertEqual(_resolve_prev_code(ctx), _dotted_to_digits("1.1.1.2.52.0.4.02.000"))

    def test_prev_level_ex_1_1(self):
        ctx = _make_ctx("1.1.1.2.53.0.0.00.000")
        nv = _nv_target_for(ctx)
        self.assertEqual(_resolve_prev_level(ctx, nv_target=nv), _dotted_to_digits("1.1.1.2.52.0.0.00.000"))

    def test_prev_level_ex_1_2(self):
        ctx = _make_ctx("1.1.1.2.00.0.0.00.000")
        nv = _nv_target_for(ctx)
        self.assertEqual(_resolve_prev_level(ctx, nv_target=nv), _dotted_to_digits("1.1.1.1.00.0.0.00.000"))

    def test_directions_constant(self):
        self.assertEqual(
            DIRECTIONS,
            frozenset({"next_code", "next_level", "prev_code", "prev_level"}),
        )


class StructuralNavigationNvTargetTests(TestCase):
    NV_TARGET = 6

    def _irpj_ctx(self, cod_dotted: str) -> _NavContext:
        return _make_ctx(
            cod_dotted,
            extra_codes=IRPJ_IPI_EXTRA_CODES + FICTITIOUS_CODES,
        )

    def test_next_level_l2_branch_change(self):
        ctx = self._irpj_ctx("1.1.1.3.03.4.0.00.000")
        self.assertEqual(
            _resolve_next_level(ctx, nv_target=self.NV_TARGET),
            _dotted_to_digits("1.1.1.4.00.0.0.00.000"),
        )

    def test_next_level_l3_descent_after_l2(self):
        ctx = self._irpj_ctx("1.1.1.4.00.0.0.00.000")
        self.assertEqual(
            _resolve_next_level(ctx, nv_target=self.NV_TARGET),
            _dotted_to_digits("1.1.1.4.01.0.0.00.000"),
        )

    def test_next_level_l3_second_descent_step(self):
        ctx = self._irpj_ctx("1.1.1.4.01.0.0.00.000")
        self.assertEqual(
            _resolve_next_level(ctx, nv_target=self.NV_TARGET),
            _dotted_to_digits("1.1.1.4.01.1.0.00.000"),
        )

    def test_next_level_l2_intermediate_450_before_500(self):
        ctx = self._irpj_ctx("1.1.1.4.01.5.0.00.000")
        self.assertEqual(
            _resolve_next_level(ctx, nv_target=self.NV_TARGET),
            _dotted_to_digits("1.1.1.4.50.0.0.00.000"),
        )

    def test_irpj_ipi_next_level_sequence(self):
        sequence = [
            "1.1.1.3.03.1.0.00.000",
            "1.1.1.3.03.2.0.00.000",
            "1.1.1.3.03.3.0.00.000",
            "1.1.1.3.03.4.0.00.000",
            "1.1.1.4.00.0.0.00.000",
            "1.1.1.4.01.0.0.00.000",
            "1.1.1.4.01.1.0.00.000",
            "1.1.1.4.01.2.0.00.000",
            "1.1.1.4.01.3.0.00.000",
            "1.1.1.4.01.4.0.00.000",
            "1.1.1.4.01.5.0.00.000",
            "1.1.1.4.50.0.0.00.000",
            "1.1.1.5.00.0.0.00.000",
            "1.1.2.0.00.0.0.00.000",
            "1.2.0.0.00.0.0.00.000",
            "2.0.0.0.00.0.0.00.000",
        ]
        for index in range(len(sequence) - 1):
            ctx = self._irpj_ctx(sequence[index])
            found = _resolve_next_level(ctx, nv_target=self.NV_TARGET)
            self.assertEqual(
                found,
                _dotted_to_digits(sequence[index + 1]),
                msg=f"passo {index + 1}: {sequence[index]} → {sequence[index + 1]}",
            )
