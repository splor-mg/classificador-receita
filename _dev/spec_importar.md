# Protocolo de importação (`importer`) — MINUTA

Rascunho da especificação transversal dos protocolos de **importação** (família `importer*.py`), alinhada ao **ADR-005**. **Não substitui** a carga operacional via `docs/assets/seed_*.csv` nem specs de domínio como `spec_itemClassificacao_*.md`.

> **Status:** MINUTA — etapas e módulos abaixo são **planejados**; IDs normativos cobrem apenas distinções já estabelecidas no repositório. Detalhes operacionais pendentes ficam em § **Decisões em aberto**.

## Objetivo

Registrar o **contrato alvo** do protocolo de importação: ler fontes brutas externas, normalizá-las conforme o datapackage do projeto e produzir artefatos em `data-raw/` e `data/` antes da gravação no banco — com escopo **transversal** (não exclusivo de `itemClassificacao`).

Premissa desta MINUTA: descreve intenção de desenho e reutilização de módulos existentes; implementação completa ainda **não** está consolidada.

## Referências

- **ADR-005** — `docs/adr/adr-005_layout-dados.md` (layout `docs/assets/referencias/`, `data-raw/`, `data/`).
- [`spec_classificador-receita.md`](spec_classificador-receita.md) § **Convenções** — distinção carga × importação; prefixo `IMPORT`.
- `apps/core/code_null_normalization.py` — tratamento de campos vazios (candidato a reutilização).
- `apps/core/code_name_connectives.py` — padrão de mapeamento em módulo dedicado.
- [`spec_lista_abreviacoes.md`](spec_lista_abreviacoes.md) — conectivos e normalização lexical relacionada.
- Futuro: `spec_normalizacao_nomes.md` *(a criar)* — normalização de nomes transversal.

Termos *deve* / *não deve* / *pode* conforme RFC 2119 (ver `_dev/spec_conventions.md` **Referências**).

## Como citar este documento

| Mecanismo          | Uso                                                                 |
| ------------------ | ------------------------------------------------------------------- |
| **Seção numerada** | `§ N` / `§ N.M` — navegação neste arquivo.                          |
| **ID normativo**   | `IMPORT-NN` — citação estável (índice **mínimo** enquanto MINUTA).  |
| **Prefixo**        | `IMPORT` — ver § **Convenções** em `spec_classificador-receita.md`. |

**Índice de IDs normativos deste arquivo:**

| ID        | Tema      | Seção | Resumo                                                                                                                                        |
| --------- | --------- | ----- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| IMPORT-01 | Escopo    | 1.1   | **Importação** e **carga** (seeds → BD) **devem** ser tratadas como protocolos **distintos**.                                                 |
| IMPORT-02 | Pipeline  | 1.2   | O import **deve** seguir o encadeamento fonte bruta → `data-raw/` → `data/` → BD, conforme ADR-005.                                           |
| IMPORT-03 | Escopo    | 1.3   | Esta spec **deve** permanecer **transversal** — **não** acoplada exclusivamente a `itemClassificacao` (fallback operacional pode focar nela). |
| IMPORT-04 | Validação | 2.7   | Antes da persistência tratada, o pipeline **deve** executar validação **Frictionless** dos dados normalizados.                                |
| IMPORT-05 | Artefatos | 2.8   | Saída tabular tratada **deve** ser gravada em `data-raw/`; entrada típica em `docs/assets/referencias/` quando aplicável.                     |

**Índice por tema:**

| Tema      | IDs                  |
| --------- | -------------------- |
| Escopo    | IMPORT-01, IMPORT-03 |
| Pipeline  | IMPORT-02            |
| Validação | IMPORT-04            |
| Artefatos | IMPORT-05            |

---

## Escopo

| Inclui (planejado)                                            | Não inclui                                                                       |
| ------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| Leitura de fontes brutas (Excel, CSV, …)                      | Carga direta de `docs/assets/seed_*.csv` → BD **(IMPORT-01)**                    |
| Normalização tabular e mapeamento de colunas                  | Regras Admin de `itemClassificacao`                                              |
| Autocomplete de `classificacao_id`, `nivel_id`, mãe, vigência | Spec final de normalização de nomes *(prevista em `spec_normalizacao_nomes.md`)* |
| Validação Frictionless **(IMPORT-04)**                        | Versionamento de `data/` no repositório                                          |

---

## 1. Distinção carga × importação

### 1.1 Protocolos distintos **(IMPORT-01)**

- **Carga:** `docs/assets/seed_*.csv` → banco via `carregar_classificador` (datapackage).
- **Importação:** fonte externa ainda não estruturada → tratamento → `data-raw/` → `data/` → BD.

### 1.2 Pipeline de artefatos **(IMPORT-02)**

Conforme ADR-005 e `spec_classificador-receita.md`:

| Etapa                | Local típico               |
| -------------------- | -------------------------- |
| Entrada bruta        | `docs/assets/referencias/` |
| Primeiro tratamento  | `data-raw/`                |
| Lançamentos apurados | `data/`                    |
| Runtime operacional  | PostgreSQL (Admin)         |

