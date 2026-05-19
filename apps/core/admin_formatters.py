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


def _apply_digit_mask(codigo, digit_mask):
    """Aplica ``digit_mask`` em ``codigo`` ou retorna ``None`` se incompatível.

    A máscara é considerada compatível somente quando:

    * é não-vazia;
    * nenhum elemento é zero/``None``/falsy;
    * a soma dos ``numero_digitos`` é exatamente ``len(codigo)``.

    Em qualquer outro caso devolve ``None`` para sinalizar incompatibilidade ao
    chamador (que decide entre buscar uma resolução alternativa ou devolver o
    código bruto).
    """
    if not digit_mask:
        return None
    if any(not n for n in digit_mask):
        return None
    if sum(digit_mask) != len(codigo):
        return None

    partes = []
    pos = 0
    for tamanho in digit_mask:
        partes.append(codigo[pos:pos + tamanho])
        pos += tamanho
    return ".".join(partes)


def format_receita_cod_by_vigencia(codigo, vigencia_inicio, vigencia_fim, cache):
    if not codigo:
        return codigo
    digit_mask = get_active_digit_mask_for_vigencia(cache, vigencia_inicio, vigencia_fim)
    formatted = _apply_digit_mask(codigo, digit_mask)
    if formatted is not None:
        return formatted
    return codigo


def _resolve_secondary_digit_mask_for_changelist(record_vigencia_fim, cache):
    """Resolve a máscara secundária (apenas para apresentação na *changelist*).

    Para cada ``nivel_ref`` distinto, escolhe entre as linhas ativas de
    ``NivelHierarquico`` (``data_registro_fim = TRANSACTION_TIME_SENTINEL``)
    aquela cuja vigência **contém** ``record_vigencia_fim``, preferindo:

    1. **maior** ``data_vigencia_fim`` (versão que se estende mais para o
       futuro — interpreta-se "vigência canônica do presente/futuro");
    2. **mais recente** ``data_registro_inicio`` como desempate de transação.

    Esta resolução só é invocada quando a regra primária estrita
    (``get_active_digit_mask_for_vigencia``) falha para a janela de vigência do
    registro. Ela é **exclusiva da changelist** — não deve ser usada em
    formulários, lookups, validações, sugestões de código filho ou qualquer
    outro contexto onde a regra estrita é a única política aceitável.

    Ver spec ``_dev/spec_itemClassificacao_mascara_apresentacao.md``.
    """
    if not record_vigencia_fim:
        return None

    cache_key = ("secondary-changelist", record_vigencia_fim)
    if cache_key in cache:
        return cache[cache_key]

    qs = (
        NivelHierarquico.objects.filter(
            data_registro_fim=TRANSACTION_TIME_SENTINEL,
            data_vigencia_inicio__lte=record_vigencia_fim,
            data_vigencia_fim__gte=record_vigencia_fim,
        )
        .order_by(
            "nivel_ref",
            "-data_vigencia_fim",
            "-data_registro_inicio",
        )
        .values("nivel_ref", "numero_digitos")
    )

    digit_mask = []
    seen_nivel_refs = set()
    for row in qs:
        nivel_ref = row["nivel_ref"]
        if nivel_ref in seen_nivel_refs:
            continue
        seen_nivel_refs.add(nivel_ref)
        digit_mask.append(row["numero_digitos"])

    cache[cache_key] = digit_mask
    return digit_mask


def format_receita_cod_for_changelist(codigo, vigencia_inicio, vigencia_fim, cache):
    """Formata ``receita_cod`` para apresentação na changelist de ``ItemClassificacao``.

    Aplica resolução em dois níveis:

    * **Primário (estrito)**: idêntico a ``format_receita_cod_by_vigencia`` —
      exige uma única linha ativa de ``NivelHierarquico`` cuja vigência contenha
      integralmente a janela do registro, por ``nivel_ref``.
    * **Secundário (apenas changelist)**: aciona-se quando o primário não
      produz uma máscara compatível. Por ``nivel_ref``, escolhe a linha ativa
      ancorada em ``record.data_vigencia_fim``, preferindo maior
      ``data_vigencia_fim`` própria e desempatando por ``data_registro_inicio``
      mais recente (ver ``_resolve_secondary_digit_mask_for_changelist``).

    Quando ambos os níveis falham, devolve ``codigo`` bruto — comportamento
    discreto, igual ao adotado fora da changelist.

    Justificativa de existência (em contraste com ``format_receita_cod_by_vigencia``):
    a changelist mistura linhas de vigências distintas. Sem este helper, ao
    haver split bitemporal num ``NivelHierarquico`` qualquer, registros cuja
    vigência não esteja inteiramente contida numa única linha do nível
    apareceriam **sem máscara**, enquanto outros (alinhados à nova faixa)
    apareceriam **com máscara** — assimetria visual confusa. Ver spec
    ``_dev/spec_itemClassificacao_mascara_apresentacao.md``.
    """
    if not codigo:
        return codigo

    strict_mask = get_active_digit_mask_for_vigencia(cache, vigencia_inicio, vigencia_fim)
    formatted = _apply_digit_mask(codigo, strict_mask)
    if formatted is not None:
        return formatted

    secondary_mask = _resolve_secondary_digit_mask_for_changelist(vigencia_fim, cache)
    formatted = _apply_digit_mask(codigo, secondary_mask)
    if formatted is not None:
        return formatted

    return codigo


def get_active_vigencia_masks():
    masks = []
    qs = (
        NivelHierarquico.objects.filter(data_registro_fim=TRANSACTION_TIME_SENTINEL)
        .order_by("data_vigencia_inicio", "data_vigencia_fim", "nivel_ref")
        .values("id", "data_vigencia_inicio", "data_vigencia_fim", "numero_digitos")
    )

    current_key = None
    current_digits = []
    current_level_pks = []
    for row in qs:
        key = (row["data_vigencia_inicio"], row["data_vigencia_fim"])
        if key != current_key:
            if current_key is not None:
                masks.append(
                    {
                        "vigencia_inicio": current_key[0].isoformat(),
                        "vigencia_fim": current_key[1].isoformat(),
                        "digit_mask": current_digits,
                        "level_pks": current_level_pks,
                    }
                )
            current_key = key
            current_digits = []
            current_level_pks = []
        current_digits.append(row["numero_digitos"])
        current_level_pks.append(row["id"])

    if current_key is not None:
        masks.append(
            {
                "vigencia_inicio": current_key[0].isoformat(),
                "vigencia_fim": current_key[1].isoformat(),
                "digit_mask": current_digits,
                "level_pks": current_level_pks,
            }
        )
    return masks
