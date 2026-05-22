# Item de classificação — edição de `receita_cod` na tela de alteração (change)

Esta especificação define o comportamento quando o usuário **altera** o campo **Código Canônico da Natureza de Receita** (`receita_cod`) na view **change** de `ItemClassificacao` no Django Admin.

**Regra de negócio:** uma vez criado, o código canônico **não pode ser substituído na mesma linha de registro** (mesmo PK / mesma entidade bitemporal). Na change, alterar o código no input serve para **navegar** (outro registro ou tela de inclusão) ou deve ser **desfeito**; **não** para gravar outro código via **Salvar** ou via **Editar vigência** (confirmação bitemporal).

**Dois eixos de comportamento:**

| Eixo | Gatilho | Efeito |
|------|---------|--------|
| **Navegação** **(G-cod.blur)** | `blur` em `receita_cod` com **COD-2 ≠ COD-1** | Modais **M2–M4**: redirecionar ou restaurar **COD-1**. |
| **Persistência** **(G-cod.save)** | **Salvar** ou lápis **Editar vigência** com **COD-2 ≠ COD-1** | **Não** abrir `bitemporal_confirm.html`; modal **M-cod-block**. |

**Implementação de referência (alvo):** `apps/core/templates/admin/core/change_form.html` (`showCoreAttentionModal`, blur, validação de dígitos); `apps/core/admin_handlers.py` (`BitemporalChangeHandler`); novo endpoint JSON em `ItemClassificacaoAdmin` (família `lookup-*-by-code` / `resolve-code-navigation` em `apps/core/item_classificacao_code_lookup.py`).

**Specs relacionadas (não substituídas, salvo onde indicado):**

| Spec | Relação |
|------|---------|
| `_dev/spec_itemClassificacao_formulario.md` | Largura `37ch`; **(R-clear)** só na **add**; **(R-revert)** na **change** (esta spec). |
| `_dev/spec_itemClassificacao_mascara_apresentacao.md` | **B1** — normalização e máscara no blur. |
| `_dev/spec_itemClassificacao_foreignKeys_lookup.md` | Lookups na **add**; na **change** com código alterado, **não** reconciliar hierarquia no blur (**G-cod.blur**). |
| `_dev/spec_itemClassificacao_criar_filho.md` | **(T6)**, **(T7)**; aviso de alterações não guardadas na navegação (**v2**). |
| `_dev/spec_itemClassificacao_navegacao.md` | Botões **(G-nav.\*)** na change; distinto de **(G-cod.blur)**. |
| `_dev/spec_itemClassificacao_criar_nome.md` | Protocolos da add após redirecionamento (**C4**). |
| `_dev/toDo.md` | Alerta «código já existente» na add — fora desta spec. |

---

## Escopo

| Inclui | Não inclui |
|--------|------------|
| View **change** de `ItemClassificacao` | Fluxos na view **add** (sugestão de filho, **R-clear**, lookups normais) |
| **(G-cod.blur)** — blur, cenários **C1–C4**, modais **M2–M4** | `readonly` permanente em `receita_cod` |
| **(G-cod.save)** — bloqueio de **Salvar** e **Editar vigência** | Persistir **COD-2** no mesmo registro (domínio + UI) |
| Borracha na change — **(R-revert)** | «Limpar formulário inteiro» da add — **(R-clear)** |
| Endpoint `resolve-code-navigation` (recomendado) | Detalhe interno de estratégias bitemporais além do bloqueio |

---

## Notação

| Símbolo | Significado |
|---------|-------------|
| **COD-1** | Código canônico (somente dígitos `0-9`) do registro em edição **ao carregar** a change; snapshot até sair da página ou **(R-revert)**. |
| **COD-2** | Código canônico normalizado do input no momento da avaliação (**B1**: sem pontuação de máscara). |
| **(T-cod.0) Código alterado na change** | **COD-2** não vazio **e** **COD-2 ≠ COD-1**. |
| **V1** | Vigência do registro aberto: `data_vigencia_inicio` e `data_vigencia_fim` do `instance` na change. |
| **`<código>`** | `receita_cod` **formatado** (máscara) para exibição em modais. |

