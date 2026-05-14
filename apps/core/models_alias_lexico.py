"""
Catálogo de abreviações léxicas para nomenclatura de itens de classificação (radical do pai).

Somente transaction time (registro); vigência orçamentária não se aplica aqui.
Alinhado ao uso de sentinela em ``TRANSACTION_TIME_SENTINEL`` (ADR-001).
"""

import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower
from django.utils import timezone

from apps.core.alias_lexico_termo_policy import termo_nome_rejeitado_encurtamento_iv


_TRANSACTION_SENTINEL = datetime.datetime(9999, 12, 31, 0, 0, 0)


def lista_abreviacoes_registro_inicio_novo() -> datetime.datetime:
    """
    Spec ``_dev/spec_lista_abreviacoes.md`` *(L)*: ``data_registro_início`` = 01/01/<ano civil corrente>
    às 00:00:00 na timezone actual do Django.
    """
    y = timezone.localdate().year
    return timezone.make_aware(
        datetime.datetime(y, 1, 1, 0, 0, 0),
        timezone.get_current_timezone(),
    )


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
        help_text=(
            "Forma completa a partir da qual se deriva a abreviação. "
            "Único na tabela em sentido semântico (case-insensitive; ativa ou inativa em transaction time)."
        ),
    )
    abreviacao = models.CharField(
        max_length=256,
        verbose_name="Abreviação",
        help_text="Forma curta sugerida correspondente ao termo.",
    )
    data_registro_inicio = models.DateTimeField(
        default=lista_abreviacoes_registro_inicio_novo,
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
        constraints = [
            UniqueConstraint(
                Lower("termo"),
                name="unique_lista_abrev_termo_ci",
            ),
        ]
        indexes = [
            models.Index(fields=["data_registro_fim"], name="idx_lista_abrev_reg_fim"),
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
        if termo_nome_rejeitado_encurtamento_iv(t):
            raise ValidationError(
                {
                    "termo": (
                        "O termo não pode conter token de abreviação por encurtamento no sentido (iv) "
                        "(ex.: «Contrib.»). Use a forma por extenso (ex.: «Contribuição Patronal»)."
                    )
                }
            )
        dup = AliasLexico.objects.filter(termo__iexact=t)
        if self.pk:
            dup = dup.exclude(pk=self.pk)
        if dup.exists():
            raise ValidationError(
                {
                    "termo": (
                        "Já existe uma entrada com o mesmo termo (unicidade semântica, "
                        "sem distinção de maiúsculas/minúsculas)."
                    )
                }
            )
        ini = self.data_registro_inicio
        fim = self.data_registro_fim
        if ini and fim and ini > fim:
            raise ValidationError(
                {"data_registro_fim": "Data de fim do registro deve ser posterior ao início."}
            )
