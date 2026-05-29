"""Testes do fluxo de nomenclatura (spec itemClassificacao_criar_nome)."""

from django.test import SimpleTestCase

from apps.core.code_name_abbrev import (
    calcular_radical_abreviado,
    norm,
    norm_colapso_espacos,
    radical_com_sufixo_canonico,
)
from apps.core.code_name_connectives import (
    LEXICO_CONNECTIVOS_FIXOS,
    NOME_CLASSIFICACAO_CONNECTIVOS_FIXOS,
    compactar_texto_radical_a6,
    normalizar_token_pontuacao_a6,
    token_e_abreviacao_encurtamento_iv,
)
from apps.core.alias_lexico_infer import _CONNECTIVES
from apps.core.code_name_messages import (
    MENSAGEM_SUGESTAO_LITERAL_KEY,
    MENSAGEM_TRACO_FINAL_KEY,
    RECEITA_NOME_SUBMIT_SUGESTAO_LITERAL_ERROR,
    RECEITA_NOME_SUBMIT_TRACO_FINAL_ERROR,
    RECEITA_NOME_SUGESTAO_INFO_ABREV_TEMPLATE,
    RECEITA_NOME_SUGESTAO_INFO_COMPLETO,
    RECEITA_NOME_VAZIO_ERROR,
    code_name_messages_dict,
    format_receita_nome_sugestao_info_abrev,
)
from apps.core.code_name_validation import (
    radical_efetivo_para_guardrail,
    receita_nome_eh_sugestao_literal,
    receita_nome_termina_com_traco,
    receita_nome_vazio_no_add,
    validar_receita_nome_guardrail_g0,
    validar_receita_nome_guardrail_g1,
)


class G2MessagesTests(SimpleTestCase):
    def test_g2_1_menciona_versao_completa(self) -> None:
        self.assertIn("versão completa", RECEITA_NOME_SUGESTAO_INFO_COMPLETO)
        self.assertIn("após o traço", RECEITA_NOME_SUGESTAO_INFO_COMPLETO)

    def test_g2_1_menciona_remover_traco(self) -> None:
        self.assertIn("remova o traço final", RECEITA_NOME_SUGESTAO_INFO_COMPLETO)

    def test_g2_2_template_menciona_versao_abreviada(self) -> None:
        self.assertIn("versão abreviada", RECEITA_NOME_SUGESTAO_INFO_ABREV_TEMPLATE)

    def test_g2_2_template_menciona_remover_traco(self) -> None:
        self.assertIn("remova o traço final", RECEITA_NOME_SUGESTAO_INFO_ABREV_TEMPLATE)

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
        # **G0 vs G1**: ITCD - (termina com traço) → G0 não bloqueia, G1 bloqueia.
        self.assertFalse(validar_receita_nome_guardrail_g0(receita_nome="ITCD - "))
        bloquear, chave = validar_receita_nome_guardrail_g1(
            receita_nome="ITCD - ",
            nome_mae="Nome longo ITCD",
            radical_abreviado="ITCD",
        )
        self.assertTrue(bloquear)
        self.assertEqual(chave, MENSAGEM_SUGESTAO_LITERAL_KEY)

    def test_g0_vs_g1_sem_traco_libera_em_ambos(self) -> None:
        # **G0 vs G1**: ITCD (sem traço final) → G0 e G1 não bloqueiam.
        self.assertFalse(validar_receita_nome_guardrail_g0(receita_nome="ITCD"))
        bloquear, chave = validar_receita_nome_guardrail_g1(
            receita_nome="ITCD",
            nome_mae="Nome longo ITCD",
            radical_abreviado="ITCD",
        )
        self.assertFalse(bloquear)
        self.assertIsNone(chave)

    def test_mensagem_g0(self) -> None:
        self.assertIn("Natureza de Receita", RECEITA_NOME_VAZIO_ERROR)


class NormTests(SimpleTestCase):
    def test_norm_nao_colapsa_espacos(self) -> None:
        self.assertEqual(norm("Imposto  sobre"), "imposto  sobre")
        self.assertNotEqual(norm("Imposto  sobre"), norm("Imposto sobre"))

    def test_norm_colapso(self) -> None:
        self.assertEqual(norm_colapso_espacos("Imposto  sobre"), "imposto sobre")


