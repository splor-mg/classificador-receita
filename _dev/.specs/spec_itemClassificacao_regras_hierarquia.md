# Regras de `parent_item_id` em `item_classificacao`

Regras de domínio para o vínculo pai–filho na hierarquia de `item_classificacao`. **Não substitui** `spec_itemClassificacao_validar_hierarquia.md` (fluxo Admin de confirmação) nem `spec_itemClassificacao_foreignKeys_lookup.md` (endpoints JSON de lookup).

## Objetivo

Definir como o projeto **deve** validar `parent_item_id` para garantir coerência estrutural, semântica de `receita_cod` e compatibilidade temporal entre item filho e item mãe.

Premissa: o comportamento descrito reflete a implementação vigente em `apps/core/code_parent_item_validation.py` e validações de domínio associadas.

## Referências

- ADR-001 — bitemporalidade (`docs/adr/adr-001_bitemporalidade.md`).
- ADR-003 — chave semântica e máscara de níveis (`docs/adr/adr-003_chave-semantica.md`).
- [`spec_foreignKeys_vigencia.md`](spec_foreignKeys_vigencia.md) — modelo de vigência e registro.
- [`spec_itemClassificacao_validar_hierarquia.md`](spec_itemClassificacao_validar_hierarquia.md) — aviso de salto de nível e intermediários no Admin (**R-nivel-submit**).
- [`spec_itemClassificacao_foreignKeys_lookup.md`](spec_itemClassificacao_foreignKeys_lookup.md) — lookup de código e hierarquia no Admin.
- [`spec_itemClassificacao_criar_filho.md`](spec_itemClassificacao_criar_filho.md) — gravação de filho com vigência contida na mãe.
- [`spec_classificador-receita.md`](spec_classificador-receita.md) § **Convenções** — prefixo `ITEMRH`.

Termos *deve* / *não deve* / *pode* conforme RFC 2119 (ver `_dev/spec_conventions.md` **Referências**).

## Como citar este documento

| Mecanismo          | Uso                                                                 |
| ------------------ | ------------------------------------------------------------------- |
| **Seção numerada** | `§ N` / `§ N.M` — navegação neste arquivo.                          |
| **ID normativo**   | `ITEMRH-NN` — citação estável.                                      |
| **Prefixo**        | `ITEMRH` — ver § **Convenções** em `spec_classificador-receita.md`. |

**Índice de IDs normativos deste arquivo:**

