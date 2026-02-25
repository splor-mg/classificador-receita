from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.core.exceptions import ValidationError

from apps.core.models_base_legal import BaseLegalTecnica
from apps.core.domain_choices import ORGAOS_ENTIDADES_CHOICES


# Constantes para valores sentinelas (conforme ADR-001)
VALID_TIME_SENTINEL = '9999-12-31'
TRANSACTION_TIME_SENTINEL = '9999-12-31'


class BitemporalModel(models.Model):
    """
    Classe base abstrata para models bitemporais.
    
    Implementa os campos de valid_time (data_vigência) e transaction_time (data_registro)
    conforme ADR-001 - Estratégia de Bitemporalidade.
    
    Todos os models do classificador herdam desta classe base.
    """
    data_vigencia_inicio = models.DateField(
        verbose_name='Data de Início da Vigência',
        help_text='Data de início da vigência no domínio orçamentário (valid_time - início)'
    )
    data_vigencia_fim = models.DateField(
        verbose_name='Data do Fim da Vigência',
        help_text='Data de fim da vigência (valid_time - fim). Valor sentinela 9999-12-31 indica vigência ativa no momento corrente e futuro.'
    )
    data_registro_inicio = models.DateField(
        verbose_name='Data de Início do Registro',
        help_text='Data em que o sistema registrou esta informação (transaction_time - início)'
    )
    data_registro_fim = models.DateField(
        verbose_name='Data do Fim do Registro',
        help_text='Data em que esta informação deixou de ser considerada verdadeira pelo sistema (transaction_time - fim). Valor sentinela 9999-12-31 indica registro ativo no momento corrente e futuro.'
    )

    class Meta:
        abstract = True

    def clean(self):
        """Validação básica de intervalos temporais"""
        if self.data_vigencia_inicio and self.data_vigencia_fim:
            if self.data_vigencia_inicio > self.data_vigencia_fim:
                raise ValidationError({
                    'data_vigencia_fim': 'Data de fim da vigência deve ser posterior à data de início.'
                })
        if self.data_registro_inicio and self.data_registro_fim:
            if self.data_registro_inicio > self.data_registro_fim:
                raise ValidationError({
                    'data_registro_fim': 'Data de fim do registro deve ser posterior à data de início.'
                })


class SerieClassificacao(BitemporalModel):
    """
    Série de Classificações (GSIM ClassificationSeries).
    
    Responsável pela IDENTIDADE do classificador/série (classificador de receita) ao longo do tempo.

    Neste escopo, responde a questões de alto nível, como quem é a unidade institucional responsável, qual o propósito da série.
    
    Não guarda estrutura nem datas de lançamento. Não é uma entidade com níveis e itens (códigos).
    """
    serie_id = models.CharField(
        max_length=100,
        verbose_name='Identificador da Série',
        help_text='Identificador único da série de classificações',
        db_index=True
    )
    serie_ref = models.IntegerField(
        null=False,
        blank=False,
        verbose_name='Referência Numérica da Série',
        help_text=(
            'Identificador numérico estável da série de classificações, usado na chave primária '
            'lógica (bitemporal). Mesmo valor para todas as linhas que pertencem à mesma entidade '
            '(mesmo serie_id).'
        ),
    )
    serie_nome = models.CharField(
        max_length=255,
        blank=False,
        verbose_name='Nome da Série',
        help_text='Nome oficial da série de classificações'
    )
    descricao = models.TextField(
        blank=False,
        verbose_name='Descrição',
        help_text='Descrição detalhada da série de classificações e seu propósito'
    )
    orgao_responsavel = models.CharField(
        max_length=255,
        blank=False,
        verbose_name='Órgão Responsável',
        help_text=(
            'Órgão ou entidade responsável pela manutenção da série de classificações. '
            'Valores válidos: dominios/orgaos_entidades.yaml (domainRef).'
        ),
        choices=ORGAOS_ENTIDADES_CHOICES,
    )

    class Meta:
        db_table = 'serie_classificacao'
        verbose_name = 'Série de Classificação'
        verbose_name_plural = 'Séries de Classificações'
        constraints = [
            models.UniqueConstraint(
                fields=['serie_id', 'data_vigencia_inicio', 'data_registro_inicio'],
                name='unique_serie_registro'
            ),
            models.UniqueConstraint(
                fields=['serie_ref', 'data_vigencia_inicio', 'data_registro_inicio'],
                name='unique_serie_ref_registro',
            ),
        ]
        indexes = [
            models.Index(
                fields=['serie_id', 'data_registro_fim'],
                name='idx_serie_registro_fim'
                ),
            models.Index(
                fields=['data_vigencia_inicio', 'data_vigencia_fim'], 
                name='idx_serie_vigencia'
                ),
        ]

    def __str__(self):
        return f"{self.serie_nome} ({self.serie_id})"


