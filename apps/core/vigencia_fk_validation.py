"""
Validação de contenção temporal entre um registro bitemporal e os alvos de suas
Foreign Keys.

Ver `_dev/spec_foreingKeys.md`, tópico "Definição de Vigência por União
Contígua de Mesma Entidade Semântica".

Resumo do algoritmo (duas etapas, por FK):

1. **Etapa 1 — linha única apontada.** Se a vigência da linha apontada pela
   FK contém integralmente `[ini_filho, fim_filho]`, passa.
2. **Etapa 2 — união contígua das linhas ativas.** Aplicada apenas quando o
   modelo-alvo herda de ``BitemporalModel``. Varre todas as linhas com mesmo
   ``*_ref`` e ``data_registro_fim = sentinela``, calcula a união contígua
   (fusão estrita: ``prox_ini == ant_fim + 1 dia``) e verifica se o filho
   está integralmente coberto. Se sim, passa.
3. **Falha com diagnóstico.** Caso contrário, ``ValidationError`` com a união
   consolidada e a lista de gaps (faixas não cobertas do filho).

FKs cujo modelo-alvo NÃO é bitemporal (ex.: ``BaseLegalTecnica``) seguem apenas
a Etapa 1 — comportamento idêntico ao anterior à mudança.
"""

from __future__ import annotations

import datetime
from typing import List, Optional, Tuple

from django.core.exceptions import ValidationError
from django.db.models import Model
from django.utils import timezone


# Constantes locais para evitar import cíclico com apps.core.models.
_VALID_TIME_SENTINEL = datetime.date(9999, 12, 31)
_TRANSACTION_TIME_SENTINEL = datetime.datetime(9999, 12, 31, 0, 0, 0)
_ONE_DAY = datetime.timedelta(days=1)


# ---------------------------------------------------------------------------
# Etapa 1: contenção da linha apontada
# ---------------------------------------------------------------------------
def vigencia_interval_contains(
    container_start,
    container_end,
    inner_start,
    inner_end,
) -> bool:
    """True se ``[inner_start, inner_end] ⊆ [container_start, container_end]`` (fechados)."""
    if container_start is None or container_end is None:
        return True
    if inner_start is None or inner_end is None:
        return True
    return container_start <= inner_start and inner_end <= container_end


# ---------------------------------------------------------------------------
# Detecção e resolução do alvo da FK
# ---------------------------------------------------------------------------
def _get_vigencia(instance) -> Tuple[Optional[object], Optional[object]]:
    ini = getattr(instance, "data_vigencia_inicio", None)
    fim = getattr(instance, "data_vigencia_fim", None)
    return ini, fim


def _get_field(instance, field_name: str):
    try:
        field = instance._meta.get_field(field_name)
    except Exception:
        return None
    if not getattr(field, "is_relation", False) or getattr(field, "many_to_many", False):
        return None
    return field


def _fk_target(instance, field) -> Optional[Model]:
    rel_obj = getattr(instance, field.name, None)
    if rel_obj is not None:
        return rel_obj
    raw_id = getattr(instance, field.attname, None)
    if raw_id is None:
        return None
    related_model = field.remote_field.model
    return related_model.objects.filter(pk=raw_id).first()


def _is_bitemporal_target(field) -> bool:
    """True quando o modelo-alvo da FK herda de ``BitemporalModel``."""
    from apps.core.models import BitemporalModel  # import local p/ evitar ciclo

    related_model = field.remote_field.model
    if not isinstance(related_model, type):
        return False
    try:
        return issubclass(related_model, BitemporalModel)
    except TypeError:
        return False


# ---------------------------------------------------------------------------
# Identidade semântica do alvo (prioridade: *_ref; fallback: *_id)
# ---------------------------------------------------------------------------
def _identity_filter_for_target(target) -> Optional[dict]:
    """
    Filtro de varredura priorizando ``*_ref`` (chave surrogada). Cai para
    ``*_id`` apenas se nenhum ``*_ref`` estiver preenchido. ``None`` significa
    que não foi possível identificar a entidade (ex.: alvo sem ambos).
    """
    concrete_fields = list(getattr(target._meta, "concrete_fields", []) or [])

    ref_filter: dict = {}
    for f in concrete_fields:
        if getattr(f, "is_relation", False):
            continue
        if not f.name.endswith("_ref"):
            continue
        value = getattr(target, f.name, None)
        if value in (None, ""):
            continue
        ref_filter[f.name] = value
    if ref_filter:
        return ref_filter

    id_filter: dict = {}
    for f in concrete_fields:
        if getattr(f, "is_relation", False):
            continue
        if not f.name.endswith("_id"):
            continue
        value = getattr(target, f.name, None)
        if value in (None, ""):
            continue
        id_filter[f.name] = value
    if id_filter:
        return id_filter

    return None


