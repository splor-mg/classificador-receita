# Domínios compartilhados entre models, espelhando schemas/dominios/*.yaml.
# Fonte de verdade conceitual: arquivos YAML em schemas/dominios/;
# este módulo mantém as opções para uso em CharField(choices=...) no Django.

# Domínio orgaos_entidades (dominios/orgaos_entidades.yaml).
# Usado em: SerieClassificacao.orgao_responsavel, BaseLegalTecnica.orgao_responsavel.
ORGAOS_ENTIDADES_CHOICES = [
    ('planalto', 'Presidência da República / Planalto'),
    ('congresso', 'Congresso Nacional'),
    ('camara', 'Câmara dos Deputados'),
    ('senado', 'Senado Federal'),
    ('stf', 'Supremo Tribunal Federal'),
    ('stj', 'Superior Tribunal de Justiça'),
    ('trf', 'Tribunal Regional Federal'),
    ('tcu', 'Tribunal de Contas da União'),
    ('cgu', 'Controladoria-Geral da União'),
    ('agu', 'Advocacia-Geral da União'),
    ('stn', 'Secretaria do Tesouro Nacional'),
    ('sof', 'Secretaria de Orçamento Federal'),
    ('rfb', 'Receita Federal do Brasil'),
    ('bacen', 'Banco Central do Brasil'),
    ('almg', 'Assembleia Legislativa de Minas Gerais'),
    ('tcemg', 'Tribunal de Contas do Estado de Minas Gerais'),
    ('tjmg', 'Tribunal de Justiça de Minas Gerais'),
    ('cgemg', 'Controladoria-Geral do Estado de Minas Gerais'),
    ('agemg', 'Advocacia-Geral do Estado de Minas Gerais'),
    ('seplag-mg', 'Secretaria de Estado de Planejamento e Gestão de Minas Gerais'),
    ('sef-mg', 'Secretaria de Estado da Fazenda de Minas Gerais'),
]
