# Criação no Admin: sugestão de código filho (`receita_cod`)

Fluxo **add** de `ItemClassificacao`: quando o usuário escolhe item mãe com `receita_cod` vazio, o sistema sugere o primeiro código de detalhamento hierárquico coerente. **Não substitui** `spec_itemClassificacao_regras_hierarquia.md`, lookup inverso (**ITEMLKP**) nem nomenclatura (**ITEMNOM**).

## Objetivo

Dado item mãe na add com `receita_cod` vazio, determinar e preencher o **primeiro** `receita_cod` que:

1. respeita a **máscara** da classificação da mãe (**ITEMCF-30** / **(V1)**);
2. mantém o **prefixo** até **NM** (**ITEMCF-14** / **(T4)**);
3. discrimina o segmento no nível alvo **`L`**, cauda em zero canônico;
4. varre **RAMO** **(ITEMCF-32)** sem filtrar classificação;
5. aplica **(A)/(H)/(F)** conforme **ITEMCF-50**;
6. falha com **ITEMCF-80**–**ITEMCF-82** quando esgotado.

Premissa: endpoint `suggest-child-code-by-parent/`, `classification_item_suggest_child_code.py`, `change_form.html` / JS dedicado; reutiliza `digit_mask_for_classificacao_vigencia`, `split_receita_cod_segments_tolerant`, `_canonical_zero_segment`.

## Referências

- `apps/core/classification_item_suggest_child_code.py`, `classification_item_child_from_change.py`
- `apps/core/classification_item_code_lookup.py` — família lookup-hierarchy / lookup-parent
- `apps/core/code_parent_item_validation.py`
- [`spec_itemClassificacao_regras_hierarquia.md`](spec_itemClassificacao_regras_hierarquia.md) — **ITEMRH**
- [`spec_itemClassificacao_foreignKeys_lookup.md`](spec_itemClassificacao_foreignKeys_lookup.md) — **ITEMLKP**; lookup inverso após código preenchido
- [`spec_itemClassificacao_criar_nome.md`](spec_itemClassificacao_criar_nome.md) — **ITEMNOM** (**P-mãe**)
- [`spec_itemClassificacao_validar_hierarquia.md`](spec_itemClassificacao_validar_hierarquia.md) — **ITEMVH**; salto de nível no submit
- [`spec_itemClassificacao_formulario.md`](spec_itemClassificacao_formulario.md) — **ITEMFORM**
- [`spec_classificador-receita.md`](spec_classificador-receita.md) § **Convenções** — prefixo `ITEMCF`

Termos *deve* / *não deve* / *pode* conforme RFC 2119 (ver `_dev/spec_conventions.md` **Referências**).

**Migração de símbolos legados:**

| Legado                 | ID atual                                |
| ---------------------- | --------------------------------------- |
| `(T1)`–`(T12)`         | `ITEMCF-10`–`ITEMCF-22`                 |
| `(V1)`–`(V3)`, `(V3′)` | `ITEMCF-30`–`ITEMCF-34`                 |
| `(G1)`–`(G7)`          | `ITEMCF-40`–`ITEMCF-46`                 |
| Regra `(B)`            | `ITEMCF-50`                             |
| `(A)` / `(H)` / `(F)`  | `ITEMCF-61` / `ITEMCF-62` / `ITEMCF-63` |
| Passos 0–6             | `ITEMCF-60`–`ITEMCF-66`                 |
| `(E1)`–`(E3)`          | `ITEMCF-80`–`ITEMCF-82`                 |
| Contrato HTTP          | `ITEMCF-90`–`ITEMCF-92`                 |
| `DD1`–`DD3`            | `ITEMCF-110`–`ITEMCF-112`               |
| Atalho v2              | `ITEMCF-120`–`ITEMCF-135`               |

## Como citar este documento

| Mecanismo          | Uso                                                                 |
| ------------------ | ------------------------------------------------------------------- |
| **Seção numerada** | `§ N` / `§ N.M` — navegação neste arquivo.                          |
| **ID normativo**   | `ITEMCF-NN` — citação estável.                                      |
| **Prefixo**        | `ITEMCF` — ver § **Convenções** em `spec_classificador-receita.md`. |

**Índice de IDs normativos deste arquivo:**

