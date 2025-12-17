#!/usr/bin/env python3
"""
Script para validar schemas Frictionless do Classificador de Receita.

Uso:
    poetry run validar-schemas

Este script valida todos os schemas YAML no diretório schemas/ e o datapackage.yaml principal.

Requisitos:
    - Dependências instaladas via Poetry (frictionless)
"""

import sys
from pathlib import Path
from frictionless import validate, Package, Schema

def validate_schemas():
    """Valida todos os schemas individuais."""
    schemas_dir = Path("schemas")
    if not schemas_dir.exists():
        print("❌ Diretório 'schemas' não encontrado.")
        return False
    
    schema_files = list(schemas_dir.glob("*.yaml"))
    if not schema_files:
        print("❌ Nenhum arquivo de schema encontrado em 'schemas/'.")
        return False
    
    print(f"📋 Validando {len(schema_files)} schemas...\n")
    
    all_valid = True
    for schema_file in sorted(schema_files):
        try:
            schema = Schema(schema_file)
            report = validate(schema)
            if report.valid:
                print(f"✅ {schema_file.name}: válido")
            else:
                print(f"❌ {schema_file.name}: inválido")
                for error in report.errors:
                    print(f"   - {error.message}")
                all_valid = False
        except Exception as e:
            print(f"❌ {schema_file.name}: erro ao validar - {str(e)}")
            all_valid = False
    
    return all_valid

def validate_datapackage():
    """Valida o datapackage.yaml principal."""
    datapackage_file = Path("datapackage.yaml")
    if not datapackage_file.exists():
        print("❌ Arquivo 'datapackage.yaml' não encontrado.")
        return False
    
    print(f"\n📦 Validando datapackage.yaml...\n")
    
    try:
        package = Package(datapackage_file)
        report = validate(package)
        if report.valid:
            print("✅ datapackage.yaml: válido")
            print(f"   - {len(package.resources)} recursos definidos")
            return True
        else:
            print("❌ datapackage.yaml: inválido")
            for error in report.errors:
                print(f"   - {error.message}")
            return False
    except Exception as e:
        print(f"❌ datapackage.yaml: erro ao validar - {str(e)}")
        return False

def main():
    """Função principal."""
    print("=" * 60)
    print("Validação de Schemas Frictionless - Classificador de Receita")
    print("=" * 60)
    print()
    
    schemas_valid = validate_schemas()
    package_valid = validate_datapackage()
    
    print()
    print("=" * 60)
    if schemas_valid and package_valid:
        print("✅ Todas as validações passaram!")
        return 0
    else:
        print("❌ Algumas validações falharam.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

