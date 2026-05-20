"""
Sugestão de ``receita_cod`` para item filho a partir do item mãe (admin add).

Ver ``_dev/spec_itemClassificacao_criar_filho.md``.
"""

from __future__ import annotations

import logging
from datetime import date
from typing import Any, Dict, List, Optional, Set, Tuple

from django.http import HttpRequest
from django.urls import reverse

from apps.core.admin_formatters import format_receita_cod_by_vigencia
from apps.core.admin_mixins import transaction_time_sentinel_for_query
from apps.core.item_classificacao_code_lookup import (
    _classificacao_payload_from_obj,
    _parse_admin_get_date,
)
from apps.core.models import ItemClassificacao, NivelHierarquico
from apps.core.parent_item_validation import (
    _canonical_zero_segment,
    _receita_cod_digits_only,
    digit_mask_for_classificacao_vigencia,
    split_receita_cod_segments_tolerant,
)

logger = logging.getLogger(__name__)


def _vigencia_overlaps(
    ini_a: Optional[date],
    fim_a: Optional[date],
    ini_b: Optional[date],
    fim_b: Optional[date],
) -> bool:
    if not ini_a or not fim_a or not ini_b or not fim_b:
        return False
    return ini_a <= fim_b and fim_a >= ini_b


def _level_capacity(mask: List[int], level_number: int) -> int:
    """Capacidade numérica do nível L (1-based): 10^w - 1."""
    idx = level_number - 1
    if idx < 0 or idx >= len(mask):
        return 0
    width = mask[idx]
    if width <= 0:
        return 0
    return 10**width - 1


def _choose_segment_value(
    occupied_vigente: Set[int],
    capacity: int,
) -> Tuple[Optional[int], str]:
    """
    Escolhe o valor do segmento no nível alvo.

    Retorna ``(valor, strategy)`` com strategy em ``first`` | ``expansion`` | ``gap``,
    ou ``(None, "")`` se esgotado (**E1**).
    """
    if capacity < 1:
        return None, ""

    if not occupied_vigente:
        return 1, "first"

    expansion = max(occupied_vigente) + 1
    if 1 <= expansion <= capacity and expansion not in occupied_vigente:
        return expansion, "expansion"

    for candidate in range(1, capacity + 1):
        if candidate not in occupied_vigente:
            return candidate, "gap"

    return None, ""


def _assemble_child_receita_cod(
    mask: List[int],
    parent_parts: List[Optional[str]],
    level_number: int,
    segment_value: int,
) -> str:
    """Monta dígitos canônicos do filho (nível ``level_number`` discriminado, cauda zerada)."""
    l_idx = level_number - 1
    parts: List[str] = []
    for i, width in enumerate(mask):
        if i < l_idx:
            seg = parent_parts[i] if i < len(parent_parts) and parent_parts[i] is not None else ""
            if not seg:
                seg = "0" * width
            parts.append(seg.zfill(width)[-width:])
        elif i == l_idx:
            parts.append(str(segment_value).zfill(width))
        else:
            parts.append("0" * width)
    return "".join(parts)


def _radical_digits(mask: List[int], parent_cod_digits: str, nm: int) -> str:
    radical_len = int(sum(mask[:nm]))
    if radical_len <= 0:
        return ""
    return parent_cod_digits[:radical_len]


def _segment_int_at_level(
    parts: List[Optional[str]],
    level_number: int,
) -> Optional[int]:
    idx = level_number - 1
    if idx < 0 or idx >= len(parts):
        return None
    seg = parts[idx]
    if seg is None or _canonical_zero_segment(seg):
        return None
    try:
        return int(seg)
    except ValueError:
        return None


def _accumulate_occupation_at_level(
    occupied_vigente: Set[int],
    parts: List[Optional[str]],
    level_number: int,
    *,
    vig_ini: date,
    vig_fim: date,
    item_vig_ini: Optional[date],
    item_vig_fim: Optional[date],
) -> None:
    value = _segment_int_at_level(parts, level_number)
    if value is None:
        return
    if _vigencia_overlaps(item_vig_ini, item_vig_fim, vig_ini, vig_fim):
        occupied_vigente.add(value)


