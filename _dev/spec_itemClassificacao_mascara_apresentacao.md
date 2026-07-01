# Apresentação de `receita_cod` com máscara no Admin

Política de **máscara visual** sobre `receita_cod` em telas do Django Admin de `ItemClassificacao` — changelist, FK semântica (`parent_item_id`) e protocolo **B1** de edição no formulário add/change. **Não substitui** `spec_foreignKeys_vigencia.md` (união contígua em validação de FK) nem regra estrita em lookups JSON e sugestão de código filho.

## Objetivo

Definir como o projeto **deve** formatar `receita_cod` para **exibição** no Admin (tier estrito + tier secundário) e como o input editável **deve** aceitar entrada mascarada preservando persistência só com dígitos.

Premissa: `receita_cod` armazenado como string numérica 8–13 dígitos; máscara derivada de `NivelHierarquico.numero_digitos` (bitemporal).

## Referências

- `apps/core/admin_formatters.py` — `format_receita_cod_by_vigencia`, tier 2, `format_receita_cod_for_admin_display`.
- `apps/core/admin.py` — `receita_cod_formatado`, `semantic_value_resolver` de `parent_item_id`.
- `apps/core/templates/admin/core/change_form.html` — protocolo **B1** no cliente.
- `apps/core/forms.py` — `ItemClassificacaoForm.clean` (B1 persistência).
- `apps/core/tests_classification_item_mascara.py`, `tests_admin_formatters.py`.
- [`spec_foreignKeys_vigencia.md`](spec_foreignKeys_vigencia.md) — união contígua (distinta desta spec).
- [`spec_itemClassificacao_foreignKeys_lookup.md`](spec_itemClassificacao_foreignKeys_lookup.md) — tier 1 puro nos endpoints JSON.
- [`spec_itemClassificacao_formulario.md`](spec_itemClassificacao_formulario.md) — **ITEMFORM-03** (**B1.5** / **B1.8**).
- [`spec_itemClassificacao_editar_codigo.md`](spec_itemClassificacao_editar_codigo.md) — normalização **B1** no blur da change.
- [`spec_django.md`](spec_django.md) — convenções Django.
- [`spec_classificador-receita.md`](spec_classificador-receita.md) § **Convenções** — prefixo `ITEMMASK`.

Termos *deve* / *não deve* / *pode* conforme RFC 2119 (ver `_dev/spec_conventions.md` **Referências**).

**Migração de símbolos legados:**

| Legado                       | ID atual                    |
| ---------------------------- | --------------------------- |
| `D1`–`D4`                    | `ITEMMASK-01`–`ITEMMASK-04` |
| `B1.1`–`B1.11`               | `ITEMMASK-12`–`ITEMMASK-22` |
| `T-1`–`T-8`                  | `ITEMMASK-25`–`ITEMMASK-32` |
| `T-B1.5`, `T-B1.6`, `T-B1.8` | `ITEMMASK-33`–`ITEMMASK-35` |

## Como citar este documento

| Mecanismo          | Uso                                                                   |
| ------------------ | --------------------------------------------------------------------- |
| **Seção numerada** | `§ N` / `§ N.M` — navegação neste arquivo.                            |
| **ID normativo**   | `ITEMMASK-NN` — citação estável.                                      |
| **Prefixo**        | `ITEMMASK` — ver § **Convenções** em `spec_classificador-receita.md`. |

**Índice de IDs normativos deste arquivo:**