class G1PredicadoBloqueioTests(SimpleTestCase):
    """``receita_nome_termina_com_traco`` (G1.2) — predicado único, sem ``b``."""

    def test_bloqueia_traco_final_ascii_com_espaco(self) -> None:
        self.assertTrue(receita_nome_termina_com_traco("IPVA - "))

    def test_bloqueia_traco_final_ascii_sem_espaco(self) -> None:
        self.assertTrue(receita_nome_termina_com_traco("IPVA -"))

    def test_bloqueia_en_dash_final(self) -> None:
        self.assertTrue(receita_nome_termina_com_traco("IPVA\u2013"))

    def test_bloqueia_em_dash_final(self) -> None:
        self.assertTrue(receita_nome_termina_com_traco("IPVA\u2014"))

    def test_bloqueia_complemento_seguido_de_traco(self) -> None:
        self.assertTrue(receita_nome_termina_com_traco("IPVA - Cota Única -"))
        self.assertTrue(receita_nome_termina_com_traco("Rec. Imposto - Carro - "))

    def test_libera_sem_traco_final(self) -> None:
        self.assertFalse(receita_nome_termina_com_traco("IPVA"))
        self.assertFalse(receita_nome_termina_com_traco("IPVA - Principal"))
        self.assertFalse(receita_nome_termina_com_traco("Rec. Imposto - Carro"))

    def test_libera_vazio(self) -> None:
        self.assertFalse(receita_nome_termina_com_traco(""))
        self.assertFalse(receita_nome_termina_com_traco("   "))

    def test_libera_radical_igual_sem_traco_regressao(self) -> None:
        """**Regressão proposital**: ``n === b`` deixa de ser bloqueio."""
        self.assertFalse(
            receita_nome_termina_com_traco(
                "Imposto sobre a Propriedade Predial e Territorial Urbana"
            )
        )


class G1SugestaoLiteralTests(SimpleTestCase):
    """``receita_nome_eh_sugestao_literal`` — usado só para selecionar G1.5.a."""

    def test_casa_com_b_mais_traco_ascii(self) -> None:
        self.assertTrue(receita_nome_eh_sugestao_literal("IPVA - ", "IPVA"))
        self.assertTrue(receita_nome_eh_sugestao_literal("IPVA -", "IPVA"))

    def test_casa_com_b_mais_en_dash(self) -> None:
        self.assertTrue(receita_nome_eh_sugestao_literal("IPVA\u2013", "IPVA"))

    def test_nao_casa_quando_igual_a_b_sem_traco(self) -> None:
        self.assertFalse(receita_nome_eh_sugestao_literal("IPVA", "IPVA"))

    def test_nao_casa_com_complemento(self) -> None:
        self.assertFalse(receita_nome_eh_sugestao_literal("IPVA - Principal", "IPVA"))

    def test_nao_casa_quando_b_vazio(self) -> None:
        self.assertFalse(receita_nome_eh_sugestao_literal("IPVA -", ""))
        self.assertFalse(receita_nome_eh_sugestao_literal("", "IPVA"))


class G1ValidacaoTuplaTests(SimpleTestCase):
    """``validar_receita_nome_guardrail_g1`` retorna ``(bloquear, chave_mensagem)``."""

    def test_libera_quando_nao_termina_com_traco(self) -> None:
        bloquear, chave = validar_receita_nome_guardrail_g1(
            receita_nome="IPVA - Principal",
            nome_mae="IPVA",
            radical_abreviado="IPVA",
        )
        self.assertFalse(bloquear)
        self.assertIsNone(chave)

    def test_bloqueia_sugestao_literal_completo(self) -> None:
        # `n = b_completo + " - "` → G1.5.a.
        bloquear, chave = validar_receita_nome_guardrail_g1(
            receita_nome="Imposto sobre a Propriedade Predial e Territorial Urbana - ",
            nome_mae="Imposto sobre a Propriedade Predial e Territorial Urbana",
            radical_abreviado="IPTU",
        )
        self.assertTrue(bloquear)
        self.assertEqual(chave, MENSAGEM_SUGESTAO_LITERAL_KEY)

    def test_bloqueia_sugestao_literal_abreviado(self) -> None:
        # `n = b_abreviado + " - "` → G1.5.a (mesmo se o modo selecionado fosse Completo).
        bloquear, chave = validar_receita_nome_guardrail_g1(
            receita_nome="IPTU - ",
            nome_mae="Imposto sobre a Propriedade Predial e Territorial Urbana",
            radical_abreviado="IPTU",
        )
        self.assertTrue(bloquear)
        self.assertEqual(chave, MENSAGEM_SUGESTAO_LITERAL_KEY)

    def test_bloqueia_sugestao_literal_sem_espaco_final(self) -> None:
        # `n = b + " -"` → ainda casa como sugestão literal (G1.5.a).
        bloquear, chave = validar_receita_nome_guardrail_g1(
            receita_nome="IPTU -",
            nome_mae="IPTU",
            radical_abreviado="IPTU",
        )
        self.assertTrue(bloquear)
        self.assertEqual(chave, MENSAGEM_SUGESTAO_LITERAL_KEY)

    def test_bloqueia_traco_pendurado_com_complemento_g1_5_b(self) -> None:
        bloquear, chave = validar_receita_nome_guardrail_g1(
            receita_nome="IPVA - Cota Única -",
            nome_mae="IPVA",
            radical_abreviado="IPVA",
        )
        self.assertTrue(bloquear)
        self.assertEqual(chave, MENSAGEM_TRACO_FINAL_KEY)

    def test_bloqueia_sem_base_traco_final_g1_5_b(self) -> None:
        # `sem_base`: nome_mae vazio, radical_abreviado None → seleciona G1.5.b.
        bloquear, chave = validar_receita_nome_guardrail_g1(
            receita_nome="Taxa municipal -",
            nome_mae="",
            radical_abreviado=None,
        )
        self.assertTrue(bloquear)
        self.assertEqual(chave, MENSAGEM_TRACO_FINAL_KEY)

    def test_libera_sem_base_sem_traco(self) -> None:
        bloquear, chave = validar_receita_nome_guardrail_g1(
            receita_nome="Taxa municipal de iluminação",
            nome_mae="",
            radical_abreviado=None,
        )
        self.assertFalse(bloquear)
        self.assertIsNone(chave)

    def test_libera_radical_igual_sem_traco_regressao(self) -> None:
        # Antigo bloqueio `n === b` agora é liberado.
        bloquear, chave = validar_receita_nome_guardrail_g1(
            receita_nome="IPVA",
            nome_mae="IPVA",
            radical_abreviado="IPVA",
        )
        self.assertFalse(bloquear)
        self.assertIsNone(chave)


