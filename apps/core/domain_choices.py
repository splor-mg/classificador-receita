"""
Domínios compartilhados entre models, espelhando schemas/dominios/*.yaml.

Fonte de verdade conceitual: arquivos YAML em schemas/dominios/;
este módulo mantém as opções para uso em CharField(choices=...) no Django
e estruturas auxiliares para apresentação (grupos, labels combinados etc.).
"""

# Domínio orgaos_entidades (dominios/orgaos_entidades.yaml).
# Usado em: SerieClassificacao.orgao_responsavel, BaseLegalTecnica.orgao_responsavel.
ORGAOS_ENTIDADES_CHOICES = [
    # Federal – Legislativo e Executivo
    ("Camara-BRA", "Câmara dos Deputados"),
    ("Congresso-BRA", "Congresso Nacional"),
    ("Planalto-BRA", "Presidência da República / Planalto"),
    ("Senado-BRA", "Senado Federal"),

    # Federal – Justiça e Controle
    ("AGU-BRA", "Advocacia-Geral da União"),
    ("CGU-BRA", "Controladoria-Geral da União"),
    ("STF-BRA", "Supremo Tribunal Federal"),
    ("STJ-BRA", "Superior Tribunal de Justiça"),
    ("TCU-BRA", "Tribunal de Contas da União"),
    ("TRF-BRA", "Tribunal Regional Federal"),

    # Federal – Finanças Públicas
    ("BACEN-BRA", "Banco Central do Brasil"),
    ("RFB-BRA", "Receita Federal do Brasil"),
    ("SOF-BRA", "Secretaria de Orçamento Federal"),
    ("STN-BRA", "Secretaria do Tesouro Nacional"),

    # Estadual – Minas Gerais
    ("AGE-MG", "Advocacia-Geral do Estado de Minas Gerais"),
    ("AL-MG", "Assembleia Legislativa de Minas Gerais"),
    ("CGE-MG", "Controladoria-Geral do Estado de Minas Gerais"),
    ("SEF-MG", "Secretaria de Estado da Fazenda de Minas Gerais"),
    ("SEPLAG-MG", "Secretaria de Estado de Planejamento e Gestão de Minas Gerais"),
    ("TCE-MG", "Tribunal de Contas do Estado de Minas Gerais"),
    ("TJ-MG", "Tribunal de Justiça de Minas Gerais"),
]


# Grupos de órgãos/entidades para uso em selects mais informativos no Admin.
# Os códigos abaixo são os mesmos de ORGAOS_ENTIDADES_CHOICES.
ORGAOS_ENTIDADES_GROUPS = [
    (
        "Federal – Legislativo e Executivo",
        ["Camara-BRA", "Congresso-BRA", "Planalto-BRA", "Senado-BRA"],
    ),
    (
        "Federal – Justiça e Controle",
        ["AGU-BRA", "CGU-BRA", "STF-BRA", "STJ-BRA", "TCU-BRA", "TRF-BRA"],
    ),
    (
        "Federal – Finanças Públicas",
        ["BACEN-BRA", "RFB-BRA", "SOF-BRA", "STN-BRA"],
    ),
    (
        "Estadual – Minas Gerais",
        ["AGE-MG", "AL-MG", "CGE-MG", "SEF-MG", "SEPLAG-MG", "TCE-MG", "TJ-MG"],
    ),
]


def build_orgaos_entidades_grouped_choices():
    """
    Constrói choices agrupadas para uso em <select> com <optgroup> no Admin.

    Cada opção é exibida como "CÓDIGO - Rótulo", por exemplo:
    "STN-BRA - Secretaria do Tesouro Nacional".

    Retorna lista no formato esperado pelo Django:
        [(label_grupo, [(value, label_renderizado), ...]), ...]
    """
    label_by_value = {value: label for value, label in ORGAOS_ENTIDADES_CHOICES}
    grouped = []
    seen = set()

    for group_label, values in ORGAOS_ENTIDADES_GROUPS:
        group_choices = []
        for value in values:
            label = label_by_value.get(value)
            if label is None:
                continue
            group_choices.append((value, f"{value} - {label}"))
            seen.add(value)
        if group_choices:
            grouped.append((group_label, group_choices))

    # Se, por algum motivo, surgirem valores no domínio que não foram
    # explicitamente atribuídos a um grupo, mantemos um grupo final
    # "Outros órgãos/entidades" para não perder opções.
    remaining = [
        (value, f"{value} - {label}")
        for value, label in ORGAOS_ENTIDADES_CHOICES
        if value not in seen
    ]
    if remaining:
        grouped.append(("Outros órgãos/entidades", remaining))

    return grouped


ORGAOS_ENTIDADES_GROUPED_CHOICES = build_orgaos_entidades_grouped_choices()
