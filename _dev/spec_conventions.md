# Convenções transversais do projeto

Modelo de registro para convenções organizacionais e orquestração de configuração em repositórios SDD. **Não substitui** specs temáticas (`spec_agents`, `spec_commits`, …) nem specs de domínio local — define layout transversal, prefixos, hub de IDs e modelo de documento normativo (§ **9**).

## Objetivo

Centralizar **convenções organizadoras** do projeto — pastas, nomenclatura (`spec_*`, `toolkit/<tool>/`, …),
configuração de ambiente (shell, Git, Python, editores) — sem duplicar comportamento funcional
de cada ferramenta.

Comportamento detalhado fica nas specs temáticas do projeto. **Onde** registrar convenções: normas **compartilháveis** no catálogo upstream (`docs/`) ou contrato maduro (`docs/specs/`, `specs/`); regras **só deste repo** em **`spec_<nome-repo>.md`** — ver [`spec_agents.md`](spec_agents.md) § **1. Pastas de especificação no projeto** (**AGENTS-06**–**11**). **Não** preencher entradas sync do manifest em `_dev/` (`spec_conventions.md`, …) com especificidades locais.

Ao introduzir tema transversal **compartilhável** novo, atualizar **`spec_conventions.md`** na pasta **protagonista**: **`docs/`** no repositório canônico **specs-catalog**; **`docs/specs/`** ou **`specs/`** (raiz) no consumidor com contrato maduro. Regras ou inventários **locais** → **`spec_<nome-repo>.md`** (seção correspondente).

## Referências

Os principais **conceitos**, **autores**, **metodologias** e **referências externas** que orientam **convenções transversais** e orquestração de configuração neste catálogo são:

???+ note "Convenções como contrato no repositório"

    **`spec_conventions.md`** centraliza o que é **transversal** (pastas, famílias de arquivos, variáveis compartilhadas, **prefixos e índice de IDs** do catálogo) sem repetir o comportamento detalhado de cada ferramenta — isso fica nas `spec_*.md` temáticas.

    **Referências externas**

    - [Context-Driven Engineering](https://thanpol.as/engineering/context-driven-engineering) — contexto explícito no repositório; README e specs como arquitetura.
    - [The Twelve-Factor App — Config](https://12factor.net/pt_br/config) — configuração no ambiente, não dispersa no código.

??? abstract "Documentação viva e DRY entre specs"

    Convenção **não** substitui spec funcional: registra *onde* e *como nomear*; a spec temática define *o que* o sistema faz. Ao criar artefato novo, atualizar inventário/tabela neste arquivo em vez de espalhar caminhos em várias specs.

    **Referências externas**

    - [Documentation as Code (Write the Docs)](https://www.writethedocs.org/guide/docs-as-code/) — docs versionadas junto ao código.
    - [Architecture Decision Records](https://adr.github.io/) — registrar decisões estruturais de forma rastreável (quando o projeto adotar ADRs).

??? note "Linguagem normativa (RFC 2119)"

    Obrigações nas specs normativas do catálogo usam termos em português alinhados ao [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) (ver também [BCP 14](https://www.rfc-editor.org/info/bcp14)):

    - **deve** ≈ MUST — exigência.
    - **não deve** ≈ MUST NOT — proibição.
    - **deve poder** ≈ SHOULD — recomendação forte.
    - **pode** ≈ MAY — opcional.

    Cada `spec_*.md` aplica *deve*/*não deve* nas normas âncora marcadas com ID (§ **2**).

??? note "Identificadores normativos (IDs)"

    Formato **`PREFIXO-NN`** (ex.: `AGENTS-06`). O **prefixo** identifica o arquivo de spec (§ **1.2**). O **número da seção** (`§ 4.1`) organiza a leitura e pode mudar; o **ID não** deve ser reutilizado com outro sentido.

    - **Índice só deste arquivo:** § **Como citar este documento** abaixo.
    - **Índice completo do catálogo:** § **2**.

??? tip "Orquestração de variáveis e configuração"

    Variáveis de ambiente, URLs, paths padrão e aliases de shell devem ter **definição canônica** em § **4** (**CONV-02**). Evita que scripts e a IA inventem o mesmo conceito com nomes diferentes.

    **Referências externas**

    - [12-Factor — Dev/prod parity & config](https://12factor.net/config) — uma configuração explícita por deploy.
    - [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — incluir no contexto só o necessário.

??? info "Nomenclatura, layout e pastas de specs"

    Padrões de nome (`spec_<domínio>`, `spec_<nome-repo>`, `0001_…`, `toolkit/<tool>/…`) variam por projeto. Em `_dev/`, **três famílias** ([`spec_agents.md`](spec_agents.md) § **1.3**): entrada **sync do manifest** (read-only); **`spec_<nome-repo>.md`** (overrides SDD — **AGENTS-03**, **AGENTS-10**); **`spec_<domínio>.md` local** (domínio do projeto — **AGENTS-04**). O prefixo `spec_` **não** implica catálogo. Papéis dos `README.md`: § **1.5** (**AGENTS-05**). Precedência: § **1.2** (**AGENTS-06**–**11**, **AGENTS-02**, **AGENTS-04**).

    **Referências externas**

    - [PEP 8](https://peps.python.org/pep-0008/) — Python, se adotado no projeto.
    - [Google Shell Style Guide](https://google.github.io/styleguide/shellguide.html) — shell, se aplicável.

??? quote "Normas e artefatos deste catálogo"

    - [`spec_agents.md`](spec_agents.md) — SDD, ordem de leitura, pastas, idioma.
    - [`spec_commits.md`](spec_commits.md) — commits (baseline EN; overrides em `spec_<nome-repo>.md`).
    - [`spec_version.md`](spec_version.md) — SemVer.
    - `_dev/toDo.md` — pendências (não normativo).
    - `README.md` na raiz do projeto de aplicação — visão geral.

## Como citar este documento

| Mecanismo           | Uso                                            |
| ------------------- | ---------------------------------------------- |
| **Seção numerada**  | `§ 4.1` — navegação neste arquivo.             |
| **ID normativo**    | `CONV-02` — citação estável.                   |
| **Índice completo** | § **2** — todos os IDs do catálogo em `docs/`. |
| **Prefixo**         | `CONV` — ver § **1.2**.                        |

**Índice de IDs normativos deste arquivo:**

| ID      | Tema         | Seção    | Resumo                                                                                                                                                                                            |
| ------- | ------------ | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CONV-01 | Registro     | 3        | Ao registrar convenção transversal neste arquivo ou equivalente, o autor **deve** incluir definição, onde vale, inventário e regra de manutenção conforme § **3**.                                |
| CONV-02 | Configuração | 4        | Variáveis de ambiente, paths e aliases compartilhados **devem** ter inventário canônico em § **4** deste arquivo; scripts e assistente **não devem** inventar defaults dispersos.                 |
| CONV-03 | Configuração | 4        | Antes de definir default para conceito já no inventário § **4**, o autor **deve** reutilizar nome e valor canônico — **não deve** duplicar.                                                       |
| CONV-04 | Hub          | 2        | Ao criar ou obsoletar ID em qualquer spec do catálogo, o mantenedor **deve** atualizar hub § **2** e o índice local **Como citar** da spec protagonista.                                          |
| CONV-05 | Manutenção   | 5        | Alterações ao modelo compartilhável do catálogo **devem** elevar-se ao upstream `docs/spec_conventions.md` — ver **AGENTS-26**; consumidor registra só exceções locais.                           |
| CONV-06 | Git          | 7.2      | Tags Git de release **devem** usar prefixo `v` + SemVer alinhado a `manifest.yaml` ou `CHANGELOG.md`; preferir tag anotada na branch estável.                                                     |
| CONV-07 | Git          | 7.3      | Inventário de tags Git **deve** residir em `spec_<nome-repo>.md` ou contrato maduro — **não deve** gravar-se em `_dev/spec_conventions.md` sync (**AGENTS-07**).                                  |
| CONV-08 | Shell        | 6.2      | Entry shell sourced **deve** seguir ordem fixa de blocos no `<tool>.sh`: bootstrap, runtime, normalizer, help, orchestrator — § **6.2**.                                                          |
| CONV-09 | Shell        | 6.1, 6.3 | Orchestrator público **deve** chamar-se `<tool>()` em scripts sourced — **não deve** usar `main()`; ver § **6.1** e § **6.3**.                                                                    |
| CONV-10 | Shell        | 6.4      | Helpers privados de entry shell **devem** usar prefixo `_<tool>_`; funções públicas em libs sourced usam `<tool>_` sem underscore inicial.                                                        |
| CONV-11 | Shell        | 6.5      | Arquivo `<tool>.sh` **deve** expor `_<tool>_normalize_action` mapeando aliases para tokens canônicos antes do dispatch.                                                                           |
| CONV-12 | Shell        | 6.5      | Aliases `help`, `-h` e `--help` **devem** normalizar para canônica `help`; dispatch **não deve** usar `-h` como token interno.                                                                    |
| CONV-13 | Shell        | 6.6      | Implementação de help **deve** residir em `_<tool>_show_help` no entry; texto longo fica na spec do tool.                                                                                         |
| CONV-14 | Shell        | 6.7      | Atalhos `<tool>-h` **devem** existir só no profile — **não devem** definir-se no entry shell sourced.                                                                                             |
| CONV-15 | Shell        | 6.8      | Scripts **devem** distinguir modo sourced (`<tool>()`) de executável (`main "$@"`) conforme § **6.8**.                                                                                            |
| CONV-16 | Shell        | 6.2      | Primeira linha de entry shell sourced **deve** ser `#!/usr/bin/env bash` — **não deve** usar `#!/bin/bash` salvo exceção documentada.                                                             |
| CONV-17 | Shell        | 6.9      | Entry `<tool>.sh` **deve** permanecer orquestrador enxuto; cada canônica do normalizer **deve** mapear a exatamente um delegate.                                                                  |
| CONV-18 | Toolkit      | 1.3      | Ferramentas em `toolkit/<tool>/` **devem** documentar-se em `spec_<tool>.md` (hub) e `spec_<stem>.md` (módulo) — § **1.3**.                                                                       |
| CONV-19 | Migration    | 8.1      | Migration neste catálogo designa passo one-shot idempotente de layout — **não** migration de base de dados; ver § **8.1**.                                                                        |
| CONV-20 | Migration    | 8.2      | Registar migration quando evolução depreca path, arquivo ou chave que consumidores **podem** já ter no ambiente.                                                                                  |
| CONV-21 | Migration    | 8.3      | Migrations **devem** correr antes do fluxo que assume layout atual; implementação em bloco dedicado sourced ou invocado cedo.                                                                     |
| CONV-22 | Migration    | 8.4      | Migrations **devem** ser idempotentes, detectar legado primeiro, confirmar ações destrutivas e falhar de forma segura ao cancelamento.                                                            |
| CONV-23 | Migration    | 8.5      | Cada ferramenta com migrations **deve** documentá-las no spec do módulo e referenciar no hub `spec_<tool>.md`.                                                                                    |
| CONV-24 | Migration    | 8.6      | Ao deprecar layout consumível, assistente **deve** registrar migration, documentar e avaliar SemVer — **não deve** assumir ambiente já atualizado.                                                |
| CONV-25 | CLI          | 6.10     | Prompts interativos de scripts `toolkit/<tool>/` **devem** estar em inglês — specs PT-BR **não** autorizam diálogos traduzidos no código.                                                         |
| CONV-26 | CLI          | 6.11     | CLI hierárquica **deve** adotar `<tool> [<domínio>] [<verbo>]` com normalizers de domínio e verbo documentados no hub da ferramenta.                                                              |
| CONV-27 | CLI          | 6.12     | Templates de prompt IA **devem** registrar-se no domínio canônico `prompt`/`prm` com registry Python — ver **AGENTS-29**.                                                                         |
| CONV-28 | CLI          | 6.13     | Flags booleanas componíveis **podem** acumular após o verbo; modos exclusivos **devem** documentar-se na spec do módulo.                                                                          |
| CONV-29 | Git          | 7.1      | Branches de trabalho **devem** usar `<tipo>/<slug>` em kebab-case; branch estável `main` **não deve** servir de prefixo operacional.                                                              |
| CONV-30 | CLI          | 6.14     | CLIs Python interativos **devem** sanitizar SIGINT: sem traceback, mensagem `Cancelled.`, exit **130**; aviso se alterações parciais possíveis.                                                   |
| CONV-31 | Toolkit      | 1.5      | Módulos Python reutilizados **devem** residir em `toolkit/<tool>/` de afinidade — **não devem** ficar soltos na raiz `toolkit/`.                                                                  |
| CONV-32 | Spec         | 9.1      | Toda spec normativa **deve** seguir esqueleto fixo em PT-BR; exemplos de output de terminal, prompts interativos e estruturas de diálogo citados na spec **devem** estar em inglês (**CONV-25**). |
| CONV-33 | Spec         | 9.2      | Índice local **deve** usar quatro colunas `ID                                                                                                                                                     | Tema | Seção | Resumo` mais **Índice por tema** imediatamente abaixo. |
| CONV-34 | Spec         | 9.4      | Coluna **Resumo** **deve** ser frase autônoma PT-BR (~25–55 palavras) com quem, modal, ação, contexto e dependências.                                                                             |
| CONV-35 | Spec         | 9.6      | Cada ID no índice **deve** ter âncora `**(PREFIX-NN)**` no corpo e cada norma citável **deve** ter linha no índice.                                                                               |
| CONV-36 | Spec         | 9.7      | Criar ID para obrigação RFC 2119, contrato ou mensagem fixa; **não** criar ID para exemplo, pendência ou ADR sem norma derivada.                                                                  |
| CONV-37 | Spec         | 9.11     | Specs **devem** adotar contrato de compilação em seis camadas (índice, âncoras, metadados, norma, aceite, mensagens) — **CONTEXT-10**.                                                            |
| CONV-38 | Spec         | 9.9      | Símbolos normativos compartilhados em ≥2 specs **devem** migrar para glossário `PREFIX-GL-NN` registrado no repo-spec.                                                                            |

**Índice por tema:**

| Tema         | IDs                                                                                      |
| ------------ | ---------------------------------------------------------------------------------------- |
| Registro     | CONV-01                                                                                  |
| Configuração | CONV-02, CONV-03                                                                         |
| Hub          | CONV-04                                                                                  |
| Manutenção   | CONV-05                                                                                  |
| Toolkit      | CONV-18, CONV-31                                                                         |
| Shell        | CONV-08, CONV-09, CONV-10, CONV-11, CONV-12, CONV-13, CONV-14, CONV-15, CONV-16, CONV-17 |
| CLI          | CONV-25, CONV-26, CONV-27, CONV-28, CONV-30                                              |
| Git          | CONV-06, CONV-07, CONV-29                                                                |
| Migration    | CONV-19, CONV-20, CONV-21, CONV-22, CONV-23, CONV-24                                     |
| Spec         | CONV-32, CONV-33, CONV-34, CONV-35, CONV-36, CONV-37, CONV-38                            |
---

## 1. Numeração e prefixos do catálogo

### 1.1 Regras gerais

- Seções normativas do catálogo usam **`## N. Título`** e, quando necessário, **`### N.M`** e listas numeradas.
- **Objetivo**, **Referências** e **Como citar este documento** ficam sem número de capítulo (metadados do arquivo).
- Cada spec tem **índice local** de IDs em **Como citar** (4 colunas — **CONV-33**); este arquivo mantém o **índice completo** em § **2**.
- **Modelo completo** para redigir ou revisar qualquer `spec_*.md`: § **9** (**CONV-32**–**38**). 

### 1.2 Prefixos por arquivo (catálogo `docs/`)

| Arquivo                                      | Prefixo ID | Escopo Conventional Commits (referência) |
| -------------------------------------------- | ---------- | ---------------------------------------- |
| [`spec_agents.md`](spec_agents.md)           | `AGENTS`   | `agents`                                 |
| [`spec_commits.md`](spec_commits.md)         | `COMMITS`  | `commits`                                |
| [`spec_issues.md`](spec_issues.md)           | `ISSUES`   | `issues`                                 |
| [`spec_conventions.md`](spec_conventions.md) | `CONV`     | `conventions`                            |
| [`spec_version.md`](spec_version.md)         | `VERSION`  | `version`                                |
| [`spec_context.md`](spec_context.md)         | `CONTEXT`  | `context`                                |

Specs **do domínio** no contrato maduro (`docs/specs/`, `specs/`): acrescentar linhas nesta tabela ao adotar IDs.

### 1.3 Specs por ferramenta (`toolkit/<tool>/specs/`) **(CONV-18)**

Ferramentas CLI em `toolkit/<tool>/` **devem** documentar comportamento em `toolkit/<tool>/specs/`:

| Papel      | Arquivo          | Conteúdo                                                                                                     |
| ---------- | ---------------- | ------------------------------------------------------------------------------------------------------------ |
| **Hub**    | `spec_<tool>.md` | Entry (`<tool>.sh`), normalização, tabela **canônica → delegate**, índice de módulos, variáveis transversais |
| **Módulo** | `spec_<stem>.md` | Comportamento do script `<stem>.py` ou `<stem>.sh` (`<stem>` = basename sem extensão)                        |

**Regra geral:** um `spec_<stem>.md` **por arquivo de implementação substantivo** — salvo exceções abaixo.

**Exceções** (não exigem spec dedicada):

- `README.md` na pasta da ferramenta (índice operacional curto).
- Arquivo trivial (orientação: &lt; ~30 linhas, sem comportamento normativo próprio).
- Re-export ou shim que só encaminha para outro módulo já especificado.
- Artefatos gerados ou só de teste.

**Sem duplicar norma:** o hub referencia módulos (`Detalhes: spec_sync.md`); cada spec de módulo referencia o hub para CLI, aliases e dispatch. Comportamento detalhado fica no módulo; orquestração fica no hub.

**Harmonização com CONV-17:** cada canônica do normalizer → um delegate no hub → implementação no módulo correspondente (`sync.py`, `nav.sh`, …).

**Referência:** `computer-setup/toolkit/gtt/specs/` (`spec_gtt.md` + `spec_nav.md`, `spec_issues_sync.md`, …); `toolkit/sdd/specs/`.

### 1.4 Manifesto multinível

Repositórios com `manifest.yaml` que declaram `version:`, `areas.*` e opcionalmente grupos filhos versionados (`toolkit.*`, …) **devem** manter consistência SemVer entre níveis — ver [`spec_version.md`](spec_version.md) § **9** (**VERSION-10**, **VERSION-11**, **VERSION-12**, **VERSION-13**).

| Regra          | Resumo                                                                                    |
| -------------- | ----------------------------------------------------------------------------------------- |
| **VERSION-10** | Núcleo de `version:` ≥ núcleo de qualquer outro campo versionado no manifesto             |
| **VERSION-11** | Núcleo de cada entrada em grupo filho ≤ núcleo de `areas.<nome>` homônimo                 |
| **VERSION-12** | Seção YAML do grupo filho **deve** ter o mesmo nome que a chave do agregador em `areas.*` |
| **VERSION-13** | Todo bump em filho propaga PATCH/MINOR/MAJOR na cadeia até `version:`                     |

| Repositório                            | `areas.*`                                                                                                     |
| -------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| **`specs-catalog`**                    | Uma chave por entrada do manifesto (`readme`, `agents`, `commits`, …) — alinhada a `entries` / `commit_scope` |
| **Consumidor** (ex.: `computer-setup`) | Áreas do repo (`setup`, `toolkit`, `utils`) + opcional grupo filho `toolkit.<tool>` (seção `toolkit:`)        |

Exemplos de layout: `specs-catalog/manifest.yaml`, `computer-setup/manifest.yaml`. O assistente **deve** verificar **VERSION-10** e **VERSION-13** ao sugerir bumps ou `git tag`; **VERSION-11** / **VERSION-12** quando existir grupo filho versionado.

### 1.5 Módulos Python compartilhados entre ferramentas **(CONV-31)**

Quando um script ou módulo Python é **reutilizado por várias ferramentas** em `toolkit/<tool>/`, **não deve** ficar como arquivo irmão das pastas das ferramentas (ex.: `toolkit/<module>.py` ao lado de `toolkit/gtt/`, `toolkit/sdd/`).

| Regra              | Detalhe                                                                                                                                   |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **Localização**    | **Deve** residir em `toolkit/<tool>/` da ferramenta com **maior afinidade** semântica com o módulo                                        |
| **Proibido**       | Arquivos de implementação substantivos soltos na raiz `toolkit/` (agregador das pastas `<tool>/`)                                         |
| **Import**         | Consumidores: `from <tool>.<module> import …` com `toolkit/` no `sys.path` (ou delegate equivalente documentado no hub da pasta anfitriã) |
| **Documentação**   | Referenciar no hub `spec_<tool>.md` da pasta anfitriã; spec de módulo dedicada se o arquivo tiver comportamento normativo (**CONV-18**)   |
| **Afinidade vaga** | No consumidor `computer-setup`, protocolo transversal pessoal do mantenedor → `toolkit/clh/` (CarLos Henrique — abreviação **clh**)       |

**Exemplo:** sanitização de SIGINT (**CONV-30**) → `toolkit/clh/cli_interrupt.py`, importado por várias ferramentas via `from clh.cli_interrupt import …`.

---

## 2. Índice completo de IDs normativos (catálogo) **(CONV-04)**

Lista **canônica** de IDs em vigor no catálogo upstream (`docs/`). Ao adicionar ou obsoletar um ID, atualizar **esta tabela** e o índice em **Como citar** do arquivo correspondente. **(CONV-04)**

**Papel vs compilação:** este § **2** é **hub** para navegação humana, grep e manutenção **CONV-04**. O gerador `sdd context compile` **não** deve usar este arquivo como `source` canônico de `AGENTS-*`, `COMMITS-*`, etc. — ver [`spec_context.md`](spec_context.md) § **3.1.1** (**CONTEXT-09**); passo 4 só preenche IDs em falta.

### `AGENTS` — [`spec_agents.md`](spec_agents.md)

| ID        | Tema          | Seção          | Resumo                                                                                                                                                                                                                                                                                                                                                                                                   |
| --------- | ------------- | -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| AGENTS-01 | Pastas        | 1.1            | Cópias sync em `_dev/` servem para bootstrap SDD; o contrato maduro do domínio **deve** residir em `docs/specs/` ou `specs/` na raiz — **não** substituem esse destino.                                                                                                                                                                                                                                  |
| AGENTS-02 | Pastas        | 1.3            | O projeto **deve** registrar padrão de nomenclatura do contrato maduro em `docs/specs/spec_conventions.md`, `specs/spec_conventions.md` ou `spec_<nome-repo>.md` § **Convenções**.                                                                                                                                                                                                                       |
| AGENTS-03 | Pastas        | 1.3.2          | Quando o consumidor acumula exceções SDD, **recomenda-se** `spec_<nome-repo>.md` com seções por tema alinhadas às chaves do manifest.                                                                                                                                                                                                                                                                    |
| AGENTS-04 | Pastas        | 1.3.3          | `spec_*.md` em `_dev/` fora do manifest é domínio local; sync **deve** identificar-se pela chave em `manifest.yaml`, **não** pelo nome do arquivo.                                                                                                                                                                                                                                                       |
| AGENTS-05 | Pastas        | 1.5            | Cada `README.md` (raiz, `_dev/`, maduro) tem papel distinto; o assistente **não deve** fundir conteúdos entre eles.                                                                                                                                                                                                                                                                                      |
| AGENTS-06 | Precedência   | 1.2            | Contrato maduro em `docs/specs/` ou `specs/` prevalece sobre cópias sync do catálogo no mesmo tema — domínio ou processo SDD.                                                                                                                                                                                                                                                                            |
| AGENTS-07 | Precedência   | 1.2            | Overrides SDD locais **devem** ficar só em `spec_<nome-repo>.md`; **não deve** gravar exceções permanentes em entradas sync (`_dev/spec_agents.md`, etc.).                                                                                                                                                                                                                                               |
| AGENTS-08 | Precedência   | 1.2            | O assistente **deve** seguir ordem de leitura § **1.2** conforme a tarefa — pilha de domínio (§ **1.2.1**) ou processo SDD (§ **1.2.2**).                                                                                                                                                                                                                                                                |
| AGENTS-09 | Precedência   | 1.2            | Após aplicar precedência, o assistente **deve** indicar qual fonte prevaleceu — caminho, § ou ID normativo.                                                                                                                                                                                                                                                                                              |
| AGENTS-10 | Precedência   | 1.2, 1.3, 3, 6 | Overrides de processo SDD **devem** residir em `spec_<nome-repo>.md` e prevalecem sobre entradas sync do manifest no mesmo tema.                                                                                                                                                                                                                                                                         |
| AGENTS-11 | Precedência   | 1.2            | Exceções permanentes de processo SDD **não devem** ir em entradas sync; registrar em `spec_<nome-repo>.md` ou contrato maduro.                                                                                                                                                                                                                                                                           |
| AGENTS-12 | Artefatos     | 1.4            | Em projetos SDD versionados, **recomenda-se** cedo README, CHANGELOG, `manifest.yaml`, `_dev/` e contrato maduro — **sem** impor em todos os repos.                                                                                                                                                                                                                                                      |
| AGENTS-13 | Artefatos     | 1.4, 1.5       | O assistente **não deve** criar nem completar silenciosamente `README.md`, `CHANGELOG.md` ou `spec_<nome-repo>.md` sem pedido explícito.                                                                                                                                                                                                                                                                 |
| AGENTS-14 | Idioma        | 2              | Respostas do assistente na IDE **devem** estar em inglês; aceita prompts em qualquer idioma salvo pedido explícito de outra língua de saída.                                                                                                                                                                                                                                                             |
| AGENTS-15 | Idioma        | 2              | Código e comentários **devem** estar em inglês; **não deve** introduzir comentários em português em arquivos que já seguem inglês.                                                                                                                                                                                                                                                                       |
| AGENTS-16 | Idioma        | 2              | O assistente **deve** mapear termos vagos do operador para vocabulário técnico preciso; perguntar antes de implementar se a imprecisão for ambígua.                                                                                                                                                                                                                                                      |
| AGENTS-17 | Commits       | 3, 5           | Em pedido sobre commit, staging ou push, o assistente **deve** ler na íntegra a spec de commits em vigor (com precedência § **1.2**) antes de responder.                                                                                                                                                                                                                                                 |
| AGENTS-18 | Commits       | 3, 5, 8        | O assistente **nunca deve** executar `git add`, `git commit`, `git push` nem equivalentes sem pedido **explícito** do desenvolvedor.                                                                                                                                                                                                                                                                     |
| AGENTS-19 | Commits       | 3, 5           | A spec de commits em vigor (com precedência § **1.2**) **deve** prevalecer sobre hábitos genéricos de Conventional Commits.                                                                                                                                                                                                                                                                              |
| AGENTS-20 | Commits       | 3, 3.1, 8      | Ao concluir implementação com arquivos alterados, o assistente **deve** aplicar o protocolo wrapup § **3.1** — **sem** executar Git (**AGENTS-18**).                                                                                                                                                                                                                                                     |
| AGENTS-21 | Leitura       | 4              | O assistente **não deve** inventar regra de domínio sem base em spec ou código; em dúvida, alinhar com quem solicitou a mudança.                                                                                                                                                                                                                                                                         |
| AGENTS-22 | Leitura       | 4.1            | O assistente **deve** trabalhar com contexto visível; materializar `rules`/`tasks` por leitura de ferramenta quando o índice compilado resolve o path — **não** exigir `@` ao operador; reler quando o escopo mudar; citar ID normativo ao aplicar regra.                                                                                                                                                |
| AGENTS-23 | Configuração  | 5              | Variável ou default novo **deve** ir para inventário em contrato maduro ou `spec_<nome-repo>.md` § **Convenções** — **não** em `_dev/spec_conventions.md` sync.                                                                                                                                                                                                                                          |
| AGENTS-24 | Versionamento | 3, 6, 8        | Antes de concluir tarefa com alterações no repo, o responsável **deve** ler `spec_version.md` e avaliar impacto SemVer ou registrar «sem bump».                                                                                                                                                                                                                                                          |
| AGENTS-25 | Versionamento | 6              | Com bump publicável, o assistente **deve** sugerir `git tag` (**VERSION-07**), atualizar inventário em `spec_<nome-repo>.md` (**CONV-07**) e reconciliar `CHANGELOG.md`.                                                                                                                                                                                                                                 |
| AGENTS-26 | Versionamento | 6.4            | Ao alterar `_dev/spec_*.md`, o assistente **deve** avaliar se trechos são genéricos e candidatos a elevação upstream (`specs-catalog`).                                                                                                                                                                                                                                                                  |
| AGENTS-27 | Contradição   | 7              | Se pedido ou patch contradiz spec vigente, o assistente **não deve** implementar silenciosamente; **deve** alertar e perguntar ao desenvolvedor.                                                                                                                                                                                                                                                         |
| AGENTS-28 | Contradição   | 7              | Em contradição resolvida, o desenvolvedor **deve** registrar a decisão em commit ou nota na spec protagonista do contrato.                                                                                                                                                                                                                                                                               |
| AGENTS-29 | Implementação | 8              | CLI em `toolkit/<tool>/` **deve** seguir gramática domínio + verbo, help em camadas (**CONV-26**) e flags componíveis (**CONV-28**).                                                                                                                                                                                                                                                                     |
| AGENTS-30 | Saída         | 9              | Em tarefas não triviais, o assistente **deve** resumir specs, lacunas, decisão de versionamento (arquivos bumpados ou «sem bump»), edições em `CHANGELOG`/`manifest`, e **sugerir** `git add` + HEREDOC no chat (**não** executar Git — **COMMITS-16**).                                                                                                                                                 |
| AGENTS-31 | Sync          | 10             | Protocolo `*_new.md` aplica-se **só** a entradas sync do manifest em `_dev/` — **não** a specs de domínio local nem contrato maduro.                                                                                                                                                                                                                                                                     |
| AGENTS-32 | Sync          | 10.3           | O assistente **não deve** substituir a entrada sync local inteira pelo conteúdo de `*_new.md` sem pedido explícito do operador.                                                                                                                                                                                                                                                                          |
| AGENTS-33 | Sync          | 10.4           | O assistente **não deve** publicar nem fazer push no repositório canônico `specs-catalog` sem pedido explícito.                                                                                                                                                                                                                                                                                          |
| AGENTS-34 | Sync          | 10.2           | O assistente **deve** seguir protocolo § **10** quando o pedido envolver sync/merge de specs do catálogo e existir par entrada sync + `*_new.md`.                                                                                                                                                                                                                                                        |
| AGENTS-35 | Postura       | 12.1           | Quando abordagem ou pedido comprometer objetivo verificável, qualidade sustentável ou spec vigente, o assistente **deve** discordar de forma construtiva e propor alternativa — **não** concordar por complacência (**AGENTS-27** quando houver contradição normativa explícita).                                                                                                                        |
| AGENTS-36 | Postura       | 12.2           | Em tarefas **não triviais**, o assistente **deve** planejar, decompor em etapas (**mids**) e **registrar** o plano em `_dev/.epic/.epic-NN_<slug>.md` (template `templates/epic/epic_template.md`, contrato `templates/epic/epic_spec.md`); **deve** manter `_dev/.epic/.epic_index.md` alinhado; **não deve** patch superficial nem implementar sem plano escrito quando `_dev/.epic/` existir no repo. |
| AGENTS-37 | Postura       | 12.3           | Com pedido vago ou raso, o assistente **deve** estruturar com specs, ordem de leitura § **4** e metodologia do projeto antes de codar; **não deve** transformar input fraco em plano fraco por complacência (**AGENTS-16**, **AGENTS-21**).                                                                                                                                                              |
| AGENTS-38 | Postura       | 12.4           | O assistente **deve** agir como par técnico sênior: sinalizar riscos, lacunas de spec e escopo excessivo; **deve** recusar ou delimitar pedidos destrutivos ou que violem normas citáveis — sem ser assistente passivo (**AGENTS-18**, **AGENTS-27**).                                                                                                                                                   |


### `CONTEXT` — [`spec_context.md`](spec_context.md)

| ID         | Tema       | Seção | Resumo                                                                                                                                                                                                                    |
| ---------- | ---------- | ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CONTEXT-01 | Artefato   | 1.1   | O contexto SDD compilado **deve** residir em `_dev/.sdd-context.yaml` na raiz do consumidor — **não** substituir por pasta `.sdd/` ou outro layout sem norma explícita no contrato maduro.                                |
| CONTEXT-02 | Artefato   | 1.2   | Operador e assistente **não devem** editar `_dev/.sdd-context.yaml` à mão; alterações normativas vão para specs fonte e o artefato **deve** ser regenerado com `sdd context compile`.                                     |
| CONTEXT-03 | Artefato   | 1.3   | O consumidor **deve** executar `sdd context compile` após sync de specs, bump de `areas.*`, alteração de overrides locais ou primeira adopção desta norma.                                                                |
| CONTEXT-04 | Artefato   | 1.4   | `_dev/.sdd-context.yaml` **deve** ser versionado no Git do consumidor; commit com escopo `context` quando o diff principal for só o artefato — **não** adicionar entrada `entries.*` no manifest.                         |
| CONTEXT-05 | Assistente | 2     | O artefato compilado complementa **AGENTS-22** — operador **pode** anexar `@`; assistente **deve** usar `rules`/`tasks` como índice e **não deve** dispensar leitura integral de specs quando exigida.                    |
| CONTEXT-06 | Esquema    | 3     | O gerador **deve** emitir YAML com `schema_version: 1`; evolução para versões superiores **deve** ser documentada nesta spec antes de consumidores adotarem.                                                              |
| CONTEXT-07 | Esquema    | 3     | Campos top-level v1 **obrigatórios**: `schema_version`, `generated_at`, `generator`, `repo`, `catalog`, `consumer`, `sources`, `rules`, `tasks`, `path_scopes` — lista `sources` **gerada** em runtime.                   |
| CONTEXT-08 | Gerador    | 4     | Comando canônico **`sdd context compile`** — implementação em `computer-setup/toolkit/sdd/context_compile.py`; detalhes operacionais ficam em `toolkit/sdd/specs/`, **não** duplicados aqui salvo norma transversal nova. |
| CONTEXT-09 | Compilação | 3.1.1 | Resolução de `rules` em quatro passos (sync → local `_dev/` → contrato maduro → hub § **2** só fallback); ID já presente **pode** ser sobrescrito pelo passo seguinte; passo 4 só acrescenta ausentes.                    |
| CONTEXT-10 | Compilação | 3.4   | Alvo de extração semântica: índice 4 colunas + camadas 2–6 do contrato § **9.11** (**CONV-37**); coluna **Resumo** alimenta `rules.<ID>.summary`; **Tema** disponível para filtros RAG.                                   |


### `COMMITS` — [`spec_commits.md`](spec_commits.md)

| ID         | Tema        | Seção    | Resumo                                                                                                                                                                                                                         |
| ---------- | ----------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| COMMITS-01 | Modo IA     | 1        | Modo **sugestão** é o padrão: o assistente **não deve** executar `git add`, `git commit` nem `git push` sem autorização explícita do desenvolvedor.                                                                            |
| COMMITS-02 | Modo IA     | 1.1      | Pedidos genéricos sobre commit («ajuda com commit», «o que commitar») **devem** ativar só o protocolo de sugestão § **8** — **não** autorizam execução real.                                                                   |
| COMMITS-03 | Modo IA     | 1.2      | Execução real de Git só após pedido **explícito** do operador, com confirmação clicável de proposta e inclusão opcional de `git push`.                                                                                         |
| COMMITS-04 | Modo IA     | 1.3      | Após entregar sugestões de staging/mensagem, o assistente **deve** encerrar com opções clicáveis A/B/C — manual, commit sem push, ou commit com push.                                                                          |
| COMMITS-05 | Idioma      | 3        | Título e corpo do commit **devem** estar em **inglês** nesta baseline; overrides de idioma só em `_dev/spec_<nome-repo>.md` § **Commits** (**AGENTS-10**).                                                                     |
| COMMITS-06 | Mensagem    | 3.2      | Linhas `See …` **devem** ser copiadas só de `_dev/_dev.md` quando existirem — o assistente **não deve** inventar URLs ou placeholders.                                                                                         |
| COMMITS-07 | Tipo        | 3.8      | Diff **apenas** de documentação normativa (`spec_*.md`, README descritivo) **deve** usar tipo `docs` — **não** `feat` por ser «feature conceptual».                                                                            |
| COMMITS-08 | Staging     | 7        | O assistente **não deve** sugerir `git add` de credenciais (`.env`, chaves privadas, tokens) nem arquivos sensíveis equivalentes.                                                                                              |
| COMMITS-09 | Staging     | 7        | O assistente **não deve** executar `dev-td-up` (commit+push automáticos) sem pedido **explícito** do operador.                                                                                                                 |
| COMMITS-10 | Precedência | (obj.)   | Contrato maduro de commits em `docs/specs/` ou `specs/` (raiz) **deve** prevalecer sobre cópia sync `_dev/spec_commits.md` — **AGENTS-06**, § **1.2**.                                                                         |
| COMMITS-11 | Mensagem    | 3.3      | No corpo do commit, **deve** preferir descrever comportamento aplicado — **não** citar IDs transitórios de `_dev/spec_*` salvo quando o commit altera a própria regra.                                                         |
| COMMITS-12 | Changelog   | 3.4      | Com `CHANGELOG.md`, o commit de implementação **deve** atualizar `[Unreleased]` no mesmo commit; Perfil B lockstep fecha `## [versão]` no bump de `version:` (**VERSION-15**, **VERSION-16**).                                 |
| COMMITS-13 | Mensagem    | 3.5      | Commits user-facing com `CHANGELOG.md` **devem** separar **causa** (título/corpo) de **impacto** via trailer `Impact:` em inglês — candidato a bullet KAC.                                                                     |
| COMMITS-14 | Changelog   | 3.6, 3.7 | Trailers `Changelog-*` só quando tipo CC + `Impact:` + heurísticas de diff **não** bastam; preferir inferir seção KAC antes de trailers explícitos.                                                                            |
| COMMITS-15 | Staging     | 7, 8     | Sugestões de commit **devem** usar HEREDOC integral; incluir `Impact:` quando aplicável (**COMMITS-13**) e bloco `See` só conforme **COMMITS-06**.                                                                             |
| COMMITS-16 | Modo IA     | 8.0      | Ao concluir implementação com alterações rastreáveis, o assistente **deve** seguir § **8.0** (versionamento + changelog + **sugerir** `git add` + HEREDOC no chat) — **não** **executar** Git (**AGENTS-20**, **COMMITS-01**). |


### `ISSUES` — [`spec_issues.md`](spec_issues.md)

| ID        | Tema        | Seção  | Resumo                                                                                                                                                                                              |
| --------- | ----------- | ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ISSUES-01 | Repositório | 1      | Antes de criar ou sugerir issue, o autor **deve** consultar padrão existente em `.github/issues/` (ou path equivalente no contrato maduro) — título, corpo, nome de arquivo e labels.               |
| ISSUES-02 | Título      | 2.1    | O título do issue **deve** usar **sentence case** — só a primeira palavra com maiúscula inicial, salvo nomes próprios, siglas e identificadores técnicos já capitalizados.                          |
| ISSUES-03 | Título      | 2.2    | Quando o repositório já usa escopo explícito, novos issues **devem** seguir o mesmo esquema — em geral `(<escopo>) - <descrição em sentence case>` — **não** inventar separador divergente.         |
| ISSUES-04 | Título      | 2.1    | O autor **não deve** escrever o título inteiro em CAIXA ALTA; prefixos curtos acordados (`Epic:`) **podem** ter maiúscula no rótulo.                                                                |
| ISSUES-05 | Idioma      | 3      | Título e corpo do issue **devem** estar em **inglês** nesta baseline do catálogo — inclusive sugestões do assistente de IA; outro idioma só via `_dev/spec_<nome-repo>.md` § **Issues**.            |
| ISSUES-06 | Precedência | (obj.) | Contrato maduro de issues em `docs/specs/` ou `specs/` (raiz) **deve** prevalecer sobre cópia sync em `_dev/spec_issues.md` — ver **AGENTS-06** e § **1.2** em `spec_agents.md`.                    |
| ISSUES-07 | Repositório | 1.2    | Nome de arquivo de issue local **deve** manter coerência com padrão numérico e slug já usado em `.github/issues/` — **não** proliferar formatos divergentes.                                        |
| ISSUES-08 | Commits     | 4      | Ao implementar trabalho rastreado por issue, o commit **deve** referenciar o issue conforme [`spec_commits.md`](spec_commits.md) (`See`, `Closes #N`, `Refs #N`) e alinhar escopo quando aplicável. |


### `CONV` — este arquivo

| ID      | Tema         | Seção    | Resumo                                                                                                                                                                                            |
| ------- | ------------ | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CONV-01 | Registro     | 3        | Ao registrar convenção transversal neste arquivo ou equivalente, o autor **deve** incluir definição, onde vale, inventário e regra de manutenção conforme § **3**.                                |
| CONV-02 | Configuração | 4        | Variáveis de ambiente, paths e aliases compartilhados **devem** ter inventário canônico em § **4** deste arquivo; scripts e assistente **não devem** inventar defaults dispersos.                 |
| CONV-03 | Configuração | 4        | Antes de definir default para conceito já no inventário § **4**, o autor **deve** reutilizar nome e valor canônico — **não deve** duplicar.                                                       |
| CONV-04 | Hub          | 2        | Ao criar ou obsoletar ID em qualquer spec do catálogo, o mantenedor **deve** atualizar hub § **2** e o índice local **Como citar** da spec protagonista.                                          |
| CONV-05 | Manutenção   | 5        | Alterações ao modelo compartilhável do catálogo **devem** elevar-se ao upstream `docs/spec_conventions.md` — ver **AGENTS-26**; consumidor registra só exceções locais.                           |
| CONV-06 | Git          | 7.2      | Tags Git de release **devem** usar prefixo `v` + SemVer alinhado a `manifest.yaml` ou `CHANGELOG.md`; preferir tag anotada na branch estável.                                                     |
| CONV-07 | Git          | 7.3      | Inventário de tags Git **deve** residir em `spec_<nome-repo>.md` ou contrato maduro — **não deve** gravar-se em `_dev/spec_conventions.md` sync (**AGENTS-07**).                                  |
| CONV-08 | Shell        | 6.2      | Entry shell sourced **deve** seguir ordem fixa de blocos no `<tool>.sh`: bootstrap, runtime, normalizer, help, orchestrator — § **6.2**.                                                          |
| CONV-09 | Shell        | 6.1, 6.3 | Orchestrator público **deve** chamar-se `<tool>()` em scripts sourced — **não deve** usar `main()`; ver § **6.1** e § **6.3**.                                                                    |
| CONV-10 | Shell        | 6.4      | Helpers privados de entry shell **devem** usar prefixo `_<tool>_`; funções públicas em libs sourced usam `<tool>_` sem underscore inicial.                                                        |
| CONV-11 | Shell        | 6.5      | Arquivo `<tool>.sh` **deve** expor `_<tool>_normalize_action` mapeando aliases para tokens canônicos antes do dispatch.                                                                           |
| CONV-12 | Shell        | 6.5      | Aliases `help`, `-h` e `--help` **devem** normalizar para canônica `help`; dispatch **não deve** usar `-h` como token interno.                                                                    |
| CONV-13 | Shell        | 6.6      | Implementação de help **deve** residir em `_<tool>_show_help` no entry; texto longo fica na spec do tool.                                                                                         |
| CONV-14 | Shell        | 6.7      | Atalhos `<tool>-h` **devem** existir só no profile — **não devem** definir-se no entry shell sourced.                                                                                             |
| CONV-15 | Shell        | 6.8      | Scripts **devem** distinguir modo sourced (`<tool>()`) de executável (`main "$@"`) conforme § **6.8**.                                                                                            |
| CONV-16 | Shell        | 6.2      | Primeira linha de entry shell sourced **deve** ser `#!/usr/bin/env bash` — **não deve** usar `#!/bin/bash` salvo exceção documentada.                                                             |
| CONV-17 | Shell        | 6.9      | Entry `<tool>.sh` **deve** permanecer orquestrador enxuto; cada canônica do normalizer **deve** mapear a exatamente um delegate.                                                                  |
| CONV-18 | Toolkit      | 1.3      | Ferramentas em `toolkit/<tool>/` **devem** documentar-se em `spec_<tool>.md` (hub) e `spec_<stem>.md` (módulo) — § **1.3**.                                                                       |
| CONV-19 | Migration    | 8.1      | Migration neste catálogo designa passo one-shot idempotente de layout — **não** migration de base de dados; ver § **8.1**.                                                                        |
| CONV-20 | Migration    | 8.2      | Registar migration quando evolução depreca path, arquivo ou chave que consumidores **podem** já ter no ambiente.                                                                                  |
| CONV-21 | Migration    | 8.3      | Migrations **devem** correr antes do fluxo que assume layout atual; implementação em bloco dedicado sourced ou invocado cedo.                                                                     |
| CONV-22 | Migration    | 8.4      | Migrations **devem** ser idempotentes, detectar legado primeiro, confirmar ações destrutivas e falhar de forma segura ao cancelamento.                                                            |
| CONV-23 | Migration    | 8.5      | Cada ferramenta com migrations **deve** documentá-las no spec do módulo e referenciar no hub `spec_<tool>.md`.                                                                                    |
| CONV-24 | Migration    | 8.6      | Ao deprecar layout consumível, assistente **deve** registrar migration, documentar e avaliar SemVer — **não deve** assumir ambiente já atualizado.                                                |
| CONV-25 | CLI          | 6.10     | Prompts interativos de scripts `toolkit/<tool>/` **devem** estar em inglês — specs PT-BR **não** autorizam diálogos traduzidos no código.                                                         |
| CONV-26 | CLI          | 6.11     | CLI hierárquica **deve** adotar `<tool> [<domínio>] [<verbo>]` com normalizers de domínio e verbo documentados no hub da ferramenta.                                                              |
| CONV-27 | CLI          | 6.12     | Templates de prompt IA **devem** registrar-se no domínio canônico `prompt`/`prm` com registry Python — ver **AGENTS-29**.                                                                         |
| CONV-28 | CLI          | 6.13     | Flags booleanas componíveis **podem** acumular após o verbo; modos exclusivos **devem** documentar-se na spec do módulo.                                                                          |
| CONV-29 | Git          | 7.1      | Branches de trabalho **devem** usar `<tipo>/<slug>` em kebab-case; branch estável `main` **não deve** servir de prefixo operacional.                                                              |
| CONV-30 | CLI          | 6.14     | CLIs Python interativos **devem** sanitizar SIGINT: sem traceback, mensagem `Cancelled.`, exit **130**; aviso se alterações parciais possíveis.                                                   |
| CONV-31 | Toolkit      | 1.5      | Módulos Python reutilizados **devem** residir em `toolkit/<tool>/` de afinidade — **não devem** ficar soltos na raiz `toolkit/`.                                                                  |
| CONV-32 | Spec         | 9.1      | Toda spec normativa **deve** seguir esqueleto fixo em PT-BR; exemplos de output de terminal, prompts interativos e estruturas de diálogo citados na spec **devem** estar em inglês (**CONV-25**). |
| CONV-33 | Spec         | 9.2      | Índice local **deve** usar quatro colunas `ID                                                                                                                                                     | Tema | Seção | Resumo` mais **Índice por tema** imediatamente abaixo. |
| CONV-34 | Spec         | 9.4      | Coluna **Resumo** **deve** ser frase autônoma PT-BR (~25–55 palavras) com quem, modal, ação, contexto e dependências.                                                                             |
| CONV-35 | Spec         | 9.6      | Cada ID no índice **deve** ter âncora `**(PREFIX-NN)**` no corpo e cada norma citável **deve** ter linha no índice.                                                                               |
| CONV-36 | Spec         | 9.7      | Criar ID para obrigação RFC 2119, contrato ou mensagem fixa; **não** criar ID para exemplo, pendência ou ADR sem norma derivada.                                                                  |
| CONV-37 | Spec         | 9.11     | Specs **devem** adotar contrato de compilação em seis camadas (índice, âncoras, metadados, norma, aceite, mensagens) — **CONTEXT-10**.                                                            |
| CONV-38 | Spec         | 9.9      | Símbolos normativos compartilhados em ≥2 specs **devem** migrar para glossário `PREFIX-GL-NN` registrado no repo-spec.                                                                            |


### `VERSION` — [`spec_version.md`](spec_version.md)

| ID         | Tema        | Seção | Resumo                                                                                                                                                                                                                                                       |
| ---------- | ----------- | ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| VERSION-01 | Avaliação   | 4     | Antes de concluir tarefa com alterações no repo, o responsável **deve** avaliar SemVer ou «sem bump» **e aplicar** bumps em arquivos de versionamento e `CHANGELOG` quando existirem (**AGENTS-20**).                                                        |
| VERSION-02 | Avaliação   | 3     | Classificação SemVer **deve** seguir tabela § **3**: MAJOR = incompatível; MINOR = extensão compatível; PATCH = correção sem mudar obrigação.                                                                                                                |
| VERSION-03 | Manifesto   | 1     | Catálogo **deve** declarar `version:` primário e rastreio secundário `areas.<entry>` no `manifest.yaml` — **não** versionar cada `spec_*.md` isoladamente.                                                                                                   |
| VERSION-04 | Avaliação   | 4     | Ao decidir qual spec foi alterada, **deve** aplicar precedência § **1.2** em `spec_agents.md` antes de classificar bump.                                                                                                                                     |
| VERSION-05 | Avaliação   | 4     | Alteração em `_dev/spec_*.md` **deve** distinguir regra local do consumidor vs padrão elevável upstream — ver **AGENTS-26**.                                                                                                                                 |
| VERSION-06 | Avaliação   | 4     | Promoção de norma de `_dev/` para contrato maduro (`docs/specs/` ou `specs/`) **deve** trigger revisão de versionamento e commits.                                                                                                                           |
| VERSION-07 | Tags        | 7     | Com bump publicável, o assistente **deve** sugerir comandos `git tag` copiáveis ao operador — **não** executar tag/push (**VERSION-08**, **AGENTS-18**).                                                                                                     |
| VERSION-08 | Tags        | 7     | O assistente **não deve** executar `git tag`, `git push origin vX.Y.Z` nem `git push --tags` sem pedido **explícito** do operador.                                                                                                                           |
| VERSION-09 | Changelog   | 8     | Projetos com `CHANGELOG.md` **devem** manter `[Unreleased]` alinhado a tags, pré-releases e estado do manifesto.                                                                                                                                             |
| VERSION-10 | Manifesto   | 9     | Núcleo de `version:` **não deve** ser menor que o núcleo de qualquer outro campo SemVer no mesmo manifesto.                                                                                                                                                  |
| VERSION-11 | Manifesto   | 9.3   | Núcleo de entrada em grupo filho (ex. `toolkit.gtt`) **não deve** exceder núcleo de `areas.<nome>` homônimo.                                                                                                                                                 |
| VERSION-12 | Manifesto   | 9.6   | Seção YAML de grupo filho versionado **deve** ter o mesmo nome que a chave do agregador pai em `areas.*`.                                                                                                                                                    |
| VERSION-13 | Manifesto   | 9.7   | Todo bump declarado num campo versionado **deve** propagar PATCH/MINOR/MAJOR na cadeia ascendente até `version:` na mesma tarefa.                                                                                                                            |
| VERSION-14 | Changelog   | 8.6   | `CHANGELOG.md` **deve** seguir Keep a Changelog: eixos versão × tipo; bullets de impacto perceptível; omitir tipos vazios.                                                                                                                                   |
| VERSION-15 | Changelog   | 8.7   | Perfil B lockstep (adotado): fechar `## [X.Y.Z] - data` no **mesmo commit** do bump de `version:` — **não** só após tag.                                                                                                                                     |
| VERSION-16 | Changelog   | 8.8   | Seções `## [X.Y.Z]` cuja tag `vX.Y.Z` existe no remoto são **imutáveis** — bullets novos vão para `[Unreleased]` ou nova versão.                                                                                                                             |
| VERSION-17 | Changelog   | 8.6   | Ao criar `## [X.Y.Z] - DATA`, se outra seção já usa a mesma `DATA`, o cabeçalho **deve** incluir sufixo `(N)` — ver checklist § **8.6** (**VERSION-17**).                                                                                                    |
| VERSION-18 | Pré-release | 8.2.1 | Em branch de trabalho com sufixo pré-release, após fixar núcleo SemVer vs última tag estável em `main`, entregas intermediárias **devem** incrementar só o sufixo (`-beta.N`, `-rc.N`) — **não** PATCH/MINOR/MAJOR adicionais em `version:` na mesma branch. |


---

## 3. Como registrar uma convenção **(CONV-01)**

Em **`spec_conventions.md`** (upstream **`docs/`** no catálogo; **`docs/specs/`**, **`specs/`** (raiz) ou **`spec_<nome-repo>.md`** § **Convenções** no consumidor — **nunca** a cópia sync **`_dev/spec_conventions.md`**), cada convenção transversal **deve** cumprir **(CONV-01)**:

1. **Definição** — o que o padrão cobre e o que fica de fora (uma frase + critérios).
2. **Onde vale** — pasta ou grupo de arquivos (ex.: `toolkit/gtt/specs/`, `apps/core/code_*.py`).
3. **Tabela espelho** (quando houver contrato + código) — artefato ↔ módulo ↔ campos.
4. **Inventário** — lista atual de membros da família (atualizar ao criar ou renomear).
5. **Regra de manutenção** — «ao acrescentar X, criar Y e linha na tabela/inventário»; specs funcionais só citam **caminhos** ou **IDs**.

---

## 4. Orquestração de configuração e variáveis **(CONV-02**–**03)**

**Registre aqui** as definições canônicas de variáveis de ambiente, paths padrão, URLs e aliases de shell que vários scripts compartilham. **(CONV-02)**

**Quem altera o projeto:** [`spec_agents.md`](spec_agents.md) § **5** (**AGENTS-23**).

Antes de definir default para conceito já inventariado, **deve** usar o valor do inventário — **não** duplicar nome nem default. **(CONV-03)**

### 4.1 O que preencher

| Campo                    | Conteúdo                                                                                                              |
| ------------------------ | --------------------------------------------------------------------------------------------------------------------- |
| **Fonte(s) canônica(s)** | Arquivo(s) orquestrador(es) (ex.: `profile`, `general-setup.sh`) — única fonte de verdade para exports compartilhados |
| **Inventário**           | Tabela `Variável` · `Significado` · `Usado em` (scripts, specs) — manter atualizada                                   |
| **Regra de manutenção**  | «Ao criar script que precise de X, usar `VAR` do inventário; não definir default duplicado»                           |

### 4.2 Inventário (exemplo — substituir)

| Variável      | Significado   | Usado em      |
| ------------- | ------------- | ------------- |
| *(preencher)* | *(preencher)* | *(preencher)* |

### 4.3 Artefatos orquestradores (exemplo — substituir)

| Artefato           | Papel                                                            |
| ------------------ | ---------------------------------------------------------------- |
| *(ex.: `profile`)* | *(ex.: exports de shell carregados no login; variáveis `*_PRF`)* |

---

## 5. Manutenção **(CONV-05)**

Alterações **só deste projeto** (consumidor): registrar em **`_dev/spec_<nome-repo>.md`** (seção correspondente — **AGENTS-03**, **AGENTS-10**) e/ou em contrato maduro `docs/specs/` ou `specs/` (`spec_conventions.md` ou arquivo equivalente). **Não** editar entradas sync do manifest em `_dev/` (`spec_conventions.md`, `spec_commits.md`, …). Commitar conforme a norma de commits em vigor.

Alterações ao **modelo compartilhado** do catálogo: elevar ao repositório canônico (`docs/spec_conventions.md` upstream) — **(CONV-05)** / **AGENTS-26**.

Ao acrescentar norma citável neste arquivo: próximo `CONV-NN` livre; atualizar § **2** e o índice em **Como citar**. Specs novas ou revisões **devem** seguir § **9** (**CONV-32**–**38**).

---

## 6. Entry point shell (`toolkit/<tool>/<tool>.sh`) **(CONV-08**–**CONV-15)**

Norma para scripts **sourced** pelo profile que expõem CLI de ferramenta (`gtt`, `sdd`, …). Comportamento funcional permanece em `spec_<tool>.md` do projeto consumidor — equivalente semântico a `def main():` em Python CLI.

Referência: [Google Shell Style Guide](https://google.github.io/styleguide/shellguide.html).

### 6.1 Âmbito **(CONV-09)**

| Tipo                      | Entry                         | Exemplo                           |
| ------------------------- | ----------------------------- | --------------------------------- |
| **Sourced** (profile)     | `<tool>() { … }`              | `gtt.sh`, `sdd.sh`                |
| **Executável** (one-shot) | `main()` + `main "$@"` no fim | `branches.sh` invocado como `gbr` |
| **Módulo Python**         | `def main():`                 | `issues_sync.py`, `tags.py`       |

### 6.2 Ordem de blocos no arquivo **(CONV-08)**

Ordem **de cima para baixo** no `<tool>.sh`:

```text
#!/usr/bin/env bash
# <tool> — one-line summary. Usage: <tool> help

# 1. Bootstrap — source libs (*.sh)

# 2. Private runtime — _<tool>_resolve_script, _<tool>_run_python, …

# 3. Command normalization — _<tool>_normalize_action

# 4. Help — _<tool>_show_help

# 5. Entry / orchestrator — <tool>() { … }

# (Profile hooks — NÃO definir <tool>-h no entry; ver CONV-14)
```

Regras: bootstrap antes de runtime; normalizer e help antes do orchestrator; orchestrator no fim («definitions first, entry last»).

**Shebang **(CONV-16)**:** a primeira linha **deve** ser `#!/usr/bin/env bash` (localiza `bash` via `PATH`; [Google Shell Style Guide](https://google.github.io/styleguide/shellguide.html)). **Não** usar `#!/bin/bash` salvo restrição explícita documentada em `spec_<tool>.md` do projeto.

### 6.3 Função entry pública **(CONV-09)**

- Orchestrator **deve** chamar-se como a ferramenta: `gtt()`, `sdd()`, …
- **Não deve** usar `main()` em scripts sourced.

| Python                       | Shell sourced                    |
| ---------------------------- | -------------------------------- |
| `def main():`                | `<tool>() { … }`                 |
| `if __name__ == "__main__":` | profile: `source …/<tool>.sh`    |
| imports / setup              | bootstrap `source` + `_<tool>_*` |

Corpo mínimo: config local → zero-args/help → `_<tool>_normalize_action` + `shift` → `case` só com canônicas → delegar.

### 6.4 Helpers privados **(CONV-10)**

| Padrão            | Uso                                 |
| ----------------- | ----------------------------------- |
| `_<tool>_<verbo>` | Função privada (runtime, bootstrap) |
| `<tool>_<verbo>`  | Função pública em lib sourced       |

### 6.5 Normalização de comandos **(CONV-11)**

Função **`_<tool>_normalize_action`**: primeiro token → ação canônica (stdout). Aliases na spec `<tool>`; dispatch sem aliases duplicados. Ferramentas hierárquicas usam também **`_<tool>_normalize_domain`** e **`_<tool>_normalize_verb`** (**CONV-26**); `_normalize_action` pode ser alias de `_normalize_verb` para o parser legado.

#### Help na normalização **(CONV-12)**

| Alias aceite | Canônica |
| ------------ | -------- |
| `help`       | `help`   |
| `-h`         | `help`   |
| `--help`     | `help`   |

Dispatch: `help)` → `_<tool>_show_help`. **Não** usar `-h` como canônica interna.

### 6.6 Help **(CONV-13)**

Implementação: `_<tool>_show_help` no entry. Texto e aliases longos: `spec_<tool>.md`.

### 6.7 Atalhos `<tool>-h` e profile **(CONV-14)**

`help` / `-h` / `--help` resolvem **no entry**. Atalhos `gtt-h`, `sdd-h`, etc. **só no profile** — ex.: `gtt-h() { gtt --help; }`.

### 6.8 Executável vs sourced **(CONV-15)**

Sourced + `<tool>()` para CLI via profile; `main "$@"` para invocação direta; `return 0` se sourced quando o arquivo serve também como lib.

### 6.9 Entry enxuto, libs e harmonização **(CONV-17)**

O `<tool>.sh` é **orquestrador**: bootstrap, normalização, help e `case` de dispatch. **Não** concentra lógica de domínio pesada.

| O quê                            | Onde vive                                                 | Agrupamento                                                  |
| -------------------------------- | --------------------------------------------------------- | ------------------------------------------------------------ |
| Alias → canônica                 | `_<tool>_normalize_action` (entry ou lib sourced)         | Tabela de aliases — não é “um arquivo por token”             |
| Dispatch                         | `<tool>() { … }`                                          | Um ramo `case` por **ação canônica**                         |
| Lógica shell reutilizável        | `*.sh` sourced no bootstrap (`nav.sh`, `git_admin.sh`, …) | Por **domínio/cohesão**, não por flag CLI                    |
| Lógica complexa (IO, API, menus) | Python (`_<tool>_run_python`, módulos por área)           | Subcomando alinhado à canônica quando a complexidade o exige |

**Harmonização normalize → delegate:** cada ação canônica emitida por `_<tool>_normalize_action` **deve** corresponder a **exatamente um** destino no orchestrator (função pública em lib, `_<tool>_run_python <módulo> …`, ou helper runtime). A tabela canônica → delegate e o índice de módulos vivem em `spec_<tool>.md`; comportamento detalhado de cada módulo em `spec_<stem>.md` (**CONV-18**).

Exemplos:

| Canônica         | Delegate                             |
| ---------------- | ------------------------------------ |
| `gtt` `-is-pull` | `_gtt_run_python issues_sync pull …` |
| `sdd` `pull`     | `_sdd_run_python sync pull "$key" …` |

**Quando extrair do entry** (para arquivo sourced separado):

- função ou bloco **reutilizado** por mais de um ramo do dispatch;
- normalizer, help ou runtime **dominam** o arquivo (orientação: ~40 linhas ou mais de lógica não-dispatch);
- lib já existente é o domínio natural (ex.: mover helpers de branches para `branches.sh`).

**Não** é obrigatório — nem recomendado por defeito — um arquivo shell **por ação CLI**. Tabelas de alias curtas permanecem no normalizer; a implementação vai para lib shell ou Python conforme a complexidade. Um arquivo só para `_<tool>_normalize_action` é opcional quando o entry ficar grande demais (ex.: `normalize.sh` sourced no bootstrap).

**Referência:** `computer-setup/toolkit/gtt/gtt.sh`; spec funcional `toolkit/gtt/specs/spec_gtt.md`.

### 6.10 Prompts interativos (CLI) **(CONV-25)**

Mensagens exibidas ao operador por scripts em `toolkit/<tool>/` (Python, shell, ou módulos invocados pelo entry) **devem** estar em **inglês**: títulos de diálogo, perguntas `Y/n`, rótulos de tabela, avisos (`⚠️`), confirmações e texto de ajuda embutido no fluxo interativo. **(CONV-25)**

| Camada                                                           | Idioma                                  | Exemplos                                     |
| ---------------------------------------------------------------- | --------------------------------------- | -------------------------------------------- |
| Specs normativas do catálogo (`docs/`) e cópias `_dev/spec_*.md` | Português (instruções ao desenvolvedor) | Este arquivo                                 |
| Specs temáticas do consumidor (`toolkit/<tool>/specs/`)          | Conforme o projeto                      | Podem ser PT-BR                              |
| Código e comentários em scripts                                  | Inglês                                  | **AGENTS-15**                                |
| **Caixas de diálogo / prompts CLI**                              | **Inglês**                              | `Confirm? [Y/n]:`, `Start release workflow?` |
| Mensagens de **commit** sugeridas pelo script                    | Conforme `spec_commits.md`              | Em geral inglês (`docs(manifest): …`)        |

Specs temáticas em português **não** autorizam prompts em português no código. Ao documentar fluxos interativos na spec do módulo, descrever o **texto em inglês** que o script exibe. Ver também § **9.1** (**CONV-32**) — prose normativa em PT-BR; citações de terminal/prompt em inglês.

### 6.11 CLI hierárquica (`<tool> <domínio> <verbo>`) **(CONV-26)**

Ferramentas com vários fluxos (sync, prompts, navegação, …) **devem** adotar gramática explícita **domínio + verbo**, documentada em `toolkit/<tool>/specs/spec_<tool>.md` § **Gramática do CLI**. **(AGENTS-29)**

| Peça        | Regra                                                                                 |
| ----------- | ------------------------------------------------------------------------------------- |
| **Forma**   | `<tool> [<domínio>] [<verbo>] [args...] [flags...]` — flags: § **6.13** (**CONV-28**) |
| **Domínio** | substantivo **singular** canônico (`issue`, `sync`, `prompt`, …)                      |
| **Verbo**   | token **sem hífen** (`open`, `pull`, `check`, …)                                      |
| **Default** | verbo implícito por domínio quando omitido (tabela na spec do tool)                   |
| **Aliases** | no normalizer apenas; dispatch usa só pares canônicos                                 |

**Normalizers (shell):**

| Função                     | Papel                                                              |
| -------------------------- | ------------------------------------------------------------------ |
| `_<tool>_normalize_domain` | primeiro token → domínio canônico ou vazio                         |
| `_<tool>_normalize_verb`   | verbo + aliases curtos (`pl`, `ps`, `op`, …)                       |
| `_<tool>_normalize_action` | opcional — alias legado de `_normalize_verb` para CLI plano antigo |

Ferramentas **simples** (um só fluxo) podem manter só `_<tool>_normalize_action` (**CONV-11**). Ferramentas **hierárquicas** usam `_normalize_domain` + `_normalize_verb` e **podem** manter compatibilidade com formas planas legadas num ramo `_dispatch_legacy`.

**Abreviações (alinhamento entre tools):**

| Token | Verbo usual        | Notas                                                        |
| ----- | ------------------ | ------------------------------------------------------------ |
| `op`  | `open`             |                                                              |
| `pl`  | `pull`             |                                                              |
| `ps`  | `push`             |                                                              |
| `ck`  | `check`            |                                                              |
| `ls`  | `list`             |                                                              |
| `prm` | `prompt` (domínio) | `<tool> prompt` / `<tool> prm` → default `all` (**CONV-27**) |
| `cr`  | `create`           |                                                              |

**Evitar:** prefixos legados `-pl`/`-ps` como forma *preferida* em specs novas — mapear para o verbo canônico, mas aceitar no normalizer durante transição. **Evitar** reutilizar `ci` como domínio quando `gtt` já o reserva para `commit`.

**Help em camadas (**CONV-13** estendido):** `_<tool>_show_help_global`, `_<tool>_show_help_domain`; opcional `_<tool>_show_help_verb` por domínio complexo (`gtt`).

### 6.12 Domínio `prompt` — arquivos para agente IA (`_dev/.prm_*.md`) **(CONV-27)**

Ferramentas que geram **templates de prompt** para assistentes de IA (Cursor / Composer) **devem** registrar cada artefato no domínio canônico **`prompt`** (alias de domínio **`prm`**), não como verbo de outro domínio nem flag CLI. **(AGENTS-29)**

| Regra             | Detalhe                                                                                                                         |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| **Entrada**       | `<tool> prompt` ou `<tool> prm` (sem target) → verbo implícito **`all`** → grava **todos** os prompts registrados na ferramenta |
| **Target**        | `<tool> prompt <target>` → um arquivo (ex.: `mytool prompt commit`)                                                             |
| **Registry**      | Mapa em Python `{ target → (_dev/.prm_….md, template) }`; fonte de verdade do CLI                                               |
| **Git**           | Arquivos `.prm_*` em `_dev/` — gitignored via `_dev/*`; não commitar no consumidor salvo decisão explícita                      |
| **Idioma**        | Corpo do template em **inglês** (**CONV-25**, **AGENTS-15**)                                                                    |
| **Novos prompts** | Entrada no registry + linha na spec do módulo (`spec_prompt.md` ou § equivalente em `spec_<tool>.md`)                           |
| **Legado**        | Formas antigas de invocação **podem** redireccionar com aviso stderr durante transição                                          |

**Orquestração entre tools:** compositores que invocam `<tool> prompt all` de dependências **não devem** duplicar templates — registrar na spec do compositor no consumidor.

### 6.13 Flags CLI (booleanas e composição) **(CONV-28)**

Complementa **CONV-26** com semântica de **flags** em CLIs hierárquicas (`<tool> [<domínio>] [<verbo>] …`). Comportamento por verbo e combinações exclusivas ficam na spec do módulo (`toolkit/<tool>/specs/spec_<module>.md`); aqui só o contrato transversal.

| Regra                     | Detalhe                                                                                                                                                                      |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Posição**               | Flags aplicam-se ao **verbo resolvido**. Forma canônica documentada: argumentos posicionais do verbo (se houver), depois flags. Ordem **livre entre flags** componíveis.     |
| **Booleanas componíveis** | Flags independentes (`action="store_true"`) **podem** acumular: ativar várias no mesmo comando sem ambiguidade.                                                              |
| **Forma longa**           | Canônica em help e specs: `--verbose`, `--dry-run`.                                                                                                                          |
| **Forma curta**           | Opcional, **um token por flag** (`-v`, `-n`); listar no help do verbo.                                                                                                       |
| **Sem cluster POSIX**     | **Não** exigir agrupamento `-vn` (= `-v` + `-n`) salvo implementação explícita e documentada.                                                                                |
| **Grupos exclusivos**     | Modos mutuamente exclusivos (ex.: `--json` vs `--table`) **devem** constar na spec do módulo; preferir `argparse` `add_mutually_exclusive_group` ou rejeitar com erro claro. |
| **Flags com valor**       | `--output PATH`, `--remote NAME` — não são booleanas; o valor segue imediatamente o token ou usa `=`.                                                                        |
| **Python**                | `argparse`; flags transversais a vários verbos via `parents=[common]` no subparser.                                                                                          |
| **Entry shell**           | Normalizer **deve** reconhecer e repassar flags ao delegate Python; cada flag nova entra na whitelist do splitter (`_*_split_args_flags` ou equivalente).                    |

**Exemplos abstractos** (placeholders — não assumir tool concreto):

```text
<tool> <domain> <verb> --verbose --dry-run
<tool> <domain> <verb> --dry-run --verbose
<tool> <domain> list --format table --no-header
```

Ao documentar exemplos no catálogo `docs/`, **deve** descrever o cenário e usar placeholders — ver orientação do mantenedor em `_dev/spec_specs-catalog.md` (repo **specs-catalog**).

### 6.14 Sanitização de SIGINT em CLIs Python **(CONV-30)**

Complementa **CONV-26** com tratamento de **interrupção pelo usuário** (`Ctrl+C` → `SIGINT` → `KeyboardInterrupt` em Python). Objetivo: **não** expor traceback nem stack interna da ferramenta — apenas uma mensagem de abort legível.

| Regra                           | Detalhe                                                                                                                                                                                                                                                                  |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Nome técnico**                | **Sanitização de SIGINT** — captura de `KeyboardInterrupt` no boundary do CLI, substituindo o handler por defeito do interpretador.                                                                                                                                      |
| **Mensagem padrão**             | Uma linha em branco + `ℹ️  Cancelled.` (inglês, **CONV-25**).                                                                                                                                                                                                             |
| **Código de saída**             | **130** (`128 + SIGINT`) — convenção POSIX para processo terminado por `SIGINT`.                                                                                                                                                                                         |
| **Sem traceback**               | **Não** imprimir `Traceback (most recent call last):` nem linhas de stack ao usuário.                                                                                                                                                                                    |
| **Entry point**                 | Envolver `main()` em handler compartilhado (`run_main_entry`); **não** usar `sys.exit(main())` sem captura em scripts interativos.                                                                                                                                       |
| **`input()` / prompts**         | Chamadas a `input()` em fluxos interativos **devem** passar por helper que captura `KeyboardInterrupt` e delega à sanitização (ex.: `safe_input`).                                                                                                                       |
| **Alterações parciais**         | Quando o protocolo **pode** deixar alterações no working tree (sync, commit, push, escrita de arquivos) **antes** do cancelamento, **deve** acrescentar aviso após a mensagem de abort — ex.: `⚠️  Partial changes may remain — review the working tree before retrying.` |
| **Implementação de referência** | `computer-setup/toolkit/clh/cli_interrupt.py` — `CANCELLED_MSG`, `PARTIAL_WARNING_MSG`, `exit_cancelled`, `safe_input`, `run_main_entry` (localização **CONV-31**).                                                                                                      |
| **Âmbito**                      | Scripts Python do **toolkit** com prompts ou fluxos longos; entry shell pode delegar ao Python sem duplicar lógica.                                                                                                                                                      |

**Exemplo de saída (abort simples):**

```text
Choice [Y]: ^C

ℹ️  Cancelled.
```

**Exemplo com alterações parciais possíveis:**

```text
Choice [Y]: ^C

ℹ️  Cancelled.
⚠️  Partial changes may remain — review the working tree before retrying.
```

---

## 7. Git — branches e tags

Normas transversais de nomenclatura para branches de trabalho e tags de release. Comportamento de ferramentas (`gtt tag`, `branches.sh`, …) fica nas specs temáticas do consumidor.

### 7.1 Branches de trabalho (nomenclatura) **(CONV-29)**

Branches de feature, correção e manutenção **devem** usar o formato **`<tipo>/<slug>`** — alinhado aos tipos de [`spec_commits.md`](spec_commits.md) quando aplicável.

| Parâmetro                  | Valor adotado                                                                                                                                                                     |
| -------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Formato**                | `<tipo>/<slug>` — ex.: `feat/gtt-tag-branch-push`                                                                                                                                 |
| **Tipos principais**       | `feat`, `fix`, `refactor`, `chore`, `docs`, `test`, `perf`, `ci`, `build`                                                                                                         |
| **Tipos operacionais**     | `wip` (incompleto), `hotfix` (urgente em produção), `experiment` / `spike` (prova de conceito), `backup` (snapshot antes de operação arriscada), `release` (preparação de versão) |
| **Slug**                   | minúsculas, palavras separadas por **hífen** (*kebab-case*), sem espaços nem caracteres especiais                                                                                 |
| **Branch estável**         | `main` (ou `defaults.branch` no manifesto) — integração e releases oficiais; **não** usar como prefixo de branch de trabalho                                                      |
| **Escopo por branch**      | uma finalidade por branch; evitar nomes genéricos (`fix/bug`, `feat/update`)                                                                                                      |
| **ID de issue** (opcional) | `<tipo>/<id>-<slug>` — ex.: `feat/42-tag-branch-push` — quando o projeto rastreia issues numeradas                                                                                |

Exemplos válidos: `feat/gtt-tag-branch-push`, `fix/install-profile-check`, `chore/bump-manifest-3-1-11`, `wip/context-compile-spike`.

**Não confundir** com tags Git (**CONV-06**, § **7.2**) nem com a branch estável de release.

Overrides locais (tipos extras, ID de issue obrigatório, prefixos legados): **`spec_<nome-repo>.md`** § **Convenções** ou § **Git** (**AGENTS-10**) — **não** em `_dev/spec_conventions.md` (sync).

### 7.2 Tags de release (nomenclatura) **(CONV-06)**

Tags Git marcam **um commit** como release publicável. Bump em `manifest.yaml` e entrada em `CHANGELOG.md` **não** criam tag automaticamente — ver [`spec_version.md`](spec_version.md) § **7**.

| Regra                      | Detalhe                                                                                                                                              |
| -------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Formato**                | `v` + SemVer do manifesto ou changelog do repositório — ex.: versão `2.1.0` → tag **`v2.1.0`**                                                       |
| **Alinhamento**            | O nome da tag **deve** coincidir com o campo `version` em `manifest.yaml` (ou versão declarada em `CHANGELOG.md` quando o projeto não usa manifesto) |
| **Tipo**                   | Preferir tag **anotada** (`git tag -a … -m …`); tags leves só se o projeto registrar isso explicitamente                                             |
| **Branch**                 | Releases oficiais na branch estável — em geral **`main`** (ou valor de `defaults.branch` no manifesto do catálogo)                                   |
| **Pré-release** (opcional) | `vX.Y.Z-alpha.N`, `vX.Y.Z-beta.N`, `vX.Y.Z-rc.N` — candidatura antes da estável; ver [`spec_version.md`](spec_version.md) § **8** (**VERSION-09**)   |
| **Proibido**               | Reutilizar o mesmo nome de tag para outro commit (`git tag -f`) em release já publicada no remoto                                                    |

Exemplos válidos: `v1.2.0`, `v2.0.0`, `v2.1.0-rc.1`.

### 7.3 Inventário por projeto **(CONV-07)**

Cada repositório que publica releases **deve** manter tabela **Inventário de tags Git** atualizada **sempre que** uma tag de release for criada ou quando o assistente orientar o operador a criá-la após bump de versão.

**Onde registrar (precedência):**

| Destino                                                                | Quando                                                                                                                                                                                                                                   |
| ---------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`_dev/spec_<nome-repo>.md`** § **Convenções** ou § **Versionamento** | **Sempre** no consumidor — subseção **Inventário de tags Git** (**AGENTS-03**, **AGENTS-10**). Criar o arquivo ou a seção se ainda não existirem.                                                                                        |
| Contrato maduro `docs/specs/` ou `specs/` (raiz)                       | `spec_conventions.md` ou arquivo **equivalente** na mesma pasta (objetivo semelhante — layout, escopos, inventário). **Complementa** o repo-spec; **não** substitui a seção em `spec_<nome-repo>.md` enquanto o consumidor usar `_dev/`. |
| **`_dev/spec_conventions.md`** (sync do manifest)                      | **Proibido** — entrada read-only do catálogo; **não** recebe especificidades locais (**AGENTS-07**, **AGENTS-10**).                                                                                                                      |

| Coluna     | Conteúdo                                                  |
| ---------- | --------------------------------------------------------- |
| **Tag**    | Nome exato — ex.: `v1.2.0`                                |
| **Versão** | Valor SemVer (espelho do manifesto/changelog)             |
| **Branch** | Branch onde a tag foi (ou será) aplicada — ex.: `main`    |
| **Data**   | ISO `YYYY-MM-DD` da release (ou data prevista ao sugerir) |
| **Notas**  | Resumo opcional — ex.: «MAJOR: upstream em `docs/`»       |

**Regra de manutenção:** ao sugerir ou registrar uma tag, o assistente **deve** acrescentar ou atualizar a linha correspondente no inventário **no mesmo PR/tarefa** que alterou `manifest.yaml`, `CHANGELOG.md` ou norma de versionamento — em **`spec_<nome-repo>.md`** (seção correspondente) e, se existir contrato maduro de convenções, também lá. Ferramentas (`gtt tag`, …) **devem** orientar o operador para esse path — **não** para `_dev/spec_conventions.md` (sync). O operador humano executa `git tag` e `git push` — ver **VERSION-07** / **VERSION-08** e **AGENTS-25**.

**Modelo (substituir pelos dados do projeto):**

| Tag              | Versão  | Branch | Data         | Notas                       |
| ---------------- | ------- | ------ | ------------ | --------------------------- |
| *(ex.)* `v1.0.0` | `1.0.0` | `main` | `2026-01-01` | Primeira release versionada |

---

## 8. Migrations (evolução de layout esperado) **(CONV-19)**–**CONV-24)**

Norma transversal para **scripts de instalação**, **ferramentas CLI** e **bootstrap** que alteram paths, arquivos, chaves de manifesto ou variáveis que o consumidor já pode ter no ambiente ou no repositório.

O termo **migration** neste catálogo **não** designa migrations de base de dados: designa **passos one-shot e idempotentes** que adaptam estado **legado** ao layout **atual** esperado pelo código.

Complementa [`spec_version.md`](spec_version.md) (quando comunicar breaking change) — **não** o substitui.

### 8.1 Âmbito e propósito **(CONV-19)**

| Conceito            | Significado                                                                                  |
| ------------------- | -------------------------------------------------------------------------------------------- |
| **Layout esperado** | Paths, nomes de arquivo, chaves de configuração ou metadado que o código **atual** assume    |
| **Estado legado**   | Artefato ainda presente de versão anterior (pasta obsoleta, arquivo renomeado, chave antiga) |
| **Migration**       | Detecção + adaptação do legado → layout esperado, antes ou durante o fluxo principal         |

**Propósito:** evitar que o usuário fique bloqueado após evoluir o script ou a ferramenta; reduzir deriva silenciosa entre máquinas ou clones antigos e o contrato novo.

### 8.2 Quando usar **(CONV-20)**

Registar migration quando uma evolução **depreca** algo que o consumidor **pode já ter**:

- path ou pasta substituída (ex.: scripts deixam de viver numa cópia em `$HOME` e passam a viver no repositório);
- rename de arquivo downstream ou upstream;
- rename ou remoção de chave em manifesto ou arquivo de metadado de sync;
- variável ou arquivo de configuração substituído por outro mecanismo.

**Não** usar migrations para:

- lógica de negócio recorrente (sync, pull, menu);
- correcções que não dependem de estado legado do consumidor;
- substituir bump SemVer ou comunicação de breaking change.

### 8.3 Onde e como implementar **(CONV-21)**

| Contexto                   | Padrão sugerido                                                                    |
| -------------------------- | ---------------------------------------------------------------------------------- |
| **Instalador / bootstrap** | bloco `run_migrations` (ou equivalente) invocado **antes** de ativar o layout novo |
| **Ferramenta CLI**         | `migrations.py`, `migrations.sh` ou seção dedicada sourced pelo entry              |
| **Ordem de execução**      | migrations **antes** do fluxo que assume o layout atual (sync, install, dispatch)  |

**Registo ordenado:** manter lista explícita de migrations (tuple, array ou funções registradas em sequência). Cada entrada **deve** poder correr isolada e **deve** documentar o que detecta e o que altera.

**Esqueleto comum:**

```text
1. Detectar legado (path existe, chave antiga, arquivo com nome obsoleto)
2. Se ausente → skip (idempotente)
3. Explicar ao operador o que mudou e o que será feito
4. Confirmar (salvo flag --yes documentada)
5. Aplicar (rename, remove, regravar metadado, commit sugerido)
6. Nunca repetir se o layout já está atual
```

Separar migrations da lógica principal — não intercalar adaptações legadas no meio de menus ou sync.

### 8.4 Regras operacionais **(CONV-22)**

| Regra                     | Detalhe                                                                                                                |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| **Idempotência**          | Segunda execução **não deve** re-aplicar nem falhar se já migrado                                                      |
| **Detecção primeiro**     | Só actuar quando o legado estiver presente                                                                             |
| **Confirmação**           | Ações destrutivas ou irreversíveis: prompt `[y/N]` por defeito; `--yes` / `-y` só se documentado na spec da ferramenta |
| **Mensagens claras**      | Indicar **o quê** era esperado antes, **o quê** passa a valer, **o quê** será alterado                                 |
| **Destrutivo vs. rename** | Remover artefato obsoleto ≠ renomear arquivo tracked — documentar risco distinto                                       |
| **Git**                   | Se migration altera arquivos versionados, prever subject de commit padrão e confirmação de mensagem                    |
| **Falha segura**          | Cancelamento do operador **não deve** corromper estado; fluxo principal pode continuar ou abortar de forma explícita   |

### 8.5 Documentação **(CONV-23)**

- Regra geral: **este § 8**.
- Por ferramenta (**CONV-18**): `spec_migrations.md` ou seção **Migrations** no spec do módulo `migrations.*`, listando cada migration registrada (detecção, ação, confirmação, commit sugerido).
- Hub `spec_<tool>.md`: indicar que migrations correm antes do fluxo principal e apontar para o spec de migrations.

Ao adicionar migration nova, atualizar o spec **no mesmo PR/tarefa** que altera o código.

### 8.6 Orientação para IA **(CONV-24)**

Ao **deprecar** layout, path, chave ou variável que consumidores possam já ter:

1. **Registar** migration idempotente conforme § **8.3**–**8.4**.
2. **Documentar** no spec da ferramenta (§ **8.5**).
3. **Avaliar** impacto SemVer em [`spec_version.md`](spec_version.md) — migration não dispensa comunicação de breaking change quando aplicável.
4. **Não assumir** que o ambiente ou clone já está no layout novo.
5. **Não** remover suporte ao legado sem migration ou período de detecção documentado, salvo pedido explícito do mantenedor.

---

## 9. Modelo de documento normativo **(CONV-32)**–**CONV-38)**

Normas transversais para **redigir** specs Markdown citáveis — catálogo sync (`docs/`), domínio local (`_dev/spec_<domínio>.md`), contrato maduro (`docs/specs/`, `specs/`), toolkit (`toolkit/<tool>/specs/`) ou repo-spec (`spec_<nome-repo>.md`). Aplica-se a **specs novas** e a revisões incrementais; **não** substitui tarefas de refactor em massa (renumeração temática, migração de vocabulário legado) — ver prompt `prm_specs_refactor` no toolkit SDD.

**Objetivo de compilação:** cada spec **deve** ser consumível por assistentes, `sdd context compile`, RAG e ontologia leve — índice semântico, âncoras no corpo e metadados opcionais (**CONV-37**).

### 9.1 Esqueleto do arquivo **(CONV-32)**

Antes do corpo numerado, **toda** spec normativa **deve** seguir o esqueleto abaixo. **Não** renumerar estes títulos; **não** prefixá-los com `N.`.

| Ordem | Tópico                              | Função                                                                                    |
| ----- | ----------------------------------- | ----------------------------------------------------------------------------------------- |
| 1     | `# Título` (H1)                     | Nome da spec; alinhado ao basename (`spec_<tema>.md`).                                    |
| 2     | Apresentação (parágrafo(s) após H1) | Público-alvo, papel, escopo em uma linha; **«Não substitui …»**.                          |
| 3     | `## Objetivo`                       | O **quê** e **para quem**; limites; pode incluir tabela de escopo resumida.               |
| 4     | `## Referências`                    | Contexto, ADRs, RFC 2119, specs irmãs — § **9.5**. **Sem** norma operacional nova sem ID. |
| 5     | `## Como citar este documento`      | Mecanismos + índice de IDs — § **9.2**–**9.4**.                                           |
| 6     | `---`                               | Separador **antes** do corpo numerado (`## 1. …`).                                        |

**Ordem fixa:** Objetivo → Referências → Como citar. **Não** inverter Referências e Como citar.

**Idioma:** specs normativas do catálogo **devem** estar em **português do Brasil (PT-BR)** — apresentação, Objetivo, Referências, índice e corpo. Termos técnicos consagrados em inglês (`commit`, `foreignKey`, nomes de flags) permanecem em inglês quando usual. **Não** traduzir identificadores (`PREFIX-NN`, caminhos, comandos). **Exceção:** exemplos de **output de terminal**, **prompts interativos** e **estruturas de diálogo** citados na spec (blocos de código, tabelas de fluxo, strings entre aspas) **devem** estar em **inglês** — ver **CONV-25** § **6.10**; a prose normativa ao redor permanece PT-BR.

**Após** o `---`: corpo normativo numerado (**§ 1**, **§ 2**, …). Normas citáveis vivem **aí** — **não** dispersar em Objetivo/Referências salvo **Seção** `(obj.)` no índice.

#### Blocos opcionais (domínio / funcional)

Podem preceder ou integrar o capítulo **§ 1** — **sem** numeração de capítulo no título:

| Bloco                            | Uso                                                                                                 |
| -------------------------------- | --------------------------------------------------------------------------------------------------- |
| `## Escopo`                      | Tabela inclui / não inclui; subseções **v1** / **v2** quando o repo versiona entregas.              |
| `## Notação` / `## Glossário`    | Símbolos **sem** ID próprio (placeholders). Termos transversais → § **9.11** ou IDs `PREFIX-GL-NN`. |
| `## Specs relacionadas`          | Tabela de dependências entre arquivos.                                                              |
| `## Implementação de referência` | Paths de código alvo; **não** normativo — sem ID salvo obrigação explícita.                         |
| `## Decisões em aberto`          | Pendências; **sem** IDs — listar em backlog, não como norma.                                        |

Símbolos de notação **não** substituem `PREFIX-NN`; toda obrigação RFC 2119 ou regra verificável **deve** ter ID na tabela (**CONV-36**).

#### Corpo numerado

| Nível        | Formato             | Uso                   |
| ------------ | ------------------- | --------------------- |
| Capítulo     | `## N. Título`      | Seções principais.    |
| Subseção     | `### N.M Título`    | Detalhe no capítulo.  |
| Sub-subseção | `#### N.M.P Título` | Só quando necessário. |

- **N** começa em **1** após o `---`.
- Coluna **Seção** do índice alinhada à numeração real (`1.2`, `3`, `10.3`).
- Títulos **podem** incluir intervalos de IDs: `### 1.2 Precedência **(PREFIX-02**–**05**)`**.
- Texto histórico («foi decidido», «implementação concluída») **deve** condensar-se em norma presente (*deve* / *não deve*) ou mover contexto a **Referências** / ADR.

### 9.2 Índice semântico **(CONV-33)**

Em **`## Como citar este documento`**, cada spec **deve** incluir:

1. Tabela estreita de **mecanismos** (3–4 linhas): seção numerada, ID normativo, prefixo, hub quando aplicável.
2. **`**Índice de IDs normativos deste arquivo**`:** tabela com **quatro colunas** — ordem **fixa**:

```markdown
| ID        | Tema   | Seção | Resumo |
| --------- | ------ | ----- | ------ |
| PREFIX-01 | Layout | 1.1   | …      |
```

3. **`**Índice por tema**`:** logo abaixo — derivado da tabela (se divergir, prevalece a tabela):

```markdown
| Tema   | IDs       |
| ------ | --------- |
| Layout | PREFIX-01 |
```

**Fonte canônica por arquivo:** a tabela em **Como citar** deste `spec_*.md` — base para compilação (**CONV-37**, [`spec_context.md`](spec_context.md) § **3.4**).

**Prefixo:** catálogo sync → § **1.2** e hub § **2** (**CONV-04**); domínio local → **`spec_<nome-repo>.md` § Convenções** (**AGENTS-04**, **AGENTS-07**).

Ao acrescentar ID: próximo `PREFIX-NN` livre **neste arquivo**; atualizar índice local; catálogo sync → hub § **2** (**CONV-04**).

### 9.3 Coluna `Tema`

| Regra           | Detalhe                                                                         |
| --------------- | ------------------------------------------------------------------------------- |
| **Uma palavra** | Sem espaços; ex.: `Precedência`, `Pipeline`, `Modal`, `Navegação`, `Validação`. |
| **PT-BR**       | Família normativa, **não** a norma inteira.                                     |
| **Reutilizar**  | Mesmo **Tema** para IDs da mesma família no arquivo.                            |

Agrupar linhas do índice por **Tema** facilita leitura humana e filtros RAG; **não** implica renumeração obrigatória de IDs ao criar spec nova.

### 9.4 Coluna `Resumo` **(CONV-34)**

Frase densa, autônoma, **PT-BR** (~25–55 palavras):

| Elemento         | Conteúdo                                                                 |
| ---------------- | ------------------------------------------------------------------------ |
| **Quem**         | Assistente, Admin, handler, `code_*`, operador                           |
| **Modal**        | *deve* / *não deve* / *pode*                                             |
| **O quê**        | Ação verificável                                                         |
| **Onde/quando**  | View (`add`/`change`), evento (`blur`, `submit`, `GET`), módulo          |
| **Artefatos**    | Paths principais quando couber (`change_form.html`, `admin_handlers.py`) |
| **Dependências** | IDs relacionados (`requer PREFIX-03`; «inalterado **PREFIX-18**»)        |

**Não** repetir **Tema** no resumo. Preferir **uma norma = um ID = um chunk** RAG.

### 9.5 Referências mínimas **(§ 9.1)**

| Bloco               | Conteúdo mínimo                                                                                |
| ------------------- | ---------------------------------------------------------------------------------------------- |
| Contexto do domínio | 1+ bloco ou lista com links (ADRs, specs irmãs, RFC externa)                                   |
| RFC 2119            | *deve* / *não deve* / *pode* — referência a este arquivo ou [`spec_agents.md`](spec_agents.md) |
| IDs                 | Formato `PREFIX-NN`; registro de prefixo (§ **1.2** ou repo-spec); ID **não** reutilizado      |
| Specs irmãs         | Links às `spec_*.md` aplicáveis                                                                |

### 9.6 Âncoras no corpo **(CONV-35)**

Cada `PREFIX-NN` na tabela **deve** ter âncora **`**(PREFIX-NN)**`** no corpo (ou bloco de compilação — § **9.12**). Cada norma citável com âncora **deve** ter linha na tabela. Coluna **Seção** **deve** coincidir com a numeração real.

### 9.7 O que recebe ID normativo **(CONV-36)**

#### Criar ID quando

- Obrigação RFC 2119 (*deve* / *não deve* / *pode* com efeito verificável).
- Contrato transversal (pipeline, Admin, API JSON, CLI).
- Regra referenciada em outra seção ou spec irmã.
- Decisão arquitectural com **efeito permanente** no código — condensar em norma presente, não só histórico.
- **Mensagem normativa** fixa (ValidationError, modal, `notices`, JSON `message`) — texto **exato** pt-BR no corpo; **Tema** `Erro`, `Modal` ou `Aviso`.
- **Contrato JSON** (campo obrigatório, `ok: false`, desempate) — ID por regra verificável.
- **Exit code / task CLI** — comportamento normativo (`exit 1` se falha).
- **Casos de aceite** verificáveis — ID por caso ou seção `### Casos de aceite` com âncoras.
- **Exceção a regra** — ID da exceção + menção ao ID base no **Resumo**.
- **Invariantes** de algoritmo/ORM — IDs nos *deve*/*não deve*; pseudocódigo permanece narrativo.

#### Não criar ID quando

- Exemplo ilustrativo, seed de teste, pendência (`toDo.md`, **Decisões em aberto**).
- Descrição de estado atual sem obrigação — salvo «**deve** existir / comportar-se assim».
- Duplicata exata de ID já definido na mesma spec (fundir).
- Contexto / motivação / ADR sem obrigação derivada — ficar em **Referências**.

Para cada ID novo: linha na tabela, **Índice por tema**, âncora no corpo; catálogo sync → hub § **2** (**CONV-04**).

### 9.8 Perfis de conteúdo (mapas de corpo)

Classificar a spec ao redigir e adotar capítulos adequados — **após** o `---`:

| Perfil                  | Capítulos típicos                                                                                     |
| ----------------------- | ----------------------------------------------------------------------------------------------------- |
| **Arquitetura**         | Layout, pipeline, decisões → normas presentes                                                         |
| **Fluxo Admin / UI**    | Notação → Escopo → Navegação / persistência → Modais → Servidor → Testes                              |
| **Contrato API**        | Por endpoint: params GET, shape JSON, erros (`ok: false`), regras `notices`                           |
| **Domínio transversal** | Contexto → Decisão → Algoritmo → Mensagens → Casos de aceite → Implementação                          |
| **Algoritmo / regras**  | Invariantes como IDs; corpo descritivo para pseudocódigo/ORM                                          |
| **Ferramenta / script** | Comportamento CLI, entradas/saídas, exit codes, tasks, `schemas/`                                     |
| **Rascunho**            | Esqueleto completo; **não** inventar IDs para hipóteses não implementadas                             |
| **Repo-spec**           | Seções SDD; § **Convenções** com prefixos locais — **sem** duplicar normas de domínio (**AGENTS-03**) |

### 9.9 Glossário compartilhado **(CONV-38)**

Quando o mesmo símbolo normativo aparece em **duas ou mais** specs do mesmo domínio:

1. **Preferir** arquivo `spec_<domínio>_glossario.md` (ou seção canônica em spec transversal) com IDs `PREFIX-GL-NN`.
2. Nas specs de fluxo: **Notação** remete ao glossário; corpo cita `**PREFIX-GL-NN**` em vez de símbolo ad hoc.
3. Registar o glossário na tabela de prefixos em `spec_<nome-repo>.md` § **Convenções**.

### 9.10 Metadados de compilação (opcional)

Logo após **Índice por tema**, o arquivo **pode** incluir **`## Metadados de compilação`** quando o **Resumo** alone não bastar (múltiplas camadas, muitos artefatos):

```markdown
| ID        | Camada   | Gatilho | View   | Artefatos          | Requer       |
| --------- | -------- | ------- | ------ | ------------------ | ------------ |
| PREFIX-01 | Admin    | —       | —      | `settings.py`      | —            |
| PREFIX-02 | UI+Admin | blur    | change | `change_form.html` | PREFIX-GL-02 |
```

| Coluna        | Valores sugeridos                                           |
| ------------- | ----------------------------------------------------------- |
| **Camada**    | `UI`, `Admin`, `API`, `code_*`, `ORM`, `Pipeline`, `Layout` |
| **Gatilho**   | `blur`, `submit`, `GET`, `POST`, `save`, `—`                |
| **View**      | `add`, `change`, `changelist`, `—`                          |
| **Artefatos** | Paths relativos ao repo                                     |
| **Requer**    | IDs pré-requisito (grafo)                                   |

### 9.11 Contrato de compilação **(CONV-37)**

Specs **devem** adotar práticas compatíveis com compilação semântica — **não** limitadas ao parser atual de `context_compile.py` ([**CONTEXT-10**](spec_context.md)).

| Camada                         | Formato                                                                 | Papel                                   |
| ------------------------------ | ----------------------------------------------------------------------- | --------------------------------------- |
| **1 — Índice canônico**        | Tabela `\| ID \| Tema \| Seção \| Resumo \|` em **Como citar**          | Fonte primária: ID, tema, digest, seção |
| **2 — Âncoras no corpo**       | `**(PREFIX-NN)**` junto à norma                                         | Liga chunk de corpo ao ID (**CONV-35**) |
| **3 — Metadados estruturados** | Tabela § **9.10** ou bloco YAML após o índice                           | Grafos, `path_scopes`, filtros RAG      |
| **4 — Bloco norma (futuro)**   | Fence ` ```norma id=PREFIX-NN` com corpo autônomo                       | Chunk 1:1 para embeddings               |
| **5 — Casos de aceite**        | Tabela `\| ID \| Entrada \| Resultado esperado \|` ou lista com âncoras | Testes / QA / RAG verificável           |
| **6 — Mensagens canônicas**    | Tabela `\| ID \| Código/HTTP \| Texto pt-BR \|`                         | UI/API; i18n futuro                     |

#### Ontologia leve (orientação)

- **`PREFIX-NN`** — identificador estável (fragmento URI futuro: `spec:<repo>#PREFIX-NN`).
- **`Tema`** — tipo/categoria (SKOS-like broader).
- **`Requer`** (metadados) — aresta `dependsOn` entre normas.
- **Specs relacionadas** — aresta `seeAlso` entre documentos.

Implementação do gerador: [`spec_context.md`](spec_context.md) § **3.4** (**CONTEXT-10**).

