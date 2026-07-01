# Edição de `receita_cod` na change (`ItemClassificacao`)

Comportamento quando o usuário **altera** o campo **Código Canônico da Natureza de Receita** na view **change** do Django Admin. **Não substitui** lookups na **add**, navegação estrutural **(G-nav.\*)** nem validação de domínio no `clean()`.

## Objetivo

Definir como o projeto **deve** tratar alteração de `receita_cod` na change: **navegação** (blur → redirecionar ou restaurar) ou **bloqueio de persistência** (Salvar / Editar vigência) — **nunca** gravar **COD-2** na mesma linha de registro.

Premissa: implementação em `change_form.html`, `admin_handlers.py` (`BitemporalChangeHandler`) e `classification_item_code_lookup.py` (`resolve-code-navigation`).

## Referências

- `apps/core/templates/admin/core/change_form.html` — blur, modais, **(R-revert)**.
- `apps/core/admin_handlers.py` — bloqueio servidor **(G-cod.save)**.
- `apps/core/classification_item_code_lookup.py` — `resolve-code-navigation`.
- [`spec_itemClassificacao_formulario.md`](spec_itemClassificacao_formulario.md) — `37ch`; **ITEMFORM-05**–**10** (add); **ITEMEC-19**–**23** (change).
- [`spec_itemClassificacao_mascara_apresentacao.md`](spec_itemClassificacao_mascara_apresentacao.md) — **B1** normalização/máscara.
- [`spec_itemClassificacao_foreignKeys_lookup.md`](spec_itemClassificacao_foreignKeys_lookup.md) — **ITEMEC-12** (sem hierarquia no blur da change).
- [`spec_itemClassificacao_criar_filho.md`](spec_itemClassificacao_criar_filho.md) — **(T6)**, **(T7)**; **(G6)**.
- [`spec_itemClassificacao_navegacao.md`](spec_itemClassificacao_navegacao.md) — **(G-nav.\*)** (distinto de blur).
- [`spec_itemClassificacao_criar_nome.md`](spec_itemClassificacao_criar_nome.md) — protocolos add após redirecionamento **C4**.
- [`spec_classificador-receita.md`](spec_classificador-receita.md) § **Convenções** — prefixo `ITEMEC`.

Termos *deve* / *não deve* / *pode* conforme RFC 2119 (ver `_dev/spec_conventions.md` **Referências**).

**Migração de símbolos legados:**

| Legado                            | ID atual                             |
| --------------------------------- | ------------------------------------ |
| `(G-cod.blur)`                    | `ITEMEC-10`                          |
| `(G-cod.save)`                    | `ITEMEC-13`                          |
| `(G-cod.save.1)`–`(G-cod.save.5)` | `ITEMEC-14`–`ITEMEC-18`              |
| `(T-cod.0)`–`(T-cod.4)`           | `ITEMEC-02`, `ITEMEC-04`–`ITEMEC-08` |
| `(R-revert.1)`–`(R-revert.5)`     | `ITEMEC-19`–`ITEMEC-23`              |
| `C1`–`C4`                         | `ITEMEC-24`–`ITEMEC-27`              |
| `M2`–`M4`                         | `ITEMEC-33`–`ITEMEC-36`              |
| `M-cod-block`                     | `ITEMEC-37`, `ITEMEC-38`             |

## Como citar este documento

| Mecanismo          | Uso                                                                 |
| ------------------ | ------------------------------------------------------------------- |
| **Seção numerada** | `§ N` / `§ N.M` — navegação neste arquivo.                          |
| **ID normativo**   | `ITEMEC-NN` — citação estável.                                      |
| **Prefixo**        | `ITEMEC` — ver § **Convenções** em `spec_classificador-receita.md`. |

**Índice de IDs normativos deste arquivo:**

