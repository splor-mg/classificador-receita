# Lookups JSON de código no Admin (`ItemClassificacao`)

Contrato HTTP/JSON dos endpoints usados no formulário **add/change** de `ItemClassificacao` para resolver item por código e derivar nível/mãe matriz. **Não substitui** `spec_itemClassificacao_regras_hierarquia.md` (domínio) nem `spec_itemClassificacao_validar_hierarquia.md` (submit e salto de nível).

## Objetivo

Documentar como o projeto **deve** expor e consumir os endpoints `lookup-parent-by-code` e `lookup-hierarchy-by-code` no Django Admin.

Premissa: lógica de negócio em `apps/core/classification_item_code_lookup.py`; views em `ItemClassificacaoAdmin` delegam e retornam `JsonResponse`.

## Referências

- `apps/core/classification_item_code_lookup.py` — implementação ORM.
- `apps/core/templates/admin/core/change_form.html` — consumo JS.
- `apps/core/code_name.js` — consumo complementar.
- [`spec_itemClassificacao_regras_hierarquia.md`](spec_itemClassificacao_regras_hierarquia.md) — regras de `parent_item_id`.
- [`spec_itemClassificacao_validar_hierarquia.md`](spec_itemClassificacao_validar_hierarquia.md) — **R-nivel-submit**; salto de nível no submit.
- [`spec_itemClassificacao_criar_filho.md`](spec_itemClassificacao_criar_filho.md) — **(G5)** / **(G6)** (escrita programática de mãe).
- [`spec_itemClassificacao_mascara_apresentacao.md`](spec_itemClassificacao_mascara_apresentacao.md) — `format_receita_cod_by_vigencia`.
- [`spec_classificador-receita.md`](spec_classificador-receita.md) § **Convenções** — prefixo `ITEMLKP`.

Termos *deve* / *não deve* / *pode* conforme RFC 2119 (ver `_dev/spec_conventions.md` **Referências**).

**Migração de símbolos legados:**

| Legado                      | ID atual                  |
| --------------------------- | ------------------------- |
| `N1`–`N3`                   | `ITEMLKP-25`–`ITEMLKP-27` |
| `R1`–`R3`                   | `ITEMLKP-33`–`ITEMLKP-35` |
| `C1`–`C4`                   | `ITEMLKP-36`–`ITEMLKP-39` |
| `T-notices.1`–`T-notices.4` | `ITEMLKP-42`–`ITEMLKP-45` |

## Como citar este documento

| Mecanismo          | Uso                                                                  |
| ------------------ | -------------------------------------------------------------------- |
| **Seção numerada** | `§ N` / `§ N.M` — navegação neste arquivo.                           |
| **ID normativo**   | `ITEMLKP-NN` — citação estável.                                      |
| **Prefixo**        | `ITEMLKP` — ver § **Convenções** em `spec_classificador-receita.md`. |

**Índice de IDs normativos deste arquivo:**

