# Anotações sobre Implementação do Django no Projeto

## Estrutura de Arquivos e Pastas

Ao seguir as orientações do curso [CS50's Web Programming - Week 3: Django](https://cs50.harvard.edu/web/weeks/3/), foi executado o comando `django-admin startproject classificador` dentro do repositório `classificador-receita`, que já continha uma estrutura pré-existente com `schemas`, `scripts`, `docs/` dentre outros.

Isso resultou na criação de uma estrutura aninhada, confusa de  `classificador-receita/classificador/classificador/`, onde:
- `classificador/` (pasta externa) contém `manage.py` e a pasta de configurações
- `classificador/classificador/` (pasta interna) contém `settings.py`, `urls.py`, `wsgi.py`, etc.

### Decisão: Django na Raiz

Tomando como referência [cookiecutter-django](https://cookiecutter-django.readthedocs.io/en/latest/index.html), foi decidido implementar o **Django na raiz** para reestruturar o projeto, movendo:
- `manage.py` para a raiz do repositório
- `classificador/classificador/` → `classificador/` (configurações do projeto Django)

Optar por Django na raiz simplifica o acesso direto aos recursos já existentes no projeto (`schemas/`, `scripts/` e `docs/`), proporciona uma estrutura plana e intuitiva ao eliminar pastas aninhadas desnecessárias, segue as práticas recomendadas por projetos modernos, facilita o uso dos comandos com `manage.py` na raiz e faz sentido já que Django será a principal interface de gerenciamento do classificador.


Estrutura pensada: 

```
classificador-receita/              # Repositório raiz
├── manage.py                       # Django na raiz
├── pyproject.toml                  # Poetry
├── classificador/                  # Configurações do projeto Django
│   ├── __init__.py
│   ├── settings.py                 # BASE_DIR aponta para raiz
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/                           # Apps Django (criar quando necessário)
│   └── core/                       # App principal
├── scripts/                        # Scripts utilitários (mantém)
│   ├── validate_datapackage.py
│   └── (...)
|   
├── schemas/                        # Schemas Frictionless (mantém)
├── docs/                           # Documentação (mantém)
└── README.md

```

### Observação: Organização de Apps em `apps/`

Os apps Django foram organizados dentro da pasta `apps/` visando **escalabilidade** e **padronização**, seguindo recomendações para projetos Django. Esta estrutura permite adicionar múltiplos apps de forma organizada (ex: `apps/core/`, `apps/api/`, `apps/dashboard/`) sem poluir a raiz do repositório.

No entanto, para criar novos apps nesta estrutura, o comando deve ser adaptado para especificar o caminho completo:

```bash
poetry run python manage.py startapp <nome_do_app> apps/<nome_do_app>
```

Além disso, o arquivo `classificador/settings.py` precisa ser configurado para que o Django encontre os apps dentro de `apps/`. Para isso, é necessário adicionar as seguintes linhas logo após a definição de `BASE_DIR`:

```python
import sys

# Add apps directory to Python path
sys.path.insert(0, str(BASE_DIR / "apps"))
```

Com essa configuração, os apps podem ser referenciados diretamente no `INSTALLED_APPS` (ex: `"core"`) sem necessidade de usar o prefixo `apps.` (ex: `"apps.core"`).

---

## Implementação do App Core - Models Bitemporais

### Resumo da Implementação

Foi implementada a estrutura básica do app `core` para gerenciamento das estruturas do Classificador de Natureza de Receita, seguindo os schemas definidos em `schemas/` e alinhado com os ADRs do projeto (ADR-001: Bitemporalidade e ADR-002: GSIM).

### Models Implementados

#### 1. Classe Base: `BitemporalModel`
- Classe abstrata que implementa os 4 campos bitemporais:
  - `data_vigencia_inicio` / `data_vigencia_fim` (valid_time)
  - `data_registro_inicio` / `data_registro_fim` (transaction_time)
- Validação básica de intervalos temporais no método `clean()`
- Constantes para valores sentinelas: `VALID_TIME_SENTINEL` e `TRANSACTION_TIME_SENTINEL`

#### 2. Models Principais (6 entidades)

1. **`SerieClassificacao`** (GSIM ClassificationSeries)
   - Campos: `serie_id`, `serie_nome`, `descricao`, `orgao_responsavel`
   - Sem dependências (entidade raiz)

2. **`ClassificacaoReceita`** (GSIM StatisticalClassification)
   - Campos: `classificacao_id`, `serie` (FK), `classificacao_nome`, `descricao`, `tipo_classificacao`, `numero_niveis`
   - FK: `serie` → `SerieClassificacao`

3. **`NivelHierarquico`** (GSIM ClassificationLevel)
   - Campos: `nivel_id`, `classificacao` (FK), `nivel_numero`, `nivel_nome`, `descricao`, `estrutura_codigo`, `tipo_codigo`
   - FK: `classificacao` → `ClassificacaoReceita`
   - Constraint: `unique_nivel_numero_classificacao` (garante unicidade do número do nível por classificação)

4. **`ItemClassificacao`** (GSIM ClassificationItem)
   - Campos: `item_id`, `codigo_completo`, `codigo_numerico`, `nivel` (FK), `parent_item` (FK self), `nome_oficial`, `descricao`, `item_gerado`, `valido_atualmente`
   - FKs: `nivel` → `NivelHierarquico`, `parent_item` → `ItemClassificacao` (auto-relacionamento)
   - Constraint: `unique_codigo_numerico_registro` (garante unicidade do código numérico por registro)

5. **`VersaoClassificacao`** (GSIM ClassificationVersion)
   - Campos: `versao_id`, `classificacao` (FK), `versao_numero`, `versao_nome`, `descricao`, `data_lancamento`
   - FK: `classificacao` → `ClassificacaoReceita`

6. **`VarianteClassificacao`** (GSIM ClassificationVariant)
   - Campos: `variante_id`, `classificacao` (FK), `versao` (FK opcional), `variante_nome`, `tipo_variante`, `descricao`, `proposito`
   - FKs: `classificacao` → `ClassificacaoReceita`, `versao` → `VersaoClassificacao` (opcional)

### Características Implementadas

#### Constraints e Índices
- **UniqueConstraint**: Garante unicidade bitemporal usando `(identificador, data_registro_inicio)`
- **Índices compostos**: Otimizam queries temporais e hierárquicas
- **Índices em FKs**: Melhoram performance de joins
- **Índices em campos de busca**: `codigo_numerico`, `codigo_completo`, `item_id`

#### Validações
- Validação de intervalos temporais (início < fim)
- Validação de enum (tipo_classificacao, tipo_codigo, tipo_variante)
- Validação de range numérico (numero_niveis: 1-9, codigo_numerico: 13 dígitos)

#### Django Admin
- Todos os 6 models registrados no `admin.py`
- Configurações básicas: `list_display`, `list_filter`, `search_fields`
- Campos `data_registro_*` marcados como `readonly_fields`
- `date_hierarchy` para navegação temporal
- `raw_id_fields` para FKs (melhor performance)

### Migrations

Migrations iniciais criadas com sucesso:
- `apps/core/migrations/0001_initial.py`
- Inclui criação de todas as tabelas, constraints, índices e relacionamentos

### Estrutura de Arquivos Criada

```
apps/core/
├── models.py          # 6 models + classe base BitemporalModel
├── admin.py           # Registro de todos os models no Django Admin
└── migrations/
    └── 0001_initial.py
```

### Pontos de Atenção

1. **Chaves Primárias Compostas**: Django não suporta PKs compostas nativamente. A solução implementada usa `id` como PK única (auto-increment) + `UniqueConstraint` para garantir unicidade bitemporal. Isso permite múltiplos registros históricos do mesmo identificador.

2. **Valores Sentinelas**: 
   - `data_vigencia_fim = '9999-12-31'` → vigência ativa
   - `data_registro_fim = '9999-12-31'` → registro ativo
   - Constantes definidas em `models.py` para facilitar uso

3. **Gerenciamento de `data_registro_fim`**: Conforme ADR-001, a responsabilidade é híbrida. Por enquanto, a aplicação deve gerenciar o fechamento de `data_registro_fim` ao criar novos registros. Triggers no PostgreSQL podem ser adicionados futuramente.

4. **Queries Bitemporais**: Models básicos implementados. Managers customizados para queries "current" e "as-of" podem ser adicionados futuramente conforme necessidade.

5. **Auto-relacionamento**: `ItemClassificacao.parent_item` permite hierarquia de 9 níveis. NULL para itens do nível 1 (raiz).

6. **Nomes de Tabelas**: Usando `db_table` para manter nomes em português conforme schemas (ex: `serie_classificacao`, `classificacao`).

7. **Próximos Passos**:
   - Criar managers customizados para queries bitemporais
   - Implementar signals para gerenciar `data_registro_fim` automaticamente
   - Adicionar métodos helper para valores sentinelas
   - Implementar validações customizadas mais complexas
   - Criar views e templates para interface de gestão