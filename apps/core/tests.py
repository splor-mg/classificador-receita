"""Testes do app ``core``."""

from django.test import SimpleTestCase, TestCase

from apps.core.alias_lexico_infer import (
    _infer_pairs,
    _is_sigla_second_segment_rule2,
    _significant_word_keys_major_segment,
    _try_rule_1_2_pf,
    _try_rule_1_2_pf_segment_coverage,
    _try_rule_1_2_pf_tail_echo,
    _try_rule_4_pf_pairs,
    _try_rule_a,
    _try_rule_nd_parenthetical_suffix,
    _try_rule_nd_two_segment_sigla,
)
from apps.core.alias_lexico_termo_policy import (
    termo_nome_persistivel,
    termo_nome_rejeitado_encurtamento_iv,
)


def _active_item_row(
    receita_nome: str,
    *,
    item_id: str = "it-1",
    parent_item_id: str = "-",
) -> dict[str, str]:
    return {
        "item_id": item_id,
        "item_ref": "1",
        "parent_item_id": parent_item_id,
        "receita_nome": receita_nome,
        "data_vigencia_inicio": "2026-01-01",
        "data_vigencia_fim": "9999-12-31",
        "data_registro_inicio": "2026-01-01 00:00:00",
        "data_registro_fim": "9999-12-31 00:00:00",
    }


class RuleNdTwoSegmentSiglaTests(SimpleTestCase):
    """Regra 2 (ND) e interacção com Regra 3 (ND) — ``alias_lexico_infer``."""

    def test_sigla_second_segment_strict_and_iof_ouro(self) -> None:
        self.assertTrue(_is_sigla_second_segment_rule2("IRPF"))
        self.assertTrue(_is_sigla_second_segment_rule2("PNAE"))
        self.assertTrue(_is_sigla_second_segment_rule2("DA-MJM"))
        self.assertTrue(_is_sigla_second_segment_rule2("IOF-Ouro"))
        self.assertFalse(_is_sigla_second_segment_rule2("Principal"))
        self.assertFalse(_is_sigla_second_segment_rule2("IuIE"))
        self.assertFalse(_is_sigla_second_segment_rule2("ITCD DA-MJM"))

    def test_try_rule_nd_two_segment_sigla_examples(self) -> None:
        self.assertEqual(
            _try_rule_nd_two_segment_sigla(
                "Imposto sobre a Renda de Pessoa Física - IRPF",
            ),
            ("Imposto sobre a Renda de Pessoa Física", "IRPF"),
        )
        self.assertEqual(
            _try_rule_nd_two_segment_sigla(
                "Imposto sobre Operações Financeiras Incidente sobre o Ouro - IOF-Ouro",
            ),
            (
                "Imposto sobre Operações Financeiras Incidente sobre o Ouro",
                "IOF-Ouro",
            ),
        )
        self.assertEqual(
            _try_rule_nd_two_segment_sigla(
                "Transferências Referentes ao Programa Nacional de Alimentação Escolar - PNAE",
            ),
            (
                "Transferências Referentes ao Programa Nacional de Alimentação Escolar",
                "PNAE",
            ),
        )

    def test_rule2_before_rule3_parenthetical(self) -> None:
        """Regra 2 tem prioridade sobre Regra 3 no primeiro passo de ``_infer_pairs``."""
        r2 = _try_rule_nd_two_segment_sigla("Alpha - IRPF")
        r3 = _try_rule_nd_parenthetical_suffix("Alpha - IRPF")
        self.assertEqual(r2, ("Alpha", "IRPF"))
        self.assertIsNone(r3)

    def test_infer_pairs_includes_rule2_without_parent(self) -> None:
        rows = [
            _active_item_row("Imposto sobre a Renda de Pessoa Física - IRPF", item_id="a"),
            _active_item_row(
                "Imposto sobre Vendas a Varejo de Combustíveis Líquidos e Gasosos (IVVC)",
                item_id="b",
            ),
        ]
        good, conflicts, _ = _infer_pairs(rows)
        self.assertEqual(conflicts, [])
        self.assertEqual(
            good["Imposto sobre a Renda de Pessoa Física"],
            "IRPF",
        )
        self.assertEqual(
            good["Imposto sobre Vendas a Varejo de Combustíveis Líquidos e Gasosos"],
            "IVVC",
        )

    def test_rule2_omit_when_sigla_abbrev_already_mapped(self) -> None:
        rows = [
            _active_item_row("Alienação Bens Mercadorias Apreendidos - MJM", item_id="x"),
        ]
        good, conflicts, _ = _infer_pairs(rows, abbrev_siglas_mapeadas_ci={"mjm"})
        self.assertEqual(conflicts, [])
        self.assertNotIn("Alienação Bens Mercadorias Apreendidos", good)

        good2, conflicts2, _ = _infer_pairs(rows)
        self.assertEqual(conflicts2, [])
        self.assertEqual(good2["Alienação Bens Mercadorias Apreendidos"], "MJM")