| ID         | Tema       | Seção | Resumo                                                                                                                                                        |
| ---------- | ---------- | ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ITEMLKP-01 | Parent     | 2.1   | Rota `GET …/lookup-parent-by-code/`; URL name `admin:core_itemclassificacao_lookup_parent_by_code`; template `item_classificacao_parent_lookup_url`.          |
| ITEMLKP-02 | Parent     | 2.2   | Parâmetros obrigatórios: `code`, `vigencia_inicio`, `vigencia_fim`.                                                                                           |
| ITEMLKP-03 | Parent     | 2.2   | Parâmetro em falta → resposta “vazia” (shape abaixo), **sem** erro explícito.                                                                                 |
| ITEMLKP-04 | Parent     | 2.3   | Resposta **sempre** HTTP 200 com `pk`, `semantic_value`, `display_label`, `link_url` (strings; vazias se não encontrado).                                     |
| ITEMLKP-05 | Parent     | 2.4   | Seleção: `receita_cod` normalizado; registo ativo (`data_registro_fim = sentinela`); sobreposição de vigência; desempate `order_by("pk").first()`.            |
| ITEMLKP-06 | Hierarchy  | 3.1   | Rota `GET …/lookup-hierarchy-by-code/`; URL name `admin:core_itemclassificacao_lookup_hierarchy_by_code`; template `item_classificacao_hierarchy_lookup_url`. |
| ITEMLKP-07 | Hierarchy  | 3.2   | `code` obrigatório (só dígitos; `.` removidos); `vigencia_inicio`/`vigencia_fim` obrigatórios (`YYYY-MM-DD` ou `DD/MM/YYYY`); `classificacao_pk` opcional.    |
| ITEMLKP-08 | Erro       | 3.3   | `code` vazio → `ok: false`, «Informe o código canônico.»                                                                                                      |
| ITEMLKP-09 | Erro       | 3.3   | Vigência em falta → «Informe o período de vigência…»                                                                                                          |
| ITEMLKP-10 | Erro       | 3.3   | `vigencia_fim < vigencia_inicio` → «Período inválido…»                                                                                                        |
| ITEMLKP-11 | Erro       | 3.3   | `classificacao_pk` inválido → «Classificação inválida.»                                                                                                       |
| ITEMLKP-12 | Erro       | 3.3   | Caracteres não numéricos no código → mensagem «…apenas dígitos.»                                                                                              |
| ITEMLKP-13 | Erro       | 3.3   | Sem máscara de níveis → «Não foi possível determinar a estrutura…»                                                                                            |
| ITEMLKP-14 | Erro       | 3.3   | Código mais longo que máscara e cauda não só zeros → «Código excede o limite…»                                                                                |
| ITEMLKP-15 | Erro       | 3.3   | Sem segmento detalhado ≠ zero → «…não há nível detalhado diferente de zero.»                                                                                  |
| ITEMLKP-16 | Erro       | 3.3   | Detalhamento após nível derivado → «…há detalhamento após o nível derivado…»                                                                                  |
| ITEMLKP-17 | Hierarchy  | 3.4   | Sucesso `ok: true` com `normalized_code`, `effective_vigencia`, `derived_level`, `parent`.                                                                    |
| ITEMLKP-18 | Hierarchy  | 3.5   | `classificacao_pk` presente → queries de nível/mãe filtram por identidade semântica (`classificacao_identity_filters`).                                       |
| ITEMLKP-19 | Hierarchy  | 3.6   | Máscara: `digit_mask_for_classificacao_vigencia`; fallback `resolve_receita_cod_mask_context`.                                                                |
| ITEMLKP-20 | Hierarchy  | 3.7   | Mãe: código com zeros canônicos; candidatos `matriz=True`, `nivel_numero = derived − 1`, vigência e registo ativos (ordem de tentativas no Python).           |
| ITEMLKP-21 | Cliente    | 3.8   | No blur/change/init: se `parent.found`, substituir `parent_item_id` via `setParentItemIdProgrammatically` (**G6** — sem **G5**).                              |
| ITEMLKP-22 | Cliente    | 3.8   | No submit: regras em `spec_itemClassificacao_validar_hierarquia.md`; `nivel_id` **não** substituído (**R-nivel-submit**).                                     |
| ITEMLKP-23 | Notices    | 4.1   | Arbitragem entre **N ≥ 2** candidatos ativos → aviso em `notices` no bloco `parent` ou `derived_level`.                                                       |
| ITEMLKP-24 | Notices    | 4.1   | Frontend **deve** renderizar `notices` com `<ul class="messagelist hierarchy-autofill-warning">` em **paridade** entre `parent_item_id` e `nivel_id`.         |
| ITEMLKP-25 | Notices    | 4.2   | Contagem **N** via `qs.count()` antes de `first()`; **não** expor **N** no payload.                                                                           |
| ITEMLKP-26 | Notices    | 4.2   | **N ≥ 2** e registro escolhido → anexar frase normativa a `notices`; **N ≤ 1** → sem aviso.                                                                   |
| ITEMLKP-27 | Notices    | 4.2   | Ramos cobertos: mãe primário/fallback/alternativa; nível primário/alternativa (**ITEMLKP-28**–**32**).                                                        |
| ITEMLKP-28 | Aviso      | 4.3   | Texto mãe primário: «Foram encontradas {N} versões ativas compatíveis do item mãe; foi selecionada a versão mais recente.»                                    |
| ITEMLKP-29 | Aviso      | 4.3   | Texto mãe fallback: «…do item mãe no fallback; foi selecionada…»                                                                                              |
| ITEMLKP-30 | Aviso      | 4.3   | Texto mãe alternativa: «…do item mãe noutra classificação; foi selecionada…»                                                                                  |
| ITEMLKP-31 | Aviso      | 4.3   | Texto nível primário: «…do nível {K}; foi selecionada…» (`K = derived_level.number`).                                                                         |
| ITEMLKP-32 | Aviso      | 4.3   | Texto nível alternativa: «…do nível {K} noutra classificação; foi selecionada…»                                                                               |
| ITEMLKP-33 | Redação    | 4.4   | Padrão «versões ativas compatíveis do {recurso}» — substitui «matrizes ativas compatíveis».                                                                   |
| ITEMLKP-34 | Redação    | 4.4   | Frases terminam com «; foi selecionada a versão mais recente.»                                                                                                |
| ITEMLKP-35 | Redação    | 4.4   | Frases **não** referenciam ano civil, sentinela nem campos internos.                                                                                          |
| ITEMLKP-36 | Cliente    | 4.5   | Montar uma `<ul class="messagelist hierarchy-autofill-warning">` por campo quando houver `alternative` e/ou `notices`.                                        |
| ITEMLKP-37 | Cliente    | 4.5   | Ordem na `<ul>`: `alternative` primeiro, depois `notices` na ordem do servidor.                                                                               |
| ITEMLKP-38 | Cliente    | 4.5   | Antes de inserir, `clearHierarchyMessages(row)`.                                                                                                              |
| ITEMLKP-39 | Cliente    | 4.5   | `status.error` → `<ul class="errorlist hierarchy-autofill-error">`; **não** exibir `notices` com erro.                                                        |
| ITEMLKP-40 | Manutenção | 5.1   | Alterações de contrato JSON **devem** manter este arquivo alinhado ao módulo Python e ao JS consumidor.                                                       |
| ITEMLKP-41 | Manutenção | 5.1   | Nova FK temporal na hierarquia **deve** replicar paridade de `notices` (servidor + cliente).                                                                  |
| ITEMLKP-42 | Teste      | 5.2   | Duas linhas bitemporais para mesmo item mãe → `parent.notices` com frase **ITEMLKP-28**; `<ul>` amarela em `parent_item_id`.                                  |
| ITEMLKP-43 | Teste      | 5.2   | Duas linhas para mesmo `nivel_numero` → `derived_level.notices` **ITEMLKP-31**; `<ul>` em `nivel_id`.                                                         |
| ITEMLKP-44 | Teste      | 5.2   | Nível só noutra classificação (N≥2) → **ITEMLKP-32** + `alternative`; ambos na mesma `<ul>`.                                                                  |
| ITEMLKP-45 | Teste      | 5.2   | Uma versão ativa → `notices` vazio; sem `<ul>` amarela.                                                                                                       |

