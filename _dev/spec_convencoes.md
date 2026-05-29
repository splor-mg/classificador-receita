# Convenções transversais do repositório

Este documento centraliza **convenções organizadoras e semânticas** do projeto
Classificador de Natureza de Receita. Especificações funcionais (comportamento,
fluxos de tela, mensagens normativas) permanecem em `_dev/spec_*.md` temáticas
— por exemplo `spec_itemClassificacao_criar_nome.md`, `spec_foreignKeys_vigencia.md`.

**Manutenção:** ao introduzir ou renomear um módulo coberto aqui, atualizar
esta spec. Nas specs funcionais, alterar apenas **caminhos de ficheiro** quando
necessário; não duplicar a política do prefixo `code_` em cada documento.

**Referências relacionadas:**

- ADR-001 (`docs/adr/adr-001_bitemporalidade.md`) — bitemporalidade
- `_dev/spec_django.md` — estrutura Django, mapeamento de campos temporais
- `_dev/spec_agents.md` — SDD e protocolo para agentes de IA (leitura, contradições)

---

## Idioma e nomenclatura

### Camadas de idioma (visão geral)

| Camada | Onde | Idioma | Notas |
|--------|------|--------|--------|
| **Semântica de produto** | `_dev/spec_*.md` | **Português do Brasil** | Tradução para inglês pode existir em paralelo no futuro |
| **Contrato de dados** | `schemas/`, `schemas/dominios/*.yaml` | Identificador de domínio pode ser **PT** (`orgaos_entidades`) | Catálogo de negócio; `custom.domainRef` |
| **Implementação** | `apps/core/code_*.py`, funções, testes | **Inglês** (regra geral) | Internacionalização e PEP 8 |
| **Persistência / modelo** | nomes de campos (`orgao_responsavel`, …) | **Como no schema** | Não renomear por i18n sem migração e spec |

**Códigos de valor** no catálogo (ex.: `SEF-MG`, `STN-BRA`) são dados/contrato, não nomenclatura de módulo.

### Especificações (`_dev/spec_*.md`)

- Redigir em **português do Brasil**.
- É permitido — e muitas vezes desejável — usar **termos técnicos em inglês** no
  meio do texto quando forem vocabulário usual (ex.: `foreignKey`, `null`,
  `valid_time`, `commit`, nomes de campos do modelo como `receita_cod`).
- Não é obrigatório traduzir identificadores que já existem no código.

### Catálogos em `schemas/dominios/`

- Cada arquivo define um **identificador de domínio** (`identifier: orgaos_entidades`)
  e a lista `values` (códigos permitidos).
- O nome do arquivo YAML pode permanecer alinhado ao identificador de negócio em
  português: `orgaos_entidades.yaml`.
- A implementação Django correspondente fica em **`apps/core/code_<nome_em_inglês>.py`**
  (tabela abaixo). Constantes Python podem manter prefixo alinhado ao identificador
  do domínio (ex.: `ORGAOS_ENTIDADES_CHOICES`).

| YAML (`schemas/dominios/`) | Módulo Python (`apps/core/`) | Campos que consomem |
|----------------------------|------------------------------|---------------------|
| `orgaos_entidades.yaml` | `code_organizations_entities.py` | `orgao_responsavel` em `SerieClassificacao`, `BaseLegalTecnica` |

Ao acrescentar domínio: criar YAML, módulo `code_*` espelho, linha nesta tabela e
entrada no inventário `code_*` abaixo.

### Código Python e scripts (`apps/`, `scripts/`, testes)

| Artefato                                                                     | Idioma / convenção                                                                  |
| ---------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| **Nome de arquivo** (módulos `.py`, espelhos de teste)                       | **Inglês** (`snake_case`), alinhado ao inventário `code_*` e aos padrões existentes |
| **Funções, classes, métodos, constantes**                                    | **Inglês** (`snake_case` / `PascalCase`), salvo constantes já ligadas a identificador de domínio em PT |
| **Comentários** (`#`, docstrings de módulo quando explicam regra de negócio) | **Português do Brasil**, em primeira instância                                      |
| **Mensagens ao usuário** (Admin, `ValidationError`, templates)               | **Português do Brasil**, salvo spec em contrário                                    |

**Termos técnicos em comentários e docstrings:** a orientação de português **não
proíbe** manter termos consagrados em inglês (`ForeignKey`, `null`, `valid_time`,
`queryset`, etc.) quando traduzir prejudicar clareza ou duplicar o identificador do código.

**JavaScript do Admin** (`apps/core/static/`): nomes de funções e arquivos em
**inglês** (`code_name.js`, `initCodeName`); textos de UI seguem as specs de domínio.

---

## Glossário temporal (bitemporal)

| Termo (inglês)       | Campos no modelo                            | Uso no domínio                                                |
| -------------------- | ------------------------------------------- | ------------------------------------------------------------- |
| **valid_time**       | `data_vigencia_inicio`, `data_vigencia_fim` | Período em que a informação vale no orçamento / classificador |
| **transaction_time** | `data_registro_inicio`, `data_registro_fim` | Período em que o sistema considerou o registo verdadeiro      |

Nomes de módulos em inglês (`valid_time`, `transaction_time`) alinham-se ao
ADR-001 e a `_dev/spec_django.md`. Rótulos de interface e mensagens ao utilizador
podem permanecer em português («vigência», «registro»).

