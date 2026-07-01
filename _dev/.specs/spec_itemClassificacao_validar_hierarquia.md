# Validação de hierarquia no Admin (salto de nível e intermediários)

Comportamento **técnico** no Django Admin ao **adicionar** `ItemClassificacao`: aviso de **salto de nível**, validação de zeros canônicos intermediários, listagem de intermediários e integração no submit. **Não substitui** `spec_itemClassificacao_regras_hierarquia.md` (domínio) nem endpoints de lookup em `spec_itemClassificacao_foreignKeys_lookup.md`.

## Objetivo

Documentar como o projeto **deve** orquestrar confirmação antes do submit e análise de intermediários em torno de `parent_item_id` na **add**, alinhado a `code_parent_item_validation.py`, `admin.py` e `change_form.html`.

Premissa: regras de negócio gerais permanecem em **ITEMRH**; esta spec cobre o **fluxo Admin** implementado.

## Referências

- `apps/core/code_parent_item_validation.py`
- `apps/core/admin.py` — `ItemClassificacaoAdmin`
- `apps/core/templates/admin/core/change_form.html`
- `apps/core/forms.py` — estado raiz na change
- [`spec_itemClassificacao_regras_hierarquia.md`](spec_itemClassificacao_regras_hierarquia.md) — **ITEMRH**
- [`spec_itemClassificacao_foreignKeys_lookup.md`](spec_itemClassificacao_foreignKeys_lookup.md) — **ITEMLKP**; **R-nivel-submit**
- [`spec_itemClassificacao_criar_filho.md`](spec_itemClassificacao_criar_filho.md) — **(G5)** / **(G6)**
- [`spec_itemClassificacao_formulario.md`](spec_itemClassificacao_formulario.md) — **ITEMFORM** (limpar add)
- [`spec_classificador-receita.md`](spec_classificador-receita.md) § **Convenções** — prefixo `ITEMVH`

Termos *deve* / *não deve* / *pode* conforme RFC 2119 (ver `_dev/spec_conventions.md` **Referências**).

**Migração de símbolos legados:**

| Legado                         | ID atual                 |
| ------------------------------ | ------------------------ |
| Fluxo A `level_jump`           | `ITEMVH-01`, `ITEMVH-02` |
| Fluxo B zeros intermediários   | `ITEMVH-03`–`ITEMVH-05`  |
| Fluxo C intermediários         | `ITEMVH-06`, `ITEMVH-07` |
| `R-nivel-submit`               | `ITEMVH-26`–`ITEMVH-29`  |
| `R-root.1`–`R-root.5`          | `ITEMVH-30`–`ITEMVH-34`  |
| `T-nivel-submit.*`, `T-root.*` | § **10** (referência)    |

## Como citar este documento

| Mecanismo          | Uso                                                                 |
| ------------------ | ------------------------------------------------------------------- |
| **Seção numerada** | `§ N` / `§ N.M` — navegação neste arquivo.                          |
| **ID normativo**   | `ITEMVH-NN` — citação estável.                                      |
| **Prefixo**        | `ITEMVH` — ver § **Convenções** em `spec_classificador-receita.md`. |

**Índice de IDs normativos deste arquivo:**