| ID        | Tema         | Seção | Resumo                                                                                                                                           |
| --------- | ------------ | ----- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| ITEMEC-01 | Regra        | 1     | Código canônico **não pode** ser substituído na **mesma linha** (mesmo PK); change serve para **navegar** ou **desfazer**, não gravar **COD-2**. |
| ITEMEC-02 | Termo        | 2     | **(T-cod.0):** **COD-2** não vazio **e** **COD-2 ≠ COD-1**.                                                                                      |
| ITEMEC-03 | Termo        | 2     | Normalização obrigatória: remover `.` e espaços; autoridade **COD-1** vs **COD-2** (não só `form.has_changed()`).                                |
| ITEMEC-04 | Termo        | 2     | **(T-cod.1):** ao menos um registro **(T6)** com `receita_cod` = **COD-2**.                                                                      |
| ITEMEC-05 | Termo        | 2     | **(T-cod.2):** **(T-cod.1)** e existe **(T6)** de **COD-2** com **(T7)** vs **V1**.                                                              |
| ITEMEC-06 | Termo        | 2     | **(T-cod.3):** **(T-cod.1)** e **nenhum** **(T6)** de **COD-2** com **(T7)** vs **V1**.                                                          |
| ITEMEC-07 | Termo        | 2     | **(T-cod.4):** `len(COD-2)` compatível com máscara do item ou `estrutura_codigo` **(T6)**.                                                       |
| ITEMEC-08 | Termo        | 2     | **(T-cod.2)** e **(T-cod.3)** excludentes e exaustivos para **COD-2** existente.                                                                 |
| ITEMEC-10 | Navegação    | 3     | Eixo **blur:** **COD-2 ≠ COD-1** → classificar **ITEMEC-24**–**27**, modais **ITEMEC-33**–**36** ou restaurar **COD-1**.                         |
| ITEMEC-11 | Navegação    | 3.1   | Pipeline blur: add → encerrar; change → **B1** + dígitos; sem **(T-cod.0)** → encerrar; com **(T-cod.0)** → cenários.                            |
| ITEMEC-12 | Navegação    | 3.2   | Na **change** com **(T-cod.0)**, cliente **não deve** chamar `syncHierarchyFromCode('code_blur')` nem alterar `parent_item_id` / `nivel_id`.     |
| ITEMEC-13 | Persistência | 4     | Eixo **Salvar** / **Editar vigência:** **(T-cod.0)** → **não** abrir `bitemporal_confirm.html`; exibir **ITEMEC-37**.                            |
| ITEMEC-14 | Persistência | 4.1   | Gatilhos: `name="_save"` e `name="_edit_vigencia"` `value="1"`; demais submits change com `receita_cod` alterado → mesma regra.                  |
| ITEMEC-15 | Persistência | 4.2   | **(T-cod.0)** no submit → bloquear confirmação bitemporal **independentemente** de outros campos alterados.                                      |
| ITEMEC-16 | Persistência | 4.3   | Cliente: interceptar submit; **(T-cod.0)** → `preventDefault()` + **ITEMEC-37**; senão fluxo normal.                                             |
| ITEMEC-17 | Persistência | 4.4   | Servidor: `BitemporalChangeHandler` rejeita confirmação e segunda etapa se **(T-cod.0)**; reexibir change com mensagem equivalente.              |
| ITEMEC-18 | Persistência | 4.5   | Após **ITEMEC-19**–**23**, Salvar/Editar vigência voltam ao fluxo bitemporal padrão.                                                             |
| ITEMEC-19 | Revert       | 5.1   | Borracha à direita de `receita_cod` na **change** (layout par **ITEMFORM-06**).                                                                  |
| ITEMEC-20 | Revert       | 5.2   | Restaura **somente** `receita_cod` para **COD-1** (valor + máscara); **sem** recarregar página.                                                  |
| ITEMEC-21 | Revert       | 5.3   | Ação imediata, **sem** modal.                                                                                                                    |
| ITEMEC-22 | Revert       | 5.4   | `title` / `aria-label`: «Restaurar código original».                                                                                             |
| ITEMEC-23 | Revert       | 5.5   | Pós-restauração: `clearReceitaCodMessages`, `setCustomValidity('')`, `syncItemIdPreview()`, `__coreRebaselineReceitaCodNavigationDirtyState()`.  |
| ITEMEC-24 | Cenário      | 6     | **C1:** **não** **(T-cod.4)** → erro inline `showReceitaCodError`; sem modais navegação.                                                         |
| ITEMEC-25 | Cenário      | 6     | **C2:** **(T-cod.4)** + **(T-cod.1)** + **(T-cod.2)** → modal **ITEMEC-33**.                                                                     |
| ITEMEC-26 | Cenário      | 6     | **C3:** **(T-cod.4)** + **(T-cod.1)** + **(T-cod.3)** → modal **ITEMEC-34**.                                                                     |
| ITEMEC-27 | Cenário      | 6     | **C4:** **(T-cod.4)** + **não** **(T-cod.1)** → modal **ITEMEC-35**.                                                                             |
| ITEMEC-28 | API          | 7     | `GET …/resolve-code-navigation/` com `code`, `vigencia_inicio`, `vigencia_fim`, `exclude_pk` opcional.                                           |
| ITEMEC-29 | API          | 7     | Resposta: `scenario` `C2`\|`C3`\|`C4` + `target`, ou `C1` com `message`.                                                                         |
| ITEMEC-30 | API          | 7     | Desempate C2/C3: maior `data_vigencia_fim` → `data_vigencia_inicio` → `pk`.                                                                      |
| ITEMEC-31 | Modal        | 8     | **M2**–**M4:** `showCoreAttentionModal`, «Atenção!», **Cancelar** \| **Sim**; cancelar restaura **COD-1**.                                       |
| ITEMEC-32 | Modal        | 8     | «Sim» em M2–M4: `__coreRebaselineReceitaCodNavigationDirtyState()` + `__coreConfirmUnsavedIfDirty(go)`; preservar `_changelist_filters`.         |
| ITEMEC-33 | Modal        | 8.1   | **M2** (C2): «Já existe registro ativo e vigente para o código \<código\>…» → change do PK desempatado.                                          |
| ITEMEC-34 | Modal        | 8.2   | **M3** (C3): «O \<código\> digitado tem vigência diversa…» → change desempatado.                                                                 |
| ITEMEC-35 | Modal        | 8.3   | **M4** (C4): «Não foi encontrado registro…» → **add** pré-preenchida (**ITEMEC-36**).                                                            |
| ITEMEC-36 | Modal        | 8.3   | **C4** «Sim» → add com `receita_cod` pré-preenchido; protocolos add (**B1**, `syncHierarchyFromCode`, **(V3)**, **P-mãe**).                      |
| ITEMEC-37 | Modal        | 9     | **M-cod-block:** informativo; botão único **Entendi**; **não** submete nem redireciona.                                                          |
| ITEMEC-38 | Modal        | 9     | Texto normativo de **M-cod-block** (três parágrafos — § **9**).                                                                                  |
| ITEMEC-39 | Teste        | 10    | Checklist manual § **10** **deve** cobrir navegação, persistência, revert e paridade com add.                                                    |

