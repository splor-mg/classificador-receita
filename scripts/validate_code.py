#!/usr/bin/env python3
"""
Valida a quantidade de dígitos de receita_cod conforme a máscara canônica
(`estrutura_codigo`) vigente (SCD-2 / bitemporal).

Critério: para cada item, resolve níveis hierárquicos da mesma classificação cujo
período de REGISTRO compreenda o período de registro do item e cuja VIGÊNCIA
compreenda a vigência do item. A máscara canônica é derivada de
`estrutura_codigo`; len(receita_cod) deve igualar a soma dessa máscara.

Uso:
    poetry run task validar-codigos
    python scripts/validate_code.py --items data/item_classificacao.csv --niveis docs/assets/seed_nivel_hierarquico.csv
"""

from __future__ import annotations

import argparse
import csv
import sys
from datetime import date, datetime
from pathlib import Path


def _parse_date(s: str) -> date | datetime:
    """Parse string as date or datetime."""
    s = (s or "").strip()
    if not s:
        raise ValueError("data vazia")
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            out = datetime.strptime(s, fmt)
            return out if " " in s or "T" in s else out.date()
        except ValueError:
            continue
    raise ValueError(f"formato de data não reconhecido: {s!r}")


def _normalize_to_date(d: date | datetime) -> date:
    return d.date() if isinstance(d, datetime) else d


def _registro_item_contido_em_registro_class(
    item_ri: date | datetime,
    item_rf: date | datetime,
    class_ri: date | datetime,
    class_rf: date | datetime,
) -> bool:
    """Verdadeiro se o período de registro do item está contido no período de registro da classificação."""
    # Comparação considerando apenas a parte de data quando um é date e outro datetime
    item_ri_d = _normalize_to_date(item_ri)
    item_rf_d = _normalize_to_date(item_rf)
    class_ri_d = _normalize_to_date(class_ri)
    class_rf_d = _normalize_to_date(class_rf)
    return class_ri_d <= item_ri_d and item_rf_d <= class_rf_d


def _vigencia_item_contida_em_vigencia_class(
    item_vi: date | datetime,
    item_vf: date | datetime,
    class_vi: date | datetime,
    class_vf: date | datetime,
) -> bool:
    """Verdadeiro se a vigência do item está contida na vigência da classificação."""
    item_vi_d = _normalize_to_date(item_vi)
    item_vf_d = _normalize_to_date(item_vf)
    class_vi_d = _normalize_to_date(class_vi)
    class_vf_d = _normalize_to_date(class_vf)
    return class_vi_d <= item_vi_d and item_vf_d <= class_vf_d


def parse_estrutura_codigo_mask(estrutura_codigo: str | None) -> list[int]:
    """Converte estrutura textual (ex.: X.X.0.0.00.000) em máscara numérica."""
    if not estrutura_codigo:
        return []
    parts = [p.strip() for p in str(estrutura_codigo).split(".") if p and p.strip()]
    return [len(p) for p in parts]


def load_niveis(path: Path) -> list[dict]:
    """Carrega linhas do CSV de níveis hierárquicos; normaliza datas."""
    rows = []
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            r = dict(row)
            for key in (
                "data_vigencia_inicio",
                "data_vigencia_fim",
                "data_registro_inicio",
                "data_registro_fim",
            ):
                if key in r and r[key]:
                    r[key] = _parse_date(r[key])
            rows.append(r)
    return rows


def load_items(path: Path) -> list[dict]:
    """Carrega linhas do CSV de itens; normaliza datas."""
    rows = []
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            r = dict(row)
            for key in (
                "data_vigencia_inicio",
                "data_vigencia_fim",
                "data_registro_inicio",
                "data_registro_fim",
            ):
                if key in r and r[key]:
                    r[key] = _parse_date(r[key])
            rows.append(r)
    return rows


def find_niveis_for_item(
    item: dict,
    niveis: list[dict],
) -> list[dict]:
    """
    Retorna as linhas de nível que:
    1) têm o mesmo classificacao_id do item;
    2) cujo período de REGISTRO compreende o período de registro do item;
    3) cuja VIGÊNCIA compreende a vigência do item.
    """
    cid = item.get("classificacao_id")
    item_ri = item.get("data_registro_inicio")
    item_rf = item.get("data_registro_fim")
    item_vi = item.get("data_vigencia_inicio")
    item_vf = item.get("data_vigencia_fim")
    if not all([cid, item_ri, item_rf, item_vi, item_vf]):
        return []

    out = []
    for n in niveis:
        if n.get("classificacao_id") != cid:
            continue
        c_ri = n.get("data_registro_inicio")
        c_rf = n.get("data_registro_fim")
        c_vi = n.get("data_vigencia_inicio")
        c_vf = n.get("data_vigencia_fim")
        if not all([c_ri, c_rf, c_vi, c_vf]):
            continue
        if not _registro_item_contido_em_registro_class(item_ri, item_rf, c_ri, c_rf):
            continue
        if not _vigencia_item_contida_em_vigencia_class(item_vi, item_vf, c_vi, c_vf):
            continue
        out.append(n)
    return out


