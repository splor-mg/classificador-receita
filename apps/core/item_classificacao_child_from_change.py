"""
Atalho «Criar Código Filho» na change view → add de ``ItemClassificacao``.

Regras de vigência **(V3′)** e estado do botão na barra ``object-tools``.
Ver ``_dev/spec_itemClassificacao_criar_filho.md``, secção «Atalho desde change (v2)».
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urlencode

from django.urls import reverse
from django.utils import timezone

from apps.core.admin_formatters import format_receita_cod_by_vigencia
from apps.core.item_classificacao_suggest_child_code import suggest_child_code_for_parent
from apps.core.models import ItemClassificacao
from apps.core.parent_item_validation import digit_mask_for_classificacao_vigencia

FROM_CHANGE_PARENT_QUERY_PARAM = "from_change_parent"
FROM_CHANGE_PARENT_QUERY_VALUE = "1"


def _as_date(value) -> Optional[date]:
    if value is None:
        return None
    if isinstance(value, datetime):
        if timezone.is_aware(value):
            return timezone.localtime(value).date()
        return value.date()
    if isinstance(value, date):
        return value
    return None


def vigencia_filho_from_item_mae(parent: ItemClassificacao) -> Tuple[date, date]:
    """
    Calcula ``data_vigencia_inicio`` e ``data_vigencia_fim`` do filho na entrada
    pelo atalho change → add (**V3′**).

    Comparações em data civil (fuso local do Django para datetimes aware).

    - ``fim_filho`` = ``fim_mae`` (sempre).
    - ``inicio_mae > 01/01/<ano corrente>`` → ``inicio_filho = inicio_mae``.
    - ``fim_mae <= 01/01/<ano corrente>`` (inclui ``fim_mae = 01/01/<ano corrente>``)
      → ``inicio_filho = inicio_mae``.
    - ``inicio_mae <= 01/01/<ano corrente>`` e ``fim_mae > 01/01/<ano corrente>``
      → ``inicio_filho = 01/01/<ano corrente>``.
    """
    inicio_mae = _as_date(getattr(parent, "data_vigencia_inicio", None))
    fim_mae = _as_date(getattr(parent, "data_vigencia_fim", None))
    if not inicio_mae or not fim_mae:
        raise ValueError(
            "O item mãe deve possuir data de início e fim de vigência definidas."
        )

    jan1_corrente = date(date.today().year, 1, 1)
    fim_filho = fim_mae

    if inicio_mae > jan1_corrente:
        inicio_filho = inicio_mae
    elif fim_mae <= jan1_corrente:
        inicio_filho = inicio_mae
    elif inicio_mae <= jan1_corrente and fim_mae > jan1_corrente:
        inicio_filho = jan1_corrente
    else:
        inicio_filho = inicio_mae

    return inicio_filho, fim_filho


def build_add_child_from_change_url(request, parent_pk: int) -> str:
    """URL da add com mãe pré-definida e flag de origem do atalho."""
    params = {
        "parent_item_id": str(parent_pk),
        FROM_CHANGE_PARENT_QUERY_PARAM: FROM_CHANGE_PARENT_QUERY_VALUE,
    }
    preserved = (request.GET.get("_changelist_filters") or "").strip()
    if preserved:
        params["_changelist_filters"] = preserved
    base = reverse(
        f"admin:{ItemClassificacao._meta.app_label}_{ItemClassificacao._meta.model_name}_add"
    )
    return f"{base}?{urlencode(params)}"


def _parent_is_last_hierarchical_level(parent: ItemClassificacao) -> bool:
    parent_nivel = getattr(parent, "nivel_id", None)
    nm = getattr(parent_nivel, "nivel_numero", None) if parent_nivel else None
    classificacao_obj = getattr(parent, "classificacao_id", None)
    classificacao_pk = getattr(classificacao_obj, "pk", None) if classificacao_obj else None
    if nm is None or not classificacao_pk:
        return True
    v_ini = _as_date(getattr(parent, "data_vigencia_inicio", None))
    v_fim = _as_date(getattr(parent, "data_vigencia_fim", None))
    if not v_ini or not v_fim:
        return True
    mask = digit_mask_for_classificacao_vigencia(classificacao_pk, v_ini, v_fim)
    if not mask:
        return True
    return nm >= len(mask)


def build_create_child_code_button_context(request, obj: ItemClassificacao) -> Dict[str, Any]:
    """
    Contexto de template para o botão «+ Criar Código Filho» na change view.
    """
    opts = ItemClassificacao._meta
    app_label, model_name = opts.app_label, opts.model_name
    perm = f"{app_label}.add_{model_name}"
    if not request.user.has_perm(perm):
        return {
            "item_show_create_child_code_button": False,
        }

    from apps.core.models import TRANSACTION_TIME_SENTINEL

    is_inactive = not ItemClassificacao._default_manager.filter(
        pk=obj.pk, data_registro_fim=TRANSACTION_TIME_SENTINEL
    ).exists()

    is_matriz = bool(getattr(obj, "matriz", False))
    enabled = True
    disabled_title = ""

    if is_inactive:
        enabled = False
        disabled_title = (
            "Registro inativo — apenas consulta histórica. "
            "Reative o registro para criar um código filho."
        )
    elif not is_matriz:
        enabled = True
        disabled_title = ""
    elif _parent_is_last_hierarchical_level(obj):
        enabled = False
        disabled_title = (
            "Este código já ocupa o último nível hierárquico da máscara; "
            "não é possível sugerir um código filho."
        )
    else:
        preview = suggest_child_code_for_parent(obj)
        if not preview.get("ok"):
            code = preview.get("code")
            if code in ("parent_last_level", "invalid_parent"):
                enabled = False
                disabled_title = preview.get("message") or disabled_title

    receita_cod_display = format_receita_cod_by_vigencia(
        obj.receita_cod or "",
        getattr(obj, "data_vigencia_inicio", None),
        getattr(obj, "data_vigencia_fim", None),
        {},
    )

    return {
        "item_show_create_child_code_button": True,
        "item_create_child_code_enabled": enabled,
        "item_create_child_code_disabled_title": disabled_title,
        "item_create_child_code_is_matriz": is_matriz,
        "item_create_child_code_add_url": build_add_child_from_change_url(request, obj.pk),
        "item_create_child_code_receita_cod_display": receita_cod_display,
        "item_init_child_from_change": False,
    }


def is_add_from_change_parent_request(request) -> bool:
    raw = (request.GET.get(FROM_CHANGE_PARENT_QUERY_PARAM) or "").strip().lower()
    return raw in ("1", "true", "yes", "on")


def apply_change_parent_initial_data(request, initial: Dict[str, Any]) -> Dict[str, Any]:
    """Preenche ``initial`` na add quando a origem é o atalho change → add."""
    if not is_add_from_change_parent_request(request):
        return initial

    parent_pk_raw = (request.GET.get("parent_item_id") or "").strip()
    if not parent_pk_raw.isdigit():
        return initial

    parent = (
        ItemClassificacao.objects.select_related("classificacao_id", "nivel_id")
        .filter(pk=int(parent_pk_raw))
        .first()
    )
    if not parent:
        return initial

    initial["parent_item_id"] = parent.pk
    try:
        vig_ini, vig_fim = vigencia_filho_from_item_mae(parent)
    except ValueError:
        return initial

    initial["data_vigencia_inicio"] = vig_ini
    initial["data_vigencia_fim"] = vig_fim
    return initial