**Índice por tema:**

| Tema         | IDs                   |
| ------------ | --------------------- |
| Regra        | ITEMEC-01             |
| Termo        | ITEMEC-02 … ITEMEC-08 |
| Navegação    | ITEMEC-10 … ITEMEC-12 |
| Persistência | ITEMEC-13 … ITEMEC-18 |
| Revert       | ITEMEC-19 … ITEMEC-23 |
| Cenário      | ITEMEC-24 … ITEMEC-27 |
| API          | ITEMEC-28 … ITEMEC-30 |
| Modal        | ITEMEC-31 … ITEMEC-38 |
| Teste        | ITEMEC-39             |

---

## Escopo

| Inclui                                                                                           | Não inclui                                                          |
| ------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------- |
| View **change**; **ITEMEC-10** blur **C1**–**C4**; **ITEMEC-13** bloqueio Salvar/Editar vigência | View **add** (sugestão filho, **ITEMFORM** limpar, lookups normais) |
| **ITEMEC-19**–**23** borracha change                                                             | `readonly` permanente em `receita_cod`                              |
| Endpoint `resolve-code-navigation` **(ITEMEC-28)**                                               | Persistir **COD-2** no mesmo registro                               |
|                                                                                                  | «Limpar formulário» add — **ITEMFORM-05**                           |