| ID         | Tema      | Seção | Resumo                                                                                       |
| ---------- | --------- | ----- | -------------------------------------------------------------------------------------------- |
| ITEMCF-10  | Notação   | 2     | **(T1)** `NM` — `nivel_numero` do item mãe.                                                  |
| ITEMCF-11  | Notação   | 2     | **(T2)** `L` — nível alvo do filho (`K*` ou `NM+1`).                                         |
| ITEMCF-12  | Notação   | 3     | **(T2a)** `K*` — menor nível com detalhe em **RAMO**.                                        |
| ITEMCF-13  | Notação   | 3     | **(T3)** máscara por `estrutura_codigo` + **(V1)**.                                          |
| ITEMCF-14  | Notação   | 3     | **(T4)** radical — primeiros dígitos da mãe até **NM**.                                      |
| ITEMCF-15  | Notação   | 3     | **(T5)** zero canônico (`_canonical_zero_segment`).                                          |
| ITEMCF-16  | Notação   | 3     | **(T6)** registro ativo (sentinela transaction time).                                        |
| ITEMCF-17  | Notação   | 3     | **(T7)** vigência compatível (consulta / sobreposição).                                      |
| ITEMCF-18  | Notação   | 3     | **(T8)** vigência compatível (gravação — contida na mãe).                                    |
| ITEMCF-19  | Notação   | 3     | **(T9)** valor de segmento — comparação numérica zero-padded.                                |
| ITEMCF-20  | Notação   | 3     | **(T10)** capacidade do nível `L`.                                                           |
| ITEMCF-21  | Notação   | 3     | **(T11)** `classificacao_id` derivado do `NivelHierarquico` de **`L`**.                      |
| ITEMCF-22  | Notação   | 3     | **(T12)** resolução de `nivel_id` por `nivel_numero = L` (sem filtrar classificação da mãe). |
| ITEMCF-30  | Vigência  | 4     | **(V1)** intervalo de referência (formulário ou mãe).                                        |
| ITEMCF-31  | Vigência  | 4     | **(V2a)** conjunto **FILHOS** — filhos diretos da mãe.                                       |
| ITEMCF-32  | Vigência  | 4     | **(V2b)** conjunto **RAMO** — varredura por radical.                                         |
| ITEMCF-33  | Vigência  | 4     | **(V3)** pré-preenchimento de vigência na add (copiar da mãe se vazio).                      |
| ITEMCF-34  | Vigência  | 13    | **(V3′)** vigência do filho na entrada pelo atalho change → add.                             |
| ITEMCF-40  | Gatilho   | 5     | **(G1)** sugerir após mãe com `receita_cod` vazio; não repetir se código preenchido.         |
| ITEMCF-41  | Gatilho   | 5     | **(G2)** definição de `receita_cod` vazio (sem dígitos significativos).                      |
| ITEMCF-42  | Gatilho   | 5     | **(G3)** não sugerir: mãe inválida, não matriz, último nível (**E2**).                       |
| ITEMCF-43  | Gatilho   | 5     | **(G4)** ordem: sugestão → **ITEMNOM** → lookup inverso.                                     |
| ITEMCF-44  | Modal     | 5     | **(G5)** troca de mãe com código preenchido — modal tri-estado.                              |
| ITEMCF-45  | Gatilho   | 5     | **(G6)** alteração programática de mãe — suprimir **G1**/**G5**.                             |
| ITEMCF-46  | Gatilho   | 5     | **(G7)** aplicação programática da sugestão — suprimir lookup inverso.                       |
| ITEMCF-50  | Algoritmo | 6     | **(B)** varredura por radical; escolha `K*` / **FILHOS**.                                    |
| ITEMCF-60  | Algoritmo | 7     | Passo 0 — validar estrutura, máscara, radical.                                               |
| ITEMCF-61  | Algoritmo | 7     | **(A)** expansão `max(OCUPADO_VIGENTE)+1` ou `1` (**F**).                                    |
| ITEMCF-62  | Algoritmo | 7     | **(H)** buraco — menor `d` livre.                                                            |
| ITEMCF-63  | Algoritmo | 7     | **(F)** primeiro detalhe sem ocupação.                                                       |
| ITEMCF-66  | Algoritmo | 7     | Passo 6 — pré-preencher `nivel_id`, `classificacao_id`, avisos.                              |
| ITEMCF-80  | Erro      | 9     | **(E1)** capacidade esgotada no nível **L**.                                                 |
| ITEMCF-81  | Erro      | 9     | **(E2)** mãe no último nível (`NM >= len(mask)`).                                            |
| ITEMCF-82  | Erro      | 9     | **(E3)** `NivelHierarquico` não resolvido para **L**.                                        |
| ITEMCF-90  | API       | 10    | `GET suggest-child-code-by-parent/` — parâmetros e rota.                                     |
| ITEMCF-91  | API       | 10    | Resposta `ok: true` — shape JSON.                                                            |
| ITEMCF-92  | API       | 10    | Resposta `ok: false` — códigos de erro.                                                      |
| ITEMCF-100 | Teste     | 10    | Casos automatizados v1 (lista § **10**).                                                     |
| ITEMCF-110 | Decisão   | 12    | **DD1** — reutilizar código com vigência incompatível.                                       |
| ITEMCF-111 | Decisão   | 12    | **DD2** — alerta código já existente.                                                        |
| ITEMCF-112 | Decisão   | 12    | **DD3** — máscara entre classificações no mesmo radical.                                     |
| ITEMCF-120 | Atalho v2 | 13    | Botão «+ Criar Código Filho» na change.                                                      |
| ITEMCF-130 | Atalho v2 | 13    | Modais confirmação / bloqueio Detalhe.                                                       |
| ITEMCF-135 | Atalho v2 | 13    | **(G5)** não aplica na chegada pelo atalho.                                                  |

**Índice por tema:**

| Tema        | IDs                                |
| ----------- | ---------------------------------- |
| Notação     | ITEMCF-10 … ITEMCF-22              |
| Vigência    | ITEMCF-30 … ITEMCF-34              |
| Gatilhos UI | ITEMCF-40 … ITEMCF-46              |
| Algoritmo   | ITEMCF-50, ITEMCF-60 … ITEMCF-66   |
| Erros       | ITEMCF-80 … ITEMCF-82              |
| API         | ITEMCF-90 … ITEMCF-92              |
| Teste       | ITEMCF-100                         |
| Decisão     | ITEMCF-110 … ITEMCF-112            |
| Atalho v2   | ITEMCF-120, ITEMCF-130, ITEMCF-135 |

---

## 1. Escopo

### Escopo (v1)

- Tela **add** de `ItemClassificacao` no admin.
- Gatilho: seleção de `parent_item_id` (lupa ou equivalente) com `receita_cod` **vazio** (*trim* / só pontuação = vazio).
- Sugestão de `receita_cod` (dígitos canônicos, sem pontos no POST interno; formatação visual conforme máscara no cliente).
- Pré-preenchimento **recomendado** no mesmo passo: `nivel_id` (= **`L`** resolvido), `classificacao_id` (= classificação do `nivel_id` resolvido, não diretamente da mãe), e datas de vigência do formulário **se ainda vazias** (ver **(V3)** (**ITEMCF-33**)).
- Aviso informativo (não bloqueante na sugestão) quando **`L > NM+1`** — salto de nível em relação à mãe; confirmação no submit conforme `spec_itemClassificacao_validar_hierarquia.md`.
- Mensagens de erro **(E1)** e aviso não bloqueante se o código sugerido já existir (ver **§ 11** — **ITEMCF-111** / **DD2**).

### Fora de escopo (v1)

- Alteração (`change`) de registro existente **como gatilho de sugestão** (a sugestão automática na change continua fora; ver **v2** abaixo para o **atalho** change → add).
- Geração de `item_id`, `receita_nome`, `matriz`, bases legais.
- Persistência (`save`); apenas pré-preenchimento e validação de UI.
- Protocolo completo «código já existente → link e próximo dígito» (item separado no [`_dev/toDo.md`](../toDo.md)).

---

### Specs relacionadas

| Spec                                                                                           | Relação                                                                  |
| ---------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| [`spec_itemClassificacao_regras_hierarquia.md`](spec_itemClassificacao_regras_hierarquia.md)   | Filho direto = nível **NM+1**; zeros canônicos; vigência contida na mãe. |
| [`spec_itemClassificacao_foreignKeys_lookup.md`](spec_itemClassificacao_foreignKeys_lookup.md) | Lookup inverso após `receita_cod` preenchido.                            |
| [`spec_itemClassificacao_criar_nome.md`](spec_itemClassificacao_criar_nome.md)                 | **ITEMNOM** — **P-mãe** após mãe/código.                                 |
| [`spec_itemClassificacao_validar_hierarquia.md`](spec_itemClassificacao_validar_hierarquia.md) | Salto de nível no submit.                                                |
| [`spec_itemClassificacao_formulario.md`](spec_itemClassificacao_formulario.md)                 | Largura `receita_cod`; limpar add.                                       |
| [`_dev/toDo.md`](../toDo.md)                                                                   | Alerta código existente — ver **ITEMCF-111**.                            |

## 2. Notação canónica (**ITEMCF-10**–**ITEMCF-22**)

- **(T1) `NM`:** `nivel_numero` do item mãe selecionado (`parent_item_id`).
- **(T2) `L`:** nível alvo do filho sugerido (`nivel_numero` do item a criar). **`L = K*`** quando a varredura **(V2b)** (**ITEMCF-32**) encontra detalhe; senão **`L = NM + 1`** via **(V2a)** (**ITEMCF-31**).
- **(T2a) `K*`:** **menor** índice de nível `K ∈ {NM+1, …, len(mask)}` (varredura ascendente) para o qual existe pelo menos um registro em **(V2b)** (**ITEMCF-32**) com segmento `K` ≠ zero canônico e vigência **(T7)** (**ITEMCF-17**) com **(V1)** (**ITEMCF-30**).
- **(T3) `máscara`:** lista de larguras por segmento derivada de `estrutura_codigo` da classificação da mãe (`digit_mask_for_classificacao_vigencia`), vigência efetiva **(V1)** (**ITEMCF-30**).
- **(T4) `radical`:** primeiros `sum(mask[0:NM])` **dígitos** de `receita_cod` da mãe (apenas `0-9`, sem pontuação).
- **(T5) `zero canônico`:** segmento em que todos os caracteres são `'0'` (`_canonical_zero_segment`).
- **(T6) `registro ativo`:** `data_registro_fim` = sentinela de transaction time do projeto (`TRANSACTION_TIME_SENTINEL` / `transaction_time_sentinel_for_query()`).
- **(T7) `vigência compatível (consulta)`:** sobreposição entre o intervalo do candidato e o intervalo de referência **(V1)** (**ITEMCF-30**): `início_ref ≤ fim_candidato` e `fim_ref ≥ início_candidato` (datas inclusivas).
- **(T8) `vigência compatível (gravação)`:** intervalo do **novo** filho deve estar **contido** no da mãe (`spec_itemClassificacao_regras_hierarquia.md`) — validação no `clean()` / domínio, não só na sugestão.
- **(T9) `valor de segmento`:** texto do segmento na posição do nível; comparado **numericamente** (`int(segmento)`), com saída **zero-padded** à largura `mask[L-1]`.
- **(T10) `capacidade do nível L`:** `10^w - 1` onde `w = mask[L-1]` (ex.: `w=1` → valores `1..9`; `w=2` → `1..99`). O valor **0** / zero canônico **não** é candidato a detalhamento.
- **(T11) `classificação do filho`:** `classificacao_id` do formulário de criação deve ser derivado do `NivelHierarquico` resolvido para **`L`** (`nivel_id.classificacao_id`). Se esse nível não for resolvido, a sugestão falha explicitamente (**E3**).
- **(T12) `resolução do nível alvo`:** o `NivelHierarquico` correspondente ao nível **`L`** sugerido deve ser buscado **apenas** por `nivel_numero = L`, `data_registro_fim` = sentinela e vigência compatível **(T7)** (**ITEMCF-17**) com **(V1)** (**ITEMCF-30**). **Não** restringir pela `classificacao_id` da mãe. Em caso de múltiplos candidatos, ordenar por `-data_vigencia_inicio, -data_registro_inicio, -pk`, escolher o primeiro e emitir aviso não bloqueante de ambiguidade.

---

## 3. Vigência e classificação na consulta

### **ITEMCF-30** **(V1)** Intervalo de referência para a sugestão

Ordem de prioridade:

1. Se o formulário tiver `data_vigencia_inicio` **e** `data_vigencia_fim` preenchidos → usar esse par.
2. Senão → usar `data_vigencia_inicio` e `data_vigencia_fim` do **item mãe** selecionado.

A máscara é resolvida com `classificacao_id` da mãe e **(V1)** (**ITEMCF-30**). Se a máscara não for obtida com **(V1)** (**ITEMCF-30**), repetir o fallback já usado no repositório: vigência **só** da mãe (`digit_mask_for_classificacao_vigencia(classificacao_pk, mãe.início, mãe.fim)`).

### **ITEMCF-31** **(V2a)** Filhos diretos da mãe — `FILHOS`

Conjunto usado para **(A)/(H)/(F)** no nível **`NM+1`** quando a varredura **(V2b)** (**ITEMCF-32**) não encontra detalhe em nenhum nível:

- `parent_item_id` = PK do item mãe selecionado no formulário (filhos **diretos**);
- `data_registro_fim` = sentinela (**(T6)** (**ITEMCF-16**));
- **(T7)** (**ITEMCF-17**) com **(V1)** (**ITEMCF-30**);
- **sem** filtro por `classificacao_id` / identidade semântica de classificação (um filho direto pode estar em outra edição ou classificação estatística, p.ex. `CLASS-RECEITA-MG-2018` com mãe `CLASS-RECEITA-UNIAO-2018`).

Para cada registro em **FILHOS**, o segmento considerado no passo **filhos** é sempre o da posição **`NM+1`** na máscara (índice `NM`), **independentemente** do `nivel_numero` gravado no filho (ex.: filho com `nivel_numero = 9` mas segmento `0` no nível 6 ainda conta `0` nessa posição; o valor no nível 9 não entra neste passo).

### **ITEMCF-32** **(V2b)** Varredura por radical — `RAMO`

Conjunto usado na regra **(B)** (nível a nível, profundidade máxima):

- `receita_cod` (só dígitos) com prefixo igual ao **radical** **(T4)** (**ITEMCF-14**) da mãe (`startswith`);
- `data_registro_fim` = sentinela (**(T6)** (**ITEMCF-16**));
- **(T7)** (**ITEMCF-17**) com **(V1)** (**ITEMCF-30**);
- **sem** filtro por `classificacao_id`;
- **sem** exigir `parent_item_id` = mãe (inclui ramos em outras classificações que compartilham o mesmo prefixo numérico até **NM**).

*Nota:* a máscara **(T3)** (**ITEMCF-13**) continua sendo resolvida pela classificação/vigência da **mãe**; códigos de outras classificações que compartilhem estrutura de níveis compatível são segmentados com essa máscara. Se no futuro houver máscaras incompatíveis entre classificações com o mesmo radical, documentar exceção — fora do v1.

### **ITEMCF-33** **(V3)** Pré-preenchimento de vigência no formulário (fluxo normal add / lupa)

Se, no momento da sugestão, `data_vigencia_inicio` e/ou `data_vigencia_fim` do formulário estiverem vazios, o cliente **pode** copiar as datas da mãe para esses campos (comportamento adotado nesta spec por aderência ao [`_dev/toDo.md`](../toDo.md)). Isso não dispensa **(T8)** (**ITEMCF-18**) no servidor.

**Nota:** o atalho **change → add** (**v2**, **(V3′)** (**ITEMCF-34**)) usa regras **distintas** e **prioritárias** sobre **(V3)** (**ITEMCF-33**) para as datas iniciais do filho; ver secção «Atalho desde change (v2)».

---

## 4. Gatilhos e guardrails de UI

### **ITEMCF-40** **(G1)** Quando sugerir

- **Disparar automaticamente** após seleção válida de `parent_item_id` se `receita_cod` estiver vazio (**G2**).
- **Disparar novamente automaticamente** se o usuário trocar a mãe e `receita_cod` continuar vazio.
- **Não disparar automaticamente** se `receita_cod` tiver qualquer dígito significativo (**G2** negado) — ver **(G5)** para troca de mãe nesse caso.

### **ITEMCF-41** **(G2)** `receita_cod` vazio

Campo considerado vazio: ausência de dígitos após remover pontuação de máscara e espaços. Vale para código informado manualmente ou por sugestão anterior (não se distingue a origem).

### **ITEMCF-44** **(G5)** Troca de mãe com código já preenchido

Quando o usuário altera `parent_item_id` e `receita_cod` **não** está vazio (**G2**):

1. **Não** substituir o código automaticamente.
2. **Antes** de exibir qualquer modal, o cliente **deve** guardar um *snapshot* da mãe **anterior** (PK, rótulo de exibição do widget semântico e estado de polling do raw-id) e chamar o endpoint `suggest-child-code-by-parent/` para a **nova** mãe selecionada.
   - o snapshot **deve** ser derivado do **PK observado imediatamente antes** da troca (ex.: `lastParentItemPk` no polling), cruzado com `lastConfirmedParentSnapshot` quando o PK coincidir;
   - o snapshot **deve sobreviver** a estados intermediários do popup da lupa (raw-id do Django admin), nos quais o hidden de `parent_item_id` pode ficar **momentaneamente vazio** entre o valor antigo e o novo — **não** substituir nem apagar o snapshot confirmado nesses transientes;
   - após preenchimento programático da mãe (ex.: `syncHierarchyFromCode`, **G6**), o cliente **deve** consolidar o snapshot com o PK assim que o hidden for escrito (e, quando disponível, `parent.name` do payload de hierarquia), mesmo que o display semântico ainda não tenha sido renderizado.
3. Se o endpoint retornar **erro** (`ok: false`, incluindo **E1**, **E2**, **E3** e demais códigos de falha da sugestão):
   - **reverter** automaticamente `parent_item_id` para a mãe anterior (PK + display);
   - **não** abrir o modal;
   - exibir a mensagem de erro **inline** sob o campo «Item Mãe» (mesmo padrão visual dos erros de sugestão com código vazio);
   - **não** alterar `receita_cod`, `nivel_id`, `classificacao_id` nem demais campos do formulário.
4. Se o endpoint retornar **sucesso** (`ok: true`), exibir **modal de atenção** centrado (mesma família visual do aviso de salto de nível ao gravar — ícone ⚠️, título «Atenção!»; ver também [`spec_itemClassificacao_validar_hierarquia.md`](spec_itemClassificacao_validar_hierarquia.md), seção «Modal de confirmação (G5)»), **somente após** receber a resposta, com:
   - corpo dinâmico:
     ```
     Deseja atualizar o código de natureza de receita atual?
       - atual: <receita_cod_display do formulário>
       - novo:  <receita_cod_display retornado pelo endpoint>
     ```
   - os códigos exibidos **devem** usar **máscara de apresentação** (`receita_cod_display` / valor já formatado no campo), **nunca** apenas dígitos canônicos crus;
   - botões: **Cancelar** | **Manter Atual** | **Atualizar**.
5. **Cancelar** (inclui tecla **Escape** e clique no **overlay**):
   - reverter `parent_item_id` para a mãe anterior (PK + display);
   - se o snapshot tiver **PK** mas **display** ou rótulo vazios, o cliente **deve** re-buscar o rótulo semântico pelo endpoint `semantic-lookup/item/{pk}/` (mesmo contrato do widget `foreign_key_semantic_raw_id.html`) antes de concluir a reversão visual;
   - manter `receita_cod`, `nivel_id` e `classificacao_id` **inalterados**;
   - re-aplicar nomenclatura (**P-mãe**) coerente com a mãe **anterior** — ver [`spec_itemClassificacao_criar_nome.md`](spec_itemClassificacao_criar_nome.md), seção «P-mãe durante confirmação (G5)».
6. **Manter Atual**:
   - manter a **nova** mãe selecionada;
   - manter `receita_cod`, `nivel_id` e `classificacao_id` **exatamente** como estavam **antes** da troca de mãe que disparou **(G5)**;
   - **não** executar a sugestão nem atualizar campos derivados dela;
   - aplicar **P-mãe** para a **nova** mãe (sem alterar o código).
7. **Atualizar**:
   - manter a **nova** mãe selecionada;
   - executar o mesmo fluxo de sugestão já obtido (**Passo 6**), **substituindo** `receita_cod` e campos derivados (`nivel_id`, `classificacao_id`, vigência quando vazia, avisos, nomenclatura via `applyNamingAfterParentSuggest`, etc.).

*Notas de implementação (cliente):*

- **Snapshot e popup da lupa:** manter `parentFkTransitionFromPk` (ou equivalente) quando o polling detectar PK vazio transitório após um PK não vazio; só limpar `lastConfirmedParentSnapshot` quando a remoção for real (hidden vazio **sem** troca iminente para outro PK). Durante **(G5)** em andamento, **não** atualizar o snapshot confirmado a partir de leituras transitórias.
- **Restauração sem display:** `restoreParentItemSnapshot` aplica PK + textos em cache; se faltar display/rótulo, chamar `semantic-lookup` (`kind=item`) e repovoar display, `label_link` e `nome_mae` como o widget já faz.
- Durante a chamada ao endpoint e enquanto o modal estiver aberto, **P-mãe** fica **suspenso** — ver [`spec_itemClassificacao_criar_nome.md`](spec_itemClassificacao_criar_nome.md).
- Em **Atualizar**, ignorar o cache interno de «última mãe para a qual a sugestão foi **aplicada** com sucesso», usado para evitar pedidos duplicados quando `receita_cod` está vazio (**G1**).
- Em **Manter Atual**, **não** registrar a nova mãe nesse cache de sugestão aplicada (pois o código **não** foi recalculado para ela).
- Se a mãe atual for a mesma da última sugestão **aplicada** com sucesso e o código já reflete essa sugestão, **não** repetir o modal (evita dupla confirmação por eventos duplicados do raw-id).
- Ignorar nova troca de mãe enquanto um pedido de sugestão ou um modal **(G5)** estiver em andamento.
- O componente `showCoreAttentionModal` deve ser estendido (ou substituído por variante dedicada) para retorno **tri-estado** (`cancel` | `keep` | `update`).

### **ITEMCF-45** **(G6)** Alteração programática de `parent_item_id` (sem sugestão de filho)

Quando `parent_item_id` for alterado **por script** (ex.: resposta de `lookup-hierarchy-by-code` em `change_form.html`), **não** executar **(G1)** nem **(G5)** — evita ciclo código→mãe→código.

**Implementação (cliente):** flag `window.__suppressChildCodeSuggestOnParentChange` ativa em `setParentItemIdProgrammatically(...)`; `onParentItemSelectionChanged` retorna imediatamente se a flag estiver ativa; o polling do raw-id sincroniza o último PK observado para não disparar novamente após a escrita programática.

### **ITEMCF-46** **(G7)** Aplicação programática da sugestão de filho

Ao aplicar a resposta de `suggest-child-code-by-parent/`, o cliente escreve `receita_cod`, `nivel_id`, `classificacao_id` e vigência por script. Durante esse bloco, deve suprimir o lookup inverso `receita_cod` → hierarquia (`syncHierarchyFromCode`) para evitar ciclo sugestão→`change`→lookup inverso→reescrita dos mesmos campos.

**Implementação (cliente):** flag temporária `window.__suppressHierarchyLookupFromCode`; `syncHierarchyFromCode` retorna imediatamente quando a flag está ativa; a flag é desligada ao final da aplicação programática.

### **ITEMCF-42** **(G3)** Mãe inválida para sugestão

Não sugerir (mensagem de erro ou silêncio documentado na implementação) quando:

- mãe sem `classificacao_id` ou sem máscara resolvível;
- mãe com `matriz = false` (filho exige mãe matriz — `spec_itemClassificacao_regras_hierarquia.md`);
- **`NM >= len(mask)`** (mãe já no último nível hierárquico; não há nível filho) → erro **(E2)**.

### **ITEMCF-43** **(G4)** Ordem em relação a outros fluxos

1. Usuário escolhe mãe → **esta spec** (sugestão de código + pré-preenchimentos).
2. Com `receita_cod` e mãe definidos → `spec_itemClassificacao_criar_nome.md` (**P-mãe**).
3. Se o usuário editar manualmente `receita_cod` → `lookup-hierarchy-by-code` (`spec_itemClassificacao_foreignKeys_lookup.md`) pode reconciliar nível/mãe; a spec de lookup **prevalece** sobre a sugestão anterior nesse caso; o preenchimento programático da mãe **não** reabre **(G1)**/**(G5)** (**G6**).

