# Especificação: validação de item mãe, salto de nível no admin e listagem de intermediários

## Objetivo e escopo

Documentar o comportamento **técnico** implementado em torno de `parent_item_id` no **Django Admin** ao **adicionar** `ItemClassificacao`: aviso de **salto de nível** (mãe não está em `L_filho − 1`), contagem/listagem de **itens intermediários** na base, e a relação com a **validação de domínio** já descrita em `_dev/spec_parent_item_id.md`.

Esta especificação **não** substitui `spec_parent_item_id.md` nas regras de negócio gerais; complementa o que foi feito no **código** (`apps/core/parent_item_validation.py`, `apps/core/admin.py`, `apps/core/templates/admin/core/change_form.html`) para o fluxo de **confirmação antes do submit** e para a **análise de intermediários**.

Lookups JSON de **código / hierarquia** no mesmo admin (lupa de mãe por código exacto e derivação de nível + mãe matriz): `_dev/spec_lookup_hierarquia_por_codigo_admin.md` (`apps/core/item_classificacao_code_lookup.py`).

## Glossário (implementação)

| Termo | Significado no código |
|--------|-------------------------|
| `LP` | `nivel_numero` do **item mãe** (`parent.nivel_id.nivel_numero`). |
| `L` / `L_filho` | `nivel_numero` do **nível do item em criação** (registo `NivelHierarquico` cujo PK vem no campo `nivel_id` do formulário). |
| Salto de nível | `LP < L_filho − 1` (mãe **não** é o nível imediatamente abaixo do filho). |
| Radical (intermediários) | Primeiros `sum(mask[0:LP])` **dígitos** do `receita_cod` do mãe (apenas caracteres numéricos; o BD armazena sem pontuação de máscara). |
| Zero canónico | Segmento em que todos os caracteres são `'0'` (função `_canonical_zero_segment`). |
| Registo ativo | `data_registro_fim` igual ao sentinela de tempo de transação retornado por `transaction_time_sentinel_for_query()` (mesma convenção do admin bitemporal). |

## Três fluxos distintos (importante para manutenção)

### A) Gatilho do aviso (`level_jump`) — **só níveis**

**Onde:** `ItemClassificacaoAdmin.warn_parent_level_jump_view` (`apps/core/admin.py`) apenas orquestra GET/ORM; a decisão e o payload JSON ficam em `warn_parent_level_jump_json_dict` (`apps/core/parent_item_validation.py`).

**Condição para `level_jump: true`:** existem `parent_item_id`, `nivel_id`, `classificacao_id`, `vigencia_inicio`, `vigencia_fim` válidos no GET; o `ItemClassificacao` mãe e o `NivelHierarquico` do filho existem; `child_n > 1`; `parent_n < child_n`; e **`parent_n != child_n − 1`**.

**O que não entra neste gatilho:** o `receita_cod` do filho **não** altera `true`/`false` de `level_jump`. Ou seja: o modal pode aparecer mesmo que a lista de intermediários venha vazia.

### B) Validação ao gravar — **código do filho e regras de domínio**

**Onde:** `validate_item_parent_item_rules` em `apps/core/parent_item_validation.py` (ver também `_dev/spec_parent_item_id.md`).

Quando `parent_n < nivel_n − 1`, os segmentos do **filho** nos índices `LP .. L−2` devem ser **zeros canónicos**; caso contrário, `ValidationError` (mensagem sobre detalhamento nos níveis entre mãe e filho).

Este fluxo responde à pergunta “o **código digitado** do novo item é coerente com o salto?”. É **independente** da query de intermediários na base.

### C) Listagem de intermediários — **outros registos em `ItemClassificacao`**

**Onde:** `analyze_intermediate_items_for_level_jump` (`apps/core/parent_item_validation.py`), chamada a partir de `warn_parent_level_jump_json_dict` (mesmo módulo).

Objetivo: montar `intermediate_count`, `intermediate_rows` e rótulos de nível para o texto “Além disso, existe …” no modal.

---

## Endpoint HTTP

- **Rota:** `GET …/admin/core/itemclassificacao/warn-parent-level-jump/`  
  (nome URL: `admin:core_itemclassificacao_warn_parent_level_jump`).
- **Registro da URL no template:** `item_parent_level_jump_warn_url` em `render_change_form` do `ItemClassificacaoAdmin`.

### Parâmetros GET (origem: `change_form.html`, `requestParentLevelJumpConfirmation`)