class Classificacao(BitemporalModel):
    """
    Classificação Estatística (GSIM StatisticalClassification).

    Identifica qual EDIÇÃO do classificador/série estatística estamos tratando. 
    
    Neste escopo, responde quais são os qualificadores básicos da estrutura vigente, tais como o tipo do classificador (hierárquico ou linear) e o número de níveis.    
    """
    TIPO_HIERARQUICA = 'hierárquica'
    TIPO_LINEAR = 'linear'
    TIPO_CHOICES = [
        (TIPO_HIERARQUICA, 'Hierárquica'),
        (TIPO_LINEAR, 'Linear'),
    ]

    classificacao_id = models.CharField(
        max_length=100,
        verbose_name='Identificador da Classificação',
        help_text='Identificador único da classificação estatística (chave semântica).',
        db_index=True
    )
    classificacao_ref = models.IntegerField(
        null=False,
        blank=False,
        verbose_name='Referência Numérica da Classificação',
        help_text=(
            'Identificador numérico estável da classificação estatística, usado na chave primária '
            'lógica (bitemporal). Mesmo valor para todas as linhas que pertencem à mesma entidade '
            '(mesmo classificacao_id).'
        ),
    )
    # Importante: o schema Frictionless expõe o campo como `serie_id`.
    # Mantemos o mesmo nome aqui por alinhamento, mas este campo é uma ForeignKey
    # para `SerieClassificacao` (não apenas uma string). O `db_column` garante
    # que a coluna física também se chame exatamente `serie_id`.
    serie_id = models.ForeignKey(
        SerieClassificacao,
        on_delete=models.PROTECT,
        related_name='classificacoes',
        db_column='serie_id',
        verbose_name='Série de Classificações',
        help_text='Referência à série de classificações à qual esta classificação pertence',
    )
    classificacao_nome = models.CharField(
        max_length=255,
        verbose_name='Nome da Classificação',
        help_text='Nome oficial da classificação estatística.'
    )
    descricao = models.TextField(
        blank=True,
        verbose_name='Descrição',
        help_text='Descrição detalhada da classificação, seu propósito e escopo'
    )
    tipo_classificacao = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default=TIPO_HIERARQUICA,
        verbose_name='Tipo de Classificação',
        help_text='Tipo da classificação (hierárquica ou linear)'
    )
    numero_niveis = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(9)],
        verbose_name='Número de Níveis',
        help_text='Número de níveis hierárquicos da classificação. Para o Classificador de Receita MG, o valor é 9.'
    )
    numero_digitos = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        verbose_name='Número de Dígitos do Código',
        help_text=(
            'Quantidade total de dígitos do código na classificação (ex.: 8 para a base União, '
            '10 ou 13 para MG conforme a edição).'
        ),
    )
    base_legal_tecnica_id = models.ForeignKey(
        BaseLegalTecnica,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='classificacoes_relacionadas',
        db_column='base_legal_tecnica_id',
        verbose_name='Base Legal/Técnica de Referência',
        help_text=(
            'Identificador da norma ou ato que institui ou altera esta classificação, quando aplicável. '
            'Referência à tabela base_legal_tecnica. Opcional; pode ficar em branco quando a classificação '
            'decorre de múltiplas normas ou de convenção interna.'
        ),
    )

    class Meta:
        db_table = 'classificacao'
        verbose_name = 'Classificação de Receita'
        verbose_name_plural = 'Classificações de Receita'
        constraints = [
            models.UniqueConstraint(
                fields=['classificacao_id', 'data_vigencia_inicio', 'data_registro_inicio'],
                name='unique_classificacao_registro'
            ),
            models.UniqueConstraint(
                fields=['classificacao_ref', 'data_vigencia_inicio', 'data_registro_inicio'],
                name='unique_classificacao_ref_registro',
            ),
        ]
        indexes = [
            models.Index(
                fields=['classificacao_id', 'data_registro_fim'],
                name='idx_classificacao_registro_fim',
            ),
            models.Index(
                fields=['serie_id', 'data_vigencia_inicio'],
                name='idx_classif_serie_vig',
            ),
        ]

    def __str__(self):
        return f"{self.classificacao_nome} ({self.classificacao_id})"


