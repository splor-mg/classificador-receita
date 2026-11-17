"""Apply a resolved validity window to a bitemporal queryset and to the admin."""

from datetime import date

from django.contrib import messages
from django.db.models import QuerySet

from apps.core.models import TRANSACTION_TIME_SENTINEL, VersaoClassificacao
from apps.core.validity_window import (
    PREFIX_LDO,
    PREFIX_LOA,
    RECORD_ASOF,
    RECORD_SENTINEL,
    STATUS_OK,
    VigenciaWindow,
    resolve_vigencia_window,
)

VIGENCIA_PARAM = "vigencia"


def resolve_from_get(params, today: date | None = None) -> VigenciaWindow:
    data = params
    return resolve_vigencia_window(
        today=today or date.today(),
        ano=data.get("vigencia_ano"),
        mes=data.get("vigencia_mes"),
        dia=data.get("vigencia_dia"),
        ano2=data.get("vigencia_ano2"),
        mes2=data.get("vigencia_mes2"),
        dia2=data.get("vigencia_dia2"),
        versao=data.get("vigencia_versao"),
        registro=data.get("vigencia_registro"),
    )


def describe_window(window: VigenciaWindow) -> str:
    if not window.searches or window.start is None or window.end is None:
        return ""
    if window.start == window.end:
        validity = window.start.strftime("%d/%m/%Y")
    else:
        validity = (
            f"{window.start.strftime('%d/%m/%Y')} .. {window.end.strftime('%d/%m/%Y')}"
        )
    version = window.version or "qualquer versão"
    if window.record_mode == RECORD_SENTINEL:
        record = "31/12/9999 (sentinela)"
    else:
        record = window.record_day.strftime("%d/%m/%Y") if window.record_day else ""
    return (
        f"Data Vigência assumida: {validity}. "
        f"Versão assumida: {version}. "
        f"Data de Registro assumida: {record}."
    )


def apply_vigencia_window(queryset: QuerySet, window: VigenciaWindow) -> QuerySet:
    if not window.searches or window.start is None or window.end is None:
        return queryset
    queryset = queryset.filter(
        data_vigencia_inicio__lte=window.start,
        data_vigencia_fim__gte=window.end,
    )
    if window.record_mode == RECORD_ASOF and window.record_day is not None:
        return queryset.filter(
            data_registro_inicio__date__lte=window.record_day,
            data_registro_fim__date__gte=window.record_day,
        )
    return queryset.filter(data_registro_fim=TRANSACTION_TIME_SENTINEL)


def active_version_ids() -> list[str]:
    return list(
        VersaoClassificacao.objects.filter(data_registro_fim=TRANSACTION_TIME_SENTINEL)
        .order_by("versao_id")
        .values_list("versao_id", flat=True)
        .distinct()
    )


class VigenciaSearchMixin:
    """Changelist search for the four classification lists. First paint is unchanged."""

    change_list_template = "admin/core/validity_change_list.html"

    def changelist_view(self, request, extra_context=None):
        extra = dict(extra_context or {})
        searching = request.GET.get(VIGENCIA_PARAM) == "1" and request.GET.get("_popup") != "1"
        window = resolve_from_get(request.GET) if searching else None
        if window is not None:
            request._vigencia_window = window
            for message in window.messages:
                if window.status == STATUS_OK:
                    messages.info(request, message)
                else:
                    messages.error(request, message)
        extra["vigencia_window"] = window
        extra["vigencia_summary"] = describe_window(window) if window else ""
        extra["vigencia_versions"] = active_version_ids()
        extra["vigencia_prefixes"] = (PREFIX_LDO, PREFIX_LOA)
        today = date.today()
        extra["vigencia_years"] = list(range(1990, today.year + 11))
        extra["vigencia_months"] = list(range(1, 13))
        extra["vigencia_days"] = list(range(1, 32))
        return super().changelist_view(request, extra_context=extra)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.GET.get(VIGENCIA_PARAM) != "1" or request.GET.get("_popup") == "1":
            return queryset
        window = getattr(request, "_vigencia_window", None) or resolve_from_get(request.GET)
        return apply_vigencia_window(queryset, window)