def _semantic_id_value(target) -> Optional[str]:
    """Primeiro ``*_id`` semântico (não-relacional) com valor — para a mensagem ao usuário."""
    for f in target._meta.concrete_fields:
        if getattr(f, "is_relation", False):
            continue
        if not f.name.endswith("_id"):
            continue
        value = getattr(target, f.name, None)
        if value not in (None, ""):
            return str(value)
    return None


# ---------------------------------------------------------------------------
# Sentinela de transaction_time alinhado ao tipo do campo do alvo
# ---------------------------------------------------------------------------
def _transaction_sentinel_for_model(model) -> datetime.datetime:
    try:
        field = model._meta.get_field("data_registro_fim")
    except Exception:
        return _TRANSACTION_TIME_SENTINEL
    if getattr(field, "null", False):
        return _TRANSACTION_TIME_SENTINEL
    if timezone.is_naive(_TRANSACTION_TIME_SENTINEL):
        try:
            return timezone.make_aware(
                _TRANSACTION_TIME_SENTINEL, timezone.get_current_timezone()
            )
        except Exception:
            return _TRANSACTION_TIME_SENTINEL
    return _TRANSACTION_TIME_SENTINEL


# ---------------------------------------------------------------------------
# Etapa 2: união contígua e cobertura
# ---------------------------------------------------------------------------
def _active_windows_of_entity(target) -> List[Tuple[datetime.date, datetime.date]]:
    """
    Lista ``(data_vigencia_inicio, data_vigencia_fim)`` de todas as linhas
    ativas (``data_registro_fim = sentinela``) da mesma entidade semântica do
    alvo (identidade por ``*_ref``, com fallback para ``*_id``).
    """
    related_model = type(target)
    identity = _identity_filter_for_target(target)
    if identity is None:
        ini = getattr(target, "data_vigencia_inicio", None)
        fim = getattr(target, "data_vigencia_fim", None)
        if ini is None or fim is None:
            return []
        return [(ini, fim)]
    sentinel = _transaction_sentinel_for_model(related_model)
    rows = (
        related_model._default_manager.filter(
            **identity, data_registro_fim=sentinel
        )
        .order_by("data_vigencia_inicio", "data_vigencia_fim")
        .values_list("data_vigencia_inicio", "data_vigencia_fim")
    )
    return [(ini, fim) for ini, fim in rows if ini is not None and fim is not None]


def union_contiguous(
    intervals: List[Tuple[datetime.date, datetime.date]],
) -> List[Tuple[datetime.date, datetime.date]]:
    """
    Funde intervalos vizinhos contíguos (``prox_ini == ant_fim + 1 dia``).

    Sobreposições não fundem — ficam como entradas separadas na união
    consolidada. Intervalos cujo ``fim`` é o sentinela (9999-12-31) não
    participam de fusão à direita (não existe ``fim + 1 dia`` válido).
    """
    if not intervals:
        return []
    ordered = sorted(intervals, key=lambda x: (x[0], x[1]))
    merged: List[Tuple[datetime.date, datetime.date]] = [ordered[0]]
    for ini, fim in ordered[1:]:
        last_ini, last_fim = merged[-1]
        if last_fim < _VALID_TIME_SENTINEL and ini == last_fim + _ONE_DAY:
            merged[-1] = (last_ini, max(last_fim, fim))
        else:
            merged.append((ini, fim))
    return merged


def interval_covered_by_union(
    union: List[Tuple[datetime.date, datetime.date]],
    inner_ini: datetime.date,
    inner_fim: datetime.date,
) -> Tuple[bool, List[Tuple[datetime.date, datetime.date]]]:
    """
    Verifica se ``[inner_ini, inner_fim]`` está integralmente coberto por
    ``union``. Retorna ``(ok, gaps)``, em que ``gaps`` enumera as faixas
    descobertas (vazia quando ``ok=True``).
    """
    if inner_ini is None or inner_fim is None:
        return True, []
    if not union:
        return False, [(inner_ini, inner_fim)]

    gaps: List[Tuple[datetime.date, datetime.date]] = []
    cursor: Optional[datetime.date] = inner_ini
    for u_ini, u_fim in sorted(union, key=lambda x: (x[0], x[1])):
        if cursor is None or cursor > inner_fim:
            break
        if u_fim < cursor:
            continue
        if u_ini > cursor:
            gap_end = min(u_ini - _ONE_DAY, inner_fim)
            gaps.append((cursor, gap_end))
            cursor = u_ini
        if u_fim >= cursor:
            if u_fim >= _VALID_TIME_SENTINEL or u_fim >= inner_fim:
                cursor = None
                break
            cursor = u_fim + _ONE_DAY

    if cursor is not None and cursor <= inner_fim:
        gaps.append((cursor, inner_fim))

    return (len(gaps) == 0), gaps


