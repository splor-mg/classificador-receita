# Item de classificação — criação no admin: sugestão de código filho (`receita_cod`)

Esta especificação define **como o fluxo deve funcionar** no formulário Django de **criação** (`add`) de `ItemClassificacao` no admin, quando o usuário escolhe um **item mãe** com o campo **Código Canônico da Natureza de Receita** (`receita_cod`) ainda vazio: o sistema **sugere automaticamente** o primeiro código em que pode existir **detalhamento hierárquico** coerente com a mãe, a máscara da classificação e os filhos já registrados.

**Referência no repositório (alvo de implementação futura):** novo endpoint JSON no `ItemClassificacaoAdmin` (família de `lookup-hierarchy-by-code` / `lookup-parent-by-code` em `apps/core/item_classificacao_code_lookup.py`), consumo em `change_form.html` / JS dedicado; reutilização de `digit_mask_for_classificacao_vigencia`, `split_receita_cod_segments_tolerant` e `_canonical_zero_segment` em `apps/core/parent_item_validation.py`.

**Specs relacionadas (não substituídas):**

| Spec | Relação |
|------|---------|
| `_dev/spec_itemClassificacao_regras_hierarquia.md` | Filho direto = nível **NM+1**; zeros canônicos na cauda; vigência do filho contida na da mãe ao gravar. |
| `_dev/spec_itemClassificacao_foreignKeys_lookup.md` | Lookup inverso (código → mãe/nível); executa **depois** de `receita_cod` preenchido. |
| `_dev/spec_itemClassificacao_criar_nome.md` | **P-mãe** (nomenclatura) após mãe/código definidos. |
| `_dev/spec_itemClassificacao_validar_hierarquia.md` | Aviso de salto de nível no **submit** quando `L > NM+1`; intermediários. |
| `_dev/toDo.md` | Alerta «código já existente» e «próximo dígito» — spec futura; ver **§ Decisões em aberto**. |

---

## Objetivo

Dado um **item mãe** selecionado na tela de adição, com `receita_cod` do formulário **vazio**, determinar e preencher o **primeiro** `receita_cod` coerente com a hierarquia e com o que já existe na base, tal que:

1. respeita a **máscara** resolvida a partir da `classificacao_id` da mãe (vigência **(V1)**);
2. mantém o **prefixo** da mãe até **NM** (radical **(T4)**);
3. discrimina o segmento no **nível alvo `L`**, com `NM < L ≤ len(mask)` e cauda `L+1 … fim` em **zero canônico**;
4. dado o radical, considera **todos** os itens ativos/vigentes com esse prefixo (**(V2b)**), **sem** restringir à mesma classificação da mãe, para detectar em que nível já houve detalhe;
5. na varredura **(V2b)**, nível a nível a partir de **NM+1**, para no **primeiro** nível `K*` em que já exista segmento ≠ zero canônico e sugere `maior + 1` (ou buraco **(H)**) **nesse** nível;
6. se **não** houver detalhe em nenhum nível `NM+1 … fim` na varredura **(V2b)**, aplica **(A)/(H)/(F)** só entre **filhos diretos** da mãe (**(V2a)**) no nível **`L = NM+1`**;
7. falha de forma explícita **(E1)** quando o nível alvo estiver esgotado em sentido vigente.

---

## Escopo e fora de escopo

### Escopo (v1)

- Tela **add** de `ItemClassificacao` no admin.
- Gatilho: seleção de `parent_item_id` (lupa ou equivalente) com `receita_cod` **vazio** (*trim* / só pontuação = vazio).
- Sugestão de `receita_cod` (dígitos canônicos, sem pontos no POST interno; formatação visual conforme máscara no cliente).
- Pré-preenchimento **recomendado** no mesmo passo: `nivel_id` (= **`L`** resolvido), `classificacao_id` (= classificação do `nivel_id` resolvido, não diretamente da mãe), e datas de vigência do formulário **se ainda vazias** (ver **(V3)**).
- Aviso informativo (não bloqueante na sugestão) quando **`L > NM+1`** — salto de nível em relação à mãe; confirmação no submit conforme `spec_itemClassificacao_validar_hierarquia.md`.
- Mensagens de erro **(E1)** e aviso não bloqueante se o código sugerido já existir (ver **§ Decisões em aberto — DD3**).

