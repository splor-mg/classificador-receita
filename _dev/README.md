# Especificações compartilhadas (SDD)

Conjunto de normas para **desenvolvimento guiado por especificação (SDD) assistido por IA**: alinhar desenvolvedor e assistente no **como** trabalhar (commits, idioma, ordem de leitura) enquanto o projeto define o **o quê** no contrato maduro.

## Intenção geral

- **Catálogo (estes arquivos)** — protocolo **reutilizável** sincronizado para `_dev/spec_*.md` no projeto (`spec_agents`, `spec_commits`, …). Não substitui as especificações **exclusivas** do seu sistema.
- **`_dev/spec_*.md`** — parâmetros **iniciais** após `specs … -pl`: catálogo + rascunhos até existir documentação estável do projeto.
- **Contrato maduro do projeto** — recomenda-se `docs/specs/` ou `specs/` na raiz; nomenclatura **do projeto** (não obrigatório `spec_*.md`). Ver [`spec_agents.md`](spec_agents.md) § **1. Pastas de especificação no projeto** (**AGENTS-02**).
- **Precedência** — se coexistirem `_dev/`, `docs/specs/` e `specs/` (raiz), o contrato em `docs/specs/` ou `specs/` **prevalece**; `_dev/` só sem contradição e por **lacuna**.
- **Este índice (`docs/README.md`)** — sincronizado para **`_dev/README.md`** no consumidor: mapeamento das normas do catálogo, ordem de leitura e orientação SDD. **Não** é rascunho do hub de specs do seu projeto; **não** substitui o `README.md` da raiz da aplicação.
- **Complemento de escopo** — opcional: **`_dev/spec_<escopo>.md`** (nome do repo ou ferramenta em elaboração) para expandir documentação própria enquanto o contrato maduro não existe. Detalhe: [`spec_agents.md`](spec_agents.md) § **1.3.2** (**AGENTS-22**).

## README e hub de especificação

| Caminho                                     | Papel                                                                                    |
| ------------------------------------------- | ---------------------------------------------------------------------------------------- |
| `README.md` (raiz)                          | Aplicação/repo: quick start, instalação                                                  |
| **`_dev/README.md`**                        | **Este índice** após sync — catálogo SDD e mapeamento de normas                          |
| `_dev/spec_<escopo>.md`                     | Rascunho do hub de specs do projeto; promover índice estável para `docs/specs/README.md` |
| `docs/specs/README.md` ou `specs/README.md` | Índice maduro do contrato de domínio                                                     |

Tabela completa e regras de promoção: [`spec_agents.md`](spec_agents.md) § **1.5** (**AGENTS-23**).

## O que cada norma cobre

| Documento                                    | Foco                                                                                                                                              |
| -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`spec_agents.md`](spec_agents.md)           | Orquestração SDD: pastas, precedência, idioma (specs vs respostas da IA), ordem de leitura, commits, versionamento, elevação ao catálogo canônico |
| [`spec_commits.md`](spec_commits.md)         | Commits em **inglês** (variante `sdd`)                                                                                                            |
| [`spec_commits-trb.md`](spec_commits-trb.md) | Mesma estrutura; mensagens em **português do Brasil** (variante `sdd-trb`)                                                                        |
| [`spec_issues.md`](spec_issues.md)           | Issues em **inglês** (variante `sdd`)                                                                                                             |
| [`spec_issues-trb.md`](spec_issues-trb.md)   | Mesma estrutura; título e corpo do issue em **português do Brasil** (variante `sdd-trb`)                                                          |
| [`spec_conventions.md`](spec_conventions.md) | Convenções transversais, **índice completo de IDs** (§ **2**), prefixos, entry point shell (§ **6**), **migrations** (§ **8**)                    |
| [`spec_version.md`](spec_version.md)         | SemVer, tags, `CHANGELOG.md`, consistência de manifesto multinível (`version` / `areas` / `toolkit_tools`)                                        |

Specs **só do domínio do projeto** (ex. regras de negócio, integrações) complementam o catálogo; quando maduras, devem viver em `docs/specs/` ou `specs/`, não apenas em `_dev/`.

## Leitura sugerida

1. [`spec_conventions.md`](spec_conventions.md) — § **2** (índice completo de IDs) e prefixos § **1.2**.
2. [`spec_agents.md`](spec_agents.md) — § **Como citar**, § **1. Pastas…** e § **4. Ordem de leitura…**.
3. Contrato maduro do projeto (`docs/specs/`, senão `specs/` na raiz), se existir.
4. Antes de commitar: norma de commits em vigor (`spec_commits.md`).
5. Ao alterar normas ou publicar catálogo: [`spec_version.md`](spec_version.md).

Upstream deste catálogo: normas em `docs/` deste repositório Git; versão em `manifest.yaml`; histórico de releases em [`CHANGELOG.md`](../CHANGELOG.md).