class NivelHierarquico(BitemporalModel):
    """
    Nível Hierárquico (GSIM ClassificationLevel).

    Responsável por retratar o EIXO hierárquico da classificação com respectiva quantidade de dígitos.

    Define cada nível da hierarquia da classificação.
    """
    TIPO_NUMERICO = 'numérico'
    TIPO_ALFABETICO = 'alfabético'
    TIPO_ALFANUMERICO = 'alfanumérico'
    TIPO_CODIGO_CHOICES = [
        (TIPO_NUMERICO, 'Numérico'),
        (TIPO_ALFABETICO, 'Alfabético'),
        (TIPO_ALFANUMERICO, 'Alfanumérico'),
    ]

    nivel_id = models.CharField(
        max_length=100,
        verbose_name='Identificador do Nível',
        help_text='Identificador único do nível hierárquico (chave semântica).',
        db_index=True
    )
    nivel_ref = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Referência Numérica do Nível',
        help_text=(
            'Identificador numérico estável do nível hierárquico, usado na chave primária lógica '
            '(bitemporal). Mesmo valor para todas as linhas que pertencem ao mesmo nível '
            'conceitual (mesmo nivel_id).'
        ),
    )
    # Schema expõe `classificacao_id` como campo de referência; usamos o mesmo nome aqui
    # para alinhar com o Table Schema. O `db_column` garante que a coluna física se chame
    # exatamente `classificacao_id`, mantendo compatibilidade com o recurso Frictionless.
    classificacao_id = models.ForeignKey(
        Classificacao,
        on_delete=models.PROTECT,
        related_name='niveis',
        db_column='classificacao_id',
        verbose_name='Classificação',
        help_text='Referência à classificação estatística à qual este nível pertence',
    )
    nivel_numero = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(9)],
        verbose_name='Número do Nível',
        help_text='Número sequencial do nível na hierarquia, começando em 1 para o nível mais agregado'
    )
    nivel_nome = models.CharField(
        max_length=255,
        verbose_name='Nome do Nível',
        help_text='Nome do nível hierárquico (ex: "Categoria Econômica", "Origem", "Espécie")'
    )
    descricao = models.TextField(
        blank=True,
        verbose_name='Descrição',
        help_text='Descrição detalhada do nível, seu propósito e conteúdo'
    )
    estrutura_codigo = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Estrutura do Código',
        help_text='Padrão de estrutura do código neste nível (ex: "C", "C.O", "C.O.E")'
    )
    numero_digitos = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(9)],
        verbose_name='Número de Dígitos',
        help_text='Quantidade de dígitos do código neste nível.',
    )
    tipo_codigo = models.CharField(
        max_length=20,
        choices=TIPO_CODIGO_CHOICES,
        default=TIPO_NUMERICO,
        verbose_name='Tipo de Código',
        help_text='Tipo do código no nível (numérico, alfabético, alfanumérico)'
    )

    class Meta:
        db_table = 'nivel_hierarquico'
        verbose_name = 'Nível Hierárquico'
        verbose_name_plural = 'Níveis Hierárquicos'
        constraints = [
            models.UniqueConstraint(
                fields=['nivel_id', 'data_vigencia_inicio', 'data_registro_inicio'],
                name='unique_nivel_registro',
            ),
            models.UniqueConstraint(
                fields=['classificacao_id', 'nivel_numero', 'data_vigencia_inicio', 'data_registro_inicio'],
                name='unq_nivel_numero_classif',
            ),
            models.UniqueConstraint(
                fields=['nivel_ref', 'data_vigencia_inicio', 'data_registro_inicio'],
                name='unique_nivel_ref_registro',
            ),
        ]
        indexes = [
            models.Index(
                fields=['nivel_id', 'data_registro_fim'],
                name='idx_nivel_registro_fim',
            ),
            models.Index(
                fields=['classificacao_id', 'nivel_numero'],
                name='idx_nivel_classificacao_numero',
            ),
        ]

    def __str__(self):
        return f"Nível {self.nivel_numero}: {self.nivel_nome} ({self.nivel_id})"


