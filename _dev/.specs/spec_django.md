# Django no Classificador de Receita

Arquitetura Django do repositório: layout na raiz, app `core` bitemporal, padrões de Admin (changelist, popups) e pipeline de atualização bitemporal. **Não substitui** specs de domínio (`spec_itemClassificacao_*.md`) nem ADRs em `docs/adr/`.

## Objetivo

Documentar como o projeto **deve** estruturar o Django, registrar models bitemporais e aplicar padrões transversais do Admin (pré-filtros, recolhimento de sidebar, popups FK, filtro de campos no pipeline bitemporal).

Premissa: descreve implementação vigente em `classificador/`, `apps/core/` e mixins em `admin_mixins.py`.

## Referências

- [cookiecutter-django](https://cookiecutter-django.readthedocs.io/en/latest/index.html) — inspiração layout na raiz.
- **ADR-001** — bitemporalidade (`docs/adr/adr-001_bitemporalidade.md`).
- **ADR-002** — GSIM (`docs/adr/adr-002_gsim.md`).
- **ADR-005** — layout `docs/assets/`, `data-raw/`, `data/`.
- `_dev/spec_conventions.md` — módulos `code_*`, glossário temporal.
- `_dev/spec_agents.md` — SDD e agentes.
- [`spec_itemClassificacao_formulario.md`](spec_itemClassificacao_formulario.md) — formulário `ItemClassificacao`.
- [`spec_itemClassificacao_criar_nome.md`](spec_itemClassificacao_criar_nome.md) — `receita_nome_base_mode` (caso **DJANGO-28**).
- [`spec_classificador-receita.md`](spec_classificador-receita.md) § **Convenções** — prefixo `DJANGO`.

Termos *deve* / *não deve* / *pode* conforme RFC 2119 (ver `_dev/spec_conventions.md` **Referências**).

**Migração de símbolos legados:**

| Legado                | ID atual                |
| --------------------- | ----------------------- |
| `B-pipe.1`–`B-pipe.4` | `DJANGO-25`–`DJANGO-28` |

## Como citar este documento

| Mecanismo          | Uso                                                                 |
| ------------------ | ------------------------------------------------------------------- |
| **Seção numerada** | `§ N` / `§ N.M` — navegação neste arquivo.                          |
| **ID normativo**   | `DJANGO-NN` — citação estável.                                      |
| **Prefixo**        | `DJANGO` — ver § **Convenções** em `spec_classificador-receita.md`. |

**Índice de IDs normativos deste arquivo:**

| ID        | Tema       | Seção | Resumo                                                                                                                      |
| --------- | ---------- | ----- | --------------------------------------------------------------------------------------------------------------------------- |
| DJANGO-01 | Layout     | 1.1   | `manage.py` e pacote `classificador/` (settings, urls) na **raiz** do repositório.                                          |
| DJANGO-02 | Layout     | 1.2   | Apps Django em `apps/`; `startapp` com caminho `apps/<nome>`.                                                               |
| DJANGO-03 | Layout     | 1.3   | `sys.path.insert(0, BASE_DIR / "apps")`; `INSTALLED_APPS` usa `"core"`, não `"apps.core"`.                                  |
| DJANGO-04 | Models     | 2.1   | `BitemporalModel` abstrata com 4 campos temporais e `clean()` de intervalos.                                                |
| DJANGO-05 | Models     | 2.2   | Sentinels `VALID_TIME_SENTINEL` e `TRANSACTION_TIME_SENTINEL` (`9999-12-31`).                                               |
| DJANGO-06 | Models     | 2.3   | PK `id` auto + `UniqueConstraint` bitemporal — **sem** PK composta nativa.                                                  |
| DJANGO-07 | Admin      | 3.1   | Popups FK na **add**: `popup_default_registro_ativo_ano_corrente` → `registro_ativo=ativo_corrente` na query da lupa.       |
| DJANGO-08 | Admin      | 3.1   | **Não** aplicar pop-up default na **change** nem em FKs sem a flag.                                                         |
| DJANGO-09 | Changelist | 4.1   | Entrada «fria» (GET sem filtros) → redirect 302 com `changelist_default_filters` do `ModelAdmin`.                           |
| DJANGO-10 | Changelist | 4.1   | Após «Limpar todos os filtros» → mesma changelist **sem** filtros e **sem** reaplicar default (sessão).                     |
| DJANGO-11 | Changelist | 4.1   | Sair da changelist e voltar com GET vazio → **reaplica** default.                                                           |
| DJANGO-12 | Changelist | 4.2   | `ChangelistDefaultFilterRedirectMixin` intercepta `changelist_view` quando GET vazio e sem flag skip.                       |
| DJANGO-13 | Changelist | 4.2   | `RegistroAtivoFilter`: «Todos» = sentinela `registro_ativo=todos` (no-op), não GET vazio.                                   |
| DJANGO-14 | Changelist | 4.2   | «Limpar todos»: `__changelist_skip_default=1` → flag sessão + redirect sem query.                                           |
| DJANGO-15 | Changelist | 4.2   | Popups `raw_id` (`?_popup=1`) **não** disparam redirect (GET nunca vazio).                                                  |
| DJANGO-16 | Changelist | 4.2   | `AdminChangelistSkipDefaultScopeMiddleware` invalida flags ao sair da changelist do model.                                  |
| DJANGO-17 | Changelist | 4.3   | Defaults por entidade — ver tabela § **4.3** (`ativo_historico` vs `ativo_corrente`).                                       |
| DJANGO-18 | Sidebar    | 5.1   | `ChangelistSidebarFilterCollapseMixin`: a cada GET, expandir só `changelist_expanded_filters` (+ filtros com valor activo). |
| DJANGO-19 | Sidebar    | 5.1   | Stateless — interação abrir/fechar **não** persiste entre entradas na changelist.                                           |
| DJANGO-20 | Sidebar    | 5.2   | Default `DEFAULT_CHANGELIST_EXPANDED_FILTERS` = `{registro_ativo, data_registro_inicio}`.                                   |
| DJANGO-21 | Sidebar    | 5.2   | `BaseLegalTecnicaAdmin` **sem** mixin collapse; `AliasLexico` no-op (≤3 filtros).                                           |
| DJANGO-22 | Sidebar    | 5.3   | Override `apps/core/static/admin/js/filters.js` — **sem** `sessionStorage` (conflito Django 6+).                            |
| DJANGO-23 | Sidebar    | 5.3   | Auto-expand: união de filtros declarados + filtros com parâmetro activo em `request.GET`.                                   |
| DJANGO-24 | Sidebar    | 5.4   | Template `apps/core/templates/admin/filter.html` — título sem prefixo «Por …».                                              |
| DJANGO-25 | Pipeline   | 6.1   | `BitemporalChangeHandler._apply_user_edits`: `new_values` só campos concretos do model (`get_field`).                       |
| DJANGO-26 | Pipeline   | 6.2   | `apply_bitemporal_update`: filtrar `new_values` a `{f.name for f in concrete_fields}`.                                      |
| DJANGO-27 | Pipeline   | 6.3   | **Proibido** chaves em `new_values` que não sejam campo do model — usar parâmetros explícitos da função.                    |
| DJANGO-28 | Pipeline   | 6.4   | Campos auxiliares de `ModelForm`: `required=False`; `pop` no fluxo oposto (`add` xor `change`).                             |
| DJANGO-29 | Teste      | 7     | Testes manuais/automatizados § **7** e `tests_admin_changelist_default_filters.py` **devem** ser respeitados.               |

**Índice por tema:**

| Tema        | IDs                   |
| ----------- | --------------------- |
| Layout      | DJANGO-01 … DJANGO-03 |
| Models      | DJANGO-04 … DJANGO-06 |
| Admin popup | DJANGO-07, DJANGO-08  |
| Changelist  | DJANGO-09 … DJANGO-17 |
| Sidebar     | DJANGO-18 … DJANGO-24 |
| Pipeline    | DJANGO-25 … DJANGO-28 |
| Teste       | DJANGO-29             |

---

## 1. Layout do projeto **(DJANGO-01**–**DJANGO-03)**

### 1.1 Django na raiz **(DJANGO-01)**

```
classificador-receita/
├── manage.py
├── classificador/          # settings, urls, wsgi
├── apps/
├── scripts/
├── schemas/
├── docs/
├── data-raw/
└── data/
```

Layout de `docs/assets/`, `data-raw/`, `data/`: ADR-005.

### 1.2 Apps em `apps/` **(DJANGO-02)**

```bash
poetry run python manage.py startapp <nome> apps/<nome>
```

### 1.3 `PYTHONPATH` e `INSTALLED_APPS` **(DJANGO-03)**

Em `classificador/settings.py` após `BASE_DIR`:

```python
import sys
sys.path.insert(0, str(BASE_DIR / "apps"))
```

`INSTALLED_APPS`: `"core"`, não `"apps.core"`.

---

## 2. Models bitemporais (`apps/core`) **(DJANGO-04**–**DJANGO-06)**

### 2.1 Classe base **(DJANGO-04)**

`BitemporalModel` (abstrata): `data_vigencia_inicio`/`fim`, `data_registro_inicio`/`fim`; validação de intervalos em `clean()`.

### 2.2 Sentinelas **(DJANGO-05)**

`9999-12-31` = vigência/registro ativos.

### 2.3 Chaves e constraints **(DJANGO-06)**

PK `id` auto-increment; unicidade bitemporal via `UniqueConstraint` `(identificador, data_registro_inicio)`.

### Implementação de referência

Seis entidades GSIM: `SerieClassificacao`, `Classificacao`, `NivelHierarquico`, `ItemClassificacao`, `VersaoClassificacao`, `VarianteClassificacao`. Regras de domínio em specs temáticas e `code_*.py`.

Admin: `list_display`, `list_filter`, `raw_id_fields`, `date_hierarchy`; `data_registro_*` readonly.

Migrations iniciais: `apps/core/migrations/0001_initial.py`.

**Pontos de atenção (não normativos):** gestão híbrida de `data_registro_fim` (ADR-001); managers `as-of` futuros; `db_table` em português.

---

## 3. Popups FK na add **(DJANGO-07**, **DJANGO-08)**

Em formulários **add** de `Classificacao`, `NivelHierarquico` e `ItemClassificacao`, lupas configuradas com `popup_default_registro_ativo_ano_corrente` abrem changelist com `registro_ativo=ativo_corrente` (`RegistroAtivoFilter`).

| ModelAdmin (add)    | FKs                                              |
| ------------------- | ------------------------------------------------ |
| `Classificacao`     | `serie_id`                                       |
| `NivelHierarquico`  | `classificacao_id`                               |
| `ItemClassificacao` | `classificacao_id`, `parent_item_id`, `nivel_id` |

**(DJANGO-08):** não na **change**; critério «Ano Corrente» = sobreposição com ano civil + registo ativo (não «só hoje»).

Formulário `ItemClassificacao`: ver `spec_itemClassificacao_formulario.md`.

---

## 4. Pré-filtro padrão na changelist **(DJANGO-09**–**DJANGO-17)**

### 4.1 Ciclo de vida **(DJANGO-09**–**DJANGO-11)**

| Conceito                         | Comportamento                                                   |
| -------------------------------- | --------------------------------------------------------------- |
| Entrada fria **(DJANGO-09)**     | GET sem filtros → 302 com `changelist_default_filters`          |
| Modo sem default **(DJANGO-10)** | Após «Limpar todos» → sem filtros; paginar/ordenar não reaplica |
| Reentrada **(DJANGO-11)**        | Sair e voltar → default reaplicado                              |

**Não desejado:** default a cada clique na sidebar; flag «limpei» persistir entre visitas distintas.

### 4.2 Mecânica **(DJANGO-12**–**DJANGO-16)**

1. **(DJANGO-12):** `ChangelistDefaultFilterRedirectMixin` — GET vazio + sem flag sessão → redirect com `changelist_default_filters`.
2. **(DJANGO-13):** «Todos» → `registro_ativo=todos` (no-op em `queryset()`).
3. **(DJANGO-14):** «Limpar todos» → `__changelist_skip_default=1`; sessão `admin_changelist_skip_default:<app>.<model>`.
4. **(DJANGO-15):** popups com `?_popup=1` — sem redirect.
5. **(DJANGO-16):** `AdminChangelistSkipDefaultScopeMiddleware` limpa flags stale.
6. `preserved_filters` do Django preserva recorte após save/edit.

Constantes: `REGISTRO_ATIVO_VALUE_HISTORICO` → `ativo_historico`; `REGISTRO_ATIVO_VALUE_ANO_CORRENTE` → `ativo_corrente`.

### 4.3 Defaults por `ModelAdmin` **(DJANGO-17)**

| Changelist                                                     | Default query                      | Rótulo                |
| -------------------------------------------------------------- | ---------------------------------- | --------------------- |
| `SerieClassificacao`, `Classificacao`, `VarianteClassificacao` | `registro_ativo=ativo_historico`   | Ativos (Histórico)    |
| `NivelHierarquico`, `ItemClassificacao`, `VersaoClassificacao` | `registro_ativo=ativo_corrente`    | Ativos (Ano Corrente) |
| `AliasLexico`                                                  | `lista_abreviacoes_registro=ativo` | Registro ativo        |

Configuração: mixin + `changelist_default_filters = {REGISTRO_ATIVO_QUERY_PARAM: <valor>}`.

---

## 5. Recolhimento do sidebar de filtros **(DJANGO-18**–**DJANGO-24)**

### 5.1 Comportamento **(DJANGO-18**, **DJANGO-19)**

A cada GET na changelist (critérios: GET, sem `_popup`, `len(list_filter) > 3`): expandir apenas filtros em `changelist_expanded_filters` e filtros com valor activo. **Stateless** — nova entrada recomputa estado **(DJANGO-19)**.

### 5.2 Defaults e exceções **(DJANGO-20**, **DJANGO-21)**

| Changelist                                     | Expandidos default                       |
| ---------------------------------------------- | ---------------------------------------- |
| Bitemporais com >3 filtros                     | `registro_ativo`, `data_registro_inicio` |
| `VersaoClassificacao`, `VarianteClassificacao` | só `registro_ativo`                      |
| `BaseLegalTecnica`                             | mixin **não** aplicado **(DJANGO-21)**   |
| `AliasLexico`                                  | ≤3 filtros — no-op **(DJANGO-21)**       |

### 5.3 Implementação **(DJANGO-22**, **DJANGO-23)**

- `ChangelistSidebarFilterCollapseMixin` → `request.changelist_expanded_filter_params`
- `ChangelistWithClearAllSkipDefault` anota `spec.core_collapse_open`
- **(DJANGO-22):** `filters.js` override sem `sessionStorage`
- **(DJANGO-23):** auto-expand por `spec.expected_parameters()` com valor activo (exceto sentinela `todos`)

### 5.4 Template **(DJANGO-24)**

`apps/core/templates/admin/filter.html` — `{{ title }}` direto no `<summary>`.

MRO recomendado:

```python
class MeuAdmin(
    ChangelistDefaultFilterRedirectMixin,
    ChangelistSidebarFilterCollapseMixin,
    …,
    admin.ModelAdmin,
):
    changelist_expanded_filters = frozenset({REGISTRO_ATIVO_QUERY_PARAM})  # opcional
```

---

## 6. Pipeline bitemporal — apenas campos do model **(DJANGO-25**–**DJANGO-28)**

Contrato entre `BitemporalChangeHandler` e `apply_bitemporal_update` (`apps/core/bitemporal_update.py`).

| ID        | Regra                                                                       |
| --------- | --------------------------------------------------------------------------- |
| DJANGO-25 | Handler: só campos com `model._meta.get_field(name)` entram em `new_values` |
| DJANGO-26 | Serviço: `new_values` ⊆ `concrete_fields`                                   |
| DJANGO-27 | Sem metadados disfarçados de coluna em `new_values`                         |
| DJANGO-28 | Campos auxiliares de form: `required=False`; `pop` no fluxo oposto          |

**Caso de referência:** `receita_nome_base_mode` em `ItemClassificacaoForm` — `spec_itemClassificacao_criar_nome.md`.

---

## 7. Testes **(DJANGO-29)**

### Changelist default

1. Entrada `ItemClassificacao` → `registro_ativo=ativo_corrente`
2. Limpar todos → sem query; sem default forçado
3. Paginar na lista limpa → sem default
4. Reentrada via menu → default reaplicado
5. Limpar → change → voltar → default reaplicado
6. «Todos» → `registro_ativo=todos`; sem redirect

Automatizado: `apps/core/tests_admin_changelist_default_filters.py`.

### Sidebar collapse

1. `ItemClassificacao` → só Status + Data Início Registro abertos
2. Expandir «Categoria» sem aplicar → change → volta recolhido
3. Aplicar «Categoria» → auto-expand enquanto parâmetro na URL
4. Limpar todos → só os 2 declarados
5. Popup raw_id → comportamento Django padrão
6. `AliasLexico` → padrão Django

### Pipeline

- **T-pipe.1:** change `ItemClassificacao` sem `receita_nome_base_mode` em `create(**kwargs)`
- **T-pipe.2:** form com campo auxiliar sem coluna → update conclui

---

## Specs relacionadas

| Spec                                   | Relação                      |
| -------------------------------------- | ---------------------------- |
| `spec_conventions.md`                  | `code_*`, idioma             |
| `spec_itemClassificacao_formulario.md` | UI `ItemClassificacao`       |
| `spec_itemClassificacao_criar_nome.md` | Campo auxiliar **DJANGO-28** |
| ADR-001, ADR-005                       | Bitemporalidade e dados      |
