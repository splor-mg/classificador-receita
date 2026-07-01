# Foreign Keys e contenção temporal de vigência

Regras transversais de validação de **cobertura temporal de FK** entre modelos bitemporais do classificador. **Não substitui** `spec_itemClassificacao_mascara_apresentacao.md` nem políticas de resolução de máscara visual em formulários, lookups e sugestão de código (`format_receita_cod_by_vigencia`).

## Objetivo

Definir como o projeto **deve** validar que a vigência de um registro filho esteja **integralmente contida** na vigência da entidade referenciada por FK, quando o alvo é bitemporal — usando **união contígua** das janelas ativas da mesma entidade semântica.

Premissa: o comportamento descrito reflete a implementação vigente em `apps/core/code_valid_time_fk_validation.py` e `apps/core/code_valid_time_fk_resolution.py`.

## Referências

- ADR-001 — bitemporalidade (`docs/adr/adr-001_bitemporalidade.md`).
- ADR-003 — chave semântica e `*_ref` (`docs/adr/adr-003_chave-semantica.md`).
- `apps/core/models.py` — `BitemporalModel` e modelos afetados.
- [`spec_itemClassificacao_mascara_apresentacao.md`](spec_itemClassificacao_mascara_apresentacao.md) — política de máscara visual (distinta desta spec).
- [`spec_itemClassificacao_regras_hierarquia.md`](spec_itemClassificacao_regras_hierarquia.md) — regras de `parent_item_id` no domínio.
- [`spec_classificador-receita.md`](spec_classificador-receita.md) § **Convenções** — prefixo `FKVIG`.

Termos *deve* / *não deve* / *pode* conforme RFC 2119 (ver `_dev/spec_conventions.md` **Referências**).

## Como citar este documento

| Mecanismo          | Uso                                                                |
| ------------------ | ------------------------------------------------------------------ |
| **Seção numerada** | `§ N` / `§ N.M` — navegação neste arquivo.                         |
| **ID normativo**   | `FKVIG-NN` — citação estável.                                      |
| **Prefixo**        | `FKVIG` — ver § **Convenções** em `spec_classificador-receita.md`. |

**Índice de IDs normativos deste arquivo:**

