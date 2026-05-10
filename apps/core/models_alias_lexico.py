"""
Catálogo de abreviações léxicas para nomenclatura de itens de classificação (radical do pai).

Somente transaction time (registro); vigência orçamentária não se aplica aqui.
Alinhado ao uso de sentinela em ``TRANSACTION_TIME_SENTINEL`` (ADR-001).
"""

import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


_TRANSACTION_SENTINEL = datetime.datetime(9999, 12, 31, 0, 0, 0)


class AliasLexico(models.Model):
    """
    Mapeamento termo completo → forma abreviada, com controle de vigência do registro.
    """

    alias_lexico_ref = models.PositiveIntegerField(
        unique=True,
        verbose_name="Referência numérica",
        help_text="Identificador estável da entrada (chave de negócio; não altera após a criação).",
    )
    termo = models.CharField(
        max_length=512,
        verbose_name="Termo",
        help_text="Forma completa a partir da qual se deriva a abreviação.",
    )
    abreviacao = models.CharField(
        max_length=256,
        verbose_name="Abreviação",
        help_text="Forma curta sugerida correspondente ao termo.",
    )
    data_registro_inicio = models.DateTimeField(
        default=timezone.now,
        verbose_name="Data de início do registro",
        help_text="Momento em que esta linha passou a valer no sistema.",
    )
    data_registro_fim = models.DateTimeField(
        default=_TRANSACTION_SENTINEL,
        verbose_name="Data de fim do registro",
        help_text=(
            "Momento em que a entrada deixa de ser usada. Valor sentinela 31/12/9999 indica registro ativo."
        ),
    )

    class Meta:
        db_table = "lista_abreviacoes"
        verbose_name = "Abreviação léxica"
        verbose_name_plural = "Lista de Abreviações"
        ordering = ("termo", "data_registro_inicio")
        indexes = [
            models.Index(fields=["data_registro_fim"], name="idx_lista_abrev_reg_fim"),
            models.Index(fields=["termo"], name="idx_lista_abrev_termo"),
        ]

    def __str__(self):
        esq = self.termo if len(self.termo) <= 60 else self.termo[:57] + "…"
        dir_ = self.abreviacao if len(self.abreviacao) <= 40 else self.abreviacao[:37] + "…"
        return f"{esq} → {dir_}"

    def clean(self):
        super().clean()
        t = (self.termo or "").strip()
        a = (self.abreviacao or "").strip()
        if not t:
            raise ValidationError({"termo": "Informe o termo completo."})
        if not a:
            raise ValidationError({"abreviacao": "Informe a abreviação."})
        ini = self.data_registro_inicio
        fim = self.data_registro_fim
        if ini and fim and ini > fim:
            raise ValidationError(
                {"data_registro_fim": "Data de fim do registro deve ser posterior ao início."}
            )
