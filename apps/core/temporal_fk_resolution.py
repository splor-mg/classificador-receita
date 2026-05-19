from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from django.db import models
from django.utils import timezone


_TRANSACTION_SENTINEL = datetime(9999, 12, 31, 0, 0, 0)


def _sentinel_for_field(dt_field: models.Field) -> datetime:
    if getattr(dt_field, "null", False):
        return _TRANSACTION_SENTINEL
    if timezone.is_naive(_TRANSACTION_SENTINEL):
        try:
            return timezone.make_aware(_TRANSACTION_SENTINEL, timezone.get_current_timezone())
        except Exception:
            return _TRANSACTION_SENTINEL
    return _TRANSACTION_SENTINEL


def _build_identity_filter(related_obj: models.Model) -> dict[str, Any]:
    """
    Filtro de identidade da entidade semântica do alvo.

    Prioriza ``*_ref`` (chave surrogada) por estabilidade frente a eventuais
    renomeações da chave semântica (ADR-003). Só recai em ``*_id`` quando
    nenhum ``*_ref`` estiver preenchido. PK só é usada se nem ``*_ref`` nem
    ``*_id`` estiverem disponíveis. Ver ``_dev/spec_foreignKeys_vigencia.md``.
    """
    concrete_fields = list(getattr(related_obj._meta, "concrete_fields", []) or [])

    ref_filter: dict[str, Any] = {}
    for field in concrete_fields:
        if field.is_relation or not field.name.endswith("_ref"):
            continue
        value = getattr(related_obj, field.name, None)
        if value in (None, ""):
            continue
        ref_filter[field.name] = value
    if ref_filter:
        return ref_filter

    id_filter: dict[str, Any] = {}
    for field in concrete_fields:
        if field.is_relation or not field.name.endswith("_id"):
            continue
        value = getattr(related_obj, field.name, None)
        if value in (None, ""):
            continue
        id_filter[field.name] = value
    if id_filter:
        return id_filter

    pk_name = related_obj._meta.pk.name
    return {pk_name: getattr(related_obj, pk_name)}


def _is_active_and_compatible(source_instance: Any, target: models.Model) -> bool:
    target_fields = {f.name: f for f in target._meta.concrete_fields}
    if "data_registro_fim" in target_fields:
        sentinel = _sentinel_for_field(target_fields["data_registro_fim"])
        if getattr(target, "data_registro_fim", None) != sentinel:
            return False

    source_ini = getattr(source_instance, "data_vigencia_inicio", None)
    source_fim = getattr(source_instance, "data_vigencia_fim", None)
    target_ini = getattr(target, "data_vigencia_inicio", None)
    target_fim = getattr(target, "data_vigencia_fim", None)
    if source_ini and source_fim and target_ini and target_fim:
        return target_ini <= source_ini and source_fim <= target_fim
    return True


def _is_temporal_related_model(related_model: type[models.Model]) -> bool:
    field_names = {f.name for f in related_model._meta.concrete_fields}
    return {
        "data_registro_fim",
        "data_vigencia_inicio",
        "data_vigencia_fim",
    }.issubset(field_names)


def get_temporal_fk_field_names(source_instance: Any) -> list[str]:
    """
    Lista FKs elegíveis para resolução temporal semântica.

    Híbrido:
    - auto-detecta FKs many-to-one para modelos bitemporais;
    - permite override declarativo por modelo:
      - `temporal_fk_include_fields = (...)`
      - `temporal_fk_exclude_fields = (...)`
    """
    model_cls = source_instance.__class__
    include = set(getattr(model_cls, "temporal_fk_include_fields", ()) or ())
    exclude = set(getattr(model_cls, "temporal_fk_exclude_fields", ()) or ())

    auto_fields: list[str] = []
    for field in source_instance._meta.concrete_fields:
        if not getattr(field, "is_relation", False):
            continue
        if not getattr(field, "many_to_one", False):
            continue
        related_model = field.remote_field.model
        if not isinstance(related_model, type):
            continue
        if _is_temporal_related_model(related_model):
            auto_fields.append(field.name)

    names = set(auto_fields) | include
    names -= exclude
    return sorted(names)


def resolve_active_compatible_fk(source_instance: Any, field_name: str) -> Optional[models.Model]:
    """
    Resolve FK para o registro ativo da mesma entidade e com vigência compatível.

    A resolução usa a identidade semântica do próprio alvo FK (preferindo *_ref,
    depois *_id) e, quando disponível, compatibilidade temporal por vigência.
    """
    field = source_instance._meta.get_field(field_name)
    if not getattr(field, "is_relation", False) or getattr(field, "many_to_many", False):
        return getattr(source_instance, field_name, None)

    target = getattr(source_instance, field_name, None)
    if target is None:
        raw_id = getattr(source_instance, field.attname, None)
        if raw_id is None:
            return None
        target = field.remote_field.model._default_manager.filter(pk=raw_id).first()
        if target is None:
            return None

    if _is_active_and_compatible(source_instance, target):
        return target

    related_model = target.__class__
    lookup = _build_identity_filter(target)
    qs = related_model._default_manager.filter(**lookup)

    related_fields = {f.name: f for f in related_model._meta.concrete_fields}
    if "data_registro_fim" in related_fields:
        sentinel = _sentinel_for_field(related_fields["data_registro_fim"])
        qs = qs.filter(data_registro_fim=sentinel)

    source_ini = getattr(source_instance, "data_vigencia_inicio", None)
    source_fim = getattr(source_instance, "data_vigencia_fim", None)
    compat_qs = qs
    if (
        source_ini is not None
        and source_fim is not None
        and "data_vigencia_inicio" in related_fields
        and "data_vigencia_fim" in related_fields
    ):
        compat_qs = qs.filter(data_vigencia_inicio__lte=source_ini, data_vigencia_fim__gte=source_fim)

    order = []
    for name in ("data_vigencia_inicio", "data_registro_inicio"):
        if name in related_fields:
            order.append(f"-{name}")
    order.append("-pk")
    # Regra principal: encaixe temporal integral.
    compatible = compat_qs.order_by(*order).first()
    if compatible is not None:
        return compatible

    # Fallback: se não houver contenção temporal, usa a versão ativa mais recente
    # da mesma entidade semântica.
    return qs.order_by(*order).first()


def apply_temporal_fk_resolution(source_instance: Any) -> None:
    """
    Reaponta in-place FKs elegíveis para versão ativa + vigente compatível.
    """
    for field_name in get_temporal_fk_field_names(source_instance):
        resolved = resolve_active_compatible_fk(source_instance, field_name)
        if resolved is None:
            continue
        setattr(source_instance, field_name, resolved)
