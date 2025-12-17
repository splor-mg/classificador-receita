#!/usr/bin/env python3
"""
Script para gerar diagrama ERD a partir do datapackage.yaml.

Uso:
    poetry run gerar-erd

Requisitos:
    - Dependências instaladas via Poetry (frictionless)
    - graphviz instalado (sudo apt-get install graphviz) - apenas para conversão PNG

Arquivos gerados:
    - docs/erd/erd.dot (formato Graphviz)
    - docs/erd/erd.png (imagem PNG, se graphviz estiver instalado)
"""

import sys
import os
from pathlib import Path
from frictionless import Package

def generate_erd():
    """Gera diagrama ERD a partir do datapackage.yaml."""
    datapackage_file = Path("datapackage.yaml")
    if not datapackage_file.exists():
        print("❌ Arquivo 'datapackage.yaml' não encontrado.")
        return False
    
    # Criar diretório de saída
    output_dir = Path("docs/erd")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        package = Package(datapackage_file)
        
        # Gerar ERD em formato DOT
        erd_file = output_dir / "erd.dot"
        package.to_er_diagram(path=str(erd_file))
        print(f"✅ ERD gerado: {erd_file}")
        
        # Converter DOT para PNG (requer graphviz)
        png_file = output_dir / "erd.png"
        result = os.system(f"dot -Tpng {erd_file} -o {png_file}")
        
        if result == 0:
            print(f"✅ Diagrama PNG gerado: {png_file}")
            return True
        else:
            print("⚠️  ERD DOT gerado, mas conversão para PNG falhou.")
            print("   Instale graphviz: sudo apt-get install graphviz")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao gerar ERD: {str(e)}")
        return False

def main():
    """Função principal."""
    print("=" * 60)
    print("Geração de ERD - Classificador de Receita")
    print("=" * 60)
    print()
    
    success = generate_erd()
    
    print()
    print("=" * 60)
    if success:
        print("✅ ERD gerado com sucesso!")
        return 0
    else:
        print("❌ Falha ao gerar ERD.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