def _scan_ramo_k_star(
    radical: str,
    mask: List[int],
    nm: int,
    *,
    vig_ini: date,
    vig_fim: date,
    reg_sent: Any,
) -> Tuple[Optional[int], Set[int]]:
    """
    Varredura **(V2b)**: retorna o **primeiro** nível ``K*`` (de ``NM+1`` para cima)
    com detalhe e ``OCUPADO_VIGENTE(K*)``, ou ``(None, ∅)``.
    """
    if not radical:
        return None, set()

    occupied_by_level: Dict[int, Set[int]] = {
        k: set() for k in range(nm + 1, len(mask) + 1)
    }

    ramo_qs = ItemClassificacao.objects.filter(
        receita_cod__startswith=radical,
        data_registro_fim=reg_sent,
    ).only("receita_cod", "data_vigencia_inicio", "data_vigencia_fim")

    for item in ramo_qs.iterator(chunk_size=200):
        parts = split_receita_cod_segments_tolerant(
            _receita_cod_digits_only(item.receita_cod or ""),
            mask,
        )
        if not parts:
            continue
        item_ini = getattr(item, "data_vigencia_inicio", None)
        item_fim = getattr(item, "data_vigencia_fim", None)
        for k in range(nm + 1, len(mask) + 1):
            _accumulate_occupation_at_level(
                occupied_by_level[k],
                parts,
                k,
                vig_ini=vig_ini,
                vig_fim=vig_fim,
                item_vig_ini=item_ini,
                item_vig_fim=item_fim,
            )

    k_star: Optional[int] = None
    for k in range(nm + 1, len(mask) + 1):
        if occupied_by_level[k]:
            k_star = k
            break

    if k_star is None:
        return None, set()
    return k_star, occupied_by_level[k_star]


def _scan_filhos_nm_plus_one(
    parent_pk: int,
    mask: List[int],
    nm: int,
    *,
    vig_ini: date,
    vig_fim: date,
    reg_sent: Any,
) -> Set[int]:
    """Filhos directos **(V2a)** — segmento no nível ``NM+1``, sem filtro de classificação."""
    occupied_vigente: Set[int] = set()
    level_nm_plus_one = nm + 1

    children_qs = ItemClassificacao.objects.filter(
        parent_item_id_id=parent_pk,
        data_registro_fim=reg_sent,
    ).only("receita_cod", "data_vigencia_inicio", "data_vigencia_fim")

    for child in children_qs.iterator(chunk_size=200):
        parts = split_receita_cod_segments_tolerant(
            _receita_cod_digits_only(child.receita_cod or ""),
            mask,
        )
        if not parts:
            continue
        _accumulate_occupation_at_level(
            occupied_vigente,
            parts,
            level_nm_plus_one,
            vig_ini=vig_ini,
            vig_fim=vig_fim,
            item_vig_ini=getattr(child, "data_vigencia_inicio", None),
            item_vig_fim=getattr(child, "data_vigencia_fim", None),
        )

    return occupied_vigente


def _resolve_nivel_for_level(
    level_number: int,
    vig_ini: date,
    vig_fim: date,
    reg_sent: Any,
) -> Tuple[Optional[NivelHierarquico], int]:
    """Resolve ``NivelHierarquico`` por ``nivel_numero`` e vigência, sem restringir à
    classificação do item mãe (ver `_dev/spec_itemClassificacao_criar_filho.md`).

    Retorna ``(nivel_obj, count)`` em que ``count`` é o total de candidatos
    ativos/vigentes; quando ``count > 1`` a chamada externa deve emitir aviso
    não bloqueante de ambiguidade e usar a versão mais recente devolvida.
    """
    filters: Dict[str, Any] = {
        "nivel_numero": level_number,
        "data_registro_fim": reg_sent,
        "data_vigencia_inicio__lte": vig_fim,
        "data_vigencia_fim__gte": vig_ini,
    }
    qs = (
        NivelHierarquico.objects.select_related("classificacao_id")
        .filter(**filters)
        .order_by("-data_vigencia_inicio", "-data_registro_inicio", "-pk")
    )
    return qs.first(), qs.count()