### Fora de escopo (v1)

- Alteração (`change`) de registro existente.
- Geração de `item_id`, `receita_nome`, `matriz`, bases legais.
- Persistência (`save`); apenas pré-preenchimento e validação de UI.
- Protocolo completo «código já existente → link e próximo dígito» (item separado no `_dev/toDo.md`).

---

## Alinhamento terminológico

- **(T1) `NM`:** `nivel_numero` do item mãe selecionado (`parent_item_id`).
- **(T2) `L`:** nível alvo do filho sugerido (`nivel_numero` do item a criar). **`L = K*`** quando a varredura **(V2b)** encontra detalhe; senão **`L = NM + 1`** via **(V2a)**.
- **(T2a) `K*`:** **menor** índice de nível `K ∈ {NM+1, …, len(mask)}` (varredura ascendente) para o qual existe pelo menos um registro em **(V2b)** com segmento `K` ≠ zero canônico e vigência **(T7)** com **(V1)**.
- **(T3) `máscara`:** lista de larguras por segmento derivada de `estrutura_codigo` da classificação da mãe (`digit_mask_for_classificacao_vigencia`), vigência efetiva **(V1)**.
- **(T4) `radical`:** primeiros `sum(mask[0:NM])` **dígitos** de `receita_cod` da mãe (apenas `0-9`, sem pontuação).
- **(T5) `zero canônico`:** segmento em que todos os caracteres são `'0'` (`_canonical_zero_segment`).
- **(T6) `registro ativo`:** `data_registro_fim` = sentinela de transaction time do projeto (`TRANSACTION_TIME_SENTINEL` / `transaction_time_sentinel_for_query()`).
- **(T7) `vigência compatível (consulta)`:** sobreposição entre o intervalo do candidato e o intervalo de referência **(V1)**: `início_ref ≤ fim_candidato` e `fim_ref ≥ início_candidato` (datas inclusivas).
- **(T8) `vigência compatível (gravação)`:** intervalo do **novo** filho deve estar **contido** no da mãe (`spec_itemClassificacao_regras_hierarquia.md`) — validação no `clean()` / domínio, não só na sugestão.
- **(T9) `valor de segmento`:** texto do segmento na posição do nível; comparado **numericamente** (`int(segmento)`), com saída **zero-padded** à largura `mask[L-1]`.
- **(T10) `capacidade do nível L`:** `10^w - 1` onde `w = mask[L-1]` (ex.: `w=1` → valores `1..9`; `w=2` → `1..99`). O valor **0** / zero canônico **não** é candidato a detalhamento.
- **(T11) `classificação do filho`:** `classificacao_id` do formulário de criação deve ser derivado do `NivelHierarquico` resolvido para **`L`** (`nivel_id.classificacao_id`). Se esse nível não for resolvido, a sugestão falha explicitamente (**E3**).
- **(T12) `resolução do nível alvo`:** o `NivelHierarquico` correspondente ao nível **`L`** sugerido deve ser buscado **apenas** por `nivel_numero = L`, `data_registro_fim` = sentinela e vigência compatível **(T7)** com **(V1)**. **Não** restringir pela `classificacao_id` da mãe. Em caso de múltiplos candidatos, ordenar por `-data_vigencia_inicio, -data_registro_inicio, -pk`, escolher o primeiro e emitir aviso não bloqueante de ambiguidade.

---

## Vigência e classificação na consulta

### (V1) Intervalo de referência para a sugestão

Ordem de prioridade:

1. Se o formulário tiver `data_vigencia_inicio` **e** `data_vigencia_fim` preenchidos → usar esse par.
2. Senão → usar `data_vigencia_inicio` e `data_vigencia_fim` do **item mãe** selecionado.

A máscara é resolvida com `classificacao_id` da mãe e **(V1)**. Se a máscara não for obtida com **(V1)**, repetir o fallback já usado no repositório: vigência **só** da mãe (`digit_mask_for_classificacao_vigencia(classificacao_pk, mãe.início, mãe.fim)`).

