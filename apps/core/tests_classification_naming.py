"""Testes do fluxo de nomenclatura (spec itemClassificacao_criar_nome)."""

from django.test import SimpleTestCase

from apps.core.classification_naming_abbrev import (
    calcular_radical_abreviado,
    norm,
    norm_colapso_espacos,
    radical_com_sufixo_canonico,
)
from apps.core.classification_naming_connectives import (
    LEXICO_CONNECTIVOS_FIXOS,
    NOME_CLASSIFICACAO_CONNECTIVOS_FIXOS,
    compactar_texto_radical_a6,
    normalizar_token_pontuacao_a6,
    token_e_abreviacao_encurtamento_iv,
)
from apps.core.alias_lexico_infer import _CONNECTIVES
from apps.core.classification_naming_messages import (
    RECEITA_NOME_SUGESTAO_INFO_ABREV_TEMPLATE,
    RECEITA_NOME_SUGESTAO_INFO_COMPLETO,
    RECEITA_NOME_VAZIO_ERROR,
    format_receita_nome_sugestao_info_abrev,
)
from apps.core.classification_naming_validation import (
    radical_efetivo_para_guardrail,
    receita_nome_eh_sugestao_incompleta,
    receita_nome_vazio_no_add,
    validar_receita_nome_guardrail_g0,
    validar_receita_nome_guardrail_g1,
)


class G2MessagesTests(SimpleTestCase):
    def test_g2_1_menciona_versao_completa(self) -> None:
        self.assertIn("versão completa", RECEITA_NOME_SUGESTAO_INFO_COMPLETO)
        self.assertIn("após o traço", RECEITA_NOME_SUGESTAO_INFO_COMPLETO)

    def test_g2_2_template_menciona_versao_abreviada(self) -> None:
        self.assertIn("versão abreviada", RECEITA_NOME_SUGESTAO_INFO_ABREV_TEMPLATE)

    def test_g2_2_inclui_nome_mae(self) -> None:
        msg = format_receita_nome_sugestao_info_abrev("Impostos sobre o Patrimônio")
        self.assertIn("versão abreviada", msg)
        self.assertIn('O nome do item mãe é "Impostos sobre o Patrimônio"', msg)

    def test_g2_2_escapa_aspas_internas(self) -> None:
        msg = format_receita_nome_sugestao_info_abrev('Imposto "X"')
        self.assertIn('Imposto \\"X\\"', msg)


class G0ValidationTests(SimpleTestCase):
    def test_vazio_string_vazia(self) -> None:
        self.assertTrue(receita_nome_vazio_no_add(""))
        self.assertTrue(validar_receita_nome_guardrail_g0(receita_nome=""))

    def test_vazio_so_espacos(self) -> None:
        self.assertTrue(receita_nome_vazio_no_add("   \t  "))

    def test_nao_vazio_com_texto(self) -> None:
        self.assertFalse(receita_nome_vazio_no_add("IPVA - Principal"))
        self.assertFalse(validar_receita_nome_guardrail_g0(receita_nome="ITCD - "))

    def test_g0_independe_do_modo_g1_ainda_bloqueia_incompleto(self) -> None:
        self.assertFalse(validar_receita_nome_guardrail_g0(receita_nome="ITCD - "))
        self.assertTrue(
            validar_receita_nome_guardrail_g1(
                receita_nome="ITCD - ",
                receita_nome_base_mode="base_pai_abrev",
                nome_mae="Nome longo ITCD",
                radical_abreviado="ITCD",
            )
        )

    def test_mensagem_g0(self) -> None:
        self.assertIn("Natureza de Receita", RECEITA_NOME_VAZIO_ERROR)


class NormTests(SimpleTestCase):
    def test_norm_nao_colapsa_espacos(self) -> None:
        self.assertEqual(norm("Imposto  sobre"), "imposto  sobre")
        self.assertNotEqual(norm("Imposto  sobre"), norm("Imposto sobre"))

    def test_norm_colapso(self) -> None:
        self.assertEqual(norm_colapso_espacos("Imposto  sobre"), "imposto sobre")