def _resolved_level_and_classificacao_payloads(
    nivel_obj: NivelHierarquico,
    level_number: int,
) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
    derived_level: Dict[str, Any] = {
        "number": level_number,
        "pk": str(nivel_obj.pk),
        "display_label": f"{nivel_obj.nivel_id} - {nivel_obj.nivel_nome}",
    }
    classificacao_payload = _classificacao_payload_from_obj(
        getattr(nivel_obj, "classificacao_id", None)
    )
    return derived_level, classificacao_payload


def suggest_child_code_for_parent(
    parent: ItemClassificacao,
    *,
    vigencia_inicio: Optional[date] = None,
    vigencia_fim: Optional[date] = None,
) -> Dict[str, Any]:
    """
    Núcleo do algoritmo da spec ``criar_filho``.

    Retorna dict com ``ok`` True/False e campos de sucesso ou erro.
    """
    notices: List[str] = []

    if not getattr(parent, "matriz", True):
        return {
            "ok": False,
            "code": "invalid_parent",
            "message": "O item mãe deve ser uma matriz (agregadora) para sugerir um item filho.",
        }

    parent_nivel = getattr(parent, "nivel_id", None)
    nm = getattr(parent_nivel, "nivel_numero", None) if parent_nivel else None
    if nm is None:
        return {
            "ok": False,
            "code": "invalid_parent",
            "message": "O item mãe não possui nível hierárquico válido.",
        }

    classificacao_obj = getattr(parent, "classificacao_id", None)
    classificacao_pk = getattr(classificacao_obj, "pk", None) if classificacao_obj else None
    if not classificacao_pk:
        return {
            "ok": False,
            "code": "invalid_parent",
            "message": "O item mãe não possui classificação associada.",
        }

    v1_ini = vigencia_inicio or getattr(parent, "data_vigencia_inicio", None)
    v1_fim = vigencia_fim or getattr(parent, "data_vigencia_fim", None)
    if not v1_ini or not v1_fim:
        return {
            "ok": False,
            "code": "invalid_parent",
            "message": "Informe o período de vigência no formulário ou utilize um item mãe com vigência definida.",
        }

    mask = digit_mask_for_classificacao_vigencia(classificacao_pk, v1_ini, v1_fim)
    if not mask:
        pvi = getattr(parent, "data_vigencia_inicio", None)
        pvf = getattr(parent, "data_vigencia_fim", None)
        if pvi is not None and pvf is not None:
            mask = digit_mask_for_classificacao_vigencia(classificacao_pk, pvi, pvf)
    if not mask:
        return {
            "ok": False,
            "code": "invalid_parent",
            "message": "Não foi possível determinar a máscara de código para a classificação e vigência do item mãe.",
        }

    if nm >= len(mask):
        return {
            "ok": False,
            "code": "parent_last_level",
            "message": (
                "Não é possível sugerir um item filho: o item mãe já ocupa o último nível "
                "da máscara hierárquica."
            ),
        }

    parent_cod = _receita_cod_digits_only(getattr(parent, "receita_cod", None) or "")
    parent_parts = split_receita_cod_segments_tolerant(parent_cod, mask) or []
    radical = _radical_digits(mask, parent_cod, nm)

    reg_sent = transaction_time_sentinel_for_query()

    k_star, occupied_ramo = _scan_ramo_k_star(
        radical,
        mask,
        nm,
        vig_ini=v1_ini,
        vig_fim=v1_fim,
        reg_sent=reg_sent,
    )

    if k_star is not None:
        level_target = k_star
        occupied_vigente = occupied_ramo
        strategy_origin = "radical_deep"
    else:
        level_target = nm + 1
        occupied_vigente = _scan_filhos_nm_plus_one(
            parent.pk,
            mask,
            nm,
            vig_ini=v1_ini,
            vig_fim=v1_fim,
            reg_sent=reg_sent,
        )
        strategy_origin = "direct_child"

    if level_target > nm + 1:
        notices.append(
            f"Sugestão com salto de nível: o detalhamento será no nível {level_target} "
            f"(item mãe no nível {nm})!"
        )

    capacity = _level_capacity(mask, level_target)
    segment_value, strategy = _choose_segment_value(occupied_vigente, capacity)
    if segment_value is None:
        return {
            "ok": False,
            "code": "capacity_exhausted",
            "message": (
                f"Todos os valores disponíveis para o nível {level_target} já estão detalhados "
                "com vigência compatível com o período efectivo, e não há lacuna reutilizável."
            ),
        }

    receita_cod = _assemble_child_receita_cod(mask, parent_parts, level_target, segment_value)
    receita_cod_display = format_receita_cod_by_vigencia(
        receita_cod,
        v1_ini,
        v1_fim,
        {},
    )

    nivel_obj, nivel_count = _resolve_nivel_for_level(
        level_target,
        v1_ini,
        v1_fim,
        reg_sent,
    )
    if not nivel_obj:
        return {
            "ok": False,
            "code": "level_not_resolvable",
            "message": (
                f"Não existe nível hierárquico ativo e vigente para o nível {level_target} "
                "na vigência considerada."
            ),
        }

    if nivel_count > 1:
        notices.append(
            f"Foram encontradas {nivel_count} versões ativas compatíveis "
            f"do nível {level_target}; foi selecionada a versão mais recente."
        )

    derived_level, classificacao_payload = _resolved_level_and_classificacao_payloads(
        nivel_obj,
        level_target,
    )

    existing = (
        ItemClassificacao.objects.filter(
            receita_cod=receita_cod,
            data_registro_fim=reg_sent,
            data_vigencia_inicio__lte=v1_fim,
            data_vigencia_fim__gte=v1_ini,
        )
        .order_by("pk")
        .first()
    )
    existing_code_warning: Optional[Dict[str, str]] = None
    if existing:
        try:
            link_url = reverse(
                f"admin:{existing._meta.app_label}_{existing._meta.model_name}_change",
                args=[existing.pk],
            )
        except Exception:
            link_url = ""
        existing_code_warning = {
            "message": (
                "Já existe um registo activo com este código canônico no período de vigência "
                "considerado."
            ),
            "pk": str(existing.pk),
            "link_url": link_url,
            "display_label": (
                f"{existing.receita_cod} - {existing.receita_nome or existing.item_id or ''}"
            ).strip(" -"),
        }

    return {
        "ok": True,
        "receita_cod": receita_cod,
        "receita_cod_display": receita_cod_display,
        "derived_level": derived_level,
        "classificacao": classificacao_payload,
        "strategy": strategy,
        "strategy_origin": strategy_origin,
        "level_target": level_target,
        "notices": notices,
        "vigencia": {
            "inicio": v1_ini.isoformat(),
            "fim": v1_fim.isoformat(),
        },
        "existing_code_warning": existing_code_warning,
        "parent": {
            "pk": str(parent.pk),
            "vigencia_inicio": (
                parent.data_vigencia_inicio.isoformat()
                if getattr(parent, "data_vigencia_inicio", None)
                else ""
            ),
            "vigencia_fim": (
                parent.data_vigencia_fim.isoformat()
                if getattr(parent, "data_vigencia_fim", None)
                else ""
            ),
        },
    }


def suggest_child_code_by_parent_response_data(request: HttpRequest) -> Dict[str, Any]:
    """Payload JSON para ``suggest-child-code-by-parent/``."""
    parent_pk_raw = (request.GET.get("parent_item_id") or "").strip()
    if not parent_pk_raw.isdigit():
        return {
            "ok": False,
            "code": "invalid_parent",
            "message": "Selecione um item mãe válido.",
        }

    parent = (
        ItemClassificacao.objects.select_related("classificacao_id", "nivel_id")
        .filter(pk=int(parent_pk_raw))
        .first()
    )
    if not parent:
        return {
            "ok": False,
            "code": "invalid_parent",
            "message": "Item mãe não encontrado.",
        }

    vig_ini = _parse_admin_get_date(request.GET.get("vigencia_inicio"))
    vig_fim = _parse_admin_get_date(request.GET.get("vigencia_fim"))

    return suggest_child_code_for_parent(
        parent,
        vigencia_inicio=vig_ini,
        vigencia_fim=vig_fim,
    )
