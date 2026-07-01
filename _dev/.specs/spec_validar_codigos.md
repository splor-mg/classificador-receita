# Validação de códigos (`validate_code.py`)

Especificação do script `scripts/validate_code.py`, que valida `receita_cod` de itens de classificação contra metadados bitemporais da classificação estatística. **Não substitui** `spec_validar_qualidade.md` nem o fluxo admin de hierarquia em `spec_itemClassificacao_validar_hierarquia.md`.

## Objetivo

Definir como o projeto **deve** verificar, para cada linha de `item_classificacao`, se `len(receita_cod)` corresponde ao `numero_digitos` da classificação estatística vigente e registrada no mesmo intervalo temporal do item.

Premissa: o comportamento descrito reflete a implementação vigente em `scripts/validate_code.py`.

## Referências

- GSIM — `receita_cod` como atributo do Classification Item; `numero_digitos` definido na Statistical Classification.
- `schemas/item_classificacao.yaml` — `custom.codeValidation` (regra e script).
- `schemas/classificacao.yaml`, `docs/assets/seed_classificacao.csv` — metadados de classificação com vigência e registro.
- `docs/assets/seed_item_classificacao.csv` — CSV de itens de exemplo.
- [`spec_validar_qualidade.md`](spec_validar_qualidade.md) — quality dimensions (comando distinto).
- [`spec_foreignKeys_vigencia.md`](spec_foreignKeys_vigencia.md) — modelo bitemporal no domínio.
- [`spec_classificador-receita.md`](spec_classificador-receita.md) § **Convenções** — prefixo `VALCOD`.

Termos *deve* / *não deve* / *pode* conforme RFC 2119 (ver `_dev/spec_conventions.md` **Referências**).

## Como citar este documento

| Mecanismo          | Uso                                                                 |
| ------------------ | ------------------------------------------------------------------- |
| **Seção numerada** | `§ N` / `§ N.M` — navegação neste arquivo.                          |
| **ID normativo**   | `VALCOD-NN` — citação estável.                                      |
| **Prefixo**        | `VALCOD` — ver § **Convenções** em `spec_classificador-receita.md`. |

**Índice de IDs normativos deste arquivo:**

| ID        | Tema       | Seção | Resumo                                                                                                                                                         |
| --------- | ---------- | ----- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| VALCOD-01 | Alinhamento | 1.1   | O código canónico (`receita_cod`) **deve** ser tratado como atributo do item; `numero_digitos` **deve** vir da classificação estatística (GSIM).               |
| VALCOD-02 | Alinhamento | 1.2   | A resolução **deve** considerar **duas** dimensões temporais: vigência (mundo) e registro (sistema).                                                           |
| VALCOD-03 | Dados      | 1.3   | Entradas **devem** ser linhas de `item_classificacao` e linhas de classificação (CSV/YAML de referência).                                                      |
| VALCOD-04 | Registro   | 2.1   | A validação **deve** **começar** pelo período de **registro** do item, **não** pela vigência.                                                                  |
| VALCOD-05 | Registro   | 2.2   | Por linha de item, o script **deve** usar `data_registro_inicio` e `data_registro_fim` da própria linha.                                                       |
| VALCOD-06 | Registro   | 2.3   | Na tabela de classificação, **devem** permanecer apenas linhas da mesma `classificacao_id` cujo intervalo de **registro** **compreenda** o do item.            |
| VALCOD-07 | Vigência   | 2.4   | A **vigência** **deve** ser aplicada após o filtro de registro; **não deve** ser desconsiderada.                                                               |
| VALCOD-08 | Vigência   | 2.5   | Entre linhas já filtradas por registro, **devem** permanecer só as cuja **vigência** **compreenda** a vigência do item (`data_vigencia_inicio` / `data_vigencia_fim`). |
| VALCOD-09 | Ordem      | 2.6   | A ordem **deve** ser: (1) filtrar por registro; (2) filtrar por vigência.                                                                                      |
| VALCOD-10 | Critério   | 3.1   | **Pode** haver **mais de uma** linha de classificação compatível com registro e vigência do item.                                                              |
| VALCOD-11 | Critério   | 3.2   | O teste **deve** ser **válido** quando `len(receita_cod)` corresponde ao `numero_digitos` de **cada** linha encontrada.                                        |
| VALCOD-12 | Critério   | 3.3   | Todas as linhas encontradas **devem** ter o **mesmo** `numero_digitos`.                                                                                        |
| VALCOD-13 | Falha      | 3.4   | O teste **deve falhar** se **nenhuma** linha de classificação atender registro e vigência compatíveis.                                                         |
| VALCOD-14 | Falha      | 3.5   | O teste **deve falhar** se linhas encontradas tiverem `numero_digitos` **diferentes** entre si.                                                                |
| VALCOD-15 | Falha      | 3.6   | O teste **deve falhar** se `numero_digitos` for único mas `len(receita_cod)` for **diferente** desse valor.                                                    |
| VALCOD-16 | CLI        | 4.1   | Entry point canónico: `scripts/validate_code.py`.                                                                                                                |
| VALCOD-17 | CLI        | 4.2   | Tasks Poetry: `poetry run task validar-codigos`; `poetry run task validar-tudo` inclui schemas, códigos e qualidade.                                           |
| VALCOD-18 | CLI        | 4.3   | Flags `--items` e `--niveis` **devem** permitir sobrescrever CSV de itens e de classificação.                                                                    |
| VALCOD-19 | CLI        | 4.4   | Se o arquivo de itens **não existir**, o script **deve** terminar com exit **0** e mensagem informativa — **não** falhar o pipeline.                           |
| VALCOD-20 | Schema     | 5     | A regra e o script **devem** estar documentados em `schemas/item_classificacao.yaml` em `custom.codeValidation`.                                                 |

