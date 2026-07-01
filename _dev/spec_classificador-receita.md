# Especificação local — classificador-receita

Normas de **processo SDD** deste repositório que complementam ou divergem do catálogo sincronizado em `_dev/` (`spec_agents`, `spec_commits`, `spec_issues`, …).

**Precedência** (mesmo tema de processo): contrato maduro em `docs/specs/` ou `specs/` → **este arquivo** (secção correspondente) → cópia sync do manifest → `toolkit/<tool>/specs/`. Ver `_dev/spec_agents.md` § **1.2** (**AGENTS-22**, **AGENTS-25**).

Registre aqui overrides de **como** trabalhar (idioma de commits, escopos, convenções de equipe, …). Regras de **negócio** e comportamento de domínio ficam em `spec_<domínio>.md` locais ou no contrato maduro — não neste arquivo (**AGENTS-26**).

Secções vazias podem ser omitidas; crie uma secção ao documentar a primeira regra daquele tema. Alinhe os títulos às chaves do manifest do catálogo.

## Agents

**Identidade:** este repositório implementa o **Classificador de Natureza de Receita** (Django Admin, modelos bitemporais, regras de classificação orçamentária).

**Modelo de trabalho:** SDD com convenções transversais neste arquivo (§ **Convenções**) e implementação assistida por IA, **rastreável** às specs de domínio em `_dev/spec_*.md` locais.

**Overrides de processo (pós-sync do catálogo):** commits e issues em **português do Brasil** — § **Commits** e § **Issues** abaixo prevalecem sobre `_dev/spec_commits.md` e `_dev/spec_issues.md` (**AGENTS-25**). Não reeditar entradas sync do manifest para reintroduzir PT-BR.

### Ordem de leitura local (tarefa de domínio)

Após `_dev/spec_agents.md` § **1.2** e **este arquivo** (secção do tema):

1. **`spec_classificador-receita.md` § Convenções** — nomenclatura, `code_*`, idioma, layout de dados.
2. **Specs temáticas** ligadas à tarefa (ex.: nome no add → `spec_itemClassificacao_criar_nome.md`).
3. **`spec_django.md`** — Admin, models bitemporais, estrutura Django.
4. **ADRs em `docs/adr/`** — bitemporalidade (**ADR-001**), chaves (**ADR-003**), governança de BD (**ADR-004**), layout de dados (**ADR-005**).
5. **`spec_importar.md`** / futuros `spec_import_*.md` — protocolo de importação *(detalhe operacional ainda em elaboração)*.
6. Par entrada sync + `*_new.md` — só para chaves do manifest; aplicar `_dev/spec_agents.md` § **10**; exceções locais vão para **este arquivo**, não para `spec_agents.md` sync.

Não inventar regra de domínio sem base em spec ou código; sinalizar lacunas ao desenvolvedor (**AGENTS-09**).

### Onde registrar mudanças

| Tipo de mudança                                      | Onde documentar                                              |
| ---------------------------------------------------- | ------------------------------------------------------------ |
| Comportamento, fluxo Admin, mensagens ao usuário     | Spec temática `_dev/spec_<domínio>.md` (trechos afetados)    |
| Novo módulo `code_*` ou rename                       | Inventário em **§ Convenções** (neste arquivo)               |
| Decisão arquitetural duradoura                       | ADR em `docs/adr/`                                           |
| Layout `docs/assets/`, `data-raw/`, `data/`          | **ADR-005** + § **Convenções**; import em `spec_importar.md` |
| Overrides SDD (commits, escopos, idioma de processo) | **Este arquivo**                                             |
| Anotações pessoais                                   | `_dev/toDo.md` (`dev(toDo)` — § **Commits**)                 |

### Implementação: `code_*` vs Admin

- Regras de negócio **reutilizáveis** e testáveis → `apps/core/code_*.py` (ver § **Convenções**).
- Orquestração Admin, endpoints JSON, templates, static/JS → módulos de fluxo (`classification_item_*`, `admin_handlers.py`, `admin.py`, …); podem **importar** `code_*`, mas **não** usam o prefixo `code_`.
- Não duplicar a política global de `code_*` em cada spec funcional; citar caminhos ou IDs.