| ID          | Tema          | Seção | Resumo                                                                                                                                  |
| ----------- | ------------- | ----- | --------------------------------------------------------------------------------------------------------------------------------------- |
| ITEMMASK-01 | Decisão       | 2.1   | Tier 1: regra estrita `format_receita_cod_by_vigencia` permanece primária.                                                              |
| ITEMMASK-02 | Decisão       | 2.2   | Tier 2: `_resolve_secondary_digit_mask_for_admin_display` **somente** quando tier 1 falha.                                              |
| ITEMMASK-03 | Decisão       | 2.3   | Ambos falham → `receita_cod` **bruto**; sem terceiro fallback.                                                                          |
| ITEMMASK-04 | Decisão       | 2.4   | Tier 2 **isolado** em `format_receita_cod_for_admin_display`; **não** em validação, lookups lógicos, sugestão filho, exports.           |
| ITEMMASK-05 | Tier 1        | 3.1   | Por `nivel_ref`: linha ativa com vigência **contendo integralmente** a do item; `sum(numero_digitos) == len(codigo)`.                   |
| ITEMMASK-06 | Tier 2        | 3.2   | **S1:** candidatas ativas com `vig_inicio ≤ registro.vig_fim` e `vig_fim ≥ registro.vig_fim` (âncora em `data_vigencia_fim` do item).   |
| ITEMMASK-07 | Tier 2        | 3.2   | **S2:** desempate por maior `data_vigencia_fim` da candidata.                                                                           |
| ITEMMASK-08 | Tier 2        | 3.2   | **S3:** empate → maior `data_registro_inicio`.                                                                                          |
| ITEMMASK-09 | Tier 2        | 3.2   | Sem candidata **S1** para algum `nivel_ref` → **sem** relaxamento extra; tende a fallback bruto (**intencional**).                      |
| ITEMMASK-10 | Tier          | 3.3   | `data_registro_fim ≠ sentinela` → **excluídas** de tier 1 e tier 2.                                                                     |
| ITEMMASK-11 | Distinção     | 4     | Resolução de máscara (resposta **singular**) **≠** união contígua de FK (**ITEMMASK** vs `FKVIG`).                                      |
| ITEMMASK-12 | B1            | 5.1   | Blur é autoridade: saneamento, validação de tamanho, reaplicação de máscara.                                                            |
| ITEMMASK-13 | B1            | 5.2   | Após máscara aplicada uma vez na sessão, foco **não** remove pontos.                                                                    |
| ITEMMASK-14 | B1            | 5.3   | Troca de `classificacao_id`/estrutura dispara reaplicação de máscara.                                                                   |
| ITEMMASK-15 | B1            | 5.4   | Sem máscara resolvível → dígitos; blur formata quando passar a haver máscara.                                                           |
| ITEMMASK-16 | B1            | 5.5   | Entrada add/change: aceitar `0-9` e `.`; bloquear/remover demais caracteres sem apagar pontos válidos.                                  |
| ITEMMASK-17 | B1            | 5.6   | Colagem: sanitizar para `0-9` e `.`; pipeline de blur.                                                                                  |
| ITEMMASK-18 | B1            | 5.7   | Blur corrige pontos inválidos/excedentes → forma canônica quando compatível.                                                            |
| ITEMMASK-19 | B1            | 5.8   | Submit envia `receita_cod` **somente dígitos** (contrato model/BD).                                                                     |
| ITEMMASK-20 | B1            | 5.9   | `maxlength` do widget pode exceder 13 para exibição/colagem; validação 8–13 no backend.                                                 |
| ITEMMASK-21 | B1            | 5.10  | Sugestão automática de código filho deixa estado «máscara já aplicada».                                                                 |
| ITEMMASK-22 | B1            | 5.11  | Lookups e fluxos dependentes operam sobre dígitos normalizados.                                                                         |
| ITEMMASK-23 | Implementação | 6.1   | `format_receita_cod_for_admin_display` — sufixo `_for_admin_display`; só changelist e `semantic_value_resolver` de `ItemClassificacao`. |
| ITEMMASK-24 | Implementação | 6.2   | Cache `_nivel_digit_cache`: chaves tier 1 `(vig_inicio, vig_fim)`; tier 2 `("secondary-admin-display", vig_fim)`.                       |
| ITEMMASK-25 | Teste         | 7     | **T-1:** tier 1 sucede → formatação histórica (regressão).                                                                              |
| ITEMMASK-26 | Teste         | 7     | **T-2:** split bitemporal; item cruza junção → tier 2 formata.                                                                          |
| ITEMMASK-27 | Teste         | 7     | **T-3:** desempate tier 2 por `data_vigencia_fim`.                                                                                      |
| ITEMMASK-28 | Teste         | 7     | **T-4:** desempate por `data_registro_inicio`.                                                                                          |
| ITEMMASK-29 | Teste         | 7     | **T-5:** tier 2 falha → bruto (**ITEMMASK-03**).                                                                                        |
| ITEMMASK-30 | Teste         | 7     | **T-6:** linhas encerradas em transação ignoradas.                                                                                      |
| ITEMMASK-31 | Teste         | 7     | **T-7:** código vazio → `""` sem query.                                                                                                 |
| ITEMMASK-32 | Teste         | 7     | **T-8:** `parent_item_id` display paridade changelist (cenário T-2).                                                                    |
| ITEMMASK-33 | Teste         | 7     | **T-B1.5:** bloqueio de letras/vírgulas; pontos preservados.                                                                            |
| ITEMMASK-34 | Teste         | 7     | **T-B1.6:** colagem com/sem máscara; blur canónico.                                                                                     |
| ITEMMASK-35 | Teste         | 7     | **T-B1.8:** POST mascarado → gravação só dígitos.                                                                                       |

**Índice por tema:**

| Tema          | IDs                       |
| ------------- | ------------------------- |
| Decisão       | ITEMMASK-01 … ITEMMASK-04 |
| Tier 1        | ITEMMASK-05               |
| Tier 2        | ITEMMASK-06 … ITEMMASK-09 |
| Exclusão      | ITEMMASK-10               |
| Distinção FK  | ITEMMASK-11               |
| B1            | ITEMMASK-12 … ITEMMASK-22 |
| Implementação | ITEMMASK-23, ITEMMASK-24  |
| Teste         | ITEMMASK-25 … ITEMMASK-35 |

