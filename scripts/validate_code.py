#!/usr/bin/env python3
"""
Valida a quantidade de dígitos de receita_cod conforme a classificação vigente (SCD-2 / bitemporal).

Critério: para cada item, resolve classificação(s) cujo período de REGISTRO compreenda o período
de registro do item; em seguida filtra por vigência (a vigência da classificação deve compreender
a vigência do item). Se houver mais de uma linha de classificação, todas devem ter o mesmo
numero_digitos e len(receita_cod) deve igualar esse valor. Caso contrário o teste falha.

Uso:
    poetry run task validar-codigos
    python scripts/validate_code.py --items data/item_classificacao.csv --classificacao docs/assets/seed_classificacao.csv
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


def load_classificacao(path: Path) -> list[dict]:
    """Carrega linhas do CSV de classificação; normaliza nomes e datas."""
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
            if "numero_digitos" in r and r["numero_digitos"]:
                r["numero_digitos"] = int(r["numero_digitos"])
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


def find_classificacoes_for_item(
    item: dict,
    classificacoes: list[dict],
) -> list[dict]:
    """
    Retorna as linhas de classificação que:
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
    for c in classificacoes:
        if c.get("classificacao_id") != cid:
            continue
        c_ri = c.get("data_registro_inicio")
        c_rf = c.get("data_registro_fim")
        c_vi = c.get("data_vigencia_inicio")
        c_vf = c.get("data_vigencia_fim")
        if not all([c_ri, c_rf, c_vi, c_vf]):
            continue
        if not _registro_item_contido_em_registro_class(item_ri, item_rf, c_ri, c_rf):
            continue
        if not _vigencia_item_contida_em_vigencia_class(item_vi, item_vf, c_vi, c_vf):
            continue
        out.append(c)
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
    classificacoes: list[dict],
) -> tuple[bool, str | None]:
    """
    Valida um item. Retorna (True, None) se ok; (False, mensagem) se falha.
    Falha se: nenhuma classificação encontrada; múltiplas com numero_digitos diferentes; len(cod) != numero_digitos.
    """
    cod = (item.get("receita_cod") or "").strip()
    classes = find_classificacoes_for_item(item, classificacoes)
    if not classes:
        return False, "nenhuma linha de classificação com registro e vigência compatíveis"
    numeros = {c.get("numero_digitos") for c in classes if c.get("numero_digitos") is not None}
    if not numeros:
        return False, "classificação(ões) sem numero_digitos"
    if len(numeros) > 1:
        return False, f"classificação com numero_digitos distintos nas linhas vigentes: {sorted(numeros)}"
    esperado = next(iter(numeros))
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
        "--classificacao",
        type=Path,
        default=root / "docs" / "assets" / "seed_classificacao.csv",
        help="CSV de classificação",
    )
    args = parser.parse_args()

    if not args.classificacao.exists():
        print(f"❌ Arquivo de classificação não encontrado: {args.classificacao}", file=sys.stderr)
        return 1
    if not args.items.exists():
        print(f"⚠️ Arquivo de itens não encontrado: {args.items}. Nada a validar.", file=sys.stderr)
        return 0

    classificacoes = load_classificacao(args.classificacao)
    items = load_items(args.items)

    print("=" * 60)
    print("Validação: item_id = IT-{receita_cod}; quantidade de dígitos (receita_cod)")
    print("=" * 60)
    print(f"Classificação: {args.classificacao} ({len(classificacoes)} linhas)")
    print(f"Itens: {args.items} ({len(items)} linhas)\n")

    errors = []
    for i, item in enumerate(items):
        ok_sid, msg_sid = validate_item_semantic_id(item)
        if not ok_sid:
            item_id = item.get("item_id", "?")
            item_ref = item.get("item_ref", "?")
            errors.append((i + 1, item_id, item_ref, msg_sid))
        ok, msg = validate_item(item, classificacoes)
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
