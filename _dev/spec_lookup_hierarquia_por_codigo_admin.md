# Especificação: lookups JSON de código no admin (`ItemClassificacao`)

## Objetivo e escopo

Documentar o contrato HTTP/JSON dos endpoints usados pelo formulário de **adicionar/alterar** `ItemClassificacao` no Django Admin para:

1. Resolver um **item** pelo **código exato** e janela de vigência (lupa de `parent_item_id`).
2. Derivar **nível hierárquico** a partir do **código canónico** e sugerir **item mãe matriz** coerente com a máscara e a vigência.

A lógica de negócio e ORM vive em `apps/core/item_classificacao_code_lookup.py`. As views em `ItemClassificacaoAdmin` apenas delegam e envolvem o dicionário em `JsonResponse`.

Relacionado: regras de domínio de `parent_item_id` em `_dev/spec_parent_item_id.md`; aviso de salto de nível e intermediários em `_dev/spec_validar_item_pai.md`.

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
| `code` | Sim | Código canónico **só com dígitos** (`.` removidos). |
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

**`alternative` (nível):** quando existe nível noutra classificação mas não na seleccionada, inclui `classificacao` (`pk`, `classificacao_id`, `display_label`, `link_url`) e `message` explicativa.

#### `parent`

| Campo | Tipo | Significado |
|-------|------|-------------|
| `required` | bool | `true` se `derived_level.number > 1`. |
| `found` | bool | Matriz mãe resolvida (incluindo fallbacks documentados no código). |
| `pk`, `code`, `name`, `display_label`, `link_url` | strings | Dados do item mãe ou vazios. |
| `status` | object | Igual convenção `severity` / `message` / `alternative`; em erro “detalhe em vez de matriz” pode existir `html` (fragmento com link) além de `message` em texto simples. |
| `notices` | array de strings | Avisos não bloqueantes (ex.: múltiplas matrizes, fallback de nível). |

**Âmbito de classificação:** quando `classificacao_pk` identifica um registo, as queries de nível e de mãe **primário** filtram pela identidade semântica da classificação (`classificacao_ref` / `classificacao_id` / FK), tal como em `classificacao_identity_filters` no módulo.

**Máscara:** `digit_mask_for_classificacao_vigencia(class_pk, effective_inicio, effective_fim)`; se vazia, fallback `resolve_receita_cod_mask_context(None, input_length=len(code), on_date=hoje)`.

**item mãe:** código derivado por zeros canónicos a partir do nível derivado; candidatos `matriz=True`, `nivel_numero = derived − 1`, vigência e registo activos. O ficheiro Python documenta por comentário a ordem de tentativas (matriz na classificação seleccionada, fallback por último nível detalhado, busca noutra classificação, diagnóstico “só existe como detalhe”).

---

## Manutenção

- Alterações de contrato JSON devem manter este ficheiro alinhado ao módulo `item_classificacao_code_lookup.py` e ao JavaScript que consome estes endpoints em `change_form` / `classification_naming.js` (nomes de chaves).