**Índice por tema:**

| Tema       | IDs                                              |
| ---------- | ------------------------------------------------ |
| Parent     | ITEMLKP-01 … ITEMLKP-05                          |
| Hierarchy  | ITEMLKP-06, ITEMLKP-07, ITEMLKP-17 … ITEMLKP-22  |
| Erro       | ITEMLKP-08 … ITEMLKP-16                          |
| Notices    | ITEMLKP-23 … ITEMLKP-27, ITEMLKP-28 … ITEMLKP-32 |
| Redação    | ITEMLKP-33 … ITEMLKP-35                          |
| Cliente    | ITEMLKP-21, ITEMLKP-22, ITEMLKP-36 … ITEMLKP-39  |
| Manutenção | ITEMLKP-40, ITEMLKP-41                           |
| Teste      | ITEMLKP-42 … ITEMLKP-45                          |

---

## Escopo

| Inclui                                               | Não inclui                                                        |
| ---------------------------------------------------- | ----------------------------------------------------------------- |
| Contrato JSON dos dois endpoints de lookup           | Validação de domínio no `clean()` do modelo                       |
| Parâmetros GET, shape de resposta, erros `ok: false` | Modais de salto de nível no submit                                |
| Regras de `notices` e renderização no Admin          | Política de união contígua de FK (`spec_foreignKeys_vigencia.md`) |