| ID        | Tema        | Seção | Resumo                                                                                                                                                                                        |
| --------- | ----------- | ----- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ITEMRH-01 | Alinhamento | 1.1   | O vínculo pai–filho **deve** respeitar o nível **imediatamente anterior**.                                                                                                                    |
| ITEMRH-02 | Alinhamento | 1.2   | O mãe **deve** representar a versão **não detalhada** do filho no nível subsequente, com **zeros canônicos** na cauda.                                                                        |
| ITEMRH-03 | Alinhamento | 1.3   | A validação **deve** considerar **vigência** e **registro**; **não deve** limitar-se ao status ativo no instante atual.                                                                       |
| ITEMRH-04 | Estrutura   | 2.1   | Item com `nivel_numero > 1`: `parent_item_id` **obrigatório**.                                                                                                                                |
| ITEMRH-05 | Estrutura   | 2.2   | Item com `nivel_numero = 1`: `parent_item_id` **deve** ser nulo.                                                                                                                              |
| ITEMRH-06 | Estrutura   | 2.3   | O `parent_item_id` **deve** referenciar item com `matriz = true` (mãe **não** pode ser detalhe).                                                                                              |
| ITEMRH-07 | Estrutura   | 2.4   | O mãe **deve** estar no nível imediatamente anterior (`nivel_numero_mãe = nivel_numero_filho − 1`).                                                                                           |
| ITEMRH-08 | Estrutura   | 2.5   | `nivel_id` **deve** coincidir com o nível inferido de `receita_cod`; divergência → erro em `nivel_id` (Admin: **R-nivel-submit**; servidor: `validate_item_nivel_id_receita_cod_derivation`). |
| ITEMRH-09 | Estrutura   | 2.6   | Mãe e filho **devem** pertencer à mesma `classificacao_id`.                                                                                                                                   |
| ITEMRH-10 | Semântica   | 2.7   | Campos com zeros canônicos **devem** ser tratados como **não discriminados**.                                                                                                                 |
| ITEMRH-11 | Temporal    | 2.8   | A vigência do mãe **deve conter integralmente** a vigência do filho (eixo temporal exigido para este vínculo na validação de domínio).                                                        |
| ITEMRH-12 | Segmentos   | 3.1   | Filho nível `N`: segmentos `1..N−1` do mãe **devem** ser iguais aos do filho.                                                                                                                 |
| ITEMRH-13 | Segmentos   | 3.2   | Segmentos `N..fim` do mãe **devem** estar em zero canônico do nível (ex.: `0`, `00`, `000` conforme máscara).                                                                                 |
| ITEMRH-14 | Segmentos   | 3.3   | Segmento do nível `N` no filho **deve** estar discriminado (diferente de zero canônico).                                                                                                      |
| ITEMRH-15 | Segmentos   | 3.4   | Segmentos `N+1..fim` no filho **devem** estar em zero canônico conforme máscara da classificação.                                                                                             |
| ITEMRH-16 | Temporal    | 2.8   | Aceite **deve** ser possível quando a vigência do mãe contém a do filho **mesmo** que o mãe não tenha registro ativo no sistema **hoje**. **(ITEMRH-11)**                                     |
| ITEMRH-17 | Aceite      | 4     | Os casos mínimos de § **4** **devem** ser respeitados pela validação de domínio (ilustram **ITEMRH-04**–**15**).                                                                              |

**Índice por tema:**

| Tema        | IDs                                                              |
| ----------- | ---------------------------------------------------------------- |
| Alinhamento | ITEMRH-01, ITEMRH-02, ITEMRH-03                                  |
| Estrutura   | ITEMRH-04, ITEMRH-05, ITEMRH-06, ITEMRH-07, ITEMRH-08, ITEMRH-09 |
| Semântica   | ITEMRH-10, ITEMRH-12, ITEMRH-13, ITEMRH-14, ITEMRH-15            |
| Temporal    | ITEMRH-11, ITEMRH-16                                             |
| Aceite      | ITEMRH-17                                                        |

---

## 1. Alinhamento

### 1.1 Hierarquia por nível **(ITEMRH-01)**

O pai é sempre o item no nível **imediatamente anterior** ao filho.

### 1.2 Semântica do código **(ITEMRH-02)**

O mãe codifica o prefixo comum até `N−1` e mantém zeros canônicos de `N` em diante — versão agregada/não detalhada do filho.

### 1.3 Bitemporalidade **(ITEMRH-03)**

Regras de domínio aplicam vigência (mundo) e registro (sistema). Validação **não** se restringe a “ativo agora” sem analisar intervalos.

---

## 2. Regras estruturais e temporais

### 2.1 `parent_item_id` obrigatório **(ITEMRH-04)**

`nivel_numero > 1` → `parent_item_id` preenchido.

### 2.2 Raiz sem pai **(ITEMRH-05)**

`nivel_numero = 1` → `parent_item_id` nulo.

### 2.3 Mãe matriz **(ITEMRH-06)**

Referência de pai com `matriz = false` → rejeição.

### 2.4 Nível do pai **(ITEMRH-07)**

Pai em nível diferente de `nivel_numero_filho − 1` → rejeição.

### 2.5 Coerência `nivel_id` ↔ código **(ITEMRH-08)**

`nivel_id` deve coincidir com o último segmento discriminado na máscara da classificação/vigência inferido de `receita_cod`.

| Camada   | Comportamento em divergência                                        |
| -------- | ------------------------------------------------------------------- |
| Admin    | **R-nivel-submit** (`spec_itemClassificacao_validar_hierarquia.md`) |
| Servidor | `validate_item_nivel_id_receita_cod_derivation`                     |

