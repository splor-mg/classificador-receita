from apps.core.models import NivelHierarquico, TRANSACTION_TIME_SENTINEL


def get_active_digit_mask_for_vigencia(cache, vigencia_inicio, vigencia_fim):
    if not vigencia_inicio or not vigencia_fim:
        return None
    cache_key = (vigencia_inicio, vigencia_fim)
    if cache_key in cache:
        return cache[cache_key]

    digit_mask = list(
        NivelHierarquico.objects.filter(
            data_registro_fim=TRANSACTION_TIME_SENTINEL,
            data_vigencia_inicio__lte=vigencia_inicio,
            data_vigencia_fim__gte=vigencia_fim,
        )
        .order_by("nivel_ref")
        .values_list("numero_digitos", flat=True)
    )
    cache[cache_key] = digit_mask
    return digit_mask


def format_receita_cod_by_vigencia(codigo, vigencia_inicio, vigencia_fim, cache):
    digit_mask = get_active_digit_mask_for_vigencia(cache, vigencia_inicio, vigencia_fim)
    if not codigo or not digit_mask:
        return codigo
    if any(not n for n in digit_mask):
        return codigo
    if sum(digit_mask) != len(codigo):
        return codigo

    partes = []
    pos = 0
    for tamanho in digit_mask:
        partes.append(codigo[pos:pos + tamanho])
        pos += tamanho
    return ".".join(partes)


def get_active_vigencia_masks():
    masks = []
    qs = (
        NivelHierarquico.objects.filter(data_registro_fim=TRANSACTION_TIME_SENTINEL)
        .order_by("data_vigencia_inicio", "data_vigencia_fim", "nivel_ref")
        .values("data_vigencia_inicio", "data_vigencia_fim", "numero_digitos")
    )

    current_key = None
    current_digits = []
    for row in qs:
        key = (row["data_vigencia_inicio"], row["data_vigencia_fim"])
        if key != current_key:
            if current_key is not None:
                masks.append(
                    {
                        "vigencia_inicio": current_key[0].isoformat(),
                        "vigencia_fim": current_key[1].isoformat(),
                        "digit_mask": current_digits,
                    }
                )
            current_key = key
            current_digits = []
        current_digits.append(row["numero_digitos"])

    if current_key is not None:
        masks.append(
            {
                "vigencia_inicio": current_key[0].isoformat(),
                "vigencia_fim": current_key[1].isoformat(),
                "digit_mask": current_digits,
            }
        )
    return masks