---

## 2. `lookup-parent-by-code`

### 2.1 Rota **(ITEMLKP-01)**

- **Rota:** `GET …/admin/core/itemclassificacao/lookup-parent-by-code/`
- **Nome URL:** `admin:core_itemclassificacao_lookup_parent_by_code`
- **Template:** `item_classificacao_parent_lookup_url` (`render_change_form`)

### 2.2 Parâmetros GET **(ITEMLKP-02**, **ITEMLKP-03)**

| Parâmetro         | Obrigatório | Descrição                                                              |
| ----------------- | ----------- | ---------------------------------------------------------------------- |
| `code`            | Sim         | Código Receita **sem pontos** (espaços ignorados; `.` removidos)       |
| `vigencia_inicio` | Sim         | Início da vigência do **filho** (string comparada nos filtros de data) |
| `vigencia_fim`    | Sim         | Fim da vigência do filho                                               |

Falta qualquer parâmetro → objeto vazio **(ITEMLKP-04)** sem erro explícito.

### 2.3 Resposta JSON **(ITEMLKP-04)**

Sempre HTTP **200**:

| Campo            | Tipo   | Significado                                                        |
| ---------------- | ------ | ------------------------------------------------------------------ |
| `pk`             | string | PK do item ou `""`                                                 |
| `semantic_value` | string | `receita_cod` formatado (`format_receita_cod_by_vigencia`) ou `""` |
| `display_label`  | string | `"{cod} - {nome}"` ou `""`                                         |
| `link_url`       | string | URL change do admin ou `""`                                        |

### 2.4 Critério de seleção **(ITEMLKP-05)**

- `receita_cod` igual ao código normalizado.
- Registo ativo: `data_registro_fim = TRANSACTION_TIME_SENTINEL` (aware se sentinela naive).
- Sobreposição: `data_vigencia_inicio <= vigencia_inicio` e `data_vigencia_fim >= vigencia_fim`.
- Vários candidatos: `order_by("pk").first()`.

---

## 3. `lookup-hierarchy-by-code`

### 3.1 Rota **(ITEMLKP-06)**

- **Rota:** `GET …/admin/core/itemclassificacao/lookup-hierarchy-by-code/`
- **Nome URL:** `admin:core_itemclassificacao_lookup_hierarchy_by_code`
- **Template:** `item_classificacao_hierarchy_lookup_url`

### 3.2 Parâmetros GET **(ITEMLKP-07)**

| Parâmetro          | Obrigatório | Descrição                                                                              |
| ------------------ | ----------- | -------------------------------------------------------------------------------------- |
| `code`             | Sim         | Código canônico só dígitos                                                             |
| `vigencia_inicio`  | Sim         | `YYYY-MM-DD` ou `DD/MM/YYYY`                                                           |
| `vigencia_fim`     | Sim         | Idem                                                                                   |
| `classificacao_pk` | Não         | PK da `Classificacao` no formulário; ausente = sem restrição primária de classificação |

### 3.3 Erros `ok: false` **(ITEMLKP-08**–**ITEMLKP-16)**

Resposta típica: `{"ok": false, "message": "<texto>"}`.

| ID         | Situação                    | Mensagem (resumo)                          |
| ---------- | --------------------------- | ------------------------------------------ |
| ITEMLKP-08 | `code` vazio                | Informe o código canônico.                 |
| ITEMLKP-09 | Vigência em falta           | Informe o período de vigência…             |
| ITEMLKP-10 | Período invertido           | Período inválido…                          |
| ITEMLKP-11 | `classificacao_pk` inválido | Classificação inválida.                    |
| ITEMLKP-12 | Não numérico                | …apenas dígitos.                           |
| ITEMLKP-13 | Sem máscara                 | Não foi possível determinar a estrutura…   |
| ITEMLKP-14 | Excede máscara              | Código excede o limite…                    |
| ITEMLKP-15 | Sem detalhe                 | …não há nível detalhado diferente de zero. |
| ITEMLKP-16 | Detalhe após derivado       | …há detalhamento após o nível derivado…    |