### Protocolo `*_new.md` (entradas sync do manifest)

Sidecars `spec_<chave>_new.md` são snapshot do catálogo para comparação. Após pull que substitui cópias híbridas:

1. Conteúdo **genérico** do catálogo permanece na entrada sync (read-only).
2. Regras **deste projeto** (Django, `code_*`, ADRs, PT-BR) ficam em **`spec_classificador-receita.md`** ou em specs de domínio locais — **não** regravar em `spec_agents.md`, `spec_conventions.md`, etc.
3. Fundir ou elevar trechos genéricos conforme `_dev/spec_agents.md` § **10**; remover `*_new.md` quando o merge estiver completo.

### Idioma da documentação (pt-BR)

Specs em `_dev/`, ADRs, páginas em `docs/` e README: **português do Brasil** (não português de Portugal).

| Preferir (pt-BR) | Evitar (pt-PT)                           |
| ---------------- | ---------------------------------------- |
| arquivo          | ficheiro                                 |
| artefato         | artefacto                                |
| usuário          | utilizador                               |
| registro         | registo                                  |
| seção            | secção                                   |
| conceitual       | conceptual                               |
| intermediário    | intermédio                               |
| refatoração      | refactor (como substantivo de documento) |

Termos técnicos em inglês (`foreignKey`, `valid_time`, identificadores de código) permanecem como estão. **Mensagens ao usuário final no Admin** (templates, `ValidationError`, textos de UI): **português do Brasil**, salvo spec em contrário.

### Índice técnico (referência rápida)

| Tema                           | Onde no repositório                                                    |
| ------------------------------ | ---------------------------------------------------------------------- |
| Commits e staging              | `spec_classificador-receita.md` § **Commits** + `_dev/spec_commits.md` |
| Nomenclatura, `code_*`, idioma | **Este arquivo** § **Convenções**                                      |
| Admin, models, migrações       | `spec_django.md`, ADRs                                                 |
| Python (estilo)                | `apps/core/` — PEP 8; seguir o arquivo tocado                          |
| Contratos JSON no Admin        | ex. `spec_itemClassificacao_foreignKeys_lookup.md`                     |
| RFC 2119 em specs              | `deve` / `não deve` / `pode` nas specs normativas                      |

Respostas do assistente na IDE: **inglês** (**AGENTS-07**). Código e comentários em arquivos Python: **inglês** (**AGENTS-08**).

## Commits

Override de **COMMITS-05** e § **3.1** (redação): título e corpo das mensagens em **português do Brasil** — prevalece sobre `_dev/spec_commits.md` § **3** (**AGENTS-25**).

| Parte                               | Idioma                                                  |
| ----------------------------------- | ------------------------------------------------------- |
| Título `(<tipo>)(<escopo>): …`      | **Português do Brasil**                                 |
| Corpo (após bloco `See`, se houver) | **Português do Brasil**                                 |
| Linhas `See …`                      | Igual à baseline — copiar de `_dev/_dev.md` (§ **3.2**) |

- Após `(<escopo>): `: verbo no **infinitivo** (*adicionar*, *corrigir*, *documentar*, *renomear*, *atualizar*, …); corpo em português claro, foco no *porquê*.
- Estrutura Conventional Commits, `See` (**COMMITS-06**), modo sugestão vs execução, staging § **8**: `_dev/spec_commits.md` — **não** repetir aqui.

Override § **6** (`_dev/toDo.md`): título fixo `dev(toDo): atualizar anotações`.

### Escopos locais

Consultar **nesta ordem** ao sugerir escopo:

1. Temas já nomeados na tabela abaixo ou em § **Convenções**.
2. Spec funcional principal do diff: prefixo `spec_` + **primeiro segmento** até ao **segundo** `_` (ex.: `spec_itemClassificacao_criar_nome.md` → `itemClassificacao`).
3. Spec com um só segmento após `spec_`: usar o segmento inteiro (ex.: `spec_django.md` → `django`, `spec_importar.md` → `importar`).
4. **Rename de spec:** escopo do **nome antigo** do arquivo que motivou a mudança.