| ID       | Tema            | Seção | Resumo                                                                                                                                                                                                                               |
| -------- | --------------- | ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| FKVIG-01 | Escopo          | 1.1   | Esta spec trata **somente** de validação de **cobertura temporal de FK** (vigência do filho contida na da entidade mãe).                                                                                                             |
| FKVIG-02 | Escopo          | 1.2   | Políticas de **máscara visual** e resolução estrita em UI **não** fazem parte desta spec — ver `spec_itemClassificacao_mascara_apresentacao.md`.                                                                                     |
| FKVIG-03 | Contexto        | 2     | FK Django armazena PK de **uma linha física**; a mesma entidade semântica pode ter **várias** linhas ativas com vigências parciais.                                                                                                  |
| FKVIG-04 | Decisão         | 3.1   | A validação **deve** comparar na **entidade de negócio** (`*_ref`), não só na linha apontada.                                                                                                                                        |
| FKVIG-05 | Decisão         | 3.2   | Vigência da entidade = **união contígua** das vigências de linhas com `data_registro_fim = sentinela` e mesmo `*_ref`.                                                                                                               |
| FKVIG-06 | Reaponte        | 3.3   | A FK física **continua** armazenando ponteiro para uma linha (limitação do ORM).                                                                                                                                                     |
| FKVIG-07 | Reaponte        | 3.4   | `apply_temporal_fk_resolution`: uma linha ativa cobre o filho → FK nessa linha; senão → linha ativa **mais recente** (desempate por `data_vigencia_inicio`, `data_registro_inicio`, `pk`).                                           |
| FKVIG-08 | Identidade      | 4.1   | Varredura de linhas da mesma entidade **deve** usar `*_ref` do alvo quando existir.                                                                                                                                                  |
| FKVIG-09 | Identidade      | 4.2   | Fallback: primeiro `*_id` semântico não-relacional; se ausente, PK da linha apontada.                                                                                                                                                |
| FKVIG-10 | Identidade      | 4.3   | A UI do Admin **deve** continuar exibindo `*_id` semântico; a chave de varredura é interna à validação.                                                                                                                              |
| FKVIG-11 | Aplicabilidade  | 5.1   | União contígua **somente** quando o alvo da FK herda de `BitemporalModel`.                                                                                                                                                           |
| FKVIG-12 | Aplicabilidade  | 5.2   | Alvo não bitemporal (ex.: `BaseLegalTecnica`): regra clássica de **linha única** apontada.                                                                                                                                           |
| FKVIG-13 | Aplicabilidade  | 5.3   | **Não** há exclusão por modelo; toda FK many-to-one para alvo bitemporal é coberta. Override futuro: `temporal_fk_union_validation_exclude_fields` — **não** reutilizar `temporal_fk_include_fields` / `temporal_fk_exclude_fields`. |
| FKVIG-14 | Algoritmo       | 6.1   | Por cada FK em `fk_fields` no `clean()`: alvo `None` (opcional) → ignorar silenciosamente.                                                                                                                                           |
| FKVIG-15 | Algoritmo       | 6.2   | **Etapa 1:** vigência da linha apontada contém `[ini_filho, fim_filho]` → passa imediatamente.                                                                                                                                       |
| FKVIG-16 | Algoritmo       | 6.3   | **Etapa 2:** se alvo bitemporal e Etapa 1 falhou — montar filtro de identidade (`*_ref`), coletar linhas ativas, calcular união contígua, verificar cobertura integral.                                                              |
| FKVIG-17 | Algoritmo       | 6.4   | Contiguidade **estrita:** `[a,b]` e `[c,d]` fundem em `[a,d]` **somente** quando `c == b + 1 dia`; sobreposições (`c <= b`) **não** fundem.                                                                                          |
| FKVIG-18 | Algoritmo       | 6.5   | **Etapa 3:** se Etapas 1 e 2 falharem → `ValidationError` com vigência do filho, `*_id` semântico do alvo, união consolidada e lista de **gaps**.                                                                                    |
| FKVIG-19 | Erro            | 7.1   | Sem gaps explícitos: mensagem com vigência do filho e união consolidada; com gaps: secção **Faltas:** em lista.                                                                                                                      |
| FKVIG-20 | Erro            | 7.2   | União cobre integralmente o filho → **nenhum** erro.                                                                                                                                                                                 |
| FKVIG-21 | Sentinela       | 8     | `VALID_TIME_SENTINEL` (`9999-12-31`): sem “próximo dia” em fusão; intervalo com fim sentinela é aberto à direita; gaps consideram cobertura até o fim do filho.                                                                      |
| FKVIG-22 | Aceite          | 9     | Os casos mínimos de § **9** **devem** ser respeitados pela validação (regressão e aceite).                                                                                                                                           |
| FKVIG-23 | Implementação   | 10.1  | Regra central em `apps/core/code_valid_time_fk_validation.py`; `clean()` dos cinco modelos bitemporais herdam sem alteração.                                                                                                         |
| FKVIG-24 | Implementação   | 10.2  | `_build_identity_filter` em `code_valid_time_fk_resolution.py` usa **apenas** `*_ref`, com fallback para `*_id` se `*_ref` vazio.                                                                                                    |
| FKVIG-25 | Implementação   | 10.3  | Varredura de linhas ativas usa sentinela de `data_registro_fim` adequado ao tipo do campo (aware/naive conforme `USE_TZ`).                                                                                                           |
| FKVIG-26 | Trade-off       | 11    | FK física pode apontar linha cuja vigência **sozinha** não cobre o filho — desencontro **intencional**; auditoria temporal consulta a união, não só a linha apontada.                                                                |
| FKVIG-27 | Compatibilidade | 11    | **Sem** migração de banco; mudança apenas em regra de `clean()`; dados existentes inalterados.                                                                                                                                       |

**Índice por tema:**

| Tema            | IDs                                              |
| --------------- | ------------------------------------------------ |
| Escopo          | FKVIG-01, FKVIG-02                               |
| Contexto        | FKVIG-03                                         |
| Decisão         | FKVIG-04, FKVIG-05                               |
| Reaponte        | FKVIG-06, FKVIG-07                               |
| Identidade      | FKVIG-08, FKVIG-09, FKVIG-10                     |
| Aplicabilidade  | FKVIG-11, FKVIG-12, FKVIG-13                     |
| Algoritmo       | FKVIG-14, FKVIG-15, FKVIG-16, FKVIG-17, FKVIG-18 |
| Erro            | FKVIG-19, FKVIG-20                               |
| Sentinela       | FKVIG-21                                         |
| Aceite          | FKVIG-22                                         |
| Implementação   | FKVIG-23, FKVIG-24, FKVIG-25                     |
| Trade-off       | FKVIG-26                                         |
| Compatibilidade | FKVIG-27                                         |

---

## Escopo

| Inclui                                                                        | Não inclui                                                                                 |
| ----------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| Validação de contenção de vigência filho ⊆ entidade mãe via FK **(FKVIG-01)** | Resolução de máscara visual em changelist, formulários e lookups **(FKVIG-02)**            |
| União contígua de vigências ativas da mesma entidade `*_ref` **(FKVIG-05)**   | Reaponte automático além do comportamento de `apply_temporal_fk_resolution` **(FKVIG-07)** |
| Diagnóstico de gaps na mensagem de erro **(FKVIG-18**, **FKVIG-19)**          | Política de `temporal_fk_include_fields` / `temporal_fk_exclude_fields` **(FKVIG-13)**     |

