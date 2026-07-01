# Formulário admin de `ItemClassificacao` (apresentação e ações)

Regras de **apresentação** e **ações de UI** no formulário Django Admin de `ItemClassificacao`. **Não substitui** specs de negócio (hierarquia, nomenclatura, sugestão de código, validação no submit).

## Objetivo

Definir como o projeto **deve** apresentar o campo `receita_cod` e a ação «Limpar formulário e recomeçar» na tela **add**, em paridade com FK semânticos e sem conflitar com a borracha **(R-revert)** da **change**.

Premissa: o comportamento descrito reflete a implementação vigente em `apps/core/forms.py`, `apps/core/templates/admin/core/change_form.html` e `foreign_key_semantic_raw_id.html`.

## Referências

- `apps/core/forms.py` — `ItemClassificacaoForm`.
- `apps/core/templates/admin/core/change_form.html` — modais e ação de limpar.
- `apps/core/templates/admin/widgets/foreign_key_semantic_raw_id.html` — largura `37ch` dos FK.
- [`spec_itemClassificacao_mascara_apresentacao.md`](spec_itemClassificacao_mascara_apresentacao.md) — entrada **B1.5** / persistência **B1.8**; testes `tests_classification_item_mascara.py`.
- [`spec_itemClassificacao_editar_codigo.md`](spec_itemClassificacao_editar_codigo.md) — borracha **(R-revert)** na **change** (distinta de limpar formulário).
- [`spec_itemClassificacao_criar_filho.md`](spec_itemClassificacao_criar_filho.md) — atalho «+ Criar Código Filho» (**v2**); modal **(G5)**.
- [`spec_itemClassificacao_criar_nome.md`](spec_itemClassificacao_criar_nome.md) — protocolo **P-mãe** (add).
- [`spec_itemClassificacao_foreignKeys_lookup.md`](spec_itemClassificacao_foreignKeys_lookup.md) — lookups por `receita_cod`.
- [`spec_itemClassificacao_validar_hierarquia.md`](spec_itemClassificacao_validar_hierarquia.md) — modais de salto de nível.
- [`spec_classificador-receita.md`](spec_classificador-receita.md) § **Convenções** — prefixo `ITEMFORM`.

Termos *deve* / *não deve* / *pode* conforme RFC 2119 (ver `_dev/spec_conventions.md` **Referências**).

**Migração de símbolos legados:**

| Legado        | ID atual      |
| ------------- | ------------- |
| `(UI-1)`      | `ITEMFORM-01` |
| `(R-clear.1)` | `ITEMFORM-05` |
| `(R-clear.2)` | `ITEMFORM-06` |
| `(R-clear.3)` | `ITEMFORM-07` |
| `(R-clear.4)` | `ITEMFORM-08` |
| `(R-clear.5)` | `ITEMFORM-09` |
| `(R-clear.6)` | `ITEMFORM-10` |

## Como citar este documento

| Mecanismo          | Uso                                                                   |
| ------------------ | --------------------------------------------------------------------- |
| **Seção numerada** | `§ N` / `§ N.M` — navegação neste arquivo.                            |
| **ID normativo**   | `ITEMFORM-NN` — citação estável.                                      |
| **Prefixo**        | `ITEMFORM` — ver § **Convenções** em `spec_classificador-receita.md`. |

**Índice de IDs normativos deste arquivo:**

| ID          | Tema   | Seção | Resumo                                                                                                                                                  |
| ----------- | ------ | ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ITEMFORM-01 | UI     | 2.1   | `receita_cod` na **add** e **change** **deve** usar largura **`37ch`**, em paridade com FK semânticos.                                                  |
| ITEMFORM-02 | UI     | 2.2   | `maxlength="25"` no widget permanece para edição mascarada; validação 8–13 dígitos canônicos no backend/JS.                                             |
| ITEMFORM-03 | UI     | 2.3   | Entrada do usuário: dígitos `0-9` e `.` (**B1.5**); persistência só dígitos (**B1.8**) — ver `spec_itemClassificacao_mascara_apresentacao.md`.          |
| ITEMFORM-04 | UI     | 2.4   | Campo readonly `item_id` **não** precisa unificar largura com `37ch` (`20em` próprio).                                                                  |
| ITEMFORM-05 | Limpar | 3.1   | Ação «Limpar formulário» **deve** aparecer **somente** na view **add**; **não** na **change**.                                                          |
| ITEMFORM-06 | Limpar | 3.2   | Controle: botão `type="button"` à direita de `receita_cod`; ícone borracha ~18×18px; `title` e `aria-label` «Limpar formulário e recomeçar».            |
| ITEMFORM-07 | Limpar | 3.3   | Formulário vazio (código e nome em branco) → recarrega **sem** modal; com `receita_cod` significativo ou `receita_nome` *trim* não vazio → modal antes. |
| ITEMFORM-08 | Limpar | 3.4   | Modal: título «Atenção!»; textos de confirmação; botões **Cancelar** \| **Limpar**; Escape/overlay fecham sem recarregar.                               |
| ITEMFORM-09 | Limpar | 3.5   | Ao confirmar: navegar para `pathname + search` da add (preservar `_changelist_filters`); reinicializar estado JS completo — **não** só limpar DOM.      |
| ITEMFORM-10 | Limpar | 3.6   | Ação **não** grava/apaga no servidor; **não** substitui Salvar/Cancelar; escopo = formulário inteiro da add.                                            |

