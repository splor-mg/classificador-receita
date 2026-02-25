# Domínios compartilhados entre models, espelhando schemas/dominios/*.yaml.
# Fonte de verdade conceitual: arquivos YAML em schemas/dominios/;
# este módulo mantém as opções para uso em CharField(choices=...) no Django.

# Domínio orgaos_entidades (dominios/orgaos_entidades.yaml).
# Usado em: SerieClassificacao.orgao_responsavel, BaseLegalTecnica.orgao_responsavel.
ORGAOS_ENTIDADES_CHOICES = [
    ('Planalto-BRA', 'Presidência da República / Planalto'),
    ('Congresso-BRA', 'Congresso Nacional'),
    ('Camara-BRA', 'Câmara dos Deputados'),
    ('Senado-BRA', 'Senado Federal'),
    ('STF-BRA', 'Supremo Tribunal Federal'),
    ('STJ-BRA', 'Superior Tribunal de Justiça'),
    ('TRF-BRA', 'Tribunal Regional Federal'),
    ('TCU-BRA', 'Tribunal de Contas da União'),
    ('CGU-BRA', 'Controladoria-Geral da União'),
    ('AGU-BRA', 'Advocacia-Geral da União'),
    ('STN-BRA', 'Secretaria do Tesouro Nacional'),
    ('SOF-BRA', 'Secretaria de Orçamento Federal'),
    ('RFB-BRA', 'Receita Federal do Brasil'),
    ('BACEN-BRA', 'Banco Central do Brasil'),
    ('AL-MG', 'Assembleia Legislativa de Minas Gerais'),
    ('TCE-MG', 'Tribunal de Contas do Estado de Minas Gerais'),
    ('TJ-MG', 'Tribunal de Justiça de Minas Gerais'),
    ('CGE-MG', 'Controladoria-Geral do Estado de Minas Gerais'),
    ('AGE-MG', 'Advocacia-Geral do Estado de Minas Gerais'),
    ('SEPLAG-MG', 'Secretaria de Estado de Planejamento e Gestão de Minas Gerais'),
    ('SEF-MG', 'Secretaria de Estado da Fazenda de Minas Gerais'),
]