class ItemClassificacao(BitemporalModel):
    """
    Item de Classificação (GSIM ClassificationItem)

    Representam a CODIFICAÇÃO propriamente dita do ementário/classificador. 
    
    Cada código é um item dessa tabela. Respode quais são os códigos de cada nível do classificador.
    
    """
    item_id = models.CharField(
        max_length=100,
        verbose_name='Identificador do Item',
        help_text='Identificador único do item de classificação',
        db_index=True,
    )
    item_ref = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Referência Numérica do Item',
        help_text=(
            'Identificador numérico estável do item, usado na chave primária lógica (bitemporal). '
            'Mesmo valor para todas as linhas que pertencem à mesma entidade (mesmo item_id).'
        ),
    )
    # Schema expõe `classificacao_id` como campo de referência; usamos o mesmo nome aqui
    # para alinhar com o Table Schema. O `db_column` garante que a coluna física se chame
    # exatamente `classificacao_id`, mantendo compatibilidade com o recurso Frictionless.
    classificacao_id = models.ForeignKey(
        Classificacao,
        on_delete=models.PROTECT,
        related_name='itens',
        db_column='classificacao_id',
        null=False,
        blank=False,
        verbose_name='Classificação',
        help_text='Referência à classificação estatística à qual este item pertence',
    )
    receita_cod = models.CharField(
        max_length=13,
        null=False,
        blank=False,
        verbose_name='Código Canônico da Natureza de Receita',
        help_text=(
            'Código numérico canônico da natureza de receita orçamentária'
        ),
        db_index=True,
        validators=[RegexValidator(regex=r'^[0-9]{8,13}$', message='receita_cod must be 8-13 digits')],
    )
    matriz = models.BooleanField(
        default=False,
        verbose_name='Identificador de Matriz',
        help_text=(
            'Indica se o item é natureza agregadora (Matriz) ou item folha (Detalhe). '
            'Quando true, indica item agregador; quando false, item detalhe em que a '
            'execução orçamentária pode ser registrada.'
        ),
    )
    receita_nome = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name='Nome da Classificação por Natureza de Receita',
        help_text=(
            'Nome da natureza de receita orçamentária, baseado no fato gerador para rotular a origem '
            'e o tipo do recurso que ingressa nos cofres públicos.'
        ),
    )
    receita_descricao = models.TextField(
        null=True,
        blank=True,
        verbose_name='Descrição da Natureza de Receita',
        help_text=(
            'Texto descritivo que complementa o nome, esclarecendo significado, escopo e finalidade '
            'da natureza de receita, incluindo detalhes de conceito, abrangência e casos limítrofes.'
        ),
    )
    base_legal_tecnica_id = models.ForeignKey(
        BaseLegalTecnica,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='itens_classificacao_relacionados',
        db_column='base_legal_tecnica_id',
        verbose_name='Base Legal/Técnica de Referência',
        help_text=(
            'Identificador da norma ou ato que institui ou altera esta natureza de receita, quando aplicável. '
            'Referência à tabela base_legal_tecnica. Opcional; pode ficar em branco quando a natureza de receita '
            'decorre de múltiplas normas ou de convenção interna.'
        ),
    )
    base_legal_tecnica_referencia = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Referência ao Excerto da Base Legal/Técnica',
        help_text=(
            'Trecho específico da base legal/técnica (ex.: artigo, parágrafo, inciso, anexo, item), '
            'quando a fundamentação não é a norma como um todo. Ex.: "Art. 8º, § 1º".'
        ),
    )
    destinacao_legal = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name='Destinação Legal',
        help_text=(
            'Indicação da destinação ou vinculação legal aplicável à receita classificada neste item, ' 
            'quando a norma estabelece regras de aplicação (ex.: percentual para educação, saúde, fundos).'
        ),
    )
    informacoes_gerenciais = models.TextField(
        null=True,
        blank=True,
        verbose_name='Informações Gerenciais',
        help_text=(
            'Detalhes técnicos e operacionais sobre o contexto de criação/aplicação da natureza de receita: '
            'critérios de uso, integrações (ex.: SISOR), notas de implementação, decisões de governança.'
        ),
    )
    # Schema expõe `nivel_id` como campo de referência; usamos o mesmo nome aqui
    # para alinhar com o Table Schema. O `db_column` garante que a coluna física se chame
    # exatamente `nivel_id`, mantendo compatibilidade com o recurso Frictionless.
    nivel_id = models.ForeignKey(
        NivelHierarquico,
        on_delete=models.PROTECT,
        related_name='itens',
        db_column='nivel_id',
        verbose_name='Nível Hierárquico',
        help_text='Referência ao nível hierárquico ao qual este item pertence',
    )
    parent_item_id = models.ForeignKey(
        'self',
        on_delete=models.PROTECT,
        related_name='sub_itens',
        db_column='parent_item_id',
        verbose_name='Item Pai',
        help_text='Referência ao item do nível imediatamente superior na hierarquia. NULL para itens do nível 1.',
        null=True,
        blank=True,
    )
    # Allow NULL in DB for root items; business rules enforced in `clean()`.
    # Note: migrations must be created to apply this change to the database.
    item_gerado = models.BooleanField(
        default=False,
        verbose_name='Item Gerado Automaticamente',
        help_text=(
            'Indica se o item existe por regra (gerado automaticamente a partir de uma agregadora) '
            'ou se consta explicitamente no ementário oficial.'
        ),
    )

    class Meta:
        db_table = 'item_classificacao'
        verbose_name = 'Item de Classificação'
        verbose_name_plural = 'Itens de Classificação'
        constraints = [
            models.UniqueConstraint(
                fields=['item_id', 'data_vigencia_inicio', 'data_registro_inicio'],
                name='unique_item_registro'
            ),
            models.UniqueConstraint(
                fields=['item_ref', 'data_vigencia_inicio', 'data_registro_inicio'],
                name='unique_item_ref_registro'
            ),
            models.UniqueConstraint(
                fields=['receita_cod', 'data_vigencia_inicio', 'data_registro_inicio'],
                name='unique_receita_cod_registro'
            ),
        ]
        indexes = [
            models.Index(fields=['item_id', 'data_registro_fim'], name='idx_item_registro_fim'),
            models.Index(fields=['receita_cod', 'data_registro_fim'], name='idx_item_codigo_registro_fim'),
            models.Index(fields=['nivel_id', 'data_vigencia_inicio'], name='idx_item_nivel_vigencia'),
            models.Index(fields=['parent_item_id'], name='idx_item_parent'),
        ]

    def __str__(self):
        codigo = self.receita_cod or self.item_id or ''
        nome = self.receita_nome or self.item_id or ''
        return f"{codigo} - {nome}"

    def clean(self):
        """
        Garante integridade hierárquica:

        - Itens de nível 1 (raiz) DEVEM ter parent_item_id nulo.
        - Itens de nível 2+ DEVEM ter parent_item_id preenchido.
        """
        super().clean()

        # Se não houver nível associado, deixamos a validação para outros pontos (schema já exige nivel_id).
        if not self.nivel_id:
            return

        nivel = self.nivel_id

        # Nível 1: não pode ter pai
        if nivel.nivel_numero == 1 and self.parent_item_id is not None:
            raise ValidationError(
                {'parent_item_id': 'Itens de nível 1 (raiz) não devem possuir item pai.'}
            )

        # Níveis acima de 1: precisam ter pai
        if nivel.nivel_numero > 1 and self.parent_item_id is None:
            raise ValidationError(
                {'parent_item_id': 'Itens de nível superior a 1 devem possuir um item pai.'}
            )

    def save(self, *args, _skip_validation: bool = False, **kwargs):
        """
        Override save to run model validation by default. Pass `_skip_validation=True`
        from trusted importers/loaders when inserting seed data to avoid DB-level
        validation during bulk loads. Business rules remain enforced for normal app flows.
        """
        if not _skip_validation:
            self.full_clean()
        super().save(*args, **kwargs)


