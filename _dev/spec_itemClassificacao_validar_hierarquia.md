# Especificação: validação de item mãe, salto de nível no admin e listagem de intermediários

## Objetivo e escopo

Documentar o comportamento **técnico** implementado em torno de `parent_item_id` no **Django Admin** ao **adicionar** `ItemClassificacao`: aviso de **salto de nível** (mãe não está em `L_filho − 1`), contagem/listagem de **itens intermediários** na base, e a relação com a **validação de domínio** já descrita em `_dev/spec_itemClassificacao_regras_hierarquia.md`.

Esta especificação **não** substitui `spec_itemClassificacao_regras_hierarquia.md` nas regras de negócio gerais; complementa o que foi feito no **código** (`apps/core/parent_item_validation.py`, `apps/core/admin.py`, `apps/core/templates/admin/core/change_form.html`) para o fluxo de **confirmação antes do submit** e para a **análise de intermediários**.

Lookups JSON de **código / hierarquia** no mesmo admin (lupa de mãe por código exacto e derivação de nível + mãe matriz): `_dev/spec_itemClassificacao_foreignKeys_lookup.md` (`apps/core/item_classificacao_code_lookup.py`).

## Glossário (implementação)

| Termo | Significado no código |
|--------|-------------------------|
| `LP` | `nivel_numero` do **item mãe** (`parent.nivel_id.nivel_numero`). |
| `L` / `L_filho` | `nivel_numero` do **nível do item em criação** (registo `NivelHierarquico` cujo PK vem no campo `nivel_id` do formulário). |
| Salto de nível | `LP < L_filho − 1` (mãe **não** é o nível imediatamente abaixo do filho). |
| Radical (intermediários) | Primeiros `sum(mask[0:LP])` **dígitos** do `receita_cod` do mãe (apenas caracteres numéricos; o BD armazena sem pontuação de máscara). |
| Zero canônico | Segmento em que todos os caracteres são `'0'` (função `_canonical_zero_segment`). |
| Registo ativo | `data_registro_fim` igual ao sentinela de tempo de transação retornado por `transaction_time_sentinel_for_query()` (mesma convenção do admin bitemporal). |

## Três fluxos distintos (importante para manutenção)

### A) Gatilho do aviso (`level_jump`) — **só níveis**

**Onde:** `ItemClassificacaoAdmin.warn_parent_level_jump_view` (`apps/core/admin.py`) apenas orquestra GET/ORM; a decisão e o payload JSON ficam em `warn_parent_level_jump_json_dict` (`apps/core/parent_item_validation.py`).

**Condição para `level_jump: true`:** existem `parent_item_id`, `nivel_id`, `classificacao_id`, `vigencia_inicio`, `vigencia_fim` válidos no GET; o `ItemClassificacao` mãe e o `NivelHierarquico` do filho existem; `child_n > 1`; `parent_n < child_n`; e **`parent_n != child_n − 1`**.

**O que não entra neste gatilho:** o `receita_cod` do filho **não** altera `true`/`false` de `level_jump`. Ou seja: o modal pode aparecer mesmo que a lista de intermediários venha vazia.

### B) Validação de zeros canônicos nos níveis intermédios — **bloqueio no código**

**Onde:** `find_intermediate_non_canonical_zero_message` / `validate_intermediate_canonical_zeros_json_dict` e `validate_item_parent_item_rules` em `apps/core/parent_item_validation.py`; endpoint `validate-intermediate-canonical-zeros/` no admin.

Quando `parent_n < nivel_n − 1`, os segmentos do **filho** nos índices `LP .. L−2` devem ser **zeros canônicos**; caso contrário, erro **apenas** em `receita_cod`:

> Os campos correspondentes aos níveis entre o código atual (nível **F**) e o código mãe selecionado (nível **M**), devem conter apenas zeros canônicos.

(**F** = `nivel_numero` do filho; **M** = `nivel_numero` da mãe.)

No **Salvar** (add), o cliente chama este endpoint **antes** do modal de salto (fluxo A). Se `ok: false`, exibe erro vermelho sob o código e **não** abre o pop-up. É **independente** da query de intermediários na base (fluxo C).

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
4. Segmento do nível `nn`: índice `nn − 1`. Se `None` ou zero canônico, **excluir** da contagem.

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