| ID        | Tema           | Seção | Resumo                                                                                                                                                                                      |
| --------- | -------------- | ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ITEMVH-01 | Salto          | 3.A   | `level_jump: true` quando mãe/nível/classificação/vigência válidos; `child_n > 1`; `parent_n < child_n`; **`parent_n ≠ child_n − 1`**.                                                      |
| ITEMVH-02 | Salto          | 3.A   | `receita_cod` do filho **não** altera `level_jump`; modal pode aparecer com `intermediate_count: 0`.                                                                                        |
| ITEMVH-03 | Zeros          | 3.B   | Se `parent_n < nivel_n − 1`, segmentos do filho em `LP..L−2` **devem** ser zeros canônicos; senão erro em `receita_cod`.                                                                    |
| ITEMVH-04 | Zeros          | 3.B   | Mensagem: «Os campos correspondentes aos níveis entre… (nível **F**) e… (nível **M**)… zeros canônicos.»                                                                                    |
| ITEMVH-05 | Zeros          | 3.B   | No submit add, validar zeros **antes** do modal de salto; `ok: false` → erro vermelho, **sem** pop-up.                                                                                      |
| ITEMVH-06 | Intermediários | 3.C   | `analyze_intermediate_items_for_level_jump` monta `intermediate_count`, `intermediate_rows` para o modal.                                                                                   |
| ITEMVH-07 | Salto          | 3     | `level_jump` (níveis) e listagem (query) são **independentes** — ver **ITEMVH-02**.                                                                                                         |
| ITEMVH-08 | Endpoint       | 4     | `GET …/warn-parent-level-jump/`; URL name `admin:core_itemclassificacao_warn_parent_level_jump`; template `item_parent_level_jump_warn_url`.                                                |
| ITEMVH-09 | Endpoint       | 4     | GET: `parent_item_id`, `nivel_id`, `classificacao_id`, `vigencia_inicio`, `vigencia_fim`, `receita_cod` (opcional para máscara/exclude).                                                    |
| ITEMVH-10 | Endpoint       | 4     | Parâmetros obrigatórios em falta → `{"ok": true, "level_jump": false}`.                                                                                                                     |
| ITEMVH-11 | Algoritmo      | 5     | Saída antecipada se `parent_n >= child_n − 1` ou máscara indisponível.                                                                                                                      |
| ITEMVH-12 | Algoritmo      | 5     | Radical = primeiros `sum(mask[0:LP])` dígitos do **código do pai** (não do filho).                                                                                                          |
| ITEMVH-13 | Algoritmo      | 5     | Query: mesma `classificacao_id` do form, registo ativo, `receita_cod__startswith=radical`, **(T7)** com vigência **do form**, `nivel_numero` entre `parent_n+1` e `child_n−1` inclusive.    |
| ITEMVH-14 | Algoritmo      | 5     | Pós-filtro: excluir linhas com segmento de nível `nn` zero canônico ou `exclude_receita_cod` igual ao código da linha.                                                                      |
| ITEMVH-15 | Algoritmo      | 5     | Amostras no JSON: até `sample_limit` (admin: **3**).                                                                                                                                        |
| ITEMVH-16 | Decisão        | 6.1   | Vigência na query de intermediários = **somente** datas do formulário (sem união com vigência do mãe).                                                                                      |
| ITEMVH-17 | Decisão        | 6.1   | Fallback de máscara com vigência do mãe **só** para obter `mask`; **não** expande filtros `data_vigencia_*` da query.                                                                       |
| ITEMVH-18 | Decisão        | 6.2   | `classificacao_pk` na busca = PK do **formulário** (`busca_intermediarios_class_pk`).                                                                                                       |
| ITEMVH-19 | Modal          | 6.3   | Modal salto ao gravar: título «Atenção!»; texto mãe + filho; parágrafo «Além disso, existe…» se `intermediate_count > 0`; lista até 3; «Deseja continuar e gravar o registo?»; Cancelar/OK. |
| ITEMVH-20 | Modal          | 6.4   | **(G5)** troca de mãe com código preenchido — ver `spec_itemClassificacao_criar_filho.md` (resumo UX em § **6.4**).                                                                         |
| ITEMVH-21 | Submit         | 7     | Ordem add: `runCodeDigitValidation` → `syncHierarchyFromCode` → zeros intermediários → naming → `requestParentLevelJumpConfirmation` → POST/`clean()`.                                      |
| ITEMVH-22 | Submit         | 7     | No blur/change/init: lookup **pode** atualizar `parent_item_id` quando `parent.found`; no **submit** preservar mãe manual se lookup falhar ou PK diferente.                                 |
| ITEMVH-23 | Submit         | 7     | Após `.errornote` do Django, `syncHierarchyFromCode('init')` **não** corre.                                                                                                                 |
| ITEMVH-26 | Nível          | 8.1   | **R-nivel-submit — blur/init:** cliente **pode** autofill `nivel_id` por `derived_level.pk`.                                                                                                |
| ITEMVH-27 | Nível          | 8.2   | **R-nivel-submit — submit:** cliente **não** substitui `nivel_id`; compara PK selecionado com `derived_level.number`.                                                                       |
| ITEMVH-28 | Nível          | 8.3   | Servidor: `validate_item_nivel_id_receita_cod_derivation` em `clean()` — mesma regra.                                                                                                       |
| ITEMVH-29 | Nível          | 8.4   | Mensagem: «O nível hierárquico selecionado (nível **S**) não corresponde… (nível **D**)…»                                                                                                   |
| ITEMVH-30 | Raiz           | 9.1   | **R-root.1:** estado «raiz somente leitura» de `parent_item_id` quando `nivel_numero === 1` (change server-side; add client-side).                                                          |
| ITEMVH-31 | Raiz           | 9.2   | **R-root.2:** transição **reversível** para `nivel_numero > 1`.                                                                                                                             |
| ITEMVH-32 | Raiz           | 9.3   | **R-root.3:** ao ativar raiz, `parent_item_id` hidden **vazio** (`""`).                                                                                                                     |
| ITEMVH-33 | Raiz           | 9.4   | **R-root.4:** `semantic-lookup` com `metadata.nivel_numero` para PK de `nivel_id`; derivação por código via **ITEMLKP**.                                                                    |
| ITEMVH-34 | Raiz           | 9.5   | **R-root.5:** fora do submit, `syncHierarchyFromCode` **pode** recalcular `nivel_id` e estado raiz; no submit aplica **ITEMVH-27** antes de `setParentRootReadonlyState`.                   |
| ITEMVH-35 | Raiz           | 9.6   | `syncParentRootStateFromNivel` em `init`, `change` e `semantic-fk-changed` de `nivel_id`.                                                                                                   |
| ITEMVH-36 | Raiz           | 9.7   | Display raiz: «Sem item mãe», hachurado, lupa oculta, mensagem «Item raiz, de nível 1, não possui item mãe.»                                                                                |
| ITEMVH-37 | Teste          | 10    | Casos **T-nivel-submit***, **T-root*** e regressão de intermediários § **10** **devem** ser respeitados.                                                                                    |