### (V2a) Filhos diretos da mãe — `FILHOS`

Conjunto usado para **(A)/(H)/(F)** no nível **`NM+1`** quando a varredura **(V2b)** não encontra detalhe em nenhum nível:

- `parent_item_id` = PK do item mãe selecionado no formulário (filhos **diretos**);
- `data_registro_fim` = sentinela (**(T6)**);
- **(T7)** com **(V1)**;
- **sem** filtro por `classificacao_id` / identidade semântica de classificação (um filho direto pode estar em outra edição ou classificação estatística, p.ex. `CLASS-RECEITA-MG-2018` com mãe `CLASS-RECEITA-UNIAO-2018`).

Para cada registro em **FILHOS**, o segmento considerado no passo **filhos** é sempre o da posição **`NM+1`** na máscara (índice `NM`), **independentemente** do `nivel_numero` gravado no filho (ex.: filho com `nivel_numero = 9` mas segmento `0` no nível 6 ainda conta `0` nessa posição; o valor no nível 9 não entra neste passo).

### (V2b) Varredura por radical — `RAMO`

Conjunto usado na regra **(B)** (nível a nível, profundidade máxima):

- `receita_cod` (só dígitos) com prefixo igual ao **radical** **(T4)** da mãe (`startswith`);
- `data_registro_fim` = sentinela (**(T6)**);
- **(T7)** com **(V1)**;
- **sem** filtro por `classificacao_id`;
- **sem** exigir `parent_item_id` = mãe (inclui ramos em outras classificações que compartilham o mesmo prefixo numérico até **NM**).

*Nota:* a máscara **(T3)** continua sendo resolvida pela classificação/vigência da **mãe**; códigos de outras classificações que compartilhem estrutura de níveis compatível são segmentados com essa máscara. Se no futuro houver máscaras incompatíveis entre classificações com o mesmo radical, documentar exceção — fora do v1.

### (V3) Pré-preenchimento de vigência no formulário

Se, no momento da sugestão, `data_vigencia_inicio` e/ou `data_vigencia_fim` do formulário estiverem vazios, o cliente **pode** copiar as datas da mãe para esses campos (comportamento adotado nesta spec por aderência ao `_dev/toDo.md`). Isso não dispensa **(T8)** no servidor.

---

## Gatilhos e guardrails de UI

### (G1) Quando sugerir

- **Disparar automaticamente** após seleção válida de `parent_item_id` se `receita_cod` estiver vazio (**G2**).
- **Disparar novamente automaticamente** se o usuário trocar a mãe e `receita_cod` continuar vazio.
- **Não disparar automaticamente** se `receita_cod` tiver qualquer dígito significativo (**G2** negado) — ver **(G5)** para troca de mãe nesse caso.

### (G2) `receita_cod` vazio

Campo considerado vazio: ausência de dígitos após remover pontuação de máscara e espaços. Vale para código informado manualmente ou por sugestão anterior (não se distingue a origem).

### (G5) Troca de mãe com código já preenchido

Quando o usuário altera `parent_item_id` e `receita_cod` **não** está vazio (**G2**):

1. **Não** substituir o código automaticamente.
2. Exibir **modal de atenção** centrado (mesmo componente visual do aviso de salto de nível ao gravar: `showCoreAttentionModal` em `change_form.html` — ícone ⚠️, título «Atenção!», botões Cancelar/OK), com texto orientativo, por exemplo: *«O código canônico da natureza de receita já está preenchido. Deseja atualizar o código com base no novo item mãe selecionado?»*
3. Se o usuário **confirmar** → executar o mesmo fluxo de sugestão (**endpoint** + pré-preenchimentos de **Passo 6**), **substituindo** o valor atual de `receita_cod` (e campos derivados: `nivel_id`, avisos, nomenclatura **P-mãe**, etc.).
4. Se **cancelar** → manter `receita_cod` e demais campos como estão; apenas a nova mãe permanece selecionada.

*Notas de implementação (cliente):*

- Na confirmação (**Sim**), ignora o cache de «última mãe já sugerida» usado para evitar pedidos duplicados com código vazio.
- Se a mãe atual for a mesma da última sugestão aplicada com sucesso, **não** repetir o modal (evita dupla confirmação por eventos duplicados do raw-id).
- Ignorar nova troca de mãe enquanto um pedido de sugestão estiver em andamento.