### 3.4 Sucesso `ok: true` **(ITEMLKP-17)**

```json
{
  "ok": true,
  "normalized_code": "<string>",
  "effective_vigencia": {
    "inicio": "<ISO date>",
    "fim": "<ISO date>",
    "overridden": <bool>
  },
  "derived_level": { },
  "parent": { }
}
```

- **`normalized_code`:** comprimento ajustado à máscara (`ljust` com `0` ou truncagem se cauda extra só zeros).
- **`effective_vigencia`:** `effective_vigencia_for_item_hierarchy_lookup`; `overridden` se janela alinhada ao universo da classificação.

#### `derived_level`

| Campo           | Significado                                                                   |
| --------------- | ----------------------------------------------------------------------------- |
| `number`        | `nivel_numero` inferido (1-based)                                             |
| `pk`            | PK do `NivelHierarquico` ou `""`                                              |
| `display_label` | `"{nivel_id} - {nivel_nome}"` ou vazio                                        |
| `status`        | `severity`: `ok` \| `warning` \| `error`; `message`; `alternative` (opcional) |
| `notices`       | Avisos não bloqueantes — § **4**                                              |

**`alternative` (nível):** nível noutra classificação → `classificacao` (`pk`, `classificacao_id`, `display_label`, `link_url`) + `message`.

#### `parent`

| Campo                                             | Significado                                                                                 |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| `required`                                        | `true` se `derived_level.number > 1`                                                        |
| `found`                                           | Matriz mãe resolvida (inclui fallbacks no código)                                           |
| `pk`, `code`, `name`, `display_label`, `link_url` | Dados do mãe ou vazios                                                                      |
| `status`                                          | `severity` / `message` / `alternative`; erro “detalhe em vez de matriz” pode incluir `html` |
| `notices`                                         | § **4**                                                                                     |

### 3.5 Âmbito de classificação **(ITEMLKP-18)**

Com `classificacao_pk` válido, queries de nível e mãe primária filtram por identidade semântica da classificação.

### 3.6 Máscara **(ITEMLKP-19)**

`digit_mask_for_classificacao_vigencia(class_pk, effective_inicio, effective_fim)`; se vazia, `resolve_receita_cod_mask_context(None, input_length=len(code), on_date=hoje)`.

### 3.7 Resolução do item mãe **(ITEMLKP-20)**

Código mãe por zeros canônicos a partir do nível derivado; candidatos `matriz=True`, `nivel_numero = derived − 1`, vigência e registo ativos. Ordem de tentativas documentada em comentários no módulo Python.

### 3.8 Consumo no cliente **(ITEMLKP-21**, **ITEMLKP-22)**

**Alteração do código** (`code_blur`, `classificacao_change`, `init`):

- `parent.found` → substituir `parent_item_id` via `setParentItemIdProgrammatically` (`__suppressChildCodeSuggestOnParentChange`) — **não** dispara **(G5)** (**G6** em `spec_itemClassificacao_criar_filho.md`).
- Lookup sem mãe → erro/limpeza conforme `severity` (sem preservar mãe manual).

**Submit:**

- Regras em `spec_itemClassificacao_validar_hierarquia.md`; pode preservar mãe quando lookup falha ou PK difere.
- **`nivel_id` não é substituído** — validar coerência com `derived_level.number` (**R-nivel-submit**).

---

## 4. Avisos (`notices`) — paridade mãe / nível

### 4.1 Emissão e paridade visual **(ITEMLKP-23**, **ITEMLKP-24)**

Quando o resolver arbitra entre **N ≥ 2** candidatos ativos compatíveis com a vigência para FK temporal da hierarquia, o lookup **deve** sinalizar em `notices` (`parent` ou `derived_level`). O frontend **deve** usar `<ul class="messagelist hierarchy-autofill-warning">` com `<li class="warning">` nos campos `parent_item_id` e `nivel_id`.