class Rule12PfTests(SimpleTestCase):
    """Regra 1.2 (PF) — caminho A (eco) e caminho B (cobertura lexical)."""

    def test_rule_1_2_cultura_example(self) -> None:
        parent = "Outras Transf. Convênios União Entidades - Princ. - Cultura"
        child = "Cultura - Ministério da Cidadania"
        got = _try_rule_1_2_pf_tail_echo(parent, child)
        self.assertEqual(
            got,
            (parent, "Cultura"),
        )

    def test_rule_1_2_case_insensitive_segment_match(self) -> None:
        parent = "Foo - Bar - cultura"
        child = "CULTURA - Baz"
        got = _try_rule_1_2_pf_tail_echo(parent, child)
        self.assertEqual(got, (parent, "CULTURA"))

    def test_rule_1_2_rejects_single_segment_parent(self) -> None:
        self.assertIsNone(
            _try_rule_1_2_pf_tail_echo(
                "Imposto sobre a Propriedade de Veículos Automotores",
                "IPVA - Principal",
            )
        )

    def test_rule_1_2_rejects_mismatched_tail_head(self) -> None:
        parent = "A - B - Cultura"
        child = "Outro - X"
        self.assertIsNone(_try_rule_1_2_pf_tail_echo(parent, child))

    def test_rule_1_2_before_rule_1_on_multi_segment_mother(self) -> None:
        parent = "Outras Transf. Convênios União Entidades - Princ. - Cultura"
        child = "Cultura - Ministério da Cidadania"
        self.assertIsNone(_try_rule_a(parent, child))
        self.assertIsNotNone(_try_rule_1_2_pf(parent, child))

    def test_rule_1_2_iof_ouro_path_b(self) -> None:
        parent = (
            "Cota-Parte do Imposto sobre Operações de Crédito, Câmbio e Seguro, "
            "ou Relativas a Títulos ou Valores Mobiliários - Comercialização do Ouro"
        )
        child = "Cota-Parte IOF-Ouro - Principal"
        self.assertIsNone(_try_rule_1_2_pf_tail_echo(parent, child))
        got = _try_rule_1_2_pf_segment_coverage(parent, child)
        self.assertEqual(got, (parent, "Cota-Parte IOF-Ouro"))
        self.assertEqual(_try_rule_1_2_pf(parent, child), got)

    def test_rule_1_2_path_b_word_keys_iof_ouro(self) -> None:
        child_seg = "Cota-Parte IOF-Ouro"
        keys = _significant_word_keys_major_segment(child_seg)
        self.assertTrue({"cota", "parte", "iof", "ouro"} <= keys)

    def test_rule_1_2_path_b_rejects_partial_segment_coverage(self) -> None:
        parent = "Segmento Alfa - Segmento Beta"
        child = "Só Alfa - Principal"
        self.assertIsNone(_try_rule_1_2_pf_segment_coverage(parent, child))
        self.assertIsNone(_try_rule_1_2_pf(parent, child))

    def test_infer_pairs_rule_1_2_iof_ouro(self) -> None:
        parent_name = (
            "Cota-Parte do Imposto sobre Operações de Crédito, Câmbio e Seguro, "
            "ou Relativas a Títulos ou Valores Mobiliários - Comercialização do Ouro"
        )
        parent_id = "IT-PARENT-1711550000000"
        child_id = "IT-CHILD-1711550100000"
        rows = [
            _active_item_row(parent_name, item_id=parent_id, parent_item_id="-"),
            _active_item_row(
                "Cota-Parte IOF-Ouro - Principal",
                item_id=child_id,
                parent_item_id=parent_id,
            ),
        ]
        good, conflicts, exempt = _infer_pairs(rows)
        self.assertEqual(conflicts, [])
        self.assertEqual(good[parent_name], "Cota-Parte IOF-Ouro")
        self.assertIn(parent_name, exempt)

    def test_infer_pairs_rule_1_2_parent_child(self) -> None:
        parent_id = "IT-PARENT-1717990109000"
        child_id = "IT-CHILD-1717990109001"
        parent_name = "Outras Transf. Convênios União Entidades - Princ. - Cultura"
        rows = [
            _active_item_row(
                parent_name,
                item_id=parent_id,
                parent_item_id="-",
            ),
            _active_item_row(
                "Cultura - Ministério da Cidadania",
                item_id=child_id,
                parent_item_id=parent_id,
            ),
        ]
        good, conflicts, exempt = _infer_pairs(rows)
        self.assertEqual(conflicts, [])
        self.assertEqual(good[parent_name], "Cultura")
        self.assertIn(parent_name, exempt)
        self.assertTrue(termo_nome_rejeitado_encurtamento_iv(parent_name))
        self.assertTrue(termo_nome_persistivel(parent_name, viii_exempt_termos=exempt))