**Índice por tema:**

| Tema               | IDs                             |
| ------------------ | ------------------------------- |
| Salto (A)          | ITEMVH-01, ITEMVH-02, ITEMVH-07 |
| Zeros (B)          | ITEMVH-03 … ITEMVH-05           |
| Intermediários (C) | ITEMVH-06                       |
| Endpoint           | ITEMVH-08 … ITEMVH-10           |
| Algoritmo          | ITEMVH-11 … ITEMVH-15           |
| Decisão            | ITEMVH-16 … ITEMVH-18           |
| Modal              | ITEMVH-19, ITEMVH-20            |
| Submit             | ITEMVH-21 … ITEMVH-23           |
| Nível (submit)     | ITEMVH-26 … ITEMVH-29           |
| Raiz               | ITEMVH-30 … ITEMVH-36           |
| Teste              | ITEMVH-37                       |

---

## Escopo

| Inclui                                                                        | Não inclui                                                  |
| ----------------------------------------------------------------------------- | ----------------------------------------------------------- |
| Add admin: salto de nível, zeros intermediários, listagem                     | Regras de domínio completas (**ITEMRH**)                    |
| Submit pipeline e **R-nivel-submit**                                          | Change — navegação por código (**ITEMEC**)                  |
| Estado raiz de `parent_item_id` (add + change)                                | Validação offline (`spec_validar_codigos.md`)               |
| Endpoints `warn-parent-level-jump/`, `validate-intermediate-canonical-zeros/` | **(G5)** completo — `spec_itemClassificacao_criar_filho.md` |

---

## 2. Glossário (implementação)

| Termo           | Significado                                                     |
| --------------- | --------------------------------------------------------------- |
| `LP`            | `nivel_numero` do item mãe                                      |
| `L` / `L_filho` | `nivel_numero` do nível do item novo (`nivel_id`)               |
| Salto de nível  | `LP < L_filho − 1`                                              |
| Radical         | Primeiros `sum(mask[0:LP])` dígitos do `receita_cod` do **mãe** |
| Zero canônico   | Segmento com todos os caracteres `'0'`                          |
| Registo ativo   | `data_registro_fim = transaction_time_sentinel_for_query()`     |

---

## 3. Três fluxos distintos

### 3.A Gatilho do aviso (`level_jump`) — **só níveis** **(ITEMVH-01**, **ITEMVH-02)**

**Onde:** `warn_parent_level_jump_view` → `warn_parent_level_jump_json_dict`.

**Condição `level_jump: true` (ITEMVH-01):** parâmetros válidos; mãe e nível filho existem; `child_n > 1`; `parent_n < child_n`; `parent_n ≠ child_n − 1`.

**(ITEMVH-02):** `receita_cod` **não** entra na condição booleana.

### 3.B Zeros canônicos intermediários — **bloqueio** **(ITEMVH-03**–**ITEMVH-05)**