---

## Prefixo `code_` em `apps/core/`

### Definição

Ficheiros Python em `apps/core/` cujo nome começa por **`code_`** formam o
**pacote de regras e helpers de negócio reutilizáveis** do classificador:

- Lógica testável sem acoplar a HTTP, templates ou rotas do Admin
- Consumida por `models`, `forms`, `admin`, handlers e módulos irmãos `item_*`
- Documentada funcionalmente nas specs `_dev/spec_*` correspondentes

O prefixo **não** significa apenas «dígitos de `receita_cod`»: inclui nome,
hierarquia, máscara, FK temporal, canonização de entrada no Admin e **catálogos
de domínio** espelhados de `schemas/dominios/`.

### O que fica fora de `code_`

- `models.py`, migrações, `admin.py`, templates, static/JS do Admin
- Scripts em `scripts/`, schemas Frictionless em `schemas/`
- Módulos de orquestração por fluxo (`item_classificacao_code_lookup.py`,
  `admin_handlers.py`, etc.) — podem **importar** `code_*`, mas não usam o prefixo

### Subfamílias (orientação)

| Subfamília             | Exemplos                      | Tema                                                     |
| ---------------------- | ----------------------------- | -------------------------------------------------------- |
| Nome / radical         | `code_name_*`                 | Protocolo de `receita_nome`, abreviação, validação G0–G1 |
| Máscara e apresentação | `code_mask`                   | Máscara e formatação de código por vigência              |
| Hierarquia do item     | `code_parent_item_validation` | Mãe, nível, saltos, zeros canónicos, endpoints JSON      |
| FK + valid_time        | `code_valid_time_fk_*`        | Contenção de vigência em FK; reaponte da linha apontada  |
| Entrada / placeholders | `code_null_normalization`     | `NULL` e `-` → ausência canónica em campos texto         |
| Catálogo de domínio    | `code_organizations_entities` | Choices de `orgaos_entidades` → `orgao_responsavel`      |

### Par valid_time + FK (vocabulário)

Dois módulos tratam o mesmo tema (spec `_dev/spec_foreignKeys_vigencia.md`):

| Módulo                             | Responsabilidade                                                                               |
| ---------------------------------- | ---------------------------------------------------------------------------------------------- |
| `code_valid_time_fk_validation.py` | Valida que a vigência do filho está contida na do alvo da FK (união contígua quando aplicável) |
| `code_valid_time_fk_resolution.py` | Reaponta a FK para linha compatível ao gravar (`apply_temporal_fk_resolution`)                 |

Ambos usam o segmento **`valid_time_fk`** no nome do ficheiro, alinhado ao eixo
**valid_time** (ADR-001). A função pública `apply_temporal_fk_resolution` mantém
o nome histórico.

---

## Inventário atual de módulos `code_*`

| Módulo                             | Responsabilidade resumida                                      |
| ---------------------------------- | -------------------------------------------------------------- |
| `code_mask.py`                     | Máscara de `receita_cod` por classificação/vigência            |
| `code_name_abbrev.py`              | Radical abreviado, modo base, compactação A6                   |
| `code_name_connectives.py`         | Conectivos e pontuação (SSOT para abreviação e léxico)         |
| `code_name_messages.py`            | Textos do fluxo de nome no Admin (`code_name_messages_dict`)   |
| `code_name_validation.py`          | Guardrails G0/G1 e predicados de `receita_nome`                |
| `code_null_normalization.py`       | Placeholders `NULL` / `-` → `None` em CharField/TextField      |
| `code_parent_item_validation.py`   | Regras de `parent_item_id`, hierarquia, saltos, intermediários |
| `code_valid_time_fk_resolution.py` | Reaponte automático de FK por vigência                         |
| `code_valid_time_fk_validation.py` | Contenção temporal filho ⊆ alvo(s) da FK                       |
| `code_organizations_entities.py`   | Catálogo `orgaos_entidades` (choices / optgroup no Admin)        |

**Testes espelhados (sem prefixo `code_` no nome):** `tests_code_name.py`,
`tests_code_parent_item_validation.py`, etc.

**Front-end Admin:** `static/core/js/code_name.js` — funções `initCodeName`,
`validateCodeNameOnSubmit`, …; ver `spec_itemClassificacao_criar_nome.md`.

---

## Renomeações históricas (referência)

| Antes                            | Depois                                                                    |
| -------------------------------- | ------------------------------------------------------------------------- |
| `classification_naming_*`        | `code_name_*`                                                             |
| `parent_item_validation.py`      | `code_parent_item_validation.py`                                          |
| `temporal_fk_resolution.py`      | `code_valid_time_fk_resolution.py` (via `code_temporal_fk_resolution.py`) |
| `code_temporal_fk_resolution.py` | `code_valid_time_fk_resolution.py`                                        |
| `vigencia_fk_validation.py`      | `code_valid_time_fk_validation.py`                                        |
| `null_normalization.py`          | `code_null_normalization.py`                                              |
| `domain_choices.py`              | `code_organizations_entities.py`                                          |

APIs públicas (nomes de funções, códigos `ValidationError`) podem manter
vocabulário anterior (`validate_vigencia_contained_in_fk_targets`, …) mesmo após
rename de ficheiro.