| Tema do commit                                           | Escopo sugerido                               | Tipo usual                  |
| -------------------------------------------------------- | --------------------------------------------- | --------------------------- |
| Pacote / rename `code_*`, regras transversais de módulos | `code` ou `code-name` (rename focado em nome) | `refactor` / `docs`         |
| Item de classificação (fluxos Admin)                     | `itemClassificacao`                           | `feat` / `fix` / `docs`     |
| FK e vigência temporal                                   | `foreignKeys`                                 | `feat` / `fix` / `docs`     |
| Validação de códigos / hierarquia                        | `validar`                                     | `feat` / `fix` / `test`     |
| Estrutura Django, Admin, models                          | `django`                                      | `feat` / `fix` / `refactor` |
| Filtros recolhidos do sidebar do Admin                   | `changelist-filters`                          | `feat` / `fix`              |
| Convenções transversais (este arquivo)                   | `convencoes`                                  | `docs(convencoes)`          |
| SDD, sync catálogo, `spec_agents`                        | `sdd`                                         | `docs(sdd)`                 |
| Commits, staging, agents (norma de processo)             | `commits`                                     | `docs(commits)`             |

| Arquivo da spec                                    | Escopo              |
| -------------------------------------------------- | ------------------- |
| `spec_itemClassificacao_criar_filho.md`            | `itemClassificacao` |
| `spec_itemClassificacao_criar_nome.md`             | `itemClassificacao` |
| `spec_itemClassificacao_editar_codigo.md`          | `itemClassificacao` |
| `spec_itemClassificacao_regras_hierarquia.md`      | `itemClassificacao` |
| `spec_itemClassificacao_formulario.md`             | `itemClassificacao` |
| `spec_itemClassificacao_foreignKeys_lookup.md`     | `itemClassificacao` |
| `spec_itemClassificacao_mascara_apresentacao.md`   | `itemClassificacao` |
| `spec_itemClassificacao_criar_codigo_existente.md` | `itemClassificacao` |
| `spec_foreignKeys_vigencia.md`                     | `foreignKeys`       |
| `spec_lista_abreviacoes.md`                        | `lista`             |
| `spec_django.md`                                   | `django`            |
| `spec_validar_codigos.md`                          | `validar`           |
| `spec_validar_qualidade.md`                        | `validar`           |
| `spec_importar.md`                                 | `importar`          |

### Prefixos de ID normativos (domínio local)

| Arquivo                                            | Prefixo    | Escopo                                                   |
| -------------------------------------------------- | ---------- | -------------------------------------------------------- |
| `spec_validar_codigos.md`                          | `VALCOD`   | Script `validate_code.py` e validação de `receita_cod`   |
| `spec_validar_qualidade.md`                        | `VALQUAL`  | Script `validate_quality.py` e quality dimensions        |
| `spec_itemClassificacao_regras_hierarquia.md`      | `ITEMRH`   | Regras de `parent_item_id` e hierarquia semântica        |
| `spec_foreignKeys_vigencia.md`                     | `FKVIG`    | Contenção temporal de FK e união contígua bitemporal     |
| `spec_importar.md`                                 | `IMPORT`   | Protocolo de importação (MINUTA; pipeline ADR-005)       |
| `spec_itemClassificacao_formulario.md`             | `ITEMFORM` | Formulário admin: largura `receita_cod` e limpar add     |
| `spec_itemClassificacao_foreignKeys_lookup.md`     | `ITEMLKP`  | Endpoints JSON lookup-parent / lookup-hierarchy no Admin |
| `spec_itemClassificacao_editar_codigo.md`          | `ITEMEC`   | Edição de `receita_cod` na change (blur, save, revert)   |
| `spec_itemClassificacao_mascara_apresentacao.md`   | `ITEMMASK` | Máscara visual admin (tier 1/2) e protocolo B1           |
| `spec_itemClassificacao_criar_codigo_existente.md` | `ITEMCEX`  | Alerta/erro CE e próximo código na add                   |

### Tipo vs arquivos (Django)

