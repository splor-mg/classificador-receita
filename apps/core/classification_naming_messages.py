"""
Textos do fluxo de nome da classificação (radical do item pai) na criação no admin.

Usados no cliente via json_script no template; mantidos aqui como fonte única.
"""

RECEITA_NOME_SUGESTAO_INFO = (
    "Nome sugerido com base no item mãe selecionado. "
    "Complete o nome desta classificação após o traço."
)

REMOVE_BASE_PREFIX_MISMATCH_WARNING = (
    "Não foi possível remover automaticamente o nome base do item pai, "
    "pois não há correspondência exata no início do campo."
)

RECEITA_NOME_SUBMIT_INCOMPLETO_ERROR = (
    "Atualize o nome da classificação após o traço para concluir o cadastro, "
    "ou remova o traço para repetir nome do item pai."
)


def classification_naming_messages_dict():
    return {
        "receita_nome_sugestao_info": RECEITA_NOME_SUGESTAO_INFO,
        "remove_base_prefix_mismatch": REMOVE_BASE_PREFIX_MISMATCH_WARNING,
        "receita_nome_submit_incompleto_error": RECEITA_NOME_SUBMIT_INCOMPLETO_ERROR,
    }