class VersaoClassificacao(BitemporalModel):
    """
    Versão da Classificação (GSIM ClassificationVersion)

    Versão da classificação para mudanças que alteram fronteiras conceituais entre categorias.
    """
    versao_ref = models.IntegerField(
        null=False,
        blank=False,
        verbose_name='Referência Numérica da Versão',
        help_text=(
            'Identificador numérico estável da versão, usado na chave primária lógica (bitemporal). '
            'Mesmo valor para todas as linhas que pertencem à mesma entidade (mesmo versao_id).'
        ),
    )
    versao_id = models.CharField(
        max_length=100,
        verbose_name='Identificador da Versão',
        help_text='Identificador único da versão da classificação',
        db_index=True
    )
    classificacao = models.ForeignKey(
        Classificacao,
        on_delete=models.PROTECT,
        related_name='versoes',
        verbose_name='Classificação',
        help_text='Referência à classificação estatística à qual esta versão pertence'
    )
    versao_numero = models.CharField(
        max_length=50,
        verbose_name='Número da Versão',
        help_text='Número ou identificador da versão (ex: "2024", "v1.0")'
    )
    versao_nome = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Nome da Versão',
        help_text='Nome descritivo da versão'
    )
    descricao = models.TextField(
        blank=True,
        verbose_name='Descrição',
        help_text='Descrição das mudanças e características desta versão. Versões são reservadas para mudanças que alteram fronteiras conceituais entre categorias.'
    )
    data_lancamento = models.DateField(
        null=True,
        blank=True,
        verbose_name='Data de Lançamento',
        help_text='Data oficial de lançamento/publicação da versão'
    )

    class Meta:
        db_table = 'versao_classificacao'
        verbose_name = 'Versão da Classificação'
        verbose_name_plural = 'Versões da Classificação'
        constraints = [
            models.UniqueConstraint(
                fields=['versao_id', 'data_vigencia_inicio', 'data_registro_inicio'],
                name='unique_versao_registro'
            ),
            models.UniqueConstraint(
                fields=['versao_ref', 'data_vigencia_inicio', 'data_registro_inicio'],
                name='unique_versao_ref_registro',
            ),
        ]
        indexes = [
            models.Index(fields=['versao_id', 'data_registro_fim'], name='idx_versao_registro_fim'),
            models.Index(fields=['classificacao', 'data_vigencia_inicio'], name='idx_versao_classif_vig'),
        ]

    def __str__(self):
        return f"{self.versao_nome or self.versao_numero} ({self.versao_id})"


