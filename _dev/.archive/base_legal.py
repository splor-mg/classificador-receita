#!/usr/bin/env python3
"""
Script para gerar arquivos markdown de base legal a partir de docs/assets/seed_base_legal.csv.
Uso: python _dev/base_legal.py listar
- Cria um .md em docs/base-legal/ para cada linha do CSV.
- Nome do arquivo: [esfera_federativa]_[tipo_legal]_[numero_codigo]_[ano_vigencia]_[orgao_responsavel].md (minúsculas).
- Conteúdo: parâmetros da linha em formato lista (- chave: valor).
- Se o arquivo já existir, não cria nem sobrescreve.
"""
import csv
import sys
from pathlib import Path

# Raiz do projeto (pasta onde está _dev/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = PROJECT_ROOT / "docs" / "assets" / "seed_base_legal.csv"
OUT_DIR = PROJECT_ROOT / "docs" / "base-legal"


def slug(s: str) -> str:
    """Normaliza string para uso em nome de arquivo (minúsculas)."""
    return (s or "").strip().lower()


def ano_from_date(date_str: str) -> str:
    """Extrai o ano (AAAA) de uma data no formato AAAA-MM-DD."""
    s = (date_str or "").strip()
    if len(s) >= 4:
        return s[:4]
    return s


def build_filename(row: dict) -> str:
    esfera = slug(row.get("esfera_federativa", ""))
    tipo = slug(row.get("tipo_legal", ""))
    numero_codigo = slug(str(row.get("numero_codigo", "")))
    ano = ano_from_date(row.get("data_vigencia_inicio", ""))
    orgao = slug(row.get("orgao_responsavel", ""))
    return f"{esfera}_{tipo}_{numero_codigo}_{ano}_{orgao}.md"


def row_to_markdown(row: dict, headers: list) -> str:
    lines = []
    for key in headers:
        value = row.get(key, "")
        if isinstance(value, str) and value.startswith('"') and value.endswith('"'):
            value = value[1:-1].replace('""', '"')
        lines.append(f"- {key}: {value}")
    return "\n".join(lines) + "\n"


def listar():
    if not CSV_PATH.exists():
        print(f"Arquivo não encontrado: {CSV_PATH}", file=sys.stderr)
        sys.exit(1)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        created = 0
        skipped = 0
        for row in reader:
            filename = build_filename(row)
            out_path = OUT_DIR / filename
            if out_path.exists():
                skipped += 1
                continue
            content = row_to_markdown(row, headers)
            out_path.write_text(content, encoding="utf-8")
            created += 1
        print(f"Criados: {created}, já existiam (ignorados): {skipped}")


def main():
    if len(sys.argv) < 2:
        print("Uso: python _dev/base_legal.py listar", file=sys.stderr)
        sys.exit(1)
    if sys.argv[1].strip().lower() == "listar":
        listar()
    else:
        print("Comando desconhecido. Use: python _dev/base_legal.py listar", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