| Parâmetro | Origem no formulário | Uso |
|-----------|----------------------|-----|
| `parent_item_id` | Valor do campo mãe (PK) | Carrega `ItemClassificacao` pai. |
| `nivel_id` | PK do nível do **item novo** | `child_n` = `nivel_numero` desse nível. |
| `classificacao_id` | PK da classificação selecionada | **Filtro da query** de intermediários (`classificacao_id_id`). |
| `vigencia_inicio`, `vigencia_fim` | Datas do formulário (ISO `YYYY-MM-DD`) | **Sobreposição de vigência** na análise de intermediários e formatação de códigos mascarados no JSON. |
| `receita_cod` | Dígitos do código do filho (sem pontos) | Máscara no JSON; `exclude_receita_cod` na análise (não listar o próprio rascunho se coincidir com um PK existente). |

Se faltar qualquer um dos obrigatórios da primeira linha (pai, nível, classificação, vigência), a view devolve `{"ok": true, "level_jump": false}` e o front segue o submit sem modal.

---

## Algoritmo: `analyze_intermediate_items_for_level_jump`

**Assinatura relevante:** `classificacao_pk`, `parent_item`, `child_nivel_numero`, `vig_ini`, `vig_fim`, `reg_sent`, `sample_limit`, `exclude_receita_cod` opcional.

### 1. Saída antecipada (estrutura vazia)

- `parent_n` ou `child_nivel_numero` nulos.
- `parent_n >= child_nivel_numero − 1` (não há “faixa” estrita entre mãe e filho para esta função).

### 2. Máscara de dígitos

1. `mask = digit_mask_for_classificacao_vigencia(classificacao_pk, vig_ini, vig_fim)`.
2. Se `mask` vazio: **fallback** com `data_vigencia_inicio` / `data_vigencia_fim` do **item mãe** (só para resolver `estrutura_codigo` quando a janela do formulário não produz máscara; **não** altera o filtro de vigência da query abaixo).

Se ainda não houver máscara ou `parent_n > len(mask)`, retorna contagem zero.

### 3. Radical

- `p_digits` = apenas dígitos de `parent_item.receita_cod`.
- `radical_len = sum(mask[0:parent_n])`.
- `radical = p_digits[:radical_len]`; se o mãe tiver menos dígitos que `radical_len`, retorna vazio.

**Decisão de produto:** o radical vem **sempre do código do pai**, para ancorar a árvore sob o mesmo prefixo até `LP`, incluindo ramos irmãos no nível seguinte (ex.: mesmo prefixo `111252` com dígito `9` vs `0` no segmento de nível intermediário), desde que o registo exista na **classificação** usada na query.

### 4. Intervalo de níveis (limites **inclusivos**)

- `nivel_min = parent_n + 1`
- `nivel_max = child_nivel_numero − 1`

### 5. Query ORM (`ItemClassificacao`)

Filtros **simultâneos**:

- `classificacao_id_id = classificacao_pk`
- `data_registro_fim = reg_sent`
- `receita_cod__startswith = radical`
- Sobreposição de vigência: `data_vigencia_inicio <= vig_fim` e `data_vigencia_fim >= vig_ini` com **`vig_ini` / `vig_fim` passados pelo chamador** (no admin: **apenas as datas do formulário**).
- `nivel_id__nivel_numero` entre `nivel_min` e `nivel_max` (**inclusive**).

### 6. Pós-processamento em Python (por linha)

1. Se `exclude_receita_cod` (só dígitos) for igual ao código da linha, pular.
2. `split_receita_cod_segments_tolerant(receita_cod, mask)`.
3. `nn` = `nivel_numero` da linha; confirmar `nivel_min <= nn <= nivel_max`.
4. Segmento do nível `nn`: índice `nn − 1`. Se `None` ou zero canónico, **excluir** da contagem.

Amostras: até `sample_limit` (no admin: **3**) para o JSON.

### Retorno da função

- `count`, `nivel_numeros`, `nivel_semantic_by_numero`, `samples` (cada amostra: `pk`, `receita_cod`, `display_label`, `admin_url`, `nivel_numero`).

---

## Decisões registradas (contexto técnico)

### 1. Vigência na análise de intermediários = **somente formulário**

**Problema anterior:** união do intervalo do formulário com o do mãe alargava a janela e podia incluir vigências irrelevantes para o **item filho que se pretende criar**.

**Decisão:** `analyze_intermediate_items_for_level_jump` recebe `vig_ini` / `vig_fim` **iguais** às datas do GET do formulário, sem `min`/`max` com o pai.

**Exceção mantida:** o **fallback da máscara** com vigência do mãe (secção 2 acima) continua só para obter `mask` quando a vigência do form não resolve `estrutura_codigo`; **não** expande o intervalo usado nos filtros `data_vigencia_*` da query.