---

## 1. Escopo normativo

### 1.1 Cobertura temporal de FK **(FKVIG-01)**

Validar que `[data_vigencia_inicio, data_vigencia_fim]` do filho esteja contido na vigência efetiva da entidade referenciada.

### 1.2 Distinção da máscara visual **(FKVIG-02)**

Apresentação, tier estrito/secundário na changelist e `format_receita_cod_by_vigencia` seguem `spec_itemClassificacao_mascara_apresentacao.md`.

---

## 2. Contexto: FK para linha vs entidade **(FKVIG-03)**

Modelos `SerieClassificacao`, `Classificacao`, `NivelHierarquico`, `ItemClassificacao`, `VersaoClassificacao` e `VarianteClassificacao` herdam de `BitemporalModel`. Uma entidade de negócio (mesmo `*_id` / `*_ref`) pode ter múltiplas linhas físicas por janela de vigência e eixo de registro.

O Django persiste na coluna FK apenas a PK de **uma** linha do alvo. Cenário típico de falha falsa na validação antiga:

- Filho com vigência `[ini_filho, fim_filho]`.
- Mãe (mesmo `*_id`) com várias linhas ativas em transaction-time, cada uma com vigência menor que o filho.
- Nenhuma linha isolada cobre o filho, mas a **união** das vigências ativas cobre.

Comparar só a linha apontada reprovava o salvamento indevidamente.

---

## 3. Decisão e reaponte automático

### 3.1 Unidade de comparação: entidade **(FKVIG-04)**

Promover a comparação de linha física para **entidade de negócio**, identificada por `*_ref`.

### 3.2 União contígua **(FKVIG-05)**

Vigência da entidade = união contígua das vigências de todas as linhas com `data_registro_fim = sentinela` e mesmo `*_ref`.

### 3.3 FK física **(FKVIG-06)**

A coluna FK continua armazenando ponteiro para uma linha.

### 3.4 `apply_temporal_fk_resolution` **(FKVIG-07)**

| Situação                                               | Comportamento                                                                                                                                                                |
| ------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Uma linha ativa cobre `[ini_filho, fim_filho]` sozinha | FK aponta para essa linha                                                                                                                                                    |
| Caso contrário                                         | FK aponta para linha ativa **mais recente** (maior `data_vigencia_inicio`; desempate `data_registro_inicio`, depois `pk`) — linha exibida no link à direita da lupa no Admin |

---

## 4. Identidade da entidade

### 4.1 Chave `*_ref` **(FKVIG-08)**

Varredura de “linhas ativas da mesma entidade” usa exclusivamente `*_ref` do modelo-alvo quando existir — estabilidade frente a renomeações de `*_id` (ADR-003).

### 4.2 Fallback **(FKVIG-09)**

Sem coluna `*_ref`: primeiro `*_id` semântico não-relacional; se ainda ausente, PK da linha apontada.

### 4.3 Exibição no Admin **(FKVIG-10)**

Substituição da chave de varredura é **interna**; o Admin continua mostrando `*_id` semântico.

---

## 5. Aplicabilidade

### 5.1 Alvo bitemporal **(FKVIG-11)**

Regra de união contígua aplica-se quando o alvo herda de `BitemporalModel`.

### 5.2 Alvo não bitemporal **(FKVIG-12)**

Vigência do filho deve estar contida na vigência da **linha apontada** (regra clássica).

### 5.3 Cobertura e exclusões **(FKVIG-13)**

Toda FK many-to-one para destino bitemporal é validada por união. Exclusão futura por campo: `temporal_fk_union_validation_exclude_fields` — **ortogonal** a `temporal_fk_include_fields` / `temporal_fk_exclude_fields` (reaponte).

---

## 6. Algoritmo de validação

Para cada FK declarada em `fk_fields` no `clean()` do modelo:

### 6.1 FK opcional vazia **(FKVIG-14)**

Valor `None` → ignorar silenciosamente.

### 6.2 Etapa 1 — linha apontada **(FKVIG-15)**

Vigência da linha carregada pela FK contém `[ini_filho, fim_filho]` → validação passa (caminho comum).

### 6.3 Etapa 2 — união contígua **(FKVIG-16)**

Somente se alvo bitemporal e Etapa 1 falhou:

1. Filtro de identidade priorizando `*_ref` **(FKVIG-08)**.
2. Consultar linhas com esse identificador e `data_registro_fim = sentinela`; coletar pares `(data_vigencia_inicio, data_vigencia_fim)`.
3. Calcular união contígua **(FKVIG-17)**.
4. Se `[ini_filho, fim_filho]` está integralmente coberto → passa **(FKVIG-16)**.