**Risco consciente:** se o utilizador escolher no form uma classificação **diferente** da do pai, a lista reflete o form (pode ser vazia ou incoerente com o vínculo real). Em produção, mãe e filho devem pertencer à **mesma** classificação (`spec_itemClassificacao_regras_hierarquia.md`); o caso acima foi guiado por **seed / teste** com PKs distintos.

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

Fluxo no `submit` (modo **add**):

1. `runCodeDigitValidation`
2. `syncHierarchyFromCode` — lookup de nível/mãe canónica
3. `validateIntermediateCanonicalZerosOnSubmit` — fluxo B (bloqueio; sem modal se falhar)
4. naming
5. `requestParentLevelJumpConfirmation` — fluxo A (modal só se B passou)
6. submit nativo → `clean()` / `validate_item_parent_item_rules` (mesma regra B no servidor)

**Item mãe no lookup por código:** em `syncHierarchyFromCode`, alteração do `receita_cod` (blur/change de classificação/init) **atualiza** `parent_item_id` quando o lookup devolve `parent.found`. Preservar mãe sem substituir aplica-se só no **Salvar** (`submit`): falha do lookup ou PK diferente não limpa nem bloqueia, para permitir mãe escolhida na lupa e validação de salto/zeros. Após erro do Django (`.errornote`), `syncHierarchyFromCode('init')` **não** corre.

Variáveis de contexto: `item_validate_intermediate_zeros_url`, `item_parent_level_jump_warn_url`.

---

## Referências de código (mapa rápido)

| Peça | Arquivo / símbolo |
|------|---------------------|
| Rota customizada | `ItemClassificacaoAdmin.get_urls` → `warn-parent-level-jump/` |
| View JSON | `warn_parent_level_jump_view` (`admin.py`) → `warn_parent_level_jump_json_dict` (`parent_item_validation.py`) |
| Análise intermediários | `analyze_intermediate_items_for_level_jump` |
| Validação domínio pai/filho | `validate_item_parent_item_rules` |
| Modal | `showCoreAttentionModal` (base), `showCoreLevelJumpModal` (salto ao gravar), `requestParentLevelJumpConfirmation` em `change_form.html`; troca de mãe com código preenchido usa o mesmo modal — ver **(G5)** em `spec_itemClassificacao_criar_filho.md` |
| Sentinela registo | `transaction_time_sentinel_for_query` em `apps/core/admin_mixins.py` |

## Renderização preventiva de `parent_item_id` para itens raiz (`nivel_numero = 1`)

### Regra subjacente

A regra normativa está em `_dev/spec_itemClassificacao_regras_hierarquia.md`:
itens com `nivel_numero = 1` devem ter `parent_item_id = NULL`. Esta seção
descreve **como** essa regra é refletida na renderização do form do Django
Admin de `ItemClassificacao`, com paridade entre as visões de **alteração**
(change) e **adição** (add).

### Estado visual canônico do campo `parent_item_id` em itens raiz

Quando o item em edição/criação for de `nivel_numero = 1`, o campo
`parent_item_id` deve apresentar-se em modo **somente leitura "raiz"**, com:

- valor real (hidden) **vazio**;
- display congelado com o texto "Sem item mãe" e fundo hachurado/cinza;
- lupa de busca **oculta** (sem caminho clicável para seleção de mãe);
- rótulo dinâmico do item mãe **oculto** (não há mãe a exibir);
- mensagem auxiliar visível: "Item raiz, de nível 1, não possui item mãe.".

Esse é o estado que já aparece hoje na **change view** quando a instância
persistida tem `instance.nivel_id.nivel_numero == 1` (ver
`ItemClassificacaoForm.__init__` em `apps/core/forms.py`, atributos
`data_readonly_root`, `data_empty_display`, `data_root_message` do widget
`ForeignKeySemanticDisplayRawIdWidget`).

### Comportamento na change view (server-side, inalterado)

O estado é decidido no servidor durante a renderização do form, a partir de
`self.instance.nivel_id.nivel_numero`. O template
`apps/core/templates/admin/widgets/foreign_key_semantic_raw_id.html` consome
os `widget.attrs.data_readonly_root`, `data_empty_display` e
`data_root_message` e desliga inclusive o `<script>` de resolução semântica
do hidden. Esse fluxo permanece como está.