---

## Escopo

| Inclui                                                    | Não inclui                                          |
| --------------------------------------------------------- | --------------------------------------------------- |
| Coluna `receita_cod_formatado` na changelist              | Validação de FK por união contígua (**FKVIG**)      |
| Display FK `parent_item_id` via `semantic_value_resolver` | Lookups JSON com tier 2 (**ITEMLKP** — tier 1 puro) |
| Protocolo **B1** no input add/change                      | Sugestão de código filho (regra estrita)            |
| Subtítulo do change form com máscara                      | Exports e consumidores não-admin                    |

---

## 1. Contexto

`receita_cod` persiste como `^[0-9]{8,13}$`. A máscara com pontos deriva de `NivelHierarquico.numero_digitos`, que varia no tempo (bitemporal).

A regra estrita (`format_receita_cod_by_vigencia`) exige, por `nivel_ref`, **uma** linha ativa cuja vigência **contenha integralmente** a do item — correta quando a resposta deve ser **inequívoca**.

Em telas de admin, splits bitemporais de nível podem fazer itens cuja vigência cruza a junção exibirem código **bruto** enquanto vizinhos permanecem mascarados — inconsistência visual indesejada na changelist e no display de «Item Mãe».

---

## 2. Decisão de apresentação no Admin

Em telas que **apresentam** `receita_cod`, o sistema **deve** **tentar** máscara sempre:

### 2.1 Tier 1 primário **(ITEMMASK-01)**

Manter `format_receita_cod_by_vigencia` como primeira tentativa.

### 2.2 Tier 2 secundário **(ITEMMASK-02)**

`_resolve_secondary_digit_mask_for_admin_display` **apenas** se tier 1 falhar.

### 2.3 Fallback bruto **(ITEMMASK-03)**

Ambos falham → dígitos sem pontos; sem placeholder explícito.

### 2.4 Isolamento **(ITEMMASK-04)**

Tier 2 **somente** via `format_receita_cod_for_admin_display`. Validação, lookups que alimentam lógica do cliente, sugestão de filho e exports usam **tier 1 puro**.

---

## 3. Resolução em dois níveis

### 3.1 Tier 1 — estrito **(ITEMMASK-05)**

Por cada `nivel_ref` distinto:

- `data_registro_fim = TRANSACTION_TIME_SENTINEL`
- `data_vigencia_inicio ≤ item.data_vigencia_inicio`
- `data_vigencia_fim ≥ item.data_vigencia_fim`
- Coletar `numero_digitos` ordenados por `nivel_ref`

Máscara compatível: não vazia, sem zeros/falsy, `sum(digit_mask) == len(receita_cod)`.

### 3.2 Tier 2 — secundário **(ITEMMASK-06**–**ITEMMASK-09)**

Por `nivel_ref`, quando tier 1 falha:

| Etapa  | Regra                                                                    | ID          |
| ------ | ------------------------------------------------------------------------ | ----------- |
| **S1** | Candidatas ativas; contenção ancorada em `data_vigencia_fim` do **item** | ITEMMASK-06 |
| **S2** | Maior `data_vigencia_fim` da candidata                                   | ITEMMASK-07 |
| **S3** | Empate → maior `data_registro_inicio`                                    | ITEMMASK-08 |

Mesmo teste de compatibilidade do tier 1. Sem candidata S1 para um `nivel_ref` → sem relaxamento adicional → fallback bruto **(ITEMMASK-09)**.

### 3.3 Linhas encerradas **(ITEMMASK-10)**

`data_registro_fim ≠ TRANSACTION_TIME_SENTINEL` → excluídas de ambos os tiers.

---

## 4. Distinção de `spec_foreignKeys_vigencia.md` **(ITEMMASK-11)**

| Política     | Pergunta                                       | Mecanismo                                                    |
| ------------ | ---------------------------------------------- | ------------------------------------------------------------ |
| **FKVIG**    | As versões da FK **juntas** cobrem o filho?    | União contígua                                               |
| **ITEMMASK** | Qual `numero_digitos` aplicar por `nivel_ref`? | Linha única; tier 2 relaxa contenção com âncora em `vig_fim` |

Complementares, não conflitantes. Escolha explícita em cada ponto do código.

---

## 5. Edição do input — protocolo B1

Contrato de persistência inalterado: BD só dígitos.

### 5.1 Blur autoridade **(ITEMMASK-12)**

Saneamento, validação de tamanho, reaplicação de máscara ao perder foco.

### 5.2 Máscara persistente no foco **(ITEMMASK-13)**

