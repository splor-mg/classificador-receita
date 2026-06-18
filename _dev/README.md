# Especificações compartilhadas (SDD)

Conjunto de normas para **desenvolvimento guiado por especificação (SDD) assistido por IA**: alinhar desenvolvedor e assistente no **como** trabalhar (commits, idioma, ordem de leitura) enquanto o projeto define o **o quê** no contrato maduro.

## Intenção geral

Em **`_dev/`** coexistem **três famílias** de `spec_*.md` — ver [`spec_agents.md`](spec_agents.md) § **1.3**:

| Família                 | Critério                              | Papel                                                                                                |
| ----------------------- | ------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| **Catálogo (manifest)** | Chave em `manifest.yaml` → `entries`  | Baseline sync (`spec_agents`, `spec_commits`, …) — **não editar** para regras locais (**AGENTS-25**) |
| **Repositório**         | `spec_<nome-repo>.md` (opcional)      | Especificidades **SDD** deste repo — criar quando houver overrides (**AGENTS-22**)                   |
| **Domínio local**       | Qualquer outro `spec_*.md` em `_dev/` | Regras de negócio **deste** projeto (ex. `spec_django`, `spec_itemClassificacao_*`) — **AGENTS-26**  |

O padrão de nome **`spec_<tema>.md` não identifica sync** — só a entrada no manifest (ou `.specs-sync.yaml`) identifica cópia do catálogo.

- **Contrato maduro** — `docs/specs/` ou `specs/` na raiz; prevalece no domínio (**AGENTS-02**).
- **Este índice (`docs/README.md`)** — sincronizado para **`_dev/README.md`**: mapeamento das normas **do catálogo**. **Não** substitui `README.md` da raiz da aplicação.

## README e documentação por camada

| Caminho                                         | Papel                                                      |
| ----------------------------------------------- | ---------------------------------------------------------- |
| `README.md` (raiz)                              | Aplicação/repo: quick start, instalação                    |
| **`_dev/README.md`**                            | **Este índice** após sync — catálogo SDD                   |
| **`_dev/spec_<nome-repo>.md`**                  | Especificidades SDD **deste** repo (opcional; § **1.3.2**) |
| **`_dev/spec_<domínio>.md`** (fora do manifest) | Spec de domínio local / rascunho                           |
| `docs/specs/README.md` ou `specs/README.md`     | Índice maduro do contrato de domínio                       |

Tabela completa: [`spec_agents.md`](spec_agents.md) § **1.5** (**AGENTS-23**).

## O que cada norma cobre

| Documento                                    | Foco                                                                       |
| -------------------------------------------- | -------------------------------------------------------------------------- |
| [`spec_agents.md`](spec_agents.md)           | Orquestração SDD: três famílias em `_dev/`, precedência, ordem de leitura  |
| [`spec_commits.md`](spec_commits.md)         | Commits (baseline EN; overrides em `spec_<nome-repo>.md` § Commits)        |
| [`spec_issues.md`](spec_issues.md)           | Issues (baseline EN; overrides em `spec_<nome-repo>.md` § Issues)          |
| [`spec_conventions.md`](spec_conventions.md) | Convenções transversais, índice de IDs (§ **2**), layout toolkit (§ **6**) |
| [`spec_version.md`](spec_version.md)         | SemVer, tags, `CHANGELOG.md`, manifesto multinível                         |

Regras de **domínio** exclusivas: `spec_<domínio>.md` local ou contrato maduro — não em cópias editadas das entradas sync do manifest.

## Leitura sugerida

1. [`spec_conventions.md`](spec_conventions.md) — § **2** (índice de IDs).
2. [`spec_agents.md`](spec_agents.md) — § **1.2** (precedência) e § **4** (ordem de leitura).
3. `_dev/spec_<nome-repo>.md` do consumidor (se existir).
4. Specs de domínio locais em `_dev/` ou contrato maduro (`docs/specs/`, `specs/`).
5. Antes de commitar: `spec_<nome-repo>.md` § Commits (se existir) + [`spec_commits.md`](spec_commits.md).
6. Ao alterar o catálogo: [`spec_version.md`](spec_version.md).

Upstream: normas em `docs/` deste repositório Git; versão em `manifest.yaml`; histórico em [`CHANGELOG.md`](../CHANGELOG.md).