class G1ValidationTests(SimpleTestCase):
    def test_bloqueia_radical_igual(self) -> None:
        self.assertTrue(receita_nome_eh_sugestao_incompleta("IPVA", "IPVA"))

    def test_bloqueia_radical_com_traco_ascii(self) -> None:
        self.assertTrue(receita_nome_eh_sugestao_incompleta("IPVA - ", "IPVA"))

    def test_bloqueia_radical_com_en_dash(self) -> None:
        self.assertTrue(receita_nome_eh_sugestao_incompleta("IPVA\u2013", "IPVA"))

    def test_permite_com_complemento(self) -> None:
        self.assertFalse(receita_nome_eh_sugestao_incompleta("IPVA - Principal", "IPVA"))

    def test_sem_base_nao_avalia(self) -> None:
        self.assertIsNone(radical_efetivo_para_guardrail("sem_base", "IPVA", "IPVA"))

    def test_modo_abrev_usa_radical_abreviado(self) -> None:
        b = radical_efetivo_para_guardrail(
            "base_pai_abrev", "Nome Longo da Mãe", radical_abreviado="IPVA"
        )
        self.assertEqual(b, "IPVA")

    def test_validar_g1_abreviado(self) -> None:
        self.assertTrue(
            validar_receita_nome_guardrail_g1(
                receita_nome="Rest. IPVA - ",
                receita_nome_base_mode="base_pai_abrev",
                nome_mae="Nome longo",
                radical_abreviado="Rest. IPVA",
            )
        )


class AbbrevProtocolTests(SimpleTestCase):
    def test_connectivos_ssot_unica_entre_infer_e_nomenclatura(self) -> None:
        self.assertEqual(_CONNECTIVES, LEXICO_CONNECTIVOS_FIXOS)
        self.assertEqual(NOME_CLASSIFICACAO_CONNECTIVOS_FIXOS, LEXICO_CONNECTIVOS_FIXOS)
        self.assertIn("sobre", LEXICO_CONNECTIVOS_FIXOS)

    def test_a8_sem_lexico_remove_conectivos(self) -> None:
        from unittest.mock import patch

        with patch(
            "apps.core.classification_naming_abbrev.iter_alias_lexico_ativos_ordenados",
            return_value=[],
        ):
            r = calcular_radical_abreviado("Taxa Única")
        self.assertEqual(r.radical, "Taxa Única")

    def test_a8_iptu_sem_lexico_remove_conectivos(self) -> None:
        from unittest.mock import patch

        nome = "Imposto sobre a Propriedade Predial e Territorial Urbana"
        with patch(
            "apps.core.classification_naming_abbrev.iter_alias_lexico_ativos_ordenados",
            return_value=[],
        ):
            r = calcular_radical_abreviado(nome)
        self.assertEqual(
            r.radical,
            "Imposto Propriedade Predial Territorial Urbana",
        )

    def test_a3_match_exato_passa_por_a6(self) -> None:
        from unittest.mock import patch

        nome_mae = "Imposto sobre a Propriedade de Veículos Automotores"
        with patch(
            "apps.core.classification_naming_abbrev.iter_alias_lexico_ativos_ordenados",
            return_value=[(nome_mae, "Imposto sobre o IPVA")],
        ):
            r = calcular_radical_abreviado(nome_mae)
        self.assertEqual(r.radical, "Imposto IPVA")

    def test_a6_remove_virgula_e_preserva_iv(self) -> None:
        self.assertTrue(token_e_abreviacao_encurtamento_iv("Princ."))
        self.assertEqual(normalizar_token_pontuacao_a6("Princ."), "Princ.")
        self.assertEqual(normalizar_token_pontuacao_a6("Imposto,"), "Imposto")
        self.assertEqual(
            compactar_texto_radical_a6("Tx. Insp., Princ."),
            "Tx. Insp. Princ.",
        )

    def test_a6_remove_pontuacao_solta(self) -> None:
        self.assertEqual(compactar_texto_radical_a6("! ; :"), "")
        self.assertEqual(compactar_texto_radical_a6("Taxa!"), "Taxa")

    def test_a6_remove_ponto_final_fora_iv(self) -> None:
        self.assertEqual(normalizar_token_pontuacao_a6("Automotores."), "Automotores")
        self.assertEqual(normalizar_token_pontuacao_a6("Receita."), "Receita.")

    def test_a6_via_calcular_radical_com_pontuacao(self) -> None:
        from unittest.mock import patch

        with patch(
            "apps.core.classification_naming_abbrev.iter_alias_lexico_ativos_ordenados",
            return_value=[],
        ):
            r = calcular_radical_abreviado("Imposto, sobre a Propriedade!")
        self.assertEqual(r.radical, "Imposto Propriedade")

    def test_sufixo_canonico(self) -> None:
        self.assertEqual(radical_com_sufixo_canonico("IPVA"), "IPVA - ")