**Normalização (obrigatória em todos os eixos):** remover `.` e espaços; comparar apenas dígitos. Não usar somente `form.has_changed()` em `receita_cod` — máscara e `padEnd` podem marcar alteração sem mudança semântica; a autoridade é **COD-1** vs **COD-2**.

---

## Terminologia (alinhada ao projeto)

- **(T6) Registro ativo:** `data_registro_fim` = `TRANSACTION_TIME_SENTINEL` (`transaction_time_sentinel_for_query()`).
- **(T7) Sobreposição de vigência:** intervalos **A** e **B** (datas inclusivas): `início_A ≤ fim_B` e `fim_A ≥ início_B`.
- **(T-cod.1) Código existente:** ao menos um registro **(T6)** com `receita_cod` = **COD-2** (sem exigir **(T7)** com **V1**).
- **(T-cod.2) Vigência atual (vs. COD-1):** **(T-cod.1)** e existe registro **(T6)** de **COD-2** com **(T7)** em relação a **V1**.
- **(T-cod.3) Vigência diversa (vs. COD-1):** **(T-cod.1)** e **nenhum** registro **(T6)** de **COD-2** tem **(T7)** com **V1**.
- **(T-cod.4) Máscara compatível:** `len(COD-2)` igual à soma da máscara do item em edição **ou** à soma de alguma máscara de `estrutura_codigo` em nível **(T6)** (critério de `fetchReceitaCodDigitLimit` / `runCodeDigitValidation`).

**(T-cod.2)** e **(T-cod.3)** são excludentes e exaustivos para um **COD-2** existente.

---

## Eixo navegação — blur **(G-cod.blur)**

### Ordem do pipeline

| Etapa | Condição | Ação |
|-------|----------|------|
| 0 | View **add** | **Encerrar** — esta spec não se aplica. |
| 0 | View **change** | Prosseguir. |
| 1 | `blur` em `receita_cod` | Início do pipeline. |
| 2 | **B1** + `runCodeDigitValidation` | Se inválido → **C1**; **não** abrir **M2–M4**. |
| 3 | **não** **(T-cod.0)** | **Encerrar** — sem modal de navegação. |
| 4 | **(T-cod.0)** e dígitos válidos | Classificar **C2–C4** e abrir modal correspondente. |

### `syncHierarchyFromCode`

Na **change**, após **(T-cod.0)** no blur, o cliente **não deve** chamar `syncHierarchyFromCode('code_blur')` nem alterar `parent_item_id` / `nivel_id` do registro aberto. Na **add**, vale `spec_itemClassificacao_foreignKeys_lookup.md`.

---

## Eixo persistência — Salvar e Editar vigência **(G-cod.save)**

### Contexto

No admin, alterações na change passam por `BitemporalChangeHandler` (`admin_mixins.BitemporalAdminMixin` → `admin_handlers.py`): POST válido com `form.has_changed()` **ou** flag `_edit_vigencia` (lápis ✎ em `admin_bitemporal_date_shortcuts.js`) renderiza `admin/core/bitemporal_confirm.html`.

Esse fluxo pressupõe **atualizar a mesma entidade**. Trocar `receita_cod` no formulário viola a regra de negócio e **não deve** chegar à tela de confirmação.

### **(G-cod.save.1) Gatilhos bloqueados**

| Gatilho | Identificação |
|---------|----------------|
| **Salvar** | `submit` do formulário de change com `name="_save"` (botão padrão do admin). |
| **Editar vigência** | `submit` com `name="_edit_vigencia"` e `value="1"` (lápis ao lado de `data_vigencia_inicio` / `data_vigencia_fim`). |

Qualquer outro botão de submit da change que dispare o mesmo POST para `BitemporalChangeHandler` com alterações no formulário **deve** respeitar a mesma regra se incluir `receita_cod` alterado.

### **(G-cod.save.2) Condição de bloqueio**

- Avaliar **(T-cod.0)** sobre **COD-2** obtido do input **no momento do submit** (mesma normalização **B1**).
- Se **(T-cod.0)** for verdadeiro → **bloquear** redirecionamento para `bitemporal_confirm.html`, **independentemente** de outros campos alterados (`receita_nome`, vigência, FKs, etc.).

### **(G-cod.save.3) Ação na UI (cliente)**

