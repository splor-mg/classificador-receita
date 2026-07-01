# Validação de qualidade do Data Package (`validate_quality.py`)

Especificação do script `scripts/validate_quality.py`, que aplica **quality dimensions** aos dados dos recursos Frictionless. **Não substitui** `spec_validar_codigos.md` nem a validação estrutural de `validate_datapackage.py`.

## Objetivo

Definir como o projeto **deve** aplicar regras de **quality dimensions** declaradas em `quality/quality_rules.yaml` aos **dados** (CSV) dos recursos do Data Package cujos schemas referenciam `custom.qualityDimensions` (`rulesRef`, `ruleSets`).

Premissa: o comportamento descrito reflete a implementação vigente em `scripts/validate_quality.py`.

## Referências

- `quality/quality_rules.yaml` — expressões por `ruleSet` (ex.: `temporal_consistency_bitemporal`).
- `datapackage.yaml` — recursos e caminhos de schema/dados.
- `schemas/item_classificacao.yaml`, `schemas/classificacao.yaml` — exemplos com `custom.qualityDimensions`.
- `scripts/validate_datapackage.py` — validação de **estrutura** apenas (sem dados).
- [`spec_validar_codigos.md`](spec_validar_codigos.md) — validação de códigos (comando distinto).
- [`spec_classificador-receita.md`](spec_classificador-receita.md) § **Convenções** — prefixo `VALQUAL`.

Termos *deve* / *não deve* / *pode* conforme RFC 2119 (ver `_dev/spec_conventions.md` **Referências**).

## Como citar este documento

| Mecanismo          | Uso                                                                  |
| ------------------ | -------------------------------------------------------------------- |
| **Seção numerada** | `§ N` / `§ N.M` — navegação neste arquivo.                           |
| **ID normativo**   | `VALQUAL-NN` — citação estável.                                      |
| **Prefixo**        | `VALQUAL` — ver § **Convenções** em `spec_classificador-receita.md`. |

**Índice de IDs normativos deste arquivo:**

| ID         | Tema        | Seção | Resumo                                                                                                                                                                    |
| ---------- | ----------- | ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| VALQUAL-01 | Escopo      | 1.1   | O script **deve** ser **independente** de `validate_datapackage.py` e **deve** operar sobre **dados** de recursos, não só sobre descriptors. **(VALQUAL-02)**             |
| VALQUAL-02 | Escopo      | 1.1   | `validate_datapackage.py` **não deve** acionar `validate_quality.py`; são comandos distintos.                                                                             |
| VALQUAL-03 | Regras      | 1.2   | Cada expressão em `quality_rules.yaml` **deve** usar apenas campos da **própria linha** do recurso avaliado.                                                              |
| VALQUAL-04 | Pipeline    | 2.1   | O script **deve** carregar `datapackage.yaml` e percorrer `resources`.                                                                                                    |
| VALQUAL-05 | Pipeline    | 2.2   | Por recurso, o script **deve** ler o schema em `schema` e aplicar regras só se existir `custom.qualityDimensions` com `rulesRef` e `ruleSets`.                            |
| VALQUAL-06 | Pipeline    | 2.3   | O script **deve** carregar o arquivo YAML referenciado por `rulesRef` e resolver os `ruleSets` indicados no schema.                                                       |
| VALQUAL-07 | Dados       | 2.4   | O script **deve** carregar o CSV em `path` (relativo à raiz do projeto); se o arquivo **não existir**, **deve** ignorar o recurso com **aviso** — **não** abortar o lote. |
| VALQUAL-08 | Avaliação   | 2.5   | Para cada regra aplicável, o script **deve** avaliar `expression` em **cada linha**; falha (falso ou erro) **deve** ser registrada.                                       |
| VALQUAL-09 | Saída       | 2.6   | O processo **deve** emitir relatório por recurso/regra/linha e **deve** terminar com código de saída **1** se houver pelo menos um erro.                                  |
| VALQUAL-10 | Dependência | 3     | O projeto **deve** declarar **PyYAML** para ler `datapackage.yaml` e `quality_rules.yaml`.                                                                                |
| VALQUAL-11 | CLI         | 4.1   | Entry point canónico: `scripts/validate_quality.py`.                                                                                                                      |
| VALQUAL-12 | CLI         | 4.2   | Tasks Poetry: `poetry run task validar-qualidade`; `poetry run task validar-tudo` inclui schemas, códigos e qualidade.                                                    |
| VALQUAL-13 | CLI         | 4.3   | Flags `--datapackage` e `--quality-rules` **devem** permitir sobrescrever caminhos do datapackage e do arquivo de regras.                                                 |