---

## 5. Regra (B) (**ITEMCF-50**)

Dado o **radical** da mãe, percorrer **`K = NM+1 … len(mask)`** e, para cada `K`, considerar todos os registros em **(V2b)** (**ITEMCF-32**) `RAMO`:

- extrair o segmento na posição `K-1`;
- se ≠ zero canônico e **(T7)** (**ITEMCF-17**) → incluir `int(segmento)` em `OCUPADO_VIGENTE(K)` (e em `OCUPADO_TOTAL(K)` para **(H)**).

**`K*`** = **menor** `K` (primeiro encontrado de `NM+1` para cima) com `OCUPADO_VIGENTE(K)` não vazio.

| Situação        | Nível alvo `L` | Fonte de ocupação                                       |
| --------------- | -------------- | ------------------------------------------------------- |
| Existe `K*`     | `L = K*`       | `OCUPADO_*(K*)` via **RAMO**                            |
| Não existe `K*` | `L = NM+1`     | **FILHOS** **(V2a)** (**ITEMCF-31**) no segmento `NM+1` |

Em ambos os casos aplicam-se **(A)**, **(H)** ou **(E1)** sobre o conjunto escolhido.

*Salto de nível:* se `L > NM+1`, o código sugerido tem zeros canônicos nos níveis intermediários; `nivel_id` pré-preenchido = `L`. O **gravar** continua sujeito a `spec_itemClassificacao_regras_hierarquia.md` e ao modal de `spec_itemClassificacao_validar_hierarquia.md`.