# ---------------------------------------------------------------------------
# Formatação da mensagem
# ---------------------------------------------------------------------------
def _fmt_date(d) -> str:
    if isinstance(d, datetime.date):
        return d.isoformat()
    return str(d)


def _fmt_windows(windows: List[Tuple[datetime.date, datetime.date]]) -> str:
    if not windows:
        return "(nenhuma janela ativa)"
    return "; ".join(f"{_fmt_date(i)} a {_fmt_date(f)}" for i, f in windows)


def _build_union_error_message(
    *,
    c_ini,
    c_fim,
    related_label: str,
    target,
    union: List[Tuple[datetime.date, datetime.date]],
    gaps: List[Tuple[datetime.date, datetime.date]],
) -> str:
    semantic = _semantic_id_value(target)
    suffix_ident = f" ({semantic})" if semantic else ""
    msg = (
        f"O período de vigência deste registro ({_fmt_date(c_ini)} a "
        f"{_fmt_date(c_fim)}) não está integralmente coberto pela união das "
        f"vigências ativas de {related_label} selecionada{suffix_ident}. "
        f"União consolidada: {_fmt_windows(union)}."
    )
    if gaps:
        gap_lines = "\n".join(
            f"  - {_fmt_date(i)} a {_fmt_date(f)}" for i, f in gaps
        )
        msg += f" Faltas:\n{gap_lines}"
    return msg


def _build_single_row_error_message(
    *, c_ini, c_fim, related_label: str, p_ini, p_fim
) -> str:
    return (
        f"O período de vigência deste registo ({_fmt_date(c_ini)} a "
        f"{_fmt_date(c_fim)}) deve estar contido no período de vigência de "
        f"{related_label} ({_fmt_date(p_ini)} a {_fmt_date(p_fim)})."
    )


# ---------------------------------------------------------------------------
# Função pública
# ---------------------------------------------------------------------------
def validate_vigencia_contained_in_fk_targets(
    instance,
    fk_fields: List[Tuple[str, str]],
) -> None:
    """
    Valida contenção temporal entre o registro e os alvos das FKs declaradas.

    ``fk_fields``: lista de ``(nome_do_campo_fk, rótulo_curto_para_mensagem)``.

    Ignora FK nula. Para modelos-alvo bitemporais, aplica Etapa 1 (linha
    apontada) e, se falhar, Etapa 2 (união contígua das linhas ativas com mesmo
    ``*_ref``). Para modelos não bitemporais, aplica apenas a Etapa 1.
    """
    c_ini, c_fim = _get_vigencia(instance)
    if c_ini is None or c_fim is None:
        return

    errors: dict = {}
    for field_name, related_label in fk_fields:
        field = _get_field(instance, field_name)
        if field is None:
            continue
        target = _fk_target(instance, field)
        if target is None:
            continue

        # Etapa 1: linha apontada cobre integralmente?
        p_ini, p_fim = _get_vigencia(target)
        if p_ini is not None and p_fim is not None and vigencia_interval_contains(
            p_ini, p_fim, c_ini, c_fim
        ):
            continue

        if not _is_bitemporal_target(field):
            if p_ini is None or p_fim is None:
                continue
            errors[field_name] = ValidationError(
                _build_single_row_error_message(
                    c_ini=c_ini,
                    c_fim=c_fim,
                    related_label=related_label,
                    p_ini=p_ini,
                    p_fim=p_fim,
                ),
                code="vigencia_fk_containment",
            )
            continue

        # Etapa 2: união contígua das linhas ativas da mesma entidade
        windows = _active_windows_of_entity(target)
        union = union_contiguous(windows)
        ok, gaps = interval_covered_by_union(union, c_ini, c_fim)
        if ok:
            continue

        errors[field_name] = ValidationError(
            _build_union_error_message(
                c_ini=c_ini,
                c_fim=c_fim,
                related_label=related_label,
                target=target,
                union=union,
                gaps=gaps,
            ),
            code="vigencia_fk_union_containment",
        )

    if errors:
        raise ValidationError(errors)
