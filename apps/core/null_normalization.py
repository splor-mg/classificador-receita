from django.db import models as dj_models


PLACEHOLDER_NULL_TOKENS = {"NULL", "-"}


def normalize_placeholder_text_value(value):
    """
    Normaliza placeholders textuais para ausência de dado canônica.

    Regras:
    - "NULL" (qualquer caixa) -> None
    - "-" (apenas hífen) -> None
    - demais valores permanecem inalterados
    """
    if not isinstance(value, str):
        return value
    stripped = value.strip()
    if stripped == "-":
        return None
    if stripped.upper() == "NULL":
        return None
    return value


def normalize_text_field_value(model, field_name: str, value):
    """
    Aplica normalização somente a campos textuais (CharField/TextField).
    """
    try:
        field_obj = model._meta.get_field(field_name)
    except Exception:
        return value

    if isinstance(field_obj, (dj_models.CharField, dj_models.TextField)):
        return normalize_placeholder_text_value(value)
    return value