---

## 6. Algoritmo canônico (**ITEMCF-60**–**ITEMCF-66**)

### Entrada

- Item mãe `P` (registro completo após seleção no admin).
- Opcional: vigência do formulário; senão vigência de `P` (**(V1)** (**ITEMCF-30**)).

### Passo 0 — Validar estrutura (**ITEMCF-60**)

- `NM ← P.nivel_numero`.
- Se `NM >= len(mask)` → **(E2)**.
- `mask ← digit_mask_for_classificacao_vigencia(classificacao(P), V1.início, V1.fim)` (com fallback da mãe se necessário).
- `radical ← dígitos(P.receita_cod)[:sum(mask[:NM])]`.

### Passo 1 — Varredura **(B)** / `RAMO` **(V2b)** (**ITEMCF-32**)

Para cada `K` de `NM+1` a `len(mask)`:

- Inicializar `OCUPADO_VIGENTE(K)` e `OCUPADO_TOTAL(K)` vazios.
- Para cada registro em **RAMO** com prefixo `radical`:
  - `seg ←` segmento `K-1`; ignorar se zero canônico ou inválido.
  - `v ← int(seg)` → `OCUPADO_TOTAL(K)`; se **(T7)** (**ITEMCF-17**) → também `OCUPADO_VIGENTE(K)`.