**Índice por tema:**

| Tema        | IDs                                                          |
| ----------- | ------------------------------------------------------------ |
| Alinhamento | VALCOD-01, VALCOD-02                                         |
| Dados       | VALCOD-03                                                    |
| Registro    | VALCOD-04, VALCOD-05, VALCOD-06                              |
| Vigência    | VALCOD-07, VALCOD-08                                         |
| Ordem       | VALCOD-09                                                    |
| Critério    | VALCOD-10, VALCOD-11, VALCOD-12                              |
| Falha       | VALCOD-13, VALCOD-14, VALCOD-15                              |
| CLI         | VALCOD-16, VALCOD-17, VALCOD-18, VALCOD-19                   |
| Schema      | VALCOD-20                                                    |

---

## 1. Alinhamento e fontes de dados

### 1.1 GSIM **(VALCOD-01)**

`receita_cod` é o código canónico do item de classificação. A quantidade de dígitos esperada deriva da Statistical Classification (e dos níveis), resolvida por metadados da classificação no período temporal adequado.

### 1.2 Bitemporal **(VALCOD-02)**

O script **deve** aplicar vigência (validade no mundo) e registro (validade no sistema) de forma independente, na ordem definida em § **2**.

### 1.3 Fontes **(VALCOD-03)**

- Itens: instâncias em `item_classificacao` (ex.: `docs/assets/seed_item_classificacao.csv`).
- Classificação: tabela/CSV com vigência e registro (ex.: `schemas/classificacao.yaml`, `docs/assets/seed_classificacao.csv`).

---

## 2. Resolução temporal da classificação

### 2.1 Ponto de partida: registro **(VALCOD-04)**

A validação **inicia** pelo período de **registro** (transaction time), não pela vigência.

### 2.2 Registro do item **(VALCOD-05)**

Para cada linha de item, usar `data_registro_inicio` e `data_registro_fim` dessa linha.

### 2.3 Filtro por registro na classificação **(VALCOD-06)**

Considerar apenas linhas da mesma `classificacao_id` cujo intervalo de registro **contenha** o intervalo de registro do item (classificação ativa no sistema durante toda a versão do item no sistema).

### 2.4 Vigência obrigatória **(VALCOD-07)**

Após o filtro de registro, aplicar vigência. A vigência **não** é opcional.

### 2.5 Filtro por vigência **(VALCOD-08)**

Entre as linhas já filtradas por registro, manter apenas as cuja vigência **contenha** a vigência do item (`data_vigencia_inicio`, `data_vigencia_fim`).

### 2.6 Ordem dos filtros **(VALCOD-09)**

Sequência fixa: (1) registro; (2) vigência.

---

## 3. Critério de validação e falhas

### 3.1 Múltiplas linhas **(VALCOD-10)**

Mais de uma linha de classificação compatível com registro e vigência do mesmo item é aceitável.

### 3.2 Correspondência de dígitos **(VALCOD-11)**

Válido quando `len(receita_cod)` é igual ao `numero_digitos` de **cada** linha encontrada.

### 3.3 Consistência de `numero_digitos` **(VALCOD-12)**

Todas as linhas encontradas **devem** compartilhar o **mesmo** `numero_digitos`.

### 3.4 Falha: sem linha compatível **(VALCOD-13)**

Nenhuma linha de classificação com registro e vigência compatíveis → falha.

### 3.5 Falha: `numero_digitos` conflitantes **(VALCOD-14)**

Duas ou mais linhas encontradas com `numero_digitos` distintos → falha.

### 3.6 Falha: comprimento incorreto **(VALCOD-15)**

`numero_digitos` único entre as linhas encontradas, mas `len(receita_cod)` diferente → falha.

---

## 4. Script, tasks e entradas

### 4.1 Script **(VALCOD-16)**

`scripts/validate_code.py`

### 4.2 Tasks **(VALCOD-17)**

| Task                            | Efeito                                              |
| ------------------------------- | --------------------------------------------------- |
| `poetry run task validar-codigos` | Executa apenas validação de códigos               |
| `poetry run task validar-tudo`    | Schemas + códigos + qualidade (pipeline composto) |

### 4.3 Argumentos **(VALCOD-18)**

| Flag        | Função                                           |
| ----------- | ------------------------------------------------ |
| `--items`   | Caminho alternativo ao CSV de itens              |
| `--niveis`  | Caminho alternativo ao CSV de classificação      |

### 4.4 Arquivo de itens ausente **(VALCOD-19)**

CSV de itens inexistente: exit **0**, mensagem informativa, sem erro no pipeline.

---

## 5. Referência no schema **(VALCOD-20)**

`schemas/item_classificacao.yaml` **deve** declarar a regra e o script em `custom.codeValidation`. O validador **deve** respeitar essa configuração como contrato público do recurso.
