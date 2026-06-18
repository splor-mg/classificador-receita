# Orientações para desenvolvimento (SDD) assistidos por agentes de IA

Contrato de orquestração do desenvolvimento guiado por especificação do projeto assistido por IA. Destina-se a **desenvolvedores** e, em especial, a **assistentes de IA** (Cursor e IDEs similares) em repositórios que combinam normas do **catálogo** (`spec_agents`, `spec_commits`, …) com especificações **do projeto** (ver § **1. Pastas de especificação no projeto**).

## Objetivo

Definir **como trabalhar** neste projeto ao implementar, refatorar ou documentar: ordem de leitura,
idioma, commits, configuração, versionamento e tratamento de contradições com as specs.

Vale para quem edita diretamente (terminal, editor) e para quem usa assistente de IA — as mesmas
regras normativas; trechos específicos de IDE estão indicados nas specs referenciadas (ex. `spec_commits.md`).

**Não substitui** specs de domínio nem convenções locais — complementa com protocolo transversal.

## Referências

Os principais **conceitos**, **autores**, **metodologias** e **referências externas** que orientam a especificação de agentes neste catálogo são:

???+ note "SDD (Spec-Driven Development) assistido por IA"

    **Spec-Driven Development (SDD)** trata a especificação como artefato primário: o que o sistema deve fazer fica em `spec_*.md` **antes** ou **junto** do código, para que humano e assistente IA compartilhem a mesma fonte de verdade. Com assistentes de IA, isso reduz “adivinhação” do modelo e deriva entre intenção e implementação — alinhado a *spec-first*, *spec-anchored* e, em casos extremos, *spec-as-source*.

    Neste catálogo, o SDD **assistido por IA** significa: parâmetros iniciais em `_dev/spec_*.md`, contrato maduro do projeto em `docs/specs/` ou `specs/` (raiz), e este arquivo define **como** o agente deve ler e obedecer essas normas; o código permanece **rastreável** ao que as specs descrevem (ver § **1. Pastas de especificação no projeto**).

    **Referências externas**

    - [GitHub Spec Kit — spec-driven.md](https://github.com/github/spec-kit/blob/main/spec-driven.md) — manifesto e fluxo SDD com agentes (constituição, specify, plan, implement).
    - [Spec-Driven Development: From Code to Contract…](https://arxiv.org/abs/2602.00180) — guia prático (Deepak Babu Piskala); níveis spec-first / spec-anchored / spec-as-source.
    - [What is Spec-Driven Development?](https://www.ibm.com/think/topics/spec-driven-development) — visão geral e relação com TDD/BDD.
    - [Spec-Driven Development (specdriven.ai)](https://specdriven.ai/) — metodologia e papéis de spec, testes e constituição do projeto.

??? abstract "Engenharia de contexto"

    Assistentes não “leem o repositório inteiro”: trabalham com uma **janela de contexto** limitada. **Engenharia de contexto** é a disciplina de escolher *o quê* entra nessa janela (ordem de leitura, specs temáticas, regras, pendências, ferramentas) para maximizar sinal e minimizar perda de escopo. Este documento e as `spec_*.md` por domínio são o protocolo de contexto do projeto; regras de IDE (Cursor Rules, Skills) complementam, mas não substituem specs normativas.

    **Referências externas**

    - [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — Anthropic; evolução do prompt engineering; compactação, memória e tokens de alto sinal.
    - [Context engineering (LangChain)](https://github.com/langchain-ai/context_engineering) — estratégias *write / select / compress / isolate* para agentes.
    - [A Survey of Context Engineering for Large Language Models](https://arxiv.org/html/2507.13334) — taxonomia acadêmica do campo.
    - [Context-Driven Engineering](https://thanpol.as/engineering/context-driven-engineering) — Thanasis Polychronakis; contexto explícito no repositório, spec e plano antes da implementação.

??? info "Instruções para agentes (AGENTS.md e equivalentes)"

    O ecossistema convergiu para um arquivo **previsível** na raiz (ou em subpastas) com comandos de build/teste, estilo e limites — o [formato AGENTS.md](https://agents.md). **`spec_agents.md` não substitui** esse padrão: é a camada **normativa SDD** (idioma, ordem de leitura, commits, versionamento). Em projetos que usam ambos, `AGENTS.md` costuma ser operacional e curto; `spec_agents.md` e demais `spec_*.md` carregam o contrato de comportamento.

    **Referências externas**

    - [agents.md (formato aberto)](https://agents.md) — especificação e exemplos.
    - [repositório agentsmd/agents.md](https://github.com/agentsmd/agents.md) — referência de implementação do formato.
    - [AGENTS.md — giving agents project context](https://addyosmani.com/agents/15-agents-md/) — Addy Osmani; onboarding do agente e hierarquia em monorepos.

??? info "Desenvolvimento human-in-the-loop"

    O agente **propõe** patches, mensagens de commit e documentação; o **desenvolvedor** mantém autoridade sobre o que entra no Git (revisão, `git commit`, push). Padrões úteis: plano aprovado antes de execução ampla, unidades pequenas revisáveis, agente que auto-revisa e humano que valida antes do merge. Regras operacionais deste catálogo (não commitar sem pedido, modos sugestão vs agente) estão em [`spec_commits.md`](spec_commits.md).

    **Referências externas**

    - [Building effective agents](https://www.anthropic.com/research/building-effective-agents) — Anthropic; padrão *evaluator–optimizer* e loops com supervisão humana.
    - [The Intern Pattern (AI1)](https://prickles.org/tenet/the-intern-pattern/AI1) — plano → aprovação → execução → revisão antes de merge.
    - [pair-review](https://github.com/in-the-loop-labs/pair-review) — exemplo de ferramenta “IA sugere, humano decide” no fluxo local.

??? tip "Rastreabilidade no Git"

    Commits e versões ligam mudanças de código e de spec a **escopos** legíveis (`docs(sdd): …`, SemVer no catálogo). Isso permite auditoria, changelog e sincronização entre repositórios que puxam normas do catálogo compartilhado.

    **Normas neste catálogo (obrigatório antes de commit)**

    - [`spec_commits.md`](spec_commits.md) — Conventional Commits, escopo alinhado a `spec_*.md`, regras para assistentes de IA.
    - [`spec_version.md`](spec_version.md) — SemVer para evolução de specs e do manifesto; § **7** — comandos `git tag` para o operador.

    **Referências externas**

    - [Conventional Commits](https://www.conventionalcommits.org/) — especificação do formato de mensagens.
    - [Semantic Versioning 2.0.0](https://semver.org/) — MAJOR / MINOR / PATCH.

??? note "Linguagem normativa (RFC 2119)"

    Obrigações nas specs normativas do catálogo usam *deve* / *não deve* / *pode* alinhados ao [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) — definição canônica em [`spec_conventions.md`](spec_conventions.md) **Referências**.

??? note "Identificadores normativos (IDs)"

    Regras citadas em PR, commits ou outras specs podem levar um ID estável **`AGENTS-NN`** (prefixo deste arquivo). O número da seção (`§ 1.2`, etc.) organiza a leitura e **pode** mudar em reorganizações; o ID **não** deve ser reutilizado com outro sentido — marcar obsoleto e apontar substituto.

    Índice completo de IDs do catálogo: [`spec_conventions.md`](spec_conventions.md) § **2**; prefixos: § **1.2**.

??? quote "Normas e artefatos deste catálogo"

    Detalhes operacionais **não** se repetem aqui; vivem nas specs abaixo (sincronizadas para `_dev/` ou `specs/` no projeto a que se aplica).

    - [`spec_conventions.md`](spec_conventions.md) — layout, nomenclatura `spec_*.md` (§ **1.3**), orquestração de variáveis, prefixos de ID.
    - [`spec_commits.md`](spec_commits.md) — commits.
    - [`spec_issues.md`](spec_issues.md) — issues.
    - [`spec_version.md`](spec_version.md) — versionamento.
    - [`README.md`](README.md) — índice do catálogo em `docs/`.
    - No consumidor: **`spec_<nome-repo>.md`** (§ **1.3.2** — overrides SDD locais); entradas do **manifest** em `_dev/` (`spec_agents`, `spec_commits`, … — **não editar** para regras locais — **AGENTS-25**); **`spec_<domínio>.md`** locais (§ **1.3.3** — **não** são catálogo); `_dev/_dev.md`; `_dev/toDo.md`; `README.md` na raiz do projeto.

---

## Como citar este documento

| Mecanismo          | Uso                                                                                             |
| ------------------ | ----------------------------------------------------------------------------------------------- |
| **Seção numerada** | `§ 1.2` ou título `§ **1.2 Precedência**` — navegação no Markdown.                              |
| **ID normativo**   | `AGENTS-02` — citação estável (commit, contradição, outra spec).                                |
| **Prefixo**        | `AGENTS` — índice completo do catálogo em [`spec_conventions.md`](spec_conventions.md) § **2**. |

**Índice de IDs deste arquivo** (normas âncora; demais itens seguem só numeração de seção):

| ID        | Seção | Resumo                                                                                 |
| --------- | ----- | -------------------------------------------------------------------------------------- |
| AGENTS-01 | 1.1   | Catálogo em `_dev/` não substitui contrato maduro                                      |
| AGENTS-02 | 1.2   | Contrato em `docs/specs/` ou `specs/` prevalece                                        |
| AGENTS-03 | 1.2   | Overrides SDD só em `spec_<nome-repo>.md`; não editar entradas sync do manifest        |
| AGENTS-04 | 1.2   | Ordem de leitura conforme § **1.2** (domínio vs processo SDD)                          |
| AGENTS-05 | 1.2   | Assistente indica qual spec prevaleceu                                                 |
| AGENTS-06 | 1.3   | Registrar nomenclatura em `spec_conventions.md`                                        |
| AGENTS-07 | 2     | Respostas do assistente na IDE em inglês (salvo pedido)                                |
| AGENTS-08 | 2     | Código e comentários em inglês                                                         |
| AGENTS-09 | 4     | Não inventar regra de domínio sem base em spec/código                                  |
| AGENTS-10 | 5     | Ao pedido de commit: ler spec de commits em vigor antes de agir                        |
| AGENTS-11 | 5, 8  | Não executar `git commit`/`push` sem pedido explícito                                  |
| AGENTS-12 | 5     | Spec de commits prevalece sobre hábitos genéricos                                      |
| AGENTS-13 | 6     | Antes de concluir tarefa com alterações: avaliar `spec_version.md`                     |
| AGENTS-14 | 6.4   | Avaliar elevação ao catálogo ao alterar `_dev/spec_*.md`                               |
| AGENTS-15 | 7     | Não implementar silenciosamente trecho contraditório                                   |
| AGENTS-16 | 5     | Variável nova → inventário em `spec_conventions.md`                                    |
| AGENTS-17 | 10    | Protocolo `*_new.md` só em `_dev/` do catálogo sincronizado                            |
| AGENTS-18 | 10.3  | Não substituir local inteiro pelo `_new` sem pedido explícito                          |
| AGENTS-19 | 10.4  | Não publicar no catálogo canónico sem pedido explícito                                 |
| AGENTS-20 | 6     | Bump de versão: sugerir tag Git; inventário em `spec_<nome-repo>.md` (**CONV-07**)     |
| AGENTS-21 | 1.4   | Artefatos padrão sugeridos na raiz do projeto (README, CHANGELOG, …)                   |
| AGENTS-22 | 1.3   | Recomendado: `spec_<nome-repo>.md` para especificidades SDD do repo (secções por tema) |
| AGENTS-23 | 1.5   | Papéis distintos de cada `README.md` (raiz, `_dev/`, maduro)                           |
| AGENTS-24 | 8     | Toolkit CLI hierárquica: domínio + verbo; ver **CONV-26** e **CONV-28**                |
| AGENTS-25 | 1.2   | Overrides locais só em `spec_<nome-repo>.md`; prevalecem sobre catálogo sync           |
| AGENTS-26 | 1.3   | `spec_*.md` em `_dev/` fora do manifest = domínio local; não confundir com sync        |
| AGENTS-27 | 2     | Assistente orienta termos técnicos mais precisos quando o operador usar termos vagos   |

---

## 1. Pastas de especificação no projeto

### 1.1 Papel de cada pasta

**`_dev/spec_*.md` — rascunhos e parâmetros para construir o projeto**

Os arquivos `spec_*.md` em **`_dev/`** incluem três famílias (§ **1.3**): cópias **sync do catálogo** (só chaves do manifest), **`spec_<nome-repo>.md`** (overrides SDD) e **`spec_<domínio>.md` locais** (regras de negócio e domínio deste projeto — ex.: `spec_django`, `spec_itemClassificacao_navegacao`). Enquanto o contrato maduro não existe, servem para alinhar desenvolvedor e assistente no **como** trabalhar (SDD, commits, idioma) e no **o quê** do domínio.

**`docs/specs/` ou `specs/` — contrato maduro do projeto**

Quando as especificações **próprias do projeto** estiverem maduras, recomenda-se documentá-las em **`docs/specs/`** ou na pasta **`specs/`** na raiz do repositório (irmã de `_dev/`). Aí o projeto define **seu** padrão de nomenclatura e estrutura — os arquivos **não precisam** começar com `spec_` (podem ser `0001_api.md`, pastas por domínio, etc.). Esse é o destino do contrato que descreve comportamento, integrações e regras **exclusivas** do projeto.

O catálogo em `_dev/spec_*.md` **não substitui** esse conjunto: ele ajuda a **construir** o repositório; o objetivo final do SDD é o contrato documentado em `docs/specs/` ou `specs/`. **(AGENTS-01)**

### 1.2 Precedência (obrigatório) **(AGENTS-02**–**05**, **AGENTS-25**)

A pilha depende do **tipo** de norma em disputa.

#### 1.2.1 Domínio (comportamento, regras de negócio) **(AGENTS-02**, **AGENTS-26**)

| Prioridade | Onde                                                       | Regra                                                                                        |
| ---------- | ---------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| **1**      | **`docs/specs/`** ou **`specs/`** (raiz)                   | Contrato **maduro** prevalece. **(AGENTS-02)**                                               |
| **2**      | **`_dev/spec_<domínio>.md`** (local, **fora** do manifest) | Spec de domínio **deste** projeto — autorada no consumidor; **não** é cópia do catálogo.     |
| **3**      | **`_dev/spec_<nome-repo>.md`** § **Domínio** (se existir)  | Notas transversais de domínio no repo-spec; não substitui spec dedicada quando esta existir. |

O catálogo sync (**entradas do manifest**) **não** entra na pilha de domínio — `spec_agents`, `spec_commits`, etc. tratam de **processo SDD**, não de regras de negócio exclusivas.

#### 1.2.2 Processo SDD (commits, agents, issues, convenções, versionamento)

| Prioridade | Onde                                                            | Regra                                                                                                         |
| ---------- | --------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| **1**      | **`docs/specs/`** ou **`specs/`** (raiz)                        | Contrato maduro do tema, se existir. **(AGENTS-02)**                                                          |
| **2**      | **`_dev/spec_<nome-repo>.md`** (secção do tema, **se existir**) | Overrides **SDD** deste repositório. **(AGENTS-22**, **AGENTS-25)**                                           |
| **3**      | **`_dev/`** — entrada sync do **manifest**                      | Baseline compartilhada (`spec_agents`, `spec_commits`, …). **Não editar** para regras locais. **(AGENTS-25)** |
| **4**      | **`toolkit/<tool>/specs/`**                                     | Norma da ferramenta junto ao código.                                                                          |

**Como saber se um `_dev/spec_*.md` é sync do catálogo:** pela chave em `manifest.yaml` → `entries` (`downstream`, ex. `_dev/spec_commits.md`) ou metadado em `.specs-sync.yaml` no consumidor — **não** pelo padrão de nome sozinho. **`spec_django.md`**, **`spec_itemClassificacao_*.md`**, etc. são **locais** mesmo com prefixo `spec_`. **(AGENTS-26)**

Ordem prática de leitura **(AGENTS-04)** — adaptar à tarefa:

**Tarefa de domínio** (feature, regra de negócio, módulo):

1. Contrato maduro (`docs/specs/`, senão `specs/`).
2. **`_dev/spec_<domínio>.md`** relevante (spec local do projeto).
3. `spec_<nome-repo>.md` § **Domínio**, se existir e couber.
4. Código e testes afetados.

**Tarefa de processo SDD** (commit, sync do catálogo, idioma, layout transversal):

1. Contrato maduro do tema, se existir.
2. **`_dev/spec_<nome-repo>.md`** (secção do tema).
3. Entrada sync do manifest em `_dev/` (ex. `spec_commits.md`).
4. Specs de ferramenta afetadas.

O assistente **deve** indicar qual fonte prevaleceu e citar secção ou ID. **(AGENTS-05)**

**Regra de lacuna (processo SDD):** entradas sync do manifest **não** recebem adaptações locais permanentes. Quando surgir exceção de processo, registrar em **`spec_<nome-repo>.md`** (criar o arquivo se ainda não existir) ou no contrato maduro.

### 1.3 Padrões de nomenclatura (resumo)

Em **`_dev/`**, distinguir **três** famílias de `spec_*.md`:

| Família                 | Padrão / critério                                                     | Natureza                                                                      | Exemplos                                                                         |
| ----------------------- | --------------------------------------------------------------------- | ----------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| **Catálogo (manifest)** | `_dev/` + chave em `entries` (`downstream`)                           | Cópia sync do `specs-catalog` — **somente leitura** no consumidor             | `spec_agents`, `spec_commits`, `spec_issues`, `spec_conventions`, `spec_version` |
| **Repositório**         | `spec_<nome-repo>.md` (opcional)                                      | Especificidades **SDD** deste Git — criar quando houver overrides de processo | `spec_computer-setup`, `spec_classificador-receita`                              |
| **Domínio local**       | `spec_<domínio>.md` (qualquer outro `spec_*.md` **fora** do manifest) | Regras de **negócio** e rascunhos **deste** projeto — editáveis no consumidor | `spec_django`, `spec_itemClassificacao_navegacao`, `spec_importar`               |

#### 1.3.1 Família catálogo (entrada do manifest)

Chaves em `manifest.yaml` → `entries` (`agents`, `commits`, `issues`, `conventions`, `version`, `readme`). Sincronizadas para `_dev/` via `sdd … -pl`. Atualizar só pelo catálogo upstream ou pull — **não** gravar regras de negócio, idioma local, escopos ou exceções nestes arquivos. **(AGENTS-25)**

O nome `spec_<tema>.md` **não** implica sync: só as chaves listadas no manifest são catálogo.

#### 1.3.2 Spec do repositório **(AGENTS-22)**

**Recomenda-se** manter **`_dev/spec_<nome-repo>.md`** quando o projeto acumula **especificidades SDD** que diferem do catálogo — commits em PT-BR, escopos locais, convenções de equipe, etc. `<nome-repo>` é o identificador do repositório Git (ex.: stem do clone, `computer-setup`, `classificador-receita`).

- **Ausência não é falha:** se o consumidor segue a baseline do catálogo sem exceções de processo, o arquivo **pode não existir**.
- **Quando existir regra SDD local**, ela **deve** estar aqui (ou no contrato maduro), **não** em entradas sync do manifest editadas à mão (**AGENTS-25**).

- Registra regras que **diferem** do catálogo no **processo SDD** (commits, issues, agents, convenções de layout, versionamento local, …).
- **Inventário de tags Git** (**CONV-07**): subsecção em § **Convenções** ou § **Versionamento** — **nunca** em entrada sync `_dev/spec_conventions.md`.
- Organizar em **secções por tema**, alinhadas às chaves do `manifest.yaml` do catálogo:

```markdown
# Especificação local — <nome-repo>

## Agents
## Commits
## Issues
## Convenções
## Versionamento
## Domínio
```

- Secções **omitidas** quando vazias; criar secção ao registrar a primeira regra daquele tema.
- Em **contradição** com entrada sync do manifest no mesmo tema, **prevalece** este arquivo (**AGENTS-25**).
- **Não** entra em `entries` do manifesto do catálogo (ficheiro local do consumidor).
- **Exceção:** repositório canónico **`specs-catalog`** usa `_dev/spec_specs-catalog.md` como complemento de **mantenedor** (não é consumidor típico).

Ferramenta com pasta madura (`toolkit/<tool>/specs/`): norma de **comportamento** em `spec_<module>.md` junto ao código; notas transversais de processo ficam em `spec_<nome-repo>.md`; regras de **domínio** detalhadas em `spec_<domínio>.md` local (§ **1.3.3**) ou no contrato maduro.

#### 1.3.3 Spec de domínio local **(AGENTS-26)**

Qualquer `spec_*.md` em `_dev/` cuja chave **não** figure em `manifest.yaml` → `entries` é spec **de domínio deste projeto** — esperado e válido.

- Autorada e versionada **no consumidor**; **não** é espelho do `specs-catalog`.
- Descreve comportamento, integrações e regras de negócio (ex.: `spec_django.md`, `spec_itemClassificacao_formulario.md`).
- Destino natural ao amadurecer: promover para `docs/specs/` ou `specs/` (§ **1.1**).
- **Não** usar para overrides de commits/issues/agents — isso vai em `spec_<nome-repo>.md` (§ **1.3.2**).
- O assistente **não deve** tratar estas specs como candidatas a `sdd … -pl` nem ao protocolo `*_new.md` (§ **10**).

Em **`docs/specs/`** ou **`specs/`**, a nomenclatura é **do projeto**. Exemplos vistos na prática:

- **Numeração:** `0001_nome-spec.md`, `NNNN-<tema>.md` — ordem de leitura ou fases.
- **Temático:** `api.md`, `regras-negocio.md` — sem prefixo `spec_`.
- **Por subpasta:** `docs/specs/integracao/…`, `specs/backend/…`.
- **Ainda com `spec_`:** alguns projetos mantêm `spec_<tema>.md` também na pasta madura; o que importa é a **pasta**, não o prefixo obrigatório.

O projeto **deve** registrar o padrão adotado em **`spec_conventions.md`** (na pasta madura correspondente, quando existir). **(AGENTS-06)**

No repositório **deste catálogo** (upstream), as normas compartilhadas ficam em **`docs/`**; nos projetos que sincronizam, as **entradas do manifest** chegam a `_dev/` — as demais `spec_*.md` em `_dev/` são **locais** do consumidor.

### 1.4 Artefatos padrão sugeridos (raiz do projeto) **(AGENTS-21)**

Não são obrigatórios em todos os repositórios, mas **recomenda-se** adotá-los cedo em projetos de trabalho com SDD e versionamento:

| Artefato                          | Quando sugerir                                               | Papel                                                                                                                                            |
| --------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| **`README.md`**                   | Quase sempre                                                 | Visão geral, quick start, links para specs e ferramentas                                                                                         |
| **`CHANGELOG.md`**                | Projeto com releases ou `manifest.yaml` versionado           | Histórico humano ([Keep a Changelog](https://keepachangelog.com/)); Perfil B lockstep — § **8** (**VERSION-09**, **VERSION-15**, **VERSION-16**) |
| **`manifest.yaml`**               | Catálogo, monorepo com áreas, ou consumidor com `gtt -tg-cr` | Versão SemVer e metadados (branch, áreas); ver **VERSION-03**                                                                                    |
| **`_dev/`**                       | Consumidor do catálogo `specs-catalog`                       | Entradas sync do manifest + `spec_<nome-repo>.md` + specs de domínio locais + scaffold (`_dev.md`, `toDo.md`)                                    |
| **`docs/specs/`** ou **`specs/`** | Contrato maduro do domínio                                   | Normas exclusivas do projeto (§ **1.1**)                                                                                                         |

O assistente **pode** sugerir criar `README.md` ou `CHANGELOG.md` quando o repositório ainda não os tiver e o projeto já versiona ou publica tags — **não** criar silenciosamente sem pedido do desenvolvedor.

Projetos com CLI `gtt` para tags: alinhar `CHANGELOG.md`, `manifest.yaml` e tags remotas (`gtt -tg-list`); detalhe do protocolo de pré-release no consumidor (ex.: `toolkit/gtt/specs/spec_tags.md`).

### 1.5 Papéis dos `README.md` **(AGENTS-23)**

Vários `README.md` podem coexistir; cada um tem **papel distinto**. Não fundir conteúdos entre eles.

| Caminho                                             | Papel                                                                                                                    | Sync / origem                       |
| --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ | ----------------------------------- |
| **`README.md`** (raiz)                              | Aplicação ou repositório para humanos: quick start, instalação, links gerais                                             | Local do projeto                    |
| **`_dev/README.md`**                                | Índice do **catálogo SDD** sincronizado (`docs/README.md` upstream): mapeamento das normas `spec_*.md`, ordem de leitura | **`sdd … -pl`** (manifest `readme`) |
| **`_dev/spec_<nome-repo>.md`**                      | Especificidades SDD **deste** repo (§ **1.3.2**); opcional até haver overrides                                           | Local do consumidor                 |
| **`_dev/spec_<domínio>.md`** (fora do manifest)     | Spec de **domínio** local (§ **1.3.3**); rascunho até contrato maduro                                                    | Local do consumidor                 |
| **`docs/specs/README.md`** ou **`specs/README.md`** | Índice maduro do contrato de domínio                                                                                     | Contrato maduro                     |

O assistente **deve** sugerir criar ou completar `_dev/spec_<nome-repo>.md` quando detectar regra **SDD** local em entrada sync do manifest editada — **não** criar silenciosamente sem pedido do desenvolvedor. Specs de **domínio** novas vão em `spec_<domínio>.md` local ou no contrato maduro, conforme § **1.3.3**.

---

## 2. Idioma (obrigatório no projeto)

| Camada                                             | Idioma                  | Exemplos                                                                                     |
| -------------------------------------------------- | ----------------------- | -------------------------------------------------------------------------------------------- |
| Especificações em `_dev/spec_*.md`                 | **Português do Brasil** | Catálogo e rascunhos em `_dev/` — ex.: `spec_agents.md`                                      |
| Especificações em `docs/specs/` ou `specs/` (raiz) | **Conforme o projeto**  | Idioma definido no contrato maduro (ex. em `spec_conventions.md` ou README da pasta)         |
| Scripts                                            | **Inglês**              | Identificadores, funções, strings no código                                                  |
| Comentários em scripts                             | **Inglês**              | `#` em shell; docstrings em Python                                                           |
| Mensagens de **commit**                            | `spec_commits.md`       | Conforme a variante adotada no projeto (ex.: inglês ou PT-BR)                                |
| Respostas do **assistente de IA** na IDE           | **Inglês**              | Entrada do desenvolvedor em qualquer idioma (ex.: PT-BR); outro idioma de saída só se pedido |

**Regras:**

- O assistente **deve** aceitar prompts em português (ou outro idioma do desenvolvedor) e **deve** responder em **inglês**, salvo pedido explícito de outro idioma. **(AGENTS-07)**
- Código e comentários **devem** estar em **inglês**; não introduzir comentários em português em arquivos que já seguem inglês. **(AGENTS-08)**
- **`_dev/spec_*.md`:** português normativo; termos técnicos em inglês quando usual (`commit`, `pull request`).
- **`docs/specs/` ou `specs/` (raiz):** idioma **como definido para o projeto**; não assumir PT-BR se o projeto fixar outro idioma nas convenções.
- Mensagens de commit conforme `spec_commits.md` (na pasta em uso), seja commit manual ou sugerido pela IA.
- O assistente **deve** assumir que o operador conhece apenas conceitos básicos de programação, ciência de dados e tecnologia da informação. Quando o operador usar termo impreciso, informal ou diferente do termo usual na área, o assistente **deve** indicar o termo técnico mais preciso e mapear a intenção do operador para esse vocabulário, sem interromper o fluxo da tarefa nem corrigir de forma pedante. Se a imprecisão criar ambiguidade operacional, o assistente **deve** perguntar antes de implementar. **(AGENTS-27)**

Este arquivo está em português por ser spec; isso **não** autoriza código em português.

---

## 3. Commits (desenvolvedor e assistente de IA)

**Desenvolvedor:** antes de `git commit`, ler secção **Commits** em `_dev/spec_<nome-repo>.md` (se existir), depois [`spec_commits.md`](spec_commits.md); ler `_dev/_dev.md` para linhas `See` (quando existir).

**Assistente de IA:** quando o desenvolvedor mencionar **commit**, **git add**, **mensagem de commit**,
**o que commitar**, **push**, **staging** ou equivalentes, o assistente **deve** **(AGENTS-10)**:

1. Resolver norma de commits: **`spec_<nome-repo>.md` § Commits** (se existir) → [`spec_commits.md`](spec_commits.md) do catálogo → contrato maduro em `docs/specs/` ou `specs/` se houver.
2. Ler na íntegra a spec aplicável antes de responder.
3. Ler `_dev/_dev.md` para as linhas `See` (quando existir).
4. Seguir modo sugestão vs execução (§ **1** em `spec_commits.md`; **COMMITS-01**–**04**).

Em dúvida, a **spec de commits em vigor** (com precedência § **1.2**) prevalece sobre hábitos genéricos. **(AGENTS-12)**

O assistente **não deve** executar `git commit`, `git push` nem equivalentes sem pedido **explícito** do desenvolvedor. **(AGENTS-11)**

Regras locais de commit (idioma, escopos, exemplos) **devem** estar em **`spec_<nome-repo>.md`**, não em edições de `_dev/spec_commits.md`. **(AGENTS-25)**

---

## 4. Ordem de leitura antes de alterar código

1. `spec_agents.md` — § **1.2 Precedência** (**AGENTS-02**–**05**, **AGENTS-25**, **AGENTS-26**).
2. **`_dev/spec_<nome-repo>.md`** — secção do tema em curso (processo SDD).
3. Contrato **maduro do projeto**: **`docs/specs/`**, senão **`specs/`** (raiz).
4. **`_dev/spec_<domínio>.md`** — specs de domínio locais relevantes à tarefa (**AGENTS-26**).
5. `spec_conventions.md` — na mesma pasta do contrato maduro, se existir; senão em `_dev/`, § **4**.
6. Entradas sync do **manifest** em `_dev/` (baseline SDD; não editar para overrides locais).
7. `spec_version.md` — antes de concluir; obrigatório se alterou specs ou contrato normativo.
8. `_dev/toDo.md` — contexto e pendências (não normativo).
9. Par entrada sync + `*_new.md` — se o pedido for atualização do **catálogo**, aplicar § **10** (só entradas do manifest).
10. Scripts afetados (`toolkit/<tool>/`, `setup/`, `profile`, ou layout equivalente em `spec_conventions.md`) e README de instalação, se aplicável.

Não inventar regra de domínio sem base em spec ou código existente; em caso de dúvida, alinhar com quem solicitou a mudança. **(AGENTS-09)**

---

## 5. Configurações e variáveis

Antes de **introduzir ou criar** variável de ambiente, constante de URL/path, alias de shell
ou default hardcoded para um conceito já usado no projeto:

1. **Buscar** definições existentes no projeto e em `spec_conventions.md` (§ **4**; **CONV-02**), setup, `profile`, scripts em `toolkit/<tool>/` (ou equivalente), `config` ou semelhantes.
2. **Preferir referência** à definição já existente; **não** duplicar nome nem default.
3. Se um pedido nomear valor **já definido** noutro artefato, seguir o existente — salvo pedido explícito de mudar a fonte canônica.
4. Em **ambiguidade**, esclarecer antes de implementar (desenvolvedor decide; assistente pergunta).
5. Variável **nova** → registrar no inventário em `spec_conventions.md`. **(AGENTS-16)**

O inventário global de variáveis **deve** ficar em `spec_conventions.md` ou em arquivo maduro correspondente, não neste arquivo.

---

## 6. Versionamento

**Antes de concluir** qualquer tarefa que tenha alterado arquivos no repositório do projeto, observada a precedência em § **1.2**, o responsável **deve** **(AGENTS-13)**:

1. Ler `spec_version.md` e **avaliar** impacto (MAJOR / MINOR / PATCH) ou registrar «sem bump» — conforme aquele arquivo.
2. **Commits** neste repositório: mensagens conforme `spec_commits.md`.
3. Ao **promover** normas de `_dev/` para `specs/`, tratar como marco de estabilização; revisar versionamento e commits.
4. Se a tarefa **alterou** regras **SDD locais**, registrar em **`_dev/spec_<nome-repo>.md`**, **não** em entrada sync do manifest. Se alterou **domínio**, editar `spec_<domínio>.md` local ou contrato maduro. Se a mudança for **genérica** para todo o catálogo SDD, candidata a elevação upstream (`docs/`, `manifest.yaml`). **(AGENTS-14**, **AGENTS-25**, **AGENTS-26**)
5. Se a tarefa **alterou versão** publicável (`manifest.yaml`, `CHANGELOG.md`, …): ao concluir, **sugerir** comandos `git tag` conforme [`spec_version.md`](spec_version.md) § **7** (**VERSION-07**); **atualizar** o inventário de tags em **`_dev/spec_<nome-repo>.md`** (seção **Convenções** ou **Versionamento** — **CONV-07**; contrato maduro `docs/specs/` ou `specs/` quando existir). **Reconciliar** `CHANGELOG.md` com tags publicadas (**VERSION-09**, **VERSION-15**, **VERSION-16**; [`spec_commits.md`](spec_commits.md) § **3.4**). **Não** editar seções **publicadas** nem `_dev/spec_conventions.md` (sync). **Não** executar tag/push sem pedido explícito (**VERSION-08**; **AGENTS-11**). **(AGENTS-20)**

---

## 7. Protocolo de contradição

Se um pedido/implementação **contradizer** spec, convenção ou trecho normativo:

1. Aplicar § **1.2** (**AGENTS-02**–**04**).
2. **Não** implementar silenciosamente a parte contraditória. **(AGENTS-15)**
3. **Alertar** citando pedido vs spec (caminho, § ou ID, ex. `AGENTS-02`).
4. Decidir: priorizar o pedido (e atualizar a spec **na pasta protagonista**) ou seguir a spec vigente.

O assistente **deve** perguntar ao desenvolvedor.
O desenvolvedor **deve** registrar a decisão (commit ou nota na spec do contrato do projeto).

---

## 8. Implementação

Ao **implementar** mudanças neste repositório (código, configuração, documentação normativa), aplicar as cautelas abaixo. **O quê** implementar vem das specs temáticas; **onde** colocar arquivos e convenções de nomenclatura vêm de `spec_conventions.md` e do `README.md` deste projeto.

- **Layout e artefatos:** seguir pastas, prefixos e tipos de arquivo definidos neste repositório (`spec_conventions.md`, specs temáticas); não inventar estrutura paralela sem atualizar a convenção.
- **Estilo:** no arquivo ou módulo tocado, manter o padrão já usado (nomenclatura, organização, tratamento de erros).
- **Configuração e ambiente:** alterações pontuais e rastreáveis; evitar defaults duplicados (§ **5**; **AGENTS-16**).
- **Novas normas locais:** registrar em **`_dev/spec_<nome-repo>.md`** (§ **1.3.2**); norma **do catálogo** → upstream **`specs-catalog`**. Contrato maduro do domínio → `docs/specs/` ou `specs/`.
- **Specs existentes:** editar só trechos afetados; política transversal **local** → **`spec_<nome-repo>.md`** § **Convenções**; norma **global** → catálogo upstream (`docs/spec_conventions.md`).
- **Assistente de IA:** **(AGENTS-11)** — ver § **3**.
- **`CHANGELOG.md`:** quando existir, atualizar `[Unreleased]` **no mesmo commit** da implementação sem bump de `version:` (**COMMITS-12**); com bump de `version:` (Perfil B lockstep), abrir `## [nova-versão] - AAAA-MM-DD` no mesmo commit (**VERSION-15**) — **não** editar seções **publicadas** (**VERSION-16**). Se bump só em filhos sem propagar até `version:`, **alertar** (**VERSION-13**) e usar `[Unreleased]`. Reconciliar com tags remotas quando detectar desalinhamento.
- **Escopo da mudança:** diff mínimo alinhado ao pedido; scripts de instalação, bootstrap ou setup que afetam máquinas reais exigem cautela extra e aviso quando a mudança for invasiva.
- **Migrations:** ao deprecar layout, paths ou chaves que consumidores possam já ter, registar passos de **migration** conforme [`spec_conventions.md`](spec_conventions.md) § **8** (**CONV-19**–**CONV-24**).
- **CLI toolkit:** novas ferramentas ou refactors em `toolkit/<tool>/` com vários fluxos **devem** seguir gramática **domínio + verbo**, normalizers e help em camadas — [`spec_conventions.md`](spec_conventions.md) § **6.11** (**CONV-26**; **AGENTS-24**) e flags componíveis § **6.13** (**CONV-28**). Detalhe por ferramenta na spec do módulo no consumidor (`toolkit/<tool>/specs/`).
- **Idioma:** § **2** (**AGENTS-07**, **AGENTS-08**).

---

## 9. Saída esperada (tarefas não triviais)

Quando útil — em especial com assistente de IA — resumir:

- specs consideradas;
- suposições e lacunas;
- contradições (se houver), com § ou ID;
- se exige reexecutar setup/instalação do projeto ou só recarregar configuração de ambiente;
- avaliação de versionamento (impacto ou «sem bump»);
- se houve bump de versão: comandos `git tag` sugeridos (**VERSION-07**) e actualização do inventário em **`_dev/spec_<nome-repo>.md`** (secção **Convenções** ou **Versionamento** — **CONV-07**);
- integração conservadora ou análise reversa com par `*_new.md` em `_dev/`, se aplicável (§ **10**).

---

## 10. Sincronização em `_dev/` e arquivo `*_new.md` (protocolo conservador)

Este protocolo aplica-se **somente** a arquivos sob **`_dev/`** que são **entradas sync do catálogo** (mapeamento em `manifest.yaml` → `entries` / `downstream`). **Não** se estende a `spec_<domínio>.md` locais, `spec_<nome-repo>.md`, `docs/specs/`, `specs/` na raiz nem a outros caminhos — contrato maduro e domínio local seguem § **1**. **(AGENTS-17**, **AGENTS-26**)

Pode existir um **par** no mesmo diretório `_dev/`: o arquivo em uso (ex.: `_dev/spec_agents.md`) e um segundo arquivo com sufixo **`_new`** no nome (ex.: `_dev/spec_agents_new.md`), contendo a versão **do catálogo** num dado momento — em geral quando a atualização do catálogo remoto **não** substituiu a cópia local. Este documento define o **comportamento do assistente de IA** ao revisar, fundir ou elevar trechos entre os dois; **não** exige que o operador conheça a ferramenta de sync (menus, flags ou nomes de comando).

### 10.1 O que cada arquivo representa em `_dev/`

| Artefato                                               | Papel                                                                                                                                           |
| ------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `_dev/spec_<chave>.md` (sem `_new`; chave do manifest) | **Baseline do catálogo** neste consumidor — atualizar via sync; overrides SDD vão para `spec_<nome-repo>.md`.                                   |
| `_dev/spec_<chave>_new.md`                             | Referência do catálogo no momento do `[k]` — comparar; fundir regras **genéricas** no upstream ou deslocar exceções para `spec_<nome-repo>.md`. |

### 10.2 Quando aplicar este protocolo (gatilhos de pedido)

O assistente **deve** seguir § **10** quando o desenvolvedor pedir ajuda relacionada a **atualização de especificações**, **documentos de especificação**, **specs** (catálogo em `_dev/`), **sincronizar com o catálogo**, **incorporar o remoto**, **revisar o `_new`**, **merge do catálogo**, **diff entre local e catálogo**, ou linguagem equivalente — **e** existir o par local + `*_new.md` para a mesma chave (ou o assistente tiver acabado de identificar esse par em `_dev/`).

Se não houver `*_new.md`, o fluxo é o de sync normal (`specs <chave>`, `specs check`, `-df`, etc.) — não inventar sufixo `_new`.

### 10.3 Integração catálogo → local (fluxo principal)

Objetivo: incorporar atualizações **genéricas** do catálogo e mover exceções **locais** para **`spec_<nome-repo>.md`**.

1. Ler entrada sync (`spec_<chave>.md` do manifest), **`spec_<nome-repo>.md`** (secção do tema) e `*_new.md` se existir.
2. **Preservar** no **`spec_<nome-repo>.md`** regras que contradizem ou estendem o catálogo para este projeto.
3. **Atualizar** a entrada sync apenas via sync/pull com o upstream — não acrescentar regras locais permanentes. **(AGENTS-25)**
4. Do `*_new.md`, incorporar no upstream (elevação) o que for genérico; o que for só deste repo → `spec_<nome-repo>.md`.

### 10.4 Análise reversa (local → `*_new.md`, candidato ao remoto)

Quando o desenvolvedor pedir **análise reversa**, **elevar padrão ao catálogo**, **o que vale para a nuvem/remoto**, **promover trecho genérico ao catálogo canónico**, ou equivalente — **com** par local + `*_new.md` presente:

1. Partir de **`spec_<nome-repo>.md`** e de diffs na entrada sync do manifest como fonte das regras **SDD locais**.
2. Identificar trechos **genéricos** candidatos ao catálogo (**AGENTS-14**).
3. **Atualizar o `*_new.md`** com conteúdo genérico para revisão upstream.
4. **Manter em `spec_<nome-repo>.md`** o que for específico do projeto; **não** mover para o `_new`.
5. Deixar explícito na resposta: o `_new` passou a ser **proposta de publicação**, não cópia fiel do catálogo até o operador publicar; publicação real = `specs <chave> -ps` (ou edição direta no repo **`specs-catalog`**) + versionamento do manifest, com alinhamento de quem mantém o catálogo.
6. **Não** publicar nem fazer push no catálogo canónico sem pedido explícito. **(AGENTS-19)**

**Cautela:** o `*_new.md` nasce como snapshot do remoto; usá-lo também como rascunho de subida **mistura dois papéis**. Use § **10.4** só quando o operador pedir análise reversa; em dúvida, perguntar se o destino da elevação é o `_new` (revisão antes de `-ps`) ou edição direta no repositório **`specs-catalog`**.

### 10.5 Saída esperada (merge ou análise reversa)

- O que permaneceu só no local e por quê.
- O que entrou no local a partir do catálogo, ou o que entrou no `_new` como genérico elevável.
- Decisões em aberto (conflito de redação, bump de catálogo, necessidade de `-ps`).
- Lembrete de revisar `git status` antes de commit (evitar commitar `*_new.md` por engano se a intenção era só o local).

---

## 11. Manutenção

Ao mudar o processo de desenvolvimento neste projeto, atualizar a spec na pasta em uso (`_dev/`, `docs/specs/` ou `specs/`).
Alterações em **`_dev/spec_*.md`**: aplicar **AGENTS-14** (§ **6.4**).

Ao acrescentar norma citável neste arquivo, usar o próximo `AGENTS-NN` livre; atualizar o índice em § **Como citar** e § **2** em [`spec_conventions.md`](spec_conventions.md) (**CONV-04**).