`K* ← min { K | K ≥ NM+1 ∧ OCUPADO_VIGENTE(K) ≠ ∅ }` (se existir; varredura ascendente).

### Passo 2 — Escolher `L` e conjunto `OCUPADO`

- Com `K*` → `L ← K*`, usar `OCUPADO_VIGENTE(K*)` / `OCUPADO_TOTAL(K*)`, `strategy_origin = radical_deep`.
- Sem `K*` → `L ← NM+1`; para cada registro em **FILHOS** **(V2a)** (**ITEMCF-31**), ler segmento na posição **`NM`** (nível `NM+1`); preencher `OCUPADO_*`; `strategy_origin = direct_child`.

### Passo 3 — Expansão **(A)** (**ITEMCF-61**)

Se `OCUPADO_VIGENTE` não vazio → `candidato ← max(OCUPADO_VIGENTE) + 1`; senão → `candidato ← 1` (**(F)**).

Aceitar se `1 ≤ candidato ≤ capacidade(L)` e `candidato ∉ OCUPADO_VIGENTE` → **Passo 5**.

### Passo 4 — Buraco **(H)** (**ITEMCF-62**)

`candidato ←` menor `d` em `1..capacidade(L)` com `d ∉ OCUPADO_VIGENTE`; se não houver → **(E1)**.

### Passo 5 — Montar `receita_cod`

- Segmentos `1..NM` da mãe; segmento `L` ← candidato (zero-padded); `L+1..fim` ← zero canônico.

### Passo 6 — Pré-preenchimentos (**ITEMCF-66**)

- Resolver `nivel_id` para o nível **`L`** por `nivel_numero = L`, `data_registro_fim` = sentinela e vigência compatível **(T7)** (**ITEMCF-17**) com **(V1)** (**ITEMCF-30**) — **sem** filtrar pela `classificacao_id` da mãe (**T12**). Se houver mais de um candidato, escolher o mais recente (`-data_vigencia_inicio, -data_registro_inicio, -pk`) e adicionar aviso de ambiguidade em `notices`. Se não houver nenhum, retornar **(E3)**.
- `classificacao_id` ← `nivel_id.classificacao_id` (pode diferir da classificação da mãe quando o `NivelHierarquico` selecionado for de outra classificação); vigência **(V3)** (**ITEMCF-33**).
- Se `L > NM+1` → aviso em `notices` (salto sugerido).
- **Não** alterar `matriz` / `receita_nome` (**P-mãe** depois).

---

## 7. Casos de negócio com exemplos