### Comportamento na add view (objetivo desta seção)

Na add view o `self.instance` é vazio (sem `nivel_id`), então o estado
"raiz somente leitura" precisa ser aplicado **dinamicamente no client**,
reagindo ao preenchimento do campo `Nível Hierárquico`. As fontes possíveis
desse preenchimento são:

- **manual**: usuário escolhe um `NivelHierarquico` pela lupa (`raw_id`);
- **automática**: `syncHierarchyFromCode` (em `change_form.html`) deriva o
  nível a partir do `receita_cod` + classificação + vigência e atribui
  `nivelIdInput.value`;
- **postback após erro de validação**: o POST volta com `nivel_id`
  preenchido, e o navegador renderiza o widget com esse valor inicial.

Em todos os três casos, ao saber o **PK do nível selecionado**, o cliente
deve resolver o `nivel_numero` correspondente e:

- se `nivel_numero === 1`: aplicar o estado "raiz somente leitura" no
  widget de `parent_item_id` em paridade com a change view (texto,
  hachurado, lupa oculta, label oculto, mensagem auxiliar visível,
  `hidden.value = ""`, `hidden.dataset.readonlyRoot = "1"`);
- caso contrário: **restaurar** o estado editável (display vazio, fundo
  normal, lupa visível, sem mensagem auxiliar, `dataset.readonlyRoot`
  removido). A reversibilidade é normativa: trocar o nível para outro com
  `nivel_numero > 1` deve devolver o campo ao modo normal.

### Resolução de `nivel_numero` no client

Para resolver `nivel_numero` a partir do PK selecionado no `nivel_id`, o
projeto **estende o endpoint `semantic-lookup/<kind>/<pk>/`** (definido em
`apps/core/admin_mixins.py`, mixin `BitemporalForeignKeyLookupActiveOnlyMixin`)
com um campo opcional `metadata` no payload JSON, configurável por FK via
`semantic_fk_config[campo]["metadata_resolver"]`. Para `nivel_id` em
`ItemClassificacaoAdmin`, o resolver devolve `{"nivel_numero": obj.nivel_numero}`.

Contrato do payload (compatível com clientes existentes):

```json
{
  "semantic_value": "NIVEL-1",
  "display_label": "NIVEL-1 - Categoria Econômica",
  "link_url": "/admin/core/nivelhierarquico/<pk>/change/",
  "metadata": {"nivel_numero": 1}
}
```

Quando o resolver não está declarado para a FK, o campo `metadata` é
omitido — preservando o payload anterior e a compatibilidade.

### Gatilho da sincronização no client

O JS em `change_form.html` adiciona uma função
`syncParentRootStateFromNivel(triggerName)` que:

1. lê `nivelIdInput.value`;
2. se vazio, garante o estado **editável** no `parent_item_id`;
3. se preenchido, faz fetch para o `semantic-lookup` do `nivel_id` e
   inspeciona `metadata.nivel_numero` no payload;
4. aplica `setParentRootReadonly(true|false)` no widget de `parent_item_id`
   conforme o resultado.

A função é chamada:

- no `init` (após `runCodeDigitValidation('init')`), cobrindo postback com
  erro e estados pré-preenchidos;
- no evento `change` do hidden de `nivel_id`;
- no evento `semantic-fk-changed` do hidden de `nivel_id` (disparado pelo
  próprio widget após resolver o display semântico).

### Interação com `syncHierarchyFromCode`

`syncHierarchyFromCode` já tem `early-return` quando
`parentItemIdInput.dataset.readonlyRoot === '1'`. Essa guarda continua sendo
o ponto único de verdade para "não bater no mãe quando o item é raiz".
A nova função apenas **alimenta** esse atributo (set/unset), sem mudar a
guarda existente.

### Regras normativas desta seção

- **R-root.1.** O estado "raiz somente leitura" deve ser sempre
  consequência do `nivel_numero` do nível selecionado (server-side na
  change view, client-side na add view). Nunca decidido por outro campo.