### 2.6 Mesma classificação **(ITEMRH-09)**

`classificacao_id` do filho e do mãe devem ser iguais.

### 2.7 Zeros canônicos **(ITEMRH-10)**

Segmento em zero canônico = não discriminado na comparação semântica.

### 2.8 Vigência do mãe contém a do filho **(ITEMRH-11**, **ITEMRH-16)**

Intervalo de vigência do mãe **deve** envolver integralmente o do filho. Registro inativo do mãe **no presente** **não** invalida o vínculo se a vigência ainda contiver a do filho **(ITEMRH-16)**.

---

## 3. Regra semântica por segmentos de código

Para filho no nível `N`:

### 3.1 Prefixo comum **(ITEMRH-12)**

Segmentos `1..N−1`: iguais entre mãe e filho.

### 3.2 Cauda do mãe **(ITEMRH-13)**

Segmentos `N..fim` no mãe: zero canônico por nível.

### 3.3 Discriminação no filho **(ITEMRH-14)**

Segmento do nível `N` no filho: discriminado (≠ zero canônico).

### 3.4 Cauda do filho **(ITEMRH-15)**

Segmentos `N+1..fim` no filho: zeros canônicos conforme máscara.

---

## 4. Casos de aceite mínimos **(ITEMRH-17)**

Cada linha abaixo **deve** ser reproduzida pela validação de domínio. Regras principais entre parênteses.

| Caso                                                                    | Resultado esperado   | Regras    |
| ----------------------------------------------------------------------- | -------------------- | --------- |
| Filho nível 1 com mãe informado                                         | Rejeita              | ITEMRH-05 |
| Filho nível 3 sem mãe                                                   | Rejeita              | ITEMRH-04 |
| Filho nível 4 com mãe nível 2                                           | Rejeita              | ITEMRH-07 |
| Filho nível 5 com mãe `matriz=false`                                    | Rejeita              | ITEMRH-06 |
| Filho nível 7 com prefixo diferente do mãe até nível 6                  | Rejeita              | ITEMRH-12 |
| Filho nível 7 com mãe correto, mas sem zeros canônicos de 8..fim no mãe | Rejeita              | ITEMRH-13 |
| Filho nível 7 com mãe correto, vigência incompatível                    | Rejeita              | ITEMRH-11 |
| Filho nível 7 com mãe correto e vigência compatível                     | Aceita               | ITEMRH-11 |
| Filho nível 7 com nível 7..fim do mãe sem zeros canônicos               | Rejeita              | ITEMRH-13 |
| Filho nível 7 com segmento do nível 7 em zero canônico                  | Rejeita              | ITEMRH-14 |
| Filho nível 7 com segmentos 8..fim sem zeros canônicos                  | Rejeita              | ITEMRH-15 |
| Filho nível 7 semanticamente correto, vigência incompatível             | Rejeita              | ITEMRH-11 |
| Filho nível 7 semanticamente correto e vigência compatível              | Aceita               | ITEMRH-11 |
| Mãe sem registro ativo hoje, vigência ainda contém a do filho           | Aceita               | ITEMRH-16 |
| Código deriva nível 7, `nivel_id` aponta nível 3                        | Rejeita (`nivel_id`) | ITEMRH-08 |

---

## 5. Specs relacionadas

| Spec                                                                                           | Papel                                                                 |
| ---------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| [`spec_itemClassificacao_validar_hierarquia.md`](spec_itemClassificacao_validar_hierarquia.md) | UX Admin: salto de nível, intermediários, confirmação antes do submit |
| [`spec_itemClassificacao_foreignKeys_lookup.md`](spec_itemClassificacao_foreignKeys_lookup.md) | Endpoints JSON de lookup de código e hierarquia                       |
| [`spec_itemClassificacao_criar_filho.md`](spec_itemClassificacao_criar_filho.md)               | Fluxo de criação de filho e vigência na gravação                      |