ITEM_SEMANTIC_PREFIX = "IT-"


def validate_item_semantic_id(item: dict) -> tuple[bool, str | None]:
    """item_id deve ser IT-{receita_cod}."""
    cod = (item.get("receita_cod") or "").strip()
    iid = (item.get("item_id") or "").strip()
    if not cod:
        return False, "receita_cod vazio"
    expected = f"{ITEM_SEMANTIC_PREFIX}{cod}"
    if iid != expected:
        return (
            False,
            f"item_id deve ser {expected!r} (prefixo IT- + receita_cod), obtido {iid!r}",
        )
    return True, None


def validate_item(
    item: dict,
    niveis: list[dict],
) -> tuple[bool, str | None]:
    """
    Valida um item. Retorna (True, None) se ok; (False, mensagem) se falha.
    Falha se: nenhum nível compatível encontrado; máscaras canônicas divergentes;
    len(cod) diferente do total de dígitos da máscara.
    """
    cod = (item.get("receita_cod") or "").strip()
    levels = find_niveis_for_item(item, niveis)
    if not levels:
        return False, "nenhuma linha de nível com registro e vigência compatíveis"
    estruturas = {
        (level.get("estrutura_codigo") or "").strip()
        for level in levels
        if (level.get("estrutura_codigo") or "").strip()
    }
    if not estruturas:
        return False, "nível(is) sem estrutura_codigo para derivar máscara"
    masks = {tuple(parse_estrutura_codigo_mask(e)) for e in estruturas}
    masks = {m for m in masks if m}
    if not masks:
        return False, "estrutura_codigo inválida para derivar máscara"
    if len(masks) > 1:
        readable = sorted(".".join(str(x) for x in m) for m in masks)
        return False, f"máscaras canônicas divergentes para o contexto do item: {readable}"
    esperado = sum(next(iter(masks)))
    if len(cod) != esperado:
        return False, f"len(receita_cod)={len(cod)}, esperado {esperado}"
    return True, None


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida quantidade de dígitos de receita_cod (SCD-2).")
    root = Path(__file__).resolve().parent.parent
    parser.add_argument(
        "--items",
        type=Path,
        default=root / "data" / "item_classificacao.csv",
        help="CSV de itens (item_classificacao)",
    )
    parser.add_argument(
        "--niveis",
        type=Path,
        default=root / "docs" / "assets" / "seed_nivel_hierarquico.csv",
        help="CSV de níveis hierárquicos",
    )
    args = parser.parse_args()

    if not args.niveis.exists():
        print(f"❌ Arquivo de níveis não encontrado: {args.niveis}", file=sys.stderr)
        return 1
    if not args.items.exists():
        print(f"⚠️ Arquivo de itens não encontrado: {args.items}. Nada a validar.", file=sys.stderr)
        return 0

    niveis = load_niveis(args.niveis)
    items = load_items(args.items)

    print("=" * 60)
    print("Validação: item_id = IT-{receita_cod}; quantidade de dígitos (receita_cod)")
    print("=" * 60)
    print(f"Níveis: {args.niveis} ({len(niveis)} linhas)")
    print(f"Itens: {args.items} ({len(items)} linhas)\n")

    errors = []
    for i, item in enumerate(items):
        ok_sid, msg_sid = validate_item_semantic_id(item)
        if not ok_sid:
            item_id = item.get("item_id", "?")
            item_ref = item.get("item_ref", "?")
            errors.append((i + 1, item_id, item_ref, msg_sid))
        ok, msg = validate_item(item, niveis)
        if not ok:
            item_id = item.get("item_id", "?")
            item_ref = item.get("item_ref", "?")
            errors.append((i + 1, item_id, item_ref, msg))

    if not errors:
        print("✅ Todos os itens passaram na validação de quantidade de dígitos.")
        return 0
    for idx, item_id, item_ref, msg in errors:
        print(f"❌ Linha {idx} (item_id={item_id}, item_ref={item_ref}): {msg}")
    print(f"\n❌ {len(errors)} item(ns) com erro.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