### 6.4 Contiguidade estrita **(FKVIG-17)**

Intervalos `[a, b]` e `[c, d]` (ordenados por início) fundem em `[a, d]` **somente** quando `c == b + 1 dia`. Sobreposições (`c <= b`) permanecem entradas separadas (inconsistência detectada por outras camadas).

### 6.5 Etapa 3 — falha com diagnóstico **(FKVIG-18)**

`ValidationError` com:

- Vigência do filho;
- `*_id` semântico do alvo;
- União consolidada das vigências ativas;
- Lista de **gaps** (faixas de `[ini_filho, fim_filho]` descobertas), quando houver.

---

## 7. Formato da mensagem de erro

### 7.1 Estrutura **(FKVIG-19)**

Sem gaps explícitos: vigência do filho + união consolidada. Com gaps: secção **Faltas:** em lista.

Exemplo com dois gaps:

```text
O período de vigência deste registro (2018-01-01 a 9999-12-31) não está
integralmente coberto pela união das vigências ativas de classificação
selecionada (CLASS-RECEITA-UNIAO-2018). União consolidada: 2018-01-01 a
2021-12-31; 2024-01-01 a 2024-12-31; 2026-01-01 a 9999-12-31. Faltas:
  - 2022-01-01 a 2023-12-31
  - 2025-01-01 a 2025-12-31
```

### 7.2 Sucesso silencioso **(FKVIG-20)**

União cobre integralmente o filho → nenhuma mensagem, nenhum erro.

---

## 8. Sentinela `9999-12-31` **(FKVIG-21)**

`VALID_TIME_SENTINEL` (`9999-12-31`):

- Fusão contígua: se `b == sentinela`, intervalo aberto à direita — não há `c == b + 1 dia` válido.
- Gaps: intervalo da união com `fim == sentinela` que cobre o cursor considera o restante de `[ini_filho, fim_filho]` coberto.
- Nenhum intervalo pode começar depois do sentinela.

---

## 9. Casos de aceite mínimos **(FKVIG-22)**

| Caso | Cenário                                                                                                                                                       | Resultado                                                               |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| 0    | `CLASS-RECEITA-UNIAO-2018` em duas linhas ativas `[2018-01-01, 2025-12-31]` e `[2026-01-01, 9999-12-31]`; filho `NivelHierarquico` `[2018-01-01, 9999-12-31]` | Etapa 1 falha; Etapa 2 funde em `[2018-01-01, 9999-12-31]` → **aceita** |
| 1    | Uma linha ativa cobre o filho                                                                                                                                 | Etapa 1 passa; Etapa 2 não executa                                      |
| 2    | Duas linhas com gap real `[2018-01-01, 2020-12-31]` e `[2024-01-01, 9999-12-31]`; filho `[2018-01-01, 9999-12-31]`                                            | Gap `2021-01-01 a 2023-12-31` → **rejeita**                             |
| 3    | FK para `BaseLegalTecnica` (não bitemporal)                                                                                                                   | Apenas linha única **(FKVIG-12)**                                       |
| 4    | FK opcional `None`                                                                                                                                            | Ignorada **(FKVIG-14)**                                                 |
| 5    | Auto-FK `parent_item_id` em `ItemClassificacao`                                                                                                               | Entidade = `item_ref` da linha apontada; Etapa 2 normal                 |
| 6    | Linhas com `data_registro_fim != sentinela`                                                                                                                   | **Não** entram na união                                                 |

---

## 10. Implementação de referência

### 10.1 Validação **(FKVIG-23)**

`apps/core/code_valid_time_fk_validation.py` — `validate_vigencia_contained_in_fk_targets` nos `clean()` dos cinco modelos bitemporais.

### 10.2 Identidade no reaponte **(FKVIG-24)**

`apps/core/code_valid_time_fk_resolution.py` — `_build_identity_filter` usa somente `*_ref`, fallback `*_id` se `*_ref` vazio.

### 10.3 Sentinela de registro **(FKVIG-25)**

Varredura reutiliza convenção de `apply_temporal_fk_resolution` para sentinela de `data_registro_fim` (aware/naive conforme `USE_TZ`).

---

## 11. Consequências e trade-offs **(FKVIG-26**, **FKVIG-27)**

**Vantagens:** coerência FK ↔ entidade bitemporal; menos reprovações falsas após reversionamento do mãe; erro com gaps explícitos.

**Trade-off intencional (FKVIG-26):** a linha apontada pode não cobrir sozinha o filho; a auditoria temporal consulta a união das linhas ativas.

**Compatibilidade (FKVIG-27):** sem migração de banco; apenas regra em `clean()`; dados existentes inalterados.
