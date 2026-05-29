"""
Navegação estrutural na change de ItemClassificacao.

Ver ``_dev/spec_itemClassificacao_navegacao.md``.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

from django.http import HttpRequest
from django.urls import reverse

from apps.core.admin_formatters import format_receita_cod_by_vigencia, get_active_vigencia_masks
from apps.core.admin_mixins import transaction_time_sentinel_for_query
from apps.core.item_classificacao_code_lookup import (
    _item_admin_change_url,
    _pick_navigation_record,
    _vigencia_intervals_overlap,
    normalize_receita_cod_digits,
)
from apps.core.models import ItemClassificacao
from apps.core.code_parent_item_validation import derive_nivel_numero_from_receita_cod_digits

DIRECTIONS = frozenset({"next_code", "next_level", "prev_code", "prev_level"})


@dataclass(frozen=True)
class _NavContext:
    cod_edit: str
    segments: List[str]
    mask: List[int]
    nv_edit: int
    v1_inicio: date
    v1_fim: date
    origin_pk: int
    origin_classificacao_semantic: str
    origin_classificacao_nome: str
    codes: Set[str]


def _parse_iso_date(raw: Optional[str]) -> Optional[date]:
    if not raw:
        return None
    value = str(raw).strip()
    if not value:
        return None
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        return None


def mask_edit_for_vigencia(vig_inicio: date, vig_fim: date) -> Optional[List[int]]:
    """
    MASK-EDIT: mesma regra do cliente ``getMaskForCurrentVigencia`` —
    estrutura cuja vigência contém integralmente V1 (início ≤ V1.início e fim ≥ V1.fim).
    """
    for entry in get_active_vigencia_masks():
        mask_inicio = _parse_iso_date(entry.get("vigencia_inicio"))
        mask_fim = _parse_iso_date(entry.get("vigencia_fim"))
        digit_mask = entry.get("digit_mask")
        if not mask_inicio or not mask_fim or not digit_mask:
            continue
        if mask_inicio <= vig_inicio and mask_fim >= vig_fim:
            normalized = [int(x) for x in digit_mask]
            if all(n > 0 for n in normalized):
                return normalized
    return None


def _canonical_zero_segment(segment: str) -> bool:
    return bool(segment) and set(segment) == {"0"}


def _normalize_code_for_mask(raw_code: str, mask: List[int]) -> Optional[str]:
    code = normalize_receita_cod_digits(raw_code)
    if not code:
        return None
    total = sum(mask)
    if len(code) < total:
        code = code.ljust(total, "0")
    elif len(code) > total:
        extra = code[total:]
        if extra and set(extra) != {"0"}:
            return None
        code = code[:total]
    return code


def _segment_code(code: str, mask: List[int]) -> List[str]:
    segments: List[str] = []
    pos = 0
    for width in mask:
        segments.append(code[pos : pos + width])
        pos += width
    return segments


def _radical_digits(segments: List[str], level_n: int) -> str:
    if level_n <= 0:
        return ""
    return "".join(segments[:level_n])


def _stage1_prefix_level(segments: List[str], nv_edit: int) -> int:
    """
    Nível M do radical( M ) para etapa-1: maior L <= NV-EDIT com segmento L não
    zero canônico e níveis L+1 .. NV-EDIT-1 em zero canônico no COD-EDIT.
    """
    best = 0
    for level in range(1, nv_edit + 1):
        if _canonical_zero_segment(segments[level - 1]):
            continue
        if _levels_zero_between(segments, level, nv_edit):
            best = level
    return best


def _levels_zero_between(segments: List[str], low_level: int, high_level: int) -> bool:
    """Níveis (low_level, high_level) exclusivos, 1-based."""
    for level in range(low_level + 1, high_level):
        if not _canonical_zero_segment(segments[level - 1]):
            return False
    return True


def _build_navigable_codes(v1_inicio: date, v1_fim: date, mask: List[int]) -> Set[str]:
    sentinel = transaction_time_sentinel_for_query()
    codes: Set[str] = set()
    qs = ItemClassificacao.objects.filter(
        data_registro_fim=sentinel,
        data_vigencia_inicio__lte=v1_fim,
        data_vigencia_fim__gte=v1_inicio,
    ).only("receita_cod")
    for row in qs.iterator(chunk_size=500):
        normalized = _normalize_code_for_mask(row.receita_cod or "", mask)
        if normalized:
            codes.add(normalized)
    return codes


def _is_record_active(obj: ItemClassificacao) -> bool:
    sentinel = transaction_time_sentinel_for_query()
    reg_fim = obj.data_registro_fim
    if reg_fim is None:
        return False
    return reg_fim >= sentinel


def _build_nav_context(obj: ItemClassificacao) -> Optional[_NavContext]:
    if not _is_record_active(obj):
        return None
    v1_inicio = obj.data_vigencia_inicio
    v1_fim = obj.data_vigencia_fim
    if not v1_inicio or not v1_fim:
        return None
    mask = mask_edit_for_vigencia(v1_inicio, v1_fim)
    if not mask:
        return None
    cod_edit = _normalize_code_for_mask(obj.receita_cod or "", mask)
    if not cod_edit:
        return None
    nv_edit, err = derive_nivel_numero_from_receita_cod_digits(cod_edit, mask)
    if err or not nv_edit:
        return None
    segments = _segment_code(cod_edit, mask)
    class_obj = getattr(obj, "classificacao_id", None)
    class_sem = ""
    class_nome = ""
    if class_obj is not None:
        class_sem = getattr(class_obj, "classificacao_id", "") or ""
        class_nome = getattr(class_obj, "classificacao_nome", "") or ""
    return _NavContext(
        cod_edit=cod_edit,
        segments=segments,
        mask=mask,
        nv_edit=nv_edit,
        v1_inicio=v1_inicio,
        v1_fim=v1_fim,
        origin_pk=obj.pk,
        origin_classificacao_semantic=class_sem,
        origin_classificacao_nome=class_nome,
        codes=_build_navigable_codes(v1_inicio, v1_fim, mask),
    )


def _pick_target_code(candidates: Iterable[str], *, reverse: bool) -> Optional[str]:
    filtered = [c for c in candidates if c]
    if not filtered:
        return None
    return max(filtered) if reverse else min(filtered)


def _stage1_code_variation(
    ctx: _NavContext,
    *,
    forward: bool,
) -> Optional[str]:
    nv = ctx.nv_edit
    num_levels = len(ctx.mask)
    prefix_level = _stage1_prefix_level(ctx.segments, nv)
    rad_base = _radical_digits(ctx.segments, prefix_level)
    matches: List[str] = []

    level_range = range(num_levels, nv, -1)
    for level in level_range:
        level_matches: List[str] = []
        for code in ctx.codes:
            if code == ctx.cod_edit:
                continue
            if rad_base and not code.startswith(rad_base):
                continue
            if forward and code <= ctx.cod_edit:
                continue
            if not forward and code >= ctx.cod_edit:
                continue
            segs = _segment_code(code, ctx.mask)
            if not _levels_zero_between(segs, nv, level):
                continue
            if _canonical_zero_segment(segs[level - 1]):
                continue
            level_matches.append(code)
        if level_matches:
            matches = level_matches
            break

    if not matches:
        return None
    return _pick_target_code(matches, reverse=not forward)


def _sibling_at_level(
    ctx: _NavContext,
    level: int,
    *,
    forward: bool,
) -> Optional[str]:
    if level < 1 or level > len(ctx.mask):
        return None
    prefix = _radical_digits(ctx.segments, level - 1)
    current = ctx.segments[level - 1]
    matches: List[str] = []
    for code in ctx.codes:
        if code == ctx.cod_edit:
            continue
        if forward and code <= ctx.cod_edit:
            continue
        if not forward and code >= ctx.cod_edit:
            continue
        if prefix and not code.startswith(prefix):
            continue
        segs = _segment_code(code, ctx.mask)
        seg = segs[level - 1]
        if forward:
            if seg <= current:
                continue
        else:
            if seg >= current:
                continue
        if not _levels_zero_between(segs, level, len(ctx.mask) + 1):
            continue
        matches.append(code)

    if not matches:
        return None
    if forward:
        return min(matches, key=lambda c: (_segment_code(c, ctx.mask)[level - 1], c))
    return max(matches, key=lambda c: c)


def _ascend_variation(ctx: _NavContext, *, forward: bool) -> Optional[str]:
    for level in range(ctx.nv_edit - 1, 0, -1):
        discarded = ctx.segments[level - 1]
        matches: List[str] = []
        prefix = _radical_digits(ctx.segments, level - 1)
        for code in ctx.codes:
            if code == ctx.cod_edit:
                continue
            if forward and code <= ctx.cod_edit:
                continue
            if not forward and code >= ctx.cod_edit:
                continue
            if prefix and not code.startswith(prefix):
                continue
            segs = _segment_code(code, ctx.mask)
            seg = segs[level - 1]
            if forward:
                if seg <= discarded:
                    continue
            else:
                if seg >= discarded:
                    continue
            if not _levels_zero_between(segs, level, len(ctx.mask) + 1):
                continue
            matches.append(code)
        if matches:
            if forward:
                return min(matches, key=lambda c: (_segment_code(c, ctx.mask)[level - 1], c))
            return max(matches, key=lambda c: c)
    return None


def _resolve_next_code(ctx: _NavContext) -> Optional[str]:
    found = _stage1_code_variation(ctx, forward=True)
    if found:
        return found
    found = _sibling_at_level(ctx, ctx.nv_edit, forward=True)
    if found:
        return found
    return _ascend_variation(ctx, forward=True)


def _resolve_prev_code(ctx: _NavContext) -> Optional[str]:
    found = _stage1_code_variation(ctx, forward=False)
    if found:
        return found
    # etapa-2: maior código completo no ramo inferior
    nv = ctx.nv_edit
    prefix = _radical_digits(ctx.segments, nv - 1)
    current = ctx.segments[nv - 1]
    matches: List[str] = []
    for code in ctx.codes:
        if code == ctx.cod_edit:
            continue
        if code >= ctx.cod_edit:
            continue
        if prefix and not code.startswith(prefix):
            continue
        segs = _segment_code(code, ctx.mask)
        if segs[nv - 1] >= current:
            continue
        matches.append(code)
    if matches:
        return max(matches)
    return _ascend_variation(ctx, forward=False)


def _resolve_next_level(ctx: _NavContext) -> Optional[str]:
    found = _sibling_at_level(ctx, ctx.nv_edit, forward=True)
    if found:
        return found
    return _ascend_variation(ctx, forward=True)


def _resolve_prev_level(ctx: _NavContext) -> Optional[str]:
    found = _sibling_at_level(ctx, ctx.nv_edit, forward=False)
    if found:
        return found
    return _ascend_variation(ctx, forward=False)


def _resolve_direction(ctx: _NavContext, direction: str) -> Optional[str]:
    if direction == "next_code":
        return _resolve_next_code(ctx)
    if direction == "prev_code":
        return _resolve_prev_code(ctx)
    if direction == "next_level":
        return _resolve_next_level(ctx)
    if direction == "prev_level":
        return _resolve_prev_level(ctx)
    return None


def structural_navigation_availability(obj: ItemClassificacao) -> Dict[str, bool]:
    ctx = _build_nav_context(obj)
    if not ctx:
        return {d: False for d in DIRECTIONS}
    return {
        d: _resolve_direction(ctx, d) is not None for d in DIRECTIONS
    }


def _classificacao_display(obj: ItemClassificacao) -> Tuple[str, str]:
    class_obj = getattr(obj, "classificacao_id", None)
    if not class_obj:
        return "", ""
    sem = getattr(class_obj, "classificacao_id", "") or ""
    nome = getattr(class_obj, "classificacao_nome", "") or ""
    display = f"{sem} - {nome}".strip(" -") if nome else sem
    return sem, display


def _append_changelist_filters(change_url: str, request: HttpRequest) -> str:
    filters = (request.GET.get("_changelist_filters") or "").strip()
    if not filters:
        return change_url
    sep = "&" if "?" in change_url else "?"
    return f"{change_url}{sep}_changelist_filters={filters}"


def resolve_structural_navigation_response_data(
    request: HttpRequest,
    *,
    obj: ItemClassificacao,
) -> Dict[str, Any]:
    direction = (request.GET.get("direction") or "").strip()
    if direction not in DIRECTIONS:
        return {
            "ok": False,
            "reason": "invalid_direction",
            "message": "Parâmetro direction inválido.",
        }

    ctx = _build_nav_context(obj)
    if not ctx:
        return {
            "ok": False,
            "reason": "navigation_unavailable",
            "message": "Navegação estrutural indisponível para este registro.",
        }

    target_code = _resolve_direction(ctx, direction)
    if not target_code:
        return {
            "ok": False,
            "reason": "no_candidate",
            "message": "Não há destino navegável para esta direção na vigência atual.",
        }

    sentinel = transaction_time_sentinel_for_query()
    records = list(
        ItemClassificacao.objects.filter(
            receita_cod=target_code,
            data_registro_fim=sentinel,
        ).select_related("classificacao_id")
    )
    overlapping = [
        r
        for r in records
        if _vigencia_intervals_overlap(
            r.data_vigencia_inicio,
            r.data_vigencia_fim,
            ctx.v1_inicio,
            ctx.v1_fim,
        )
    ]
    if not overlapping:
        return {
            "ok": False,
            "reason": "no_candidate",
            "message": "Não há destino navegável para esta direção na vigência atual.",
        }

    target_obj = _pick_navigation_record(overlapping)
    change_url = _append_changelist_filters(_item_admin_change_url(target_obj), request)
    codigo_display = format_receita_cod_by_vigencia(
        target_obj.receita_cod or target_code,
        target_obj.data_vigencia_inicio,
        target_obj.data_vigencia_fim,
        {},
    )
    target_sem, target_class_display = _classificacao_display(target_obj)
    origin_display = ctx.origin_classificacao_semantic
    if ctx.origin_classificacao_nome:
        origin_display = f"{ctx.origin_classificacao_semantic} - {ctx.origin_classificacao_nome}".strip(
            " -"
        )

    return {
        "ok": True,
        "direction": direction,
        "codigo_display": codigo_display,
        "target": {
            "pk": str(target_obj.pk),
            "receita_cod": target_obj.receita_cod or target_code,
            "change_url": change_url,
            "classificacao_id": target_sem,
            "classificacao_display": target_class_display,
            "classificacao_changed": target_sem != (ctx.origin_classificacao_semantic or ""),
            "origin_classificacao_display": origin_display,
        },
    }
