from django.db import models

from .domain_choices import ORGAOS_ENTIDADES_CHOICES


class BaseLegalTecnica(models.Model):
    """
    Base Legal/Técnica (normas, manuais, decisões, etc.) que podem afetar as tabelas de classificação.
    Compatível com schemas/base_legal_tecnica.yaml.

    Importante: esta tabela é apenas de VIGÊNCIA (sem data_registro_*), pois atua preponderantemente como
    dimensão de referência legal/técnica. Ver ADR-001 (escopo da bitemporalidade). Por esse motivo,
    foi modelada em arquivo à parte para não interferir no modelo bitemporal principal.
    """

    # Domínio fechado de esfera federativa, alinhado ao enum do schema.
    ESFERA_UNIAO = 'BRA'
    ESFERA_AC = 'AC'
    ESFERA_AL = 'AL'
    ESFERA_AM = 'AM'
    ESFERA_AP = 'AP'
    ESFERA_BA = 'BA'
    ESFERA_CE = 'CE'
    ESFERA_DF = 'DF'
    ESFERA_ES = 'ES'
    ESFERA_GO = 'GO'
    ESFERA_MA = 'MA'
    ESFERA_MG = 'MG'
    ESFERA_MS = 'MS'
    ESFERA_MT = 'MT'
    ESFERA_PA = 'PA'
    ESFERA_PB = 'PB'
    ESFERA_PE = 'PE'
    ESFERA_PI = 'PI'
    ESFERA_PR = 'PR'
    ESFERA_RJ = 'RJ'
    ESFERA_RN = 'RN'
    ESFERA_RO = 'RO'
    ESFERA_RR = 'RR'
    ESFERA_RS = 'RS'
    ESFERA_SC = 'SC'
    ESFERA_SE = 'SE'
    ESFERA_SP = 'SP'
    ESFERA_TO = 'TO'

    ESFERA_FEDERATIVA_CHOICES = [
        (ESFERA_UNIAO, 'BRA'),
        (ESFERA_AC, 'AC'),
        (ESFERA_AL, 'AL'),
        (ESFERA_AM, 'AM'),
        (ESFERA_AP, 'AP'),
        (ESFERA_BA, 'BA'),
        (ESFERA_CE, 'CE'),
        (ESFERA_DF, 'DF'),
        (ESFERA_ES, 'ES'),
        (ESFERA_GO, 'GO'),
        (ESFERA_MA, 'MA'),
        (ESFERA_MG, 'MG'),
        (ESFERA_MS, 'MS'),
        (ESFERA_MT, 'MT'),
        (ESFERA_PA, 'PA'),
        (ESFERA_PB, 'PB'),
        (ESFERA_PE, 'PE'),
        (ESFERA_PI, 'PI'),
        (ESFERA_PR, 'PR'),
        (ESFERA_RJ, 'RJ'),
        (ESFERA_RN, 'RN'),
        (ESFERA_RO, 'RO'),
        (ESFERA_RR, 'RR'),
        (ESFERA_RS, 'RS'),
        (ESFERA_SC, 'SC'),
        (ESFERA_SE, 'SE'),
        (ESFERA_SP, 'SP'),
        (ESFERA_TO, 'TO'),
    ]

    # Domínio fechado de tipo_legal, alinhado ao enum do schema.
    TIPO_ADCT = 'adct'
    TIPO_CR = 'cr'
    TIPO_CE = 'ce'
    TIPO_DEC = 'dec'
    TIPO_DEC_LEI = 'dec-lei'
    TIPO_EC = 'ec'
    TIPO_INST_NORM = 'inst-norm'
    TIPO_JRSP = 'jrsp'
    TIPO_LC = 'lc'
    TIPO_LCE = 'lce'
    TIPO_LDO = 'ldo'
    TIPO_LO = 'lo'
    TIPO_LOA = 'loa'
    TIPO_LOM = 'lom'
    TIPO_LOE = 'loe'
    TIPO_MAN = 'man'
    TIPO_NTJ = 'ntj'
    TIPO_NTT = 'ntt'
    TIPO_PARECER = 'parecer'
    TIPO_PEC = 'pec'
    TIPO_PL = 'pl'
    TIPO_PORT = 'port'
    TIPO_PORT_CONJ = 'port-conj'
    TIPO_PPA = 'ppa'
    TIPO_PPAG = 'ppag'
    TIPO_REG = 'reg'
    TIPO_SUM = 'sum'
    TIPO_SUM_VINC = 'sum-vinc'

    TIPO_LEGAL_CHOICES = [
        (TIPO_ADCT, 'adct'),
        (TIPO_CR, 'cr'),
        (TIPO_CE, 'ce'),
        (TIPO_DEC, 'dec'),
        (TIPO_DEC_LEI, 'dec-lei'),
        (TIPO_EC, 'ec'),
        (TIPO_INST_NORM, 'inst-norm'),
        (TIPO_JRSP, 'jrsp'),
        (TIPO_LC, 'lc'),
        (TIPO_LCE, 'lce'),
        (TIPO_LDO, 'ldo'),
        (TIPO_LO, 'lo'),
        (TIPO_LOA, 'loa'),
        (TIPO_LOM, 'lom'),
        (TIPO_LOE, 'loe'),
        (TIPO_MAN, 'man'),
        (TIPO_NTJ, 'ntj'),
        (TIPO_NTT, 'ntt'),
        (TIPO_PARECER, 'parecer'),
        (TIPO_PEC, 'pec'),
        (TIPO_PL, 'pl'),
        (TIPO_PORT, 'port'),
        (TIPO_PORT_CONJ, 'port-conj'),
        (TIPO_PPA, 'ppa'),
        (TIPO_PPAG, 'ppag'),
        (TIPO_REG, 'reg'),
        (TIPO_SUM, 'sum'),
        (TIPO_SUM_VINC, 'sum-vinc'),
    ]

    base_legal_tecnica_id = models.CharField(
        max_length=100,
        verbose_name='Identificador da Base Legal/Técnica',
        help_text=(
            'Identificador único da entidade norma/ato (chave semântica). Sugestão: '
            '[{tipo_legal}-{numero}-{orgao_responsavel}], ex.: CR-88-PLANALTO, LC-101-BRA.'
        ),
        db_index=True,
    )
    base_legal_tecnica_ref = models.IntegerField(
        verbose_name='Referência Numérica da Base Legal/Técnica',
        help_text=(
            'Identificador numérico estável da norma/ato/manuais, usado na chave primária lógica. '
            'Mesmo valor para todas as linhas que pertencem à mesma entidade '
            '(mesmo base_legal_tecnica_id).'
        ),
    )
    esfera_federativa = models.CharField(
        max_length=3,
        verbose_name='Esfera Federativa',
        help_text='Esfera federativa à qual a norma se aplica (BRA ou sigla de UF).',
        choices=ESFERA_FEDERATIVA_CHOICES,
    )
    tipo_legal = models.CharField(
        max_length=20,
        verbose_name='Tipo da Norma (sigla)',
        help_text='Tipo da norma jurídica/técnica (ex.: cr, lc, man, ntj, ntt, port).',
        choices=TIPO_LEGAL_CHOICES,
    )
    numero_codigo = models.CharField(
        max_length=50,
        verbose_name='Número/Código da Norma',
        help_text='Número ou código identificador da norma (ex.: número da lei, decreto, portaria).',
    )
    data_edicao = models.DateField(
        verbose_name='Data de Edição/Assinatura',
        help_text='Data em que a autoridade competente editou/assinou o ato normativo/instrumento técnico.',
    )
    orgao_responsavel = models.CharField(
        max_length=255,
        verbose_name='Órgão/Entidade Responsável',
        help_text=(
            'Órgão ou entidade responsável pela promulgação do ato normativo ou instrumento jurídico/técnico. '
            'Valores válidos: dominios/orgaos_entidades.yaml (domainRef).'
        ),
        choices=ORGAOS_ENTIDADES_CHOICES,
    )
    titulo_norma = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Título da Norma',
        help_text='Título oficial ou nome curto da norma.',
    )
    ementa = models.TextField(
        blank=True,
        verbose_name='Ementa',
        help_text='Ementa ou resumo da norma.',
    )
    url_fonte = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='URL da Fonte',
        help_text='URL estável para consulta ao texto da norma (Planalto, DO, portal da casa legislativa).',
    )
    data_vigencia_inicio = models.DateField(
        verbose_name='Data de Início da Vigência',
        help_text='Data a partir da qual a norma passa a ter vigência.',
    )
    data_vigencia_fim = models.DateField(
        verbose_name='Data do Fim da Vigência',
        help_text='Data até a qual a norma permanece vigente (9999-12-31 indica vigência ativa).',
    )

    class Meta:
        db_table = 'base_legal_tecnica'
        verbose_name = 'Base Legal/Técnica'
        verbose_name_plural = 'Bases Legais/Técnicas'
        constraints = [
            models.UniqueConstraint(
                fields=['base_legal_tecnica_ref', 'data_vigencia_inicio'],
                name='unique_base_legal_tecnica_ref_vigencia',
            )
        ]

    def __str__(self) -> str:
        return f"{self.base_legal_tecnica_id} - {self.titulo_norma or self.numero_codigo}"

