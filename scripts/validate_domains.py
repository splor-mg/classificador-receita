#!/usr/bin/env python3
"""
Validação de domínios compartilhados (custom.domainRef).

Uso:
    poetry run task validar-dominios

O script faz duas coisas:
1) Garante que todo custom.domainRef aponte para um arquivo de domínio existente em schemas/dominios/.
2) Garante que o arquivo de domínio tenha, pelo menos, um array "values" com a lista de códigos válidos.

OBS: Esta validação é estrutural (schema + domínios). A validação de dados contra os domínios
     pode ser adicionada depois, reutilizando esta mesma convenção.
"""

from pathlib import Path
import sys
import textwrap

import yaml
from frictionless import Schema


SCHEMAS_DIR = Path("schemas")
DOMAINS_SUBDIR = SCHEMAS_DIR / "dominios"


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def validate_domain_refs() -> bool:
    if not SCHEMAS_DIR.exists():
        print("❌ Diretório 'schemas' não encontrado.")
        return False

    schema_files = sorted(SCHEMAS_DIR.glob("*.yaml"))
    if not schema_files:
        print("❌ Nenhum arquivo de schema encontrado em 'schemas/'.")
        return False

    print("🔎 Verificando domínios compartilhados (custom.domainRef)...\n")

    all_ok = True
    for schema_path in schema_files:
        schema = Schema(schema_path)
        descriptor = schema.to_descriptor()
        fields = descriptor.get("fields", [])

        for field in fields:
            custom = field.get("custom") or {}
            domain_ref = custom.get("domainRef")
            if not domain_ref:
                continue

            # Caminho absoluto do domínio
            domain_path = SCHEMAS_DIR / domain_ref
            field_name = field.get("name")

            if not domain_path.exists():
                print(f"❌ {schema_path.name}: campo '{field_name}' referencia domínio inexistente: {domain_ref}")
                all_ok = False
                continue

            try:
                domain_desc = load_yaml(domain_path)
            except Exception as e:
                print(f"❌ {schema_path.name}: erro ao ler domínio '{domain_ref}': {e}")
                all_ok = False
                continue

            values = domain_desc.get("values")
            if not isinstance(values, list) or not values:
                print(
                    f"❌ {schema_path.name}: domínio '{domain_ref}' não possui 'values' "
                    f"como lista não vazia (necessário para atuar como enum compartilhado)."
                )
                all_ok = False
            else:
                print(
                    f"✅ {schema_path.name}: campo '{field_name}' vinculado ao domínio '{domain_ref}' "
                    f"com {len(values)} valores."
                )

    if all_ok:
        print("\n✅ Todos os domínios referenciados por custom.domainRef foram encontrados e possuem 'values' válidos.")
    else:
        print("\n❌ Problemas encontrados em domínios ou referências. Veja mensagens acima.")
    return all_ok


def main() -> int:
    print("=" * 60)
    print("Validação de Domínios Compartilhados (custom.domainRef)")
    print("=" * 60)
    print()

    ok = validate_domain_refs()
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

