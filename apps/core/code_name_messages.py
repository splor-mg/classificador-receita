"""
Textos do fluxo de nome da classificação (radical do item mãe) na criação no admin.

Usados no cliente via json_script no template; mantidos aqui como fonte única.
"""

RECEITA_NOME_SUGESTAO_INFO_COMPLETO = (
    "Nome sugerido com base na versão completa do item mãe selecionado. "
    "Complete o nome após o traço, ou remova o traço final para gravar apenas o radical."
)

RECEITA_NOME_SUGESTAO_INFO_ABREV_TEMPLATE = (
    'Nome sugerido com base na versão abreviada do item mãe selecionado. '
    'Complete o nome após o traço, ou remova o traço final para gravar apenas o radical. '
    'O nome do item mãe é "{nome_mae}"'
)

REMOVE_BASE_PREFIX_MISMATCH_WARNING = (
    "Não foi possível remover automaticamente o nome base do item mãe, "
    "pois não há correspondência exata no início do campo."
)

RECEITA_NOME_VAZIO_ERROR = (
    "Preencha o Nome da Classificação por Natureza de Receita para concluir o cadastro."
)

# **G1.5.a** — sugestão automática literal não completada.
# Disparada quando ``n`` casa com ``b_completo + (N5)`` ou ``b_abreviado + (N5)``
# (com (N7) flexível e espaços ASCII opcionais ao redor do traço).
RECEITA_NOME_SUBMIT_SUGESTAO_LITERAL_ERROR = (
    "Atualize o nome após o traço para concluir o cadastro, ou "
    "remova o traço final se desejar gravar apenas o radical "
    "sugerido (completo ou abreviado)."
)

# **G1.5.b** — nome termina com traço (não é sugestão literal).
# Vale também em ``sem_base`` (em que ``b`` é indefinido).
RECEITA_NOME_SUBMIT_TRACO_FINAL_ERROR = (
    "O Nome da Classificação por Natureza de Receita não pode terminar com traço "
    "(-, – ou —). Adicione um complemento após o último traço ou remova-o."
)

# Chaves canônicas das mensagens (também expostas via ``code_name_messages_dict``).
MENSAGEM_SUGESTAO_LITERAL_KEY = "receita_nome_submit_sugestao_literal_error"
MENSAGEM_TRACO_FINAL_KEY = "receita_nome_submit_traco_final_error"

RECEITA_NOME_LEXICO_TERMO_DUPLICADO_TEMPLATE = (
    "Verifique na Lista de Abreviações: o termo_nome «{termo_nome}» está duplicado "
    "(há mais de um registro ativo)."
)


def format_receita_nome_sugestao_info_abrev(nome_mae: str) -> str:
    escaped = (nome_mae or "").replace('"', '\\"')
    return RECEITA_NOME_SUGESTAO_INFO_ABREV_TEMPLATE.format(nome_mae=escaped)


def format_lexico_termo_duplicado(termo_nome: str) -> str:
    return RECEITA_NOME_LEXICO_TERMO_DUPLICADO_TEMPLATE.format(termo_nome=termo_nome or "")


def code_name_messages_dict():
    return {
        "receita_nome_sugestao_info_completo": RECEITA_NOME_SUGESTAO_INFO_COMPLETO,
        "receita_nome_sugestao_info_abrev_template": RECEITA_NOME_SUGESTAO_INFO_ABREV_TEMPLATE,
        "remove_base_prefix_mismatch": REMOVE_BASE_PREFIX_MISMATCH_WARNING,
        "receita_nome_vazio_error": RECEITA_NOME_VAZIO_ERROR,
        MENSAGEM_SUGESTAO_LITERAL_KEY: RECEITA_NOME_SUBMIT_SUGESTAO_LITERAL_ERROR,
        MENSAGEM_TRACO_FINAL_KEY: RECEITA_NOME_SUBMIT_TRACO_FINAL_ERROR,
        "receita_nome_lexico_termo_duplicado_template": RECEITA_NOME_LEXICO_TERMO_DUPLICADO_TEMPLATE,
    }
