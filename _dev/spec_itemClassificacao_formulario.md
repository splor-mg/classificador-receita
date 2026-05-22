# Item de classificação — formulário admin (apresentação e ações na tela de criação)

Esta especificação define regras de **apresentação** e **ações de UI** no formulário Django admin de `ItemClassificacao`, complementando as specs de negócio (hierarquia, nomenclatura, sugestão de código, validação no submit).

**Implementação de referência:** `apps/core/forms.py` (`ItemClassificacaoForm`), `apps/core/templates/admin/core/change_form.html`, widget `apps/core/templates/admin/widgets/foreign_key_semantic_raw_id.html`.

**Specs relacionadas (não substituídas):**

| Spec                                                  | Relação                                                                                                                                                                    |
| ----------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `_dev/spec_itemClassificacao_criar_filho.md`          | Sugestão de código; modal **(G5)** na troca de item mãe; atalho **«+ Criar Código Filho»** na change (**v2** — estilo verde, `isDirty`/rebaseline, aviso único no clique). |
| `_dev/spec_itemClassificacao_criar_nome.md`           | Protocolo **P-mãe** e rádios de radical (somente add).                                                                                                                     |
| `_dev/spec_itemClassificacao_foreignKeys_lookup.md`   | Lookup por `receita_cod` e FKs semânticas.                                                                                                                                 |
| `_dev/spec_itemClassificacao_validar_hierarquia.md`   | Modais de salto de nível no submit; item raiz.                                                                                                                             |
| `_dev/spec_itemClassificacao_mascara_apresentacao.md` | Máscara de exibição de códigos.                                                                                                                                            |
| `_dev/spec_itemClassificacao_editar_codigo.md`        | Edição de `receita_cod` na **change**; borracha **(R-revert)** (restaura código original — distinto de **(R-clear)**).                                                     |

---

## Escopo

| Inclui                                                         | Não inclui                                                                             |
| -------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| Largura do campo `receita_cod` (add e change)                  | Regras de validação de dígitos ou hierarquia                                           |
| Ação **Limpar formulário** (ícone vassourinha) na tela **add** | Borracha na **change** — `_dev/spec_itemClassificacao_editar_codigo.md` **(R-revert)** |
| Confirmação e recarga da URL de add                            | Persistência ou exclusão de registros                                                  |

---

## Apresentação — largura de `receita_cod`

### (UI-1) Paridade com FK semânticos

O input editável **Código Canônico da Natureza de Receita** (`receita_cod`) nas telas **add** e **change** **deve** usar largura visual **`37ch`**, em paridade com o input de exibição dos FK semânticos (`classificacao_id`, `nivel_id`, `parent_item_id` — `width: 37ch` em `foreign_key_semantic_raw_id.html`).

**Implementação (form):** `ItemClassificacaoForm.Meta.widgets["receita_cod"]` com `style: width:37ch;` (substitui o valor legado `26ch`).

**Notas:**

- `maxlength="25"` no widget permanece para edição/colagem do código **mascarado** no browser; a validação normativa de 8–13 dígitos canônicos segue no backend e no pipeline JS.
- Entrada do usuário: apenas dígitos **0-9** (pontuação da máscara não é digitável manualmente) — ver **B1.5** em `_dev/spec_itemClassificacao_mascara_apresentacao.md`.
- O campo auxiliar readonly `item_id` mantém largura própria (`20em`); esta spec **não** exige unificar `item_id` com `37ch`.

---

## Ação «Limpar formulário e recomeçar» (somente add)

### Objetivo

Na tela **Adicionar Item de Classificação**, permitir que o usuário **recomece o cadastro do zero** sem sair do admin, equivalente a abrir novamente a página de add com formulário vazio e estado JavaScript reinicializado.

### (R-clear.1) Escopo de tela

- **Deve** aparecer **apenas** na view **add** (`obj is None`).
- **Não deve** aparecer na view **change** (edição de registro existente).

### (R-clear.2) Controle na UI

- **Posição:** imediatamente à direita do input `receita_cod`, na mesma linha visual, alinhado ao padrão dos ícones de lupa dos FK (espaçamento semelhante a `related-lookup`).
- **Símbolo:** ícone SVG monocromático de **borracha** (~18×18px desenhado, área clicável ~22×22px), sem caixa — paridade visual com `.related-lookup`; metáfora de apagar/limpar o que foi digitado; input e ícone dentro de um wrapper `inline-flex` com `align-items: center` para centralização vertical.
- **Acessibilidade (obrigatório):**
  - `title="Limpar formulário e recomeçar"`
  - `aria-label="Limpar formulário e recomeçar"`
- **Tipo de controle:** `button type="button"` (não submete o formulário).

