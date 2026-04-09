"""
Validação de contenção de vigência: o intervalo [data_vigencia_inicio, data_vigencia_fim]
do registo em validação deve estar contido no intervalo de vigência de cada FK obrigatória
ou opcional preenchida (bitemporal ou base legal).
"""

from __future__ import annotations

from typing import List, Optional, Tuple

from django.core.exceptions import ValidationError
from django.db.models import Model


def vigencia_interval_contains(
    container_start,
    container_end,
    inner_start,
    inner_end,
) -> bool:
    """True se [inner_start, inner_end] ⊆ [container_start, container_end] (fechados)."""
    if container_start is None or container_end is None:
        return True
    if inner_start is None or inner_end is None:
        return True
    return container_start <= inner_start and inner_end <= container_end


def _get_vigencia(instance) -> Tuple[Optional[object], Optional[object]]:
    ini = getattr(instance, "data_vigencia_inicio", None)
    fim = getattr(instance, "data_vigencia_fim", None)
    return ini, fim


def _fk_target(instance, field_name: str) -> Optional[Model]:
    try:
        field = instance._meta.get_field(field_name)
    except Exception:
        return None
    if not getattr(field, "is_relation", False) or getattr(field, "many_to_many", False):
        return None
    rel_obj = getattr(instance, field.name, None)
    if rel_obj is not None:
        return rel_obj
    raw_id = getattr(instance, field.attname, None)
    if raw_id is None:
        return None
    related_model = field.remote_field.model
    return related_model.objects.filter(pk=raw_id).first()


def validate_vigencia_contained_in_fk_targets(
    instance,
    fk_fields: List[Tuple[str, str]],
) -> None:
    """
    Valida contenção de vigência face às FKs listadas.

    fk_fields: lista de (nome_do_campo_fk, rótulo curto para mensagem).

    Ignora FK nula. Alvos sem par de vigência completo são ignorados.
    """
    c_ini, c_fim = _get_vigencia(instance)
    if c_ini is None or c_fim is None:
        return

    errors = {}
    for field_name, related_label in fk_fields:
        target = _fk_target(instance, field_name)
        if target is None:
            continue
        p_ini, p_fim = _get_vigencia(target)
        if p_ini is None or p_fim is None:
            continue
        if not vigencia_interval_contains(p_ini, p_fim, c_ini, c_fim):
            errors[field_name] = ValidationError(
                (
                    f"O período de vigência deste registo ({c_ini} a {c_fim}) deve estar contido "
                    f"no período de vigência de {related_label} ({p_ini} a {p_fim})."
                ),
                code="vigencia_fk_containment",
            )

    if errors:
        raise ValidationError(errors)
