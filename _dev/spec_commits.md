# Convenção de mensagens de commit (Semantic Commits)

Normas de staging e mensagens para repositórios que adotam specs compartilhados. **Baseline do catálogo:** mensagens em **inglês** (§ **3**). Overrides locais (ex. PT-BR) em `_dev/spec_<nome-repo>.md` § **Commits** — **AGENTS-22**, **AGENTS-25**.

## Objetivo

Commits neste repositório seguem **[Conventional Commits](https://www.conventionalcommits.org/)**
adaptado a este repositório (setup de ambiente, aplicações, etc.).

**Idioma deste arquivo:** português (instruções a quem desenvolve no projeto). **Idioma das mensagens de commit:** inglês (§ **3**).

**Desenvolvedor (terminal / GUI Git):** seguir estrutura, tipos, escopos e staging deste documento ao commitar manualmente.

**Assistente de IA na IDE:** o trabalho padrão é **sugerir** (`git add`, mensagens, comandos copy-paste) — **não** executar `git commit`, `git push` nem equivalentes “por detrás do pano”. Execução real só após pedido **explícito** do desenvolvedor e confirmação com opções clicáveis (§ **1.2**; **COMMITS-03**; ver também **AGENTS-11**).

**Nota:** atalhos como `dev-td-up` (ex. em `toolkit/dev/dev.sh` no consumidor) podem usar mensagem legada `dev(toDo): update`; commits manuais e sugestões na IDE devem seguir **este documento**, não esse atalho — salvo quando o desenvolvedor pedir explicitamente o fluxo do atalho.

**Onde esta norma vale no projeto**

| Situação                                            | Arquivo                                                                                         |
| --------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| Sync do catálogo (`sdd … -pl`)                      | `_dev/spec_commits.md` — cópia **read-only** deste documento; **não editar** para regras locais |
| Overrides deste repositório                         | `_dev/spec_<nome-repo>.md` § **Commits** — prevalece sobre o catálogo (**AGENTS-25**)           |
| Contrato maduro em `docs/specs/` ou `specs/` (raiz) | Regras de commit do projeto nessa pasta **prevalecem** sobre `_dev/`. **(COMMITS-10)**          |

Precedência: [`spec_agents.md`](spec_agents.md) § **1.2** (**AGENTS-02**–**05**, **AGENTS-25**).

## Referências

Os principais **conceitos**, **autores**, **metodologias** e **referências externas** que orientam **como construir commits** neste catálogo são:

???+ note "Conventional Commits"

    Formato **`<tipo>[escopo opcional]: <descrição>`** com corpo e rodapés opcionais. Tipos (`feat`, `fix`, `docs`, `chore`, …) e escopos deste repositório estendem a especificação para SDD (`spec_*.md`, `toolkit/<tool>/`, etc.). O **`!`** após o tipo/escopo ou o rodapé **`BREAKING CHANGE:`** sinalizam mudança incompatível — alinhado a SemVer (ver [`spec_version.md`](spec_version.md)).

    **Referências externas**

    - [Conventional Commits 1.0.0](https://www.conventionalcommits.org/) — especificação oficial (estrutura, tipos, breaking changes).
    - [Angular commit message guidelines](https://github.com/angular/angular/blob/main/CONTRIBUTING.md#commit) — origem histórica do formato de mensagens.
    - [Conventional Commits — FAQ](https://www.conventionalcommits.org/en/v1.0.0/#faq) — escopo, corpo, rodapés e relação com versionamento.

??? abstract "Mensagens legíveis e histórico Git"

    Commits são **documentação permanente** do repositório: título infinitivo impessoal, linha de assunto curta, corpo explicando *porquê* (não só *o quê*). Boas mensagens facilitam `git log`, revisão de PR e geração de changelog.

    **Referências externas**

    - [How to Write a Git Commit Message](https://cbea.ms/git-commit/) — Chris Beams; regra dos 50/72 caracteres, imperativo, contexto no corpo.
    - [Git Book — Contributing: Commit Guidelines](https://git-scm.com/book/en/v2/Distributed-Git-Contributing-to-a-Project#_commit_guidelines) — visão geral do ecossistema Git.

??? tip "Commits atômicos e staging"

    Um commit deve representar **uma mudança lógica** revisável (facilita bisect, revert e revisão). O **staging** seletivo (`git add` por arquivo/hunk) evita misturar refatoração, spec e ruído. Esta spec define **como** sugerir `git add` e separar commits (ex.: `docs` vs `feat`, `toDo` isolado).

    **Referências externas**

    - [Git Tools — Staging](https://git-scm.com/book/en/v2/Git-Tools-Revision-Selection#_interactive_staging) — staging parcial e hunks.
    - [Atomic commits (discussão prática)](https://www.freshconsulting.com/insights/blog/atomic-commits/) — um propósito por commit (referência de boas práticas de equipe).

??? info "Commits com assistente de IA"

    O assistente **sugere** mensagens e comandos; o desenvolvedor **autoriza** `git commit` e `push`. Pedidos genéricos («ajuda com commit») não autorizam execução silenciosa — ver § **1** (**COMMITS-01**–**03**) e [`spec_agents.md`](spec_agents.md) § **3** (**AGENTS-10**–**12**).

    Se existirem specs em **`docs/specs/`**, **`specs/`** (raiz) e **`_dev/`**, aplicar a precedência em [`spec_agents.md`](spec_agents.md) § **1.2** antes de fixar escopo ou tipo.

    **Referências externas**

    - [Building effective agents](https://www.anthropic.com/research/building-effective-agents) — supervisão humana em loops de geração e revisão.
    - [AGENTS.md — git workflow](https://addyosmani.com/agents/15-agents-md/) — convenções de commit em instruções para agentes.

??? quote "Normas e artefatos deste catálogo"

    Detalhes operacionais (tipos, escopos, exemplos, `See`) estão **neste arquivo** e nas specs abaixo.

    - [`spec_agents.md`](spec_agents.md) — SDD, ordem de leitura, pastas de spec, gatilho de commit.
    - [`spec_conventions.md`](spec_conventions.md) — escopos, prefixos de ID, índice completo § **2**.
    - [`spec_issues.md`](spec_issues.md) — títulos e corpos de issue; consultar `.github/issues/`.
    - [`spec_version.md`](spec_version.md) — quando um commit exige bump ou comunicação de impacto.
    - `_dev/spec_<nome-repo>.md` — overrides locais de commit (idioma, escopos, exemplos).
    - `_dev/_dev.md` — linhas `See` no corpo do commit (quando existir).

??? note "Linguagem normativa e IDs"

    *Deve*/*não deve* conforme [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) — [`spec_conventions.md`](spec_conventions.md) **Referências**. IDs: prefixo **`COMMITS`**; índice completo em `spec_conventions.md` § **2**.

---

## Como citar este documento

| Mecanismo           | Uso                                                   |
| ------------------- | ----------------------------------------------------- |
| **Seção numerada**  | `§ 1.2` — navegação neste arquivo.                    |
| **ID normativo**    | `COMMITS-05` — citação estável.                       |
| **Índice completo** | [`spec_conventions.md`](spec_conventions.md) § **2**. |

**Índice de IDs deste arquivo:**

| ID         | Seção   | Resumo                                                                              |
| ---------- | ------- | ----------------------------------------------------------------------------------- |
| COMMITS-01 | 1       | Modo sugestão padrão; IA não executa Git sem autorização                            |
| COMMITS-02 | 1.1     | Pedidos genéricos → só protocolo de sugestão                                        |
| COMMITS-03 | 1.2     | Execução só com pedido explícito e confirmação clicável                             |
| COMMITS-04 | 1.3     | Encerramento da sugestão com opções clicáveis                                       |
| COMMITS-05 | 3       | Título e corpo do commit em **inglês**                                              |
| COMMITS-06 | 3.2     | Não inventar linhas `See`                                                           |
| COMMITS-07 | 3.8     | Diff só de spec → tipo `docs`, não `feat`                                           |
| COMMITS-08 | 7       | Não sugerir `git add` de credenciais                                                |
| COMMITS-09 | 7       | Não executar `dev-td-up` sem pedido explícito                                       |
| COMMITS-10 | (obj.)  | Contrato maduro de commits prevalece sobre `_dev/`                                  |
| COMMITS-11 | 3.3     | Evitar IDs transitórios de `_dev/spec_*` em commits                                 |
| COMMITS-12 | 3.4     | Sincronizar `CHANGELOG.md`: Perfil B lockstep; `[Unreleased]` ou nova seção no bump |
| COMMITS-13 | 3.5     | Causa vs `Impact:` — trailer de impacto user-facing (inglês)                        |
| COMMITS-14 | 3.6–3.7 | Trailers `Changelog-*` só quando heurísticas não bastam                             |

---

## 1. Modo sugestão (padrão) vs modo execução

| Modo         | Quando                                                                                | Assistente de IA na IDE                                      | O que **não** faz (IA)                                                 |
| ------------ | ------------------------------------------------------------------------------------- | ------------------------------------------------------------ | ---------------------------------------------------------------------- |
| **Sugestão** | Pedido genérico ou “ajuda com commit” (§ **1.1**)                                     | Protocolo § **8**; mensagens; `git add` para copiar          | `git add` / `git commit` / `git push` sem autorização **(COMMITS-01)** |
| **Execução** | Desenvolvedor **explícito**: “pode fazer o commit”, “executa o commit completo”, etc. | § **1.2** — confirmações com clique antes de correr comandos | Commitar sem confirmar qual proposta e se inclui push                  |

### 1.1 Pedidos genéricos → só protocolo de sugestão

Frases como as abaixo **não** autorizam commit real; disparam **apenas** o protocolo de sugestão
(§ **8**). **(COMMITS-02)**

- «quero ajuda com o commit»
- «me ajude com o commit»
- «vamos fazer o commit»
- «sugestão de commit», «mensagem de commit», «o que commitar», congêneres

Ao final da resposta em modo sugestão, **perguntar com opção clicável** se o desenvolvedor deseja que
a assistente de IA **execute o commit completo** (ver § **1.3**).

### 1.2 Modo execução (commit real)

Só após o desenvolvedor ser **explícito** no sentido de executar (ex.: «pode fazer o commit»,
**COMMITS-03**):
«faz o commit completo», «pode commitar»):

1. Se houve **várias propostas numeradas** (Commit A, B, …), **perguntar com clique** qual(is)
   executar — não assumir a primeira.
2. **Confirmar com opções clicáveis** (mutuamente exclusivas onde couber):
   - Executar **`git add` + `git commit`** com a mensagem acordada? (Sim / Não)
   - Executar também **`git push`**? (Sim / Não)
3. Só então correr os comandos no terminal, na ordem acordada.

Se o pedido for ambíguo («commit isso» sem ter pedido execução antes), tratar como **modo
sugestão** e oferecer execução no final com clique.

### 1.3 Encerramento da sugestão (obrigatório se não for execução)

Depois de entregar `git add` + mensagem(ns), o assistente **deve** incluir pergunta clicável (**COMMITS-04**):

- **A)** Só usar as sugestões manualmente (não executar nada na IDE)  
- **B)** Executar o commit completo na IDE (sem push)  
- **C)** Executar commit completo **e** push  

Se existirem várias propostas de commit, a pergunta deve referir **qual proposta** (A/B/C da
lista numerada) antes ou junto da escolha B/C.

---

## 2. Estrutura da mensagem

```
<tipo>(<escopo opcional>): <título — ver § 3.1>

<linhas See * — só se existirem em _dev/_dev.md; ver § 3.2>

<corpo opcional — parágrafos em inglês; detalhe do que mudou>
```

Se houver bloco `See`: linha em branco entre o título e as linhas `See`; linha em branco entre o
bloco `See` e o corpo. Sem bloco `See`: título seguido do corpo (linha em branco entre título e
corpo, se houver corpo).

## 3. Idioma das mensagens de commit

| Parte da mensagem                  | Idioma                                                                             |
| ---------------------------------- | ---------------------------------------------------------------------------------- |
| **Título** (`<tipo>(<escopo>): …`) | **Inglês**                                                                         |
| **Corpo** (após o bloco `See`)     | **Inglês**                                                                         |
| Linhas **`See …`**                 | Copiar de `_dev/_dev.md` quando existirem; **omitir** o bloco se vazio (§ **3.2**) |
| Este arquivo `spec_commits.md`     | Português (norma para quem redige commits)                                         |

Título e corpo do commit **devem** estar em **inglês** nesta baseline do catálogo, seja redação manual ou sugerida pelo assistente de IA (mesmo quando a conversa na IDE for em português). **(COMMITS-05)**

Para **outro idioma** ou regras locais (ex. PT-BR), documentar em `_dev/spec_<nome-repo>.md` § **Commits** — essa secção **prevalece** sobre este arquivo no consumidor (**AGENTS-25**).

### 3.1 Composição do título (Conventional Commits)

O título é **uma linha** com três partes:

```text
<tipo>(<escopo>): <mensagem resumida>
```

| Parte                   | Função                                                                                                                  |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| **`tipo`**              | Natureza da mudança (§ **4**) — o que o commit *é* (documentação, feature, fix, …).                                     |
| **`escopo`**            | Módulo ou tema afetado (§ **5**), entre parênteses — opcional mas recomendado.                                          |
| **`mensagem resumida`** | Texto **após** `(<escopo>): ` — o que o repositório/projeto **passa a ter ou a conseguir** se este commit for aplicado. |

**Redação em inglês (título e corpo):**

- Começar a mensagem (após `(<escopo>): `) com **verbo no imperativo** (estilo Conventional Commits):
  *add*, *fix*, *update*, *remove*, *document*, *refactoror*, …
- **Evitar** título só com substantivos sem verbo inicial.
- ≤ ~72 caracteres no título completo, quando possível.
- Corpo em inglês claro; frases completas; foco no *porquê* e no efeito — não repetir o título.

**Corpo da mensagem (após o bloco `See`):** parágrafos opcionais em **inglês**; listar arquivos ou
resumir alterações quando útil.

### 3.2 Linhas `See` e corpo

- **Quando incluir:** se **`_dev/_dev.md`** existir e tiver **uma ou mais** linhas `See …` com
  referência (issue, URL, etc.), copiar **todas** essas linhas logo abaixo do título, uma por linha.
- **Quando omitir:** se o arquivo **não existir**, estiver **vazio** ou **não contiver** nenhuma
  linha `See …` com referência, **não** colocar linha `See` na mensagem de commit — nem URL
  genérica, nem URL de placeholder da origem das normas. A mensagem fica só com título (e corpo opcional).
- **Depois do bloco `See`** (quando houver): corpo opcional (§ acima).
- **Não inventar** linhas `See` que não estejam em `_dev/_dev.md`. **(COMMITS-06)**

### 3.3 Parâmetros de `_dev/spec_*` no corpo

Quando for relevante mencionar no corpo do commit uma regra, parâmetro ou checklist que está
apenas em documentação de trabalho (`_dev/spec_*`), preferir explicar a regra em termos do
**comportamento aplicado**, sem depender do ID normativo cru ou do caminho transitório. **(COMMITS-11)**

Racional: specs em `_dev/` podem amadurecer para outro contrato, mudar de pasta, ser substituídas
ou abandonadas. A mensagem de commit deve continuar rastreável pelo efeito observado no diff, mesmo
se o ID local deixar de existir.

Exemplo preferido:

```text
fix(sdd): batch missing catalog files during check

Defer locally missing specs to one final numbered prompt instead of stopping at each per-key menu.
```

Evitar, salvo quando o commit altera a própria regra ou implementa explicitamente sua validação:

```text
Propagate the patch bump per VERSION-13.
```

### 3.4 Sincronizar `CHANGELOG.md` **(COMMITS-12)**

Quando o repositório mantém `CHANGELOG.md` ([Keep a Changelog](https://keepachangelog.com/); [`spec_version.md`](spec_version.md) § **8**, **VERSION-09**, **VERSION-14**, **VERSION-15**, **VERSION-16**):

**Perfil adotado:** **Perfil B — lockstep** (§ **8.7**). Fechar seção versionada no **mesmo commit** do bump de `version:`.

| Momento                                            | Ação                                                                                                                                                                                                                                      |
| -------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Commit de implementação sem bump de `version:`** | Acrescentar **pelo menos um** bullet em `[Unreleased]` na seção `Added` / `Changed` / `Fixed` / `Removed` / `Security` adequada — **no mesmo commit** que código, specs e `manifest.yaml` (quando alterados).                             |
| **Commit com bump de `version:`** (Perfil B)       | Criar `## [nova-versão] - AAAA-MM-DD` com os bullets dessa entrega; **não** editar seções de versões **publicadas** (**VERSION-16**); esvaziar `[Unreleased]`. Aplicar sufixo `(N)` se a data coincidir com outra seção (**VERSION-17**). |
| **Após tag `vX.Y.Z`**                              | Confirmar alinhamento manifesto ↔ tag; **não** reescrever seção já fechada no bump lockstep.                                                                                                                                              |
| **Bump só em filhos sem `version:`**               | **Alertar** inconsistência com **VERSION-13**; bullets em `[Unreleased]` até propagar.                                                                                                                                                    |
| **Auditoria**                                      | Se existem tags `vA..vZ` sem seção `## [A]`…`## [Z]` correspondente, ou bullets novos em seção **publicada**, **reconciliar** antes de nova implementação.                                                                                |

**Classificação do bullet** (alinhar ao tipo Conventional Commit quando possível):

| Tipo commit                                         | Seção changelog                                  |
| --------------------------------------------------- | ------------------------------------------------ |
| `feat`                                              | `### Added`                                      |
| `fix`                                               | `### Fixed`                                      |
| `refactor`, `perf`, `chore` (comportamento visível) | `### Changed`                                    |
| remoção de feature/CLI                              | `### Removed`                                    |
| `BREAKING CHANGE`                                   | `### Changed` + nota breaking, ou seção dedicada |

**Não** adicionar bullets só de bump de `manifest.yaml`. **Não** adiar a atualização do changelog para «depois da tag» se a implementação já está sendo commitada (Perfil B fecha no bump).

O **texto** do bullet deve refletir **impacto** user-facing (operador, CLI, profile, breaking change) — ver § **3.5** (`Impact:`). Pode coincidir com o trailer `Impact:` quando o repositório adotar esse contrato.

### 3.5 Causa vs impacto — trailer `Impact:` **(COMMITS-13)**

A mensagem de commit separa duas narrativas:

| Camada      | Onde                        | Conteúdo                                                                                                    |
| ----------- | --------------------------- | ----------------------------------------------------------------------------------------------------------- |
| **Causa**   | Título + corpo (após `See`) | O que mudou no repo e porquê — técnico, para `git log`                                                      |
| **Impacto** | Trailer **`Impact:`**       | O que o operador/consumidor **passa a ver ou a poder fazer** — candidato directo a bullet em `CHANGELOG.md` |

**Quando incluir `Impact:`** (inglês; uma linha ou frase completa):

- Commit **user-facing** (`feat`, `fix`, `refactor`/`perf`/`chore` com efeito perceptível) **e** o repo mantém `CHANGELOG.md`.
- **Omitir** em `docs`, `test`, `chore`/`ci` sem efeito de release, commits só de `manifest` anotado pós-tag, etc.

**Ordem no corpo** (após bloco `See` e corpo opcional de causa):

```text
feat(gtt): add tag list --inventory flag

Delegate TAB-2 rendering to shared list module; update spec_tags_list.md.

Impact: gtt tag list shows full version inventory with --inventory or -in.
```

**Regra para assistentes de IA:** ao propor commit, redigir **sempre** título/corpo orientados à **causa** e trailer **`Impact:`** orientado ao **efeito perceptível** — não repetir o título no `Impact:`.

### 3.6 Trailers `Changelog-*` — excepção à heurística **(COMMITS-14)**

Trailers explícitos **só** quando a secção Keep a Changelog **não** puder ser inferida com confiança a partir do tipo Conventional Commit + diff + `Impact:` (§ **3.7**).

| Trailer (inglês)      | Secção KAC     |
| --------------------- | -------------- |
| `Changelog-Added:`    | `### Added`    |
| `Changelog-Changed:`  | `### Changed`  |
| `Changelog-Fixed:`    | `### Fixed`    |
| `Changelog-Removed:`  | `### Removed`  |
| `Changelog-Security:` | `### Security` |

**Usar quando**, por exemplo:

- um commit agrupa **causas distintas** (`fix` + `feat`) que deviam ser commits separados mas o operador manteve um só;
- o tipo CC **não** reflecte a secção (ex.: `feat` que só remove API pública);
- heurísticas de diff (§ **3.7**) produziriam **secções contradictórias** sem confirmação explícita.

**Não** exigir `Changelog-Added:` / `Changelog-Removed:` quando add+delete de ficheiros servem **uma mesma finalidade** (ex.: substituir spec A por spec B num `feat`) — nesse caso basta **`Impact:`** + heurística de diff (§ **3.7**); o assistente **avalia** se a heurística cobre o commit antes de acrescentar trailers.

Formato (omitir linhas vazias):

```text
Impact: Tag listing spec split into module doc and shared list contract.

Changelog-Added: spec_tags_list.md — TAB-1/TAB-2 listing contract.
Changelog-Removed: Inline list section from spec_tags.md.
```

**Preferência:** actualizar `CHANGELOG.md` (§ **3.4**) no mesmo commit; trailers alimentam auditoria futura e geradores automáticos — não substituem o ficheiro enquanto o operador mantiver COMMITS-12.

### 3.7 Heurísticas de secção KAC (IA e geradores) **(COMMITS-14)**

Checklist para o assistente **antes** de propor trailers `Changelog-*`:

1. Tipo CC + `Impact:` bastam para **uma** secção? → só `Impact:`; secção inferida pela tabela abaixo.
2. Diff: adds e deletes no **mesmo** prefixo/path stem (substituição, rename, split doc)? → **uma** secção `Changed` **ou** par `Added`+`Removed` derivado do diff; texto do bullet vem de **`Impact:`** (não redigir de novo em `Changelog-*`).
3. Diff: adds **e** deletes com **finalidades distintas**? → preferir **split de commits**; se impossível, `Changelog-*` explícitos.
4. Tipo `docs`/`chore`/`test`/`ci` sem efeito user-facing? → **sem** entrada em changelog.

| Tipo commit (causa)                                 | Secção default (impacto)  |
| --------------------------------------------------- | ------------------------- |
| `feat`                                              | `Added`                   |
| `fix`                                               | `Fixed`                   |
| `refactor`, `perf`, `chore` (comportamento visível) | `Changed`                 |
| remoção de feature/CLI/API                          | `Removed`                 |
| `BREAKING CHANGE`                                   | `Changed` + nota breaking |

**Heurística de diff (substituição):** ficheiro **adicionado** e **removido** no mesmo commit, paths sob o mesmo prefixo funcional (`toolkit/gtt/specs/`, `setup/`, …), tipo `feat` ou `refactor` com `Impact:` único → gerador/IA pode emitir `Added`+`Removed` **ou** um bullet `Changed` agregado — **sem** trailers extra se `Impact:` descreve o efeito global.

### 3.8 Tipo vs arquivos alterados

| Diff principal                                                                                                      | Tipo usual                                      | Nota                                                                                          |
| ------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------- | --------------------------------------------------------------------------------------------- |
| Só documentação normativa (`_dev/spec_*.md`, pasta madura `docs/specs/` ou `specs/`, README descritivo), sem código | **`docs`**                                      | Mesmo que a spec descreva um processo novo — não usar `feat` só por ser “feature” conceptual. |
| Código + specs alinhadas ao mesmo comportamento                                                                     | `feat` / `fix` / `refactor` + escopo do domínio | Specs no mesmo commit quando mesma causa.                                                     |
| Só `_dev/toDo.md`                                                                                                   | **`dev`**                                       | Título fixo § **6**.                                                                          |
| Só `profile` / shell sem nova feature                                                                               | `refactor` / `chore`                            | Preferir `refactor(profile)` se só reorganizar aliases                                        |

`feat` reserva-se a mudança **implementada** em scripts ou configs com efeito claro para quem roda `install.sh` ou recarrega o shell. Diff **apenas** de documentação normativa → **`docs`**, não `feat`. **(COMMITS-07)**

---

## 4. Tipos (`<tipo>`)

| Tipo       | Quando usar                                                                                      |
| ---------- | ------------------------------------------------------------------------------------------------ |
| `feat`     | Comportamento novo ou extensão em scripts, `profile`, setups                                     |
| `fix`      | Correção de bug em código ou comportamento                                                       |
| `refactor` | Mudança interna sem alterar comportamento observável                                             |
| `docs`     | Só documentação normativa (`_dev/spec_*.md`, `docs/specs/`, `specs/` na raiz, README descritivo) |
| `dev`      | Anotações em `_dev/toDo.md` (§ **6**)                                                            |
| `test`     | Só testes (quando existirem)                                                                     |
| `chore`    | Build, deps, housekeeping, `.gitignore`, renomeação em lote                                      |

Evitar tipos genéricos quando um tipo acima couber. Não usar `feat` quando o diff for **apenas**
documentação (usar `docs`).

---

## 5. Escopo (`<escopo>`)

Opcional, em **camelCase** ou **kebab-case** quando já usado no histórico (`gtt`, `dev`, `auto-update`).
Ao sugerir escopo, seguir **nesta ordem**:

### 5.1 Aderência temática (normas compartilhadas + convenções locais)

Consultar a tabela abaixo. Em repositórios com convenções **locais**, mesclar temas do projeto (setup, profile, escopos próprios) com esta tabela — registar em **`_dev/spec_<nome-repo>.md`** § **Convenções** (**AGENTS-22**, **AGENTS-25**); se existir contrato maduro, também em `docs/specs/` ou `specs/` (`spec_conventions.md` ou ficheiro equivalente). **Não** usar `_dev/spec_conventions.md` (sync read-only) para regras locais.

| Tema do commit                                                                             | Escopo sugerido              | Tipo usual                                            |
| ------------------------------------------------------------------------------------------ | ---------------------------- | ----------------------------------------------------- |
| SDD, `spec_agents`, engenharia de contexto                                                 | `sdd`                        | `docs`                                                |
| **Neste repo** — `docs/`, `manifest.yaml`, `_dev/spec_*`, scaffold                         | `specs-catalog`              | `feat` / `docs` / `fix` conforme conteúdo             |
| Ferramenta sync (`toolkit/sdd/` no **computer-setup**)                                     | `sdd`                        | `feat` / `fix` / `docs(sdd)` (norma da ferramenta)    |
| Convenção de commits, staging (`spec_commits.md`, `spec_agents.md`)                        | `commits`                    | `docs(commits)`; `feat` só com código no mesmo commit |
| Só convenções locais (`spec_<nome-repo>.md` § Convenções; ou maduro `spec_conventions.md`) | `convencoes` / `conventions` | `docs(convencoes)` / `docs(conventions)`              |
| `install.sh`, `general-setup.sh`, `config-cross-plat.sh`                                   | `setup`                      | `feat` / `fix` / `chore`                              |
| `profile`, `zshrc`, `bashrc`, `profile_update.sh`                                          | `profile`                    | `feat` / `refactor` / `fix`                           |
| `gitconfig`, `gitignore`, `git_setup.sh`                                                   | `git`                        | `feat` / `chore`                                      |
| `settings.json`, `keybindings.json`                                                        | `editor`                     | `feat` / `chore`                                      |

### 5.2 Spec funcional que dá sentido à alteração

**Regra:** prefixo `spec_` + **primeiro segmento** até ao **segundo** `_` (ver [`spec_conventions.md`](spec_conventions.md) § **1.2**).

Specs com **apenas um** segmento após `spec_`: usar esse segmento inteiro
— ex. `spec_conventions.md` (catálogo ou maduro) → `conventions`; `spec_<nome-repo>.md` § **Convenções** → escopo local documentado nessa secção; `spec_agents.md` → `agents`.

**Rename de spec:** escopo derivado do **nome antigo** do arquivo que motivou a mudança.

### 5.3 Vários arquivos num único commit (mesma causa)

Agregar caminhos num só commit quando houver **uma causa** (ex.: introdução de
`spec_commits.md` + `spec_agents.md` + `spec_conventions.md` + `_dev.md`).

`_dev/toDo.md` no mesmo commit **só** se o desenvolvedor confirmar; por defeito, commit separado
`dev(toDo)` (§ **6**).

### 5.4 Vários temas distintos no mesmo commit

Preferir **commits separados** (§ **8**). Se o desenvolvedor insistir num único commit,
escolher escopo da causa **dominante** e mencionar no corpo o restante.

### 5.5 Sem spec nem convenção clara

Omitir escopo ou usar escopo já presente no `git log`; **não** inventar camelCase novo.

---

## 6. Commit só de `_dev/toDo.md`

Quando o desenvolvedor pedir para **atualizar a lista de tarefas** (ou o diff for essencialmente só
`_dev/toDo.md`), a mensagem sugerida é **mínima**:

```
dev(toDo): update task notes
```

(opcionalmente, linhas `See …` de `_dev/_dev.md` entre o título e o fim da mensagem — só se existirem)

- Título fixo: **`dev(toDo): update task notes`** (ajustar só se o desenvolvedor pedir outro título, em inglês).
  O histórico pode incluir timestamp (`dev(toDo): update 2026-03-12-09:21`) — alinhar ao pedido.
- Linhas **`See`:** copiar de **`_dev/_dev.md`** só se o arquivo tiver linhas `See …` com referência;
  caso contrário, **sem** bloco `See` (§ **3.2**).
- **Sem corpo** (sem parágrafos após o título ou após o bloco `See`), salvo pedido do desenvolvedor.
- `git add` sugerido: `_dev/toDo.md` (salvo o desenvolvedor pedir outros arquivos).

---

## 7. Boas práticas

- **Não** executar `git add`, `git commit` nem `git push` no modo sugestão; execução só § **1.2** (**COMMITS-01**, **COMMITS-03**).
- **Não** executar `dev-td-up` sem pedido explícito (commit+push automáticos). **(COMMITS-09)**
- **Não** sugerir `git add` de credenciais (`.env`, chaves privadas, tokens). **(COMMITS-08)**
- Para sugerir `git commit`: usar HEREDOC, ex. `git commit -m "$(cat <<'EOF' … EOF)"`.
- Mudanças em `install.sh` ou `profile`: mencionar no corpo se o desenvolvedor precisa rerodar install ou só `source`.

---

## 8. Sugestão de staging (`git add`) e commits

Quando o desenvolvedor pedir **sugestão de commit**, **o que commitar**, **git add** ou equivalente,
entregar um **pacote revisável**: staging proposto + mensagem(ns).

### 8.1 Passo 1 — Inventariar alterações

1. `git status --short` e diff por arquivo relevante.
2. Classificar: **código** (`toolkit/<tool>/`, `setup/`, …), **specs** (`_dev/`, `docs/specs/`, `specs/`, `toolkit/<tool>/specs/`), **`profile` / setups**, **`_dev/toDo.md`**, ruído.
3. Ligar cada grupo ao tema (§ **5**).

### 8.2 Passo 2 — Propor um ou mais commits

Um commit por **causa** coerente. Cada proposta com: arquivos → resumo → `git add` → mensagem.

**Exemplo — SDD inicial** *(nomenclatura histórica `spec_convencoes`; hoje sync `spec_conventions.md`; regras locais do consumidor → `spec_<nome-repo>.md`)*:

```bash
git add _dev/_dev.md _dev/spec_agents.md _dev/spec_commits.md _dev/spec_conventions.md .gitignore
```

```
docs(sdd): add basic SDD and commit specifications

See https://github.com/carloshob/specs-catalog

Introduce spec_agents, spec_commits, and spec_conventions (catalog sync); _dev.md with See lines.
```

**Exemplo — ferramenta GTT:**

```bash
git add toolkit/gtt/issues.py toolkit/gtt/specs/spec_issues.md
```

```
feat(gtt): add YAML export for GitHub issues

See https://github.com/carloshob/specs-catalog

Align issues.py with spec_issues (projects, milestone, relationships).
```

### 8.3 Passo 3 — Arquivos frequentemente à parte

| Situação                                      | Sugestão usual                                       |
| --------------------------------------------- | ---------------------------------------------------- |
| Só `_dev/toDo.md` / «atualizar lista»         | § **6** Commit só de toDo.md                         |
| Spec SDD sem código                           | `docs(sdd): …`                                       |
| Vários escopos de ferramenta não relacionados | Separar commits por escopo (`gtt`, `dev`, `profile`) |
| `*:Zone.Identifier` (Windows)                 | Não commitar; remover antes do staging               |
| `toDo.md` na raiz (legado)                    | Preferir `_dev/toDo.md`; não misturar sem motivo     |

### 8.4 Passo 4 — Dúvida → opções clicáveis

Perguntar com 2–4 opções (um commit / vários / excluir `toDo.md`, etc.).

### 8.5 Passo 5 — Formato da resposta

1. Resumo  
2. Pergunta com opções (se necessário)  
3. Propostas numeradas  
4. Encerramento § **1.3**  
5. Lembrete: **nada commitado** salvo modo execução confirmado  

---

## 9. Exemplo mínimo (só mensagem)

Os exemplos abaixo mostram bloco `See` **somente** quando `_dev/_dev.md` tiver linhas `See …` com
referência; senão, usar só título (e corpo opcional).

```
fix(clh): fix EXPLORER_CMD override in profile

See https://github.com/carloshob/specs-catalog

Remove duplicate EXPLORER_CMD_PRF definition that shadowed EXPLORER_CMD.
```

```
docs(sdd): document commit convention and staging for agents

See https://github.com/carloshob/specs-catalog

Add spec_commits.md; strengthen spec_agents.md and spec_conventions.md.
```

---

## 10. Manutenção

Novo ID: próximo `COMMITS-NN` livre; atualizar índice em **Como citar** e § **2** em [`spec_conventions.md`](spec_conventions.md) (**CONV-04**). Overrides locais de idioma ou escopo: `spec_<nome-repo>.md` § **Commits**, não cópias editadas de `spec_commits.md`.