1. Interceptar o `submit` do formulário na change **antes** do envio ao servidor.
2. Se **(T-cod.0)** → `preventDefault()`; exibir **M-cod-block**; manter o usuário na change com os dados atuais do formulário.
3. Se **não** **(T-cod.0)** → fluxo atual (POST → confirmação bitemporal quando houver alterações).

**Ordem típica vs. blur:** o usuário pode **Salvar** sem ter disparado blur; o bloqueio **(G-cod.save)** ainda assim se aplica. Se antes houve blur com modal de navegação e **Cancelar**, o campo pode continuar com **COD-2 ≠ COD-1** → **Salvar** exibe **M-cod-block**.

### **(G-cod.save.4) Ação no servidor (obrigatória)**

Em `BitemporalChangeHandler.handle`, **antes** de montar o contexto de `bitemporal_confirm.html`:

- Se `change` e **(T-cod.0)** entre `receita_cod` normalizado do POST e `obj.receita_cod` do `instance` → **não** retornar a template de confirmação.
- Reexibir a change com mensagem equivalente a **M-cod-block** (`message_user` e/ou erro em `receita_cod`), preservando o POST quando possível.

Repetir a verificação na **segunda etapa** (quando `edit_strategy` já veio preenchido), para impedir gravação bitemporal com código divergente.

### **(G-cod.save.5) Após **(R-revert)**

Com **COD-2** restaurado para **COD-1**, **Salvar** e **Editar vigência** voltam ao comportamento bitemporal padrão do projeto.

---

## Borracha na change **(R-revert)**

| Regra | Descrição |
|-------|-----------|
| **(R-revert.1)** | Controle à direita de `receita_cod`, mesmo layout da add (**(R-clear.2)**). |
| **(R-revert.2)** | Restaura **somente** `receita_cod` (valor + máscara) para **COD-1**; sem recarregar a página. |
| **(R-revert.3)** | Ação imediata, **sem** modal. |
| **(R-revert.4)** | `title` / `aria-label`: «Restaurar código original». |
| **(R-revert.5)** | Após restaurar: `clearReceitaCodMessages` no `.form-row` do campo (remove erro **C1**, avisos e warnings inline); `setCustomValidity('')`; `syncItemIdPreview()`; `__coreRebaselineReceitaCodNavigationDirtyState()` para `receita_cod` e `item_id` deixarem de contar como alteração não salva. |

**Implementação:** `restoreReceitaCodOrigem()` em `change_form.html` (também usada ao **Cancelar** modais **M2–M4**).

---

## Classificação no blur (cenários **C1–C4**)

Após **(G-cod.blur)** etapas 2–3, aplicar a **primeira** linha válida:

| ID | Condições | UI |
|----|-----------|-----|
| **C1** | **não** **(T-cod.4)** | Erro inline (`showReceitaCodError`), mesmo texto da add quando o comprimento não casa com a estrutura. |
| **C2** | **(T-cod.4)**; **(T-cod.1)**; **(T-cod.2)** | **M2** |
| **C3** | **(T-cod.4)**; **(T-cod.1)**; **(T-cod.3)** | **M3** |
| **C4** | **(T-cod.4)**; **não** **(T-cod.1)** | **M4** |

### Endpoint `resolve-code-navigation` (recomendado)

`GET …/admin/core/itemclassificacao/resolve-code-navigation/`

| Parâmetro | Obrigatório | Descrição |
|-----------|-------------|-----------|
| `code` | Sim | **COD-2** (dígitos). |
| `vigencia_inicio` | Sim | Início de **V1**. |
| `vigencia_fim` | Sim | Fim de **V1**. |
| `exclude_pk` | Não | PK do registro em edição. |

Resposta sugerida: `{ "ok": true, "scenario": "C2"|"C3"|"C4", "codigo_display": "...", "target": { "view": "change"|"add", "pk": "", "change_url": "", "add_url": "" } }` ou `{ "ok": false, "scenario": "C1", "message": "..." }`.

**Desempate (C2 / C3):** maior `data_vigencia_fim`; empate → maior `data_vigencia_inicio`; empate → maior `pk`.

---

## Modais

### Padrão comum (navegação **M2–M4**)