**Índice por tema:**

| Tema   | IDs                                                                          |
| ------ | ---------------------------------------------------------------------------- |
| UI     | ITEMFORM-01, ITEMFORM-02, ITEMFORM-03, ITEMFORM-04                           |
| Limpar | ITEMFORM-05, ITEMFORM-06, ITEMFORM-07, ITEMFORM-08, ITEMFORM-09, ITEMFORM-10 |

---

## Escopo

| Inclui                                                       | Não inclui                                                                        |
| ------------------------------------------------------------ | --------------------------------------------------------------------------------- |
| Largura de `receita_cod` (add e change) **(ITEMFORM-01)**    | Validação de dígitos ou hierarquia de domínio                                     |
| Ação «Limpar formulário» na **add** **(ITEMFORM-05**–**10)** | Borracha na **change** — `spec_itemClassificacao_editar_codigo.md` **(R-revert)** |
| Confirmação e recarga da URL de add **(ITEMFORM-09)**        | Persistência ou exclusão de registros                                             |

---

## 1. Specs relacionadas

| Spec                                                                                               | Relação                                                              |
| -------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| [`spec_itemClassificacao_criar_filho.md`](spec_itemClassificacao_criar_filho.md)                   | Sugestão de código; **(G5)**; atalho «+ Criar Código Filho» (**v2**) |
| [`spec_itemClassificacao_criar_nome.md`](spec_itemClassificacao_criar_nome.md)                     | **P-mãe** e rádios de radical (add)                                  |
| [`spec_itemClassificacao_foreignKeys_lookup.md`](spec_itemClassificacao_foreignKeys_lookup.md)     | Lookup por `receita_cod` e FKs semânticas                            |
| [`spec_itemClassificacao_validar_hierarquia.md`](spec_itemClassificacao_validar_hierarquia.md)     | Modais de salto de nível; item raiz                                  |
| [`spec_itemClassificacao_mascara_apresentacao.md`](spec_itemClassificacao_mascara_apresentacao.md) | Máscara de exibição; **B1.5** / **B1.8**                             |
| [`spec_itemClassificacao_editar_codigo.md`](spec_itemClassificacao_editar_codigo.md)               | Edição de `receita_cod` na change; **(R-revert)**                    |

---

## 2. Apresentação — largura de `receita_cod`

### 2.1 Paridade com FK semânticos **(ITEMFORM-01)**

O input **Código Canônico da Natureza de Receita** (`receita_cod`) nas telas **add** e **change** **deve** usar `width: 37ch`, em paridade com `classificacao_id`, `nivel_id` e `parent_item_id` em `foreign_key_semantic_raw_id.html`.

**Implementação:** `ItemClassificacaoForm.Meta.widgets["receita_cod"]` com `style: width:37ch;` (substitui legado `26ch`).

### 2.2 `maxlength` e validação **(ITEMFORM-02)**

`maxlength="25"` permanece no widget para edição/colagem mascarada no browser. Validação normativa de 8–13 dígitos canônicos no backend e pipeline JS.

### 2.3 Entrada mascarada **(ITEMFORM-03)**

Dígitos `0-9` e ponto `.` nas telas add/change (**B1.5**). Persistência no BD só com dígitos (**B1.8**). Testes: `apps/core/tests_classification_item_mascara.py`.

### 2.4 Campo `item_id` **(ITEMFORM-04)**

Campo auxiliar readonly `item_id` mantém `20em`; esta spec **não** exige unificar com `37ch`.

---

## 3. Ação «Limpar formulário e recomeçar» (somente add)

Permitir recomeçar o cadastro do zero sem sair do admin — equivalente a abrir novamente a add com formulário vazio e JS reinicializado.

