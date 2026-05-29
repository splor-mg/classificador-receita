"""
Lookups JSON do admin para `ItemClassificacao`: hierarquia a partir do código
e resolução de item mãe por código exato.

Ver `_dev/spec_itemClassificacao_foreignKeys_lookup.md`.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, Optional

from django.http import HttpRequest
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html

from apps.core.admin_formatters import format_receita_cod_by_vigencia
from apps.core.admin_mixins import transaction_time_sentinel_for_query
from apps.core.code_mask import (
    effective_vigencia_for_item_hierarchy_lookup,
    resolve_receita_cod_mask_context,
)
from apps.core.models import (
    TRANSACTION_TIME_SENTINEL,
    Classificacao,
    ItemClassificacao,
    NivelHierarquico,
)
from apps.core.code_parent_item_validation import digit_mask_for_classificacao_vigencia

RECEITA_COD_CHANGE_BLOCK_MESSAGE = (
    "Uma vez criado, o código canônico não pode ser substituído na mesma linha de registro. "
    "Não é possível gravar outro código neste item por meio de Salvar ou Editar vigência."
)


def normalize_receita_cod_digits(raw: Optional[str]) -> str:
    return (raw or "").replace(".", "").strip()


def receita_cod_changed_vs_instance(
    posted_receita_cod: Optional[str], instance: ItemClassificacao
) -> bool:
    """True quando COD-2 ≠ COD-1 (spec editar_codigo — T-cod.0)."""
    cod2 = normalize_receita_cod_digits(posted_receita_cod)
    cod1 = normalize_receita_cod_digits(getattr(instance, "receita_cod", None))
    return bool(cod2) and cod2 != cod1


def _vigencia_intervals_overlap(
    inicio_a: date, fim_a: date, inicio_b: date, fim_b: date
) -> bool:
    return inicio_a <= fim_b and fim_a >= inicio_b


def _mask_compatible_for_code(code: str) -> tuple[bool, Optional[str]]:
    ctx = resolve_receita_cod_mask_context(None, input_length=len(code), on_date=date.today())
    mask = ctx.get("digit_mask") or []
    total = sum(mask) if mask else ctx.get("numero_digitos")
    if total and len(code) == total:
        return True, None
    if total:
        if ctx.get("source") == "fallback_default_latest_active_today":
            msg = (
                f"Código informado tem {len(code)} dígitos, mas a estrutura mais recente "
                f"da classificação é de {total} dígitos."
            )
        else:
            msg = (
                f"Código informado tem {len(code)} dígitos, mas o limite da classificação "
                f"é {total} dígitos."
            )
        return False, msg
    return False, (
        f"Código informado tem {len(code)} dígitos, mas não foi possível validar a estrutura."
    )


def _format_codigo_display(
    code: str,
    vig_inicio: Optional[date],
    vig_fim: Optional[date],
) -> str:
    return format_receita_cod_by_vigencia(code, vig_inicio, vig_fim, {}) or code


def _item_admin_change_url(obj: ItemClassificacao) -> str:
    return reverse(
        f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change",
        args=[obj.pk],
    )


def _item_admin_add_url_with_code(code: str) -> str:
    from urllib.parse import urlencode

    base = reverse(
        f"admin:{ItemClassificacao._meta.app_label}_{ItemClassificacao._meta.model_name}_add"
    )
    return f"{base}?{urlencode({'receita_cod': code})}"


def _pick_navigation_record(records: list[ItemClassificacao]) -> ItemClassificacao:
    return max(
        records,
        key=lambda r: (
            r.data_vigencia_fim,
            r.data_vigencia_inicio,
            r.pk,
        ),
    )


def resolve_code_navigation_response_data(request: HttpRequest) -> Dict[str, Any]:
    """
    Classifica COD-2 para navegação na change (C1–C4).
    Ver ``_dev/spec_itemClassificacao_editar_codigo.md``.
    """
    code = normalize_receita_cod_digits(request.GET.get("code"))
    vig_inicio = _parse_admin_get_date(request.GET.get("vigencia_inicio"))
    vig_fim = _parse_admin_get_date(request.GET.get("vigencia_fim"))
    exclude_pk_raw = (request.GET.get("exclude_pk") or "").strip()

    if not code:
        return {"ok": False, "scenario": "C1", "message": "Informe o código canônico."}
    if not vig_inicio or not vig_fim:
        return {
            "ok": False,
            "scenario": "C1",
            "message": "Informe o período de vigência do registro em edição.",
        }
    if vig_fim < vig_inicio:
        return {"ok": False, "scenario": "C1", "message": "Período de vigência inválido."}

    compatible, mask_msg = _mask_compatible_for_code(code)
    if not compatible:
        return {"ok": False, "scenario": "C1", "message": mask_msg or "Código incompatível com a máscara."}

    sentinel = transaction_time_sentinel_for_query()
    qs = ItemClassificacao.objects.filter(
        receita_cod=code,
        data_registro_fim=sentinel,
    )
    if exclude_pk_raw.isdigit():
        qs = qs.exclude(pk=int(exclude_pk_raw))

    records = list(qs)
    codigo_display = _format_codigo_display(code, vig_inicio, vig_fim)

    if not records:
        return {
            "ok": True,
            "scenario": "C4",
            "codigo_display": codigo_display,
            "target": {
                "view": "add",
                "pk": "",
                "change_url": "",
                "add_url": _item_admin_add_url_with_code(code),
            },
        }

    overlapping = [
        r
        for r in records
        if _vigencia_intervals_overlap(
            r.data_vigencia_inicio,
            r.data_vigencia_fim,
            vig_inicio,
            vig_fim,
        )
    ]

    if overlapping:
        target_obj = _pick_navigation_record(overlapping)
        scenario = "C2"
    else:
        target_obj = _pick_navigation_record(records)
        scenario = "C3"

    codigo_display = _format_codigo_display(
        target_obj.receita_cod or code,
        target_obj.data_vigencia_inicio,
        target_obj.data_vigencia_fim,
    )
    return {
        "ok": True,
        "scenario": scenario,
        "codigo_display": codigo_display,
        "target": {
            "view": "change",
            "pk": str(target_obj.pk),
            "change_url": _item_admin_change_url(target_obj),
            "add_url": "",
        },
    }


def _parse_admin_get_date(raw: Optional[str]) -> Optional[date]:
    value = (raw or "").strip()
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def _classificacao_identity_filters(class_obj: Any, fallback_pk: Optional[int] = None) -> Dict[str, Any]:
    identity: Dict[str, Any] = {}
    class_ref = getattr(class_obj, "classificacao_ref", None) if class_obj else None
    class_semantic = getattr(class_obj, "classificacao_id", None) if class_obj else None
    if class_ref not in (None, ""):
        identity["classificacao_id__classificacao_ref"] = class_ref
    elif class_semantic not in (None, ""):
        identity["classificacao_id__classificacao_id"] = class_semantic
    elif fallback_pk is not None:
        identity["classificacao_id"] = fallback_pk
    return identity


def _classificacao_payload_from_obj(class_obj: Any) -> Optional[Dict[str, Any]]:
    if not class_obj:
        return None
    try:
        link_url = reverse(
            f"admin:{class_obj._meta.app_label}_{class_obj._meta.model_name}_change",
            args=[class_obj.pk],
        )
    except Exception:
        link_url = ""
    return {
        "pk": str(class_obj.pk),
        "classificacao_id": getattr(class_obj, "classificacao_id", "") or "",
        "display_label": (
            f"{getattr(class_obj, 'classificacao_id', '')} - "
            f"{getattr(class_obj, 'classificacao_nome', '')}"
        ).strip(" -"),
        "link_url": link_url,
    }


def _is_zero_segment(seg: str) -> bool:
    return bool(seg) and set(seg) == {"0"}


def _active_matrix_parent_candidates(filters_dict: Dict[str, Any]):
    return (
        ItemClassificacao.objects.select_related("classificacao_id", "nivel_id")
        .filter(**filters_dict)
        .order_by("-data_vigencia_inicio", "-data_registro_inicio", "-pk")
    )


def lookup_parent_by_code_response_data(request: HttpRequest) -> Dict[str, Any]:
    """Payload JSON para `lookup-parent-by-code/` (lupa por código exato)."""
    code = (request.GET.get("code") or "").replace(".", "").strip()
    vigencia_inicio = request.GET.get("vigencia_inicio")
    vigencia_fim = request.GET.get("vigencia_fim")
    empty = {"pk": "", "semantic_value": "", "display_label": "", "link_url": ""}
    if not code or not vigencia_inicio or not vigencia_fim:
        return empty

    sentinel = TRANSACTION_TIME_SENTINEL
    if timezone.is_naive(sentinel):
        sentinel = timezone.make_aware(sentinel, timezone.get_current_timezone())

    qs = (
        ItemClassificacao.objects.filter(
            receita_cod=code,
            data_registro_fim=sentinel,
            data_vigencia_inicio__lte=vigencia_inicio,
            data_vigencia_fim__gte=vigencia_fim,
        )
        .order_by("pk")
    )
    obj = qs.first()
    if not obj:
        return empty

    link_url = reverse(
        f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change",
        args=[obj.pk],
    )
    return {
        "pk": str(obj.pk),
        "semantic_value": format_receita_cod_by_vigencia(
            obj.receita_cod or "",
            getattr(obj, "data_vigencia_inicio", None),
            getattr(obj, "data_vigencia_fim", None),
            {},
        ),
        "display_label": f"{obj.receita_cod} - {obj.receita_nome or obj.item_id or ''}".strip(" -"),
        "link_url": link_url,
    }


def lookup_hierarchy_by_code_response_data(request: HttpRequest) -> Dict[str, Any]:
    """Payload JSON para `lookup-hierarchy-by-code/` (nível derivado + item mãe matriz)."""
    raw_code = (request.GET.get("code") or "").replace(".", "").strip()
    classificacao_pk = (request.GET.get("classificacao_pk") or "").strip()
    vigencia_inicio = _parse_admin_get_date(request.GET.get("vigencia_inicio"))
    vigencia_fim = _parse_admin_get_date(request.GET.get("vigencia_fim"))

    if not raw_code:
        return {"ok": False, "message": "Informe o código canônico."}
    if not vigencia_inicio or not vigencia_fim:
        return {
            "ok": False,
            "message": "Informe o período de vigência para derivar nível e item mãe.",
        }
    if vigencia_fim < vigencia_inicio:
        return {
            "ok": False,
            "message": "Período de vigência inválido: data fim anterior à data de início.",
        }
    if not raw_code.isdigit():
        return {"ok": False, "message": "Código canônico inválido: utilize apenas dígitos."}

    class_obj = None
    if classificacao_pk:
        try:
            class_pk_int = int(classificacao_pk)
        except ValueError:
            return {"ok": False, "message": "Classificação inválida."}
        class_obj = Classificacao.objects.filter(pk=class_pk_int).only(
            "pk",
            "classificacao_ref",
            "classificacao_id",
            "classificacao_nome",
            "data_vigencia_inicio",
            "data_vigencia_fim",
        ).first()
        if not class_obj:
            return {"ok": False, "message": "Classificação inválida."}

    (
        effective_vigencia_inicio,
        effective_vigencia_fim,
        vigencia_overridden,
        default_scope_classificacao,
    ) = effective_vigencia_for_item_hierarchy_lookup(
        vigencia_inicio, vigencia_fim, classificacao=class_obj
    )

    if class_obj is not None:
        class_pk = class_obj.pk
    elif default_scope_classificacao is not None:
        class_pk = default_scope_classificacao.pk
    else:
        class_pk = None

    user_class_scope_filters = (
        _classificacao_identity_filters(class_obj, fallback_pk=class_obj.pk)
        if class_obj is not None
        else None
    )

    mask = None
    if class_pk is not None:
        mask = digit_mask_for_classificacao_vigencia(
            class_pk, effective_vigencia_inicio, effective_vigencia_fim
        )
    if not mask:
        ctx = resolve_receita_cod_mask_context(None, input_length=len(raw_code), on_date=date.today())
        mask = ctx.get("digit_mask") if ctx else None
    if not mask:
        return {
            "ok": False,
            "message": (
                "Não foi possível determinar a estrutura de níveis para o contexto informado."
            ),
        }

    total_digits = sum(mask)
    normalized_code = raw_code
    if len(normalized_code) < total_digits:
        normalized_code = normalized_code.ljust(total_digits, "0")
    elif len(normalized_code) > total_digits:
        extra_tail = normalized_code[total_digits:]
        if extra_tail and set(extra_tail) != {"0"}:
            return {
                "ok": False,
                "message": (
                    f"Código canônico com {len(normalized_code)} dígitos excede o limite "
                    f"de {total_digits} para a classificação e vigência informadas."
                ),
            }
        normalized_code = normalized_code[:total_digits]

    segments: list[str] = []
    pos = 0
    for width in mask:
        segments.append(normalized_code[pos : pos + width])
        pos += width

    deepest_index = -1
    for idx, seg in enumerate(segments):
        if not _is_zero_segment(seg):
            deepest_index = idx
    if deepest_index < 0:
        return {
            "ok": False,
            "message": "Código canônico inválido: não há nível detalhado diferente de zero.",
        }

    for idx in range(deepest_index + 1, len(segments)):
        if not _is_zero_segment(segments[idx]):
            return {
                "ok": False,
                "message": (
                    "Código canônico inválido: há detalhamento após o nível derivado. "
                    "Ajuste os zeros canônicos."
                ),
            }

    derived_level_number = deepest_index + 1
    reg_sent = transaction_time_sentinel_for_query()
    level_base_filters = {
        "nivel_numero": derived_level_number,
        "data_vigencia_inicio__lte": effective_vigencia_fim,
        "data_vigencia_fim__gte": effective_vigencia_inicio,
        "data_registro_fim": reg_sent,
    }
    if user_class_scope_filters:
        level_selected_filters = dict(level_base_filters)
        level_selected_filters.update(user_class_scope_filters)
        level_qs = (
            NivelHierarquico.objects.select_related("classificacao_id")
            .filter(**level_selected_filters)
            .order_by("-data_vigencia_inicio", "-data_registro_inicio", "-pk")
        )
    else:
        level_qs = (
            NivelHierarquico.objects.select_related("classificacao_id")
            .filter(**level_base_filters)
            .order_by("-data_vigencia_inicio", "-data_registro_inicio", "-pk")
        )
    level_count = level_qs.count()
    level_obj = level_qs.first()

    alt_level_obj = None
    alt_level_count = 0
    if class_obj is not None and not level_obj:
        alt_qs = (
            NivelHierarquico.objects.select_related("classificacao_id")
            .filter(**level_base_filters)
            .order_by("-data_vigencia_inicio", "-data_registro_inicio", "-pk")
            .exclude(classificacao_id_id=class_obj.pk)
        )
        alt_level_count = alt_qs.count()
        alt_level_obj = alt_qs.first()

    chosen_level = level_obj or alt_level_obj

    # Avisos não bloqueantes do nível: quando o resolver bitemporal escolhe
    # entre N ≥ 2 candidatos ativos e compatíveis com a vigência informada,
    # informa explicitamente a arbitragem (paridade com `parent.notices`).
    level_notices: list[str] = []
    if level_obj is not None and level_count > 1:
        level_notices.append(
            f"Foram encontradas {level_count} versões ativas compatíveis "
            f"do nível {derived_level_number}; foi selecionada a versão mais recente."
        )
    elif level_obj is None and alt_level_obj is not None and alt_level_count > 1:
        level_notices.append(
            f"Foram encontradas {alt_level_count} versões ativas compatíveis "
            f"do nível {derived_level_number} noutra classificação; "
            "foi selecionada a versão mais recente."
        )

    derived_level_payload: Dict[str, Any] = {
        "number": derived_level_number,
        "pk": str(chosen_level.pk) if chosen_level else "",
        "display_label": (
            f"{chosen_level.nivel_id} - {chosen_level.nivel_nome}" if chosen_level else ""
        ),
        "status": {"severity": "ok", "message": "", "alternative": None},
        "notices": level_notices,
    }
    if not chosen_level:
        derived_level_payload["status"] = {
            "severity": "error",
            "message": (
                f"Não existe nível hierárquico ativo e vigente para o nível {derived_level_number} "
                "compatível com a vigência informada."
            ),
            "alternative": None,
        }
    elif class_obj is not None and alt_level_obj and not level_obj:
        alt_class = getattr(alt_level_obj, "classificacao_id", None)
        alt_class_payload = _classificacao_payload_from_obj(alt_class)
        alt_class_id = alt_class_payload.get("classificacao_id", "") if alt_class_payload else ""
        derived_level_payload["status"] = {
            "severity": "warning",
            "message": (
                f"Não existe nível hierárquico vigente para o nível {derived_level_number} "
                "na classificação selecionada, porém existe para outra classificação compatível."
            ),
            "alternative": {
                "classificacao": alt_class_payload,
                "message": (
                    "Não existe nível hierárquico vigente para a classificação selecionada, "
                    f"porém existe para {alt_class_id}. "
                    "Certifique-se de que a classificação selecionada está correta."
                ),
            },
        }

    parent_payload: Dict[str, Any] = {
        "required": derived_level_number > 1,
        "found": False,
        "pk": "",
        "code": "",
        "name": "",
        "display_label": "",
        "link_url": "",
        "status": {"severity": "ok", "message": "", "alternative": None},
        "notices": [],
    }

    if derived_level_number > 1:
        parent_segments = list(segments)
        for idx in range(deepest_index, len(parent_segments)):
            parent_segments[idx] = "0" * mask[idx]
        parent_code = "".join(parent_segments)
        parent_payload["code"] = parent_code

        parent_matrix_attempts: list[Dict[str, Any]] = []

        parent_filters = {
            "receita_cod": parent_code,
            "matriz": True,
            "nivel_id__nivel_numero": derived_level_number - 1,
            "data_vigencia_inicio__lte": effective_vigencia_fim,
            "data_vigencia_fim__gte": effective_vigencia_inicio,
            "data_registro_fim": reg_sent,
        }
        if user_class_scope_filters:
            parent_filters.update(user_class_scope_filters)
        parent_matrix_attempts.append({"matrix_filters": dict(parent_filters), "exclude_class_pk": None})

        pq = _active_matrix_parent_candidates(parent_filters)
        parent_count = pq.count()
        parent_obj = pq.first()
        notices: list[str] = []

        if parent_obj:
            if parent_count > 1:
                notices.append(
                    f"Foram encontradas {parent_count} versões ativas compatíveis do item mãe; "
                    "foi selecionada a versão mais recente."
                )
            parent_payload["found"] = True
            parent_payload["pk"] = str(parent_obj.pk)
            parent_payload["name"] = parent_obj.receita_nome or ""
            parent_payload["display_label"] = (
                f"{parent_obj.receita_cod} - {parent_obj.receita_nome or parent_obj.item_id or ''}".strip(" -")
            )
            parent_payload["link_url"] = reverse(
                f"admin:{parent_obj._meta.app_label}_{parent_obj._meta.model_name}_change",
                args=[parent_obj.pk],
            )
            if notices:
                parent_payload["notices"] = notices
        else:
            fb_obj = None
            if deepest_index >= 1 and _is_zero_segment(segments[deepest_index - 1]):
                j = -1
                for cand in range(deepest_index - 1, -1, -1):
                    if not _is_zero_segment(segments[cand]):
                        j = cand
                        break
                if j >= 0:
                    fb_segments = list(segments)
                    for fidx in range(j + 1, len(fb_segments)):
                        fb_segments[fidx] = "0" * mask[fidx]
                    fb_code = "".join(fb_segments)
                    fb_level = j + 1
                    fb_filters = {
                        "receita_cod": fb_code,
                        "matriz": True,
                        "nivel_id__nivel_numero": fb_level,
                        "data_vigencia_inicio__lte": effective_vigencia_fim,
                        "data_vigencia_fim__gte": effective_vigencia_inicio,
                        "data_registro_fim": reg_sent,
                    }
                    parent_matrix_attempts.append({"matrix_filters": dict(fb_filters), "exclude_class_pk": None})

                    fb_qs = _active_matrix_parent_candidates(fb_filters)
                    fb_cnt = fb_qs.count()
                    fb_obj = fb_qs.first()
                    if fb_obj:
                        if class_obj is not None and getattr(fb_obj, "classificacao_id_id", None) != class_obj.pk:
                            fb_alt_payload = _classificacao_payload_from_obj(
                                getattr(fb_obj, "classificacao_id", None)
                            )
                            fb_alt_id = fb_alt_payload.get("classificacao_id", "") if fb_alt_payload else ""
                            parent_payload["status"] = {
                                "severity": "warning",
                                "message": (
                                    "Não existe item mãe vigente para o código informado "
                                    "na classificação selecionada, porém existe noutra classificação compatível."
                                ),
                                "alternative": {
                                    "classificacao": fb_alt_payload,
                                    "message": (
                                        "Não existe item mãe vigente para a classificação selecionada, "
                                        f"porém existe para {fb_alt_id}. "
                                        "Certifique-se de que a classificação selecionada está correta."
                                    ),
                                },
                            }
                        notices.append(
                            f"O item mãe encontrado pertence ao nível {fb_level}, "
                            f"que não é imediatamente anterior ao item filho (nível {derived_level_number}) "
                            "que está sendo criado."
                        )
                        if fb_cnt > 1:
                            notices.append(
                                f"Foram encontradas {fb_cnt} versões ativas compatíveis do item mãe no fallback; "
                                "foi selecionada a versão mais recente."
                            )
                        parent_payload["found"] = True
                        parent_payload["pk"] = str(fb_obj.pk)
                        parent_payload["code"] = fb_code
                        parent_payload["name"] = fb_obj.receita_nome or ""
                        parent_payload["display_label"] = (
                            f"{fb_obj.receita_cod} - {fb_obj.receita_nome or fb_obj.item_id or ''}".strip(" -")
                        )
                        parent_payload["link_url"] = reverse(
                            f"admin:{fb_obj._meta.app_label}_{fb_obj._meta.model_name}_change",
                            args=[fb_obj.pk],
                        )
                        parent_payload["notices"] = notices

            if not parent_payload.get("found") and class_obj is not None:
                parent_alt_filters = {
                    "receita_cod": parent_code,
                    "matriz": True,
                    "nivel_id__nivel_numero": derived_level_number - 1,
                    "data_vigencia_inicio__lte": effective_vigencia_fim,
                    "data_vigencia_fim__gte": effective_vigencia_inicio,
                    "data_registro_fim": reg_sent,
                }
                parent_matrix_attempts.append(
                    {
                        "matrix_filters": dict(parent_alt_filters),
                        "exclude_class_pk": class_obj.pk,
                    }
                )
                parent_alt_qs = (
                    ItemClassificacao.objects.select_related("classificacao_id", "nivel_id")
                    .filter(**parent_alt_filters)
                    .exclude(classificacao_id_id=class_obj.pk)
                    .order_by("-data_vigencia_inicio", "-data_registro_inicio", "-pk")
                )
                parent_alt_cnt = parent_alt_qs.count()
                parent_alt_obj = parent_alt_qs.first()
                if parent_alt_obj:
                    alt_class_payload = _classificacao_payload_from_obj(
                        getattr(parent_alt_obj, "classificacao_id", None)
                    )
                    alt_class_id = alt_class_payload.get("classificacao_id", "") if alt_class_payload else ""
                    parent_payload["found"] = True
                    parent_payload["pk"] = str(parent_alt_obj.pk)
                    parent_payload["name"] = parent_alt_obj.receita_nome or ""
                    parent_payload["display_label"] = (
                        f"{parent_alt_obj.receita_cod} - "
                        f"{parent_alt_obj.receita_nome or parent_alt_obj.item_id or ''}"
                    ).strip(" -")
                    parent_payload["link_url"] = reverse(
                        f"admin:{parent_alt_obj._meta.app_label}_{parent_alt_obj._meta.model_name}_change",
                        args=[parent_alt_obj.pk],
                    )
                    parent_payload["status"] = {
                        "severity": "warning",
                        "message": (
                            "Não existe item mãe vigente para o código informado "
                            "na classificação selecionada, porém existe noutra classificação compatível."
                        ),
                        "alternative": {
                            "classificacao": alt_class_payload,
                            "message": (
                                "Não existe item mãe vigente para a classificação selecionada, "
                                f"porém existe para {alt_class_id}. "
                                "Certifique-se de que a classificação selecionada está correta."
                            ),
                        },
                    }
                    alt_notices: list[str] = []
                    if parent_alt_cnt > 1:
                        alt_notices.append(
                            f"Foram encontradas {parent_alt_cnt} versões ativas compatíveis do item mãe noutra classificação; "
                            "foi selecionada a versão mais recente."
                        )
                    parent_payload["notices"] = alt_notices

            if not parent_payload.get("found"):
                detail_obj = None
                for att in parent_matrix_attempts:
                    mf = att["matrix_filters"]
                    excl = att["exclude_class_pk"]
                    mqs = ItemClassificacao.objects.filter(**mf)
                    if excl is not None:
                        mqs = mqs.exclude(classificacao_id_id=excl)
                    if mqs.exists():
                        continue
                    detail_filters = dict(mf)
                    detail_filters["matriz"] = False
                    dqs = ItemClassificacao.objects.select_related("classificacao_id", "nivel_id").filter(
                        **detail_filters
                    )
                    if excl is not None:
                        dqs = dqs.exclude(classificacao_id_id=excl)
                    detail_obj = dqs.order_by(
                        "-data_vigencia_inicio", "-data_registro_inicio", "-pk"
                    ).first()
                    if detail_obj:
                        break

                if detail_obj:
                    item_url = reverse(
                        f"admin:{detail_obj._meta.app_label}_{detail_obj._meta.model_name}_change",
                        args=[detail_obj.pk],
                    )
                    plain = (
                        f"Existe item com o código {detail_obj.receita_cod} ativo e vigente, "
                        "mas está registado como detalhe, não como matriz. "
                        "Altere-o para matriz para poder utilizá-lo como item mãe nesta hierarquia."
                    )
                    parent_payload["status"] = {
                        "severity": "error",
                        "message": plain,
                        "html": format_html(
                            "Existe item com o código <strong>{}</strong> ativo e vigente, "
                            "mas está registado como <strong>detalhe</strong>, não como matriz. "
                            "Altere-o para matriz para poder utilizá-lo como item mãe nesta hierarquia. "
                            '<a href="{}" target="_blank" rel="noopener noreferrer">Ver item</a>.',
                            detail_obj.receita_cod,
                            item_url,
                        ),
                        "alternative": None,
                    }
                elif class_obj is not None:
                    parent_payload["status"] = {
                        "severity": "error",
                        "message": (
                            "Não existe item mãe ativo e vigente como matriz para o código informado "
                            "nem na classificação selecionada, nem em outra classificação compatível."
                        ),
                        "alternative": None,
                    }
                else:
                    parent_payload["status"] = {
                        "severity": "error",
                        "message": (
                            "Não existe item mãe ativo e vigente como matriz para o código informado "
                            "compatível com a vigência indicada."
                        ),
                        "alternative": None,
                    }

    return {
        "ok": True,
        "normalized_code": normalized_code,
        "effective_vigencia": {
            "inicio": effective_vigencia_inicio.isoformat() if effective_vigencia_inicio else "",
            "fim": effective_vigencia_fim.isoformat() if effective_vigencia_fim else "",
            "overridden": vigencia_overridden,
        },
        "derived_level": derived_level_payload,
        "parent": parent_payload,
    }