---

## 1. Regra de negócio **(ITEMEC-01)**

Uma vez criado, o código canônico **não pode** ser substituído na mesma linha bitemporal. Na change, editar `receita_cod` serve para **navegar** (outro registro ou add) ou **desfazer** (**ITEMEC-19**); **não** para gravar via **Salvar** ou **Editar vigência**.

| Eixo                         | Gatilho                                    | Efeito                                             |
| ---------------------------- | ------------------------------------------ | -------------------------------------------------- |
| Navegação **(ITEMEC-10)**    | `blur` com **(T-cod.0)**                   | Modais **ITEMEC-33**–**35** ou restaurar **COD-1** |
| Persistência **(ITEMEC-13)** | Salvar / Editar vigência com **(T-cod.0)** | **ITEMEC-37**; sem `bitemporal_confirm.html`       |

---

## 2. Notação e terminologia

### 2.1 Símbolos (sem ID próprio)

| Símbolo        | Significado                                                                   |
| -------------- | ----------------------------------------------------------------------------- |
| **COD-1**      | Dígitos do registro ao carregar a change; snapshot até sair ou **ITEMEC-20**. |
| **COD-2**      | Dígitos normalizados do input na avaliação (**B1**).                          |
| **V1**         | `data_vigencia_inicio` / `data_vigencia_fim` do `instance` na change.         |
| **\<código\>** | `receita_cod` formatado para modais.                                          |

### 2.2 Termos normativos **(ITEMEC-02**–**ITEMEC-08)**

- **(ITEMEC-02)** **(T-cod.0):** **COD-2** não vazio **e** **COD-2 ≠ COD-1**.
- **(ITEMEC-03)** Remover `.` e espaços; comparar só dígitos.
- **(ITEMEC-04)** **(T-cod.1):** ≥1 registro **(T6)** com `receita_cod` = **COD-2**.
- **(ITEMEC-05)** **(T-cod.2):** **(T-cod.1)** + **(T7)** de algum **(T6)** de **COD-2** vs **V1**.
- **(ITEMEC-06)** **(T-cod.3):** **(T-cod.1)** + nenhum **(T7)** vs **V1**.
- **(ITEMEC-07)** **(T-cod.4):** `len(COD-2)` vs máscara (`fetchReceitaCodDigitLimit` / `runCodeDigitValidation`).
- **(ITEMEC-08)** **(T-cod.2)** e **(T-cod.3)** excludentes e exaustivos.

**(T6)** registro ativo e **(T7)** sobreposição de vigência: ver `spec_itemClassificacao_criar_filho.md`.

---

## 3. Eixo navegação — blur **(ITEMEC-10)**

### 3.1 Pipeline **(ITEMEC-11)**

| Etapa | Condição                          | Ação                                 |
| ----- | --------------------------------- | ------------------------------------ |
| 0     | View **add**                      | Encerrar — spec não aplica           |
| 0     | View **change**                   | Prosseguir                           |
| 1     | `blur` em `receita_cod`           | Início                               |
| 2     | **B1** + `runCodeDigitValidation` | Inválido → **ITEMEC-24**; sem modais |
| 3     | **não** **(T-cod.0)**             | Encerrar                             |
| 4     | **(T-cod.0)** + dígitos válidos   | **ITEMEC-25**–**27** + modal         |

### 3.2 Hierarquia no blur **(ITEMEC-12)**

Na **change** com **(T-cod.0)**: **não** `syncHierarchyFromCode('code_blur')`; **não** alterar `parent_item_id` / `nivel_id`. Na **add**: `spec_itemClassificacao_foreignKeys_lookup.md`.

---

## 4. Eixo persistência **(ITEMEC-13)**

Contexto: `BitemporalChangeHandler` renderiza `bitemporal_confirm.html` quando há alterações ou `_edit_vigencia`. Trocar `receita_cod` viola **ITEMEC-01**.