class Rule4PfTests(SimpleTestCase):
    """Regra 4 (PF) — ``_try_rule_4_pf_pairs`` e integração em ``_infer_pairs``."""

    def test_rule4_icms_principal_princ(self) -> None:
        parent = "ICMS - Principal"
        child = "ICMS - Princ. - Cota Parte do Estado"
        pairs = _try_rule_4_pf_pairs(parent, child)
        self.assertEqual(pairs, [("Principal", "Princ.")])

    def test_rule4_icms_mjm(self) -> None:
        parent = "ICMS - Multas e Juros de Mora"
        child = "ICMS - MJM - Cota Parte do Estado"
        pairs = _try_rule_4_pf_pairs(parent, child)
        self.assertEqual(pairs, [("Multas e Juros de Mora", "MJM")])

    def test_rule4_omits_simple_connective_only(self) -> None:
        parent = "ICMS - Cota Parte do Estado"
        child = "ICMS - Cota Parte Estado - Devolução"
        self.assertEqual(_try_rule_4_pf_pairs(parent, child), [])

    def test_rule4_cessao_dotted_first_segment(self) -> None:
        parent = (
            "Cessão do Direito de Operacionalização de Pagamentos - "
            "Poderes Executivo e Legislativo"
        )
        child = (
            "Cessão Dir. Operac. Pag. - Poderes Executivo Legislativo - Principal"
        )
        pairs = _try_rule_4_pf_pairs(parent, child)
        self.assertEqual(
            pairs,
            [
                (
                    "Cessão do Direito de Operacionalização de Pagamentos",
                    "Cessão Dir. Operac. Pag.",
                ),
            ],
        )

    def test_rule4_tx_seguranca_publica(self) -> None:
        parent = "Tx. Insp. Contr. Fisc. - Princ. - Taxa de Segurança Pública"
        child = "Tx. Insp. Contr. Fisc. - Princ. - Tx. Segurança Pública - Outro"
        pairs = _try_rule_4_pf_pairs(parent, child)
        self.assertEqual(
            pairs,
            [("Taxa de Segurança Pública", "Tx. Segurança Pública")],
        )

    def test_rule4_wrong_segment_count_returns_empty(self) -> None:
        self.assertEqual(
            _try_rule_4_pf_pairs("A - B", "A - B - C - D"),
            [],
        )

    def test_infer_pairs_rule4_parent_child_cessao(self) -> None:
        parent_id = "IT-PARENT-1361011000000"
        child_id = "IT-CHILD-1361011100000"
        rows = [
            _active_item_row(
                "Cessão do Direito de Operacionalização de Pagamentos - "
                "Poderes Executivo e Legislativo",
                item_id=parent_id,
                parent_item_id="-",
            ),
            _active_item_row(
                "Cessão Dir. Operac. Pag. - Poderes Executivo Legislativo - Principal",
                item_id=child_id,
                parent_item_id=parent_id,
            ),
        ]
        good, conflicts, _ = _infer_pairs(rows)
        self.assertEqual(conflicts, [])
        self.assertEqual(
            good["Cessão do Direito de Operacionalização de Pagamentos"],
            "Cessão Dir. Operac. Pag.",
        )