### Exemplo **(A)** — filhos diretos no nível 6 (`FILHOS`)

| Código                  | Papel                          |
| ----------------------- | ------------------------------ |
| `1.1.1.2.50.0.0.00.000` | Mãe (NM=5)                     |
| `1.1.1.2.50.1.0.00.000` | Filho direto (segmento L6 = 1) |
| `1.1.1.2.50.2.0.00.000` | Filho direto (segmento L6 = 2) |

Sem detalhe em **RAMO** nos níveis 7–9 → usa **FILHOS** em `L=6` → `OCUPADO_VIGENTE = {1,2}` → candidato `3` → `1.1.1.2.50.3.0.00.000`.

### Exemplo **(B)** — detalhe no nível 9 (`RAMO`, outra classificação)

| Código                  | Papel                                                                            |
| ----------------------- | -------------------------------------------------------------------------------- |
| `1.1.1.2.50.0.0.00.000` | Mãe (NM=5), `CLASS-RECEITA-UNIAO-2018`                                           |
| `1.1.1.2.50.0.0.00.001` | Outro item, `CLASS-RECEITA-MG-2018`, `parent_item_id` = mãe, segmento L9 = `001` |

**RAMO** (níveis 6–7 sem detalhe; primeiro detalhe em L9) → `K* = 9`, `OCUPADO_VIGENTE(9) = {1}` → candidato `2` → sugestão `1.1.1.2.50.0.0.00.002` (`1112500000002`), `L = 9`.

### Exemplo **(C)** — primeiro detalhe no nível 8 (ignora detalhe mais profundo em L9)

| Código                  | Papel                 |
| ----------------------- | --------------------- |
| `1.1.1.2.50.0.0.00.000` | Mãe (NM=5)            |
| `1.1.1.2.50.0.0.00.001` | Detalhe em L9 (`001`) |
| `1.1.1.2.50.0.0.01.000` | Detalhe em L8 (`01`)  |

Níveis 6–7 sem detalhe; **primeiro** com detalhe = L8 → `OCUPADO_VIGENTE(8) = {1}` → candidato `2` → `1.1.1.2.50.0.0.02.000` (`1112500002000`), `L = 8` (não usa L9).

### Exemplo **(H)** — buraco após esgotar expansão

Filhos vigentes nos dígitos `1,2,3,4,7,8,9`; dígitos `5` e `6` existem na BD mas com vigência **incompatível** com a mãe.

- `max(OCUPADO_VIGENTE) + 1 = 10` → inválido para `w=1`.
- Menor `d ∉ OCUPADO_VIGENTE` → **5**.
- Sugestão: `1.1.1.2.50.5.0.00.000`.

### Exemplo **(F)** — sem detalhe em `RAMO` nem em `FILHOS`

Nenhum segmento ≠ zero em **RAMO** para `K ≥ 6`; **FILHOS** vazio → `L = 6`, `candidato = 1` → `1.1.1.2.50.1.0.00.000`.

---

## 8. Erros e mensagens (**ITEMCF-80**–**ITEMCF-82**)

### **ITEMCF-80** **(E1)** Capacidade esgotada (antigo **A-ERROR**)

**Condição:** Passos 2 e 3 falham — todo `d` em `1..capacidade(L)` pertence a `OCUPADO_VIGENTE`.

**Mensagem (texto orientativo):** informar que todos os valores disponíveis para o nível **L** já estão detalhados com vigência compatível com a mãe / período efetivo, e que não há lacuna reutilizável.

### **ITEMCF-81** **(E2)** Mãe no último nível

**Condição:** `NM >= len(mask)`.

**Mensagem:** não é possível sugerir filho hierárquico — a mãe já ocupa o último nível da máscara.

### **ITEMCF-82** **(E3)** Nível alvo não resolvido

**Condição:** o algoritmo determinou o nível alvo **`L`**, mas não existe `NivelHierarquico` ativo (`data_registro_fim` = sentinela) e com vigência compatível **(T7)** (**ITEMCF-17**) com **(V1)** (**ITEMCF-30**) para `nivel_numero = L` — em **nenhuma** classificação (a busca em **T12** não filtra pela classificação da mãe).

**Mensagem:** informar que não existe nível hierárquico ativo e vigente para o nível sugerido na vigência considerada. Sem esse nível, o formulário não deve preencher `nivel_id` nem `classificacao_id`.

---

## 9. Contrato HTTP (proposto) (**ITEMCF-90**–**ITEMCF-92**)

Alinhado ao `spec_itemClassificacao_foreignKeys_lookup.md`.

- **Rota (proposta):** `GET …/admin/core/itemclassificacao/suggest-child-code-by-parent/`
- **Parâmetros GET:**

| Parâmetro         | Obrigatório | Descrição                        |
| ----------------- | ----------- | -------------------------------- |
| `parent_item_id`  | Sim         | PK do item mãe.                  |
| `vigencia_inicio` | Não         | Se omitido, usa vigência da mãe. |
| `vigencia_fim`    | Não         | Idem.                            |

### Resposta sucesso (`ok: true`)

| Campo                 | Descrição                                                                                                                           |
| --------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `ok`                  | `true`                                                                                                                              |
| `receita_cod`         | Dígitos canônicos sugeridos.                                                                                                        |
| `receita_cod_display` | Código formatado para o campo (máscara + vigência).                                                                                 |
| `derived_level`       | `number`, `pk`, `display_label` do nível **L**.                                                                                     |
| `classificacao`       | Payload no estilo do lookup (PK, rótulo de exibição) da classificação do `derived_level`, isto é, `derived_level.classificacao_id`. |
| `strategy`            | `expansion` \| `gap` \| `first` — auditoria.                                                                                        |
| `strategy_origin`     | `radical_deep` \| `direct_child` — origem do nível `L` (**Passo 2**).                                                               |
| `level_target`        | Número do nível `L` sugerido.                                                                                                       |
| `notices`             | Lista de avisos (ex.: filho com `nivel_numero ≠ L` ignorado).                                                                       |

### Resposta erro (`ok: false`)

| Campo     | Descrição                                                                                      |
| --------- | ---------------------------------------------------------------------------------------------- |
| `ok`      | `false`                                                                                        |
| `code`    | `capacity_exhausted` \| `parent_last_level` \| `level_not_resolvable` \| `invalid_parent` \| … |
| `message` | Texto para o usuário (**E1**, **E2**, **E3**, …).                                              |

---

## 10. Testes automatizados (recomendados) (**ITEMCF-100**)

