"""
Detecção de conflito por código canônico já existente (admin add).

Ver ``_dev/spec_itemClassificacao_criar_codigo_existente.md`` (CE / CE★).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Dict, Optional

from django.http import HttpRequest
from django.urls import reverse
from django.utils.html import format_html, strip_tags

from apps.core.admin_formatters import format_receita_cod_by_vigencia
from apps.core.admin_mixins import transaction_time_sentinel_for_query
from apps.core.classification_item_code_lookup import (
    _parse_admin_get_date,
    normalize_receita_cod_digits,
)
from apps.core.models import ItemClassificacao


def _format_vigencia_br(value: date) -> str:
    return value.strftime("%d/%m/%Y")


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
    """Payload serializável (endpoint JSON)."""
    return {
        "pk": conflict.pk,
        "receita_cod": conflict.receita_cod,
        "receita_cod_display": conflict.receita_cod_display,
        "display_label": conflict.display_label,
        "link_url": conflict.link_url,
        "vigencia_inicio": conflict.vigencia_inicio.isoformat(),
        "vigencia_fim": conflict.vigencia_fim.isoformat(),
        "vigencia_inicio_display": _format_vigencia_br(conflict.vigencia_inicio),
        "vigencia_fim_display": _format_vigencia_br(conflict.vigencia_fim),
    }


def existing_code_conflict_message_html(conflict: ExistingCodeConflict):
    """
    Fragmento HTML canônico CE-2/CE-3/CE-5 (alerta, erro de submit e JSON).

    Inclui link do código (nova aba) e «Clique aqui» (``js-existing-code-conflict-next``).
    """
    cod = conflict.receita_cod_display or conflict.receita_cod
    ini = _format_vigencia_br(conflict.vigencia_inicio)
    fim = _format_vigencia_br(conflict.vigencia_fim)
    link_url = (conflict.link_url or "").strip()
    if link_url:
        cod_part = format_html(
            '<a href="{}" target="_blank" rel="noopener noreferrer">{}</a>',
            link_url,
            cod,
        )
    else:
        cod_part = cod
    return format_html(
        "Já existe o {} com vigência de {} até {}. "
        '<a href="#" class="js-existing-code-conflict-next">Clique aqui</a> '
        "para ir para o próximo código disponível ou ajuste a data de vigência do código atual.",
        cod_part,
        ini,
        fim,
    )


def existing_code_conflict_plain_message(conflict: ExistingCodeConflict) -> str:
    """Texto sem HTML (fallback / campo ``message`` do JSON)."""
    return strip_tags(str(existing_code_conflict_message_html(conflict))).strip()


def lookup_existing_code_conflict_response_data(request: HttpRequest) -> Dict[str, Any]:
    """Payload JSON para ``lookup-existing-code-conflict/`` (admin add)."""
    raw_code = request.GET.get("code")
    vig_ini = _parse_admin_get_date(request.GET.get("vigencia_inicio"))
    vig_fim = _parse_admin_get_date(request.GET.get("vigencia_fim"))

    code = normalize_receita_cod_digits(raw_code)
    if not code:
        return {"ok": False, "message": "Informe o código canônico."}
    if not vig_ini or not vig_fim:
        return {
            "ok": False,
            "message": "Informe o período de vigência para verificar o código.",
        }
    if vig_fim < vig_ini:
        return {
            "ok": False,
            "message": "Período de vigência inválido: data fim anterior à data de início.",
        }

    conflict = resolve_existing_code_conflict(code, vig_ini, vig_fim)
    if not conflict:
        return {"ok": True, "has_conflict": False}

    message_html = existing_code_conflict_message_html(conflict)
    return {
        "ok": True,
        "has_conflict": True,
        "code_digits": conflict.receita_cod,
        "code_display": conflict.receita_cod_display,
        "message_html": str(message_html),
        "message": existing_code_conflict_plain_message(conflict),
        "conflict": existing_code_conflict_to_dict(conflict),
    }