**Onde:** `validate_intermediate_canonical_zeros_json_dict`, `validate_item_parent_item_rules`; endpoint `validate-intermediate-canonical-zeros/`.

Segmentos `LP..L−2` do filho devem ser zeros canônicos **(ITEMVH-03)**. Mensagem **(ITEMVH-04)**. No submit, validar **antes** do modal **(ITEMVH-05)**.

### 3.C Listagem de intermediários **(ITEMVH-06**, **ITEMVH-07)**

**Onde:** `analyze_intermediate_items_for_level_jump` via `warn_parent_level_jump_json_dict`.

Independente de **ITEMVH-01** para contagem — **ITEMVH-07**.

---

## 4. Endpoint `warn-parent-level-jump` **(ITEMVH-08**–**ITEMVH-10)**

Ver tabela de parâmetros GET **(ITEMVH-09)**. Faltando obrigatórios → **ITEMVH-10**.

---

## 5. Algoritmo `analyze_intermediate_items_for_level_jump` **(ITEMVH-11**–**ITEMVH-15)**

1. **(ITEMVH-11):** retorno vazio se `parent_n >= child_n − 1` ou sem máscara.
2. Máscara: `digit_mask_for_classificacao_vigencia(class_pk, vig_ini, vig_fim)`; fallback vigência do mãe **só para mask** **(ITEMVH-17)**.
3. **(ITEMVH-12):** radical do código do **pai**.
4. `nivel_min = parent_n + 1`; `nivel_max = child_n − 1`.
5. **(ITEMVH-13):** query ORM com filtros listados; vigência **do form** **(ITEMVH-16)**; `classificacao_id` do form **(ITEMVH-18)**.
6. **(ITEMVH-14):** pós-processamento Python por linha.
7. **(ITEMVH-15):** até 3 amostras no JSON.

**Retorno:** `count`, `nivel_numeros`, `nivel_semantic_by_numero`, `samples` (`pk`, `receita_cod`, `display_label`, `admin_url`, `nivel_numero`).

---

## 6. Decisões técnicas e modal

### 6.1 Vigência **(ITEMVH-16**, **ITEMVH-17)**

Query usa apenas `vig_ini`/`vig_fim` do GET do formulário.

### 6.2 Classificação **(ITEMVH-18)**

`busca_intermediarios_class_pk` = PK do form. Risco consciente se form ≠ classificação do mãe (seed/teste); produção: mesma classificação (**ITEMRH-09**).

### 6.3 Modal de salto ao gravar **(ITEMVH-19)**

- Título «Atenção!»
- Parágrafo 1: mãe (link código mascarado + rótulo nível) + filho (sem link no trecho principal)
- Se intermediários: «Além disso, existe …» com `no`/`nos`, contagem zero-padded `< 100`
- Lista até 3 links change
- «Deseja continuar e gravar o registo?» — Cancelar / OK

### 6.4 Modal **(G5)** **(ITEMVH-20)**

Detalhe normativo em `spec_itemClassificacao_criar_filho.md`. Resumo: só após sugestão bem-sucedida; tri-botão Cancelar | Manter Atual | Atualizar; snapshot de mãe anterior preservado.

---

## 7. Integração no submit (add) **(ITEMVH-21**–**ITEMVH-23)**

| Ordem | Etapa                                                        |
| ----- | ------------------------------------------------------------ |
| 1     | `runCodeDigitValidation`                                     |
| 2     | `syncHierarchyFromCode` + **ITEMVH-26**–**29** no submit     |
| 3     | `validateIntermediateCanonicalZerosOnSubmit` **(ITEMVH-05)** |
| 4     | naming                                                       |
| 5     | `requestParentLevelJumpConfirmation` **(ITEMVH-01)**         |
| 6     | POST → `clean()` / `validate_item_parent_item_rules`         |

**(ITEMVH-22):** blur atualiza mãe quando lookup encontra; submit preserva mãe manual.

**(ITEMVH-23):** pós-erro Django, sem `syncHierarchyFromCode('init')`.

Variáveis: `item_validate_intermediate_zeros_url`, `item_parent_level_jump_warn_url`.

---

## 8. Coerência `nivel_id` × código — **R-nivel-submit** **(ITEMVH-26**–**ITEMVH-29)**