- `showCoreAttentionModal`, título «Atenção!».
- Botões: **Cancelar** | **Sim**.
- **Cancelar**, **Escape**, overlay: fechar; restaurar `receita_cod` para **COD-1**.
- **Sim**: `location.assign` para URL do endpoint; preservar `_changelist_filters` quando existir.
- **Alterações não guardadas (navegação M2–M4):** após «Sim», chamar `__coreRebaselineReceitaCodNavigationDirtyState()` (rebaseline de `receita_cod` e `item_id` — preview derivado atualizado no blur por `syncItemIdPreview`) e em seguida `__coreConfirmUnsavedIfDirty(go)`. Assim, **somente** a troca de código + `item_id` **não** dispara o segundo `confirm`; se **outros** campos estiverem alterados, o aviso **deve** aparecer.

#### **M2** — vigência atual

```
Atenção!

Deseja ser direcionado para a tela de edição do <código>?
```

#### **M3** — vigência diversa

```
Atenção!

O <código> digitado tem vigência diversa do código atual.

Deseja ser direcionado para a tela de edição do <código>?
```

#### **M4** — código inexistente

```
Atenção!

Não foi encontrado registro para o <código>.

Deseja ser direcionado para a tela de criação de um novo código?
```

| Cenário | «Sim» |
|---------|--------|
| **C2**, **C3** | `change` do PK desempatado. |
| **C4** | `add` com `receita_cod` pré-preenchido; protocolos da add (**B1**, `syncHierarchyFromCode`, **(V3)**, **P-mãe**). |

### **M-cod-block** — bloqueio de persistência **(G-cod.save)**

Modal **informativo** (não oferece redirecionamento nem gravação).

- Botão único: **Entendi** (fecha o modal; **não** submete o formulário).
- **Sem** ação «Sim» para confirmação bitemporal.

**Texto (corpo — três parágrafos ou lista equivalente):**

```
Atenção!

Uma vez criado, o código canônico não pode ser substituído na mesma linha de registro. Não é possível gravar outro código neste item por meio de Salvar ou Editar vigência.

Para abrir outro código já cadastrado: confirme a alteração ao sair do campo Código Canônico (TAB ou clique fora) e escolha a opção no aviso, ou localize o item na lista do admin.

Para cadastrar um código novo: use Adicionar Item de Classificação.

Para desfazer o que foi digitado nesta tela: use o ícone Restaurar código original ao lado do campo.
```

**Implementação:** `showCoreAttentionModal` com um botão (ex.: `okLabel: 'Entendi'`, sem `cancelLabel` ou cancelar oculto); ou variante dedicada com a mesma família visual.

---

## Testes manuais recomendados (change)

### Navegação **(G-cod.blur)**

1. Blur sem alterar código → sem modal.
2. Blur com dígitos incompatíveis → **C1**, sem **M2–M4**.
3. **COD-2** com **(T-cod.2)** → **M2** → Cancelar → campo volta a **COD-1**.
4. **M2** → Sim → change do registro correto (desempate se várias vigências).
5. **(T-cod.3)** → **M3** e redirecionamento.
6. Código inexistente → **M4** → Sim → add pré-preenchida **sem** segundo `confirm` de alterações não guardadas (somente `receita_cod` alterado).
7. **M4** → Sim com `receita_cod` e outro campo alterados → `confirm` de alterações não guardadas antes de sair.

### Persistência **(G-cod.save)**

8. Alterar só `receita_cod` → **Salvar** → **M-cod-block**; permanece na change; **não** exibe `bitemporal_confirm.html`.
9. Mesmo com `receita_nome` (ou outro campo) alterado junto → **Salvar** ainda bloqueia se **(T-cod.0)**.
10. Alterar código → lápis **Editar vigência** → **M-cod-block** (sem confirmação bitemporal).
11. Alterar código → **Salvar** sem blur prévio → **M-cod-block**.
12. **(R-revert)** → **Salvar** → fluxo bitemporal normal se houver outras alterações.

### Borracha e add

13. **(R-revert)** após erro **C1** (ex.: dígitos a mais) → borracha → valor **COD-1**, mensagem vermelha removida, sem aviso de saída só por `receita_cod`/`item_id`.
14. **(R-revert)** restaura **COD-1** sem recarregar a página.
15. Na **add**, vassourinha **(R-clear)** inalterada; sem **(G-cod.save)** nem **(G-cod.blur)** de redirecionamento na change.