### (G6) Alteração programática de `parent_item_id` (sem sugestão de filho)

Quando `parent_item_id` for alterado **por script** (ex.: resposta de `lookup-hierarchy-by-code` em `change_form.html`), **não** executar **(G1)** nem **(G5)** — evita ciclo código→mãe→código.

**Implementação (cliente):** flag `window.__suppressChildCodeSuggestOnParentChange` ativa em `setParentItemIdProgrammatically(...)`; `onParentItemSelectionChanged` retorna imediatamente se a flag estiver ativa; o polling do raw-id sincroniza o último PK observado para não disparar novamente após a escrita programática.

### (G7) Aplicação programática da sugestão de filho

Ao aplicar a resposta de `suggest-child-code-by-parent/`, o cliente escreve `receita_cod`, `nivel_id`, `classificacao_id` e vigência por script. Durante esse bloco, deve suprimir o lookup inverso `receita_cod` → hierarquia (`syncHierarchyFromCode`) para evitar ciclo sugestão→`change`→lookup inverso→reescrita dos mesmos campos.

**Implementação (cliente):** flag temporária `window.__suppressHierarchyLookupFromCode`; `syncHierarchyFromCode` retorna imediatamente quando a flag está ativa; a flag é desligada ao final da aplicação programática.

### (G3) Mãe inválida para sugestão

Não sugerir (mensagem de erro ou silêncio documentado na implementação) quando:

- mãe sem `classificacao_id` ou sem máscara resolvível;
- mãe com `matriz = false` (filho exige mãe matriz — `spec_itemClassificacao_regras_hierarquia.md`);
- **`NM >= len(mask)`** (mãe já no último nível hierárquico; não há nível filho) → erro **(E2)**.

### (G4) Ordem em relação a outros fluxos

