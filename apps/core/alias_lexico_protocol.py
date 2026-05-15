"""
Protocolo da lista de abreviações: inserção idempotente e vigência orçamentária (ItemClassificacao).

Única convenção para comparar ``DateField`` de vigência com instante ``T`` (``datetime``, UTC).
"""

from __future__ import annotations

from datetime import date, datetime, timezone as dt_timezone

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone as django_timezone

from apps.core.models_alias_lexico import AliasLexico


def calendar_date_utc(instant: datetime) -> date:
    """
    Data civil em UTC correspondente ao instante (para cruzar com ``DateField`` de vigência).
    ``instant`` ingénuo é interpretado na timezone atual do Django antes de converter a UTC.
    """
    if django_timezone.is_naive(instant):
        instant = django_timezone.make_aware(instant, django_timezone.get_current_timezone())
    return instant.astimezone(dt_timezone.utc).date()


def budget_period_contains_instant(
    data_vigencia_inicio: date | None,
    data_vigencia_fim: date | None,
    instant: datetime,
) -> bool:
    """
    True if ``data_vigencia_inicio <= d <= data_vigencia_fim`` with ``d`` the UTC calendar date of
    ``instant``, **inclusive** on both ends (budget-period / vigência orçamentária semantics).
    """
    if data_vigencia_inicio is None or data_vigencia_fim is None:
        return False
    d = calendar_date_utc(instant)
    return data_vigencia_inicio <= d <= data_vigencia_fim


def insert_alias_lexico_if_new(
    *,
    termo_viii_exempt: bool = False,
    **kwargs,
) -> tuple[bool, AliasLexico | None]:
    """
    Tenta ``INSERT`` de ``AliasLexico``. Duplicata de ``termo`` (unicidade **case-insensitive** no BD)
    resulta em ``(False, None)`` — equivalente a “não houve insert” para efeitos de export (ii).

    ``ValidationError`` em ``full_clean()`` (incl. **(viii)** do termo) resulta em ``(False, None)``,
    salvo ``termo_viii_exempt=True`` (ex.: Regra 1.2 — ``receita_nome`` integral da mãe).

    Usa ``transaction.atomic`` interno para isolar ``IntegrityError`` sem abortar a transação exterior.
    """
    obj = AliasLexico(**kwargs)
    if termo_viii_exempt:
        obj._skip_termo_viii_check = True
    try:
        obj.full_clean()
    except ValidationError:
        return False, None
    try:
        with transaction.atomic():
            obj.save()
    except IntegrityError:
        return False, None
    return True, obj