Após primeira aplicação bem-sucedida na sessão, foco subsequente **não** remove pontos.

### 5.3 Reaplicação estrutural **(ITEMMASK-14)**

Mudança de `classificacao_id`/estrutura → atualizar máscara.

### 5.4 Ausência temporária de máscara **(ITEMMASK-15)**

Exibir dígitos; blur formata quando máscara ficar resolvível.

### 5.5 Digitação **(ITEMMASK-16)**

Add/change: `0-9` e `.`; demais caracteres bloqueados (`beforeinput`) ou removidos sem apagar pontos válidos.

### 5.6 Colagem **(ITEMMASK-17)**

Sanitizar para `0-9` e `.`; mesmo pipeline do blur.

### 5.7 Correção no blur **(ITEMMASK-18)**

Pontos inválidos/excedentes → forma canônica quando compatível.

### 5.8 Persistência **(ITEMMASK-19)**

Submit/POST: apenas dígitos.

### 5.9 `maxlength` do widget **(ITEMMASK-20)**

Pode ser >13 para UI; validação normativa 8–13 no backend.

### 5.10 Sugestão de filho **(ITEMMASK-21)**

Preenchimento com `receita_cod_display` → estado «máscara aplicada».

### 5.11 Fluxos dependentes **(ITEMMASK-22)**

Lookups e lógica usam versão normalizada (dígitos).

---

## 6. Implementação de referência

### 6.1 Escopo da função composta **(ITEMMASK-23)**

| Módulo / ponto                                                     | Papel                    |
| ------------------------------------------------------------------ | ------------------------ |
| `admin_formatters.format_receita_cod_by_vigencia`                  | Tier 1 puro (uso geral)  |
| `admin_formatters._resolve_secondary_digit_mask_for_admin_display` | Tier 2                   |
| `admin_formatters.format_receita_cod_for_admin_display`            | Composição admin         |
| `admin.py` `receita_cod_formatado`                                 | Changelist               |
| `semantic_fk_config["parent_item_id"]`                             | Display Item Mãe         |
| `change_form.html`                                                 | B1 cliente               |
| `forms.ItemClassificacaoForm.clean`                                | B1 servidor              |
| `_apply_digit_mask`                                                | Utilitário compartilhado |

**Não** reutilizar `format_receita_cod_for_admin_display` em validação, modais normativos ou JSON que vira parâmetro de programa.

### 6.2 Cache **(ITEMMASK-24)**

`_nivel_digit_cache` em `ItemClassificacaoAdmin`: chaves tier 1 `(data_vigencia_inicio, data_vigencia_fim)`; tier 2 `("secondary-admin-display", data_vigencia_fim)`.

---

## 7. Casos de teste recomendados **(ITEMMASK-25**–**ITEMMASK-35)**

| ID          | Caso                                                                      |
| ----------- | ------------------------------------------------------------------------- |
| ITEMMASK-25 | Tier 1 sucede — regressão                                                 |
| ITEMMASK-26 | Split `NIVEL-3` 2018–2026-01 / 2026-02–∞; item `[2026-01-01, ∞]` → tier 2 |
| ITEMMASK-27 | Duas candidatas S1; vence maior `vig_fim`                                 |
| ITEMMASK-28 | Empate `vig_fim`; vence `registro_inicio`                                 |
| ITEMMASK-29 | Sem candidata S1 → bruto                                                  |
| ITEMMASK-30 | Linhas encerradas ignoradas                                               |
| ITEMMASK-31 | Código vazio → `""`                                                       |
| ITEMMASK-32 | Display `parent_item_id` paridade T-2                                     |
| ITEMMASK-33 | T-B1.5 — `tests_classification_item_mascara.py`                           |
| ITEMMASK-34 | T-B1.6 — colagem manual/E2E                                               |
| ITEMMASK-35 | T-B1.8 — `test_clean_rejects_invalid_separator`                           |

---

## Specs relacionadas

| Spec                                                                                           | Relação                                           |
| ---------------------------------------------------------------------------------------------- | ------------------------------------------------- |
| [`spec_foreignKeys_vigencia.md`](spec_foreignKeys_vigencia.md)                                 | União contígua FK — **não** estendida aqui        |
| [`spec_itemClassificacao_foreignKeys_lookup.md`](spec_itemClassificacao_foreignKeys_lookup.md) | Endpoints JSON — tier 1 puro                      |
| [`spec_itemClassificacao_formulario.md`](spec_itemClassificacao_formulario.md)                 | Largura `37ch`; **ITEMMASK-16** / **ITEMMASK-19** |
| [`spec_itemClassificacao_editar_codigo.md`](spec_itemClassificacao_editar_codigo.md)           | Blur change com **B1**                            |
| [`spec_django.md`](spec_django.md)                                                             | Convenções Django                                 |
