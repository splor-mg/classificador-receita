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

    - [`spec_commits.md`](spec_commits.md) / [`spec_commits-trb.md`](spec_commits-trb.md) — mensagens ao publicar mudanças normativas.
    - [`spec_agents.md`](spec_agents.md) — **AGENTS-13**, **AGENTS-14**.
    - [`spec_conventions.md`](spec_conventions.md) — convenções afetadas por bump; § **6** — nomenclatura e inventário de tags Git.
    - Catálogo canónico: `manifest.yaml` + [`_dev/spec_specs-catalog.md`](../_dev/spec_specs-catalog.md).

---

## Como citar este documento

| Mecanismo           | Uso                                                                |
| ------------------- | ------------------------------------------------------------------ |
| **Seção numerada**  | `§ 3.1` — navegação neste arquivo.                                 |
| **ID normativo**    | `VERSION-01` — citação estável.                                    |
| **Índice completo** | [`spec_conventions.md`](spec_conventions.md) § **2**.              |
| **Prefixo**         | `VERSION` — § **1** em `spec_conventions.md` (tabela de prefixos). |

**Índice de IDs deste arquivo:**

| ID         | Seção | Resumo                                                                   |
| ---------- | ----- | ------------------------------------------------------------------------ |
| VERSION-01 | 4     | Antes de concluir tarefa com alterações: avaliar impacto SemVer          |
| VERSION-02 | 3     | Classificar MAJOR / MINOR / PATCH pela tabela                            |
| VERSION-03 | 1     | Catálogo: `version:` primário + `areas.<entry>` secundário no manifesto  |
| VERSION-04 | 4     | Precedência de pastas ao decidir qual spec foi alterada                  |
| VERSION-05 | 4.4   | `_dev/spec_*`: projeto local vs padrão elevável (**AGENTS-14**)          |
| VERSION-06 | 4.5   | Promoção `_dev/` → contrato maduro: revisar versionamento                |
| VERSION-07 | 7     | Bump de versão: sugerir comando `git tag` ao operador                    |
| VERSION-08 | 7     | Não executar `git tag`/`git push` de tag sem pedido explícito            |
| VERSION-09 | 8     | `CHANGELOG.md` `[Unreleased]` alinhado a tags e pré-releases             |
| VERSION-10 | 9     | Manifesto multinível: `version` ≥ qualquer outro campo SemVer            |
| VERSION-11 | 9.2   | `toolkit_tools.*` ≤ `areas.toolkit` (consumidor com mapa por ferramenta) |

---

## 1. Parâmetros gerais

| Parâmetro                          | Regra                                                                                   |
| ---------------------------------- | --------------------------------------------------------------------------------------- |
| **Versão deste repositório**       | Histórico Git local; mensagens conforme `spec_commits.md` em vigor.                     |
| **Normas no projeto**              | `_dev/spec_*.md` e contrato maduro — ver [`spec_agents.md`](spec_agents.md) § **1**.    |
| **Catálogo compartilhado**         | Versão global na origem (`manifest`); mudanças que afetam adotantes exigem coordenação. |
| **Versão do catálogo**             | Campo primário `version:` no manifesto; rastreio secundário por entrada em `areas.<entry>` (chaves = `entries` / `commit_scope`). **Não** versionar cada `spec_*.md` fora do manifesto. **(VERSION-03)** |

---

## 2. Escopo deste documento

Define **classificação de impacto** e **checklist antes de concluir** tarefas. Release do repositório canónico **`specs-catalog`** segue o checklist **desse** repositório, não duplicado aqui.

---

## 3. Semantic Versioning — como classificar

Use a tabela para mudanças em specs normativas e, por analogia, para código **neste** repositório. **(VERSION-02)**

| Componente | Quando incrementar                                                                                            |
| ---------- | ------------------------------------------------------------------------------------------------------------- |
| **MAJOR**  | Mudança **incompatível**: remove ou renomeia contrato; exige ação de quem já seguia a spec.                   |
| **MINOR**  | **Adição compatível**: nova spec, nova seção normativa, extensão de protocolo sem invalidar quem está em dia. |
| **PATCH**  | **Correção compatível**: typos, clareza, correção de contradição sem mudar obrigação.                         |

Em dúvida entre MINOR e PATCH: **PATCH** se ninguém precisa mudar processo; **MINOR** se surge capacidade ou spec nova relevante.

---

## 4. Antes de concluir (desenvolvedor ou assistente de IA)

