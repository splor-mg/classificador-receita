"""
Lookups JSON do admin para `ItemClassificacao`: hierarquia a partir do código
e resolução de item pai por código exato.

Ver `_dev/spec_lookup_hierarquia_por_codigo_admin.md`.
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
from apps.core.parent_item_validation import digit_mask_for_classificacao_vigencia


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
    """Payload JSON para `lookup-hierarchy-by-code/` (nível derivado + item pai matriz)."""
    raw_code = (request.GET.get("code") or "").replace(".", "").strip()
    classificacao_pk = (request.GET.get("classificacao_pk") or "").strip()
    vigencia_inicio = _parse_admin_get_date(request.GET.get("vigencia_inicio"))
    vigencia_fim = _parse_admin_get_date(request.GET.get("vigencia_fim"))

    if not raw_code:
        return {"ok": False, "message": "Informe o código canônico."}
    if not vigencia_inicio or not vigencia_fim:
        return {
            "ok": False,
            "message": "Informe o período de vigência para derivar nível e item pai.",
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
        level_obj = (
            NivelHierarquico.objects.select_related("classificacao_id")
            .filter(**level_selected_filters)
            .order_by("-data_vigencia_inicio", "-data_registro_inicio", "-pk")
            .first()
        )
    else:
        level_obj = (
            NivelHierarquico.objects.select_related("classificacao_id")
            .filter(**level_base_filters)
            .order_by("-data_vigencia_inicio", "-data_registro_inicio", "-pk")
            .first()
        )

    alt_level_obj = None
    if class_obj is not None and not level_obj:
        alt_qs = (
            NivelHierarquico.objects.select_related("classificacao_id")
            .filter(**level_base_filters)
            .order_by("-data_vigencia_inicio", "-data_registro_inicio", "-pk")
            .exclude(classificacao_id_id=class_obj.pk)
        )
        alt_level_obj = alt_qs.first()

    chosen_level = level_obj or alt_level_obj
    derived_level_payload: Dict[str, Any] = {
        "number": derived_level_number,
        "pk": str(chosen_level.pk) if chosen_level else "",
        "display_label": (
            f"{chosen_level.nivel_id} - {chosen_level.nivel_nome}" if chosen_level else ""
        ),
        "status": {"severity": "ok", "message": "", "alternative": None},
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
                    f"Foram encontradas {parent_count} matrizes ativas compatíveis; "
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
                                    "Não existe item pai vigente para o código informado "
                                    "na classificação selecionada, porém existe noutra classificação compatível."
                                ),
                                "alternative": {
                                    "classificacao": fb_alt_payload,
                                    "message": (
                                        "Não existe item pai vigente para a classificação selecionada, "
                                        f"porém existe para {fb_alt_id}. "
                                        "Certifique-se de que a classificação selecionada está correta."
                                    ),
                                },
                            }
                        notices.append(
                            f"O item pai encontrado pertence ao nível {fb_level}, "
                            f"que não é imediatamente anterior ao item filho (nível {derived_level_number}) "
                            "que está sendo criado."
                        )
                        if fb_cnt > 1:
                            notices.append(
                                f"Foram encontradas {fb_cnt} matrizes ativas compatíveis no fallback; "
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
                            "Não existe item pai vigente para o código informado "
                            "na classificação selecionada, porém existe noutra classificação compatível."
                        ),
                        "alternative": {
                            "classificacao": alt_class_payload,
                            "message": (
                                "Não existe item pai vigente para a classificação selecionada, "
                                f"porém existe para {alt_class_id}. "
                                "Certifique-se de que a classificação selecionada está correta."
                            ),
                        },
                    }
                    alt_notices: list[str] = []
                    if parent_alt_cnt > 1:
                        alt_notices.append(
                            f"Foram encontradas {parent_alt_cnt} matrizes ativas compatíveis noutra classificação; "
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
                        "Altere-o para matriz para poder utilizá-lo como item pai nesta hierarquia."
                    )
                    parent_payload["status"] = {
                        "severity": "error",
                        "message": plain,
                        "html": format_html(
                            "Existe item com o código <strong>{}</strong> ativo e vigente, "
                            "mas está registado como <strong>detalhe</strong>, não como matriz. "
                            "Altere-o para matriz para poder utilizá-lo como item pai nesta hierarquia. "
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
                            "Não existe item pai ativo e vigente como matriz para o código informado "
                            "nem na classificação selecionada, nem em noutra classificação compatível."
                        ),
                        "alternative": None,
                    }
                else:
                    parent_payload["status"] = {
                        "severity": "error",
                        "message": (
                            "Não existe item pai ativo e vigente como matriz para o código informado "
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