class InsertAliasLexicoViiiExemptTests(TestCase):
    """INSERT com ``termo_viii_exempt`` (Regra 1.2) persiste termo com token (iv)."""

    def test_insert_rule_12_termo_with_princ_token(self) -> None:
        from apps.core.alias_lexico_protocol import insert_alias_lexico_if_new
        from apps.core.models import AliasLexico
        from apps.core.models_alias_lexico import (
            lista_abreviacoes_registro_fim_sentinela,
            lista_abreviacoes_registro_inicio_novo,
        )

        termo = "Outras Transf. Convênios União Entidades - Princ. - Cultura"
        AliasLexico.objects.filter(termo__iexact=termo).delete()
        ok, obj = insert_alias_lexico_if_new(
            termo=termo,
            abreviacao="Cultura",
            alias_lexico_ref=88888,
            data_registro_inicio=lista_abreviacoes_registro_inicio_novo(),
            data_registro_fim=lista_abreviacoes_registro_fim_sentinela(),
            termo_viii_exempt=True,
        )
        self.assertTrue(ok)
        self.assertIsNotNone(obj)
        if obj is not None:
            obj.delete()


class TermoNomeEncurtamentoIvPolicyTests(SimpleTestCase):
    """Spec (viii): token (iv) no ``termo`` / ``termo_nome`` — ``alias_lexico_termo_policy``."""

    def test_invalid_contrib_patronal(self) -> None:
        self.assertTrue(termo_nome_rejeitado_encurtamento_iv("Contrib. Patronal"))

    def test_valid_contribuicao_patronal(self) -> None:
        self.assertFalse(termo_nome_rejeitado_encurtamento_iv("Contribuição Patronal"))

    def test_sigla_icms_allowed_in_termo(self) -> None:
        self.assertFalse(termo_nome_rejeitado_encurtamento_iv("Contribuição para o ICMS"))

    def test_strip_wrapping_punctuation(self) -> None:
        self.assertTrue(termo_nome_rejeitado_encurtamento_iv("(Contrib.) Patronal"))

    def test_empty_invalid(self) -> None:
        self.assertTrue(termo_nome_rejeitado_encurtamento_iv(""))
        self.assertTrue(termo_nome_rejeitado_encurtamento_iv("   "))


class ListaAbreviacoesRegistroInicioTests(SimpleTestCase):
    """Spec (L) / ``lista_abreviacoes_registro_inicio_novo``."""

    def test_registro_inicio_novo_e_1_janeiro_ano_corrente(self) -> None:
        from django.utils import timezone

        from apps.core.models_alias_lexico import lista_abreviacoes_registro_inicio_novo

        dt = lista_abreviacoes_registro_inicio_novo()
        local = timezone.localtime(dt)
        self.assertEqual(local.year, timezone.localdate().year)
        self.assertEqual((local.month, local.day, local.hour, local.minute), (1, 1, 0, 0))

    def test_admin_add_preview_inicio_fmt_usa_padrao_l(self) -> None:
        from django.contrib.admin.sites import AdminSite

        from apps.core.admin import AliasLexicoAdmin, _alias_lexico_format_registro_dt
        from apps.core.models import AliasLexico
        from apps.core.models_alias_lexico import lista_abreviacoes_registro_inicio_novo

        admin = AliasLexicoAdmin(AliasLexico, AdminSite())
        esperado = _alias_lexico_format_registro_dt(lista_abreviacoes_registro_inicio_novo())
        self.assertEqual(admin.data_registro_inicio_fmt(None), esperado)

    def test_clean_com_defaults_nao_compara_naive_com_aware(self) -> None:
        from unittest.mock import MagicMock, patch

        from apps.core.models import AliasLexico
        from apps.core.models_alias_lexico import (
            lista_abreviacoes_registro_fim_sentinela,
            lista_abreviacoes_registro_inicio_novo,
        )

        obj = AliasLexico(
            alias_lexico_ref=1,
            termo="Contribuição Patronal",
            abreviacao="Contr. Patronal",
            data_registro_inicio=lista_abreviacoes_registro_inicio_novo(),
            data_registro_fim=lista_abreviacoes_registro_fim_sentinela(),
        )
        dup_qs = MagicMock()
        dup_qs.exists.return_value = False
        with patch.object(AliasLexico.objects, "filter", return_value=dup_qs):
            obj.clean()
        self.assertLess(obj.data_registro_inicio, obj.data_registro_fim)
