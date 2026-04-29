from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional, Tuple

from apps.core.models import Classificacao, NivelHierarquico, TRANSACTION_TIME_SENTINEL


def parse_estrutura_codigo_mask(estrutura_codigo: str | None) -> List[int]:
    """
    Converte estrutura textual (ex.: ``X.X.0.0.00.000``) em máscara numérica.

    Cada segmento separado por ponto representa um grupo de dígitos.
    Exemplo:
      - X.X.0.0.00.000 -> [1, 1, 1, 1, 2, 3]
      - X.X.X.X.XX.X.X.XX.XXX -> [1, 1, 1, 1, 2, 1, 1, 2, 3]
    """
    if not estrutura_codigo:
        return []
    parts = [p.strip() for p in str(estrutura_codigo).split(".") if p and p.strip()]
    return [len(p) for p in parts]


def get_latest_active_vigente_classificacao(on_date: date | None = None) -> Optional[Classificacao]:
    ref_date = on_date or date.today()
    return (
        Classificacao.objects.filter(
            data_registro_fim=TRANSACTION_TIME_SENTINEL,
            data_vigencia_inicio__lte=ref_date,
            data_vigencia_fim__gte=ref_date,
        )
        .order_by("-data_vigencia_inicio", "-data_registro_inicio", "-pk")
        .first()
    )


def get_mask_from_classificacao_estrutura(
    classificacao: Classificacao | None, on_date: date | None = None
) -> Tuple[List[int], str]:
    """
    Obtém a máscara vigente da classificação via ``estrutura_codigo`` do nível
    mais detalhado (maior ``nivel_numero``).
    """
    if classificacao is None:
        return [], ""
    ref_date = on_date or date.today()
    nivel = (
        NivelHierarquico.objects.filter(
            classificacao_id=classificacao,
            data_registro_fim=TRANSACTION_TIME_SENTINEL,
            data_vigencia_inicio__lte=ref_date,
            data_vigencia_fim__gte=ref_date,
        )
        .exclude(estrutura_codigo__isnull=True)
        .exclude(estrutura_codigo__exact="")
        .order_by("-nivel_numero", "-nivel_ref", "-pk")
        .first()
    )
    if not nivel:
        # Fallback para classificações históricas selecionadas no formulário:
        # usa a estrutura ativa mais recente da própria classificação, mesmo fora
        # da vigência corrente.
        nivel = (
            NivelHierarquico.objects.filter(
                classificacao_id=classificacao,
                data_registro_fim=TRANSACTION_TIME_SENTINEL,
            )
            .exclude(estrutura_codigo__isnull=True)
            .exclude(estrutura_codigo__exact="")
            .order_by("-data_vigencia_inicio", "-nivel_numero", "-nivel_ref", "-pk")
            .first()
        )
    if not nivel:
        return [], ""
    estrutura = (nivel.estrutura_codigo or "").strip()
    return parse_estrutura_codigo_mask(estrutura), estrutura


def resolve_receita_cod_mask_context(
    classificacao: Classificacao | None,
    *,
    input_length: int | None = None,
    on_date: date | None = None,
) -> Dict[str, Any]:
    """
    Resolve contexto de máscara para UI/validação do código canônico.

    Regras:
    - com classificação selecionada: usa estrutura da própria classificação.
    - sem classificação: usa estrutura da classificação mais recente ativa/vigente hoje (default).
    - sem classificação e `input_length` diferente do default: tenta casar com estruturas
      históricas ativas (`data_registro_fim = sentinela`) e, havendo múltiplas, aplica a mais recente.
    """
    ref_date = on_date or date.today()
    selected = classificacao
    source = "selected_classificacao" if selected is not None else "fallback_default_latest_active_today"
    warning = ""
    match_count = 0

    if selected is None:
        selected = get_latest_active_vigente_classificacao(ref_date)

    digit_mask, estrutura_codigo = get_mask_from_classificacao_estrutura(selected, ref_date)
    total = sum(digit_mask) if digit_mask else None

    if classificacao is None and input_length and input_length > 0 and total and input_length != total:
        rows = (
            NivelHierarquico.objects.filter(data_registro_fim=TRANSACTION_TIME_SENTINEL)
            .exclude(estrutura_codigo__isnull=True)
            .exclude(estrutura_codigo__exact="")
            .order_by("-data_vigencia_inicio", "-data_registro_inicio", "-nivel_numero", "-pk")
            .values("classificacao_id", "data_vigencia_inicio", "data_vigencia_fim", "estrutura_codigo")
        )
        seen = set()
        matches: List[Dict[str, Any]] = []
        for row in rows:
            key = (
                row.get("classificacao_id"),
                row.get("data_vigencia_inicio"),
                row.get("data_vigencia_fim"),
                row.get("estrutura_codigo"),
            )
            if key in seen:
                continue
            seen.add(key)
            mask = parse_estrutura_codigo_mask(row.get("estrutura_codigo"))
            if mask and sum(mask) == input_length:
                matches.append({"mask": mask, "estrutura_codigo": row.get("estrutura_codigo") or ""})
        if matches:
            match_count = len(matches)
            digit_mask = matches[0]["mask"]
            estrutura_codigo = matches[0]["estrutura_codigo"]
            total = input_length
            source = "historical_length_match_latest"
            if match_count > 1:
                warning = (
                    f"Há {match_count} estruturas válidas para {input_length} dígitos; "
                    "foi aplicada a máscara da estrutura mais recente."
                )

    return {
        "digit_mask": digit_mask,
        "estrutura_codigo": estrutura_codigo,
        "numero_digitos": total,
        "source": source,
        "warning": warning,
        "match_count": match_count,
    }
