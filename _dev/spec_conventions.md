# Convenções transversais do projeto

Modelo de registro para convenções organizacionais e orquestração de configuração em repositórios SDD.

## Objetivo

Centralizar **convenções organizadoras** do projeto — pastas, nomenclatura (`spec_*`, `toolkit/<tool>/`, …),
configuração de ambiente (shell, Git, Python, editores) — sem duplicar comportamento funcional
de cada ferramenta.

Comportamento detalhado fica nas specs temáticas do projeto. **Onde** registrar convenções: cópia do catálogo em `_dev/`; contrato maduro em **`docs/specs/`** ou **`specs/`** (raiz) — ver [`spec_agents.md`](spec_agents.md) § **1. Pastas de especificação no projeto** (**AGENTS-02**–**03**).

Ao introduzir tema transversal novo, atualizar **`spec_conventions.md`** na pasta **protagonista** (madura, se existir; senão `_dev/`).

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

    Formato **`PREFIXO-NN`** (ex.: `AGENTS-02`). O **prefixo** identifica o arquivo de spec (§ **1.2**). O **número da seção** (`§ 4.1`) organiza a leitura e pode mudar; o **ID não** deve ser reutilizado com outro sentido.

    - **Índice só deste arquivo:** § **Como citar este documento** abaixo.
    - **Índice completo do catálogo:** § **2**.