| Diff principal                                    | Tipo usual                                      |
| ------------------------------------------------- | ----------------------------------------------- |
| Só `_dev/spec_*.md`, `docs/`, README (sem código) | **`docs`**                                      |
| Código + specs alinhadas ao mesmo comportamento   | `feat` / `fix` / `refactor` + escopo do domínio |
| Só `apps/core/tests_*.py`                         | **`test`**                                      |
| Só `_dev/toDo.md`                                 | **`dev`**                                       |

`feat` reserva-se a mudança **implementada** em código, Admin ou JS/CSS visível.

### Exemplos (mensagens em PT-BR)

```
refactor(code): renomear módulos para pacote code_*

See #18
See https://github.com/splor-mg/classificador-receita/tree/migracao

Consolidar regras reutilizáveis em apps/core/code_*.py; atualizar inventário em spec_classificador-receita.md.
```

```
feat(itemClassificacao): bloquear submit quando código já existe na add

See #18
See https://github.com/splor-mg/classificador-receita/tree/migracao

Validação no cliente e no servidor; mensagem alinhada ao endpoint JSON.
```

```
docs(convencoes): documentar inventário code_* no repo-spec

See #18
See https://github.com/splor-mg/classificador-receita/tree/migracao

Migrar convenções locais para spec_classificador-receita.md após sync do catálogo.
```

Vários arquivos no **mesmo commit** quando houver **uma causa** (ex.: rename `code_*` + atualização de imports + inventário neste arquivo). Temas independentes → commits separados (§ **5.4** em `spec_commits.md`).

## Issues

Override de **ISSUES-05**: título e corpo do issue em **português do Brasil** — prevalece sobre `_dev/spec_issues.md` § **3** (**AGENTS-25**).

- Padrão `.github/issues/`, sentence case, ligação a commits (**ISSUES-01**–**04**, **ISSUES-08**): `_dev/spec_issues.md` — **não** repetir aqui.

### Prefixo temático

Quando o repositório usar escopo entre parênteses:

```text
(classificador) - Refatorar validação de código em componentes modulares
```

- Escopo raiz do produto: **`(classificador)`** — tema transversal do repositório.
- Escopos de módulo ou fluxo (minúsculas): `(django)`, `(itemClassificacao)`, `(foreignKeys)`, `(validar)`, `(specs)`, …
- Separador: ` - ` (espaço, hífen, espaço).
- Descrição: **sentence case** — ver `spec_issues.md` § **2.1**.

### Coerência issue ↔ commit

Ao implementar trabalho rastreado por issue:

- Referência no commit conforme `spec_commits.md` (`See …`, `Closes #NN`, `Refs #NN`).
- Manter coerência entre escopo do issue (`(django)`) e escopo do commit (`django`), quando aplicável.

## Convenções

Convenções **organizadoras e semânticas** do Classificador de Natureza de Receita. Comportamento funcional permanece nas specs temáticas (`spec_itemClassificacao_*.md`, `spec_foreignKeys_vigencia.md`, …).

**Manutenção:** ao introduzir ou renomear módulo `code_*`, domínio YAML ou tema transversal, atualizar **esta secção**. Nas specs funcionais, alterar apenas **caminhos de arquivo** quando necessário; não duplicar a política de `code_*` em cada documento.

**Nota:** normas de **toolkit shell**, entry point `toolkit/<tool>/<tool>.sh`, manifest multinível e migrations do catálogo (`spec_conventions.md` § **6**–**8**) **não se aplicam** a este repositório Django.

**Referências relacionadas:**

- **ADR-001** — `docs/adr/adr-001_bitemporalidade.md`
- **ADR-003** — `docs/adr/adr-003_chave-semantica.md`
- **ADR-004** — `docs/adr/adr-004_governanca-banco.md`
- **ADR-005** — `docs/adr/adr-005_layout-dados.md`
- `spec_django.md` — estrutura Django, mapeamento de campos temporais

### Layout de artefatos de dados (ADR-005)

Política completa: **`docs/adr/adr-005_layout-dados.md`**. Importação operacional: `spec_importar.md` *(protocolo `spec_import_*.md` a detalhar)*.

