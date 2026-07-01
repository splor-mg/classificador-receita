# Versionamento (normas e releases)

Normas para decidir **quando** e **como** evoluir versões em projetos que usam especificações compartilhadas (SDD).

## Objetivo

Este documento orienta **desenvolvedores** e **assistentes de IA** a:

- classificar impacto de mudanças em specs e em código (**Semantic Versioning**);
- verificar, **antes de concluir** qualquer implementação relevante neste repositório, se a mudança exige bump, comunicação de impacto ou atualização na origem do catálogo.

**Não substitui** `spec_commits.md` (mensagens de commit **deste** repositório). Complementa [`spec_agents.md`](spec_agents.md).

## Referências

Os principais **conceitos**, **autores**, **metodologias** e **referências externas** que orientam **como versionar** mudanças (código e specs) neste catálogo são:

???+ note "Semantic Versioning (SemVer)"

    Versão **`MAJOR.MINOR.PATCH`**: incrementos comunicam **impacto** em consumidores — incompatível (MAJOR), adição compatível (MINOR), correção compatível (PATCH). Aplica-se a releases de software e, por analogia, a evolução de normas `spec_*.md` e do **manifesto** do catálogo.

    **Referências externas**

    - [Semantic Versioning 2.0.0](https://semver.org/lang/pt-BR/) — Tom Preston-Werner (PT-BR).
    - [semver.org (English)](https://semver.org/) — texto canônico em inglês.

??? abstract "Releases, changelog e comunicação de impacto"

    Versionar não é só um número: é **comunicar** o que mudou para quem sincroniza specs ou depende do repositório.

    **Referências externas**

    - [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/) — formato humano de changelog.
    - [Git Basics — Tagging](https://git-scm.com/book/en/v2/Git-Basics-Tagging) — tags anotadas.

??? tip "Conventional Commits e bump de versão"

    Mensagens **`feat`** / **`fix`** e **`BREAKING CHANGE`** alinham o histórico à classificação SemVer — ver [`spec_commits.md`](spec_commits.md).

    **Referências externas**

    - [Conventional Commits — FAQ (versionamento)](https://www.conventionalcommits.org/en/v1.0.0/#how-does-conventional-commits-handle-semver).
    - [semantic-release](https://semantic-release.gitbook.io/) — automação a partir de commits convencionais.

??? info "Versionamento de especificações (SDD)"

    Specs normativas são **contrato**: quebra de regra seguida → MAJOR; extensão compatível → MINOR; redação sem mudar obrigação → PATCH. O catálogo declara versão primária (`version:`) e rastreio por entrada (`areas.<entry>`) no `manifest.yaml` — ver **VERSION-03**. Pastas: [`spec_agents.md`](spec_agents.md) § **1** (**AGENTS-02**).

    **Referências externas**

    - [Spec-Driven Development (arXiv)](https://arxiv.org/abs/2602.00180).

??? note "Linguagem normativa e IDs"

    *Deve*/*não deve* conforme [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) — ver [`spec_conventions.md`](spec_conventions.md) **Referências**. IDs: prefixo **`VERSION`**; índice completo em § **2** de `spec_conventions.md`.

??? quote "Normas e artefatos deste catálogo"

    - [`spec_commits.md`](spec_commits.md) — mensagens ao publicar mudanças normativas.
    - [`spec_agents.md`](spec_agents.md) — **AGENTS-24**, **AGENTS-26**.
    - [`spec_conventions.md`](spec_conventions.md) — convenções afetadas por bump; § **7** — inventário de tags Git (**CONV-07**).
    - Catálogo canônico: `manifest.yaml` + [`_dev/spec_specs-catalog.md`](../_dev/spec_specs-catalog.md).

## Como citar este documento

| Mecanismo           | Uso                                                                |
| ------------------- | ------------------------------------------------------------------ |
| **Seção numerada**  | `§ 3.1` — navegação neste arquivo.                                 |
| **ID normativo**    | `VERSION-01` — citação estável.                                    |
| **Índice completo** | [`spec_conventions.md`](spec_conventions.md) § **2**.              |
| **Prefixo**         | `VERSION` — § **1** em `spec_conventions.md` (tabela de prefixos). |

**Índice de IDs normativos deste arquivo:**

| ID         | Tema        | Seção | Resumo                                                                                                                                                                                                                                                                         |
| ---------- | ----------- | ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| VERSION-01 | Avaliação   | 4     | Antes de concluir tarefa com alterações no repo, o responsável **deve** avaliar SemVer ou «sem bump» **e aplicar** bumps em arquivos de versionamento e `CHANGELOG` quando existirem (**AGENTS-20**).                                                                          |
| VERSION-02 | Avaliação   | 3     | Classificação SemVer **deve** seguir tabela § **3**: MAJOR = incompatível; MINOR = extensão compatível; PATCH = correção sem mudar obrigação.                                                                                                                                  |
| VERSION-03 | Manifesto   | 1     | Catálogo **deve** declarar `version:` primário e rastreio secundário `areas.<entry>` no `manifest.yaml` — **não** versionar cada `spec_*.md` isoladamente.                                                                                                                     |
| VERSION-04 | Avaliação   | 4     | Ao decidir qual spec foi alterada, **deve** aplicar precedência § **1.2** em `spec_agents.md` antes de classificar bump.                                                                                                                                                       |
| VERSION-05 | Avaliação   | 4     | Alteração em `_dev/spec_*.md` **deve** distinguir regra local do consumidor vs padrão elevável upstream — ver **AGENTS-26**.                                                                                                                                                   |
| VERSION-06 | Avaliação   | 4     | Promoção de norma de `_dev/` para contrato maduro (`docs/specs/` ou `specs/`) **deve** trigger revisão de versionamento e commits.                                                                                                                                             |
| VERSION-07 | Tags        | 7     | Com bump publicável, o assistente **deve** sugerir comandos `git tag` copiáveis ao operador — **não** executar tag/push (**VERSION-08**, **AGENTS-18**).                                                                                                                       |
| VERSION-08 | Tags        | 7     | O assistente **não deve** executar `git tag`, `git push origin vX.Y.Z` nem `git push --tags` sem pedido **explícito** do operador.                                                                                                                                             |
| VERSION-09 | Changelog   | 8     | Projetos com `CHANGELOG.md` **devem** manter `[Unreleased]` alinhado a tags, pré-releases e estado do manifesto.                                                                                                                                                               |
| VERSION-10 | Manifesto   | 9     | Núcleo de `version:` **não deve** ser menor que o núcleo de qualquer outro campo SemVer no mesmo manifesto.                                                                                                                                                                    |
| VERSION-11 | Manifesto   | 9.3   | Núcleo de entrada em grupo filho (ex. `toolkit.gtt`) **não deve** exceder núcleo de `areas.<nome>` homônimo.                                                                                                                                                                   |
| VERSION-12 | Manifesto   | 9.6   | Seção YAML de grupo filho versionado **deve** ter o mesmo nome que a chave do agregador pai em `areas.*`.                                                                                                                                                                      |
| VERSION-13 | Manifesto   | 9.7   | Todo bump declarado num campo versionado **deve** propagar PATCH/MINOR/MAJOR na cadeia ascendente até `version:` na mesma tarefa.                                                                                                                                              |
| VERSION-14 | Changelog   | 8.6   | `CHANGELOG.md` **deve** seguir Keep a Changelog: eixos versão × tipo; bullets de impacto perceptível; omitir tipos vazios.                                                                                                                                                     |
| VERSION-15 | Changelog   | 8.7   | Perfil B lockstep (adotado): fechar `## [X.Y.Z] - data` no **mesmo commit** do bump de `version:` — **não** só após tag.                                                                                                                                                       |
| VERSION-16 | Changelog   | 8.8   | Seções `## [X.Y.Z]` cuja tag `vX.Y.Z` existe no remoto são **imutáveis** — bullets novos vão para `[Unreleased]` ou nova versão.                                                                                                                                               |
| VERSION-17 | Changelog   | 8.6   | Ao criar `## [X.Y.Z] - DATA`, se outra seção já usa a mesma `DATA`, o cabeçalho **deve** incluir sufixo `(N)` — ver checklist § **8.6** (**VERSION-17**).                                                                                                                      |
| VERSION-18 | Pré-release | 8.2.1 | Em branch de trabalho com sufixo `-alpha`/`-beta`/`-rc`, após fixar o núcleo SemVer face à última tag estável em `main`, entregas intermediárias **devem** incrementar só o sufixo pré-release — **não** PATCH/MINOR/MAJOR adicionais no núcleo de `version:` na mesma branch. |

**Índice por tema:**

| Tema        | IDs                                                        |
| ----------- | ---------------------------------------------------------- |
| Avaliação   | VERSION-01, VERSION-02, VERSION-04, VERSION-05, VERSION-06 |
| Manifesto   | VERSION-03, VERSION-10, VERSION-11, VERSION-12, VERSION-13 |
| Tags        | VERSION-07, VERSION-08                                     |
| Changelog   | VERSION-09, VERSION-14, VERSION-15, VERSION-16, VERSION-17 |
| Pré-release | VERSION-18                                                 |

---

## 1. Parâmetros gerais

| Parâmetro                    | Regra                                                                                                                                                                                                    |
| ---------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Versão deste repositório** | Histórico Git local; mensagens conforme `spec_commits.md` em vigor.                                                                                                                                      |
| **Normas no projeto**        | `_dev/spec_*.md` e contrato maduro — ver [`spec_agents.md`](spec_agents.md) § **1**.                                                                                                                     |
| **Catálogo compartilhado**   | Versão global na origem (`manifest`); mudanças que afetam adotantes exigem coordenação.                                                                                                                  |
| **Versão do catálogo**       | Campo primário `version:` no manifesto; rastreio secundário por entrada em `areas.<entry>` (chaves = `entries` / `commit_scope`). **Não** versionar cada `spec_*.md` fora do manifesto. **(VERSION-03)** |

---

## 2. Escopo deste documento

Define **classificação de impacto** e **checklist antes de concluir** tarefas. Release do repositório canônico **`specs-catalog`** segue o checklist **desse** repositório, não duplicado aqui.

---

## 3. Semantic Versioning — como classificar **(VERSION-02)**

Use a tabela para mudanças em specs normativas e, por analogia, para código **neste** repositório. **(VERSION-02)**

| Componente | Quando incrementar                                                                                            |
| ---------- | ------------------------------------------------------------------------------------------------------------- |
| **MAJOR**  | Mudança **incompatível**: remove ou renomeia contrato; exige ação de quem já seguia a spec.                   |
| **MINOR**  | **Adição compatível**: nova spec, nova seção normativa, extensão de protocolo sem invalidar quem está em dia. |
| **PATCH**  | **Correção compatível**: typos, clareza, correção de contradição sem mudar obrigação.                         |

Em dúvida entre MINOR e PATCH: **PATCH** se ninguém precisa mudar processo; **MINOR** se surge capacidade ou spec nova relevante.

---

## 4. Antes de concluir (desenvolvedor ou assistente de IA) **(VERSION-01**, **VERSION-04**–**06)**

**Antes de dar por concluída** qualquer tarefa que alterou arquivos **neste** repositório, o responsável **deve** **(VERSION-01)**:

1. Aplicar precedência de pastas ([`spec_agents.md`](spec_agents.md) § **1.2**; **VERSION-04** / **AGENTS-02**–**04**) ao decidir **qual spec** foi alterada.
2. **Avaliar** impacto (MAJOR / MINOR / PATCH) ou registrar «sem bump» — aplica-se ao conjunto da mudança (código, configs, `_dev/`, `docs/specs/`, `specs/`, `README`, etc.). **(VERSION-02)**
   - **Assistente de IA:** a avaliação **deve** constar no resumo de saída; quando a decisão for bump ou changelog user-facing, o assistente **deve** **editar** os arquivos (`manifest.yaml`, `pyproject.toml`, `package.json`, `CHANGELOG.md`, …) **antes** de sugerir `git add` + HEREDOC no chat — ver **AGENTS-20** § **3.1** e **COMMITS-16**. **Não** basta concluir «mentalmente» sem tocar nos artefatos.
3. **Contrato maduro** (`docs/specs/`, `specs/`): commits conforme norma em vigor; comunicar se breaking.
4. **Alteração em `_dev/spec_*.md`:** avaliar projeto local vs padrão elevável ao catálogo — **(VERSION-05)** / **AGENTS-26**; não publicar no upstream sem alinhamento.
5. **Promoção** de norma de `_dev/` para `docs/specs/` ou `specs/`: marco de estabilização; revisar versionamento e commits. **(VERSION-06)**
6. **Só código** (sem spec): versionamento habitual; usar SemVer acima quando alterar **contrato** documentado.
7. Se a tarefa **alterou versão** em `manifest.yaml`, `CHANGELOG.md` ou equivalente: ao concluir, **sugerir** ao operador os comandos `git tag` conforme § **7** (**VERSION-07**); **não** executar tag/push sem pedido explícito (**VERSION-08**).

---

## 5. Relação com commits

Mensagens de commit **neste** repositório: [`spec_commits.md`](spec_commits.md) (inglês). Overrides locais nos consumidores: `spec_<nome-repo>.md` § **Commits**. Contrato maduro: [`spec_agents.md`](spec_agents.md) § **3** (**AGENTS-10**).

---

## 6. Manutenção

Ao evoluir regras de versionamento para todos os projetos que adotam o catálogo, atualizar `docs/spec_version.md` na origem e integrar nos consumidores.

Novo ID: próximo `VERSION-NN`; atualizar índice local e § **2** em `spec_conventions.md` (**CONV-04**).

---

## 7. Tags Git e orientação ao operador **(VERSION-07**, **VERSION-08)**

Bump em `manifest.yaml` ou entrada fechada em `CHANGELOG.md` **não** cria tag automaticamente. A tag é um **rótulo Git** num commit — em geral o último commit da release na branch estável (`main`).

### 7.1 Quando o assistente deve orientar **(VERSION-07)**

Sempre que a tarefa **alterou** versão publicável (`manifest.yaml`, `CHANGELOG.md`, ou decisão explícita de release), o assistente **deve**, ao concluir:

1. Confirmar **branch** alvo (padrão: `main` ou `defaults.branch` do manifesto).
2. Confirmar **nome da tag** conforme [`spec_conventions.md`](spec_conventions.md) § **7.2** (**CONV-06**) — ex.: versão `2.1.0` → tag `v2.1.0`.
3. Entregar bloco **copiável** com os comandos abaixo (substituir `vX.Y.Z` e mensagem).
4. Lembrar de **atualizar o inventário** em **`_dev/spec_<nome-repo>.md`** (seção **Convenções** ou **Versionamento** — **CONV-07** / **AGENTS-20**); se existir contrato maduro de convenções em `docs/specs/` ou `specs/`, também lá. **Não** editar `_dev/spec_conventions.md` (sync).

O assistente **não deve** executar `git tag`, `git push origin vX.Y.Z` nem `git push --tags` sem pedido **explícito** do operador — mesma regra de cautela que commits (**VERSION-08**; **AGENTS-11**).

### 7.2 Comandos sugeridos (modelo)

Após merge/commit na branch estável, com working tree limpa no commit desejado:

```bash
# Verificar commit alvo (HEAD na branch estável)
git log -1 --oneline

# Criar tag anotada (preferida)
git tag -a vX.Y.Z -m "Release X.Y.Z"

# Publicar só esta tag no remoto
git push origin vX.Y.Z
```

Opcional — release no GitHub (cria tag no remoto se ainda não existir):

```bash
gh release create vX.Y.Z --title "vX.Y.Z" --notes "Ver CHANGELOG.md"
```

### 7.3 Checklist rápido para o operador

| Passo | Ação                                                                                                          |
| ----- | ------------------------------------------------------------------------------------------------------------- |
| 1     | Versão em `manifest.yaml` / `CHANGELOG.md` commitada em `main`                                                |
| 2     | `git tag -a vX.Y.Z -m "Release X.Y.Z"` no commit correto                                                      |
| 3     | `git push origin vX.Y.Z`                                                                                      |
| 4     | Linha no **Inventário de tags Git** em **`spec_<nome-repo>.md`** (e contrato maduro se existir — **CONV-07**) |

---

## 8. `CHANGELOG.md` e seção `[Unreleased]` **(VERSION-09**, **VERSION-14**–**18)**

Projetos que adotam [Keep a Changelog](https://keepachangelog.com/) **devem** manter a seção **`[Unreleased]`** coerente com o **estado de release** do repositório — manifesto, tags Git remotas e, quando existir, o protocolo `gtt -tg-*` (ver implementação de referência em `computer-setup/toolkit/gtt/specs/spec_tags.md`).

**Perfil adotado neste ecossistema (SDD / consumidores com `manifest.yaml` + `gtt tag`):** **Perfil B — lockstep** (§ **8.7**, **VERSION-15**). Até maior amadurecimento dos protocolos de publicação, o trabalho com bump da versão primária fecha seção no CHANGELOG **no mesmo commit** do bump, não apenas após a tag.

### 8.1 O que é «Unreleased»

**`[Unreleased]`** documenta alterações **ainda sem seção versionada fechada** no CHANGELOG — em especial quando **não** há bump da versão primária (`version:`) no mesmo commit.

| Situação                                                                                     | O que vai em `[Unreleased]`                                 |
| -------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| Trabalho **sem** bump de `version:` no mesmo commit                                          | Sim                                                         |
| Bump **apenas** em campos filhos (`areas.*`, `toolkit.*`, …) **sem** propagar até `version:` | Sim — e **alertar** inconsistência com **VERSION-13**       |
| Bump de `version:` no mesmo commit (Perfil B)                                                | **Não** — abrir `## [nova-versão] - AAAA-MM-DD` (§ **8.7**) |
| Alteração já em `## [X.Y.Z]` cuja tag `vX.Y.Z` **existe** no remoto                          | **Não** — seção **publicada** e imutável (§ **8.8**)        |

**Publicada** (§ **8.8**): existe tag estável `vX.Y.Z` no remoto (`origin` ou remote padrão).

### 8.2 Pré-releases (alinhamento com tags Git)

Quando o projeto usa tags de candidatura (convenção em [`spec_conventions.md`](spec_conventions.md) § **6.1**; protocolo detalhado em consumidores com `gtt -tg-cr`):

| Tipo de tag / manifesto                  | Significado para o changelog                                                                |
| ---------------------------------------- | ------------------------------------------------------------------------------------------- |
| `vX.Y.Z` (release)                       | Release **fechada** — seção `## [X.Y.Z]` no CHANGELOG; tag no remoto confirma **publicada** |
| `vX.Y.Z-rc.N`                            | Release candidate — pode permanecer em `[Unreleased]` ou subseção opcional até `vX.Y.Z`     |
| `vX.Y.Z-beta.N`                          | Beta — idem                                                                                 |
| `vX.Y.Z-alpha.N`                         | Alpha — idem                                                                                |
| `version: X.Y.Z-rc.N` em `manifest.yaml` | Manifesto em pré-release — `[Unreleased]` reflete esse núcleo + sufixo                      |

Ordem SemVer entre pré-releases do mesmo núcleo: `alpha` &lt; `beta` &lt; `rc` &lt; release estável.

**Regra:** não listar em `[Unreleased]` alterações que já constam numa seção **publicada**. Não **editar** seções `## [X.Y.Z]` já publicadas (§ **8.8**).

### 8.2.1 Núcleo fixo em branch de trabalho **(VERSION-18)**

Em branches de feature/fix (≠ `main` / branch default), quando o manifesto usa sufixo de pré-release (`-alpha.N`, `-beta.N`, `-rc.N`), o operador **deve** separar **avaliação SemVer do núcleo** de **marcos intermediários** na mesma branch.

#### Baseline e avaliação inicial

1. **Baseline:** última tag **estável** `vX.Y.Z` no remoto da branch default (`origin/main` ou `defaults.branch` do manifesto).
2. **Avaliação SemVer (uma vez por branch):** classificar o **delta acumulado** branch → baseline (**VERSION-02**) — MAJOR, MINOR ou PATCH — e fixar o **núcleo** resultante `M` (`MAJOR.MINOR.PATCH`).
3. **Primeiro manifesto na branch:** `version: M-<id>.1` (ex.: baseline `v1.15.2`, uma funcionalidade compatível → `1.16.0-beta.1`).

A quantidade de funcionalidades ou entregas **não** altera o núcleo: cinco `feat` compatíveis continuam `1.16.0`, não `1.17.0` … `1.20.0`.

#### Entregas intermediárias na mesma branch

Após o núcleo `M` estar fixo na branch:

| Campo / artefato              | Regra                                                                                                                                                                                                       |
| ----------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`version:` (núcleo `M`)**   | **Não deve** subir PATCH/MINOR/MAJOR por entrega intermediária — só incrementar o sufixo pré-release: `M-beta.1` → `M-beta.2` → …                                                                           |
| **`areas.*` / grupos filhos** | Podem bump SemVer no **escopo local** da entrega (**VERSION-13** na cadeia interna); a propagação até `version:` **deve** refletir apenas incremento do sufixo pré-release quando o núcleo `M` já está fixo |
| **`CHANGELOG.md`**            | Acumular bullets em `[Unreleased]` entre marcos; opcional nota por `-beta.N`                                                                                                                                |
| **Tag Git**                   | Opcional por marco (`vM-beta.N`); release estável `vM` **só** após merge em `main` (§ **7**)                                                                                                                |

**Exemplo (baseline `v1.15.2` estável; branch feat com cinco entregas compatíveis):**

```text
main (estável):     v1.15.2
branch feat:        1.16.0-beta.1  ← 1.ª entrega (núcleo MINOR fixado)
                    1.16.0-beta.2  ← 2.ª entrega
                    …
                    1.16.0-beta.5  ← 5.ª entrega
PR / feature done:  1.16.0-rc.1    ← candidata a merge (mesmo núcleo M)
merge main:         1.16.0 + tag v1.16.0 (remover sufixo)
```

**Exemplo (baseline `v1.15.2`; branch só com correções):**

```text
main:     v1.15.2
branch:   1.15.3-beta.1 … 1.15.3-beta.N
merge:    v1.15.3
```

#### Progressão `beta` → `rc` → release

| Fase                      | Sufixo típico | Quando                                                          |
| ------------------------- | ------------- | --------------------------------------------------------------- |
| Desenvolvimento na branch | `-beta.N`     | Entregas intermediárias (mids, feats)                           |
| PR / feature complete     | `-rc.1`       | Branch pronta para review/merge (**mesmo núcleo `M`**)          |
| Merge em `main`           | *(nenhum)*    | Tag estável `vM`; Perfil B lockstep (§ **8.7**, **VERSION-15**) |

Ordem entre tipos no **mesmo núcleo:** `alpha.N` &lt; `beta.N` &lt; `rc.N` &lt; release estável. Protocolo detalhado de tags: consumidores com `gtt tag` (`spec_tags.md`).

#### Exceções

| Situação                                                                    | Ação                                                                                                          |
| --------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| Descoberta de **BREAKING CHANGE** mid-branch                                | Recalcular núcleo **uma vez** (ex.: `1.16.0-beta.2` → `2.0.0-beta.3`); reiniciar contagem beta no novo núcleo |
| Bump de classe SemVer (PATCH→MINOR ou MINOR→MAJOR) antes de fechar a branch | Tratar como **nova avaliação** — novo núcleo + `-beta.1`                                                      |
| Trabalho **direto em `main`**                                               | **VERSION-18** não aplica — Perfil B lockstep (§ **8.7**)                                                     |

#### Relação com **VERSION-13**

- **Primeiro bump** na branch (fixação do núcleo): **VERSION-13** aplica-se na propagação completa até `version:` com sufixo `-beta.1` (ou `-alpha.1` / `-rc.1` conforme fase).
- **Entregas seguintes** na mesma branch com núcleo já fixo: **VERSION-18** prevalece sobre nova propagação PATCH/MINOR/MAJOR em `version:` — incrementar só `-beta.N` (ou `-rc.N` na transição de fase).

### 8.3 Fechar uma release

**Perfil B (lockstep — adotado):** no **mesmo commit** que altera código/specs e faz bump de `version:` (e propagação **VERSION-13**), abrir no CHANGELOG:

```text
## [X.Y.Z] - AAAA-MM-DD
```

com bullets do working diretory nessa seção; deixar `[Unreleased]` vazio. Em seguida, criar tag `vX.Y.Z` conforme § **7** e atualizar inventário **CONV-07** em **`spec_<nome-repo>.md`**.

**Perfil A (clássico Keep a Changelog — referência):** acumular em `[Unreleased]` durante o trabalho; **após** `git tag vX.Y.Z`, renomear `[Unreleased]` → `## [X.Y.Z] - AAAA-MM-DD`. Útil em projetos sem lockstep; **não** é o perfil adotado no protocolo SDD atual.

Passos comuns após fechar a seção (ambos os perfis):

1. Consolidar bullets (revisar duplicados e ordem Added/Changed/Fixed/Removed).
2. Alinhar `manifest.yaml` (`version` e `areas.*` / grupos filhos quando aplicável).
3. `git tag vX.Y.Z` e `git push origin vX.Y.Z` quando o operador pedir (**VERSION-07**, **VERSION-08**).

### 8.4 Verificação rápida (operador ou assistente)

```bash
# Última tag estável no remoto (exemplo)
git ls-remote --tags origin 'v*' | grep -v '\^{}' | tail -5

# Commits em main desde essa tag
git log vX.Y.Z..HEAD --oneline
```

Se `git log` lista commits user-facing, `[Unreleased]` está vazio e **não** há nova `## [versão]` para o bump pendente, o changelog está **desalinhado**.

### 8.5 Projetos sem `CHANGELOG.md`

Opcional. Se o projeto versiona só com `manifest.yaml`, aplicar a mesma lógica mental: trabalho pós-tag estável = próximo bump; pré-release = sufixo no manifesto ou tags `v*-rc.*` / `v*-beta.*` / `v*-alpha.*`.

### 8.6 Estrutura do arquivo **(VERSION-14**, **VERSION-17**)

Adotar [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) com estas regras:

**Eixos de organização**

| Eixo       | Regra                                                                                       |
| ---------- | ------------------------------------------------------------------------------------------- |
| **Versão** | Seções `## [Unreleased]` ou `## [X.Y.Z] - AAAA-MM-DD` (data ao **fechar** a entrada)        |
| **Tipo**   | Subseções `### Added`, `### Changed`, `### Fixed`, `### Removed`, `### Security`            |
| **Ordem**  | Versões **mais recentes primeiro**; dentro de cada tipo, bullets **mais recentes primeiro** |

**Uma seção de cada tipo por versão** — não repetir `### Fixed` três vezes sob o mesmo `[Unreleased]` ou sob o mesmo `## [X.Y.Z]`.

**Sufixo em datas repetidas (VERSION-17)**

Só deve existir nova seção `## [X.Y.Z]` quando há **nova versão** (novo núcleo SemVer publicado). Se **mais de uma** seção compartilha a mesma data `AAAA-MM-DD`:

1. Considerar apenas seções com essa data.
2. Ordenar os núcleos `X.Y.Z` em ordem **decrescente** (SemVer).
3. Na ordem do arquivo (mais recente no topo), percorrer de **baixo para cima** entre as seções dessa data: a **primeira** (menor versão entre as que compartilham a data) **sem** sufixo; da **segunda** em diante (subindo), sufixo `(2)`, `(3)`, … `(N)` em ordem crescente.

Exemplo — versões `1.11.3`, `1.11.2`, `1.11.1` e `1.10.1` na mesma data `2026-06-13`:

- Ordem decrescente: `1.11.3` → `1.11.2` → `1.11.1` → `1.10.1`.
- De baixo para cima na data: `1.10.1` (sem sufixo), `1.11.1` `(2)`, `1.11.2` `(3)`, `1.11.3` `(4)`.

```text
## [1.11.3] - 2026-06-13 (4)
## [1.11.2] - 2026-06-13 (3)
## [1.11.1] - 2026-06-13 (2)
## [1.10.1] - 2026-06-13
```

Atribuir o sufixo **no momento** em que a nova seção é criada; **não** reescrever cabeçalhos de seções já **publicadas** (§ **8.8**).

**Checklist ao abrir `## [X.Y.Z] - AAAA-MM-DD` (assistente de IA — VERSION-17)**

Antes de gravar o cabeçalho da nova seção versionada:

1. Listar no `CHANGELOG.md` todas as seções `## […] - AAAA-MM-DD` com a **mesma data** (ignorar `[Unreleased]`).
2. Se **não** houver outra seção com essa data → cabeçalho **sem** sufixo: `## [X.Y.Z] - AAAA-MM-DD`.
3. Se **já** houver uma ou mais → a nova seção é a próxima na sequência `(N)`:
   - contar quantas seções com essa data já existem no arquivo;
   - sufixo da nova = `(contagem + 1)` — ex.: já existem `1.14.8`, `1.14.9 (2)`, `1.14.10 (3)` na mesma data → nova `1.14.11` **deve** ser `## [1.14.11] - AAAA-MM-DD (4)`.
4. **Não** alterar sufixos de seções já publicadas (§ **8.8**, **VERSION-16**).

Atalho operacional: `grep '## \[' CHANGELOG.md | grep 'AAAA-MM-DD'` antes de fechar a seção.

**O que registrar (bullets)**

- Impacto **perceptível** para operador ou consumidor (CLI, profile, spec normativa, breaking change).
- Prefixo claro: `` `gtt tag list` ``, `` `dev prm` ``, `Profile`, `spec_tags_list.md`.
- Formato: `` `<superfície>`: <o que mudou>. ``

**O que evitar**

- Linhas só com `manifest.yaml: X → Y` (o manifesto já rastreia números).
- Duplicar o mesmo fix em `Added` e `Fixed`.
- Copiar o `git log` inteiro ou listar arquivos sem efeito.
- **Editar** bullets ou cabeçalhos de seções **publicadas**.

**Manifest no changelog:** citar versões **inline** na bullet da feature quando útil — não a cada bump intermediário de campo filho.

**Seção vazia:** omitir tipos sem entradas (não deixar `### Added` vazio).

### 8.7 Fluxo `main` direto e Perfil lockstep **(VERSION-15)**

Consumidores que publicam tags estáveis `vX.Y.Z` em `main` (sem `-rc`/`-beta`/`-alpha` no fluxo habitual) adotam **Perfil B — lockstep** até maior amadurecimento dos protocolos de versionamento.

| Perfil           | Quando fechar `## [X.Y.Z]` no CHANGELOG                                                                       | Adotado no SDD atual |
| ---------------- | ------------------------------------------------------------------------------------------------------------- | -------------------- |
| **A** (clássico) | Após `git tag vX.Y.Z` — mover `[Unreleased]` → `## [X.Y.Z] - AAAA-MM-DD`                                      | Não (referência)     |
| **B** (lockstep) | No **mesmo commit** que o bump de `version:` — bullets do working diretory em `## [nova-versão] - AAAA-MM-DD` | **Sim**              |

**Perfil B — passos (assistente de IA e operador):**

1. **Durante o trabalho sem bump de `version:`:** bullets em `[Unreleased]` no mesmo commit da implementação ([`spec_commits.md`](spec_commits.md) § **3.4**).
2. **Quando o commit inclui bump de `version:`** (e propagação **VERSION-13** quando aplicável): criar **nova** seção `## [<nova-versão>] - <AAAA-MM-DD>` com os bullets dessa entrega; **não** alterar seções de versões anteriores; esvaziar `[Unreleased]` se estava em uso.
3. **Sugerir** `git tag v<nova-versão>` e push quando apropriado (**VERSION-07**); **não** executar sem pedido explícito (**VERSION-08**).
4. Commits `docs(manifest): annotate version fields…` **pós-tag** (§ **7.8** em consumidores `gtt`) **não** entram no changelog — não são release unit.
5. Se o diff altera versão de campo **filho** sem alterar `version:` após propagação esperada (**VERSION-13**), **alertar** inconsistência; registrar bullets em `[Unreleased]` até o manifesto estar coerente.

Assistentes de IA **devem** reconciliar `[Unreleased]` com tags remotas quando detectarem trabalho já coberto por tags existentes (`gtt tag list` / `git tag -l`).

### 8.8 Seções publicadas imutáveis **(VERSION-16)**

**Publicada:** a seção `## [X.Y.Z] - …` corresponde a uma versão cuja tag estável **`vX.Y.Z` existe no remoto** (`origin`).

**Não deve** (assistente de IA nem operador):

- acrescentar, remover ou reescrever bullets em seção **publicada**;
- mover conteúdo novo para uma seção cuja versão é **menor ou igual** à última tag publicada.

**Destino obrigatório de bullets novos:**

| Situação no commit                                                  | Onde registrar                                       |
| ------------------------------------------------------------------- | ---------------------------------------------------- |
| Bump de `version:` (Perfil B)                                       | Nova `## [nova-versão] - AAAA-MM-DD`                 |
| Sem bump de `version:`                                              | `[Unreleased]`                                       |
| Tentativa de editar `## [1.11.15]` quando `version:` já é `1.11.16` | **Proibido** — usar `## [1.11.16]` ou `[Unreleased]` |

---

## 9. Consistência em manifestos com múltiplos níveis **(VERSION-10**, **VERSION-11**, **VERSION-12**, **VERSION-13**)

Alguns consumidores (ex.: `computer-setup`) declaram **mais de um campo SemVer** no mesmo `manifest.yaml`: versão **primária** (`version:`), versões **secundárias** (`areas.*`) e, opcionalmente, **grupos filhos** com entradas versionadas (ex.: `toolkit.*` por pasta em `toolkit/<tool>/`).

Comparações usam o **núcleo** `MAJOR.MINOR.PATCH` (ignorar sufixos `-alpha`, `-beta`, `-rc` na ordenação; exibir sufixos ao operador).

### 9.1 Hierarquia e papéis

| Nível          | Exemplo (consumidor)                                       | Papel                                                                            |
| -------------- | ---------------------------------------------------------- | -------------------------------------------------------------------------------- |
| **Primário**   | `version:`                                                 | Nome da tag Git estável `vX.Y.Z`; release do repositório                         |
| **Secundário** | `areas.setup`, `areas.toolkit`, `areas.utils` (consumidor) | Artefato agregado por área do repo                                               |
| **Secundário** | `areas.readme`, `areas.agents`, … (`specs-catalog`)        | Rastreio SemVer **por entrada** do catálogo (`entries`)                          |
| **Terciário**  | `toolkit.gtt`, `toolkit.sdd` (consumidor)                  | Rastreio SemVer **por ferramenta** sob `toolkit/<tool>/` (seção YAML `toolkit:`) |

O catálogo **`specs-catalog`** usa níveis **primário** (`version`) e **secundário** (`areas.<entry>`). **VERSION-11**, **VERSION-12** e **VERSION-13** aplicam-se a consumidores com grupos filhos versionados (ex.: toolkit). **VERSION-10** e **VERSION-13** aplicam-se a qualquer manifesto multinível.

### 9.2 Versão primária domina o manifesto **(VERSION-10)**

O núcleo de **`version:`** **não deve** ser **menor** que o núcleo de **qualquer** outro campo SemVer no mesmo manifesto (secundário, terciário ou futuro nível).

| Situação                                 | Avaliação                                                                    |
| ---------------------------------------- | ---------------------------------------------------------------------------- |
| `version: 1.4.3`, `areas.toolkit: 1.4.1` | **Consistente** (primário à frente — típico em `[Unreleased]`)               |
| `version: 1.4.2`, `areas.setup: 1.4.3`   | **Inconsistente** — subir `version` (PATCH ou superior) antes de tag estável |
| `version: 1.4.2`, `toolkit.gtt: 1.4.3`   | **Inconsistente** — idem                                                     |

**Regra de manutenção:** ao bumpar `areas.*` ou entradas de grupos filhos para núcleo **superior** ao de `version:`, o responsável **deve** bump correspondente em `version:` (em geral PATCH) **antes** de orientar tag estável `vM` — alinhado ao protocolo de artefatos secundários em consumidores com `gtt tag check` (ver `computer-setup/toolkit/gtt/specs/spec_tags.md` § **15**).

Ferramentas de verificação (`gtt tag check`, assistente em revisão de manifesto) **devem** reportar violação de **VERSION-10** como divergência a corrigir.

### 9.3 Filho sob agregador homônimo **(VERSION-11)**

Quando existir grupo filho versionado ligado a um agregador em `areas.*`, cada entrada do filho é retrato de um sub-artefato; o agregador `areas.<nome>` é retrato do **conjunto**.

**Pré-requisito:** o grupo filho **deve** obedecer **VERSION-12** (seção YAML `<nome>:` ↔ `areas.<nome>`).

O núcleo de **`<nome>.<item>`** (ex.: `toolkit.gtt`) **não deve** ser **maior** que o núcleo de **`areas.<nome>`** (ex.: `areas.toolkit`).

| Situação                                     | Avaliação                                                                      |
| -------------------------------------------- | ------------------------------------------------------------------------------ |
| `areas.toolkit: 1.4.2`, `toolkit.gtt: 1.4.2` | **Consistente**                                                                |
| `areas.toolkit: 1.4.1`, `toolkit.gtt: 1.4.2` | **Inconsistente** — bump `areas.toolkit` (≥ núcleo de `gtt`) ao fechar o ciclo |
| `areas.toolkit: 1.4.2`, `toolkit.sdd: 1.2.0` | **Consistente** (filho atrás do agregado é normal)                             |

**Regra de manutenção:** ao bumpar uma entrada do grupo filho acima do agregador homônimo, o responsável **deve** bump `areas.<nome>` no **mesmo PR/tarefa** ou no commit imediato seguinte, salvo nota explícita em `CHANGELOG.md` de adiamento documentado.

### 9.4 Ordem resumida (consumidor típico)

```text
núcleo(version:)  ≥  núcleo(areas.*)  ≥  núcleo(<grupo-filho>.* quando areas.<grupo-filho> existe)
```

### 9.5 Checklist (operador ou assistente)

Antes de sugerir tag estável ou dar por fechado bump de manifesto:

1. Comparar núcleos: `version` ≥ cada `areas.*` ≥ cada entrada em grupos filhos ligados (**VERSION-10**, **VERSION-11**, **VERSION-12**).
2. Confirmar **propagação simétrica** (**VERSION-13**): todo bump versionado propagou na cadeia até `version:` com a mesma magnitude SemVer.
3. Se `version` está à frente apenas por trabalho `[Unreleased]`, documentar em `CHANGELOG.md` — não é violação de **VERSION-10**; **VERSION-13** aplica-se na mesma às entradas que **foram** bumpadas nesta tarefa.
4. Se filho > pai em núcleo, corrigir manifesto antes de `gtt tag create` / orientação de tag.
5. Confirmar que cada seção YAML de grupo filho tem o **mesmo nome** que a chave do agregador pai em `areas` (**VERSION-12**).

### 9.6 Nomenclatura de grupos filhos **(VERSION-12)**

Para declarar um **grupo de versionamento filho** (terciário em diante), o nome da **seção YAML** de topo **deve** ser **igual** ao nome da chave do agregador no nível imediamente superior.

| Agregador (pai) | Seção filha válida | Seção inválida (exemplo) |
| --------------- | ------------------ | ------------------------ |
| `areas.toolkit` | `toolkit:`         | `toolkit_tools:`         |

**Regra geral:** se existe `areas.<nome>`, um mapa SemVer aninhado de sub-artefatos **deve** usar seção `<nome>:` no manifesto — **não** um sufixo arbitrário (`_tools`, `_items`, …).

Ferramentas (`gtt tag check`, assistente em revisão) **devem**:

1. Detetar grupos filhos pela convenção **VERSION-12** (e aliases legados documentados no consumidor, ex.: `toolkit_tools` → `toolkit`).
2. Aplicar **VERSION-11** entre entradas do grupo filho e o agregador homônimo.
3. Reportar seções com nome incorreto como violação **VERSION-12** antes ou junto da comparação de núcleos.

**Extensão futura:** níveis quarto e seguintes repetem a mesma regra — o nome da seção filha coincide com a chave do agregador no nível pai imediato.

### 9.7 Propagação simétrica de bump por magnitude SemVer **(VERSION-13)**

**VERSION-10** e **VERSION-11** definem **tetos** (filho não pode ultrapassar pai). **VERSION-13** complementa com **propagação ativa**: sempre que um campo versionado no manifesto **sobe** o núcleo `MAJOR.MINOR.PATCH`, os agregadores na cadeia ascendente **devem** subir **no mesmo componente** SemVer (PATCH, MINOR ou MAJOR), no **mesmo PR/tarefa** ou commit imediato seguinte.

#### 9.7.1 Cadeias de propagação

| Origem do bump                                        | Propaga para                 | Não propaga para                              |
| ----------------------------------------------------- | ---------------------------- | --------------------------------------------- |
| Entrada em grupo filho (ex.: `toolkit.gtt`)           | `areas.toolkit` → `version:` | Outros `areas.*` irmãos (`setup`, `utils`, …) |
| `areas.<entry>` (ex.: `areas.setup`, `areas.version`) | `version:`                   | Outros `areas.*` irmãos                       |
| `version:`                                            | — (topo)                     | —                                             |

**`specs-catalog`:** só existe primário + secundário — bump em `areas.<entry>` **deve** propagar PATCH/MINOR/MAJOR correspondente em `version:`.

**Consumidor típico (`computer-setup`):** bump em `toolkit.<tool>` propaga para `areas.toolkit` e depois `version:`; bump em `areas.setup` propaga só para `version:`.

#### 9.7.2 Magnitude do incremento

Classifique o bump do artefato alterado (**VERSION-02**) e aplique o **mesmo tipo** em cada nível superior da cadeia:

| Bump no filho                 | Efeito em cada ancestral na cadeia        |
| ----------------------------- | ----------------------------------------- |
| **PATCH** (`…Z` → `…Z+1`)     | +1 PATCH                                  |
| **MINOR** (`…Y.Z` → `…Y+1.0`) | +1 MINOR (PATCH reinicia em `0`)          |
| **MAJOR** (`X…` → `X+1.0.0`)  | +1 MAJOR (MINOR e PATCH reiniciam em `0`) |

Os núcleos **não precisam coincidir numericamente** entre níveis — só o **tipo** de incremento propaga. Exemplo (consumidor):

```text
Antes:  toolkit.gtt 1.0.0 | areas.toolkit 1.8.4 | version 1.8.6
PATCH em aid → 1.0.1     | areas.toolkit 1.8.5   | version 1.8.7

Antes:  toolkit.gtt 1.0.0 | areas.toolkit 1.8.4 | version 1.8.6
MINOR em aid → 1.1.0     | areas.toolkit 1.9.0   | version 1.9.0

Antes:  toolkit.gtt 1.0.0 | areas.toolkit 1.8.4 | version 1.8.6
MAJOR em aid → 2.0.0     | areas.toolkit 2.0.0   | version 2.0.0
```

#### 9.7.3 Vários campos na mesma tarefa

Se **mais de um** campo versionado sobe na mesma tarefa, aplicar **VERSION-13** em cada cadeia e usar para `version:` a **maior magnitude** entre as propagações exigidas (MAJOR > MINOR > PATCH).

Exemplo: `areas.version` sobe MINOR e `areas.conventions` sobe PATCH na mesma entrega → `version:` sobe **MINOR**.

#### 9.7.4 Relação com VERSION-10 e VERSION-11

| Regra          | Papel                                                            |
| -------------- | ---------------------------------------------------------------- |
| **VERSION-10** | Garante `version:` ≥ qualquer filho (teto)                       |
| **VERSION-11** | Garante agregador homônimo ≥ entradas do grupo filho (teto)      |
| **VERSION-13** | Garante que **todo bump declarado** sobe a cadeia até `version:` |

Cumprir **VERSION-13** numa tarefa que altera versões no manifesto **implica** satisfazer **VERSION-10** para os campos bumpados. O primário pode continuar **à frente** de filhos **não** alterados nesta tarefa (trabalho `[Unreleased]`).

#### 9.7.5 Operador e assistente

Ao atualizar `manifest.yaml` (incl. sugestões em `gtt commit` / `_dev/.prm_commit.md`):

1. Identificar qual(is) campo(s) SemVer a mudança exige.
2. Classificar PATCH / MINOR / MAJOR (**VERSION-02**).
3. Propagar na cadeia (**VERSION-13**).
4. Registar em `CHANGELOG.md` os bumps relevantes (`areas.*`, `version:`, entradas de grupo filho).
5. Verificar checklist § **9.5** antes de orientar tag estável.
