# Sistema de Gestão do Classificador de Natureza de Receita

Sistema de gestão voltado para organização, classificação e versionamento histórico de informações do Classificador de Natureza de Receita do Estado de Minas Gerais em um banco de dados taxonômico, relacional e normalizado, permitindo rastreabilidade e consulta eficiente das categorias e alterações ao longo do tempo.

## Principais Funcionalidades

- Banco de dados bitemporal (PostgreSQL) para rastreamento histórico completo
- Aplicação web Django para gestão operacional do classificador
- Dashboard público para consulta e transparência
- Sincronização automática bidirecional com SISOR

## Tecnologias

- Django, PostgreSQL, Docker, Frictionless Data Package
- Poetry (gerenciamento de dependências Python)

## Instalação

Este projeto usa [Poetry](https://python-poetry.org/) para gerenciamento de dependências.

### Pré-requisitos

- Python 3.11 ou superior
- Poetry instalado ([instruções de instalação](https://python-poetry.org/docs/#installation))

### Configuração

```bash
# Instalar dependências
poetry install

# Ativar ambiente virtual
poetry shell
```

## Documentação

Documentação completa disponível em [`docs/projeto.md`](docs/projeto.md)

## Scripts de Validação e Geração

O projeto inclui scripts utilitários para validação de schemas Frictionless e geração de diagramas ERD.

### Validação de Schemas

Valida todos os schemas Frictionless e o datapackage.yaml principal:

```bash
poetry run validar-schemas
```

**O que faz:**
- Valida cada schema YAML no diretório `schemas/`
- Valida o `datapackage.yaml` principal
- Reporta erros de validação

### Geração de ERD

Gera diagrama Entidade-Relacionamento (ERD) a partir do `datapackage.yaml`:

```bash
poetry run gerar-erd
```

**O que faz:**
- Lê o `datapackage.yaml`
- Gera arquivo `docs/erd/erd.dot` (formato Graphviz)
- Converte para `docs/erd/erd.png` (imagem, se graphviz estiver instalado)

**Requisitos:**
- `graphviz` instalado: `sudo apt-get install graphviz` (apenas para conversão PNG)

**Arquivos gerados:**
- `docs/erd/erd.dot` - Diagrama em formato Graphviz DOT
- `docs/erd/erd.png` - Diagrama em formato PNG (se graphviz estiver instalado)

### Integração com CI/CD

Estes scripts podem ser integrados em pipelines CI/CD (ex: GitHub Actions) para validação automática dos schemas.

**Exemplo de uso no CI:**
```yaml
- name: Validar schemas
  run: poetry run validar-schemas
```

