"""
Detecção de conflito por código canônico já existente (admin add).

Ver ``_dev/spec_itemClassificacao_criar_codigo_existente.md`` (CE / CE★).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Dict, Optional

from django.urls import reverse

from apps.core.admin_formatters import format_receita_cod_by_vigencia
from apps.core.admin_mixins import transaction_time_sentinel_for_query
from apps.core.item_classificacao_code_lookup import normalize_receita_cod_digits
from apps.core.models import ItemClassificacao


@dataclass(frozen=True)
class ExistingCodeConflict:
    """Registro ativo (CE★) em conflito de vigência com o formulário."""

    pk: str
    receita_cod: str
    receita_cod_display: str
    display_label: str
    link_url: str
    vigencia_inicio: date
    vigencia_fim: date


def vigencia_intervals_overlap(
    ini_a: Optional[date],
    fim_a: Optional[date],
    ini_b: Optional[date],
    fim_b: Optional[date],
) -> bool:
    """Sobreposição inclusiva (T7): ``ini_a <= fim_b`` e ``fim_a >= ini_b``."""
    if not ini_a or not fim_a or not ini_b or not fim_b:
        return False
    return ini_a <= fim_b and fim_a >= ini_b


def queryset_active_receita_cod_overlapping_vigencia(
    receita_cod_digits: str,
    vigencia_inicio: date,
    vigencia_fim: date,
):
    """
    Itens ativos com o mesmo ``receita_cod`` e vigência sobreposta ao intervalo informado.

    Ordenação CE★: ``-data_vigencia_inicio``, ``-data_registro_inicio``, ``-pk``.
    """
    reg_sent = transaction_time_sentinel_for_query()
    return (
        ItemClassificacao.objects.filter(
            receita_cod=receita_cod_digits,
            data_registro_fim=reg_sent,
            data_vigencia_inicio__lte=vigencia_fim,
            data_vigencia_fim__gte=vigencia_inicio,
        )
        .order_by("-data_vigencia_inicio", "-data_registro_inicio", "-pk")
    )


def resolve_existing_code_conflict(
    receita_cod: Optional[str],
    vigencia_inicio: Optional[date],
    vigencia_fim: Optional[date],
) -> Optional[ExistingCodeConflict]:
    """
    Retorna CE★ quando há conflito (CE); caso contrário ``None``.

    Entrada inválida (código vazio ou vigência incompleta) → ``None``.
    """
    code = normalize_receita_cod_digits(receita_cod)
    if not code or not vigencia_inicio or not vigencia_fim:
        return None
    if vigencia_fim < vigencia_inicio:
        return None

    obj = queryset_active_receita_cod_overlapping_vigencia(
        code,
        vigencia_inicio,
        vigencia_fim,
    ).first()
    if not obj:
        return None

    return _conflict_from_item(obj, form_vigencia_inicio=vigencia_inicio, form_vigencia_fim=vigencia_fim)


def _conflict_from_item(
    obj: ItemClassificacao,
    *,
    form_vigencia_inicio: date,
    form_vigencia_fim: date,
) -> ExistingCodeConflict:
    v_ini = obj.data_vigencia_inicio
    v_fim = obj.data_vigencia_fim
    cod = obj.receita_cod or ""
    try:
        link_url = reverse(
            f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change",
            args=[obj.pk],
        )
    except Exception:
        link_url = ""

    cod_display = format_receita_cod_by_vigencia(
        cod,
        form_vigencia_inicio,
        form_vigencia_fim,
        {},
    )
    nome = obj.receita_nome or obj.item_id or ""
    display_label = f"{cod} - {nome}".strip(" -")

    return ExistingCodeConflict(
        pk=str(obj.pk),
        receita_cod=cod,
        receita_cod_display=cod_display,
        display_label=display_label,
        link_url=link_url,
        vigencia_inicio=v_ini,
        vigencia_fim=v_fim,
    )


def existing_code_conflict_to_dict(conflict: ExistingCodeConflict) -> Dict[str, Any]:
    """Payload serializável (endpoint JSON na E2)."""
    return {
        "pk": conflict.pk,
        "receita_cod": conflict.receita_cod,
        "receita_cod_display": conflict.receita_cod_display,
        "display_label": conflict.display_label,
        "link_url": conflict.link_url,
        "vigencia_inicio": conflict.vigencia_inicio.isoformat(),
        "vigencia_fim": conflict.vigencia_fim.isoformat(),
    }