**Antes de dar por concluída** qualquer tarefa que alterou arquivos **neste** repositório, o responsável **deve** **(VERSION-01)**:

1. Aplicar precedência de pastas ([`spec_agents.md`](spec_agents.md) § **1.2**; **VERSION-04** / **AGENTS-02**–**04**) ao decidir **qual spec** foi alterada.
2. **Avaliar** impacto (MAJOR / MINOR / PATCH) ou registrar «sem bump» — aplica-se ao conjunto da mudança (código, configs, `_dev/`, `docs/specs/`, `specs/`, `README`, etc.). **(VERSION-02)**
3. **Contrato maduro** (`docs/specs/`, `specs/`): commits conforme norma em vigor; comunicar se breaking.
4. **Alteração em `_dev/spec_*.md`:** avaliar projeto local vs padrão elevável ao catálogo — **(VERSION-05)** / **AGENTS-14**; não publicar no upstream sem alinhamento.
5. **Promoção** de norma de `_dev/` para `docs/specs/` ou `specs/`: marco de estabilização; revisar versionamento e commits. **(VERSION-06)**
6. **Só código** (sem spec): versionamento habitual; usar SemVer acima quando alterar **contrato** documentado.
7. Se a tarefa **alterou versão** em `manifest.yaml`, `CHANGELOG.md` ou equivalente: ao concluir, **sugerir** ao operador os comandos `git tag` conforme § **7** (**VERSION-07**); **não** executar tag/push sem pedido explícito (**VERSION-08**).

---

## 5. Relação com commits

Mensagens de commit **neste** repositório: [`spec_commits.md`](spec_commits.md) ou [`spec_commits-trb.md`](spec_commits-trb.md), conforme variante `sdd` / `sdd-trb`. Contrato maduro de commits: [`spec_agents.md`](spec_agents.md) § **3** (**AGENTS-10**).

---

## 6. Manutenção

Ao evoluir regras de versionamento para todos os projetos que adotam o catálogo, atualizar `docs/spec_version.md` na origem e integrar nos consumidores.

Novo ID: próximo `VERSION-NN`; atualizar índice local e § **2** em `spec_conventions.md` (**CONV-04**).

---

## 7. Tags Git e orientação ao operador

Bump em `manifest.yaml` ou entrada fechada em `CHANGELOG.md` **não** cria tag automaticamente. A tag é um **rótulo Git** num commit — em geral o último commit da release na branch estável (`main`).

### 7.1 Quando o assistente deve orientar **(VERSION-07)**

Sempre que a tarefa **alterou** versão publicável (`manifest.yaml`, `CHANGELOG.md`, ou decisão explícita de release), o assistente **deve**, ao concluir:

1. Confirmar **branch** alvo (padrão: `main` ou `defaults.branch` do manifesto).
2. Confirmar **nome da tag** conforme [`spec_conventions.md`](spec_conventions.md) § **6** (**CONV-06**) — ex.: versão `2.1.0` → tag `v2.1.0`.
3. Entregar bloco **copiável** com os comandos abaixo (substituir `vX.Y.Z` e mensagem).
4. Lembrar de **atualizar o inventário** em `_dev/spec_conventions.md` do projeto (**CONV-07** / **AGENTS-20**).

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

| Passo | Ação                                                                            |
| ----- | ------------------------------------------------------------------------------- |
| 1     | Versão em `manifest.yaml` / `CHANGELOG.md` commitada em `main`                  |
| 2     | `git tag -a vX.Y.Z -m "Release X.Y.Z"` no commit correto                        |
| 3     | `git push origin vX.Y.Z`                                                        |
| 4     | Linha no **Inventário de tags Git** em `_dev/spec_conventions.md` (**CONV-07**) |

---

## 8. `CHANGELOG.md` e secção `[Unreleased]` **(VERSION-09)**