### (R-clear.3) Quando pedir confirmação

| Situação                                                                                     | Comportamento                                       |
| -------------------------------------------------------------------------------------------- | --------------------------------------------------- |
| Formulário **sem** dados preenchidos pelo usuário (estado inicial após carga/recarga da add) | **Recarrega** direto, **sem** modal.                |
| Formulário **com** dados preenchidos                                                         | Exibe modal de confirmação **antes** de recarregar. |

**«Dados preenchidos»** — considera-se que há conteúdo relevante **somente** quando **qualquer** condição abaixo for verdadeira:

1. **Código Canônico da Natureza de Receita** (`receita_cod`) contém ao menos um dígito significativo (após remover pontuação de máscara);
2. **Nome da Classificação por Natureza de Receita** (`receita_nome`) com texto não vazio (*trim*).

Demais campos (FKs, `receita_descricao`, vigências, base legal, rádios `matriz`/`item_gerado`, `item_ref` pré-preenchido na carga da add, etc.) **não** disparam o modal sozinhos — se código e nome estiverem em branco, a ação recarrega direto.

### (R-clear.4) Modal de confirmação

Quando **(R-clear.3)** exige confirmação:

- **Título:** «Atenção!» (mesma família visual dos modais já usados no `change_form.html`, ex.: **(G5)** e salto de nível).
- **Texto orientativo (duas linhas / dois parágrafos):**
  1. «Deseja limpar o formulário e recomeçar?»
  2. «Os dados já preenchidos serão perdidos.»
- **Botões:** **Cancelar** | **Limpar**
- **Cancelar**, tecla **Escape** e clique no **overlay** fecham o modal **sem** recarregar.
- **Confirmar** executa **(R-clear.5)**.

### (R-clear.5) Efeito da ação — recarga da URL (opção A)

Ao confirmar (ou quando não há confirmação):

1. O cliente **deve** navegar para a **URL atual da página de add**, preservando **`pathname` + `search`** (query string), em especial parâmetros de retorno à changelist (ex.: `_changelist_filters` ou equivalente do Django admin).
2. **Não deve** remover query string da barra de endereço (opção **A** — manter contexto de navegação «lista filtrada → add → voltar à lista»).
3. A recarga **deve** reinicializar todo o estado do formulário e do JavaScript (snapshots de item mãe, **P-mãe**, modais pendentes, mensagens inline, etc.) — **não** basta limpar campos no DOM.

**Implementação recomendada:** `window.location.assign(window.location.pathname + window.location.search)` (ou `location.reload()` na mesma URL).

### (R-clear.6) Fora de escopo da ação

- **Não** grava nem apaga registros no servidor.
- **Não** substitui os botões **Salvar**, **Salvar e adicionar outro** ou **Cancelar** do admin.
- **Não** limpa apenas `receita_cod`; o escopo é **formulário inteiro** da add.

---

## Referências de código (mapa rápido)

| Peça                                     | Local                                                          |
| ---------------------------------------- | -------------------------------------------------------------- |
| Largura `receita_cod`                    | `ItemClassificacaoForm` em `apps/core/forms.py`                |
| Ícone vassourinha + confirmação + reload | `change_form.html` (bloco `isAddMode`, junto a `receita_cod`)  |
| Modal reutilizável                       | `showCoreAttentionModal` / variante dedicada no mesmo template |
| Largura FK semânticos                    | `foreign_key_semantic_raw_id.html` (`37ch`)                    |

---

## Testes manuais recomendados (add)

1. Add vazia → clicar vassourinha → recarrega **sem** modal.
2. Preencher código e classificação → vassourinha → modal → **Cancelar** → dados permanecem.
3. Mesmo cenário → **Limpar** → formulário vazio; URL mantém `?…` de changelist se existia.
4. Entrar na add a partir de changelist filtrada → após limpar, **Voltar/Cancelar** do admin ainda retorna à lista com filtros coerentes.
5. Change view → **não** exibe vassourinha **(R-clear)**; borracha **(R-revert)** — `spec_itemClassificacao_editar_codigo.md`.
6. `receita_cod` na add e na change com largura alinhada aos FK (`37ch`).

## Testes manuais recomendados (change — atalho filho)

Ver checklist completo em `_dev/spec_itemClassificacao_criar_filho.md` (secção v2). Resumo:

1. Change **sem** editar → «+ Criar Código Filho» verde no estado normal; clique **sem** `confirm` de alterações não guardadas (Matriz).
2. Editar um campo → clique → **um** `confirm` de alterações não guardadas; depois modal «Continuar».
3. Detalhe → modal de bloqueio; Matriz inactiva ou sem sugestão → botão desactivado.
