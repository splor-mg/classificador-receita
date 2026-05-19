# Especificação: lookups JSON de código no admin (`ItemClassificacao`)

## Objetivo e escopo

Documentar o contrato HTTP/JSON dos endpoints usados pelo formulário de **adicionar/alterar** `ItemClassificacao` no Django Admin para:

1. Resolver um **item** pelo **código exato** e janela de vigência (lupa de `parent_item_id`).
2. Derivar **nível hierárquico** a partir do **código canônico** e sugerir **item mãe matriz** coerente com a máscara e a vigência.

A lógica de negócio e ORM vive em `apps/core/item_classificacao_code_lookup.py`. As views em `ItemClassificacaoAdmin` apenas delegam e envolvem o dicionário em `JsonResponse`.

Relacionado: regras de domínio de `parent_item_id` em `_dev/spec_itemClassificacao_regras_hierarquia.md`; aviso de salto de nível e intermediários em `_dev/spec_itemClassificacao_validar_hierarquia.md`.

---

## 1) `lookup-parent-by-code`

- **Rota:** `GET …/admin/core/itemclassificacao/lookup-parent-by-code/`
- **Nome URL:** `admin:core_itemclassificacao_lookup_parent_by_code`
- **Variável no template:** `item_classificacao_parent_lookup_url` (definida em `render_change_form`).

### Parâmetros GET

| Parâmetro | Obrigatório | Descrição |
|-----------|-------------|-----------|
| `code` | Sim | Código Receita **sem pontos** (espaços são ignorados; `.` removidos). |
| `vigencia_inicio` | Sim | Início da vigência do **filho** (formato enviado pelo front; comparado como string nas queries de filtro de data). |
| `vigencia_fim` | Sim | Fim da vigência do filho (idem). |

Se faltar qualquer um dos três, a resposta é o objeto “vazio” abaixo (sem erro explícito).

### Resposta JSON (sempre 200 com este shape)

| Campo | Tipo | Significado |
|-------|------|-------------|
| `pk` | string | PK do `ItemClassificacao` encontrado, ou `""`. |
| `semantic_value` | string | `receita_cod` formatado com `format_receita_cod_by_vigencia` para exibição, ou `""`. |
| `display_label` | string | `"{cod} - {nome}"` ou `""`. |
| `link_url` | string | URL do change do admin do item, ou `""`. |

### Critério de seleção (quando há `code` + vigência)

- `receita_cod` igual ao código normalizado (sem `.`).
- Registo ativo: `data_registro_fim` igual a `TRANSACTION_TIME_SENTINEL` (aware se o sentinela for naive).
- Sobreposição de vigência: `data_vigencia_inicio <= vigencia_inicio` e `data_vigencia_fim >= vigencia_fim`.
- Se vários: `order_by("pk").first()` (primeiro PK).

---

## 2) `lookup-hierarchy-by-code`

- **Rota:** `GET …/admin/core/itemclassificacao/lookup-hierarchy-by-code/`
- **Nome URL:** `admin:core_itemclassificacao_lookup_hierarchy_by_code`
- **Variável no template:** `item_classificacao_hierarchy_lookup_url`.

### Parâmetros GET

| Parâmetro | Obrigatório | Descrição |
|-----------|-------------|-----------|
| `code` | Sim | Código canônico **só com dígitos** (`.` removidos). |
| `vigencia_inicio` | Sim | Data (`YYYY-MM-DD` ou `DD/MM/YYYY`). |
| `vigencia_fim` | Sim | Data (mesmos formatos). |
| `classificacao_pk` | Não | PK da `Classificacao` escolhida no formulário. Ausente = sem restrição de classificação nas queries de nível/mãe (salvo onde o código reintroduz busca noutra classificação). |

### Erros (`ok: false`)

Resposta típica: `{"ok": false, "message": "<texto>"}`.

| Situação | Mensagem (resumo) |
|----------|-------------------|
| `code` vazio | Informe o código canônico. |
| Vigência em falta | Informe o período de vigência… |
| `vigencia_fim < vigencia_inicio` | Período inválido… |
| `classificacao_pk` inválido (não inteiro ou sem registo) | Classificação inválida. |
| Código com caracteres não numéricos | …apenas dígitos. |
| Sem máscara de níveis para o contexto | Não foi possível determinar a estrutura… |
| Código mais longo que o total de dígitos e cauda não é só zeros | Código excede o limite… |
| Sem segmento detalhado ≠ zero | …não há nível detalhado diferente de zero. |
| Detalhamento após o nível derivado | …há detalhamento após o nível derivado… |

### Sucesso (`ok: true`)

```json
{
  "ok": true,
  "normalized_code": "<string>",
  "effective_vigencia": {
    "inicio": "<ISO date>",
    "fim": "<ISO date>",
    "overridden": <bool>
  },
  "derived_level": { ... },
  "parent": { ... }
}
```

