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

2. **`Classificacao`** (GSIM StatisticalClassification)
   - Campos: `classificacao_id`, `serie` (FK), `classificacao_nome`, `descricao`, `tipo_classificacao`, `numero_niveis`
   - FK: `serie` → `SerieClassificacao`

3. **`NivelHierarquico`** (GSIM ClassificationLevel)
   - Campos: `nivel_id`, `classificacao` (FK), `nivel_numero`, `nivel_nome`, `descricao`, `estrutura_codigo`, `tipo_codigo`
   - FK: `classificacao` → `Classificacao`
   - Constraint: `unique_nivel_numero_classificacao` (garante unicidade do número do nível por classificação)

4. **`ItemClassificacao`** (GSIM ClassificationItem)
   - Campos: `item_id`, `codigo_completo`, `codigo_numerico`, `nivel` (FK), `parent_item` (FK self), `nome_oficial`, `descricao`, `item_gerado`, `valido_atualmente`
   - FKs: `nivel` → `NivelHierarquico`, `parent_item` → `ItemClassificacao` (auto-relacionamento)
   - Constraint: `unique_codigo_numerico_registro` (garante unicidade do código numérico por registro)

5. **`VersaoClassificacao`** (GSIM ClassificationVersion)
   - Campos: `versao_id`, `classificacao` (FK), `versao_numero`, `versao_nome`, `descricao`, `data_lancamento`
   - FK: `classificacao` → `Classificacao`

6. **`VarianteClassificacao`** (GSIM ClassificationVariant)
   - Campos: `variante_id`, `classificacao` (FK), `versao` (FK opcional), `variante_nome`, `tipo_variante`, `descricao`, `proposito`
   - FKs: `classificacao` → `Classificacao`, `versao` → `VersaoClassificacao` (opcional)

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

##### Lupa (raw id) na criação de registros: filtro «Ativos (Ano Corrente)»

Em formulários de **adicionar** (`…_add`) para `Classificacao`, `NivelHierarquico` e `ItemClassificacao`, o `href` da lupa de algumas FKs inclui na query string o mesmo parâmetro que o filtro de sidebar **Status do Registro → Ativos (Ano Corrente)** (`registro_ativo=ativo_corrente`, constantes em `apps.core.admin_mixins`). Assim a changelist do popup abre já com esse critério; o utilizador pode mudar para «Todos» ou outra opção na barra lateral.

Campos configurados (via `popup_default_registro_ativo_ano_corrente` em `semantic_fk_config`):

| ModelAdmin (origem) | FK |
|---------------------|-----|
| `Classificacao` | `serie_id` (Série de Classificação) |
| `NivelHierarquico` | `classificacao_id` |
| `ItemClassificacao` | `classificacao_id`, `parent_item_id` (item mãe), `nivel_id` |

Não se aplica à vista de **alterar** nem a FKs sem essa flag (ex.: base legal técnica em classificação/item). O critério «Ano Corrente» é o já definido em `RegistroAtivoFilter` (sobreposição da vigência com o ano civil corrente e registo ativo em tempo de transação), não «vigente apenas no dia de hoje».

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


### Padrões de Changelist no Django Admin

Esta secção documenta padrões transversais aplicados às telas de **listagem** (changelist) do Django Admin neste projeto, para além das configurações pontuais de cada `ModelAdmin`. O objectivo é uniformizar a experiência ao abrir cada changelist: o utilizador deve chegar **já num recorte útil** e poder, a partir daí, navegar com os filtros do sidebar de forma previsível.

#### Pré-filtro padrão por «Status do Registro»

Comportamento: ao abrir uma changelist sem qualquer parâmetro na query string (acesso directo via link/menu, primeira visita), o admin responde com um **redirect HTTP 302** para a **mesma URL** com o parâmetro do filtro `Status do Registro` já aplicado. A partir daí, todo o fluxo segue o padrão do Django Admin (filtros laterais, busca, paginação, `preserved_filters` para save/edit, etc.).

Mapa de defaults por changelist:

| Changelist (ModelAdmin) | Filtro | Valor default | Significado |
|--------------------------|--------|----------------|--------------|
| `SerieClassificacao` | `RegistroAtivoFilter` | `registro_ativo=ativo_historico` | «Ativos (Histórico)»: registo activo em transaction time, qualquer vigência |
| `Classificacao` | `RegistroAtivoFilter` | `registro_ativo=ativo_historico` | idem |
| `NivelHierarquico` | `RegistroAtivoFilter` | `registro_ativo=ativo_historico` | idem |
| `ItemClassificacao` | `RegistroAtivoFilter` | `registro_ativo=ativo_historico` | idem |
| `VersaoClassificacao` | `RegistroAtivoFilter` | `registro_ativo=ativo_historico` | idem |
| `VarianteClassificacao` | `RegistroAtivoFilter` | `registro_ativo=ativo_historico` | idem |
| `AliasLexico` | `AliasLexicoRegistroAtivoFilter` | `lista_abreviacoes_registro=ativo` | «Registro ativo»: `data_registro_fim` = sentinela (não há vigência orçamentária neste modelo, logo não existe «Histórico» distinto) |

#### Mecânica

1. **Mixin de redirect**: `ChangelistDefaultFilterRedirectMixin` em `apps/core/admin_mixins.py`. O `ModelAdmin` declara um dicionário `changelist_default_filters = {param: value}`; o mixin sobrepõe `changelist_view(request, …)` e, se o request for `GET` com `request.GET` vazio, devolve um `HttpResponseRedirect` para `request.path + "?" + urlencode(changelist_default_filters)`. Em todas as demais situações (com parâmetros, POST, etc.) delega no `super().changelist_view(...)`.

2. **«Todos» explícito (no-op) no filtro**: a entrada padrão «Todos» do `SimpleListFilter` gera, por defeito, uma URL **sem o parâmetro** — o que reentraria no redirect do mixin e devolveria o utilizador ao default. Para preservar a semântica de «Todos», o `RegistroAtivoFilter` (e o `AliasLexicoRegistroAtivoFilter`) **sobrepõe `choices(changelist)`** para gerar a entrada «Todos» com um valor sentinela explícito (`registro_ativo=todos` ou `lista_abreviacoes_registro=todos`), interpretado como **no-op** no `queryset()` do próprio filtro. Assim:
   - Primeira visita → GET vazio → redirect aplica o default.
   - Clique em «Todos» pelo utilizador → GET com `…=todos` → no-op, sem redirect, sem filtro.
   - Clique em qualquer outra opção → GET com valor explícito → filtro normal.

3. **Popups (`raw_id` lookup)**: não são afectados. A URL do popup contém sempre, no mínimo, `?_popup=1&_to_field=…`, logo `request.GET` nunca é vazio e o redirect não dispara. O pré-filtro `popup_default_registro_ativo_ano_corrente` (ver subsecção «Lupa (raw id) na criação de registros») continua a funcionar de forma independente.

4. **`preserved_filters`**: como o pré-filtro entra na query string, todo o mecanismo padrão do Django Admin (`_changelist_filters=…` após save/edit) preserva o recorte do utilizador entre navegações.

#### Configuração por `ModelAdmin`

Cada `ModelAdmin` que queira pré-filtrar a sua changelist deve:

1. Acrescentar `ChangelistDefaultFilterRedirectMixin` à hierarquia de bases (recomenda-se posição cedo no MRO, para que `changelist_view` seja interceptado antes de qualquer outro mixin).
2. Declarar `changelist_default_filters = { <param>: <value> }` apontando para o `SimpleListFilter` desejado.
3. Garantir que esse `SimpleListFilter` tem o tratamento de «Todos» como no-op (override de `choices()` + branch no `queryset()`).

Exemplo:

```python
class SerieClassificacaoAdmin(
    ChangelistDefaultFilterRedirectMixin,
    # … demais mixins …
    admin.ModelAdmin,
):
    changelist_default_filters = {
        REGISTRO_ATIVO_QUERY_PARAM: REGISTRO_ATIVO_VALUE_HISTORICO,
    }
    list_filter = [RegistroAtivoFilter, …]
```

#### Notas de extensão

- O mixin é **genérico**: aceita múltiplos pares chave/valor em `changelist_default_filters`, podendo combinar mais filtros default no futuro (ex.: `nivel_numero_recente`, `tipo_classificacao`).
- A escolha do default por changelist é **decisão de domínio** e fica explícita no `ModelAdmin` (não no mixin nem no filtro). O mixin transporta apenas a mecânica.
- Para mudar o default sem mudar código de mixin/filtro, basta editar `changelist_default_filters` no `ModelAdmin` correspondente.