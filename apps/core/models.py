from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError


# Constantes para valores sentinelas (conforme ADR-001)
VALID_TIME_SENTINEL = '9999-12-31'
TRANSACTION_TIME_SENTINEL = '9999-12-31 23:59:59'


class BitemporalModel(models.Model):
    """
    Classe base abstrata para models bitemporais.
    
    Implementa os campos de valid_time (vigência) e transaction_time (registro)
    conforme ADR-001 - Estratégia de Bitemporalidade.
    
    Todos os models do classificador herdam desta classe base.
    """
    data_vigencia_inicio = models.DateField(
        verbose_name='Data de Início da Vigência',
        help_text='Data de início da vigência no domínio orçamentário (valid_time - início)'
    )
    data_vigencia_fim = models.DateField(
        verbose_name='Data de Fim da Vigência',
        help_text='Data de fim da vigência (valid_time - fim). Valor sentinela 9999-12-31 indica vigência ativa.'
    )
    data_registro_inicio = models.DateTimeField(
        verbose_name='Data/Hora de Registro Início',
        help_text='Data e hora em que o sistema registrou esta informação (transaction_time - início)'
    )
    data_registro_fim = models.DateTimeField(
        verbose_name='Data/Hora de Registro Fim',
        help_text='Data e hora em que esta informação deixou de ser considerada verdadeira pelo sistema (transaction_time - fim). Valor sentinela 9999-12-31 23:59:59 indica registro ativo.'
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
    Série de Classificações (GSIM ClassificationSeries)
    
    Agrupa classificações relacionadas ao mesmo domínio ao longo do tempo.
    """
    serie_id = models.CharField(
        max_length=100,
        verbose_name='Identificador da Série',
        help_text='Identificador único da série de classificações (GSIM ClassificationSeries.identifier)',
        db_index=True
    )
    serie_nome = models.CharField(
        max_length=255,
        verbose_name='Nome da Série',
        help_text='Nome oficial da série de classificações (GSIM ClassificationSeries.name)'
    )
    descricao = models.TextField(
        blank=True,
        verbose_name='Descrição',
        help_text='Descrição detalhada da série de classificações e seu propósito'
    )
    orgao_responsavel = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Órgão Responsável',
        help_text='Órgão ou entidade responsável pela manutenção da série de classificações'
    )

    class Meta:
        db_table = 'serie_classificacao'
        verbose_name = 'Série de Classificações'
        verbose_name_plural = 'Séries de Classificações'
        constraints = [
            models.UniqueConstraint(
                fields=['serie_id', 'data_registro_inicio'],
                name='unique_serie_registro'
            )
        ]
        indexes = [
            models.Index(fields=['serie_id', 'data_registro_fim'], name='idx_serie_registro_fim'),
            models.Index(fields=['data_vigencia_inicio', 'data_vigencia_fim'], name='idx_serie_vigencia'),
        ]

    def __str__(self):
        return f"{self.serie_nome} ({self.serie_id})"


class ClassificacaoReceita(BitemporalModel):
    """
    Classificação Estatística (GSIM StatisticalClassification)
    
    Uma classificação estatística específica, válida para um período específico.
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
        help_text='Identificador único da classificação estatística (GSIM StatisticalClassification.identifier)',
        db_index=True
    )
    serie = models.ForeignKey(
        SerieClassificacao,
        on_delete=models.PROTECT,
        related_name='classificacoes',
        verbose_name='Série de Classificações',
        help_text='Referência à série de classificações à qual esta classificação pertence'
    )
    classificacao_nome = models.CharField(
        max_length=255,
        verbose_name='Nome da Classificação',
        help_text='Nome oficial da classificação estatística (GSIM StatisticalClassification.name)'
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

    class Meta:
        db_table = 'classificacao_receita'
        verbose_name = 'Classificação de Receita'
        verbose_name_plural = 'Classificações de Receita'
        constraints = [
            models.UniqueConstraint(
                fields=['classificacao_id', 'data_registro_inicio'],
                name='unique_classificacao_registro'
            )
        ]
        indexes = [
            models.Index(fields=['classificacao_id', 'data_registro_fim'], name='idx_classificacao_registro_fim'),
            models.Index(fields=['serie', 'data_vigencia_inicio'], name='idx_classificacao_serie_vigencia'),
        ]

    def __str__(self):
        return f"{self.classificacao_nome} ({self.classificacao_id})"


class NivelHierarquico(BitemporalModel):
    """
    Nível Hierárquico (GSIM ClassificationLevel)
    
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
        help_text='Identificador único do nível hierárquico (GSIM ClassificationLevel.identifier)',
        db_index=True
    )
    classificacao = models.ForeignKey(
        ClassificacaoReceita,
        on_delete=models.PROTECT,
        related_name='niveis',
        verbose_name='Classificação',
        help_text='Referência à classificação estatística à qual este nível pertence'
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
                fields=['nivel_id', 'data_registro_inicio'],
                name='unique_nivel_registro'
            ),
            models.UniqueConstraint(
                fields=['classificacao', 'nivel_numero', 'data_registro_inicio'],
                name='unique_nivel_numero_classificacao'
            )
        ]
        indexes = [
            models.Index(fields=['nivel_id', 'data_registro_fim'], name='idx_nivel_registro_fim'),
            models.Index(fields=['classificacao', 'nivel_numero'], name='idx_nivel_classificacao_numero'),
        ]

    def __str__(self):
        return f"Nível {self.nivel_numero}: {self.nivel_nome} ({self.nivel_id})"


class ItemClassificacao(BitemporalModel):
    """
    Item de Classificação (GSIM ClassificationItem)
    
    Cada código/item da classificação, representando uma categoria em um nível específico.
    """
    item_id = models.CharField(
        max_length=100,
        verbose_name='Identificador do Item',
        help_text='Identificador único do item de classificação',
        db_index=True
    )
    codigo_completo = models.CharField(
        max_length=50,
        verbose_name='Código Completo',
        help_text='Código completo formatado (ex: "1.0.1.1.01.1.1.01.001")',
        db_index=True
    )
    codigo_numerico = models.BigIntegerField(
        validators=[MinValueValidator(1000000000000), MaxValueValidator(9999999999999)],
        verbose_name='Código Numérico',
        help_text='Código numérico de 13 dígitos sem formatação',
        db_index=True
    )
    nivel = models.ForeignKey(
        NivelHierarquico,
        on_delete=models.PROTECT,
        related_name='itens',
        verbose_name='Nível Hierárquico',
        help_text='Referência ao nível hierárquico ao qual este item pertence'
    )
    parent_item = models.ForeignKey(
        'self',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='sub_itens',
        verbose_name='Item Pai',
        help_text='Referência ao item do nível imediatamente superior na hierarquia. NULL para itens do nível 1.'
    )
    nome_oficial = models.CharField(
        max_length=500,
        verbose_name='Nome Oficial',
        help_text='Nome oficial do item de classificação'
    )
    descricao = models.TextField(
        blank=True,
        verbose_name='Descrição',
        help_text='Descrição detalhada do item de classificação'
    )
    item_gerado = models.BooleanField(
        default=False,
        verbose_name='Item Gerado',
        help_text='Indica se o item foi gerado automaticamente para completar o nível'
    )
    valido_atualmente = models.BooleanField(
        default=True,
        verbose_name='Válido Atualmente',
        help_text='Indica se o item está atualmente válido na classificação'
    )

    class Meta:
        db_table = 'item_classificacao'
        verbose_name = 'Item de Classificação'
        verbose_name_plural = 'Itens de Classificação'
        constraints = [
            models.UniqueConstraint(
                fields=['item_id', 'data_registro_inicio'],
                name='unique_item_registro'
            ),
            models.UniqueConstraint(
                fields=['codigo_numerico', 'data_registro_inicio'],
                name='unique_codigo_numerico_registro'
            )
        ]
        indexes = [
            models.Index(fields=['item_id', 'data_registro_fim'], name='idx_item_registro_fim'),
            models.Index(fields=['codigo_numerico', 'data_registro_fim'], name='idx_item_codigo_registro_fim'),
            models.Index(fields=['nivel', 'data_vigencia_inicio'], name='idx_item_nivel_vigencia'),
            models.Index(fields=['parent_item'], name='idx_item_parent'),
        ]

    def __str__(self):
        return f"{self.codigo_completo} - {self.nome_oficial}"


class VersaoClassificacao(BitemporalModel):
    """
    Versão da Classificação (GSIM ClassificationVersion)
    
    Versão da classificação para mudanças que alteram fronteiras conceituais entre categorias.
    """
    versao_id = models.CharField(
        max_length=100,
        verbose_name='Identificador da Versão',
        help_text='Identificador único da versão da classificação',
        db_index=True
    )
    classificacao = models.ForeignKey(
        ClassificacaoReceita,
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
                fields=['versao_id', 'data_registro_inicio'],
                name='unique_versao_registro'
            )
        ]
        indexes = [
            models.Index(fields=['versao_id', 'data_registro_fim'], name='idx_versao_registro_fim'),
            models.Index(fields=['classificacao', 'data_vigencia_inicio'], name='idx_versao_classificacao_vigencia'),
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
        ClassificacaoReceita,
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
                fields=['variante_id', 'data_registro_inicio'],
                name='unique_variante_registro'
            )
        ]
        indexes = [
            models.Index(fields=['variante_id', 'data_registro_fim'], name='idx_variante_registro_fim'),
            models.Index(fields=['classificacao', 'data_vigencia_inicio'], name='idx_variante_classificacao_vigencia'),
        ]

    def __str__(self):
        return f"{self.variante_nome} ({self.variante_id})"
