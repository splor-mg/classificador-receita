#!/usr/bin/env python3
"""
Aplica as regras de qualityDimensions (quality-rules.yaml) aos dados dos recursos
cujos schemas declaram custom.qualityDimensions.

Uso:
    poetry run task validar-qualidade
    python scripts/validate_quality.py
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

# Load YAML without hard dependency on pyyaml if we use frictionless
try:
    import yaml
except ImportError:
    yaml = None


def load_yaml(path: Path) -> dict:
    if yaml is None:
        raise RuntimeError("PyYAML necessário para validar qualidade. Instale com: pip install pyyaml")
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def get_schema_custom_quality(schema_path: Path) -> dict | None:
    """Retorna custom.qualityDimensions do schema ou None."""
    if not schema_path.exists():
        return None
    data = load_yaml(schema_path)
    return data.get("custom", {}).get("qualityDimensions")


def load_quality_rules(rules_path: Path) -> dict:
    """Carrega quality-rules.yaml; retorna dict com ruleSets."""
    if not rules_path.exists():
        return {}
    data = load_yaml(rules_path)
    return data.get("ruleSets", {})


def load_resource_rows(csv_path: Path) -> list[dict]:
    """Carrega linhas do CSV como list[dict]."""
    if not csv_path.exists():
        return []
    rows = []
    with csv_path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(dict(row))
    return rows


def evaluate_expression(expression: str, row: dict) -> tuple[bool, str | None]:
    """
    Avalia a expressão com os campos da linha como variáveis.
    Retorna (True, None) se verdadeiro, (False, mensagem) se falso ou erro.
    """
    try:
        # Restringe o contexto às chaves da linha (evita injeção)
        safe_dict = {k: v for k, v in row.items()}
        result = eval(expression, {"__builtins__": {}}, safe_dict)
        if result:
            return True, None
        return False, f"expressão falsa: {expression!r}"
    except Exception as e:
        return False, f"erro ao avaliar {expression!r}: {e}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida regras de qualityDimensions nos dados.")
    root = Path(__file__).resolve().parent.parent
    parser.add_argument(
        "--datapackage",
        type=Path,
        default=root / "datapackage.yaml",
        help="Caminho do datapackage.yaml",
    )
    parser.add_argument(
        "--quality-rules",
        type=Path,
        default=root / "quality" / "quality-rules.yaml",
        help="Caminho do quality-rules.yaml",
    )
    args = parser.parse_args()

    if not args.datapackage.exists():
        print(f"❌ Datapackage não encontrado: {args.datapackage}", file=sys.stderr)
        return 1
    if not args.quality_rules.exists():
        print(f"❌ Quality rules não encontrado: {args.quality_rules}", file=sys.stderr)
        return 1

    package = load_yaml(args.datapackage)
    resources = package.get("resources", [])
    rules_content = load_quality_rules(args.quality_rules)
    if not rules_content:
        print("⚠️ Nenhum ruleSet em quality-rules.yaml.")
        return 0

    # Fallback: alguns recursos podem estar em docs/assets com nome seed_*
    fallback_names = {
        "classificacao_receita": "seed_classificacao.csv",
        "serie_classificacao": "seed_serie_classificacao.csv",
        "nivel_hierarquico": "seed_nivel_hierarquico.csv",
        "versao_classificacao": "seed_versao_classificacao.csv",
    }

    print("=" * 60)
    print("Validação de quality dimensions")
    print("=" * 60)

    total_errors = 0
    for res in resources:
        name = res.get("name", "")
        schema_ref = res.get("schema", "")
        path_ref = res.get("path", "")
        if not schema_ref or not path_ref:
            continue
        schema_path = root / schema_ref
        csv_path = root / path_ref
        if not csv_path.exists() and name in fallback_names:
            csv_path = root / "docs" / "assets" / fallback_names[name]
        qd = get_schema_custom_quality(schema_path)
        if not qd:
            continue
        rule_sets = qd.get("ruleSets", [])
        if not rule_sets:
            continue
        rows = load_resource_rows(csv_path)
        if not rows:
            print(f"\n⚠️ Recurso {name}: arquivo não encontrado ou vazio ({csv_path}), pulando.")
            continue
        print(f"\n📋 Recurso: {name} ({len(rows)} linhas)")
        resource_errors = 0
        for set_name in rule_sets:
            rule_set = rules_content.get(set_name)
            if not rule_set:
                print(f"   ⚠️ RuleSet {set_name!r} não encontrado em quality-rules.yaml")
                continue
            for rule in rule_set.get("rules", []):
                rname = rule.get("name", "?")
                expr = rule.get("expression")
                if not expr:
                    continue
                for i, row in enumerate(rows):
                    ok, msg = evaluate_expression(expr, row)
                    if not ok:
                        resource_errors += 1
                        total_errors += 1
                        print(f"   ❌ Linha {i + 1} regra {rname}: {msg}")
        if resource_errors == 0 and rows:
            print(f"   ✅ Regras aplicadas sem erros.")

    print("\n" + "=" * 60)
    if total_errors == 0:
        print("✅ Validação de qualidade concluída sem erros.")
        return 0
    print(f"❌ {total_errors} erro(s) de qualidade.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