- **`normalized_code`:** comprimento ajustado à soma da máscara (`ljust` com `0` ou truncagem se a cauda extra for só zeros).
- **`effective_vigencia`:** resultado de `effective_vigencia_for_item_hierarchy_lookup` (datas efectivas para máscara e queries; `overridden` indica se a janela foi alinhada ao universo da classificação).

#### `derived_level`

| Campo | Tipo | Significado |
|-------|------|-------------|
| `number` | int | `nivel_numero` inferido (1-based). |
| `pk` | string | PK do `NivelHierarquico` escolhido, ou `""`. |
| `display_label` | string | Rótulo `"{nivel_id} - {nivel_nome}"` ou vazio. |
| `status` | object | `severity`: `ok` \| `warning` \| `error`; `message`; `alternative` (opcional). |
| `notices` | array de strings | Avisos não bloqueantes do nível (ex.: múltiplas versões ativas compatíveis do nível, com seleção da mais recente). Ver seção **«Avisos (`notices`) — paridade item mãe / nível hierárquico»** abaixo. |

**`alternative` (nível):** quando existe nível noutra classificação mas não na seleccionada, inclui `classificacao` (`pk`, `classificacao_id`, `display_label`, `link_url`) e `message` explicativa.

#### `parent`

| Campo | Tipo | Significado |
|-------|------|-------------|
| `required` | bool | `true` se `derived_level.number > 1`. |
| `found` | bool | Matriz mãe resolvida (incluindo fallbacks documentados no código). |
| `pk`, `code`, `name`, `display_label`, `link_url` | strings | Dados do item mãe ou vazios. |
| `status` | object | Igual convenção `severity` / `message` / `alternative`; em erro “detalhe em vez de matriz” pode existir `html` (fragmento com link) além de `message` em texto simples. |
| `notices` | array de strings | Avisos não bloqueantes do item mãe (ex.: múltiplas versões ativas compatíveis, fallback por último nível detalhado, alternativa noutra classificação). Ver seção **«Avisos (`notices`) — paridade item mãe / nível hierárquico»** abaixo. |

**Âmbito de classificação:** quando `classificacao_pk` identifica um registo, as queries de nível e de mãe **primário** filtram pela identidade semântica da classificação (`classificacao_ref` / `classificacao_id` / FK), tal como em `classificacao_identity_filters` no módulo.

**Máscara:** `digit_mask_for_classificacao_vigencia(class_pk, effective_inicio, effective_fim)`; se vazia, fallback `resolve_receita_cod_mask_context(None, input_length=len(code), on_date=hoje)`.

**item mãe:** código derivado por zeros canônicos a partir do nível derivado; candidatos `matriz=True`, `nivel_numero = derived − 1`, vigência e registo activos. O ficheiro Python documenta por comentário a ordem de tentativas (matriz na classificação seleccionada, fallback por último nível detalhado, busca noutra classificação, diagnóstico “só existe como detalhe”).

**Consumo no cliente (`change_form.html`):**

- **Alteração do código** (`code_blur`, `classificacao_change`, `init`): se `parent.found`, o cliente **substitui** `parent_item_id` pelo PK devolvido via `setParentItemIdProgrammatically` (flag `__suppressChildCodeSuggestOnParentChange`), mesmo que o campo já estivesse preenchido (ex.: autocomplete anterior). Essa escrita **não** dispara sugestão de código filho nem `confirm` de troca de mãe — ver **(G6)** em `_dev/spec_itemClassificacao_criar_filho.md`. Se o lookup não encontrar mãe, aplica erro/limpeza conforme severidade (sem preservar mãe “manual”), também via escrita programática quando limpa o campo.
- **Salvar** (`submit`): regras em `_dev/spec_itemClassificacao_validar_hierarquia.md` — pode preservar mãe já preenchida quando o lookup falha ou devolve PK diferente.

---

## Avisos (`notices`) — paridade item mãe / nível hierárquico

Sempre que o resolver bitemporal arbitra entre **N ≥ 2** candidatos ativos e compatíveis com a vigência informada para uma FK temporal da hierarquia (`item mãe` ou `nível hierárquico`), o lookup **deve** sinalizar a arbitragem ao usuário por meio de um aviso textual em `notices`, no respectivo bloco do payload (`parent` ou `derived_level`). O frontend **deve** renderizar esses avisos no **mesmo padrão visual** nos dois campos (`<ul class="messagelist hierarchy-autofill-warning">` com `<li class="warning">`), em paridade com a renderização do `alternative` quando coexistirem na mesma `<ul>`.

### Regra de emissão (servidor)