### 4.1 Gatilhos **(ITEMEC-14)**

| Gatilho             | Identificação                       |
| ------------------- | ----------------------------------- |
| **Salvar**          | `name="_save"`                      |
| **Editar vigência** | `name="_edit_vigencia"` `value="1"` |

### 4.2 Condição **(ITEMEC-15)**

**(T-cod.0)** no submit (normalização **B1**) → bloquear confirmação bitemporal mesmo com outros campos alterados.

### 4.3 Cliente **(ITEMEC-16)**

Interceptar submit na change; **(T-cod.0)** → `preventDefault()` + **ITEMEC-37**. Salvar sem blur prévio ainda bloqueia.

### 4.4 Servidor **(ITEMEC-17)**

`BitemporalChangeHandler.handle`: antes de `bitemporal_confirm.html` e na segunda etapa (`edit_strategy` preenchido) — **(T-cod.0)** → não confirmar; mensagem equivalente a **ITEMEC-38**.

### 4.5 Após revert **(ITEMEC-18)**

**COD-2** = **COD-1** após **ITEMEC-20** → fluxo bitemporal padrão.

---

## 5. Borracha na change **(ITEMEC-19**–**ITEMEC-23)**

| ID        | Regra                                                            |
| --------- | ---------------------------------------------------------------- |
| ITEMEC-19 | Controle à direita de `receita_cod` (layout par **ITEMFORM-06**) |
| ITEMEC-20 | Restaura só `receita_cod` → **COD-1**; sem reload                |
| ITEMEC-21 | Sem modal                                                        |
| ITEMEC-22 | `title` / `aria-label`: «Restaurar código original»              |
| ITEMEC-23 | Pós-ação: limpar mensagens, rebaseline dirty state               |

**Implementação:** `restoreReceitaCodOrigem()` — também no **Cancelar** de **ITEMEC-31**.

---

## 6. Cenários no blur **(ITEMEC-24**–**ITEMEC-27)**

Primeira linha válida após pipeline § **3.1**:

| ID        | Condições                                     | UI            |
| --------- | --------------------------------------------- | ------------- |
| ITEMEC-24 | **não** **(T-cod.4)**                         | Erro inline   |
| ITEMEC-25 | **(T-cod.4)** + **(T-cod.1)** + **(T-cod.2)** | **ITEMEC-33** |
| ITEMEC-26 | **(T-cod.4)** + **(T-cod.1)** + **(T-cod.3)** | **ITEMEC-34** |
| ITEMEC-27 | **(T-cod.4)** + **não** **(T-cod.1)**         | **ITEMEC-35** |

---

## 7. Endpoint `resolve-code-navigation` **(ITEMEC-28**–**ITEMEC-30)**

`GET …/admin/core/itemclassificacao/resolve-code-navigation/`

| Parâmetro         | Obrigatório | Descrição           |
| ----------------- | ----------- | ------------------- |
| `code`            | Sim         | **COD-2** (dígitos) |
| `vigencia_inicio` | Sim         | Início **V1**       |
| `vigencia_fim`    | Sim         | Fim **V1**          |
| `exclude_pk`      | Não         | PK em edição        |

Resposta sugerida **(ITEMEC-29):** `{ "ok": true, "scenario": "C2"|"C3"|"C4", "codigo_display": "...", "target": { "view", "pk", "change_url", "add_url" } }` ou `{ "ok": false, "scenario": "C1", "message" }`.

Desempate **(ITEMEC-30):** `data_vigencia_fim` → `data_vigencia_inicio` → `pk`.

---

## 8. Modais de navegação **(ITEMEC-31**–**ITEMEC-36)**

### 8.1 Padrão comum **(ITEMEC-31**, **ITEMEC-32)**

- `showCoreAttentionModal`, «Atenção!», **Cancelar** \| **Sim**.
- Cancelar / Escape / overlay → **COD-1** via `restoreReceitaCodOrigem()`.
- «Sim» → `location.assign`; **ITEMEC-32** rebaseline + `__coreConfirmUnsavedIfDirty`.

