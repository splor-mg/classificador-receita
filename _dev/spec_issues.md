# Convenção de issues (GitHub)

Normas básicas de título e redação para issues em repositórios que adotam specs compartilhados. **Baseline do catálogo:** título e corpo em **inglês** (§ **3**). Overrides locais em `_dev/spec_<nome-repo>.md` § **Issues** — **AGENTS-22**, **AGENTS-25**.

## Objetivo

Issues registram **trabalho planejado** antes de PR e commit: contexto, escopo e rastreabilidade com o histórico Git.

Esta spec complementa [`spec_commits.md`](spec_commits.md) (execução) e [`spec_agents.md`](spec_agents.md) (SDD). **Não** substitui specs de ferramenta locais (ex.: formato YAML em `toolkit/gtt/specs/spec_issues.md`).

**Idioma deste arquivo:** português (instruções a quem desenvolve no projeto). **Idioma do título e corpo do issue:** inglês (§ **3**).

**Onde esta norma vale no projeto**

| Situação                                            | Arquivo                                                                              |
| --------------------------------------------------- | ------------------------------------------------------------------------------------ |
| Sync do catálogo (`sdd … -pl`)                      | `_dev/spec_issues.md` — cópia **read-only** deste documento                          |
| Overrides deste repositório                         | `_dev/spec_<nome-repo>.md` § **Issues** — prevalece sobre o catálogo (**AGENTS-25**) |
| Contrato maduro em `docs/specs/` ou `specs/` (raiz) | Regras de issue do projeto **prevalecem** sobre `_dev/`. **(ISSUES-06)**             |

Precedência: [`spec_agents.md`](spec_agents.md) § **1.2** (**AGENTS-02**–**05**, **AGENTS-25**).

## Referências

Os principais **conceitos** e **referências externas** que orientam **como redigir issues** neste catálogo são:

???+ note "GitHub Issues"

    Issues são o registro de trabalho no repositório: título visível na lista, corpo com contexto e critérios, labels/projects opcionais. Não há RFC ou PEP universal para títulos — adota-se convenção **local** alinhada ao que já existe no repo.

    **Referências externas**

    - [GitHub Docs — About issues](https://docs.github.com/en/issues/tracking-your-work-with-issues/about-issues) — visão geral.
    - [GitHub Docs — Using templates](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests) — templates e consistência.

??? abstract "Títulos legíveis"

    Título curto, **sentence case**, sem gritar em caixa alta. O padrão concreto do repositório (prefixo de escopo, epic, slug de arquivo) **deve** ser inferido de issues existentes — ver § **1** (**ISSUES-01**).

    **Referências externas**

    - [Best Practices for Using GitHub Issues](https://rewind.com/blog/best-practices-for-using-github-issues/) — labels e triagem (referência de equipe).

??? quote "Normas e artefatos deste catálogo"

    - [`spec_agents.md`](spec_agents.md) — SDD, precedência, assistente de IA.
    - [`spec_commits.md`](spec_commits.md) — linhas `See`, `Closes #N`, escopos de commit.
    - [`spec_conventions.md`](spec_conventions.md) — prefixos de ID, índice § **2**.
    - `_dev/spec_<nome-repo>.md` — overrides locais de issues (idioma, prefixos, exemplos).

??? note "Linguagem normativa e IDs"

    *Deve*/*não deve* conforme [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) — [`spec_conventions.md`](spec_conventions.md) **Referências**. IDs: prefixo **`ISSUES`**; índice completo em `spec_conventions.md` § **2**.

---

## Como citar este documento

| Mecanismo           | Uso                                                   |
| ------------------- | ----------------------------------------------------- |
| **Seção numerada**  | `§ 2.1` — navegação neste arquivo.                    |
| **ID normativo**    | `ISSUES-02` — citação estável.                        |
| **Índice completo** | [`spec_conventions.md`](spec_conventions.md) § **2**. |

**Índice de IDs deste arquivo:**

| ID        | Seção  | Resumo                                                              |
| --------- | ------ | ------------------------------------------------------------------- |
| ISSUES-01 | 1      | Antes de criar issue: ler padrão em `.github/issues/`               |
| ISSUES-02 | 2.1    | Título em sentence case (só primeira palavra com maiúscula inicial) |
| ISSUES-03 | 2.2    | Seguir prefixo temático do repo quando existir (ex. `(scope) - …`)  |
| ISSUES-04 | 2.1    | Não usar título inteiro em CAIXA ALTA                               |
| ISSUES-05 | 3      | Título e corpo do issue em **inglês**                               |
| ISSUES-06 | (obj.) | Contrato maduro de issues prevalece sobre cópia em `_dev/`          |
| ISSUES-07 | 1.2    | Nome de arquivo local alinhado ao padrão de `.github/issues/`       |
| ISSUES-08 | 4      | Referenciar issue no commit conforme `spec_commits.md`              |

---

## 1. Padrão do repositório (`.github/issues/`)

Antes de **criar** ou **sugerir** um issue, o autor **deve** consultar issues já registrados em **`.github/issues/`** (ou path equivalente definido no contrato maduro do projeto). **(ISSUES-01)**

### 1.1 O que observar

| Elemento              | Ação                                                                                            |
| --------------------- | ----------------------------------------------------------------------------------------------- |
| **Campo `title`**     | Formato de escopo, separadores e capitalização usados nos YAML/Markdown locais.                 |
| **Corpo (`body`)**    | Seções recorrentes (Description, Acceptance criteria, …).                                       |
| **Nome do arquivo**   | Padrão numérico e slug (ex.: `0016_profile-Refactor-….yml`) — manter coerência. **(ISSUES-07)** |
| **Labels / projects** | Reutilizar taxonomia existente; não inventar labels paralelas sem atualizar a convenção.        |

### 1.2 Exemplo (referência de forma, não de conteúdo)

Quando o repositório usa escopo entre parênteses:

```text
(profile) - Refactor file into modular components for better maintainability
```

- Escopo: `(profile)` — tema ou módulo.
- Separador: ` - ` (espaço, hífen, espaço).
- Descrição: **sentence case** — ver § **2.1**.

Se **nenhum** issue existir ainda em `.github/issues/`, registrar o padrão escolhido neste arquivo ou em spec madura do projeto antes de proliferar formatos divergentes.

---

## 2. Formato do título

### 2.1 Sentence case **(ISSUES-02**, **ISSUES-04)**

O título do issue **deve** usar **sentence case**: apenas a **primeira letra da primeira palavra** em maiúscula, salvo:

- nomes próprios e marcas (`GitHub`, `Windows`, …);
- siglas e acrónimos (`API`, `SDD`, `YAML`, …);
- identificadores técnicos que já vêm capitalizados no código.

**Não deve** escrever o título inteiro em CAIXA ALTA. Prefixos curtos acordados (`Epic:`) **podem** ter maiúscula inicial no rótulo; o resto do título permanece em sentence case.

| Evitar                      | Preferir                                            |
| --------------------------- | --------------------------------------------------- |
| `REFACTOR PROFILE FILE`     | `Refactor profile file into modular components`     |
| `(profile) - REFACTOR FILE` | `(profile) - Refactor file into modular components` |

### 2.2 Prefixo temático **(ISSUES-03)**

Quando `.github/issues/` já usa **escopo explícito**, novos issues **devem** seguir o mesmo esquema — em geral:

```text
(<escopo>) - <descrição em sentence case>
```

- `<escopo>`: módulo, ferramenta ou área (`profile`, `specs`, `gtt`, …) — minúsculas salvo nome próprio.
- **Epic** (opcional): se o projeto distinguir epics, usar prefixo acordado (`Epic: …` ou label `type::epic`) **sem** duplicar metadata no título e nas labels sem necessidade.

**Não** inventar outro separador (`:`, `/`, `[scope]`) se o repositório já padronizou `(scope) - …`.

---

## 3. Idioma do título e do corpo

| Parte                         | Idioma     |
| ----------------------------- | ---------- |
| **Título** do issue           | **Inglês** |
| **Corpo** (`body`)            | **Inglês** |
| Este arquivo `spec_issues.md` | Português  |

Título e corpo **devem** estar em **inglês** nesta baseline do catálogo, seja redação manual ou sugerida pelo assistente de IA (mesmo quando a conversa na IDE for em português). **(ISSUES-05)**

Para **outro idioma** ou convenções locais, documentar em `_dev/spec_<nome-repo>.md` § **Issues** — essa secção **prevalece** sobre este arquivo (**AGENTS-25**).

---

## 4. Ligação a commits **(ISSUES-08)**

Ao implementar trabalho rastreado por issue:

- Incluir referência no commit conforme [`spec_commits.md`](spec_commits.md) (linhas `See …`, `Closes #NN`, `Refs #NN`).
- Manter coerência entre escopo do issue (`(profile)`) e escopo do commit (`profile`), quando aplicável.

---

## 5. Assistente de IA

- **Sugerir** título e corpo alinhados a § **1**–**3**; **não** abrir issue no GitHub nem alterar `.github/issues/` sem pedido explícito do desenvolvedor (paralelo a **COMMITS-01** / **AGENTS-11**).
- Se existirem specs em **`docs/specs/`**, **`specs/`** (raiz) e **`_dev/`**, aplicar precedência em [`spec_agents.md`](spec_agents.md) § **1.2** antes de fixar formato.

---

## 6. Manutenção

Ao acrescentar norma citável neste arquivo: próximo `ISSUES-NN` livre; atualizar § **Como citar** e § **2** em [`spec_conventions.md`](spec_conventions.md) (**CONV-04**). Overrides locais: `spec_<nome-repo>.md` § **Issues**.

Alterações ao **modelo compartilhado** do catálogo: elevar ao repositório canônico (`docs/spec_issues.md` upstream) — **AGENTS-14**.