| Local                      | Missão resumida                                                            |
| -------------------------- | -------------------------------------------------------------------------- |
| `docs/assets/referencias/` | Fontes externas de referência; entrada típica do import                    |
| `data-raw/`                | Primeiro tratamento do import: normalização tabular do arquivo bruto       |
| `data/`                    | Lançamentos apurados a partir de `data-raw/`; gravação no BD pelo import   |
| `docs/assets/seed_*.csv`   | Recursos do `datapackage.yaml`; carga inicial via `carregar_classificador` |
| PostgreSQL                 | Fonte operacional em runtime (Admin, governança ADR-004)                   |

**Distinção obrigatória:** **carga** (seeds → BD) ≠ **importação** (fonte externa → `data-raw/` → `data/` → BD). O Django **não** lê `data/` nem `data-raw/` nos fluxos de carga existentes.

### Camadas de idioma

| Camada                    | Onde                                               | Idioma                                                    | Notas                               |
| ------------------------- | -------------------------------------------------- | --------------------------------------------------------- | ----------------------------------- |
| **Semântica de produto**  | `_dev/spec_*.md`, ADRs, `docs/`                    | **Português do Brasil**                                   | Tabela pt-BR vs pt-PT: § **Agents** |
| **Contrato de dados**     | `schemas/`, `schemas/dominios/*.yaml`              | Identificador de domínio pode ser PT (`orgaos_entidades`) | `custom.domainRef`                  |
| **Implementação**         | `apps/core/code_*.py`, funções, testes             | **Inglês**                                                | PEP 8                               |
| **Persistência / modelo** | campos (`orgao_responsavel`, …)                    | **Como no schema**                                        | Não renomear por i18n sem migração  |
| **Mensagens Admin / UI**  | templates, `ValidationError`, `code_name_messages` | **Português do Brasil**                                   | Ver specs de domínio                |

Códigos de valor no catálogo (`SEF-MG`, `STN-BRA`) são dados/contrato, não nomenclatura de módulo.

### Catálogos `schemas/dominios/` ↔ módulos `code_*`

- Cada YAML define `identifier` e `values` (códigos permitidos).
- Nome do arquivo YAML pode permanecer em português: `orgaos_entidades.yaml`.
- Implementação Django: `apps/core/code_<nome_em_inglês>.py`. Constantes Python podem usar prefixo do domínio (ex.: `ORGAOS_ENTIDADES_CHOICES`).

| YAML (`schemas/dominios/`) | Módulo Python (`apps/core/`)     | Campos que consomem                                             |
| -------------------------- | -------------------------------- | --------------------------------------------------------------- |
| `orgaos_entidades.yaml`    | `code_organizations_entities.py` | `orgao_responsavel` em `SerieClassificacao`, `BaseLegalTecnica` |

Ao acrescentar domínio: criar YAML, módulo `code_*` espelho, linha nesta tabela e entrada no inventário abaixo.

### Código Python (`apps/`, testes)

| Artefato                                        | Idioma / convenção                                                    |
| ----------------------------------------------- | --------------------------------------------------------------------- |
| Nome de arquivo (`.py`, testes espelhados)      | **Inglês** (`snake_case`), alinhado ao inventário `code_*`            |
| Funções, classes, métodos, constantes           | **Inglês**, salvo constantes ligadas a identificador de domínio em PT |
| Comentários e docstrings de regra de negócio    | **Português do Brasil** em primeira instância                         |
| Mensagens ao usuário (Admin, `ValidationError`) | **Português do Brasil**                                               |

Termos técnicos em comentários (`ForeignKey`, `valid_time`, `queryset`, …) podem permanecer em inglês.

**JavaScript do Admin** (`static/core/js/`): nomes de funções e arquivos em **inglês** (`code_name.js`, `initCodeName`); textos de UI seguem specs de domínio.

### Glossário temporal (bitemporal)

| Termo (inglês)       | Campos no modelo                            | Uso no domínio                                                |
| -------------------- | ------------------------------------------- | ------------------------------------------------------------- |
| **valid_time**       | `data_vigencia_inicio`, `data_vigencia_fim` | Período em que a informação vale no orçamento / classificador |
| **transaction_time** | `data_registro_inicio`, `data_registro_fim` | Período em que o sistema considerou o registro verdadeiro     |

