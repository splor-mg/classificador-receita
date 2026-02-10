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
from datetime import datetime
from frictionless import validate, Package, Schema


def _log(line: str, buffer: list[str]) -> None:
    """Imprime no stdout e adiciona a linha ao buffer de log."""
    print(line)
    buffer.append(line)


def validate_schemas(log_lines: list[str]) -> bool:
    """Valida todos os schemas individuais."""
    schemas_dir = Path("schemas")
    if not schemas_dir.exists():
        _log("❌ Diretório 'schemas' não encontrado.", log_lines)
        return False

    schema_files = list(schemas_dir.glob("*.yaml"))
    if not schema_files:
        _log("❌ Nenhum arquivo de schema encontrado em 'schemas/'.", log_lines)
        return False

    _log(f"📋 Validando {len(schema_files)} schemas...\n", log_lines)

    all_valid = True
    for schema_file in sorted(schema_files):
        try:
            # Usamos validate com type='schema' para ter o mesmo comportamento da CLI
            report = validate(str(schema_file), type="schema")
            if report.valid:
                _log(f"✅ {schema_file.name}: válido", log_lines)
            else:
                _log(f"❌ {schema_file.name}: inválido", log_lines)
                for error in report.errors:
                    _log(f"   - {error.message}", log_lines)
                all_valid = False
        except Exception as e:
            _log(f"❌ {schema_file.name}: erro ao validar - {str(e)}", log_lines)
            all_valid = False

    return all_valid


def validate_datapackage(log_lines: list[str]) -> bool:
    """Valida o datapackage.yaml principal."""
    datapackage_file = Path("datapackage.yaml")
    if not datapackage_file.exists():
        _log("❌ Arquivo 'datapackage.yaml' não encontrado.", log_lines)
        return False

    _log(f"\n📦 Validando datapackage.yaml...\n", log_lines)

    try:
        # Carrega o package para inspecionar metadados (paths, schemas)
        package = Package(datapackage_file)
        # Usa validate no arquivo descriptor, como a CLI faz
        report = validate(str(datapackage_file))
        if report.valid:
            _log("✅ datapackage.yaml: válido", log_lines)
            _log(f"   - {len(package.resources)} recursos definidos", log_lines)
            return True
        else:
            _log("❌ datapackage.yaml: inválido", log_lines)
            # Tenta primeiro erros diretos (metadata); em seguida, flattens por recurso
            if report.errors:
                for error in report.errors:
                    _log(f"   - {error.message}", log_lines)
            else:
                # Usamos flatten para obter mensagens por recurso/tabela, em formato enxuto
                for resource_name, err_type, note in report.flatten(["resourceName", "type", "note"]):
                    _log(f"   - {resource_name}: {err_type} - {note}", log_lines)
                    # Quando houver um recurso associado, registra também schema e path declarados no datapackage
                    if resource_name:
                        try:
                            resource = package.get_resource(resource_name)
                        except Exception:
                            resource = None
                        if resource is not None:
                            schema_ref = resource.descriptor.get("schema")
                            path = resource.path
                            _log(f"     schema={schema_ref} path={path}", log_lines)
            return False
    except Exception as e:
        _log(f"❌ datapackage.yaml: erro ao validar - {str(e)}", log_lines)
        return False


def main():
    """Função principal."""
    log_lines: list[str] = []

    header = f"Validação de Schemas Frictionless - Classificador de Receita ({datetime.now().isoformat(timespec='seconds')})"
    _log("=" * 60, log_lines)
    _log(header, log_lines)
    _log("=" * 60, log_lines)
    _log("", log_lines)

    schemas_valid = validate_schemas(log_lines)
    package_valid = validate_datapackage(log_lines)

    _log("", log_lines)
    _log("=" * 60, log_lines)
    if schemas_valid and package_valid:
        _log("✅ Todas as validações passaram!", log_lines)
        exit_code = 0
    else:
        _log("❌ Algumas validações falharam.", log_lines)
        exit_code = 1

    # Persistir log em disco (sobrescreve a cada execução)
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    log_path = logs_dir / "validate_schemas.log"
    log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")

    return exit_code

if __name__ == "__main__":
    sys.exit(main())

