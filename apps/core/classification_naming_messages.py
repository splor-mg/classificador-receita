"""
Textos do fluxo de nome da classificação (radical do item mãe) na criação no admin.

Usados no cliente via json_script no template; mantidos aqui como fonte única.
"""

RECEITA_NOME_SUGESTAO_INFO_COMPLETO = (
    "Nome sugerido com base na versão completa do item mãe selecionado. "
    "Complete o nome desta classificação após o traço."
)

RECEITA_NOME_SUGESTAO_INFO_ABREV_TEMPLATE = (
    'Nome sugerido com base na versão abreviada do item mãe selecionado. '
    'Complete o nome desta classificação após o traço. '
    'O nome do item mãe é "{nome_mae}"'
)

REMOVE_BASE_PREFIX_MISMATCH_WARNING = (
    "Não foi possível remover automaticamente o nome base do item mãe, "
    "pois não há correspondência exata no início do campo."
)

RECEITA_NOME_VAZIO_ERROR = (
    "Preencha o Nome da Classificação por Natureza de Receita para concluir o cadastro."
)

RECEITA_NOME_SUBMIT_INCOMPLETO_ERROR = (
    "Atualize o nome da classificação após o traço para concluir o cadastro, "
    "ou remova o traço se não quiser um complemento além do radical sugerido "
    "(completo ou abreviado) com base no item mãe."
)

RECEITA_NOME_LEXICO_TERMO_DUPLICADO_TEMPLATE = (
    "Verifique na Lista de Abreviações: o termo_nome «{termo_nome}» está duplicado "
    "(há mais de um registro ativo)."
)


def format_receita_nome_sugestao_info_abrev(nome_mae: str) -> str:
    escaped = (nome_mae or "").replace('"', '\\"')
    return RECEITA_NOME_SUGESTAO_INFO_ABREV_TEMPLATE.format(nome_mae=escaped)


def format_lexico_termo_duplicado(termo_nome: str) -> str:
    return RECEITA_NOME_LEXICO_TERMO_DUPLICADO_TEMPLATE.format(termo_nome=termo_nome or "")


def classification_naming_messages_dict():
    return {
        "receita_nome_sugestao_info_completo": RECEITA_NOME_SUGESTAO_INFO_COMPLETO,
        "receita_nome_sugestao_info_abrev_template": RECEITA_NOME_SUGESTAO_INFO_ABREV_TEMPLATE,
        "remove_base_prefix_mismatch": REMOVE_BASE_PREFIX_MISMATCH_WARNING,
        "receita_nome_vazio_error": RECEITA_NOME_VAZIO_ERROR,
        "receita_nome_submit_incompleto_error": RECEITA_NOME_SUBMIT_INCOMPLETO_ERROR,
        "receita_nome_lexico_termo_duplicado_template": RECEITA_NOME_LEXICO_TERMO_DUPLICADO_TEMPLATE,
    }
