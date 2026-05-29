---
title: ADR-005 - Layout de artefatos de dados
description: Papéis de docs/assets, data-raw e data no repositório; distinção entre carga (seeds), importação e runtime Django
---

# ADR-005 — Layout de artefatos de dados

## Status

- **Estado**: Proposta
- **Data**: 2026-05-29
- **Decisor(es)**: DCAF e AID
- **Participantes**: DCAF e AID

## Contexto

O repositório nasceu com **Frictionless Data Package** (`datapackage.yaml`, `schemas/`, validação via scripts) e evoluiu para incluir **Django/PostgreSQL** como interface operacional do classificador. Os CSVs versionados em `docs/assets/seed_*.csv` passaram a ser, simultaneamente, recursos do datapackage e parâmetro de **carga inicial** do banco.

Está em elaboração um **protocolo de importação** de fontes externas (ex.: ementários em XLSX). Esse fluxo é distinto da **carga** (`carregar_classificador`): parte de arquivos brutos, produz artefatos intermediários e, por fim, incorpora lançamentos ao banco. Sem convenção explícita de pastas, haveria risco de misturar fontes brutas, substrato normalizado, lançamentos prontos para gravação e seeds de reprodutibilidade.

Forças em jogo: (1) **rastreabilidade** — saber de qual fonte veio cada transformação; (2) **separação de responsabilidades** — Django carrega seeds; importação gerencia `data-raw` e `data/`; (3) **compatibilidade** — manter datapackage e seeds onde já estão referenciados; (4) **flexibilidade de entrada** — o operador indica o caminho absoluto ou relativo do arquivo bruto a importar.

## Decisão

Adotar **três zonas de artefatos** na raiz do repositório, com missões fixas. O comportamento detalhado do protocolo de importação (CLI, estágios, naming, governança bitemporal na gravação) será normativo em **`_dev/spec_import_*.md`** quando redigido; esta ADR define **apenas onde cada tipo de dado fica**.

### Missões por localização

| Local                          | Missão                                                                                                                                                                                                                                                                                             | Quem consome / produz                                                                                                                              |
| ------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`docs/assets/referencias/`** | Fontes **externas de referência** recebidas ou arquivadas (XLSX, RTF, CSV de terceiros, exemplos didáticos). Imutáveis ou tratadas como arquivo de origem; **não** são recursos do datapackage.                                                                                                    | Entrada humana; **entrada** do protocolo de importação (caminho informado pelo operador).                                                          |
| **`data-raw/`**                | Saída do **primeiro tratamento** do import: limpeza, transformações iniciais e normalização tabular do arquivo bruto. Ex.: ementário de 2002 já estruturado em CSV, sem ainda mapear ao modelo de lançamentos do classificador.                                                                    | **Produzido** pelo protocolo de importação; **lido** na fase seguinte do mesmo protocolo.                                                          |
| **`data/`**                    | **Lançamentos** apurados a partir de `data-raw/`: conjuntos de registros que o import identifica como necessários para atualizar o banco (append/correções conforme governança ADR-004).                                                                                                           | **Produzido** e **consumido** pelo protocolo de importação até concluir a gravação no PostgreSQL. **Não** é lido pelo Django para carga rotineira. |
| **`docs/assets/seed_*.csv`**   | Recursos do **datapackage** (`datapackage.yaml`): snapshot validado, reprodutível, alinhado aos schemas Frictionless. Parâmetro de **carga inicial** / reposição de ambiente via `carregar_classificador`. Podem ser exportados da BD após operação (artefato derivado, conforme specs temáticas). | **Lido** pelo comando de carga Django e pelos scripts de validação Frictionless; **não** substituído por arquivos em `data/` ou `data-raw/`.       |
| **PostgreSQL (via Django)**    | Fonte operacional em runtime; edições pelo Admin e fluxos de governança (ADR-004).                                                                                                                                                                                                                 | Admin, APIs, comandos de domínio; export opcional para `seed_*.csv`.                                                                               |

### Fluxo conceitual (importação vs carga)

