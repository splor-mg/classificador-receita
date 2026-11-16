"""Agregação do nível hierárquico e a recusa no Salvar do item.

#85 registra o campo, com padrão Híbrido.
#86 recusa, no caminho do Salvar, Detalhe num nível Matriz e Matriz num nível Detalhe.
"""

from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.forms.utils import ErrorDict
from django.test import SimpleTestCase

from apps.core.admin import NivelHierarquicoAdmin
from apps.core.forms import ItemClassificacaoForm, PlaceholderNullNormalizationFormMixin
from apps.core.models import ItemClassificacao, NivelHierarquico


class NivelAgregacaoFieldTests(SimpleTestCase):
    def test_new_level_defaults_to_hibrido(self):
        field = NivelHierarquico._meta.get_field("agregacao")
        self.assertEqual(field.default, NivelHierarquico.AGREGACAO_HIBRIDO)
        self.assertEqual(field.verbose_name, "Agregação")
        self.assertEqual(
            [label for _value, label in field.choices],
            ["Híbrido", "Matriz", "Detalhe"],
        )
        self.assertEqual(NivelHierarquico().agregacao, NivelHierarquico.AGREGACAO_HIBRIDO)

    def test_admin_form_shows_agregacao(self):
        self.assertIn("agregacao", NivelHierarquicoAdmin.fields)


class ItemAgregacaoSaveTests(SimpleTestCase):
    def _item(self, *, agregacao: str, matriz: bool, nivel_numero: int = 7) -> ItemClassificacao:
        item = ItemClassificacao(matriz=matriz)
        item.nivel_id = NivelHierarquico(
            nivel_id="NIVEL-TEST",
            nivel_numero=nivel_numero,
            agregacao=agregacao,
        )
        return item

    def _clean_item(self, item: ItemClassificacao) -> None:
        with patch("apps.core.models.apply_temporal_fk_resolution"):
            item.clean()

    def test_save_rejects_detalhe_when_level_is_matriz(self):
        item = self._item(agregacao=NivelHierarquico.AGREGACAO_MATRIZ, matriz=False)
        with self.assertRaises(ValidationError) as caught:
            self._clean_item(item)
        self.assertIn("matriz", caught.exception.message_dict)
        self.assertIsNone(item.pk)

    def test_save_rejects_matriz_when_level_is_detalhe(self):
        item = self._item(agregacao=NivelHierarquico.AGREGACAO_DETALHE, matriz=True)
        with self.assertRaises(ValidationError) as caught:
            self._clean_item(item)
        self.assertIn("matriz", caught.exception.message_dict)
        self.assertIsNone(item.pk)

    def test_save_accepts_matriz_and_detalhe_when_level_is_hibrido(self):
        for matriz in (True, False):
            item = self._item(
                agregacao=NivelHierarquico.AGREGACAO_HIBRIDO,
                matriz=matriz,
                nivel_numero=1,
            )
            self._clean_item(item)
            self.assertIsNone(item.pk)

    def _clean_form(self, *, agregacao: str, matriz: bool, nivel_numero: int = 7):
        nivel = NivelHierarquico(
            nivel_id="NIVEL-TEST",
            nivel_numero=nivel_numero,
            agregacao=agregacao,
        )
        form = ItemClassificacaoForm(data={"matriz": "matriz" if matriz else "detalhe"})
        form._errors = ErrorDict()
        cleaned = {
            "nivel_id": nivel,
            "matriz": matriz,
            "receita_cod": "",
            "receita_nome": "Nome de teste",
            "receita_nome_base_mode": "sem_base",
            "data_vigencia_inicio": None,
            "data_vigencia_fim": None,
            "classificacao_id": None,
            "parent_item_id": None,
        }
        form.cleaned_data = cleaned

        def _keep_assigned(_instance, field_name):
            return getattr(_instance, field_name)

        with (
            patch.object(PlaceholderNullNormalizationFormMixin, "clean", return_value=cleaned),
            patch("apps.core.forms.resolve_active_compatible_fk", side_effect=_keep_assigned),
            patch.object(
                ItemClassificacaoForm, "_get_receita_cod_digit_rule", return_value=(13, "TEST")
            ),
            patch("apps.core.forms.validar_receita_nome_guardrail_g0", return_value=False),
            patch("apps.core.forms.validar_receita_nome_guardrail_g1", return_value=(False, None)),
        ):
            form.clean()
        return form

    def test_form_save_rejects_detalhe_on_matriz_level(self):
        form = self._clean_form(agregacao=NivelHierarquico.AGREGACAO_MATRIZ, matriz=False)
        self.assertIn("matriz", form.errors)

    def test_form_save_rejects_matriz_on_detalhe_level(self):
        form = self._clean_form(agregacao=NivelHierarquico.AGREGACAO_DETALHE, matriz=True)
        self.assertIn("matriz", form.errors)

    def test_form_save_accepts_either_on_hibrido_level(self):
        for matriz in (True, False):
            form = self._clean_form(
                agregacao=NivelHierarquico.AGREGACAO_HIBRIDO,
                matriz=matriz,
            )
            self.assertTrue(form._errors is None or "matriz" not in form._errors)