1. Mãe com dois **FILHOS** em L6 com dígitos `1` e `2`, sem **RAMO** mais profundo → sugere `3` em L6 (**A**, `direct_child`).
2. Mãe + item **RAMO** só em L9 com `001` (outra classificação) → sugere `002` em L9 (**B**, `radical_deep`).
2b. Mãe + detalhe em L8 (`01`) e L9 (`001`) → sugere `02` em L8 (**C**, `radical_deep`; primeiro nível com detalhe).
3. Cenário **(H)** com `5` e `6` só incompatíveis em **FILHOS** L6 → sugere `5`.
4. Sem **RAMO** nem **FILHOS** → `…1…` em L6 (**F**).
5. `OCUPADO_VIGENTE(L) = {1..9}` sem buraco → **(E1)**.
6. Mãe no último nível → **(E2)**.
7. `receita_cod` já preenchido + mesma mãe → não sugere automaticamente (**G1**).
8. `receita_cod` preenchido + troca de mãe **pelo usuário** → endpoint antes do modal → **Cancelar** reverte mãe e nomenclatura; **Manter Atual** mantém nova mãe e código; **Atualizar** recalcula código e campos derivados (**G5**).
8b. Endpoint retorna erro (**E1**/**E2**/**E3**) antes do modal → reverte mãe anterior + erro inline; modal **não** abre (**G5**).
9. Lookup de hierarquia altera mãe com código preenchido → **sem** `confirm` nem sugestão (**G6**).
10. Paridade servidor + JS (integração).
11. Payload de sucesso deriva `classificacao.pk` de `derived_level.classificacao_id`, não diretamente de `parent_item_id.classificacao_id`.
12. Nível **`L`** inexistente em qualquer `NivelHierarquico` ativo e vigente compatível com **(V1)** (**ITEMCF-30**) → erro `level_not_resolvable` (**E3**).
13. Existe `NivelHierarquico` para o nível **`L`** apenas em classificação distinta da mãe (mesma vigência) → sugestão devolve esse nível, `classificacao` do payload reflete essa outra classificação, e `notices` inclui aviso quando há mais de uma versão compatível.

---

## 11. Decisões em aberto (requerem confirmação do produto) (**ITEMCF-110**–**ITEMCF-112**)

Registradas de forma explícita; o restante do documento já adota o comportamento **mais aderente** ao repositório.

### **ITEMCF-110** DD1 — Reutilizar `receita_cod` com registro inativo ou só vigência incompatível

**Comportamento adotado na v1:** a sugestão **pode** devolver um código que **já existe** na BD para outra vigência ou com vigência incompatível com **(V1)** (**ITEMCF-30**) (caso **(H)**). A **unicidade** na gravação segue as regras bitemporais / validação de domínio já existentes.

**Pergunta ao produto:** ao gravar, deve o sistema **sempre** permitir nova linha com o mesmo `receita_cod` e vigência disjunta, ou deve bloquear se existir **qualquer** registro ativo com aquele código na classificação?

### **ITEMCF-111** DD2 — Alerta «código já existente»

**Comportamento adotado:** após sugestão, se já existir registro **ativo** com o mesmo `receita_cod`, vigência **(T7)** (**ITEMCF-17**) com **(V1)** (**ITEMCF-30**), mostrar aviso com link — **sem** exigir mesma classificação (coerente com **RAMO**).

**Pergunta ao produto:** o aviso deve oferecer botão «ir para o próximo dígito» que **reexecuta** este algoritmo excluindo o código encontrado?

### **ITEMCF-112** DD3 — Máscara entre classificações no mesmo radical

**Comportamento adotado (v1):** segmentar **RAMO** com a máscara da mãe. Se duas classificações tiverem estruturas incompatíveis com o mesmo prefixo numérico, o comportamento fica indefinido até regra explícita.

---

## 12. Atalho desde change (v2) (**ITEMCF-120**–**ITEMCF-135**)

Esta secção define o atalho na tela de **edição/visualização** (`change`) de `ItemClassificacao` que abre a **add** com o registo atual como **item mãe** e dispara o mesmo protocolo de sugestão de código (**G1**, endpoint `suggest-child-code-by-parent/`, `applyChildCodeSuggestPayload` no cliente). **Não** duplica o algoritmo de código; apenas navega e inicializa o formulário de criação.

**Implementação:** `apps/core/classification_item_child_from_change.py`, `ItemClassificacaoAdmin.get_changeform_initial_data` / `render_change_form`, bloco `object-tools` e JavaScript em `apps/core/templates/admin/core/change_form.html`.

**Specs relacionadas:** [`spec_itemClassificacao_regras_hierarquia.md`](spec_itemClassificacao_regras_hierarquia.md) (mãe `matriz = true`); [`spec_itemClassificacao_formulario.md`](spec_itemClassificacao_formulario.md) (`_changelist_filters` na URL de retorno).

### Escopo (v2)

- Botão **«+ Criar Código Filho»** na **change** de `ItemClassificacao` (não popup).
- Modal de **confirmação** antes de navegar para a add (registo **activo** e **matriz**).
- Modal de **bloqueio** (somente informativo) quando o registo atual é **Detalhe** (`matriz = false`).
- URL da add com `parent_item_id=<pk>` e `from_change_parent=1`.
- Pré-preenchimento na add: mãe, vigência **(V3′)** (**ITEMCF-34**), display semântico da mãe, sugestão **(G1)** com `force`.

### Fora de escopo (v2)

- Sugestão de código **na própria change** (sem navegar para a add).
- Alterar `matriz` automaticamente; o usuário deve editar o registo atual.
- **(G5)** na entrada pelo atalho (ver abaixo).

### Posição do botão (UI)

- Barra **`object-tools`** do Django Admin, **à esquerda** do botão **«Histórico»** (topo direito da change), classe `core-create-child-code-link`, texto **`+ Criar Código Filho`**.
- **Aparência:** fundo verde (`#2e7d32`), texto e símbolo «+» brancos, **sempre** visíveis (estado normal — não apenas `:hover`). Hover/focus ligeiramente mais escuro (`#1b5e20`). CSS com especificidade sobre o tema do admin (`ul.object-tools a.core-create-child-code-link`).
- Não usar a `submit-row` inferior (reservada a Bloquear / Excluir / Salvar).

### Estados do botão

| Estado do registo atual                                                        | Botão                                    | Ao clicar                                            |
| ------------------------------------------------------------------------------ | ---------------------------------------- | ---------------------------------------------------- |
| **Activo** (`data_registro_fim` = sentinela) + **Matriz** + pode sugerir filho | Activado (verde)                         | Modal confirmação → add                              |
| **Activo** + **Detalhe**                                                       | Activado (verde)                         | Modal **bloqueio** — só «Entendi»; **sem** navegação |
| **Inactivo**                                                                   | Desactivado (`aria-disabled`, opacidade) | Nada                                                 |
| Último nível hierárquico / impossível sugerir (**E2** e afins)                 | Desactivado + `title` explicativo        | Nada                                                 |
| Sem permissão `add` em `ItemClassificacao`                                     | Oculto                                   | —                                                    |

A verificação de «pode sugerir filho» no servidor reutiliza `suggest_child_code_for_parent` (pré-visualização) ou critério equivalente (**último nível** da máscara).

### Modal de bloqueio — Detalhe

Quando `matriz = false` e o usuário clica no botão:

1. Exibir modal (família `showCoreAttentionModal`, ícone ⚠️, título «Atenção!»).
2. Corpo (sentido obrigatório): para registar um **item filho** a partir deste código, o registo atual deve estar como **Matriz**; altere «Matriz / Detalhe» neste registo antes de criar um código filho.
3. Um botão **«Entendi»** (fecha o modal).
4. **Proibido** navegar para a add.

### Modal de confirmação — Matriz activa

1. Se houver **alterações não guardadas feitas pelo usuário** na change, o cliente **deve** aplicar o aviso de `setupUnsavedChangesWarning` (`window.__coreConfirmUnsavedIfDirty`) **antes** do modal de confirmação. **Um único canal** no clique do botão (handler dedicado); o botão **não** está em `guardedLinks` (evita `confirm` duplicado).
2. Modal (título **«Criar Código Filho»** — «Código» com C maiúsculo):
   - «Você será encaminhado para a tela de criação de novo Item (Código) de Classificação.»
   - «O código atual (**&lt;código canónico&gt;**) será o assumido como mãe do novo código a ser criado.» — **&lt;código canónico&gt;** = valor **dinâmico** do registo atual (máscara de apresentação): preferir o campo `receita_cod` visível no formulário; fallback `data-receita-cod-display` no botão (servidor: `format_receita_cod_by_vigencia` do objeto da change).
   - «Deseja continuar?»
3. Botões: **Cancelar** | **Continuar**.
4. **Continuar** → `window.location` para a URL da add (secção URL).

### Alterações não guardadas (`isDirty`) na change

O mecanismo global `setupUnsavedChangesWarning` mantém-se para Cancelar / Bloquear / Excluir. Para **«Criar Código Filho»**, reutiliza-se `__coreConfirmUnsavedIfDirty` no handler do botão.

**Falso positivo a evitar:** na carga da change de `ItemClassificacao`, `runCodeDigitValidation('init')` (máscara de `receita_cod`), polling de FKs e init na add podem alterar o DOM **sem** acção do usuário e marcar `isDirty` incorrectamente.

**Mecânica (cliente):**

1. Após `runCodeDigitValidation('init')` (e `syncHierarchyFromCode('init')` na add, quando aplicável), chamar `window.__coreRebaselineFormDirtySnapshot()` — redefine `initialState` e `originalState` de cada campo visível para o valor **atual** pós-init.
2. Repetir o rebaseline com `setTimeout` (~750 ms) para absorver polling de raw-id (350 ms) e `refreshConfirmedParentSnapshot` (~500 ms).
3. Durante escrita programática pontual em `receita_cod` (formatação de máscara), usar `window.__coreSuppressDirtyRecompute` para não disparar `recomputeDirty` intermédio.
4. Após `initChildCodeFromChangeParent` na add, novo rebaseline.

Com isso, abrir a change **sem editar** e clicar em «Criar Código Filho» **não** exibe o `confirm` de alterações não guardadas; editar um campo e clicar **sim** exibe o aviso antes do modal de navegação.

### URL da add

```
/admin/core/itemclassificacao/add/?parent_item_id=<pk>&from_change_parent=1
```

- Preservar `_changelist_filters` da request atual quando existir (retorno coerente na add — `spec_itemClassificacao_formulario.md`).
- `from_change_parent=1` é parâmetro **interno** de fluxo (não é filtro de negócio).

### **ITEMCF-34** **(V3′)** Vigência do filho na entrada pelo atalho

Ao abrir a add via atalho, `get_changeform_initial_data` **deve** preencher `data_vigencia_inicio` e `data_vigencia_fim` do filho a partir da vigência do **item mãe** (registo da change), com comparações em **data civil** (fuso local do Django para datetimes aware).

Constante de implementação: `vigencia_filho_from_item_mae(parent)` em `classification_item_child_from_change.py`.

| Regra        | Condição (mãe)                                                                    | `data_vigencia_inicio` do filho | `data_vigencia_fim` do filho            |
| ------------ | --------------------------------------------------------------------------------- | ------------------------------- | --------------------------------------- |
| **Fim**      | sempre                                                                            | —                               | **sempre** = `data_vigencia_fim` da mãe |
| **Início A** | `inicio_mae > 01/01/<ano civil corrente>`                                         | `inicio_mae`                    | (regra Fim)                             |
| **Início B** | `fim_mae <= 01/01/<ano civil corrente>` (inclui `fim_mae = 01/01/<ano corrente>`) | `inicio_mae`                    | (regra Fim)                             |
| **Início C** | `inicio_mae <= 01/01/<ano corrente>` **e** `fim_mae > 01/01/<ano corrente>`       | `01/01/<ano corrente>`          | (regra Fim)                             |

Ordem de avaliação no código: **A** → **B** → **C** (mutuamente exclusivos na prática).

O cliente na add **não deve** sobrescrever essas datas no `applyChildCodeSuggestPayload` quando os campos já estiverem preenchidos (mesmo critério de «só preencher vigência se vazio» em **(V3)** (**ITEMCF-33**)). O endpoint `suggest-child-code-by-parent/` **deve** receber na query as datas já presentes no formulário (**V1** na sugestão).

### Inicialização na add (após redirect)

Ordem recomendada no cliente (`initChildCodeFromChangeParent`):

1. Ler `parent_item_id` já no hidden (initial do servidor).
2. `enrichParentSnapshotFromSemantic` + `applyParentSnapshotToDom` (paridade com a lupa).
3. `suggestChildCodeFromParent('from_change_parent', { force: true })` — **(G1)** com `receita_cod` vazio.
4. Durante o bloco, `__suppressChildCodeSuggestOnParentChange = true` para não disparar **(G5)**.

### Relação com **(G5)** (**ITEMCF-135**)

**(G5) não se aplica** na chegada pelo atalho: na add, `receita_cod` inicia vazio e a mãe é escrita programaticamente sem troca manual.

**(G5) aplica-se apenas** se, **depois** na add, o usuário **trocar** o item mãe (lupa) **com** `receita_cod` já preenchido — fluxo já especificado em **(G5)**.

### Casos de teste (v2)

1. Change activa + matriz → Confirmar → add com mãe, vigência **(V3′)** (**ITEMCF-34**) e código sugerido.
2. Change Detalhe → modal bloqueio, permanece na change.
3. Change inactiva → botão desactivado.
4. Mãe com `fim_mae < 01/01/ano` → `inicio_filho = inicio_mae`; `fim_filho = fim_mae`.
5. Mãe com `fim_mae = 01/01/ano` → `inicio_filho = inicio_mae` (regra B).
6. Mãe com vigência sobreposta ao ano corrente → `inicio_filho = 01/01/ano`.
7. `inicio_mae` no futuro → `inicio_filho = inicio_mae`.
8. Change com alterações não guardadas → aviso antes do modal de confirmação.
9. Change **sem** editar, após carga completa (rebaseline) → **sem** aviso de alterações não guardadas ao clicar no botão; botão verde no estado normal (não só hover).

---