- **R-root.2.** A transição é **reversível**: trocar para um nível com
  `nivel_numero > 1` deve restaurar o campo editável e remover a mensagem
  auxiliar.
- **R-root.3.** O hidden de `parent_item_id` deve ser **limpo** sempre
  que o estado raiz for ativado (`hidden.value = ""`), garantindo que o
  POST não carregue um PK residual incompatível com a regra normativa
  (`parent_item_id = NULL` para nível 1).
- **R-root.4.** O endpoint `semantic-lookup` é o único contrato usado para
  resolver `nivel_numero` no client a partir de um **PK** isolado. A
  derivação a partir do **código** continua a cargo de
  `lookup-hierarchy-by-code`, cujo payload já expõe `derived_level.number`
  e deve ser usado como fonte síncrona quando o gatilho da mudança vem
  do `receita_cod` (ver R-root.5).
- **R-root.5.** O estado raiz **não** pode ser usado como guarda de
  early-return em `syncHierarchyFromCode`. A função deve sempre poder
  recalcular `nivel_id` a partir do novo `receita_cod`; o estado raiz é
  decisão derivada, não condição de entrada. Especificamente:
    - `syncHierarchyFromCode` aplica `setParentRootReadonlyState(true)`
      quando `data.derived_level.number === 1`, e
      `setParentRootReadonlyState(false)` para `number > 1`, **sem
      consultar** `data.parent` para essa decisão (o `parent.required`
      do payload continua sendo a fonte normativa do que fazer com o
      conteúdo do `parent_item_id`, mas não da renderização raiz);
    - `syncParentRootStateFromNivel` continua existindo para cobrir as
      mudanças de `nivel_id` que **não** passam pela derivação por
      código (ex.: seleção manual pela lupa, postback após erro com
      `nivel_id` pré-preenchido).

### Casos de teste recomendados

- **T-root.1.** Add view, usuário escolhe NIVEL-1 pela lupa → estado raiz
  é aplicado (display "Sem item mãe", lupa oculta, mensagem visível).
- **T-root.2.** Add view, `syncHierarchyFromCode` deriva NIVEL-1 → estado
  raiz é aplicado automaticamente após a sincronização.
- **T-root.3.** Add view, usuário troca de NIVEL-1 para NIVEL-2 → estado
  raiz é desfeito; lupa volta a aparecer; campo aceita seleção de mãe.
- **T-root.4.** Add view, postback com erro de validação e `nivel_id` já
  apontando para NIVEL-1 → `syncParentRootStateFromNivel('init')` aplica o
  estado raiz no primeiro render JS, sem "piscar".
- **T-root.5.** Change view, instância com `nivel_id.nivel_numero = 1` →
  estado raiz já aplicado pelo servidor (sem dependência do JS).
- **T-root.6.** `semantic-lookup/<kind=nivel>/<pk>/` retorna `metadata`
  contendo `nivel_numero`; demais kinds (`item`, `classificacao`, etc.) não
  retornam `metadata` (compatibilidade com clientes anteriores).
- **T-root.7.** Add view, usuário preenche `receita_cod` para um código de
  nível 1 (ex.: `1000000000000`), TAB → estado raiz ativado. Em seguida,
  altera o código para um de nível 2 (ex.: `1100000000000`), TAB →
  `syncHierarchyFromCode` recalcula, `nivel_id` muda para NIVEL-2 e o
  estado raiz é desativado, voltando a permitir a seleção de mãe e
  permitindo que a derivação automática do `parent_item_id` ocorra.
  Verifica explicitamente que **R-root.5** está em vigor.

## Relação com outras especificações

- **`_dev/spec_itemClassificacao_regras_hierarquia.md`:** regras normativas de `parent_item_id`, prefixo, cauda do pai, salto e zeros no filho, mesma classificação, vigência do mãe contendo a do filho, etc.
- **`_dev/spec_validar_codigos.md`:** validação offline de códigos; não substitui o fluxo admin acima.

## Exemplo que guiou decisões (seed)

Linha de referência em `docs/assets/seed_item_classificacao.csv` (ex.: item com `receita_cod` `1112529000000`, nível 6, classificação MG): usado para validar que a listagem precisava do **mesmo** `classificacao_id` que o formulário quando o mãe do teste apontava para outro PK de classificação.