### 4.2 Regras de emissão (servidor) **(ITEMLKP-25**–**ITEMLKP-27)**

- **(ITEMLKP-25):** **N** = `qs.count()` antes de `first()`; não expor **N** no JSON.
- **(ITEMLKP-26):** **N ≥ 2** e registro escolhido → frase em `notices`; **N ≤ 1** → sem aviso.
- **(ITEMLKP-27):** Ramos: mãe primário, mãe fallback último nível detalhado, mãe alternativa noutra classificação; nível primário; nível alternativa.

### 4.3 Textos normativos (pt-BR) **(ITEMLKP-28**–**ITEMLKP-32)**

| Cenário           | ID         | Texto                                                                                                                        |
| ----------------- | ---------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Mãe primário      | ITEMLKP-28 | `Foram encontradas {N} versões ativas compatíveis do item mãe; foi selecionada a versão mais recente.`                       |
| Mãe fallback      | ITEMLKP-29 | `Foram encontradas {N} versões ativas compatíveis do item mãe no fallback; foi selecionada a versão mais recente.`           |
| Mãe alternativa   | ITEMLKP-30 | `Foram encontradas {N} versões ativas compatíveis do item mãe noutra classificação; foi selecionada a versão mais recente.`  |
| Nível primário    | ITEMLKP-31 | `Foram encontradas {N} versões ativas compatíveis do nível {K}; foi selecionada a versão mais recente.`                      |
| Nível alternativa | ITEMLKP-32 | `Foram encontradas {N} versões ativas compatíveis do nível {K} noutra classificação; foi selecionada a versão mais recente.` |

### 4.4 Redação **(ITEMLKP-33**–**ITEMLKP-35)**

- **(ITEMLKP-33):** padrão «versões ativas compatíveis do {recurso}».
- **(ITEMLKP-34):** sufixo «; foi selecionada a versão mais recente.» (arbitragem por `-data_vigencia_inicio`, `-data_registro_inicio`, `-pk`).
- **(ITEMLKP-35):** sem ano civil, sentinela nem campos internos na mensagem ao usuário.

### 4.5 Consumo no cliente **(ITEMLKP-36**–**ITEMLKP-39)**

- **(ITEMLKP-36):** uma `<ul class="messagelist hierarchy-autofill-warning">` por `.form-row` quando houver `alternative` e/ou `notices`; mesmo `marginTop` nos dois campos.
- **(ITEMLKP-37):** ordem: `alternative` primeiro, depois cada `notices`.
- **(ITEMLKP-38):** `clearHierarchyMessages(row)` antes de inserir nova `<ul>`.
- **(ITEMLKP-39):** `severity = error` → `<ul class="errorlist hierarchy-autofill-error">`; não exibir `notices` com erro.

---

## 5. Manutenção e testes

### 5.1 Manutenção **(ITEMLKP-40**, **ITEMLKP-41)**

Alterações de contrato JSON **devem** manter este arquivo, `classification_item_code_lookup.py` e JS (`change_form` / `code_name.js`) alinhados. Nova FK temporal exposta pelo endpoint **deve** replicar contagem local, `notices` e renderização cliente.

### 5.2 Testes recomendados **(ITEMLKP-42**–**ITEMLKP-45)**

| ID         | Cenário                                                                                                                           |
| ---------- | --------------------------------------------------------------------------------------------------------------------------------- |
| ITEMLKP-42 | Duas linhas bitemporais ativas para mesmo item mãe → `parent.notices` **ITEMLKP-28**; `<ul>` em `parent_item_id`                  |
| ITEMLKP-43 | Duas linhas para mesmo `nivel_numero` na classificação selecionada → `derived_level.notices` **ITEMLKP-31**; `<ul>` em `nivel_id` |
| ITEMLKP-44 | Nível só noutra classificação (N≥2) → **ITEMLKP-32** + `alternative` na mesma `<ul>`                                              |
| ITEMLKP-45 | Uma versão ativa → `notices` vazio; sem `<ul>` amarela                                                                            |