### 2. `classificacao_pk` na busca = **PK do formulário**

**Problema observado:** em base de teste, o mãe (ex.: PK de classificação `5`) e um item intermediário desejado para o exemplo (ex.: `item_ref` 3966 com `classificacao_id` `6`) não coincidem; filtrar pela classificação do mãe zerava a lista mesmo com radical, nível e vigência corretos para o exemplo.

**Decisão:** `ItemClassificacaoAdmin` define `busca_intermediarios_class_pk = class_id_int` (GET) e passa esse valor para `analyze_intermediate_items_for_level_jump`.

**Risco consciente:** se o utilizador escolher no form uma classificação **diferente** da do pai, a lista reflete o form (pode ser vazia ou incoerente com o vínculo real). Em produção, mãe e filho devem pertencer à **mesma** classificação (`spec_parent_item_id.md`); o caso acima foi guiado por **seed / teste** com PKs distintos.

### 3. Modal ≠ mesma regra que a listagem

O utilizador pode ver `level_jump: true` e `intermediate_count: 0`: o primeiro depende só de **níveis**; o segundo da **query** acima. A especificação deixa isso explícito para evitar confusão em suporte e QA.

### 4. Texto e UX do modal (`change_form.html`)

- Título: **“Atenção!”**
- Primeiro parágrafo: `O item mãe, (` + link com código mascarado do mãe + ` - ` + rótulo semântico do nível do mãe + `)` + texto fixo até o código/nível do **filho** entre parêntesis (filho **sem** link no trecho principal).
- Se `intermediate_count > 0` ou houver linhas: segundo parágrafo **“Além disso, existe … código(s) discriminado(s) no(s) …”** com `no` vs `nos` conforme o rótulo de níveis contém a substring ` e `; contagem com zero à esquerda para `< 100` (`intermediate_count_display`).
- Lista: até 3 itens; cada linha com código mascarado + tab + nome, link para o change do admin (`white-space: pre-wrap`).
- Pergunta final: **“Deseja continuar e gravar o registo?”** (sem “mesmo assim”).
- Botões Cancelar / OK; overlay clicável cancela.

### 5. Debug temporário (removido na entrega deste spec)

Foi implementado um bloco condicionado a `?debug=1` que acrescentava `intermediate_debug` ao JSON para sondar um PK fixo (ex. 3966). **Foi removido** do `admin.py` após o diagnóstico (classificação do form vs. do pai). Este item documenta o **histórico** para quem ler commits antigos.

---

## Integração no submit (front)

**Arquivo:** `apps/core/templates/admin/core/change_form.html`.

Fluxo: no `submit` do form em modo **add**, após validações de dígitos e hierarquia (`runCodeDigitValidation`, `syncHierarchyFromCode`), chama-se `requestParentLevelJumpConfirmation()`.

- Se a resposta não tiver `level_jump`, devolve `true` e o fluxo segue para o submit nativo.
- Se tiver `level_jump`, abre `showCoreLevelJumpModal` com o JSON; **OK** libera o submit (`allowNativeSubmit`), **Cancelar** aborta.

Variável de contexto: `item_parent_level_jump_warn_url` (definida no admin ao renderizar o change form).

---

## Referências de código (mapa rápido)

| Peça | Arquivo / símbolo |
|------|---------------------|
| Rota customizada | `ItemClassificacaoAdmin.get_urls` → `warn-parent-level-jump/` |
| View JSON | `warn_parent_level_jump_view` (`admin.py`) → `warn_parent_level_jump_json_dict` (`parent_item_validation.py`) |
| Análise intermediários | `analyze_intermediate_items_for_level_jump` |
| Validação domínio pai/filho | `validate_item_parent_item_rules` |
| Modal | `showCoreLevelJumpModal`, `requestParentLevelJumpConfirmation` em `change_form.html` |
| Sentinela registo | `transaction_time_sentinel_for_query` em `apps/core/admin_mixins.py` |

## Relação com outras especificações

- **`_dev/spec_parent_item_id.md`:** regras normativas de `parent_item_id`, prefixo, cauda do pai, salto e zeros no filho, mesma classificação, vigência do mãe contendo a do filho, etc.
- **`_dev/spec_validar_codigos.md`:** validação offline de códigos; não substitui o fluxo admin acima.

## Exemplo que guiou decisões (seed)

Linha de referência em `docs/assets/seed_item_classificacao.csv` (ex.: item com `receita_cod` `1112529000000`, nível 6, classificação MG): usado para validar que a listagem precisava do **mesmo** `classificacao_id` que o formulário quando o mãe do teste apontava para outro PK de classificação.