| Gatilho                              | `nivel_id`                                                           |
| ------------------------------------ | -------------------------------------------------------------------- |
| blur / change / init **(ITEMVH-26)** | Pode autofill por `derived_level.pk`                                 |
| submit **(ITEMVH-27)**               | **Não** substituir; validar `nivel_numero` vs `derived_level.number` |
| servidor **(ITEMVH-28)**             | `validate_item_nivel_id_receita_cod_derivation`                      |

Mensagem **(ITEMVH-29)**. Inferência de **D:** `derive_nivel_numero_from_receita_cod_digits`.

**Testes:** T-nivel-submit.1–3 (§ **10**).

---

## 9. Item raiz — `parent_item_id` quando `nivel_numero = 1` **(ITEMVH-30**–**ITEMVH-36)**

Regra de domínio: **ITEMRH-05**. Esta seção cobre **renderização** Admin.

### 9.1 Change (servidor) **(ITEMVH-30**, **ITEMVH-36)**

`ItemClassificacaoForm.__init__` + widget `data_readonly_root` quando `instance.nivel_id.nivel_numero == 1`.

### 9.2 Add (cliente) **(ITEMVH-30**–**ITEMVH-35)**

`syncParentRootStateFromNivel(trigger)`:

1. `nivel_id` vazio → editável
2. fetch `semantic-lookup` → `metadata.nivel_numero`
3. `nivel_numero === 1` → estado raiz **(ITEMVH-36)**; senão restaurar editável **(ITEMVH-31)**

Gatilhos **(ITEMVH-35):** `init`, `change`, `semantic-fk-changed` em `nivel_id`.

### 9.3 Regras **(ITEMVH-32**–**ITEMVH-34)**

- **(ITEMVH-32):** hidden `parent_item_id` = `""` em raiz
- **(ITEMVH-33):** `metadata_resolver` em `semantic_fk_config["nivel_id"]`
- **(ITEMVH-34):** `syncHierarchyFromCode` fora do submit recalcula `nivel_id` e estado raiz; no submit valida **ITEMVH-27** primeiro

Payload `semantic-lookup` com `metadata: {"nivel_numero": N}` quando resolver declarado.

**Testes:** T-root.1–7 (§ **10**).

---

## 10. Casos de teste recomendados **(ITEMVH-37)**

### Nível no submit

- **T-nivel-submit.1:** código nível 7, `nivel_id` NIVEL-3 → erro em `nivel_id`, sem gravação
- **T-nivel-submit.2:** NIVEL-7 selecionado → prossegue (demais fluxos)
- **T-nivel-submit.3:** blur pode autofill após nível manual incorreto

### Raiz

- **T-root.1–7:** lupa NIVEL-1, derivação por código, reversão, postback, change server-side, `metadata` no lookup, transição nível 1→2 (**R-root.5**)

### Intermediários / salto

- Regressão tier máscara changelist (**ITEMMASK-32**)
- `level_jump: true` + `intermediate_count: 0` aceitável **(ITEMVH-07)**
- Cenário seed `1112529000000` (classificação do form vs mãe)

---

## Implementação de referência

| Peça           | Símbolo                                                                                            |
| -------------- | -------------------------------------------------------------------------------------------------- |
| Rota salto     | `warn-parent-level-jump/`                                                                          |
| JSON salto     | `warn_parent_level_jump_json_dict`                                                                 |
| Intermediários | `analyze_intermediate_items_for_level_jump`                                                        |
| Domínio        | `validate_item_parent_item_rules`, `validate_item_nivel_id_receita_cod_derivation`                 |
| Modais         | `showCoreLevelJumpModal`, `showCoreParentChangeConfirmModal`, `requestParentLevelJumpConfirmation` |
| Sentinela      | `transaction_time_sentinel_for_query`                                                              |

---

## Specs relacionadas

| Spec                                                                                           | Relação                  |
| ---------------------------------------------------------------------------------------------- | ------------------------ |
| [`spec_itemClassificacao_regras_hierarquia.md`](spec_itemClassificacao_regras_hierarquia.md)   | Domínio **ITEMRH**       |
| [`spec_itemClassificacao_foreignKeys_lookup.md`](spec_itemClassificacao_foreignKeys_lookup.md) | Lookups JSON             |
| [`spec_itemClassificacao_criar_filho.md`](spec_itemClassificacao_criar_filho.md)               | **(G5)**, sugestão filho |
| [`spec_validar_codigos.md`](spec_validar_codigos.md)                                           | Validação offline        |