1. Usuário escolhe mãe → **esta spec** (sugestão de código + pré-preenchimentos).
2. Com `receita_cod` e mãe definidos → `spec_itemClassificacao_criar_nome.md` (**P-mãe**).
3. Se o usuário editar manualmente `receita_cod` → `lookup-hierarchy-by-code` (`spec_itemClassificacao_foreignKeys_lookup.md`) pode reconciliar nível/mãe; a spec de lookup **prevalece** sobre a sugestão anterior nesse caso; o preenchimento programático da mãe **não** reabre **(G1)**/**(G5)** (**G6**).

---

## Regra (B) — varredura por radical (nível a nível)

Dado o **radical** da mãe, percorrer **`K = NM+1 … len(mask)`** e, para cada `K`, considerar todos os registros em **(V2b)** `RAMO`:

- extrair o segmento na posição `K-1`;
- se ≠ zero canônico e **(T7)** → incluir `int(segmento)` em `OCUPADO_VIGENTE(K)` (e em `OCUPADO_TOTAL(K)` para **(H)**).

**`K*`** = **menor** `K` (primeiro encontrado de `NM+1` para cima) com `OCUPADO_VIGENTE(K)` não vazio.

| Situação | Nível alvo `L` | Fonte de ocupação |
|----------|----------------|-------------------|
| Existe `K*` | `L = K*` | `OCUPADO_*(K*)` via **RAMO** |
| Não existe `K*` | `L = NM+1` | **FILHOS** **(V2a)** no segmento `NM+1` |

Em ambos os casos aplicam-se **(A)**, **(H)** ou **(E1)** sobre o conjunto escolhido.

*Salto de nível:* se `L > NM+1`, o código sugerido tem zeros canônicos nos níveis intermediários; `nivel_id` pré-preenchido = `L`. O **gravar** continua sujeito a `spec_itemClassificacao_regras_hierarquia.md` e ao modal de `spec_itemClassificacao_validar_hierarquia.md`.

---

## Algoritmo canônico — primeiro slot de detalhamento

### Entrada

- Item mãe `P` (registro completo após seleção no admin).
- Opcional: vigência do formulário; senão vigência de `P` (**(V1)**).

### Passo 0 — Validar estrutura

- `NM ← P.nivel_numero`.
- Se `NM >= len(mask)` → **(E2)**.
- `mask ← digit_mask_for_classificacao_vigencia(classificacao(P), V1.início, V1.fim)` (com fallback da mãe se necessário).
- `radical ← dígitos(P.receita_cod)[:sum(mask[:NM])]`.

### Passo 1 — Varredura **(B)** / `RAMO` **(V2b)**

Para cada `K` de `NM+1` a `len(mask)`:

- Inicializar `OCUPADO_VIGENTE(K)` e `OCUPADO_TOTAL(K)` vazios.
- Para cada registro em **RAMO** com prefixo `radical`:
  - `seg ←` segmento `K-1`; ignorar se zero canônico ou inválido.
  - `v ← int(seg)` → `OCUPADO_TOTAL(K)`; se **(T7)** → também `OCUPADO_VIGENTE(K)`.

`K* ← min { K | K ≥ NM+1 ∧ OCUPADO_VIGENTE(K) ≠ ∅ }` (se existir; varredura ascendente).

### Passo 2 — Escolher `L` e conjunto `OCUPADO`

- Com `K*` → `L ← K*`, usar `OCUPADO_VIGENTE(K*)` / `OCUPADO_TOTAL(K*)`, `strategy_origin = radical_deep`.
- Sem `K*` → `L ← NM+1`; para cada registro em **FILHOS** **(V2a)**, ler segmento na posição **`NM`** (nível `NM+1`); preencher `OCUPADO_*`; `strategy_origin = direct_child`.

### Passo 3 — Expansão **(A)**

Se `OCUPADO_VIGENTE` não vazio → `candidato ← max(OCUPADO_VIGENTE) + 1`; senão → `candidato ← 1` (**(F)**).

Aceitar se `1 ≤ candidato ≤ capacidade(L)` e `candidato ∉ OCUPADO_VIGENTE` → **Passo 5**.

### Passo 4 — Buraco **(H)**

`candidato ←` menor `d` em `1..capacidade(L)` com `d ∉ OCUPADO_VIGENTE`; se não houver → **(E1)**.

### Passo 5 — Montar `receita_cod`

- Segmentos `1..NM` da mãe; segmento `L` ← candidato (zero-padded); `L+1..fim` ← zero canônico.

### Passo 6 — Pré-preenchimentos

- Resolver `nivel_id` para o nível **`L`** por `nivel_numero = L`, `data_registro_fim` = sentinela e vigência compatível **(T7)** com **(V1)** — **sem** filtrar pela `classificacao_id` da mãe (**T12**). Se houver mais de um candidato, escolher o mais recente (`-data_vigencia_inicio, -data_registro_inicio, -pk`) e adicionar aviso de ambiguidade em `notices`. Se não houver nenhum, retornar **(E3)**.
- `classificacao_id` ← `nivel_id.classificacao_id` (pode diferir da classificação da mãe quando o `NivelHierarquico` selecionado for de outra classificação); vigência **(V3)**.
- Se `L > NM+1` → aviso em `notices` (salto sugerido).
- **Não** alterar `matriz` / `receita_nome` (**P-mãe** depois).

---

## Casos de negócio com exemplos

### Exemplo **(A)** — filhos diretos no nível 6 (`FILHOS`)

| Código | Papel |
|--------|--------|
| `1.1.1.2.50.0.0.00.000` | Mãe (NM=5) |
| `1.1.1.2.50.1.0.00.000` | Filho direto (segmento L6 = 1) |
| `1.1.1.2.50.2.0.00.000` | Filho direto (segmento L6 = 2) |

Sem detalhe em **RAMO** nos níveis 7–9 → usa **FILHOS** em `L=6` → `OCUPADO_VIGENTE = {1,2}` → candidato `3` → `1.1.1.2.50.3.0.00.000`.

### Exemplo **(B)** — detalhe no nível 9 (`RAMO`, outra classificação)

| Código | Papel |
|--------|--------|
| `1.1.1.2.50.0.0.00.000` | Mãe (NM=5), `CLASS-RECEITA-UNIAO-2018` |
| `1.1.1.2.50.0.0.00.001` | Outro item, `CLASS-RECEITA-MG-2018`, `parent_item_id` = mãe, segmento L9 = `001` |

**RAMO** (níveis 6–7 sem detalhe; primeiro detalhe em L9) → `K* = 9`, `OCUPADO_VIGENTE(9) = {1}` → candidato `2` → sugestão `1.1.1.2.50.0.0.00.002` (`1112500000002`), `L = 9`.

### Exemplo **(C)** — primeiro detalhe no nível 8 (ignora detalhe mais profundo em L9)

| Código | Papel |
|--------|--------|
| `1.1.1.2.50.0.0.00.000` | Mãe (NM=5) |
| `1.1.1.2.50.0.0.00.001` | Detalhe em L9 (`001`) |
| `1.1.1.2.50.0.0.01.000` | Detalhe em L8 (`01`) |

Níveis 6–7 sem detalhe; **primeiro** com detalhe = L8 → `OCUPADO_VIGENTE(8) = {1}` → candidato `2` → `1.1.1.2.50.0.0.02.000` (`1112500002000`), `L = 8` (não usa L9).

### Exemplo **(H)** — buraco após esgotar expansão

Filhos vigentes nos dígitos `1,2,3,4,7,8,9`; dígitos `5` e `6` existem na BD mas com vigência **incompatível** com a mãe.

- `max(OCUPADO_VIGENTE) + 1 = 10` → inválido para `w=1`.
- Menor `d ∉ OCUPADO_VIGENTE` → **5**.
- Sugestão: `1.1.1.2.50.5.0.00.000`.

### Exemplo **(F)** — sem detalhe em `RAMO` nem em `FILHOS`

Nenhum segmento ≠ zero em **RAMO** para `K ≥ 6`; **FILHOS** vazio → `L = 6`, `candidato = 1` → `1.1.1.2.50.1.0.00.000`.

---

## Erros e mensagens

### (E1) Capacidade esgotada (antigo **A-ERROR**)

**Condição:** Passos 2 e 3 falham — todo `d` em `1..capacidade(L)` pertence a `OCUPADO_VIGENTE`.

**Mensagem (texto orientativo):** informar que todos os valores disponíveis para o nível **L** já estão detalhados com vigência compatível com a mãe / período efetivo, e que não há lacuna reutilizável.

### (E2) Mãe no último nível

**Condição:** `NM >= len(mask)`.

**Mensagem:** não é possível sugerir filho hierárquico — a mãe já ocupa o último nível da máscara.

### (E3) Nível alvo não resolvido

**Condição:** o algoritmo determinou o nível alvo **`L`**, mas não existe `NivelHierarquico` ativo (`data_registro_fim` = sentinela) e com vigência compatível **(T7)** com **(V1)** para `nivel_numero = L` — em **nenhuma** classificação (a busca em **T12** não filtra pela classificação da mãe).

**Mensagem:** informar que não existe nível hierárquico ativo e vigente para o nível sugerido na vigência considerada. Sem esse nível, o formulário não deve preencher `nivel_id` nem `classificacao_id`.

---

## Contrato HTTP (proposto)

Alinhado ao `spec_itemClassificacao_foreignKeys_lookup.md`.

- **Rota (proposta):** `GET …/admin/core/itemclassificacao/suggest-child-code-by-parent/`
- **Parâmetros GET:**

| Parâmetro | Obrigatório | Descrição |
|-----------|-------------|-----------|
| `parent_item_id` | Sim | PK do item mãe. |
| `vigencia_inicio` | Não | Se omitido, usa vigência da mãe. |
| `vigencia_fim` | Não | Idem. |

### Resposta sucesso (`ok: true`)

| Campo | Descrição |
|-------|-----------|
| `ok` | `true` |
| `receita_cod` | Dígitos canônicos sugeridos. |
| `receita_cod_display` | Código formatado para o campo (máscara + vigência). |
| `derived_level` | `number`, `pk`, `display_label` do nível **L**. |
| `classificacao` | Payload no estilo do lookup (PK, rótulo de exibição) da classificação do `derived_level`, isto é, `derived_level.classificacao_id`. |
| `strategy` | `expansion` \| `gap` \| `first` — auditoria. |
| `strategy_origin` | `radical_deep` \| `direct_child` — origem do nível `L` (**Passo 2**). |
| `level_target` | Número do nível `L` sugerido. |
| `notices` | Lista de avisos (ex.: filho com `nivel_numero ≠ L` ignorado). |

### Resposta erro (`ok: false`)

| Campo | Descrição |
|-------|-----------|
| `ok` | `false` |
| `code` | `capacity_exhausted` \| `parent_last_level` \| `level_not_resolvable` \| `invalid_parent` \| … |
| `message` | Texto para o usuário (**E1**, **E2**, **E3**, …). |

---

## Testes automatizados (recomendados)

1. Mãe com dois **FILHOS** em L6 com dígitos `1` e `2`, sem **RAMO** mais profundo → sugere `3` em L6 (**A**, `direct_child`).
2. Mãe + item **RAMO** só em L9 com `001` (outra classificação) → sugere `002` em L9 (**B**, `radical_deep`).
2b. Mãe + detalhe em L8 (`01`) e L9 (`001`) → sugere `02` em L8 (**C**, `radical_deep`; primeiro nível com detalhe).
3. Cenário **(H)** com `5` e `6` só incompatíveis em **FILHOS** L6 → sugere `5`.
4. Sem **RAMO** nem **FILHOS** → `…1…` em L6 (**F**).
5. `OCUPADO_VIGENTE(L) = {1..9}` sem buraco → **(E1)**.
6. Mãe no último nível → **(E2)**.
7. `receita_cod` já preenchido + mesma mãe → não sugere automaticamente (**G1**).
8. `receita_cod` preenchido + troca de mãe **pelo usuário** → modal de atenção → OK recalcula código; Cancelar mantém código (**G5**).
9. Lookup de hierarquia altera mãe com código preenchido → **sem** `confirm` nem sugestão (**G6**).
10. Paridade servidor + JS (integração).
11. Payload de sucesso deriva `classificacao.pk` de `derived_level.classificacao_id`, não diretamente de `parent_item_id.classificacao_id`.
12. Nível **`L`** inexistente em qualquer `NivelHierarquico` ativo e vigente compatível com **(V1)** → erro `level_not_resolvable` (**E3**).
13. Existe `NivelHierarquico` para o nível **`L`** apenas em classificação distinta da mãe (mesma vigência) → sugestão devolve esse nível, `classificacao` do payload reflete essa outra classificação, e `notices` inclui aviso quando há mais de uma versão compatível.

---

## Decisões em aberto (requerem confirmação do produto)

Registradas de forma explícita; o restante do documento já adota o comportamento **mais aderente** ao repositório.

### DD1 — Reutilizar `receita_cod` com registro inativo ou só vigência incompatível

**Comportamento adotado na v1:** a sugestão **pode** devolver um código que **já existe** na BD para outra vigência ou com vigência incompatível com **(V1)** (caso **(H)**). A **unicidade** na gravação segue as regras bitemporais / validação de domínio já existentes.

**Pergunta ao produto:** ao gravar, deve o sistema **sempre** permitir nova linha com o mesmo `receita_cod` e vigência disjunta, ou deve bloquear se existir **qualquer** registro ativo com aquele código na classificação?

### DD2 — Alerta «código já existente»

**Comportamento adotado:** após sugestão, se já existir registro **ativo** com o mesmo `receita_cod`, vigência **(T7)** com **(V1)**, mostrar aviso com link — **sem** exigir mesma classificação (coerente com **RAMO**).

**Pergunta ao produto:** o aviso deve oferecer botão «ir para o próximo dígito» que **reexecuta** este algoritmo excluindo o código encontrado?

### DD3 — Máscara entre classificações no mesmo radical

**Comportamento adotado (v1):** segmentar **RAMO** com a máscara da mãe. Se duas classificações tiverem estruturas incompatíveis com o mesmo prefixo numérico, o comportamento fica indefinido até regra explícita.

---

## Manutenção

- Alterações de contrato JSON ou de critérios de vigência devem manter este arquivo alinhado ao módulo de lookup/sugestão e ao JavaScript do `change_form`.
