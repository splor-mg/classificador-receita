"""
Conectivos e palavras funcionais omitíveis na compactação de nomes (lista fixa).

A ordem de aplicação (frases → palavras → conectivos) e o uso em ``AliasLexico``
serão consolidados no serviço de abreviação nas próximas etapas.
"""

# Normalizar comparações em minúsculas (acentos preservados como cadastrados nos dados).
NOME_CLASSIFICACAO_CONNECTIVOS_FIXOS = frozenset(
    {
        "a",
        "o",
        "as",
        "os",
        "e",
        "ou",
        "de",
        "da",
        "do",
        "das",
        "dos",
        "em",
        "na",
        "no",
        "nas",
        "nos",
        "por",
        "para",
        "com",
        "sem",
        "ao",
        "aos",
        "à",
        "às",
        "pelo",
        "pela",
        "pelos",
        "pelas",
        "um",
        "uma",
        "uns",
        "umas",
    }
)
