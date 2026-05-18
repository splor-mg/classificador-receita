"""
Regras de consistência de `parent_item_id` em `ItemClassificacao`.

Ver `_dev/spec_parent_item_id.md`. A compatibilidade temporal entre mãe e filho
considera apenas vigência (tempo válido), não o registro bitemporal ativo.
A contenção de vigência do filho no mãe já é coberta por
`validate_vigencia_contained_in_fk_targets` quando `parent_item_id` está preenchido.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from django.core.exceptions import ValidationError
from django.http import HttpRequest
from django.urls import reverse

from apps.core.admin_formatters import format_receita_cod_by_vigencia
from apps.core.code_mask import get_mask_for_classificacao_pk_vigencia


def _canonical_zero_segment(segment: str) -> bool:
    return bool(segment) and set(segment) == {"0"}


def _receita_cod_digits_only(canonical: str) -> str:
    """Apenas dígitos do código canônico (sem máscara / pontuação)."""
    return "".join(c for c in (canonical or "").strip() if c.isdigit())


def _extra_tail_after_mask(receita_cod: str, mask: List[int]) -> str:
    """Retorna dígitos excedentes além da soma da máscara (pode ser vazio)."""
    if not receita_cod or not mask:
        return ""
    consumed = sum(mask)
    if len(receita_cod) <= consumed:
        return ""
    return receita_cod[consumed:]


def digit_mask_for_classificacao_vigencia(
    classificacao_pk: int, vig_inicio, vig_fim
) -> Optional[List[int]]:
    """
    Resolve máscara canônica (via `estrutura_codigo`) para a classificação e vigência.
    """
    if vig_inicio is None or vig_fim is None or classificacao_pk is None:
        return None
    mask = get_mask_for_classificacao_pk_vigencia(classificacao_pk, vig_inicio, vig_fim)
    return mask or None


def split_receita_cod_segments_tolerant(
    receita_cod: str, mask: List[int]
) -> Optional[List[Optional[str]]]:
    """
    Segmenta `receita_cod` por máscara sem reprovar por tamanho total.

    - Se o código tiver dígitos suficientes para um segmento, retorna o recorte.
    - Se faltar dígito para completar o segmento, retorna None naquela posição.
    - Dígitos excedentes ao fim da máscara são ignorados.
    """
    if not receita_cod or not mask:
        return None

    parts: List[Optional[str]] = []
    pos = 0
    total = len(receita_cod)
    for width in mask:
        end = pos + width
        if end <= total:
            parts.append(receita_cod[pos:end])
        else:
            parts.append(None)
        pos = end
    return parts


def validate_item_receita_cod_level_consistency(instance) -> None:
    """
    Regra mínima para fechar o buraco de validação do nível 1.

    Para item de nível 1, o segmento do próprio nível deve estar discriminado
    (não apenas zeros) e todos os níveis posteriores (2...fim) devem estar
    zerados.
    """
    nivel = getattr(instance, "nivel_id", None)
    if nivel is None:
        return

    nivel_n = getattr(nivel, "nivel_numero", None)
    if nivel_n is None:
        return

    # Esta validação é propositalmente restrita ao nível 1.
    if nivel_n != 1:
        return

    c_cod = (getattr(instance, "receita_cod", None) or "").strip()
    if not c_cod:
        return

    child_class = getattr(instance, "classificacao_id", None)
    class_pk = getattr(child_class, "pk", None) if child_class is not None else None
    vig_ini = getattr(instance, "data_vigencia_inicio", None)
    vig_fim = getattr(instance, "data_vigencia_fim", None)

    mask = digit_mask_for_classificacao_vigencia(class_pk, vig_ini, vig_fim)
    if mask is None:
        raise ValidationError(
            {
                "receita_cod": (
                    "Não foi possível determinar a máscara de dígitos por nível "
                    "para esta classificação e vigência; verifique `nivel_hierarquico`."
                )
            }
        )

    if nivel_n > len(mask):
        raise ValidationError(
            {
                "nivel_id": (
                    f"O nível do item ({nivel_n}) não é compatível com a máscara "
                    f"da classificação ({len(mask)} níveis)."
                )
            }
        )

    child_parts = split_receita_cod_segments_tolerant(c_cod, mask)
    if child_parts is None:
        raise ValidationError(
            {
                "receita_cod": (
                    "Não foi possível segmentar o código canônico pela máscara de níveis "
                    "desta classificação e vigência."
                )
            }
        )

    idx = nivel_n - 1  # nível N => índice N-1
    child_level_seg = child_parts[idx]
    if child_level_seg is None:
        raise ValidationError(
            {
                "receita_cod": (
                    f"Código canônico insuficiente para validar o segmento do nível {nivel_n}."
                )
            }
        )

    if _canonical_zero_segment(child_level_seg):
        raise ValidationError(
            {
                "receita_cod": (
                    f"No nível {nivel_n}, o segmento do código deve estar discriminado "
                    "(não pode ser apenas zeros)."
                )
            }
        )

    for i in range(idx + 1, len(mask)):
        seg = child_parts[i]
        if seg is None:
            continue
        if not _canonical_zero_segment(seg):
            raise ValidationError(
                {
                    "receita_cod": (
                        "O código informado apresenta detalhamento (dígitos diferentes "
                        f"de zero) em níveis subsequentes ao nível {nivel_n}, que é o "
                        "nível definido para esta codificação."
                    )
                }
            )

    child_tail = _extra_tail_after_mask(c_cod, mask)
    if child_tail and not _canonical_zero_segment(child_tail):
        raise ValidationError(
            {
                "receita_cod": (
                    "O código informado apresenta detalhamento (dígitos diferentes "
                    f"de zero) em níveis subsequentes ao nível {nivel_n}, que é o "
                    "nível definido para esta codificação."
                )
            }
        )


def intermediate_levels_canonical_zero_error_message(
    child_nivel_numero: int, parent_nivel_numero: int
) -> str:
    """Mensagem de bloqueio (fluxo B) para níveis intermédios não canônicos entre mãe e filho."""
    return (
        f"Os campos correspondentes aos níveis entre o código atual (nível {child_nivel_numero}) "
        f"e o código mãe selecionado (nível {parent_nivel_numero}), devem conter apenas "
        "zeros canônicos."
    )


def find_intermediate_non_canonical_zero_message(
    *,
    receita_cod: str,
    parent_item: Any,
    child_nivel_numero: int,
    classificacao_pk: int,
    vig_ini,
    vig_fim,
) -> Optional[str]:
    """
  Retorna mensagem de erro em ``receita_cod`` quando há salto de nível e algum
  segmento intermédio do filho não é zero canônico; ``None`` se OK ou sem salto.
    """
    parent_nivel = getattr(parent_item, "nivel_id", None)
    parent_n = getattr(parent_nivel, "nivel_numero", None) if parent_nivel else None
    if parent_n is None or parent_n >= child_nivel_numero - 1:
        return None

    c_cod = _receita_cod_digits_only(receita_cod)
    p_cod = (getattr(parent_item, "receita_cod", None) or "").strip()
    if not c_cod or not p_cod:
        return None

    mask = digit_mask_for_classificacao_vigencia(classificacao_pk, vig_ini, vig_fim)
    if not mask:
        return None

    child_parts = split_receita_cod_segments_tolerant(c_cod, mask)
    if child_parts is None:
        return None

    for i in range(parent_n, child_nivel_numero - 1):
        seg = child_parts[i]
        if seg is None or not _canonical_zero_segment(seg):
            return intermediate_levels_canonical_zero_error_message(
                child_nivel_numero, parent_n
            )
    return None


def validate_intermediate_canonical_zeros_json_dict(
    *,
    parent_item: Any,
    child_nivel: Any,
    receita_cod_digits: str,
    vig_inicio,
    vig_fim,
    classificacao_pk: int,
) -> Dict[str, Any]:
    """Payload JSON para validação pré-submit (fluxo B) no admin."""
    if not parent_item or not child_nivel:
        return {"ok": True}
    child_n = getattr(child_nivel, "nivel_numero", None)
    if child_n is None or child_n <= 1:
        return {"ok": True}
    message = find_intermediate_non_canonical_zero_message(
        receita_cod=receita_cod_digits,
        parent_item=parent_item,
        child_nivel_numero=child_n,
        classificacao_pk=classificacao_pk,
        vig_ini=vig_inicio,
        vig_fim=vig_fim,
    )
    if message:
        return {"ok": False, "message": message}
    return {"ok": True}


def validate_item_parent_item_rules(instance) -> None:
    """
    Aplica regras de `_dev/spec_parent_item_id.md` (exceto contenção de vigência,
    já tratada em `validate_vigencia_contained_in_fk_targets`).

    Levanta `ValidationError` com chaves de campo quando aplicável.
    """
    nivel = getattr(instance, "nivel_id", None)
    if nivel is None:
        return

    nivel_n = getattr(nivel, "nivel_numero", None)
    if nivel_n is None:
        return

    parent = getattr(instance, "parent_item_id", None)

    if nivel_n == 1:
        if parent is not None:
            raise ValidationError(
                {"parent_item_id": "Itens de nível 1 (raiz) não devem possuir item mãe."}
            )
        return

    if parent is None:
        raise ValidationError(
            {
                "parent_item_id": (
                    "Itens de nível superior a 1 devem possuir um item mãe."
                )
            }
        )

    self_pk = getattr(instance, "pk", None)
    parent_pk = getattr(parent, "pk", None)
    if (
        self_pk is not None
        and parent_pk is not None
        and self_pk == parent_pk
    ):
        raise ValidationError(
            {"parent_item_id": "Um item não pode ser mãe de si mesmo."}
        )

    if not getattr(parent, "matriz", False):
        raise ValidationError(
            {
                "parent_item_id": (
                    "O item mãe deve ser de natureza matriz (agregador), não detalhe."
                )
            }
        )

    parent_nivel = getattr(parent, "nivel_id", None)
    if parent_nivel is None:
        raise ValidationError({"parent_item_id": "O item mãe não possui nível hierárquico válido."})

    parent_n = getattr(parent_nivel, "nivel_numero", None)
    if parent_n is None:
        raise ValidationError({"parent_item_id": "O item mãe não possui nível hierárquico válido."})

    if parent_n >= nivel_n:
        raise ValidationError(
            {
                "parent_item_id": (
                    "O item mãe deve estar em nível hierárquico estritamente acima "
                    f"(menor número de nível) do item filho (nível do filho: {nivel_n})."
                )
            }
        )

    child_class = getattr(instance, "classificacao_id", None)
    parent_class = getattr(parent, "classificacao_id", None)
    if child_class is None or parent_class is None:
        return

    c_cod = (getattr(instance, "receita_cod", None) or "").strip()
    p_cod = (getattr(parent, "receita_cod", None) or "").strip()
    vig_ini = getattr(instance, "data_vigencia_inicio", None)
    vig_fim = getattr(instance, "data_vigencia_fim", None)

    if not c_cod or not p_cod:
        return

    class_pk = getattr(child_class, "pk", None)
    mask = digit_mask_for_classificacao_vigencia(class_pk, vig_ini, vig_fim)
    if mask is None:
        raise ValidationError(
            {
                "receita_cod": (
                    "Não foi possível determinar a máscara de dígitos por nível "
                    "para esta classificação e vigência; verifique `nivel_hierarquico`."
                )
            }
        )

    if nivel_n > len(mask):
        raise ValidationError(
            {
                "nivel_id": (
                    f"O nível do item ({nivel_n}) não é compatível com a máscara "
                    f"da classificação ({len(mask)} níveis)."
                )
            }
        )

    if parent_n > len(mask):
        raise ValidationError(
            {
                "parent_item_id": (
                    f"O nível do item mãe ({parent_n}) não é compatível com a máscara "
                    f"da classificação ({len(mask)} níveis)."
                )
            }
        )

    child_parts = split_receita_cod_segments_tolerant(c_cod, mask)
    parent_parts = split_receita_cod_segments_tolerant(p_cod, mask)
    if child_parts is None:
        raise ValidationError(
            {
                "receita_cod": (
                    "Não foi possível segmentar o código canônico pela máscara de níveis "
                    "desta classificação e vigência."
                )
            }
        )
    if parent_parts is None:
        raise ValidationError(
            {
                "parent_item_id": (
                    "O código canônico do item mãe não está alinhado à máscara de níveis "
                    "desta classificação e vigência."
                )
            }
        )

    idx = nivel_n - 1  # nível L => índice L-1

    # Prefixo comum: níveis 1..LP (índices 0..parent_n-1) iguais entre filho e pai.
    for i in range(0, parent_n):
        child_seg = child_parts[i]
        parent_seg = parent_parts[i]
        if child_seg is None or parent_seg is None:
            raise ValidationError(
                {
                    "receita_cod": (
                        "Código canônico insuficiente para validar os níveis anteriores "
                        "ao nível do item."
                    ),
                    "parent_item_id": (
                        "Código do item mãe insuficiente para validar a hierarquia "
                        "com o item filho."
                    ),
                }
            )
        if child_seg != parent_seg:
            raise ValidationError(
                {
                    "parent_item_id": (
                        "O código do item mãe deve coincidir com o do filho em todos os "
                        f"níveis até {parent_n} (nível do pai)."
                    ),
                    "receita_cod": (
                        "Prefixo do código incompatível com o item mãe indicado."
                    ),
                }
            )

    # Cauda do pai: a partir do nível LP+1, apenas zeros canônicos.
    for i in range(parent_n, len(mask)):
        seg = parent_parts[i]
        if seg is None:
            continue
        if not _canonical_zero_segment(seg):
            raise ValidationError(
                {
                    "parent_item_id": (
                        f"A partir do nível {parent_n + 1}, o código do item mãe deve usar "
                        "apenas zeros canônicos nos segmentos correspondentes."
                    )
                }
            )

    parent_tail = _extra_tail_after_mask(p_cod, mask)
    if parent_tail and not _canonical_zero_segment(parent_tail):
        raise ValidationError(
            {
                "parent_item_id": (
                    f"A partir do nível {parent_n + 1}, o código do item mãe deve usar "
                    "apenas zeros canônicos, inclusive em dígitos excedentes "
                    "além da máscara."
                )
            }
        )

    # Salto de nível: níveis LP+1 .. L-1 no filho devem ser zeros canônicos (só receita_cod).
    if parent_n < nivel_n - 1:
        jump_msg = find_intermediate_non_canonical_zero_message(
            receita_cod=c_cod,
            parent_item=parent,
            child_nivel_numero=nivel_n,
            classificacao_pk=class_pk,
            vig_ini=vig_ini,
            vig_fim=vig_fim,
        )
        if jump_msg:
            raise ValidationError({"receita_cod": jump_msg})

    child_level_seg = child_parts[idx]
    if child_level_seg is None:
        raise ValidationError(
            {
                "receita_cod": (
                    f"Código canônico insuficiente para validar o segmento do nível {nivel_n}."
                )
            }
        )

    if _canonical_zero_segment(child_level_seg):
        raise ValidationError(
            {
                "receita_cod": (
                    f"No nível {nivel_n}, o segmento do código deve estar discriminado "
                    "(não pode ser apenas zeros)."
                )
            }
        )

    for i in range(idx + 1, len(mask)):
        seg = child_parts[i]
        if seg is None:
            continue
        if not _canonical_zero_segment(seg):
            raise ValidationError(
                {
                    "receita_cod": (
                        "O código informado apresenta detalhamento (dígitos diferentes "
                        f"de zero) em níveis subsequentes ao nível {nivel_n}, que é o "
                        "nível definido para esta codificação."
                    )
                }
            )

    child_tail = _extra_tail_after_mask(c_cod, mask)
    if child_tail and not _canonical_zero_segment(child_tail):
        raise ValidationError(
            {
                "receita_cod": (
                    "O código informado apresenta detalhamento (dígitos diferentes "
                    f"de zero) em níveis subsequentes ao nível {nivel_n}, que é o "
                    "nível definido para esta codificação."
                )
            }
        )


def analyze_intermediate_items_for_level_jump(
    *,
    classificacao_pk: int,
    parent_item,
    child_nivel_numero: int,
    vig_ini,
    vig_fim,
    reg_sent,
    sample_limit: int = 5,
    exclude_receita_cod: Optional[str] = None,
) -> Dict[str, object]:
    """
    Conta e amostra itens intermediários para o aviso de salto de nível.

    Critério (códigos no BD sem pontuação de máscara):

    - radical numérico = primeiros dígitos do ``receita_cod`` do mãe até ao fim
      do nível do mãe (soma das larguras ``mask[0:LP]``);
    - ``classificacao_pk``: PK da classificação usada na query (no admin, o do
      **formulário** de criação);
    - registo ativo (``data_registro_fim`` sentinela);
    - sobreposição de vigência com ``vig_ini``/``vig_fim`` (no admin: **só** as
      datas do formulário);
    - ``receita_cod__startswith=radical``;
    - ``nivel_numero`` entre ``LP+1`` e ``L_filho-1`` (inclusive);
    - segmento do código na posição do próprio nível do item não é zero canônico.

    Se ``digit_mask_for_classificacao_vigencia`` com ``(classificacao_pk, vig_ini,
    vig_fim)`` devolver máscara vazia, tenta-se de novo com a vigência do **pai**
    apenas para resolver a máscara (não altera o filtro de vigência da query).
    """
    from django.urls import reverse

    from apps.core.models import ItemClassificacao

    parent_nivel = getattr(parent_item, "nivel_id", None)
    parent_n = getattr(parent_nivel, "nivel_numero", None)
    empty: Dict[str, object] = {
        "count": 0,
        "nivel_numeros": [],
        "nivel_semantic_by_numero": {},
        "samples": [],
    }
    if parent_n is None or child_nivel_numero is None:
        return empty
    if parent_n >= child_nivel_numero - 1:
        return empty

    mask = digit_mask_for_classificacao_vigencia(classificacao_pk, vig_ini, vig_fim)
    if not mask:
        pvi = getattr(parent_item, "data_vigencia_inicio", None)
        pvf = getattr(parent_item, "data_vigencia_fim", None)
        if pvi is not None and pvf is not None:
            mask = digit_mask_for_classificacao_vigencia(classificacao_pk, pvi, pvf)
    if not mask or parent_n > len(mask):
        return empty

    p_cod = (getattr(parent_item, "receita_cod", None) or "").strip()
    p_digits = _receita_cod_digits_only(p_cod)
    radical_len = int(sum(mask[:parent_n]))
    if radical_len <= 0 or len(p_digits) < radical_len:
        return empty
    radical = p_digits[:radical_len]

    exclude_digits = _receita_cod_digits_only(exclude_receita_cod) if exclude_receita_cod else ""

    nivel_min = parent_n + 1
    nivel_max = child_nivel_numero - 1

    qs = (
        ItemClassificacao.objects.filter(
            classificacao_id_id=classificacao_pk,
            data_registro_fim=reg_sent,
            receita_cod__startswith=radical,
            data_vigencia_inicio__lte=vig_fim,
            data_vigencia_fim__gte=vig_ini,
            nivel_id__nivel_numero__gte=nivel_min,
            nivel_id__nivel_numero__lte=nivel_max,
        )
        .select_related("nivel_id")
        .order_by("-data_vigencia_inicio", "-data_registro_inicio", "-pk")
    )

    count = 0
    nivel_numeros: set = set()
    nivel_semantic_by_numero: Dict[int, str] = {}
    samples: List[Dict[str, str]] = []
    for it in qs.iterator(chunk_size=100):
        it_cod = (it.receita_cod or "").strip()
        if exclude_digits and _receita_cod_digits_only(it_cod) == exclude_digits:
            continue
        parts = split_receita_cod_segments_tolerant(it_cod, mask)
        if not parts:
            continue
        nn = getattr(it.nivel_id, "nivel_numero", None)
        if nn is None or nn < nivel_min or nn > nivel_max:
            continue
        idx = nn - 1
        if idx < 0 or idx >= len(parts):
            continue
        seg = parts[idx]
        if seg is None or _canonical_zero_segment(seg):
            continue
        count += 1
        nid_str = (getattr(it.nivel_id, "nivel_id", None) or "").strip()
        nivel_numeros.add(nn)
        if nid_str and nn not in nivel_semantic_by_numero:
            nivel_semantic_by_numero[nn] = nid_str
        if len(samples) < sample_limit:
            link = reverse(
                f"admin:{it._meta.app_label}_{it._meta.model_name}_change",
                args=[it.pk],
            )
            samples.append(
                {
                    "pk": str(it.pk),
                    "receita_cod": it.receita_cod or "",
                    "display_label": (
                        f"{it.receita_cod} - {it.receita_nome or it.item_id or ''}"
                    ).strip(" -"),
                    "admin_url": link,
                    "nivel_numero": str(nn) if nn is not None else "",
                }
            )

    return {
        "count": count,
        "nivel_numeros": sorted(nivel_numeros),
        "nivel_semantic_by_numero": nivel_semantic_by_numero,
        "samples": samples,
    }


def find_intermediate_items_for_level_jump(
    *,
    classificacao_pk: int,
    parent_item,
    child_nivel_numero: int,
    vig_ini,
    vig_fim,
    reg_sent,
    limit: int = 5,
    exclude_receita_cod: Optional[str] = None,
) -> List[Dict[str, str]]:
    data = analyze_intermediate_items_for_level_jump(
        classificacao_pk=classificacao_pk,
        parent_item=parent_item,
        child_nivel_numero=child_nivel_numero,
        vig_ini=vig_ini,
        vig_fim=vig_fim,
        reg_sent=reg_sent,
        sample_limit=limit,
        exclude_receita_cod=exclude_receita_cod,
    )
    return data["samples"]  # type: ignore[return-value]


def _warn_modal_nivel_semantic_id(nobj: Any) -> str:
    if not nobj:
        return ""
    nid = (getattr(nobj, "nivel_id", None) or "").strip()
    num = getattr(nobj, "nivel_numero", None)
    return nid or (f"n.º {num}" if num is not None else "")


def _warn_modal_format_nivel_labels_pt(nums: List[int], sem_by_num: Dict[int, str]) -> str:
    labels = []
    for n in nums:
        labels.append((sem_by_num.get(n) or "").strip() or f"n.º {n}")
    if not labels:
        return ""
    if len(labels) == 1:
        return labels[0]
    if len(labels) == 2:
        return f"{labels[0]} e {labels[1]}"
    return ", ".join(labels[:-1]) + f" e {labels[-1]}"


def warn_parent_level_jump_json_dict(
    request: HttpRequest,
    *,
    parent_item: Any,
    child_nivel: Any,
    vig_inicio: Any,
    vig_fim: Any,
    classificacao_form_pk: int,
    child_receita_cod_digits: str,
    reg_sent: Any,
) -> Dict[str, Any]:
    """
    Monta o dicionário JSON para o aviso de salto de nível no admin (antes do submit).

    Retorna ``{"ok": true, "level_jump": false}`` quando não há salto estrutural
    (mãe já está em ``L_filho - 1``) ou dados insuficientes; caso contrário retorna
    o payload completo com ``level_jump: true``, análise de intermediários e
    códigos mascarados para o modal.
    """
    from apps.core.models import ItemClassificacao

    child_n = getattr(child_nivel, "nivel_numero", None)
    parent_nivel = getattr(parent_item, "nivel_id", None)
    parent_n = getattr(parent_nivel, "nivel_numero", None) if parent_nivel else None

    if child_n is None or child_n <= 1 or parent_n is None or parent_n >= child_n:
        return {"ok": True, "level_jump": False}

    if parent_n == child_n - 1:
        return {"ok": True, "level_jump": False}

    busca_intermediarios_class_pk = classificacao_form_pk
    analysis = analyze_intermediate_items_for_level_jump(
        classificacao_pk=busca_intermediarios_class_pk,
        parent_item=parent_item,
        child_nivel_numero=child_n,
        vig_ini=vig_inicio,
        vig_fim=vig_fim,
        reg_sent=reg_sent,
        sample_limit=3,
        exclude_receita_cod=child_receita_cod_digits or None,
    )
    icount = int(analysis["count"])
    level_nums = list(analysis["nivel_numeros"])
    sem_by_num = analysis.get("nivel_semantic_by_numero") or {}
    sem_by_num_int = {int(k): str(v) for k, v in sem_by_num.items()}

    mask_cache: Dict[str, Any] = {}
    parent_cod_masked = format_receita_cod_by_vigencia(
        parent_item.receita_cod or "", vig_inicio, vig_fim, mask_cache
    )
    if parent_cod_masked == (parent_item.receita_cod or "") and parent_item.receita_cod:
        parent_cod_masked = format_receita_cod_by_vigencia(
            parent_item.receita_cod,
            getattr(parent_item, "data_vigencia_inicio", None),
            getattr(parent_item, "data_vigencia_fim", None),
            mask_cache,
        )

    child_cod_masked = ""
    if child_receita_cod_digits:
        child_cod_masked = format_receita_cod_by_vigencia(
            child_receita_cod_digits, vig_inicio, vig_fim, mask_cache
        )
        if child_cod_masked == child_receita_cod_digits:
            child_cod_masked = format_receita_cod_by_vigencia(
                child_receita_cod_digits, None, None, {}
            )

    parent_nivel_sem = _warn_modal_nivel_semantic_id(parent_nivel)
    child_nivel_sem = _warn_modal_nivel_semantic_id(child_nivel)

    parent_abs = request.build_absolute_uri(
        reverse(
            f"admin:{parent_item._meta.app_label}_{parent_item._meta.model_name}_change",
            args=[parent_item.pk],
        )
    )

    niveis_txt = _warn_modal_format_nivel_labels_pt(level_nums, sem_by_num_int)
    if not niveis_txt and icount > 0:
        niveis_txt = "nos níveis intermediários"
    count_disp = f"{icount:02d}" if icount < 100 else str(icount)

    ic_model = ItemClassificacao
    intermediate_rows: List[Dict[str, Any]] = []
    for row in list(analysis["samples"]):
        rc = row.get("receita_cod") or ""
        masked = format_receita_cod_by_vigencia(rc, vig_inicio, vig_fim, mask_cache)
        if masked == rc and rc:
            masked = format_receita_cod_by_vigencia(rc, None, None, mask_cache)
        dl = (row.get("display_label") or "").strip()
        nome_rest = ""
        if rc and dl.startswith(rc):
            nome_rest = dl[len(rc) :].lstrip(" -").strip()
        else:
            parts = dl.split(" - ", 1)
            if len(parts) > 1:
                nome_rest = parts[1].strip()
        list_line = f"{masked} - {nome_rest}".strip(" -") if nome_rest else masked
        intermediate_rows.append(
            {
                "cod_masked": masked,
                "nome": nome_rest,
                "list_line": list_line,
                "admin_absolute_url": request.build_absolute_uri(
                    reverse(
                        f"admin:{ic_model._meta.app_label}_{ic_model._meta.model_name}_change",
                        args=[int(row["pk"])],
                    )
                ),
            }
        )

    return {
        "ok": True,
        "level_jump": True,
        "parent": {
            "cod_masked": parent_cod_masked,
            "admin_absolute_url": parent_abs,
            "nivel_semantic": parent_nivel_sem,
        },
        "child": {
            "cod_masked": child_cod_masked or child_receita_cod_digits,
            "nivel_semantic": child_nivel_sem,
        },
        "intermediate_count": icount,
        "intermediate_count_display": count_disp,
        "intermediate_niveis_label": niveis_txt,
        "intermediate_rows": intermediate_rows,
        "has_intermediate_codes": icount > 0,
    }