### 3.1 Escopo de tela **(ITEMFORM-05)**

| View                    | Ação limpar         |
| ----------------------- | ------------------- |
| **add** (`obj is None`) | **Deve** exibir     |
| **change**              | **Não deve** exibir |

### 3.2 Controle na UI **(ITEMFORM-06)**

- **Posição:** à direita de `receita_cod`, mesma linha; espaçamento semelhante a `related-lookup`.
- **Símbolo:** SVG borracha monocromática ~18×18px, área clicável ~22×22px; wrapper `inline-flex` + `align-items: center`.
- **Acessibilidade:** `title` e `aria-label` = «Limpar formulário e recomeçar».
- **Tipo:** `button type="button"`.

### 3.3 Quando pedir confirmação **(ITEMFORM-07)**

| Situação                                         | Comportamento                 |
| ------------------------------------------------ | ----------------------------- |
| Estado inicial (sem dados relevantes do usuário) | Recarrega **sem** modal       |
| Formulário com dados relevantes                  | Modal **antes** de recarregar |

**Dados relevantes** — **somente** se:

1. `receita_cod` contém ao menos um dígito significativo (após remover pontuação de máscara); ou
2. `receita_nome` com texto não vazio (*trim*).

Demais campos (FKs, `receita_descricao`, vigências, base legal, rádios, `item_ref` pré-preenchido, etc.) **não** disparam modal sozinhos.

### 3.4 Modal de confirmação **(ITEMFORM-08)**

Quando **(ITEMFORM-07)** exige confirmação:

- **Título:** «Atenção!» (família visual de **(G5)** e salto de nível).
- **Texto:** «Deseja limpar o formulário e recomeçar?» / «Os dados já preenchidos serão perdidos.»
- **Botões:** **Cancelar** \| **Limpar**
- **Cancelar**, **Escape** e clique no overlay fecham sem recarregar.
- **Limpar** executa **(ITEMFORM-09)**.

### 3.5 Efeito — recarga da URL **(ITEMFORM-09)**

1. Navegar para `pathname + search` da add (preservar `_changelist_filters` e query string).
2. **Não** remover query string (manter contexto changelist filtrada → add → voltar).
3. Reinicializar formulário e JS (snapshots de mãe, **P-mãe**, modais pendentes, mensagens inline) — **não** basta limpar campos no DOM.

**Implementação recomendada:** `window.location.assign(window.location.pathname + window.location.search)`.

### 3.6 Fora de escopo **(ITEMFORM-10)**

- **Não** grava nem apaga registros.
- **Não** substitui **Salvar**, **Salvar e adicionar outro** ou **Cancelar** do admin.
- Escopo: **formulário inteiro** da add, não só `receita_cod`.

---

## 4. Implementação de referência

| Peça                         | Local                                                   |
| ---------------------------- | ------------------------------------------------------- |
| Largura `receita_cod`        | `ItemClassificacaoForm` em `apps/core/forms.py`         |
| Ícone + confirmação + reload | `change_form.html` (`isAddMode`, junto a `receita_cod`) |
| Modal reutilizável           | `showCoreAttentionModal` / variante no mesmo template   |
| Largura FK semânticos        | `foreign_key_semantic_raw_id.html` (`37ch`)             |

---

## 5. Testes manuais recomendados

### 5.1 Add

1. Add vazia → vassourinha → recarrega **sem** modal **(ITEMFORM-07)**.
2. Preencher código e classificação → vassourinha → modal → **Cancelar** → dados permanecem **(ITEMFORM-08)**.
3. Mesmo cenário → **Limpar** → formulário vazio; URL mantém query de changelist **(ITEMFORM-09)**.
4. Add a partir de changelist filtrada → após limpar, **Voltar/Cancelar** retorna com filtros coerentes.
5. Change → **sem** vassourinha **(ITEMFORM-05)**; borracha **(R-revert)** em `spec_itemClassificacao_editar_codigo.md`.
6. `receita_cod` add/change com `37ch` **(ITEMFORM-01)**.

### 5.2 Change — atalho filho

Checklist completo em [`spec_itemClassificacao_criar_filho.md`](spec_itemClassificacao_criar_filho.md) (secção **v2**). Resumo:

1. Change sem editar → «+ Criar Código Filho» verde; clique sem `confirm` de alterações não guardadas (Matriz).
2. Editar campo → clique → **um** `confirm`; depois modal «Continuar».
3. Detalhe → modal de bloqueio; Matriz inativa ou sem sugestão → botão desactivado.
