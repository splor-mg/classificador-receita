"""
Regras de consistência de `parent_item_id` em `ItemClassificacao`.

Ver `_dev/spec_parent_item_id.md`. A compatibilidade temporal entre pai e filho
considera apenas vigência (tempo válido), não o registro bitemporal ativo.
A contenção de vigência do filho no pai já é coberta por
`validate_vigencia_contained_in_fk_targets` quando `parent_item_id` está preenchido.
"""

from __future__ import annotations

from typing import List, Optional

from django.core.exceptions import ValidationError

from apps.core.models import NivelHierarquico


def _canonical_zero_segment(segment: str) -> bool:
    return bool(segment) and set(segment) == {"0"}


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
    Lista de `numero_digitos` por nível (1..K), na ordem crescente de `nivel_numero`,
    para a classificação e janela de vigência do item.

    Para cada `nivel_numero`, usa a linha mais recente em `data_registro_inicio` entre
    as que cobrem a vigência [vig_inicio, vig_fim] em tempo válido.
    """
    if vig_inicio is None or vig_fim is None or classificacao_pk is None:
        return None

    rows = (
        NivelHierarquico.objects.filter(
            classificacao_id=classificacao_pk,
            data_vigencia_inicio__lte=vig_inicio,
            data_vigencia_fim__gte=vig_fim,
        )
        .order_by("nivel_numero", "-data_registro_inicio")
        .values_list("nivel_numero", "numero_digitos", named=True)
    )

    by_level: dict[int, int] = {}
    for row in rows:
        if row.nivel_numero not in by_level:
            by_level[row.nivel_numero] = row.numero_digitos

    if not by_level:
        return None

    max_level = max(by_level)
    mask: List[int] = []
    for lvl in range(1, max_level + 1):
        if lvl not in by_level:
            return None
        mask.append(by_level[lvl])
    return mask


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
                {"parent_item_id": "Itens de nível 1 (raiz) não devem possuir item pai."}
            )
        return

    if parent is None:
        raise ValidationError(
            {
                "parent_item_id": (
                    "Itens de nível superior a 1 devem possuir um item pai."
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
            {"parent_item_id": "Um item não pode ser pai de si mesmo."}
        )

    if not getattr(parent, "matriz", False):
        raise ValidationError(
            {
                "parent_item_id": (
                    "O item pai deve ser de natureza matriz (agregador), não detalhe."
                )
            }
        )

    parent_nivel = getattr(parent, "nivel_id", None)
    if parent_nivel is None:
        raise ValidationError({"parent_item_id": "O item pai não possui nível hierárquico válido."})

    parent_n = getattr(parent_nivel, "nivel_numero", None)
    if parent_n != nivel_n - 1:
        raise ValidationError(
            {
                "parent_item_id": (
                    f"O item pai deve estar no nível imediatamente anterior "
                    f"(esperado nível {nivel_n - 1}, obtido {parent_n})."
                )
            }
        )

    child_class = getattr(instance, "classificacao_id", None)
    parent_class = getattr(parent, "classificacao_id", None)
    if child_class is None or parent_class is None:
        return

    if getattr(child_class, "pk", None) != getattr(parent_class, "pk", None):
        raise ValidationError(
            {
                "parent_item_id": (
                    "O item pai deve pertencer à mesma classificação que o item filho."
                )
            }
        )

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
                    "O código canônico do item pai não está alinhado à máscara de níveis "
                    "desta classificação e vigência."
                )
            }
        )

    idx = nivel_n - 1  # nível N => índice N-1

    for i in range(0, idx):
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
                        "Código do item pai insuficiente para validar a hierarquia "
                        "com o item filho."
                    ),
                }
            )
        if child_seg != parent_seg:
            raise ValidationError(
                {
                    "parent_item_id": (
                        "O código do item pai deve coincidir com o do filho em todos os "
                        f"níveis anteriores a {nivel_n}."
                    ),
                    "receita_cod": (
                        "Prefixo do código incompatível com o item pai indicado."
                    ),
                }
            )

    for i in range(idx, len(mask)):
        seg = parent_parts[i]
        if seg is None:
            continue
        if not _canonical_zero_segment(seg):
            raise ValidationError(
                {
                    "parent_item_id": (
                        f"A partir do nível {nivel_n}, o código do item pai deve usar "
                        "apenas zeros canônicos nos segmentos correspondentes."
                    )
                }
            )

    parent_tail = _extra_tail_after_mask(p_cod, mask)
    if parent_tail and not _canonical_zero_segment(parent_tail):
        raise ValidationError(
            {
                "parent_item_id": (
                    f"A partir do nível {nivel_n}, o código do item pai deve usar "
                    "apenas zeros canônicos, inclusive em dígitos excedentes "
                    "além da máscara."
                )
            }
        )

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