- **N1.** A contagem **N** é a quantidade de candidatos ativos e compatíveis com a vigência informada (mesmo critério da consulta principal), obtida via `qs.count()` antes de `qs.first()`. **N** existe apenas como variável local no Python; **não** é exposta como campo separado no payload — só aparece interpolada no texto do aviso.
- **N2.** Quando **N ≥ 2** e há registro escolhido, anexar a frase normativa à lista `notices` do respectivo bloco. Quando **N ≤ 1**, **não** emitir aviso.
- **N3.** Os ramos cobertos são:
  - **Item mãe — primário:** busca por matriz canônica na classificação selecionada (ou sem escopo, se nenhuma foi fornecida).
  - **Item mãe — fallback por último nível detalhado:** quando o item mãe pertence a nível anterior ao imediatamente superior.
  - **Item mãe — alternativa noutra classificação:** quando não há matriz na classificação selecionada, mas existe em outra.
  - **Nível hierárquico — primário:** busca por `NivelHierarquico` ativo do `nivel_numero` derivado, no escopo da classificação selecionada (ou sem escopo).
  - **Nível hierárquico — alternativa noutra classificação:** quando não há nível na classificação selecionada, mas existe em outra.

### Textos normativos (pt-BR)

| Cenário | Texto |
|---------|-------|
| Item mãe — primário | `Foram encontradas {N} versões ativas compatíveis do item mãe; foi selecionada a versão mais recente.` |
| Item mãe — fallback | `Foram encontradas {N} versões ativas compatíveis do item mãe no fallback; foi selecionada a versão mais recente.` |
| Item mãe — alternativa noutra classificação | `Foram encontradas {N} versões ativas compatíveis do item mãe noutra classificação; foi selecionada a versão mais recente.` |
| Nível hierárquico — primário | `Foram encontradas {N} versões ativas compatíveis do nível {K}; foi selecionada a versão mais recente.` |
| Nível hierárquico — alternativa noutra classificação | `Foram encontradas {N} versões ativas compatíveis do nível {K} noutra classificação; foi selecionada a versão mais recente.` |

Notas de redação:

- **R1.** O padrão único é **«versões ativas compatíveis do {recurso}»** — `{recurso}` = «item mãe» ou «nível {K}» (com `{K}` igual a `derived_level.number`). Substitui a redação legada baseada em «matrizes ativas compatíveis».
- **R2.** As frases terminam sempre com **«; foi selecionada a versão mais recente.»**, em sinal explícito da arbitragem por `-data_vigencia_inicio`, `-data_registro_inicio`, `-pk`.
- **R3.** As frases **não** referenciam ano civil, sentinela nem campos internos: são voltadas para o usuário do Admin.

### Regra de consumo (cliente — `change_form.html`)

- **C1.** Para **cada** dos campos `parent_item_id` e `nivel_id`, ao receber o payload do lookup, montar uma única `<ul class="messagelist hierarchy-autofill-warning">` na respectiva `.form-row` quando houver **`alternative`** (status `warning` com bloco `alternative`) **e/ou** itens em `notices`. Mesma classe CSS e mesmo `marginTop` nos dois campos.
- **C2.** Ordem dentro da `<ul>`: primeiro o `<li>` do `alternative` (se houver), depois um `<li>` por nota de `notices`, na ordem fornecida pelo servidor.
- **C3.** Antes de inserir a nova `<ul>`, executar `clearHierarchyMessages(row)` para não acumular avisos de submits anteriores.
- **C4.** Quando o status do bloco for `error`, manter o tratamento atual (validade customizada + `<ul class="errorlist hierarchy-autofill-error">`); `notices` não são exibidos em conjunto com erros (a UX foca no bloqueio).

---

## Manutenção

- Alterações de contrato JSON devem manter este ficheiro alinhado ao módulo `item_classificacao_code_lookup.py` e ao JavaScript que consome estes endpoints em `change_form` / `classification_naming.js` (nomes de chaves).
- A regra de paridade «item mãe / nível hierárquico» (seção acima) **deve** ser preservada em cada nova FK temporal da hierarquia que vier a ser exposta pelo endpoint: criar variáveis locais de contagem (sem expor no payload), emitir `notices` no bloco correspondente, espelhar a renderização no cliente.

### Testes recomendados

- **T-notices.1.** Duas linhas bitemporais ativas e vigentes para o mesmo item mãe (`receita_cod`, `matriz=True`, `nivel_numero = derived − 1`): payload retorna `parent.notices` com a frase do **item mãe — primário**; o cliente renderiza a `<ul>` amarela no campo `parent_item_id`.
- **T-notices.2.** Duas linhas bitemporais ativas e vigentes para o mesmo `nivel_numero` derivado, na classificação selecionada: payload retorna `derived_level.notices` com a frase do **nível hierárquico — primário**; o cliente renderiza a `<ul>` amarela no campo `nivel_id`.
- **T-notices.3.** Cenário T-notices.2 sem nível na classificação selecionada, com **duas** linhas em outra classificação: payload retorna `derived_level.notices` com a frase do **nível hierárquico — alternativa noutra classificação** e `derived_level.status.severity = "warning"` com o `alternative`; o cliente renderiza ambos na mesma `<ul>`.
- **T-notices.4.** Apenas **uma** versão ativa e compatível (caso comum): `notices` permanece vazio em `parent` e `derived_level`; nenhuma `<ul>` amarela aparece nas duas linhas.