### 1.3 Escopo transversal **(IMPORT-03)**

O importador **deve** ser desenhado para reutilização entre entidades do projeto; o foco inicial pode ser `itemClassificacao`, sem restringir a spec a esse domínio.

---

## 2. Etapas planejadas do protocolo

As subseções abaixo descrevem **intenção de desenho** — sem IDs próprios até consolidação implementada.

### 2.1 Leitura de arquivos

- Suporte a Excel (`xls`, `xlsx`, …), CSV e outros formatos tabulares usuais.
- Preferir bibliotecas consolidadas para leitura.
- Avaliar módulo dedicado `importer_read.py` **somente** se houver ganho de separação.

### 2.2 Identificação do modelo de dados

- Detectar código hierárquico vs plano; inferir máscara quando hierárquico.
- A entidade/changelist de destino define colunas essenciais (PK).
- Mecanismo genérico o suficiente para outras classes, com fallback em `itemClassificacao`.

### 2.3 Normalização de nomes de colunas

- Converter cabeçalhos brutos para nomes do datapackage.
- Mapeamento em arquivo/módulo separado (análogo a `code_name_connectives.py`) para não poluir o orquestrador.

### 2.4 Transformações de dados

**Campos vazios**

- Tratar `NULL`, `"-"` e equivalentes; reutilizar `code_null_normalization.py` quando possível.

**Compilação de atributos**

- Gerar atributos derivados dos brutos — ex.: colunas por nível hierárquico → concatenar em ordem → `receita_cod` único.
- Avaliar módulo dedicado (ex.: `importer_compile.py`).

**Autocomplete**

Campos-alvo quando ausentes nos brutos:

| Campo              | Comportamento planejado                                                     |
| ------------------ | --------------------------------------------------------------------------- |
| `classificacao_id` | Enquadramento por protocolos existentes de classificação                    |
| `nivel_id`         | Inferência de nível                                                         |
| Item mãe           | Identificação com avaliação de fallback (vazio vs primeiro superior válido) |
| `data_vigencia`    | Fallback comum: 1º de janeiro do ano                                        |

- Se o bruto já trouxer o campo, **pular** autocomplete para esse campo.
- Em qualquer caso, rodar validação/check pós-autocomplete.

**Normalização de IDs**

- Protocolo de caixa alta e proibição de separador por traço em IDs semânticos.
- Avaliar `code_id_normalization.py` e spec dedicada (transversal ao import).

### 2.5 Normalização de strings de nome

Prevista spec própria `spec_normalizacao_nomes.md` e módulo `code_name_normalization.py` (transversal):

- Remover espaços múltiplos.
- Maiúsculas apenas em siglas e iniciais de palavras.
- Conectivos do projeto em caixa baixa (ver `code_name_connectives.py` / `spec_lista_abreviacoes.md`).

### 2.6 Verificação de campos mínimos (PK)

- Confirmar presença de colunas obrigatórias antes das etapas seguintes. *(Detalhe operacional pendente.)*

### 2.7 Validação Frictionless **(IMPORT-04)**

Executar `frictionless validate` (ou equivalente do projeto) sobre o dataset normalizado.

### 2.8 Persistência em `data-raw` **(IMPORT-05)**

Gravar tabela/arquivo tratado em `data-raw/`. Avaliar cópia do input bruto quando a fonte **não** estiver já em `docs/assets/referencias/`.

### 2.9 Evolução de diferenças e `data/`

Módulo separado (nome em aberto — ex. `importer_apply_db`, `importer_evolve_db`):

- Comparar vigências do `data-raw/` tratado com o que já está vigente no período por instância.
- Gravar lançamentos de diferença em `data/` (diretório **não** versionado — confirmar `.gitignore` e boas práticas).
- Parametrizar decisões de sobreposição vs encerramento de vigência anterior e nova vigência.

---

## Decisões em aberto

| Tópico                            | Pendência                                                      |
| --------------------------------- | -------------------------------------------------------------- |
| Nome dos módulos `importer_*`     | Orquestrador, leitura, compilação, evolução BD                 |
| Arquivo de mapeamento colunas     | Formato (YAML/CSV/Python) e localização                        |
| Fallback item mãe no autocomplete | Vazio vs primeiro superior encontrado                          |
| `spec_normalizacao_nomes.md`      | Spec e módulo `code_id_normalization.py` transversais          |
| § 2.6 PK mínimas                  | Lista por entidade/changelist                                  |
| Divergência com ADR-005           | Revisar texto original da MINUTA linha a linha na consolidação |
| Etapa final BD                    | Regras de sobreposição e encerramento de vigência              |

---

## Specs relacionadas (futuras)

| Artefato                                                         | Papel                                                     |
| ---------------------------------------------------------------- | --------------------------------------------------------- |
| `spec_import_*.md` *(família)*                                   | Detalhe operacional por protocolo/CLI quando implementado |
| `spec_normalizacao_nomes.md` *(a criar)*                         | Normalização lexical transversal                          |
| [`spec_classificador-receita.md`](spec_classificador-receita.md) | Inventário SDD e layout ADR-005                           |
