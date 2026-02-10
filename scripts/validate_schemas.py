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
import subprocess
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
        # Usa validate no arquivo descriptor para saber se está válido
        report = validate(str(datapackage_file))
        if report.valid:
            _log("✅ datapackage.yaml: válido", log_lines)
            return True
        else:
            _log("❌ datapackage.yaml: inválido", log_lines)

            # Quando o datapackage for inválido, executa o CLI do Frictionless
            # com saída direta no terminal (stdout/stderr herdados) para que
            # as cores (ex.: verde para VALID) e o layout sejam idênticos a:
            #   poetry run frictionless validate datapackage.yaml
            _log("\n===== Saída de 'frictionless validate datapackage.yaml' (no terminal) =====\n", log_lines)
            try:
                subprocess.run(
                    ["frictionless", "validate", str(datapackage_file)],
                    check=False,
                    # Sem capture: CLI escreve direto no terminal e usa cores (TTY)
                )
                _log("(Relatório detalhado exibido acima no terminal.)", log_lines)
            except Exception as e:
                _log(f"   (Falha ao executar CLI 'frictionless validate': {e})", log_lines)
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