class VarianteClassificacao(BitemporalModel):
    """
    Variante de Classificação (GSIM ClassificationVariant)

    Variante da classificação para extensões, agregações e reagrupamentos.
    """
    TIPO_EXTENSAO = 'extensão'
    TIPO_AGREGACAO = 'agregação'
    TIPO_REAGRUPAMENTO = 'reagrupamento'
    TIPO_OUTRO = 'outro'
    TIPO_CHOICES = [
        (TIPO_EXTENSAO, 'Extensão'),
        (TIPO_AGREGACAO, 'Agregação'),
        (TIPO_REAGRUPAMENTO, 'Reagrupamento'),
        (TIPO_OUTRO, 'Outro'),
    ]

    variante_id = models.CharField(
        max_length=100,
        verbose_name='Identificador da Variante',
        help_text='Identificador único da variante de classificação',
        db_index=True
    )
    classificacao = models.ForeignKey(
        Classificacao,
        on_delete=models.PROTECT,
        related_name='variantes',
        verbose_name='Classificação de Origem',
        help_text='Referência à classificação estatística na qual esta variante se baseia'
    )
    versao = models.ForeignKey(
        VersaoClassificacao,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='variantes',
        verbose_name='Versão de Origem',
        help_text='Referência à versão da classificação na qual esta variante se baseia'
    )
    variante_nome = models.CharField(
        max_length=255,
        verbose_name='Nome da Variante',
        help_text='Nome descritivo da variante'
    )
    tipo_variante = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        verbose_name='Tipo de Variante',
        help_text='Tipo da variante (extensão, agregação, reagrupamento, outro)'
    )
    descricao = models.TextField(
        blank=True,
        verbose_name='Descrição',
        help_text='Descrição detalhada da variante, seu propósito e diferenças em relação à classificação de origem'
    )
    proposito = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Propósito',
        help_text='Propósito específico da variante (ex: "relatório específico", "norma estadual")'
    )

    class Meta:
        db_table = 'variante_classificacao'
        verbose_name = 'Variante de Classificação'
        verbose_name_plural = 'Variantes de Classificação'
        constraints = [
            models.UniqueConstraint(
                fields=['variante_id', 'data_vigencia_inicio', 'data_registro_inicio'],
                name='unique_variante_registro'
            )
        ]
        indexes = [
            models.Index(fields=['variante_id', 'data_registro_fim'], name='idx_variante_registro_fim'),
            models.Index(fields=['classificacao', 'data_vigencia_inicio'], name='idx_variante_classif_vig'),
        ]

    def __str__(self):
        return f"{self.variante_nome} ({self.variante_id})"