Nomes de módulos em inglês (`valid_time_fk`, …) alinham-se ao ADR-001 e a `spec_django.md`. Rótulos de interface podem permanecer em português («vigência», «registro»).

### Prefixo `code_` em `apps/core/`

**Definição:** arquivos Python cujo nome começa por **`code_`** formam o pacote de **regras e helpers de negócio reutilizáveis**:

- Lógica testável sem acoplar a HTTP, templates ou rotas do Admin
- Consumida por `models`, `forms`, `admin`, handlers e módulos `classification_item_*`
- Documentada nas specs `_dev/spec_*` correspondentes

O prefixo inclui nome, hierarquia, máscara, FK temporal, normalização de entrada no Admin e catálogos espelhados de `schemas/dominios/`.

**Fora de `code_`:** `models.py`, migrações, `admin.py`, templates, static/JS, `scripts/`, schemas Frictionless, módulos de orquestração por fluxo (`classification_item_code_lookup.py`, `admin_handlers.py`, …).

#### Subfamílias

| Subfamília             | Exemplos                      | Tema                                                     |
| ---------------------- | ----------------------------- | -------------------------------------------------------- |
| Nome / radical         | `code_name_*`                 | Protocolo de `receita_nome`, abreviação, validação G0–G1 |
| Máscara e apresentação | `code_mask`                   | Máscara e formatação de código por vigência              |
| Hierarquia do item     | `code_parent_item_validation` | Mãe, nível, saltos, zeros canônicos, endpoints JSON      |
| FK + valid_time        | `code_valid_time_fk_*`        | Contenção de vigência em FK; reaponte da linha apontada  |
| Entrada / placeholders | `code_null_normalization`     | `NULL` e `-` → ausência canônica em campos texto         |
| Catálogo de domínio    | `code_organizations_entities` | Choices de `orgaos_entidades` → `orgao_responsavel`      |

#### Par valid_time + FK

Dois módulos, spec `spec_foreignKeys_vigencia.md`:

| Módulo                             | Responsabilidade                                                               |
| ---------------------------------- | ------------------------------------------------------------------------------ |
| `code_valid_time_fk_validation.py` | Valida que a vigência do filho está contida na do alvo da FK                   |
| `code_valid_time_fk_resolution.py` | Reaponta a FK para linha compatível ao gravar (`apply_temporal_fk_resolution`) |

Segmento **`valid_time_fk`** no nome do arquivo, alinhado ao eixo **valid_time** (ADR-001).

### Inventário atual de módulos `code_*`

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
| `code_organizations_entities.py`   | Catálogo `orgaos_entidades` (choices / optgroup no Admin)      |

**Testes espelhados:** `tests_code_name.py`, `tests_code_parent_item_validation.py`, `tests_classification_item_*.py` (fluxos `classification_item_*`).

**Front-end Admin:** `static/core/js/code_name.js` — `initCodeName`, `validateCodeNameOnSubmit`, …; ver `spec_itemClassificacao_criar_nome.md`.

### Renomeações históricas (`classification_*` → `code_*`)

| Antes                            | Depois                                                                    |
| -------------------------------- | ------------------------------------------------------------------------- |
| `classification_naming_*`        | `code_name_*`                                                             |
| `parent_item_validation.py`      | `code_parent_item_validation.py`                                          |
| `temporal_fk_resolution.py`      | `code_valid_time_fk_resolution.py` (via `code_temporal_fk_resolution.py`) |
| `code_temporal_fk_resolution.py` | `code_valid_time_fk_resolution.py`                                        |
| `vigencia_fk_validation.py`      | `code_valid_time_fk_validation.py`                                        |
| `null_normalization.py`          | `code_null_normalization.py`                                              |
| `domain_choices.py`              | `code_organizations_entities.py`                                          |

APIs públicas (`validate_vigencia_contained_in_fk_targets`, códigos `ValidationError`) podem manter vocabulário anterior após rename de arquivo.

## Versionamento