??? tip "Orquestração de variáveis e configuração"

    Variáveis de ambiente, URLs, paths padrão e aliases de shell devem ter **definição canônica** em § **4** (**CONV-02**). Evita que scripts e a IA inventem o mesmo conceito com nomes diferentes.

    **Referências externas**

    - [12-Factor — Dev/prod parity & config](https://12factor.net/config) — uma configuração explícita por deploy.
    - [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — incluir no contexto só o necessário.

??? info "Nomenclatura, layout e pastas de specs"

    Padrões de nome (`spec_<domínio>`, `spec_<nome-repo>`, `0001_…`, `toolkit/<tool>/…`) variam por projeto. Em `_dev/`, **três famílias** ([`spec_agents.md`](spec_agents.md) § **1.3**): entrada **sync do manifest** (read-only); **`spec_<nome-repo>.md`** (overrides SDD — **AGENTS-22**, **AGENTS-25**); **`spec_<domínio>.md` local** (domínio do projeto — **AGENTS-26**). O prefixo `spec_` **não** implica catálogo. Papéis dos `README.md`: § **1.5** (**AGENTS-23**). Precedência: § **1.2** (**AGENTS-02**–**06**, **AGENTS-25**, **AGENTS-26**).

    **Referências externas**

    - [PEP 8](https://peps.python.org/pep-0008/) — Python, se adotado no projeto.
    - [Google Shell Style Guide](https://google.github.io/styleguide/shellguide.html) — shell, se aplicável.

??? quote "Normas e artefatos deste catálogo"

    - [`spec_agents.md`](spec_agents.md) — SDD, ordem de leitura, pastas, idioma.
    - [`spec_commits.md`](spec_commits.md) — commits (baseline EN; overrides em `spec_<nome-repo>.md`).
    - [`spec_version.md`](spec_version.md) — SemVer.
    - `_dev/toDo.md` — pendências (não normativo).
    - `README.md` na raiz do projeto de aplicação — visão geral.

---

## Como citar este documento

| Mecanismo           | Uso                                            |
| ------------------- | ---------------------------------------------- |
| **Seção numerada**  | `§ 4.1` — navegação neste arquivo.             |
| **ID normativo**    | `CONV-02` — citação estável.                   |
| **Índice completo** | § **2** — todos os IDs do catálogo em `docs/`. |
| **Prefixo**         | `CONV` — ver § **1.2**.                        |

**Índice de IDs deste arquivo:**

| ID      | Seção | Resumo                                                                                   |
| ------- | ----- | ---------------------------------------------------------------------------------------- |
| CONV-01 | 3     | Ao registrar convenção: definição, onde vale, inventário, manutenção                     |
| CONV-02 | 4     | Variáveis compartilhadas: inventário canônico neste arquivo                              |
| CONV-03 | 4     | Não duplicar default de variável já no inventário                                        |
| CONV-04 | 2, 11 | Ao criar ID em qualquer spec do catálogo: atualizar § **2** e o índice local da spec     |
| CONV-05 | 5     | Modelo compartilhado: elevar ao upstream (**AGENTS-14**)                                 |
| CONV-06 | 7     | Nomenclatura de tags Git: prefixo `v` + SemVer                                           |
| CONV-07 | 7     | Inventário de tags em `spec_<nome-repo>.md` ou contrato maduro — **não** em entrada sync |
| CONV-08 | 6     | Entry shell: ordem de blocos no `<tool>.sh` sourced                                      |
| CONV-09 | 6     | Entry shell: orchestrator `<tool>()`, não `main()`                                       |
| CONV-10 | 6     | Entry shell: helpers privados `_<tool>_*`                                                |
| CONV-11 | 6     | Entry shell: `_<tool>_normalize_action`                                                  |
| CONV-12 | 6.3   | Entry shell: help `help`/`-h`/`--help` → canônica `help`                                 |
| CONV-13 | 6     | Entry shell: `_<tool>_show_help`                                                         |
| CONV-14 | 6     | Entry shell: `<tool>-h` só no profile, não no entry                                      |
| CONV-15 | 6     | Entry shell: script executável vs sourced                                                |
| CONV-16 | 6.2   | Entry shell: shebang `#!/usr/bin/env bash`                                               |
| CONV-17 | 6.9   | Entry shell: entry enxuto, libs e harmonização normalize → delegate                      |
| CONV-18 | 1.3   | Toolkit: `spec_<module>.md` por script; hub `spec_<tool>.md`                             |
| CONV-19 | 8     | Migrations: âmbito e propósito                                                           |
| CONV-20 | 8.1   | Migrations: quando usar (deprecação de layout esperado)                                  |
| CONV-21 | 8.2   | Migrations: onde e como implementar                                                      |
| CONV-22 | 8.3   | Migrations: regras operacionais (idempotência, confirmação, registo)                     |
| CONV-23 | 8.4   | Migrations: documentação por ferramenta                                                  |
| CONV-24 | 8.5   | Migrations: orientação para IA ao deprecar layout                                        |
| CONV-25 | 6.10  | Prompts interativos de scripts toolkit em **inglês** (**AGENTS-08**)                     |
| CONV-26 | 6.11  | CLI hierárquica: domínio + verbo; normalizers; help em camadas (**AGENTS-24**)           |
| CONV-27 | 6.12  | Domínio `prompt` / `prm` para ficheiros `_dev/.prm_*.md` (**AGENTS-24**)                 |
| CONV-28 | 6.13  | Flags CLI: booleanas componíveis, ordem livre após verbo; shell → Python (**AGENTS-24**) |

---

## 1. Numeração e prefixos do catálogo

### 1.1 Regras gerais

- Seções normativas do catálogo usam **`## N. Título`** e, quando necessário, **`### N.M`** e listas numeradas.
- **Objetivo**, **Referências** e **Como citar este documento** ficam sem número de capítulo (metadados do arquivo).
- Cada spec tem **índice local** de IDs em **Como citar**; este arquivo mantém o **índice completo** em § **2**.

### 1.2 Prefixos por arquivo (catálogo `docs/`)

| Arquivo                                      | Prefixo ID | Escopo Conventional Commits (referência) |
| -------------------------------------------- | ---------- | ---------------------------------------- |
| [`spec_agents.md`](spec_agents.md)           | `AGENTS`   | `agents`                                 |
| [`spec_commits.md`](spec_commits.md)         | `COMMITS`  | `commits`                                |
| [`spec_issues.md`](spec_issues.md)           | `ISSUES`   | `issues`                                 |
| [`spec_conventions.md`](spec_conventions.md) | `CONV`     | `conventions`                            |
| [`spec_version.md`](spec_version.md)         | `VERSION`  | `version`                                |

Specs **do domínio** no contrato maduro (`docs/specs/`, `specs/`): acrescentar linhas nesta tabela ao adotar IDs.

### 1.3 Specs por ferramenta (`toolkit/<tool>/specs/`) **(CONV-18)**

Ferramentas CLI em `toolkit/<tool>/` **devem** documentar comportamento em `toolkit/<tool>/specs/`:

| Papel      | Ficheiro         | Conteúdo                                                                                                     |
| ---------- | ---------------- | ------------------------------------------------------------------------------------------------------------ |
| **Hub**    | `spec_<tool>.md` | Entry (`<tool>.sh`), normalização, tabela **canónica → delegate**, índice de módulos, variáveis transversais |
| **Módulo** | `spec_<stem>.md` | Comportamento do script `<stem>.py` ou `<stem>.sh` (`<stem>` = basename sem extensão)                        |

**Regra geral:** um `spec_<stem>.md` **por ficheiro de implementação substantivo** — salvo excepções abaixo.

**Excepções** (não exigem spec dedicada):

- `README.md` na pasta da ferramenta (índice operacional curto).
- Ficheiro trivial (orientação: &lt; ~30 linhas, sem comportamento normativo próprio).
- Re-export ou shim que só encaminha para outro módulo já especificado.
- Artefactos gerados ou só de teste.

**Sem duplicar norma:** o hub referencia módulos (`Detalhes: spec_sync.md`); cada spec de módulo referencia o hub para CLI, aliases e dispatch. Comportamento detalhado fica no módulo; orquestração fica no hub.

**Harmonização com CONV-17:** cada canónica do normalizer → um delegate no hub → implementação no módulo correspondente (`sync.py`, `nav.sh`, …).

**Referência:** `computer-setup/toolkit/gtt/specs/` (`spec_gtt.md` + `spec_nav.md`, `spec_issues_sync.md`, …); `toolkit/sdd/specs/`.

### 1.4 Manifesto multinível

Repositórios com `manifest.yaml` que declaram `version:`, `areas.*` e opcionalmente grupos filhos versionados (`toolkit.*`, …) **devem** manter consistência SemVer entre níveis — ver [`spec_version.md`](spec_version.md) § **9** (**VERSION-10**, **VERSION-11**, **VERSION-12**, **VERSION-13**).

| Regra          | Resumo                                                                                     |
| -------------- | ------------------------------------------------------------------------------------------ |
| **VERSION-10** | Núcleo de `version:` ≥ núcleo de qualquer outro campo versionado no manifesto              |
| **VERSION-11** | Núcleo de cada entrada em grupo filho ≤ núcleo de `areas.<nome>` homónimo                  |
| **VERSION-12** | Secção YAML do grupo filho **deve** ter o mesmo nome que a chave do agregador em `areas.*` |
| **VERSION-13** | Todo bump em filho propaga PATCH/MINOR/MAJOR na cadeia até `version:`                      |

| Repositório                            | `areas.*`                                                                                                     |
| -------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| **`specs-catalog`**                    | Uma chave por entrada do manifesto (`readme`, `agents`, `commits`, …) — alinhada a `entries` / `commit_scope` |
| **Consumidor** (ex.: `computer-setup`) | Áreas do repo (`setup`, `toolkit`, `utils`) + opcional grupo filho `toolkit.<tool>` (secção `toolkit:`)       |

Exemplos de layout: `specs-catalog/manifest.yaml`, `computer-setup/manifest.yaml`. O assistente **deve** verificar **VERSION-10** e **VERSION-13** ao sugerir bumps ou `git tag`; **VERSION-11** / **VERSION-12** quando existir grupo filho versionado.

---

## 2. Índice completo de IDs normativos (catálogo)

Lista **canônica** de IDs em vigor no catálogo upstream (`docs/`). Ao adicionar ou obsoletar um ID, atualizar **esta tabela** e o índice em **Como citar** do arquivo correspondente. **(CONV-04)**

### `AGENTS` — [`spec_agents.md`](spec_agents.md)

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
| AGENTS-09 | 4     | Não inventar regra de domínio sem base                                                 |
| AGENTS-10 | 3     | Ao pedido de commit: ler spec de commits em vigor                                      |
| AGENTS-11 | 3, 8  | Não executar `git commit`/`push` sem pedido explícito                                  |
| AGENTS-12 | 3     | Spec de commits prevalece sobre hábitos genéricos                                      |
| AGENTS-13 | 6     | Antes de concluir: avaliar `spec_version.md`                                           |
| AGENTS-14 | 6.4   | Avaliar elevação ao catálogo ao alterar `_dev/spec_*.md`                               |
| AGENTS-15 | 7     | Não implementar silenciosamente trecho contraditório                                   |
| AGENTS-16 | 5     | Variável nova → inventário em `spec_conventions.md`                                    |
| AGENTS-17 | 10    | Protocolo `*_new.md` só em `_dev/` do catálogo                                         |
| AGENTS-18 | 10.3  | Não substituir local inteiro pelo `_new` sem pedido explícito                          |
| AGENTS-19 | 10.4  | Não publicar no catálogo canónico sem pedido explícito                                 |
| AGENTS-20 | 6     | Bump de versão: sugerir tag Git; inventário em `spec_<nome-repo>.md` (**CONV-07**)     |
| AGENTS-21 | 1.4   | Artefatos padrão sugeridos na raiz (README, CHANGELOG, manifest)                       |
| AGENTS-22 | 1.3   | Recomendado: `spec_<nome-repo>.md` para especificidades SDD do repo (secções por tema) |
| AGENTS-23 | 1.5   | Papéis distintos de cada `README.md` (raiz, `_dev/`, maduro)                           |
| AGENTS-24 | 8     | Toolkit CLI hierárquica: domínio + verbo (**CONV-26**, **CONV-28**)                    |
| AGENTS-25 | 1.2   | Overrides locais só em `spec_<nome-repo>.md`; prevalecem sobre catálogo sync           |
| AGENTS-26 | 1.3   | `spec_*.md` em `_dev/` fora do manifest = domínio local; não confundir com sync        |
| AGENTS-27 | 2     | Assistente orienta termos técnicos mais precisos quando o operador usar termos vagos   |

### `COMMITS` — [`spec_commits.md`](spec_commits.md)

| ID         | Seção   | Resumo                                                                      |
| ---------- | ------- | --------------------------------------------------------------------------- |
| COMMITS-01 | 1       | Modo sugestão padrão; IA não executa Git sem autorização                    |
| COMMITS-02 | 1.1     | Pedidos genéricos de commit → só protocolo de sugestão                      |
| COMMITS-03 | 1.2     | Execução real só com pedido explícito e confirmação clicável                |
| COMMITS-04 | 1.3     | Encerramento da sugestão com opções clicáveis (obrigatório)                 |
| COMMITS-05 | 3       | Título e corpo em **inglês** (catálogo); overrides em `spec_<nome-repo>.md` |
| COMMITS-06 | 3.2     | Não inventar linhas `See`; copiar só de `_dev/_dev.md`                      |
| COMMITS-07 | 3.8     | Diff só de spec → tipo `docs`, não `feat`                                   |
| COMMITS-08 | 6       | Não sugerir `git add` de credenciais                                        |
| COMMITS-09 | 6       | Não executar `dev-td-up` sem pedido explícito                               |
| COMMITS-10 | (obj.)  | Contrato maduro de commits prevalece sobre cópia em `_dev/`                 |
| COMMITS-11 | 3.3     | Evitar IDs transitórios de `_dev/spec_*` em commits                         |
| COMMITS-12 | 3.4     | Actualizar `CHANGELOG.md` `[Unreleased]` com a implementação                |
| COMMITS-13 | 3.5     | Causa vs `Impact:` — trailer de impacto user-facing                         |
| COMMITS-14 | 3.6–3.7 | Trailers `Changelog-*` só quando heurísticas não bastam                     |

### `ISSUES` — [`spec_issues.md`](spec_issues.md)

| ID        | Seção  | Resumo                                                                      |
| --------- | ------ | --------------------------------------------------------------------------- |
| ISSUES-01 | 1      | Antes de criar issue: ler padrão em `.github/issues/`                       |
| ISSUES-02 | 2.1    | Título em sentence case                                                     |
| ISSUES-03 | 2.2    | Seguir prefixo temático do repo (ex. `(scope) - …`)                         |
| ISSUES-04 | 2.1    | Não usar título inteiro em CAIXA ALTA                                       |
| ISSUES-05 | 3      | Título e corpo em **inglês** (catálogo); overrides em `spec_<nome-repo>.md` |
| ISSUES-06 | (obj.) | Contrato maduro de issues prevalece sobre `_dev/`                           |
| ISSUES-07 | 1.2    | Nome de arquivo local alinhado a `.github/issues/`                          |
| ISSUES-08 | 4      | Referenciar issue no commit conforme spec de commits                        |

### `CONV` — este arquivo

| ID      | Seção | Resumo                                                                                   |
| ------- | ----- | ---------------------------------------------------------------------------------------- |
| CONV-01 | 3     | Estrutura ao registrar convenção transversal                                             |
| CONV-02 | 4     | Inventário canônico de variáveis aqui                                                    |
| CONV-03 | 4     | Não duplicar default já definido no inventário                                           |
| CONV-04 | 2     | Manter índice completo ao criar/alterar IDs                                              |
| CONV-05 | 5     | Elevar modelo compartilhado ao upstream                                                  |
| CONV-06 | 7     | Nomenclatura de tags Git: prefixo `v` + SemVer                                           |
| CONV-07 | 7     | Inventário de tags em `spec_<nome-repo>.md` ou contrato maduro — **não** em entrada sync |
| CONV-08 | 6     | Entry shell: ordem de blocos no `<tool>.sh` sourced                                      |
| CONV-09 | 6     | Entry shell: orchestrator `<tool>()`, não `main()`                                       |
| CONV-10 | 6     | Entry shell: helpers privados `_<tool>_*`                                                |
| CONV-11 | 6     | Entry shell: `_<tool>_normalize_action`                                                  |
| CONV-12 | 6.5   | Entry shell: help `help`/`-h`/`--help` → canônica `help`                                 |
| CONV-13 | 6     | Entry shell: `_<tool>_show_help`                                                         |
| CONV-14 | 6     | Entry shell: `<tool>-h` só no profile, não no entry                                      |
| CONV-15 | 6     | Entry shell: script executável vs sourced                                                |
| CONV-16 | 6.2   | Entry shell: shebang `#!/usr/bin/env bash`                                               |
| CONV-17 | 6.9   | Entry shell: entry enxuto, libs e harmonização normalize → delegate                      |
| CONV-18 | 1.3   | Toolkit: `spec_<module>.md` por script; hub `spec_<tool>.md`                             |
| CONV-19 | 8     | Migrations: âmbito e propósito                                                           |
| CONV-20 | 8.1   | Migrations: quando usar (deprecação de layout esperado)                                  |
| CONV-21 | 8.2   | Migrations: onde e como implementar                                                      |
| CONV-22 | 8.3   | Migrations: regras operacionais (idempotência, confirmação, registo)                     |
| CONV-23 | 8.4   | Migrations: documentação por ferramenta                                                  |
| CONV-24 | 8.5   | Migrations: orientação para IA ao deprecar layout                                        |
| CONV-25 | 6.10  | Prompts interativos de scripts toolkit em **inglês** (**AGENTS-08**)                     |
| CONV-26 | 6.11  | CLI hierárquica: domínio + verbo; normalizers; help em camadas (**AGENTS-24**)           |
| CONV-27 | 6.12  | Domínio `prompt` / `prm` para ficheiros `_dev/.prm_*.md` (**AGENTS-24**)                 |
| CONV-28 | 6.13  | Flags CLI: booleanas componíveis, ordem livre após verbo; shell → Python (**AGENTS-24**) |

### `VERSION` — [`spec_version.md`](spec_version.md)

| ID         | Seção | Resumo                                                                        |
| ---------- | ----- | ----------------------------------------------------------------------------- |
| VERSION-01 | 3     | Antes de concluir tarefa com alterações: avaliar impacto SemVer               |
| VERSION-02 | 3     | MAJOR / MINOR / PATCH conforme tabela                                         |
| VERSION-03 | 1     | Catálogo: `version:` primário + `areas.<entry>` no manifesto                  |
| VERSION-04 | 4     | Precedência de pastas ao decidir qual spec mudou                              |
| VERSION-05 | 4.4   | Alteração em `_dev/spec_*`: projeto vs elevável (**AGENTS-14**)               |
| VERSION-06 | 4     | Promoção `_dev/` → contrato maduro: revisar versionamento                     |
| VERSION-07 | 7     | Bump de versão: sugerir comando `git tag` ao operador                         |
| VERSION-08 | 7     | Não executar `git tag`/`git push` de tag sem pedido explícito                 |
| VERSION-09 | 8     | `CHANGELOG.md` `[Unreleased]` alinhado a tags e pré-releases                  |
| VERSION-14 | 8.6   | Estrutura Keep a Changelog: versão × tipo; bullets de impacto; sufixo de data |
| VERSION-15 | 8.7   | Perfil lockstep (adotado): fechar seção no bump, no mesmo commit              |
| VERSION-16 | 8.8   | Seções publicadas imutáveis; destino dos bullets                              |
| VERSION-17 | 8.6   | Sufixo `(N)` quando a mesma data aparece em mais de uma seção                 |
| VERSION-10 | 9     | Manifesto multinível: `version` ≥ qualquer outro campo SemVer                 |
| VERSION-11 | 9.3   | Entrada de grupo filho ≤ agregador homônimo em `areas.*`                      |
| VERSION-12 | 9.6   | Nome da seção YAML do grupo filho = chave do agregador pai                    |
| VERSION-13 | 9.7   | Propagação simétrica de bump por magnitude SemVer no manifesto                |

---

## 3. Como registrar uma convenção

Em **`spec_conventions.md`** (em `docs/specs/`, `specs/` na raiz ou `_dev/`, conforme o layout), cada convenção transversal **deve** ter **(CONV-01)**:

1. **Definição** — o que o padrão cobre e o que fica de fora (uma frase + critérios).
2. **Onde vale** — pasta ou grupo de arquivos (ex.: `toolkit/gtt/specs/`, `apps/core/code_*.py`).
3. **Tabela espelho** (quando houver contrato + código) — artefato ↔ módulo ↔ campos.
4. **Inventário** — lista atual de membros da família (atualizar ao criar ou renomear).
5. **Regra de manutenção** — «ao acrescentar X, criar Y e linha na tabela/inventário»; specs funcionais só citam **caminhos** ou **IDs**.

---

## 4. Orquestração de configuração e variáveis

**Registre aqui** as definições canônicas de variáveis de ambiente, paths padrão, URLs e aliases de shell que vários scripts compartilham. **(CONV-02)**

**Quem altera o projeto:** [`spec_agents.md`](spec_agents.md) § **5** (**AGENTS-16**).

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

## 5. Manutenção

Alterações **só deste projeto** (consumidor): registar em **`_dev/spec_<nome-repo>.md`** (secção correspondente — **AGENTS-22**, **AGENTS-25**) e/ou em contrato maduro `docs/specs/` ou `specs/` (`spec_conventions.md` ou ficheiro equivalente). **Não** editar entradas sync do manifest em `_dev/` (`spec_conventions.md`, `spec_commits.md`, …). Commitar conforme a norma de commits em vigor.

Alterações ao **modelo compartilhado** do catálogo: elevar ao repositório canônico (`docs/spec_conventions.md` upstream) — **(CONV-05)** / **AGENTS-14**.

Ao acrescentar norma citável neste arquivo: próximo `CONV-NN` livre; atualizar § **2** e o índice em **Como citar**.

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

### 6.2 Ordem de blocos no ficheiro **(CONV-08)**

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

**Shebang (CONV-16):** a primeira linha **deve** ser `#!/usr/bin/env bash` (localiza `bash` via `PATH`; [Google Shell Style Guide](https://google.github.io/styleguide/shellguide.html)). **Não** usar `#!/bin/bash` salvo restrição explícita documentada em `spec_<tool>.md` do projeto.

### 6.3 Função entry pública **(CONV-09)**

- Orchestrator **deve** chamar-se como a ferramenta: `gtt()`, `sdd()`, …
- **Não deve** usar `main()` em scripts sourced.

| Python                       | Shell sourced                    |
| ---------------------------- | -------------------------------- |
| `def main():`                | `<tool>() { … }`                 |
| `if __name__ == "__main__":` | profile: `source …/<tool>.sh`    |
| imports / setup              | bootstrap `source` + `_<tool>_*` |

Corpo mínimo: config local → zero-args/help → `_<tool>_normalize_action` + `shift` → `case` só com canónicas → delegar.

### 6.4 Helpers privados **(CONV-10)**

| Padrão            | Uso                                 |
| ----------------- | ----------------------------------- |
| `_<tool>_<verbo>` | Função privada (runtime, bootstrap) |
| `<tool>_<verbo>`  | Função pública em lib sourced       |

### 6.5 Normalização de comandos **(CONV-11)**

Função **`_<tool>_normalize_action`**: primeiro token → ação canónica (stdout). Aliases na spec `<tool>`; dispatch sem aliases duplicados. Ferramentas hierárquicas usam também **`_<tool>_normalize_domain`** e **`_<tool>_normalize_verb`** (**CONV-26**); `_normalize_action` pode ser alias de `_normalize_verb` para o parser legado.

#### Help na normalização **(CONV-12)**

| Alias aceite | Canônica |
| ------------ | -------- |
| `help`       | `help`   |
| `-h`         | `help`   |
| `--help`     | `help`   |

Dispatch: `help)` → `_<tool>_show_help`. **Não** usar `-h` como canónica interna.

### 6.6 Help **(CONV-13)**

Implementação: `_<tool>_show_help` no entry. Texto e aliases longos: `spec_<tool>.md`.

### 6.7 Atalhos `<tool>-h` e profile **(CONV-14)**

`help` / `-h` / `--help` resolvem **no entry**. Atalhos `gtt-h`, `sdd-h`, etc. **só no profile** — ex.: `gtt-h() { gtt --help; }`.

### 6.8 Executável vs sourced **(CONV-15)**

Sourced + `<tool>()` para CLI via profile; `main "$@"` para invocação directa; `return 0` se sourced quando o ficheiro serve também como lib.

### 6.9 Entry enxuto, libs e harmonização **(CONV-17)**

O `<tool>.sh` é **orquestrador**: bootstrap, normalização, help e `case` de dispatch. **Não** concentra lógica de domínio pesada.

| O quê                            | Onde vive                                                 | Agrupamento                                                  |
| -------------------------------- | --------------------------------------------------------- | ------------------------------------------------------------ |
| Alias → canónica                 | `_<tool>_normalize_action` (entry ou lib sourced)         | Tabela de aliases — não é “um ficheiro por token”            |
| Dispatch                         | `<tool>() { … }`                                          | Um ramo `case` por **ação canónica**                         |
| Lógica shell reutilizável        | `*.sh` sourced no bootstrap (`nav.sh`, `git_admin.sh`, …) | Por **domínio/cohesão**, não por flag CLI                    |
| Lógica complexa (IO, API, menus) | Python (`_<tool>_run_python`, módulos por área)           | Subcomando alinhado à canónica quando a complexidade o exige |

**Harmonização normalize → delegate:** cada ação canónica emitida por `_<tool>_normalize_action` **deve** corresponder a **exactamente um** destino no orchestrator (função pública em lib, `_<tool>_run_python <módulo> …`, ou helper runtime). A tabela canónica → delegate e o índice de módulos vivem em `spec_<tool>.md`; comportamento detalhado de cada módulo em `spec_<stem>.md` (**CONV-18**).

Exemplos:

| Canónica         | Delegate                             |
| ---------------- | ------------------------------------ |
| `gtt` `-is-pull` | `_gtt_run_python issues_sync pull …` |
| `sdd` `pull`     | `_sdd_run_python sync pull "$key" …` |

**Quando extrair do entry** (para ficheiro sourced separado):

- função ou bloco **reutilizado** por mais de um ramo do dispatch;
- normalizer, help ou runtime **dominam** o ficheiro (orientação: ~40 linhas ou mais de lógica não-dispatch);
- lib já existente é o domínio natural (ex.: mover helpers de branches para `branches.sh`).

**Não** é obrigatório — nem recomendado por defeito — um ficheiro shell **por ação CLI**. Tabelas de alias curtas permanecem no normalizer; a implementação vai para lib shell ou Python conforme a complexidade. Um ficheiro só para `_<tool>_normalize_action` é opcional quando o entry ficar grande demais (ex.: `normalize.sh` sourced no bootstrap).

**Referência:** `computer-setup/toolkit/gtt/gtt.sh`; spec funcional `toolkit/gtt/specs/spec_gtt.md`.

### 6.10 Prompts interativos (CLI) **(CONV-25)**

Mensagens exibidas ao operador por scripts em `toolkit/<tool>/` (Python, shell, ou módulos invocados pelo entry) **devem** estar em **inglês**: títulos de diálogo, perguntas `Y/n`, rótulos de tabela, avisos (`⚠️`), confirmações e texto de ajuda embutido no fluxo interativo. **(CONV-25)**

| Camada                                                           | Idioma                                  | Exemplos                                     |
| ---------------------------------------------------------------- | --------------------------------------- | -------------------------------------------- |
| Specs normativas do catálogo (`docs/`) e cópias `_dev/spec_*.md` | Português (instruções ao desenvolvedor) | Este arquivo                                 |
| Specs temáticas do consumidor (`toolkit/<tool>/specs/`)          | Conforme o projeto                      | Podem ser PT-BR                              |
| Código e comentários em scripts                                  | Inglês                                  | **AGENTS-08**                                |
| **Caixas de diálogo / prompts CLI**                              | **Inglês**                              | `Confirm? [Y/n]:`, `Start release workflow?` |
| Mensagens de **commit** sugeridas pelo script                    | Conforme `spec_commits.md`              | Em geral inglês (`docs(manifest): …`)        |

Specs temáticas em português **não** autorizam prompts em português no código. Ao documentar fluxos interativos na spec do módulo, descrever o **texto em inglês** que o script exibe.

### 6.11 CLI hierárquica (`<tool> <domínio> <verbo>`) **(CONV-26)**

Ferramentas com vários fluxos (sync, prompts, navegação, …) **devem** adoptar gramática explícita **domínio + verbo**, documentada em `toolkit/<tool>/specs/spec_<tool>.md` § **Gramática do CLI**. **(AGENTS-24)**

| Peça        | Regra                                                                                 |
| ----------- | ------------------------------------------------------------------------------------- |
| **Forma**   | `<tool> [<domínio>] [<verbo>] [args...] [flags...]` — flags: § **6.13** (**CONV-28**) |
| **Domínio** | substantivo **singular** canónico (`issue`, `sync`, `prompt`, …)                      |
| **Verbo**   | token **sem hífen** (`open`, `pull`, `check`, …)                                      |
| **Default** | verbo implícito por domínio quando omitido (tabela na spec do tool)                   |
| **Aliases** | no normalizer apenas; dispatch usa só pares canónicos                                 |

**Normalizers (shell):**

| Função                     | Papel                                                              |
| -------------------------- | ------------------------------------------------------------------ |
| `_<tool>_normalize_domain` | primeiro token → domínio canónico ou vazio                         |
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

**Evitar:** prefixos legados `-pl`/`-ps` como forma *preferida* em specs novas — mapear para o verbo canónico, mas aceitar no normalizer durante transição. **Evitar** reutilizar `ci` como domínio quando `gtt` já o reserva para `commit`.

**Help em camadas (**CONV-13** estendido):** `_<tool>_show_help_global`, `_<tool>_show_help_domain`; opcional `_<tool>_show_help_verb` por domínio complexo (`gtt`).

### 6.12 Domínio `prompt` — ficheiros para agente IA (`_dev/.prm_*.md`) **(CONV-27)**

Ferramentas que geram **templates de prompt** para assistentes de IA (Cursor / Composer) **devem** registar cada artefacto no domínio canónico **`prompt`** (alias de domínio **`prm`**), não como verbo de outro domínio nem flag CLI. **(AGENTS-24)**

| Regra             | Detalhe                                                                                                                        |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Entrada**       | `<tool> prompt` ou `<tool> prm` (sem target) → verbo implícito **`all`** → grava **todos** os prompts registados na ferramenta |
| **Target**        | `<tool> prompt <target>` → um ficheiro (ex.: `mytool prompt commit`)                                                           |
| **Registry**      | Mapa em Python `{ target → (_dev/.prm_….md, template) }`; fonte de verdade do CLI                                              |
| **Git**           | Ficheiros `.prm_*` em `_dev/` — gitignored via `_dev/*`; não commitar no consumidor salvo decisão explícita                    |
| **Idioma**        | Corpo do template em **inglês** (**CONV-25**, **AGENTS-08**)                                                                   |
| **Novos prompts** | Entrada no registry + linha na spec do módulo (`spec_prompt.md` ou § equivalente em `spec_<tool>.md`)                          |
| **Legado**        | Formas antigas de invocação **podem** redireccionar com aviso stderr durante transição                                         |

**Orquestração entre tools:** compositores que invocam `<tool> prompt all` de dependências **não devem** duplicar templates — registar na spec do compositor no consumidor.

### 6.13 Flags CLI (booleanas e composição) **(CONV-28)**

Complementa **CONV-26** com semântica de **flags** em CLIs hierárquicas (`<tool> [<domínio>] [<verbo>] …`). Comportamento por verbo e combinações exclusivas ficam na spec do módulo (`toolkit/<tool>/specs/spec_<module>.md`); aqui só o contrato transversal.

| Regra                     | Detalhe                                                                                                                                                                      |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Posição**               | Flags aplicam-se ao **verbo resolvido**. Forma canónica documentada: argumentos posicionais do verbo (se houver), depois flags. Ordem **livre entre flags** componíveis.     |
| **Booleanas componíveis** | Flags independentes (`action="store_true"`) **podem** acumular: activar várias no mesmo comando sem ambiguidade.                                                             |
| **Forma longa**           | Canónica em help e specs: `--verbose`, `--dry-run`.                                                                                                                          |
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

---

## 7. Tags Git de release (nomenclatura e registro)

Tags Git marcam **um commit** como release publicável. Bump em `manifest.yaml` e entrada em `CHANGELOG.md` **não** criam tag automaticamente — ver [`spec_version.md`](spec_version.md) § **7**.

### 7.1 Nomenclatura canônica **(CONV-06)**

| Regra                      | Detalhe                                                                                                                                              |
| -------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Formato**                | `v` + SemVer do manifesto ou changelog do repositório — ex.: versão `2.1.0` → tag **`v2.1.0`**                                                       |
| **Alinhamento**            | O nome da tag **deve** coincidir com o campo `version` em `manifest.yaml` (ou versão declarada em `CHANGELOG.md` quando o projeto não usa manifesto) |
| **Tipo**                   | Preferir tag **anotada** (`git tag -a … -m …`); tags leves só se o projeto registrar isso explicitamente                                             |
| **Branch**                 | Releases oficiais na branch estável — em geral **`main`** (ou valor de `defaults.branch` no manifesto do catálogo)                                   |
| **Pré-release** (opcional) | `vX.Y.Z-alpha.N`, `vX.Y.Z-beta.N`, `vX.Y.Z-rc.N` — candidatura antes da estável; ver [`spec_version.md`](spec_version.md) § **8** (**VERSION-09**)   |
| **Proibido**               | Reutilizar o mesmo nome de tag para outro commit (`git tag -f`) em release já publicada no remoto                                                    |

Exemplos válidos: `v1.2.0`, `v2.0.0`, `v2.1.0-rc.1`.

### 7.2 Inventário por projeto **(CONV-07)**

Cada repositório que publica releases **deve** manter tabela **Inventário de tags Git** actualizada **sempre que** uma tag de release for criada ou quando o assistente orientar o operador a criá-la após bump de versão.

**Onde registar (precedência):**

| Destino                                                                | Quando                                                                                                                                                                                                                                      |
| ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`_dev/spec_<nome-repo>.md`** § **Convenções** ou § **Versionamento** | **Sempre** no consumidor — subsecção **Inventário de tags Git** (**AGENTS-22**, **AGENTS-25**). Criar o ficheiro ou a secção se ainda não existirem.                                                                                        |
| Contrato maduro `docs/specs/` ou `specs/` (raiz)                       | `spec_conventions.md` ou ficheiro **equivalente** na mesma pasta (objectivo semelhante — layout, escopos, inventário). **Complementa** o repo-spec; **não** substitui a secção em `spec_<nome-repo>.md` enquanto o consumidor usar `_dev/`. |
| **`_dev/spec_conventions.md`** (sync do manifest)                      | **Proibido** — entrada read-only do catálogo; **não** recebe especificidades locais (**AGENTS-03**, **AGENTS-25**).                                                                                                                         |

| Coluna     | Conteúdo                                                  |
| ---------- | --------------------------------------------------------- |
| **Tag**    | Nome exato — ex.: `v1.2.0`                                |
| **Versão** | Valor SemVer (espelho do manifesto/changelog)             |
| **Branch** | Branch onde a tag foi (ou será) aplicada — ex.: `main`    |
| **Data**   | ISO `YYYY-MM-DD` da release (ou data prevista ao sugerir) |
| **Notas**  | Resumo opcional — ex.: «MAJOR: upstream em `docs/`»       |

**Regra de manutenção:** ao sugerir ou registrar uma tag, o assistente **deve** acrescentar ou actualizar a linha correspondente no inventário **no mesmo PR/tarefa** que alterou `manifest.yaml`, `CHANGELOG.md` ou norma de versionamento — em **`spec_<nome-repo>.md`** (secção correspondente) e, se existir contrato maduro de convenções, também lá. O operador humano executa `git tag` e `git push` — ver **VERSION-07** / **VERSION-08** e **AGENTS-20**.

**Modelo (substituir pelos dados do projeto):**

| Tag              | Versão  | Branch | Data         | Notas                       |
| ---------------- | ------- | ------ | ------------ | --------------------------- |
| *(ex.)* `v1.0.0` | `1.0.0` | `main` | `2026-01-01` | Primeira release versionada |

---

## 8. Migrations (evolução de layout esperado) **(CONV-19**–**CONV-24)**

Norma transversal para **scripts de instalação**, **ferramentas CLI** e **bootstrap** que alteram paths, ficheiros, chaves de manifesto ou variáveis que o consumidor já pode ter no ambiente ou no repositório.

O termo **migration** neste catálogo **não** designa migrations de base de dados: designa **passos one-shot e idempotentes** que adaptam estado **legado** ao layout **actual** esperado pelo código.

Complementa [`spec_version.md`](spec_version.md) (quando comunicar breaking change) — **não** o substitui.

### 8.1 Âmbito e propósito **(CONV-19)**

| Conceito            | Significado                                                                                    |
| ------------------- | ---------------------------------------------------------------------------------------------- |
| **Layout esperado** | Paths, nomes de ficheiro, chaves de configuração ou metadado que o código **actual** assume    |
| **Estado legado**   | Artefacto ainda presente de versão anterior (pasta obsoleta, ficheiro renomeado, chave antiga) |
| **Migration**       | Detecção + adaptação do legado → layout esperado, antes ou durante o fluxo principal           |

**Propósito:** evitar que o utilizador fique bloqueado após evoluir o script ou a ferramenta; reduzir deriva silenciosa entre máquinas ou clones antigos e o contrato novo.

### 8.2 Quando usar **(CONV-20)**

Registar migration quando uma evolução **depreca** algo que o consumidor **pode já ter**:

- path ou pasta substituída (ex.: scripts deixam de viver numa cópia em `$HOME` e passam a viver no repositório);
- rename de ficheiro downstream ou upstream;
- rename ou remoção de chave em manifesto ou ficheiro de metadado de sync;
- variável ou ficheiro de configuração substituído por outro mecanismo.

**Não** usar migrations para:

- lógica de negócio recorrente (sync, pull, menu);
- correcções que não dependem de estado legado do consumidor;
- substituir bump SemVer ou comunicação de breaking change.

### 8.3 Onde e como implementar **(CONV-21)**

| Contexto                   | Padrão sugerido                                                                     |
| -------------------------- | ----------------------------------------------------------------------------------- |
| **Instalador / bootstrap** | bloco `run_migrations` (ou equivalente) invocado **antes** de activar o layout novo |
| **Ferramenta CLI**         | `migrations.py`, `migrations.sh` ou secção dedicada sourced pelo entry              |
| **Ordem de execução**      | migrations **antes** do fluxo que assume o layout actual (sync, install, dispatch)  |

**Registo ordenado:** manter lista explícita de migrations (tuple, array ou funções registadas em sequência). Cada entrada **deve** poder correr isolada e **deve** documentar o que detecta e o que altera.

**Esqueleto comum:**

```text
1. Detectar legado (path existe, chave antiga, ficheiro com nome obsoleto)
2. Se ausente → skip (idempotente)
3. Explicar ao operador o que mudou e o que será feito
4. Confirmar (salvo flag --yes documentada)
5. Aplicar (rename, remove, regravar metadado, commit sugerido)
6. Nunca repetir se o layout já está actual
```

Separar migrations da lógica principal — não intercalar adaptações legadas no meio de menus ou sync.

### 8.4 Regras operacionais **(CONV-22)**

| Regra                     | Detalhe                                                                                                                 |
| ------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| **Idempotência**          | Segunda execução **não deve** re-aplicar nem falhar se já migrado                                                       |
| **Detecção primeiro**     | Só actuar quando o legado estiver presente                                                                              |
| **Confirmação**           | Acções destrutivas ou irreversíveis: prompt `[y/N]` por defeito; `--yes` / `-y` só se documentado na spec da ferramenta |
| **Mensagens claras**      | Indicar **o quê** era esperado antes, **o quê** passa a valer, **o quê** será alterado                                  |
| **Destrutivo vs. rename** | Remover artefacto obsoleto ≠ renomear ficheiro tracked — documentar risco distinto                                      |
| **Git**                   | Se migration altera ficheiros versionados, prever subject de commit padrão e confirmação de mensagem                    |
| **Falha segura**          | Cancelamento do operador **não deve** corromper estado; fluxo principal pode continuar ou abortar de forma explícita    |

### 8.5 Documentação **(CONV-23)**

- Regra geral: **este § 8**.
- Por ferramenta (**CONV-18**): `spec_migrations.md` ou secção **Migrations** no spec do módulo `migrations.*`, listando cada migration registada (detecção, acção, confirmação, commit sugerido).
- Hub `spec_<tool>.md`: indicar que migrations correm antes do fluxo principal e apontar para o spec de migrations.

Ao adicionar migration nova, actualizar o spec **no mesmo PR/tarefa** que altera o código.

### 8.6 Orientação para IA **(CONV-24)**

Ao **deprecar** layout, path, chave ou variável que consumidores possam já ter:

1. **Registar** migration idempotente conforme § **8.3**–**8.4**.
2. **Documentar** no spec da ferramenta (§ **8.5**).
3. **Avaliar** impacto SemVer em [`spec_version.md`](spec_version.md) — migration não dispensa comunicação de breaking change quando aplicável.
4. **Não assumir** que o ambiente ou clone já está no layout novo.
5. **Não** remover suporte ao legado sem migration ou período de detecção documentado, salvo pedido explícito do mantenedor.