### 8.2 Textos **(ITEMEC-33**–**ITEMEC-35)**

**ITEMEC-33 (M2 / C2):**

```text
Atenção!

Já existe registro ativo e vigente para o código <código>.

Deseja ser direcionado para a tela de edição desse código?
```

**ITEMEC-34 (M3 / C3):**

```text
Atenção!

O <código> digitado tem vigência diversa do código atual.

Deseja ser direcionado para a tela de edição do <código>?
```

**ITEMEC-35 (M4 / C4):**

```text
Atenção!

Não foi encontrado registro para o <código>.

Deseja ser direcionado para a tela de criação de um novo código?
```

| Cenário            | «Sim»                                |
| ------------------ | ------------------------------------ |
| C2, C3             | `change` do PK desempatado           |
| C4 **(ITEMEC-36)** | `add` pré-preenchida; protocolos add |

---

## 9. Modal de bloqueio **(ITEMEC-37**, **ITEMEC-38)**

Informativo; botão **Entendi** apenas; não submete.

**Texto normativo (ITEMEC-38):**

```text
Atenção!

Uma vez criado, o código canônico não pode ser substituído na mesma linha de registro. Não é possível gravar outro código neste item por meio de Salvar ou Editar vigência.

Para abrir outro código já cadastrado: confirme a alteração ao sair do campo Código Canônico (TAB ou clique fora) e escolha a opção no aviso, ou localize o item na lista do admin.

Para cadastrar um código novo: use Adicionar Item de Classificação.

Para desfazer o que foi digitado nesta tela: use o ícone Restaurar código original ao lado do campo.
```

---

## 10. Testes manuais **(ITEMEC-39)**

### Navegação

1. Blur sem alterar → sem modal.
2. Dígitos incompatíveis → **ITEMEC-24**.
3. **(T-cod.2)** → **ITEMEC-33** → Cancelar → **COD-1**.
4. **ITEMEC-33** → Sim → change correta (desempate).
5. **(T-cod.3)** → **ITEMEC-34**.
6. Inexistente → **ITEMEC-35** → Sim → add sem `confirm` extra se só código alterado.
7. **ITEMEC-35** → Sim com outro campo alterado → `confirm` alterações não guardadas.

### Persistência

8. Só `receita_cod` → Salvar → **ITEMEC-37**; sem `bitemporal_confirm.html`.
9. `receita_nome` + código → Salvar ainda bloqueia com **(T-cod.0)**.
10. Editar vigência → **ITEMEC-37**.
11. Salvar sem blur → **ITEMEC-37**.
12. **ITEMEC-20** → Salvar → fluxo bitemporal normal.

### Revert e add

13. **ITEMEC-20** após **ITEMEC-24** → limpa erro, sem aviso falso.
14. **ITEMEC-20** sem reload.
15. Na **add**: **ITEMFORM** inalterado; sem eixos desta spec.

---

## Specs relacionadas

| Spec                                                                                               | Relação                              |
| -------------------------------------------------------------------------------------------------- | ------------------------------------ |
| [`spec_itemClassificacao_formulario.md`](spec_itemClassificacao_formulario.md)                     | Largura; limpar add vs revert change |
| [`spec_itemClassificacao_mascara_apresentacao.md`](spec_itemClassificacao_mascara_apresentacao.md) | **B1**                               |
| [`spec_itemClassificacao_foreignKeys_lookup.md`](spec_itemClassificacao_foreignKeys_lookup.md)     | Lookups add; **ITEMEC-12**           |
| [`spec_itemClassificacao_criar_filho.md`](spec_itemClassificacao_criar_filho.md)                   | **(T6)**, **(T7)**, **(G6)**         |
| [`spec_itemClassificacao_navegacao.md`](spec_itemClassificacao_navegacao.md)                       | **(G-nav.\*)**                       |
| [`spec_itemClassificacao_criar_nome.md`](spec_itemClassificacao_criar_nome.md)                     | Add pós-**C4**                       |