Este repositório **não** mantém `manifest.yaml` nem `CHANGELOG.md` no momento. Avaliar impacto conforme `_dev/spec_version.md` quando normas ou releases forem adotadas (**AGENTS-13**).

### Inventário de tags Git (**CONV-07**)

Manter **nesta secção** (não em `_dev/spec_conventions.md` sync). Atualizar ao criar tag `vX.Y.Z` (**AGENTS-20**, **VERSION-07**).

| Tag                                  | Commit (curto) | Data | Notas |
| ------------------------------------ | -------------- | ---- | ----- |
| *(nenhuma tag `v*` publicada ainda)* | —              | —    | —     |

Convenção de nome: prefixo `v` + SemVer (**CONV-06**). Tag anotada preferida: `git tag -a vX.Y.Z -m "Release X.Y.Z"`. Não executar `git tag` / `git push` de tag sem pedido explícito (**VERSION-08**, **AGENTS-11**).

## Domínio

Índice leve das specs **locais** (fora do manifest do catálogo) e ADRs. Comportamento detalhado permanece em cada arquivo.

### ADRs (`docs/adr/`)

| ADR                                                                                                             | Tema                                               |
| --------------------------------------------------------------------------------------------------------------- | -------------------------------------------------- |
| [ADR-001](https://github.com/splor-mg/classificador-receita/blob/migracao/docs/adr/adr-001_bitemporalidade.md)  | Bitemporalidade (`valid_time`, `transaction_time`) |
| [ADR-002](https://github.com/splor-mg/classificador-receita/blob/migracao/docs/adr/adr-002_gsim.md)             | GSIM                                               |
| [ADR-003](https://github.com/splor-mg/classificador-receita/blob/migracao/docs/adr/adr-003_chave-semantica.md)  | Chave semântica                                    |
| [ADR-004](https://github.com/splor-mg/classificador-receita/blob/migracao/docs/adr/adr-004_governanca-banco.md) | Governança do banco                                |
| [ADR-005](https://github.com/splor-mg/classificador-receita/blob/migracao/docs/adr/adr-005_layout-dados.md)     | Layout `docs/assets/`, `data-raw/`, `data/`        |

### Specs de domínio (`_dev/`)

| Spec                                               | Foco                                              |
| -------------------------------------------------- | ------------------------------------------------- |
| `spec_django.md`                                   | Admin, models bitemporais, estrutura do projeto   |
| `spec_itemClassificacao_criar_codigo_existente.md` | Bloqueio de código duplicado na add               |
| `spec_itemClassificacao_criar_filho.md`            | Criação de filho na hierarquia                    |
| `spec_itemClassificacao_criar_nome.md`             | Protocolo de `receita_nome`, abreviação, JS Admin |
| `spec_itemClassificacao_editar_codigo.md`          | Edição de código                                  |
| `spec_itemClassificacao_formulario.md`             | Formulário de item                                |
| `spec_itemClassificacao_foreignKeys_lookup.md`     | Lookup JSON de FK no Admin                        |
| `spec_itemClassificacao_mascara_apresentacao.md`   | Máscara e apresentação de código                  |
| `spec_itemClassificacao_navegacao.md`              | Navegação na árvore                               |
| `spec_itemClassificacao_regras_hierarquia.md`      | Regras de hierarquia                              |
| `spec_itemClassificacao_validar_hierarquia.md`     | Validação de hierarquia                           |
| `spec_foreignKeys_vigencia.md`                     | FK e contenção de vigência                        |
| `spec_lista_abreviacoes.md`                        | Lista de abreviações                              |
| `spec_validar_codigos.md`                          | Validação de códigos                              |
| `spec_validar_qualidade.md`                        | Validação de qualidade                            |
| `spec_importar.md`                                 | Importação (rascunho)                             |

### Lacunas conhecidas

- **`spec_import_*.md`** — protocolo operacional de importação (CLI, naming, gravação) a detalhar; índice transversal em § **Convenções** (layout ADR-005) e rascunho em `spec_importar.md`.
- Contrato maduro em `docs/specs/` ou `specs/` — **ainda não existe**; `_dev/spec_*.md` locais são a fonte de domínio até promoção (**AGENTS-01**).