```text
[qualquer caminho]/fonte.xlsx          docs/assets/seed_*.csv
         │                                      │
         │ importar <caminho-do-arquivo>        │ carregar_classificador
         ▼                                      ▼
    data-raw/  ──►  data/  ──►  PostgreSQL  ◄──┘ (carga inicial / export)
   (normalizado)   (lançamentos)
```

### Entrada do comando de importação

O protocolo de importação recebe **somente o caminho do arquivo bruto** a processar. O operador pode executar o comando com um path **de qualquer localização** (absoluto ou relativo ao diretório de trabalho). Não se exige que o arquivo esteja em `docs/assets/referencias/`; essa pasta é convenção de arquivo, não restrição técnica da CLI.

Exemplo ilustrativo (comando e flags definitivos ficam na spec de importação):

```bash
poetry run task importar /caminho/para/ementario_receita_mg_2002_sisor.xlsx
```

### O que o Django **não** faz

- **Não** lê arquivos em `data/` para carga ou migração de dados.
- **Não** lê arquivos em `data-raw/` como parte dos fluxos de Admin ou de `carregar_classificador`.
- A incorporação ao banco dos lançamentos em `data/` é **responsabilidade exclusiva do protocolo de importação** (até conclusão da gravação).

A carga Django continua limitada aos recursos declarados em `datapackage.yaml` (`docs/assets/seed_*.csv`), como hoje.

## Alternativas Consideradas

### Alternativa 1: Mover todos os CSVs para `data/` (padrão Frictionless genérico)

- **Descrição**: Recursos do datapackage em `data/`; seeds deixam de ficar em `docs/assets/`.
- **Prós**: Alinhamento visual a exemplos comuns de datapackage.
- **Contras**: Refatoração ampla (`datapackage.yaml`, export admin, dezenas de referências em specs e scripts); mistura recursos publicados com lançamentos intermediários de import.
- **Razão da rejeição**: Custo alto; `seed_*` em `docs/assets/` já cumpre contrato Frictionless e carga inicial.

### Alternativa 2: Unificar `data-raw`, `data` e seeds em uma só pasta

- **Descrição**: Tudo sob `docs/assets/` ou só `data/`.
- **Prós**: Menos pastas na raiz.
- **Contras**: Ambiguidade entre fonte bruta, substrato normalizado, lançamentos pendentes e snapshot versionado; risco de validar Frictionless sobre artefatos intermediários.
- **Razão da rejeição**: Papéis distintos exigem separação clara.

### Alternativa 3: Django ler `data/` na carga

- **Descrição**: Estender `carregar_classificador` para também ingerir lançamentos em `data/`.
- **Prós**: Um único comando de “carga”.
- **Contras**: Acopla import externo ao ORM de seeds; governança bitemporal e idempotência do import ficam no comando errado.
- **Razão da rejeição**: Import e carga têm origens e garantias diferentes; separar responsabilidades.

## Consequências

### Positivas

- Papéis estáveis para agentes, operadores e specs (`spec_convencoes.md`, futura `spec_import_*.md`).
- Seeds e datapackage permanecem estáveis; importação evolui sem quebrar carga inicial.
- Rastreabilidade em três saltos: fonte informada → `data-raw/` → `data/` → BD.

### Negativas / Riscos

- Três pastas além de `docs/assets/` exigem disciplina de naming e Git (artefatos em `data/` e `data-raw/` podem crescer).
- Até existir `spec_import_*.md`, detalhes de naming e idempotência ficam em aberto.

### Mitigações

- Índice transversal em `_dev/spec_convencoes.md` (§ Layout de artefatos de dados) apontando para esta ADR.
- Política de versionamento Git para `data/` e `data-raw/` definida na spec de importação quando redigida.
- Scripts e validadores que hoje assumem paths legados (`data/item_classificacao.csv`) alinhados a `docs/assets/seed_*.csv`.

## Referências

- [ADR-004: Governança do banco](adr-004_governanca-banco.md)
- [ADR-001: Bitemporalidade](adr-001_bitemporalidade.md)
- `_dev/spec_convencoes.md` — índice de pastas
- `datapackage.yaml` — recursos em `docs/assets/seed_*.csv`
- `_dev/spec_import_*.md` — *(a redigir)* comportamento do protocolo de importação
