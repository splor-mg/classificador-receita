# Contexto SDD compilado (artefato `.sdd-context.yaml`)

Normas para o **artefato de contexto SDD** gerado no consumidor: índice compacto de regras, tarefas e escopos de path para assistentes de IA. **Esta spec** (`spec_context.md`) sincroniza via manifest; o **YAML gerado** **não** — vive só no repositório consumidor.

## Objetivo

Definir **onde** fica o contexto compilado, **como** regenerá-lo, **o que** contém (esquema v1) e **como** o assistente o usa junto com § **4.1** em [`spec_agents.md`](spec_agents.md) (**AGENTS-22**).

O artefato **complementa** specs Markdown em `_dev/` e anexos `@`: reduz tokens e deriva quando o operador inclui `_dev/.sdd-context.yaml` no prompt ou quando o assistente o lê após sync/commit.

**Não substitui** leitura integral de specs aplicáveis na ordem de § **4** em `spec_agents.md` — especialmente em contradição, precedência ou trechos normativos citados por ID.

## Referências

Os principais **conceitos** e **referências externas** que orientam **contexto compilado** neste catálogo são:

???+ note "Engenharia de contexto"

    Assistentes trabalham com **janela de contexto** limitada. Um índice YAML gerado a partir das specs sync + overrides locais concentra IDs, resumos e gatilhos de tarefa sem reenviar dezenas de páginas Markdown a cada turno.

    **Normas neste catálogo**

    - [`spec_agents.md`](spec_agents.md) § **4.1** (**AGENTS-22**) — releitura, anexos `@`, citação por ID.
    - Este arquivo — artefato `_dev/.sdd-context.yaml`, esquema v1, regeneração.

    **Referências externas**

    - [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — Anthropic; compactação e tokens de alto sinal.
    - [Context engineering (LangChain)](https://github.com/langchain-ai/context_engineering) — estratégias *write / select / compress / isolate*.

??? abstract "Gerador no toolkit SDD"

    O comando **`sdd context compile`** (implementação em `computer-setup/toolkit/sdd/context_compile.py`) lê o consumidor em **camadas de precedência** (§ **3.1.1**, **CONTEXT-09**): specs sync do manifest, overrides locais em `_dev/`, contrato maduro (`docs/specs/` ou `specs/`), e por último o hub `spec_conventions.md` só para IDs em falta. Escreve **`_dev/.sdd-context.yaml`**.

    **Não** confundir com pasta **`.sdd/`** — o artefato canônico é **um arquivo** na raiz de `_dev/`, não um subdiretório oculto.

??? info "Sync do catálogo vs artefato gerado"

    | Artefato                 | Sync manifest (`sdd … -pl`) | Versionar no Git do consumidor |
    | ------------------------ | --------------------------- | ------------------------------ |
    | `_dev/spec_context.md`   | Sim (`entries.context`)     | Sim (cópia read-only da norma) |
    | `_dev/.sdd-context.yaml` | **Não**                     | **Sim** (saída gerada)         |

    Entradas `entries.*` do manifest cobrem **normas upstream** em `docs/` — **não** saídas geradas pelo toolkit.

??? quote "Normas e artefatos deste catálogo"

    - [`spec_agents.md`](spec_agents.md) — ordem de leitura, **AGENTS-22**.
    - [`spec_conventions.md`](spec_conventions.md) — prefixos de ID, índice § **2**, modelo de documento § **9** (**CONV-32**–**38**).
    - [`spec_commits.md`](spec_commits.md) — commitar regeneração com escopo `context` quando aplicável.
    - `_dev/spec_<nome-repo>.md` — overrides SDD incluídos na compilação quando existir.

??? note "Linguagem normativa e IDs"

    *Deve*/*não deve* conforme [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) — [`spec_conventions.md`](spec_conventions.md) **Referências**. IDs: prefixo **`CONTEXT`**; índice completo em `spec_conventions.md` § **2**.

## Como citar este documento

| Mecanismo           | Uso                                                   |
| ------------------- | ----------------------------------------------------- |
| **Seção numerada**  | `§ 2.1` — navegação neste arquivo.                    |
| **ID normativo**    | `CONTEXT-03` — citação estável.                       |
| **Índice completo** | [`spec_conventions.md`](spec_conventions.md) § **2**. |

**Índice de IDs normativos deste arquivo:**

| ID         | Tema       | Seção | Resumo                                                                                                                                                                                                                    |
| ---------- | ---------- | ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CONTEXT-01 | Artefato   | 1.1   | O contexto SDD compilado **deve** residir em `_dev/.sdd-context.yaml` na raiz do consumidor — **não** substituir por pasta `.sdd/` ou outro layout sem norma explícita no contrato maduro.                                |
| CONTEXT-02 | Artefato   | 1.2   | Operador e assistente **não devem** editar `_dev/.sdd-context.yaml` à mão; alterações normativas vão para specs fonte e o artefato **deve** ser regenerado com `sdd context compile`.                                     |
| CONTEXT-03 | Artefato   | 1.3   | O consumidor **deve** executar `sdd context compile` após sync de specs, bump de `areas.*`, alteração de overrides locais ou primeira adopção desta norma.                                                                |
| CONTEXT-04 | Artefato   | 1.4   | `_dev/.sdd-context.yaml` **deve** ser versionado no Git do consumidor; commit com escopo `context` quando o diff principal for só o artefato — **não** adicionar entrada `entries.*` no manifest.                         |
| CONTEXT-05 | Assistente | 2     | O artefato compilado complementa **AGENTS-22** — operador **pode** anexar `@`; assistente **deve** usar `rules`/`tasks` como índice e **não deve** dispensar leitura integral de specs quando exigida.                    |
| CONTEXT-06 | Esquema    | 3     | O gerador **deve** emitir YAML com `schema_version: 1`; evolução para versões superiores **deve** ser documentada nesta spec antes de consumidores adotarem.                                                             |
| CONTEXT-07 | Esquema    | 3     | Campos top-level v1 **obrigatórios**: `schema_version`, `generated_at`, `generator`, `repo`, `catalog`, `consumer`, `sources`, `rules`, `tasks`, `path_scopes` — lista `sources` **gerada** em runtime.                   |
| CONTEXT-08 | Gerador    | 4     | Comando canônico **`sdd context compile`** — implementação em `computer-setup/toolkit/sdd/context_compile.py`; detalhes operacionais ficam em `toolkit/sdd/specs/`, **não** duplicados aqui salvo norma transversal nova. |
| CONTEXT-09 | Compilação | 3.1.1 | Resolução de `rules` em quatro passos (sync → local `_dev/` → contrato maduro → hub § **2** só fallback); ID já presente **pode** ser sobrescrito pelo passo seguinte; passo 4 só acrescenta ausentes.                    |
| CONTEXT-10 | Compilação | 3.4   | Alvo de extração semântica: índice 4 colunas + camadas 2–6 do contrato § **9.11** (**CONV-37**); coluna **Resumo** alimenta `rules.<ID>.summary`; **Tema** disponível para filtros RAG.                                  |

**Índice por tema:**

| Tema       | IDs                                            |
| ---------- | ---------------------------------------------- |
| Artefato   | CONTEXT-01, CONTEXT-02, CONTEXT-03, CONTEXT-04 |
| Assistente | CONTEXT-05                                     |
| Esquema    | CONTEXT-06, CONTEXT-07                         |
| Gerador    | CONTEXT-08                                     |
| Compilação | CONTEXT-09, CONTEXT-10                         |

---

## 1. Artefato no consumidor

### 1.1 Caminho canônico **(CONTEXT-01)**

O contexto SDD compilado **deve** residir em:

```text
_dev/.sdd-context.yaml
```

relativo à **raiz do repositório consumidor**.

- **Deve** usar este caminho exato — **não** substituir por pasta `.sdd/`, `.sdd/context.yaml` ou outro layout sem norma explícita no contrato maduro do projeto.
- O assistente **deve** tratar o arquivo como **gerado** (ver § **1.2**).

### 1.2 Proibição de edição manual **(CONTEXT-02)**

Operador e assistente **não devem** editar `_dev/.sdd-context.yaml` à mão para alterar regras, tarefas ou escopos.

Alterações normativas **devem** ir para:

- specs sync do manifest em `_dev/spec_*.md`;
- overrides em `_dev/spec_<nome-repo>.md`;
- specs de domínio locais ou contrato maduro — conforme precedência em [`spec_agents.md`](spec_agents.md) § **1.2**.

Depois, **deve** regenerar o artefato (§ **1.3**, **CONTEXT-08**).

### 1.3 Gatilhos de regeneração **(CONTEXT-03)**

O consumidor **deve** executar **`sdd context compile`** (ou equivalente documentado no hub `toolkit/sdd/specs/`) quando:

| Evento                                       | Motivo                                                  |
| -------------------------------------------- | ------------------------------------------------------- |
| **`sdd … -pl`** ou sync manual de entrada    | Conteúdo das specs fonte mudou                          |
| Bump de `areas.*` ou `version:` relevante    | Metadados `catalog` / versões no índice desatualizados |
| Criação ou edição de `spec_<nome-repo>.md`   | Overrides locais entram na compilação                   |
| Adição de spec de domínio local referenciada | `sources` e `rules` derivadas do repo mudaram           |
| Primeira adopção desta norma no repo         | Artefato ainda inexistente                              |

Regeneração **pode** ser sugerida pelo assistente após sync — **não** executar silenciosamente sem pedido do operador quando o comando altera Git working tree.

### 1.4 Versionamento no Git **(CONTEXT-04)**

`_dev/.sdd-context.yaml` **deve** ser versionado no repositório **consumidor** (commit normal), salvo política explícita em contrato maduro.

- Mensagens de commit: escopo **`context`** quando o diff principal for o artefato gerado — ver [`spec_commits.md`](spec_commits.md).
- **Não** adicionar entrada `entries.*` no manifest para este arquivo — não é sync upstream.

---

## 2. Uso com assistentes de IA **(CONTEXT-05)**

Complementa [`spec_agents.md`](spec_agents.md) § **4.1** (**AGENTS-22**):

| Prática                     | Orientação                                                                                                                                                                                                |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Anexo `@`**               | Operador **pode** anexar `_dev/.sdd-context.yaml` em tarefas amplas (implementação, precedência, checklist SDD)                                                                                           |
| **Leitura pelo assistente** | **Deve** usar `rules` e `tasks` como índice; aplicar **`tasks.wrapup`** ao concluir implementação (**AGENTS-20**, **COMMITS-16**); citar **ID normativo** (`AGENTS-02`, `COMMITS-12`, …) ao aplicar regra |
| **Specs integrais**         | **Deve** ler ou reler Markdown normativo quando **AGENTS-22** exigir (contradição, deriva, seção citada, commits)                                                                                        |
| **Substituição**            | **Não deve** tratar o YAML como única fonte de verdade sobre domínio ou contrato maduro                                                                                                                   |

Ordem geral de leitura permanece § **4** em `spec_agents.md`; o artefato compilado **reduz** re-leitura repetida de índices longos, **não** elimina specs aplicáveis.

---

## 3. Esquema v1 **(CONTEXT-06**, **CONTEXT-07)**

O gerador **deve** emitir YAML com **`schema_version: 1`**. Campos top-level **obrigatórios** na v1:

| Campo            | Tipo (v1)  | Descrição                                                                                        |
| ---------------- | ---------- | ------------------------------------------------------------------------------------------------ |
| `schema_version` | inteiro    | Versão do esquema; valor **`1`** para esta norma                                                 |
| `generated_at`   | string ISO | Timestamp UTC da compilação                                                                      |
| `generator`      | string     | Identificador do gerador (ex.: `sdd context compile` + versão do toolkit)                        |
| `repo`           | object/map | Metadados do repositório consumidor (nome, path, branch quando aplicável)                        |
| `catalog`        | object/map | Origem do catálogo (repo, tag/`version`, `areas.*` relevantes)                                   |
| `consumer`       | object/map | Identificação do consumidor (manifest, variant, paths `_dev/`)                                   |
| `sources`        | list       | Arquivos **efetivamente lidos** nesta compilação (lista **gerada** — não hardcoded no gerador) |
| `rules`          | map        | Chave = **ID normativo**; valor = `summary` + `source` (path da spec)                            |
| `tasks`          | list       | Tarefas SDD (`commit`, `sync`, …) com `rule_ids` e `artifacts`                                   |
| `path_scopes`    | map/list   | Escopos de path (ex.: `_dev/`, `toolkit/sdd/`) para navegação rápida                             |

### 3.1 Regras (`rules`)

Cada entrada **deve** permitir ao assistente resolver **ID → resumo → arquivo fonte**:

```yaml
rules:
  AGENTS-22:
    summary: "Contexto visível; releitura; anexos @; citação por ID"
    source: _dev/spec_agents.md
  CONTEXT-02:
    summary: "Não editar .sdd-context.yaml à mão"
    source: _dev/spec_context.md
```

O campo **`source`** **deve** apontar para a **spec temática** ou override que **definiu** o ID na compilação — **não** para o hub § **2** de [`spec_conventions.md`](spec_conventions.md), salvo ID exclusivo desse hub (ex.: `CONV-*`) ou fallback quando o ID ainda não existir em outra camada (**CONTEXT-09**).

O gerador **deve** extrair IDs no formato **`PREFIXO-NN`** a partir de **linhas de tabela Markdown** no índice local **Como citar** de cada spec — alvo canônico: **quatro colunas** `| ID | Tema | Seção | Resumo |` (**CONV-33**, **CONTEXT-10**). Implementação atual aceita também tabelas legadas de **três colunas** (`| ID | Seção | Resumo |`) até evolução do parser.

Extração de IDs **no corpo** (âncoras `**(PREFIX-NN)**`, metadados, casos de aceite) e coluna **Tema** seguem o contrato de compilação § **3.4** — evolução do gerador, não bloqueio para redação de specs conforme § **9** em [`spec_conventions.md`](spec_conventions.md).

#### 3.1.1 Ordem de resolução de `rules` **(CONTEXT-09)**

Alinhada a [`spec_agents.md`](spec_agents.md) § **1.2** (**AGENTS-06**, **AGENTS-10**, **AGENTS-26**). O gerador **deve** aplicar **quatro passos**; dentro de cada passo, ordem **alfabética estável** por path relativo. Em cada passo **1–3**, um ID já presente em `rules` **pode ser sobrescrito** pelo passo seguinte; no passo **4**, só **acrescentar** IDs **ausentes**.

| Passo | Origem                                | Critério                                                                                                                                                                                                                                                                    |
| ----- | ------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **1** | `_dev/spec_*.md` **sync do catálogo** | Paths listados em `_dev/.specs-sync.yaml` (preferencial) ou `entries.*.downstream` do manifesto local — **exceto** `_dev/spec_conventions.md`. Ex.: `spec_agents.md`, `spec_commits.md`. **Não** incluir `spec_<nome-repo>.md` nem specs de domínio local (**AGENTS-26**). |
| **2** | Demais `_dev/spec_*.md`               | Arquivos `spec_*.md` em `_dev/` que **não** são sync do passo 1 — ex.: `spec_<nome-repo>.md`, `spec_<domínio>.md` local.                                                                                                                                                   |
| **3** | Contrato maduro                       | Arquivos `.md` em **`docs/specs/`** (preferencial) ou **`specs/`** (raiz), recursivamente — **não** limitado ao prefixo `spec_`. Sobrescreve passos 1–2 quando o mesmo ID existir.                                                                                         |
| **4** | Hub de convenções                     | `_dev/spec_conventions.md` § **2** — **apenas fallback**: acrescentar ID se ainda **não** estiver em `rules`.                                                                                                                                                               |

**Identificar sync (passo 1):** (a) chaves/paths em `_dev/.specs-sync.yaml`; (b) se ausente ou incompleto, `entries.*.downstream` do `manifest.yaml` do consumidor. **Não** inferir sync só pelo padrão de nome `spec_*.md`.

**Campo `sources`:** **deve** listar todos os arquivos lidos nos passos 1–4 (paths + papel), **gerados em runtime** — **não** lista fixa no código do gerador (**CONTEXT-07**).

### 3.2 Tarefas (`tasks`)

Entradas descrevem **fluxos SDD** recorrentes — ex.: preparar commit, sync de uma entrada, avaliar versão:

```yaml
tasks:
  - id: wrapup
    when: "End of implementation with tracked file changes — do not wait for operator to ask for commit"
    description: "Ordered wrapup: evaluate SemVer, edit version files and CHANGELOG when present, suggest git add + HEREDOC in chat — never execute Git (COMMITS-16)"
    steps:
      - "Evaluate SemVer (VERSION-01, AGENTS-24); apply bumps to manifest/pyproject/package when applicable"
      - "Update CHANGELOG.md (COMMITS-12) when the repo maintains one; when opening ## [X.Y.Z] - DATE apply (N) suffix per VERSION-17 / spec_version.md § 8.6 checklist if DATE already used"
      - "Suggest git add + HEREDOC commit message in chat (COMMITS-15, COMMITS-16, AGENTS-30) — do not wait for operator to ask"
    must_not:
      - "execute git add"
      - "execute git commit"
      - "execute git push"
    must:
      - "paste git add + HEREDOC in chat when implementation altered tracked files"
    rule_ids:
      - AGENTS-20
      - AGENTS-24
      - AGENTS-13
      - AGENTS-18
      - COMMITS-01
      - COMMITS-12
      - COMMITS-13
      - COMMITS-15
      - COMMITS-16
      - VERSION-01
      - VERSION-13
      - VERSION-14
      - VERSION-15
      - VERSION-16
      - VERSION-17
      - AGENTS-11
      - AGENTS-30
    artifacts:
      - CHANGELOG.md
      - manifest.yaml
      - pyproject.toml
      - package.json
      - _dev/_dev.md
    commit_command_shape: |
      git add <paths>
      git commit -m "$(cat <<'EOF'
      <type>(<scope>): <imperative title — cause>
      <See lines from _dev/_dev.md when present — COMMITS-06>
      <optional body>
      Impact: <user-visible effect — CHANGELOG bullet when applicable>
      EOF
      )"
  - id: commit
    description: "When operator explicitly asks for commit help — same flow as wrapup (COMMITS-16, AGENTS-17)"
    rule_ids:
      - AGENTS-10
      - AGENTS-11
      - AGENTS-17
      - AGENTS-20
      - COMMITS-01
      - COMMITS-04
      - COMMITS-05
      - COMMITS-12
      - COMMITS-15
      - COMMITS-16
    artifacts:
      - CHANGELOG.md
      - manifest.yaml
      - _dev/spec_commits.md
      - _dev/_dev.md
  - id: sync
    description: "Pull/push de entrada do manifest"
    rule_ids: [AGENTS-34, AGENTS-31]
    artifacts: [_dev/spec_agents.md]
```

Campos exatos por tarefa **podem** evoluir no gerador (`when`, `commit_command_shape`, …); consumidores **devem** ignorar chaves desconhecidas sem falhar.

### 3.3 Escopos de path (`path_scopes`)

Agrupam paths do repo relevantes ao SDD (sync, toolkit, contrato maduro) para orientar buscas e anexos `@` — **não** substituem inventários locais (ex.: tags Git em **`spec_<nome-repo>.md`** — **CONV-07**).

Evolução de esquema (**`schema_version` > 1**) **deve** ser documentada nesta spec e no CHANGELOG do catálogo antes de consumidores adotarem.

### 3.4 Contrato de extração semântica **(CONTEXT-10)**

Alinhado a [`spec_conventions.md`](spec_conventions.md) § **9.11** (**CONV-37**). O gerador `sdd context compile` **deve** evoluir para consumir, por ordem de preferência:

| Camada | Fonte na spec                                | Campo(s) em `rules` / artefato derivado                                     | Estado v1        |
| ------ | -------------------------------------------- | ---------------------------------------------------------------------------- | ---------------- |
| **1**  | Índice `\| ID \| Tema \| Seção \| Resumo \|` | `summary` ← **Resumo**; **Tema** em metadados opcionais                      | Parcial (4 col.) |
| **2**  | Âncoras `**(PREFIX-NN)**` no corpo           | Ligação ID ↔ chunk de corpo                                                  | Fora do gerador  |
| **3**  | Tabela **Metadados de compilação**           | `Camada`, `Gatilho`, `View`, `Artefatos`, `Requer` → grafos / `path_scopes` | Fora do gerador  |
| **4**  | Fence ` ```norma id=…`                       | Chunk autônomo para embeddings                                               | Reservado        |
| **5**  | Tabela casos de aceite                       | Entrada / resultado esperado                                                 | Reservado        |
| **6**  | Tabela mensagens canônicas                   | Código HTTP / texto pt-BR                                                    | Reservado        |

**Regras:**

- **Fonte canônica** de cada ID **deve** ser a spec temática que o define (**CONTEXT-09**) — **não** o hub § **2** de `spec_conventions.md`, salvo `CONV-*`.
- Coluna **Resumo** **deve** alimentar `rules.<ID>.summary` sem truncagem agressiva — rubrica **CONV-34**.
- Coluna **Tema** **deve** estar disponível para filtros RAG quando o parser adotar 4 colunas.
- Campo **`Requer`** nos metadados (§ **9.10** em `spec_conventions.md`) **deve** poder materializar arestas entre IDs no artefato compilado ou camada derivada.
- Consumidores **devem** regenerar `_dev/.sdd-context.yaml` após alteração de índices ou metadados (**CONTEXT-03**).

Implementação de referência: `computer-setup/toolkit/sdd/context_compile.py` — evoluir sem quebrar consumo de índices legados de **três colunas** em specs ainda não refactoradas.

---

## 4. Gerador **(CONTEXT-08)**

| Item               | Valor                                                          |
| ------------------ | -------------------------------------------------------------- |
| **Comando**        | `sdd context compile`                                          |
| **Implementação**  | `computer-setup/toolkit/sdd/context_compile.py`                |
| **Saída**          | `_dev/.sdd-context.yaml` (path relativo à raiz do consumidor)  |
| **Pré-requisitos** | Consumidor com `_dev/` e manifest; specs sync quando aplicável |

Detalhes operacionais (flags, dry-run, validação) **devem** ficar em `toolkit/sdd/specs/` no repositório `computer-setup` — **não** duplicados aqui salvo norma transversal nova (**CONV-04**).

---

## 5. Relação com o manifest do catálogo

| Chave manifest                       | Papel                                                           |
| ------------------------------------ | --------------------------------------------------------------- |
| `entries.context`                    | Sync de **`docs/spec_context.md`** → `_dev/spec_context.md`     |
| `areas.context`                      | SemVer da norma `spec_context.md` (independente do YAML gerado) |
| *(ausente para `.sdd-context.yaml`)* | Saída gerada — **fora** de `entries` (**CONTEXT-04**)           |

Ao publicar nova versão de `spec_context.md` no catálogo, consumidores sync **`context`** via `sdd context -pl` (ou alias documentado) e **devem** recompilar o artefato (**CONTEXT-03**).