Projetos que adoptam [Keep a Changelog](https://keepachangelog.com/) **devem** manter a secção **`[Unreleased]`** coerente com o **estado de release** do repositório — manifesto, tags Git remotas e, quando existir, o protocolo `gtt -tg-*` (ver implementação de referência em `computer-setup/toolkit/gtt/specs/spec_tags.md`).

### 8.1 O que é «Unreleased»

**`[Unreleased]`** documenta alterações **ainda não publicadas** como release estável `vX.Y.Z` no remoto (`origin` ou remote por defeito).

| Situação                                                                              | O que vai em `[Unreleased]`               |
| ------------------------------------------------------------------------------------- | ----------------------------------------- |
| Commits em `main` **após** a última tag estável `vX.Y.Z` no remoto                    | Sim — até fechar a release                |
| Manifesto com núcleo `X.Y.Z` **sem** tag estável `vX.Y.Z` no remoto                   | Sim — trabalho em curso para essa versão  |
| Manifesto com sufixo `-alpha.N`, `-beta.N` ou `-rc.N`                                 | Sim — candidatura a release (pré-release) |
| Alteração já incluída numa secção `## [X.Y.Z]` cuja tag `vX.Y.Z` **existe** no remoto | **Não** — não duplicar em `[Unreleased]`  |

### 8.2 Pré-releases (alinhamento com tags Git)

Quando o projeto usa tags de candidatura (convenção em [`spec_conventions.md`](spec_conventions.md) § **6.1**; protocolo detalhado em consumidores com `gtt -tg-cr`):

| Tipo de tag / manifesto                  | Significado para o changelog                                                          |
| ---------------------------------------- | ------------------------------------------------------------------------------------- |
| `vX.Y.Z` (release)                       | Release **fechada** — mover entradas de `[Unreleased]` para `## [X.Y.Z] - YYYY-MM-DD` |
| `vX.Y.Z-rc.N`                            | Release candidate — permanece em `[Unreleased]` ou subsecção opcional até `vX.Y.Z`    |
| `vX.Y.Z-beta.N`                          | Beta — idem                                                                           |
| `vX.Y.Z-alpha.N`                         | Alpha — idem                                                                          |
| `version: X.Y.Z-rc.N` em `manifest.yaml` | Manifesto em pré-release — `[Unreleased]` reflecte esse núcleo + sufixo               |

Ordem SemVer entre pré-releases do mesmo núcleo: `alpha` &lt; `beta` &lt; `rc` &lt; release estável.

**Regra:** não listar em `[Unreleased]` alterações que já constam numa versão **já taggeada** como `vX.Y.Z` no remoto. Ex.: se `gtt -tg-list` mostra `v1.4.2` e não há commits de release posteriores taggeados, a secção `## [1.4.2]` está **fechada**; só commits **posteriores** à tag entram em `[Unreleased]`.

### 8.3 Fechar uma release

1. Consolidar `[Unreleased]` (revisar duplicados e ordem Added/Changed/Fixed/Removed).
2. Renomear para `## [X.Y.Z] - YYYY-MM-DD` (data da tag ou do merge em `main`).
3. Deixar `[Unreleased]` vazio ou com placeholder mínimo até novo trabalho.
4. Alinhar `manifest.yaml` (`version` e `areas.*` quando aplicável).
5. Criar tag `vX.Y.Z` conforme § **7** e inventário **CONV-07**.

### 8.4 Verificação rápida (operador ou assistente)

```bash
# Última tag estável no remoto (exemplo)
git ls-remote --tags origin 'v*' | grep -v '\^{}' | tail -5

# Commits em main desde essa tag
git log vX.Y.Z..HEAD --oneline
```

Se `git log` lista commits e `[Unreleased]` está vazio, o changelog está **desalinhado** — actualizar `[Unreleased]` ou fechar release se o bump já foi decidido.

### 8.5 Projetos sem `CHANGELOG.md`

Opcional. Se o projeto versiona só com `manifest.yaml`, aplicar a mesma lógica mental: trabalho pós-tag estável = próximo bump; pré-release = sufixo no manifesto ou tags `v*-rc.*` / `v*-beta.*` / `v*-alpha.*`.

---

## 9. Consistência em manifestos com múltiplos níveis **(VERSION-10**, **VERSION-11)**

Alguns consumidores (ex.: `computer-setup`) declaram **mais de um campo SemVer** no mesmo `manifest.yaml`: versão **primária** (`version:`), versões **secundárias** (`areas.*`) e, opcionalmente, **terciárias** (`toolkit_tools.*` por pasta em `toolkit/<tool>/`).

Comparações usam o **núcleo** `MAJOR.MINOR.PATCH` (ignorar sufixos `-alpha`, `-beta`, `-rc` na ordenação; exibir sufixos ao operador).

### 9.1 Hierarquia e papéis

| Nível          | Exemplo (consumidor)                          | Papel                                                    |
| -------------- | --------------------------------------------- | -------------------------------------------------------- |
| **Primário**   | `version:`                                    | Nome da tag Git estável `vX.Y.Z`; release do repositório |
| **Secundário** | `areas.setup`, `areas.toolkit`, `areas.utils` (consumidor) | Artefato agregado por área do repo                       |
| **Secundário** | `areas.readme`, `areas.agents`, … (`specs-catalog`)        | Rastreio SemVer **por entrada** do catálogo (`entries`)  |
| **Terciário**  | `toolkit_tools.gtt`, `toolkit_tools.sdd` (consumidor)      | Rastreio SemVer **por ferramenta** sob `toolkit/<tool>/` |

O catálogo **`specs-catalog`** usa níveis **primário** (`version`) e **secundário** (`areas.<entry>`). **VERSION-11** (`toolkit_tools` ≤ `areas.toolkit`) aplica-se só a consumidores com toolkit. As regras de **VERSION-10** aplicam-se a qualquer manifesto multinível.

### 9.2 Versão primária domina o manifesto **(VERSION-10)**

O núcleo de **`version:`** **não deve** ser **menor** que o núcleo de **qualquer** outro campo SemVer no mesmo manifesto (secundário, terciário ou futuro nível).

| Situação                                     | Avaliação                                                                    |
| -------------------------------------------- | ---------------------------------------------------------------------------- |
| `version: 1.4.3`, `areas.toolkit: 1.4.1`     | **Consistente** (primário à frente — típico em `[Unreleased]`)               |
| `version: 1.4.2`, `areas.setup: 1.4.3`       | **Inconsistente** — subir `version` (PATCH ou superior) antes de tag estável |
| `version: 1.4.2`, `toolkit_tools.gtt: 1.4.3` | **Inconsistente** — idem                                                     |

**Regra de manutenção:** ao bumpar `areas.*` ou `toolkit_tools.*` para núcleo **superior** ao de `version:`, o responsável **deve** bump correspondente em `version:` (em geral PATCH) **antes** de orientar tag estável `vM` — alinhado ao protocolo de artefatos secundários em consumidores com `gtt tag check` (ver `computer-setup/toolkit/gtt/specs/spec_tags.md` § **15**).

Ferramentas de verificação (`gtt tag check`, assistente em revisão de manifesto) **devem** reportar violação de **VERSION-10** como divergência a corrigir.

### 9.3 Terciário sob secundário agregado **(VERSION-11)**

Quando existir mapa **`toolkit_tools`** e área agregada **`areas.toolkit`**, cada `toolkit_tools.<tool>` é retrato da ferramenta; `areas.toolkit` é retrato do **conjunto** do toolkit.

O núcleo de **`toolkit_tools.<tool>`** **não deve** ser **maior** que o núcleo de **`areas.toolkit`**.

| Situação                                           | Avaliação                                                                      |
| -------------------------------------------------- | ------------------------------------------------------------------------------ |
| `areas.toolkit: 1.4.2`, `toolkit_tools.gtt: 1.4.2` | **Consistente**                                                                |
| `areas.toolkit: 1.4.1`, `toolkit_tools.gtt: 1.4.2` | **Inconsistente** — bump `areas.toolkit` (≥ núcleo de `gtt`) ao fechar o ciclo |
| `areas.toolkit: 1.4.2`, `toolkit_tools.sdd: 1.2.0` | **Consistente** (ferramenta atrás do agregado é normal)                        |

**Regra de manutenção:** ao bumpar `toolkit_tools.<tool>` acima de `areas.toolkit`, o responsável **deve** bump `areas.toolkit` no **mesmo PR/tarefa** ou no commit imediato seguinte, salvo nota explícita em `CHANGELOG.md` de adiamento documentado.

### 9.4 Ordem resumida (consumidor típico)

```text
núcleo(version:)  ≥  núcleo(areas.*)  ≥  núcleo(toolkit_tools.* sob areas.toolkit)
```

### 9.5 Checklist (operador ou assistente)

Antes de sugerir tag estável ou dar por fechado bump de manifesto:

1. Comparar núcleos: `version` ≥ cada `areas.*` ≥ cada `toolkit_tools.*` relevante (**VERSION-10**, **VERSION-11**).
2. Se `version` está à frente apenas por trabalho `[Unreleased]`, documentar em `CHANGELOG.md` — não é violação.
3. Se filho > pai em núcleo, corrigir manifesto antes de `gtt tag create` / orientação de tag.
