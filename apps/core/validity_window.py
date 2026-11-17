"""Resolve the validity window shared by the inquiry and the changelist search.

Settled cases come from the archived conception. Section 10 of that file stays
open: this module does not choose a calendar day for LOA-PPAG, does not turn a
registered version into a date span, and does not add a second version slot.
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional

PREFIX_LDO = "LDO"
PREFIX_LOA = "LOA-PPAG"

STATUS_OK = "ok"
STATUS_REFUSED = "refused"
STATUS_UNRESOLVED = "unresolved"

RECORD_SENTINEL = "sentinel"
RECORD_ASOF = "asof"


@dataclass
class Side:
    year: Optional[int] = None
    month: Optional[int] = None
    day: Optional[int] = None

    def is_empty(self) -> bool:
        return self.year is None and self.month is None and self.day is None


@dataclass
class VigenciaWindow:
    status: str
    start: Optional[date] = None
    end: Optional[date] = None
    version: Optional[str] = None
    record_mode: str = RECORD_SENTINEL
    record_day: Optional[date] = None
    reordered: bool = False
    reorder_note: str = ""
    messages: list[str] = field(default_factory=list)
    field_errors: dict[str, str] = field(default_factory=dict)

    @property
    def searches(self) -> bool:
        return self.status == STATUS_OK


def _blank(value) -> bool:
    return value is None or str(value).strip() == ""


def _opt_int(value, label: str, errors: dict[str, str]) -> Optional[int]:
    if _blank(value):
        return None
    text = str(value).strip()
    if not text.isdigit():
        errors[label] = "Informe um número."
        return None
    return int(text)


def _parse_record(value, errors: dict[str, str]) -> Optional[date]:
    if _blank(value):
        return None
    text = str(value).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    errors["registro"] = "A data de registro não existe."
    return None


def _side_from(year, month, day, prefix: str, errors: dict[str, str]) -> Side:
    return Side(
        year=_opt_int(year, f"{prefix}_ano", errors),
        month=_opt_int(month, f"{prefix}_mes", errors),
        day=_opt_int(day, f"{prefix}_dia", errors),
    )


def _complete(side: Side, today: date, day_field: str, errors: dict[str, str]) -> Optional[date]:
    year = side.year if side.year is not None else today.year
    month = side.month if side.month is not None else 12
    if month < 1 or month > 12:
        errors[day_field.replace("dia", "mes")] = "O mês informado não existe."
        return None
    last = calendar.monthrange(year, month)[1]
    day = side.day if side.day is not None else last
    if day < 1 or day > last:
        errors[day_field] = "O dia informado não existe nesse mês."
        return None
    return date(year, month, day)


def _fmt(value: date) -> str:
    return value.strftime("%d/%m/%Y")


def resolve_vigencia_window(
    *,
    today: date,
    ano=None,
    mes=None,
    dia=None,
    ano2=None,
    mes2=None,
    dia2=None,
    versao=None,
    registro=None,
) -> VigenciaWindow:
    """Return the assumed window, a refusal, or an unresolved open question."""
    errors: dict[str, str] = {}
    left = _side_from(ano, mes, dia, "esq", errors)
    right = _side_from(ano2, mes2, dia2, "dir", errors)
    record_day = _parse_record(registro, errors)
    version = "" if _blank(versao) else str(versao).strip()
    dates_filled = not left.is_empty() or not right.is_empty()

    if errors:
        return VigenciaWindow(
            status=STATUS_REFUSED,
            messages=list(errors.values()),
            field_errors=errors,
        )

    registered = bool(version) and version not in (PREFIX_LDO, PREFIX_LOA)
    if registered and dates_filled:
        message = (
            "A pesquisa não parte com data de vigência e versão cadastrada ao mesmo tempo."
        )
        return VigenciaWindow(
            status=STATUS_REFUSED,
            version=version,
            messages=[message],
            field_errors={"versao": message},
        )

    if version == PREFIX_LOA:
        message = (
            "O dia de calendário de LOA-PPAG ainda não está decidido. A pesquisa não parte."
        )
        return VigenciaWindow(
            status=STATUS_UNRESOLVED,
            version=PREFIX_LOA,
            messages=[message],
        )

    if registered:
        message = (
            "O intervalo de uma versão cadastrada ainda não está decidido. "
            "A data de vigência não é usada e a pesquisa não parte."
        )
        return VigenciaWindow(
            status=STATUS_UNRESOLVED,
            version=version,
            messages=[message],
        )

    if version == PREFIX_LDO:
        year_source = left if left.year is not None else right
        year = year_source.year if year_source.year is not None else today.year
        start = end = date(year, 5, 15)
        return VigenciaWindow(
            status=STATUS_OK,
            start=start,
            end=end,
            version=PREFIX_LDO,
            record_mode=RECORD_ASOF,
            record_day=start,
        )

    if left.is_empty() and right.is_empty():
        start = end = date(today.year, 12, 31)
    elif left.is_empty():
        start = end = _complete(right, today, "dir_dia", errors)
    elif right.is_empty():
        start = end = _complete(left, today, "esq_dia", errors)
    else:
        start = _complete(left, today, "esq_dia", errors)
        end = _complete(right, today, "dir_dia", errors)

    if errors or start is None or end is None:
        return VigenciaWindow(
            status=STATUS_REFUSED,
            messages=list(errors.values()) or ["A data de vigência não pôde ser assumida."],
            field_errors=errors,
        )

    note = ""
    reordered = False
    if start > end:
        original = (_fmt(start), _fmt(end))
        start, end = end, start
        reordered = True
        note = (
            "O período informado foi reordenado de "
            f"{original[0]} .. {original[1]} para {_fmt(start)} .. {_fmt(end)}."
        )

    if record_day is None:
        return VigenciaWindow(
            status=STATUS_OK,
            start=start,
            end=end,
            record_mode=RECORD_SENTINEL,
            reordered=reordered,
            reorder_note=note,
            messages=[note] if note else [],
        )
    return VigenciaWindow(
        status=STATUS_OK,
        start=start,
        end=end,
        record_mode=RECORD_ASOF,
        record_day=record_day,
        reordered=reordered,
        reorder_note=note,
        messages=[note] if note else [],
    )
