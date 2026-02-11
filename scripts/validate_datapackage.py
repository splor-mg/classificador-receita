#!/usr/bin/env python3
"""
Script para validar schemas Frictionless do Classificador de Receita.

Uso:
    poetry run validar-datapackage

Este script valida todos os schemas YAML no diretório schemas/ e o datapackage.yaml principal.

Requisitos:
    - Dependências instaladas via Poetry (frictionless)
"""

import sys
import subprocess
import yaml
from pathlib import Path
from datetime import datetime
from frictionless import validate, Package, Schema


def _log(line: str, buffer: list[str]) -> None:
    """Imprime no stdout e adiciona a linha ao buffer de log."""
    print(line)
    buffer.append(line)


def validate_schemas(log_lines: list[str], resource_name: str | None = None) -> bool:
    """Valida schemas individuais.

    Se resource_name for informado, valida apenas o schema cujo nome de arquivo
    (sem extensão) corresponda ao recurso (ex.: 'serie_classificacao' -> 'serie_classificacao.yaml').
    Caso contrário, valida todos os schemas em schemas/.
    """
    schemas_dir = Path("schemas")
    if not schemas_dir.exists():
        _log("❌ Diretório 'schemas' não encontrado.", log_lines)
        return False

    schema_files = list(schemas_dir.glob("*.yaml"))
    # Filtra pelo nome do recurso, se fornecido
    if resource_name:
        schema_files = [f for f in schema_files if f.stem == resource_name]
        if not schema_files:
            _log(
                f"❌ Nenhum schema correspondente ao recurso '{resource_name}' encontrado em 'schemas/'.",
                log_lines,
            )
            return False
    else:
        if not schema_files:
            _log("❌ Nenhum arquivo de schema encontrado em 'schemas/'.", log_lines)
            return False

    if resource_name:
        _log(f"📋 Validando schema do recurso '{resource_name}'...\n", log_lines)
    else:
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


def validate_datapackage(log_lines: list[str], resource_name: str | None = None) -> bool:
    """Valida o datapackage.yaml principal ou um recurso específico.

    - Sem resource_name: valida o datapackage.yaml inteiro.
    - Com resource_name: valida apenas o recurso indicado no datapackage.yaml.
    """
    datapackage_file = Path("datapackage.yaml")
    if not datapackage_file.exists():
        _log("❌ Arquivo 'datapackage.yaml' não encontrado.", log_lines)
        return False

    # Modo: validar apenas um recurso específico
    if resource_name:
        _log(f"\n📦 Validando datapackage.yaml (recurso '{resource_name}')...\n", log_lines)
        try:
            package = Package(datapackage_file)
            try:
                resource = package.get_resource(resource_name)
            except Exception:
                _log(f"❌ Recurso '{resource_name}' não encontrado em datapackage.yaml.", log_lines)
                return False

            # Valida pelo path do CSV + schema (evita "resource is not open" ao validar via Package)
            base = datapackage_file.parent
            data_path = base / resource.path
            dp_descriptor = yaml.safe_load(datapackage_file.read_text(encoding="utf-8")) or {}
            schema_ref = ""
            for r in dp_descriptor.get("resources", []):
                if r.get("name") == resource_name:
                    schema_ref = r.get("schema") or ""
                    break
            report = (
                validate(str(data_path), schema=str(base / schema_ref))
                if schema_ref
                else validate(str(data_path))
            )
            if report.valid:
                _log(f"✅ recurso '{resource_name}' em datapackage.yaml: válido", log_lines)
                return True

            _log(f"❌ recurso '{resource_name}' em datapackage.yaml: inválido", log_lines)
            _log(
                f"\n===== Saída de 'frictionless validate datapackage.yaml --resource-name {resource_name}' (no terminal) =====\n",
                log_lines,
            )
            try:
                subprocess.run(
                    ["frictionless", "validate", str(datapackage_file), "--resource-name", resource_name],
                    check=False,
                    # Sem capture: CLI escreve direto no terminal e usa cores (TTY)
                )
            except Exception as e:
                _log(f"   (Falha ao executar CLI 'frictionless validate': {e})", log_lines)
            return False
        except Exception as e:
            _log(f"❌ Erro ao validar recurso '{resource_name}' no datapackage: {str(e)}", log_lines)
            return False

    # Modo padrão: validar o datapackage inteiro, recurso por recurso (CSV+schema)
    _log(f"\n📦 Validando datapackage.yaml (todos os recursos)...\n", log_lines)

    try:
        dp_descriptor = yaml.safe_load(datapackage_file.read_text(encoding="utf-8")) or {}
    except Exception as e:
        _log(f"❌ datapackage.yaml: erro ao ler/parsear YAML - {str(e)}", log_lines)
        return False

    resources = dp_descriptor.get("resources", [])
    if not resources:
        _log("❌ datapackage.yaml: nenhum recurso definido em 'resources'.", log_lines)
        return False

    base = datapackage_file.parent
    all_valid = True

    for res in resources:
        name = res.get("name")
        path = res.get("path")
        schema_ref = res.get("schema")

        if not name or not path:
            _log(f"❌ Recurso sem 'name' ou 'path' definido no datapackage: {res}", log_lines)
            all_valid = False
            continue

        data_path = base / path
        if not data_path.is_file():
            _log(f"❌ recurso '{name}': arquivo CSV não encontrado em '{data_path}'", log_lines)
            all_valid = False
            continue

        # Validação recurso a recurso, como no modo filtrado
        try:
            if schema_ref:
                schema_path = base / schema_ref
                report = validate(str(data_path), schema=str(schema_path))
            else:
                report = validate(str(data_path))

            if report.valid:
                _log(f"✅ recurso '{name}' em datapackage.yaml: válido", log_lines)
            else:
                _log(f"❌ recurso '{name}' em datapackage.yaml: inválido", log_lines)
                for error in report.errors:
                    _log(f"   - {error.message}", log_lines)
                all_valid = False
        except Exception as e:
            _log(f"❌ recurso '{name}' em datapackage.yaml: erro ao validar - {str(e)}", log_lines)
            _log(f"   - {str(e)}", log_lines)
            all_valid = False

    # Em caso de qualquer recurso inválido, também delega ao CLI completo
    # para exibir o mesmo relatório tabular do comando:
    #   poetry run frictionless validate datapackage.yaml
    if not all_valid:
        _log(
            "\n===== Saída de 'frictionless validate datapackage.yaml' (no terminal) =====\n",
            log_lines,
        )
        try:
            subprocess.run(
                ["frictionless", "validate", str(datapackage_file)],
                check=False,
                # Sem capture: CLI escreve direto no terminal e usa cores (TTY)
            )
        except Exception as e:
            _log(f"   (Falha ao executar CLI 'frictionless validate': {e})", log_lines)

    return all_valid


def main():
    """Função principal."""
    log_lines: list[str] = []

    # Argumento opcional: nome do recurso (ex.: 'serie_classificacao')
    resource_name = sys.argv[1] if len(sys.argv) > 1 else None

    header = f"Validação de Schemas Frictionless - Classificador de Receita ({datetime.now().isoformat(timespec='seconds')})"
    _log("=" * 60, log_lines)
    _log(header, log_lines)
    _log("=" * 60, log_lines)
    _log("", log_lines)

    schemas_valid = validate_schemas(log_lines, resource_name=resource_name)
    package_valid = validate_datapackage(log_lines, resource_name=resource_name)

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

