# Sistema de Gestão do Classificador de Natureza de Receita

Sistema de gestão voltado para organização, classificação e versionamento histórico de informações do Classificador de Natureza de Receita do Estado de Minas Gerais em um banco de dados taxonômico, relacional e normalizado, permitindo rastreabilidade e consulta eficiente das categorias e alterações ao longo do tempo.

## Principais Funcionalidades

- Banco de dados bitemporal (PostgreSQL) para rastreamento histórico completo.
- Aplicação web Django para gestão operacional do classificador.
- Dashboard público para consulta e transparência.
- Sincronização automática bidirecional com SISOR.

## Tecnologias

- Django, PostgreSQL, Docker, Frictionless Data Package.
- Poetry (gerenciamento de dependências Python).

## Instalação

Este projeto usa [Poetry](https://python-poetry.org/) para gerenciamento de dependências.

### Pré-requisitos

- Python 3.11 ou superior.
- Poetry instalado ([instruções de instalação](https://python-poetry.org/docs/#installation)).

### Configuração

```bash
# Instalar dependências
poetry install

# Ativar ambiente virtual
poetry shell
```

## Documentação

Documentação completa disponível em [`docs/projeto.md`](docs/projeto.md).

- **Aplicação Django (sistema):** `poetry run task dev-server` → [http://localhost:8000](http://localhost:8000) — página inicial do classificador e admin.
- **Site da documentação (Zensical):** `poetry run task serve` → [http://localhost:8001](http://localhost:8001) — apresentação, projeto, ERD, ADRs e referências com navegação lateral.

### Modelo de Dados

O **modelo conceitual de dados** do classificador é definido primariamente pelos **Table Schemas Frictionless**, registrados na pasta `schemas`, e pelo **Data Package**, em `datapackage.yaml`:


Os **models Django** (`apps/core/models.py`) e as migrations são a implementação dessa especificação no banco PostgreSQL, e devem ser mantidos alinhados a esses schemas. Sempre que o modelo de dados evoluir, a ordem esperada é:

1. Atualizar o(s) `schemas/*.yaml` e o `datapackage.yaml` correspondentes.
2. Ajustar os models Django e gerar novas migrations para refletir essas mudanças.
3. Rodar os scripts de validação ( antes de aplicar as migrations em ambientes compartilhados.


## Scripts de Validação e Geração

O projeto inclui scripts utilitários para validação de schemas Frictionless e geração de diagramas ERD.

### Validação de Schemas

Valida todos os schemas Frictionless e o datapackage.yaml principal.

```bash
poetry run task validar-datapackage
```

**O que faz:**
- Valida cada schema YAML no diretório `schemas/`.
- Valida o `datapackage.yaml` principal.
- Reporta erros de validação.

### Geração de ERD

Gera diagrama Entidade-Relacionamento (ERD) a partir do `datapackage.yaml`.

```bash
poetry run task gerar-erd
```

**O que faz:**
- Lê o `datapackage.yaml`.
- Gera arquivo `docs/erd/erd.dot` (formato Graphviz).
- Converte para `docs/erd/erd.png` (imagem, se graphviz estiver instalado).

**Requisitos:**
- `graphviz` instalado: `sudo apt-get install graphviz` (apenas para conversão PNG).

**Arquivos gerados:**
- `docs/erd/erd.dot` - Diagrama em formato Graphviz DOT.
- `docs/erd/erd.png` - Diagrama em formato PNG (se graphviz estiver instalado).

```