class G1MensagensDictTests(SimpleTestCase):
    """Chaves expostas no ``code_name_messages_dict``."""

    def test_chaves_presentes(self) -> None:
        d = code_name_messages_dict()
        self.assertEqual(
            d[MENSAGEM_SUGESTAO_LITERAL_KEY],
            RECEITA_NOME_SUBMIT_SUGESTAO_LITERAL_ERROR,
        )
        self.assertEqual(
            d[MENSAGEM_TRACO_FINAL_KEY],
            RECEITA_NOME_SUBMIT_TRACO_FINAL_ERROR,
        )

    def test_g1_5_a_menciona_radical_sugerido(self) -> None:
        self.assertIn("após o traço", RECEITA_NOME_SUBMIT_SUGESTAO_LITERAL_ERROR)
        self.assertIn("remova o traço final", RECEITA_NOME_SUBMIT_SUGESTAO_LITERAL_ERROR)
        self.assertIn(
            "radical sugerido", RECEITA_NOME_SUBMIT_SUGESTAO_LITERAL_ERROR
        )

    def test_g1_5_b_menciona_inconsistencia_de_traco(self) -> None:
        self.assertIn("não pode terminar com traço", RECEITA_NOME_SUBMIT_TRACO_FINAL_ERROR)


class RadicalEfetivoTests(SimpleTestCase):
    def test_sem_base_retorna_none(self) -> None:
        self.assertIsNone(radical_efetivo_para_guardrail("sem_base", "IPVA", "IPVA"))

    def test_modo_abrev_usa_radical_abreviado(self) -> None:
        b = radical_efetivo_para_guardrail(
            "base_pai_abrev", "Nome Longo da Mãe", radical_abreviado="IPVA"
        )
        self.assertEqual(b, "IPVA")

    def test_modo_completo_usa_nome_mae(self) -> None:
        b = radical_efetivo_para_guardrail("base_pai_completo", "IPVA", "IPVA")
        self.assertEqual(b, "IPVA")

    def test_base_pai_legado_aceito(self) -> None:
        # `base_pai` (legado) é normalizado para `base_pai_completo`.
        b = radical_efetivo_para_guardrail("base_pai", "IPVA", "IPVA")
        self.assertEqual(b, "IPVA")


class AbbrevProtocolTests(SimpleTestCase):
    def test_connectivos_ssot_unica_entre_infer_e_nomenclatura(self) -> None:
        self.assertEqual(_CONNECTIVES, LEXICO_CONNECTIVOS_FIXOS)
        self.assertEqual(NOME_CLASSIFICACAO_CONNECTIVOS_FIXOS, LEXICO_CONNECTIVOS_FIXOS)
        self.assertIn("sobre", LEXICO_CONNECTIVOS_FIXOS)

    def test_a8_sem_lexico_remove_conectivos(self) -> None:
        from unittest.mock import patch

        with patch(
            "apps.core.code_name_abbrev.iter_alias_lexico_ativos_ordenados",
            return_value=[],
        ):
            r = calcular_radical_abreviado("Taxa Única")
        self.assertEqual(r.radical, "Taxa Única")

    def test_a8_iptu_sem_lexico_remove_conectivos(self) -> None:
        from unittest.mock import patch

        nome = "Imposto sobre a Propriedade Predial e Territorial Urbana"
        with patch(
            "apps.core.code_name_abbrev.iter_alias_lexico_ativos_ordenados",
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
            "apps.core.code_name_abbrev.iter_alias_lexico_ativos_ordenados",
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
            "apps.core.code_name_abbrev.iter_alias_lexico_ativos_ordenados",
            return_value=[],
        ):
            r = calcular_radical_abreviado("Imposto, sobre a Propriedade!")
        self.assertEqual(r.radical, "Imposto Propriedade")

    def test_sufixo_canonico(self) -> None:
        self.assertEqual(radical_com_sufixo_canonico("IPVA"), "IPVA - ")