**Índice por tema:**

| Tema        | IDs                                            |
| ----------- | ---------------------------------------------- |
| Escopo      | VALQUAL-01, VALQUAL-02                         |
| Regras      | VALQUAL-03                                     |
| Pipeline    | VALQUAL-04, VALQUAL-05, VALQUAL-06, VALQUAL-07 |
| Avaliação   | VALQUAL-08                                     |
| Saída       | VALQUAL-09                                     |
| Dependência | VALQUAL-10                                     |
| CLI         | VALQUAL-11, VALQUAL-12, VALQUAL-13             |

---

## 1. Escopo e regras de qualidade

### 1.1 Independência e dados **(VALQUAL-01**, **VALQUAL-02)**

O comando de qualidade **deve** validar **dados** tabulares dos recursos. A validação estrutural de schemas e datapackage permanece em `validate_datapackage.py`, que **não deve** invocar este script.

### 1.2 Regras auto-contidas **(VALQUAL-03)**

Expressões em `quality_rules.yaml` **devem** ser avaliáveis linha a linha (ex.: `data_vigencia_fim >= data_vigencia_inicio`) sem contexto de outras linhas ou recursos.

---

## 2. Comportamento do pipeline

### 2.1 Datapackage **(VALQUAL-04)**

Carregar `datapackage.yaml` na raiz do projeto (ou caminho de `--datapackage`) e iterar `resources`.

### 2.2 Schema e quality dimensions **(VALQUAL-05)**

Para cada recurso, ler o schema referenciado. Aplicar quality dimensions **somente** quando o schema declarar `custom.qualityDimensions` com `rulesRef` e `ruleSets` preenchidos.

### 2.3 Arquivo de regras **(VALQUAL-06)**

Resolver `rulesRef` (ex.: `quality/quality_rules.yaml`) e carregar os `ruleSets` listados no schema (ex.: `temporal_consistency_bitemporal`).

### 2.4 Dados do recurso **(VALQUAL-07)**

Ler o CSV em `path`. Recurso sem arquivo físico: **pular** com aviso; continuar os demais.

### 2.5 Avaliação **(VALQUAL-08)**

Para cada regra de cada `ruleSet`, avaliar `expression` por linha usando nomes de coluna como variáveis. Registrar falhas de expressão falsa ou exceção de avaliação.

### 2.6 Saída e exit code **(VALQUAL-09)**

Relatório agregado por recurso, regra e linha. Exit code **1** se existir ao menos uma falha; **0** caso contrário.

---

## 3. Dependências **(VALQUAL-10)**

**PyYAML** é obrigatório para parsing de `datapackage.yaml` e `quality_rules.yaml` (declarado nas dependências do projeto).

---

## 4. Script, tasks e argumentos

### 4.1 Script **(VALQUAL-11)**

`scripts/validate_quality.py`

### 4.2 Tasks **(VALQUAL-12)**

| Task                                | Efeito                                            |
| ----------------------------------- | ------------------------------------------------- |
| `poetry run task validar-qualidade` | Executa apenas validação de qualidade             |
| `poetry run task validar-tudo`      | Schemas + códigos + qualidade (pipeline composto) |

### 4.3 Argumentos **(VALQUAL-13)**

| Flag              | Função                                    |
| ----------------- | ----------------------------------------- |
| `--datapackage`   | Caminho alternativo ao `datapackage.yaml` |
| `--quality-rules` | Caminho alternativo ao YAML de regras     |

---

## 5. Configuração nos schemas

Schemas com `custom.qualityDimensions` (ex.: `schemas/item_classificacao.yaml`, `schemas/classificacao.yaml`) **devem** declarar `rulesRef` e `ruleSets`. O script **deve** respeitar essa configuração para decidir quais regras aplicar a cada recurso — sem hardcode de lista de recursos na spec.
