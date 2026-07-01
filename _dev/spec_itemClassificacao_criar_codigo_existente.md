# Código já existente na add (`ItemClassificacao`)

Comportamento na tela **add** quando `receita_cod` coincide com registro **ativo** e vigência **sobreposta** à do formulário: **alerta** amarelo na edição; **erro** bloqueante no submit. **Não substitui** `spec_itemClassificacao_editar_codigo.md` (change) nem o algoritmo canônico de «próximo código» em `spec_itemClassificacao_criar_filho.md`.

## Objetivo

Na add, o projeto **deve**:

1. detectar conflito **CE** e exibir alerta inline amarelo;
2. oferecer link do **CE★** em nova aba e «próximo código disponível» no formulário;
3. bloquear gravação com erro vermelho se **CE** persistir no submit.

Premissa: `classification_item_existing_code.py`, endpoint `lookup-existing-code-conflict/`, `ItemClassificacaoForm.clean()`, `change_form.html` (`scheduleExistingCodeConflictCheck`).

## Referências

- `apps/core/classification_item_existing_code.py`
- `apps/core/tests_classification_item_existing_code.py`
- [`spec_itemClassificacao_criar_filho.md`](spec_itemClassificacao_criar_filho.md) — protocolo «próximo código»; **(T6)** / **(T7)**.
- [`spec_itemClassificacao_foreignKeys_lookup.md`](spec_itemClassificacao_foreignKeys_lookup.md) — padrão de mensagens inline e links.
- [`spec_itemClassificacao_criar_nome.md`](spec_itemClassificacao_criar_nome.md) — **P-mãe** após mudança de código.
- [`spec_itemClassificacao_validar_hierarquia.md`](spec_itemClassificacao_validar_hierarquia.md) — pipeline de submit.
- [`spec_itemClassificacao_editar_codigo.md`](spec_itemClassificacao_editar_codigo.md) — fluxos da **change**.
- [`spec_classificador-receita.md`](spec_classificador-receita.md) § **Convenções** — prefixo `ITEMCEX`.

Termos *deve* / *não deve* / *pode* conforme RFC 2119 (ver `_dev/spec_conventions.md` **Referências**).

**Migração de símbolos legados:**

| Legado                          | ID atual                  |
| ------------------------------- | ------------------------- |
| `CE-1`                          | `ITEMCEX-03`              |
| `CE-2`                          | `ITEMCEX-04`              |
| `CE-3`                          | `ITEMCEX-05`              |
| `CE-3a`–`CE-3d`                 | `ITEMCEX-06`–`ITEMCEX-09` |
| `CE-4`                          | `ITEMCEX-11`              |
| `CE-5` (submit cliente)         | `ITEMCEX-10`              |
| `CE-5` (efeitos próximo código) | `ITEMCEX-12`              |
| `CE-6`–`CE-12`                  | `ITEMCEX-13`–`ITEMCEX-22` |
| `DP1`–`DP6`                     | `ITEMCEX-23`–`ITEMCEX-28` |

## Como citar este documento

| Mecanismo          | Uso                                                                  |
| ------------------ | -------------------------------------------------------------------- |
| **Seção numerada** | `§ N` / `§ N.M` — navegação neste arquivo.                           |
| **ID normativo**   | `ITEMCEX-NN` — citação estável.                                      |
| **Prefixo**        | `ITEMCEX` — ver § **Convenções** em `spec_classificador-receita.md`. |

**Índice de IDs normativos deste arquivo:**

| ID         | Tema     | Seção | Resumo                                                                                                                                                         |
| ---------- | -------- | ----- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ITEMCEX-01 | Termo    | 2     | **CE:** mesmo `receita_cod` (dígitos), registo **(T6)**, vigência **(T7)** com a vigência efetiva do formulário.                                               |
| ITEMCEX-02 | Termo    | 2     | **CE★:** entre CE, desempate `-data_vigencia_inicio`, `-data_registro_inicio`, `-pk`.                                                                          |
| ITEMCEX-03 | Detecção | 3.1   | Blur/change na add → resolver CE; se sim, alerta amarelo com **CE★**; se não, remover aviso.                                                                   |
| ITEMCEX-04 | Mensagem | 3.2   | Fragmento HTML único `existing_code_conflict_message_html` (alerta e erro); link código `target="_blank"`; «Clique aqui» `js-existing-code-conflict-next`.     |
| ITEMCEX-05 | Submit   | 3.3   | Submit com CE persistente → bloquear gravação; mesmo HTML de **ITEMCEX-04** em erro vermelho.                                                                  |
| ITEMCEX-06 | UX       | 3.4   | **Não** exibir alerta amarelo e erro vermelho CE simultaneamente no mesmo campo.                                                                               |
| ITEMCEX-07 | Servidor | 3.5   | `clean()` na add usa `existing_code_conflict_message_html` (`format_html`), não texto plano.                                                                   |
| ITEMCEX-08 | UX       | 3.6   | Pós-POST com erro CE: remover `.existing-code-conflict-warning`; não repor amarelo; vincular handler no `errorlist` servidor.                                  |
| ITEMCEX-09 | UX       | 3.7   | Ao resolver CE sem POST: limpar alerta/erro CE e banner «Por favor, corrija…» se sem outros erros (`onExistingCodeConflictResolved` + `syncFormErrorSummary`). |
| ITEMCEX-10 | Submit   | 3.8   | Cliente: antes do POST, após `syncHierarchyFromCode('submit')`, consultar endpoint; `has_conflict` → erro vermelho e cancelar submit.                          |
| ITEMCEX-11 | Próximo  | 4.1   | «Clique aqui» reutiliza protocolo de próximo código de `spec_itemClassificacao_criar_filho.md`.                                                                |
| ITEMCEX-12 | Próximo  | 4.2   | Após próximo código: pipeline completo (nível, classificação, **P-mãe**, validações) — não atalho parcial.                                                     |
| ITEMCEX-13 | Vigência | 5.1   | Vigência efetiva do formulário (par início/fim; fallbacks alinhados a lookups/sugestão); comparação **(T7)**.                                                  |
| ITEMCEX-14 | Vigência | 5.2   | Mudança de datas reavalia CE do `receita_cod` atual; remove ou mantém alerta conforme resultado.                                                               |
| ITEMCEX-15 | API      | 6.1   | `lookup-existing-code-conflict/`: `ok: true`, `has_conflict: true` + `message_html`, `conflict` (CE★), `code_digits`, `code_display`.                          |
| ITEMCEX-16 | API      | 6.2   | Sem conflito: `ok: true`, `has_conflict: false`.                                                                                                               |
| ITEMCEX-17 | API      | 6.3   | Erro técnico: `ok: false`, `message`.                                                                                                                          |
| ITEMCEX-18 | UX       | 7.1   | Alerta: `messagelist existing-code-conflict-warning` + `li.warning`; erro: `errorlist` com mesmo HTML interno.                                                 |
| ITEMCEX-19 | UX       | 7.2   | Mensagem não deve «piscar» sem mudança real dos critérios CE.                                                                                                  |
| ITEMCEX-20 | UX       | 7.3   | Link do código: nova aba; próximo código: mesma página.                                                                                                        |
| ITEMCEX-21 | Submit   | 8.1   | Ordem: após validações de formato/hierarquia → CE → cancelar ou continuar.                                                                                     |
| ITEMCEX-22 | Submit   | 8.2   | Cliente antecipa bloqueio; servidor repete em `clean()` (defesa em profundidade).                                                                              |
| ITEMCEX-23 | Decisão  | 9     | **DP1:** edição = alerta; submit = erro bloqueante.                                                                                                            |
| ITEMCEX-24 | Decisão  | 9     | **DP2:** fragmento HTML único; muda só container (amarelo vs vermelho).                                                                                        |
| ITEMCEX-25 | Decisão  | 9     | **DP3:** link do conflito em nova aba.                                                                                                                         |
| ITEMCEX-26 | Decisão  | 9     | **DP4:** próximo código no formulário atual com pipeline completo.                                                                                             |
| ITEMCEX-27 | Decisão  | 9     | **DP5:** mensagem referencia apenas **CE★**.                                                                                                                   |
| ITEMCEX-28 | Decisão  | 9     | **DP6:** resolver CE localmente remove banner global se sem outros erros.                                                                                      |
| ITEMCEX-29 | Teste    | 10    | Casos § **10** **devem** ser respeitados (alerta, vigência, submit, próximo código, paridade).                                                                 |

**Índice por tema:**

| Tema     | IDs                                              |
| -------- | ------------------------------------------------ |
| Termo    | ITEMCEX-01, ITEMCEX-02                           |
| Detecção | ITEMCEX-03                                       |
| Mensagem | ITEMCEX-04                                       |
| Submit   | ITEMCEX-05, ITEMCEX-10, ITEMCEX-21, ITEMCEX-22   |
| UX       | ITEMCEX-06 … ITEMCEX-09, ITEMCEX-18 … ITEMCEX-20 |
| Próximo  | ITEMCEX-11, ITEMCEX-12                           |
| Vigência | ITEMCEX-13, ITEMCEX-14                           |
| API      | ITEMCEX-15 … ITEMCEX-17                          |
| Decisão  | ITEMCEX-23 … ITEMCEX-28                          |
| Teste    | ITEMCEX-29                                       |

---

## Escopo

| Inclui (v1)                              | Fora de escopo (v1)                                |
| ---------------------------------------- | -------------------------------------------------- |
| Add admin; campo `receita_cod`           | Change — `spec_itemClassificacao_editar_codigo.md` |
| Alerta amarelo + erro vermelho no submit | Alterar algoritmo canônico de próximo código       |
| Link CE★ nova aba; «Clique aqui» local   | Regras de unicidade além do bloqueio aqui definido |
| Desempate **CE★**                        |                                                    |

---

## 2. Terminologia **(ITEMCEX-01**, **ITEMCEX-02)**

- **(T6)** / **(T7):** ver `spec_itemClassificacao_criar_filho.md`.
- **CE (ITEMCEX-01):** `receita_cod` normalizado igual; `data_registro_fim = sentinela`; **(T7)** com vigência efetiva do formulário.
- **CE★ (ITEMCEX-02):** entre CE, ordenar por `-data_vigencia_inicio`, `-data_registro_inicio`, `-pk`.

---

## 3. Regras funcionais

### 3.1 Detecção na edição **(ITEMCEX-03)**

Ao preencher/alterar `receita_cod` na add: se **CE** → alerta amarelo referenciando **CE★**; senão → remover aviso CE.

### 3.2 Mensagem canônica **(ITEMCEX-04)**

Um único fragmento HTML no servidor (`existing_code_conflict_message_html`).

Formato orientativo:

> Já existe o [<código>](<link-change>) com vigência de <DD/MM/YYYY> até <DD/MM/YYYY>. [Clique aqui](ação-local) para ir para o próximo código disponível ou ajuste a data de vigência do código atual.

- Link do código: `target="_blank"`, `rel="noopener noreferrer"`.
- «Clique aqui»: `class="js-existing-code-conflict-next"`, `href="#"`, ação local.
- Alerta: `<ul class="messagelist existing-code-conflict-warning"><li class="warning">`.

Persiste enquanto **CE** em edição; some quando vigência/código deixam de conflitar ou após próximo código sem conflito.

### 3.3 Submit com CE **(ITEMCEX-05)**

Bloquear gravação; mesmo HTML em erro vermelho em `receita_cod`; manter links e «Clique aqui».

### 3.4 Exclusividade alerta × erro **(ITEMCEX-06)**

| Fase                  | Exibição                       |
| --------------------- | ------------------------------ |
| Edição                | Somente alerta amarelo         |
| Submit bloqueado      | Somente erro vermelho          |
| CE resolvido          | Nenhuma mensagem CE            |
| Novo CE após correção | Somente alerta até novo submit |

Ao passar para erro de submit, remover `.existing-code-conflict-warning`.

### 3.5 `clean()` na add **(ITEMCEX-07)**

`ItemClassificacaoForm.clean()` usa `existing_code_conflict_message_html` via `format_html`.

### 3.6 Pós-submit / `init` **(ITEMCEX-08)**

Add recarregada com `errorlist` CE em `receita_cod`:

1. Remover `.existing-code-conflict-warning`.
2. **Não** chamar `scheduleExistingCodeConflictCheck` para repor amarelo.
3. Vincular `js-existing-code-conflict-next` no `errorlist` do servidor.

### 3.7 Banner global **(ITEMCEX-09)**

Resolver CE sem novo POST → remover alerta, erro CE e `errorlist` com `js-existing-code-conflict-next`; se sem outros `ul.errorlist`, remover `p.errornote` (cliente e Django).

### 3.8 Bloqueio no submit (cliente) **(ITEMCEX-10)**

Após `syncHierarchyFromCode('submit')`: consultar endpoint; `has_conflict` → erro vermelho com `message_html`, cancelar POST. Servidor repete **(ITEMCEX-22)**.

---

## 4. Próximo código disponível

### 4.1 Reuso do protocolo **(ITEMCEX-11)**

«Clique aqui» delega a `spec_itemClassificacao_criar_filho.md`.

### 4.2 Pipeline completo **(ITEMCEX-12)**

Após aplicar próximo código:

- reconciliar `nivel_id` e `classificacao_id` quando aplicável;
- executar **P-mãe** e autocompletes de `spec_itemClassificacao_criar_nome.md`;
- reaplicar validações de código e hierarquia do fluxo normal.

---

## 5. Vigência de referência

### 5.1 Fonte **(ITEMCEX-13)**

1. `data_vigencia_inicio` / `data_vigencia_fim` do formulário quando preenchidos;
2. fallbacks normativos do fluxo (ex.: mãe), alinhados a módulos de lookup/sugestão;
3. comparação sempre por **(T7)**.

### 5.2 Reatividade **(ITEMCEX-14)**

Alteração de datas → reavaliar CE para `receita_cod` atual; atualizar ou remover alerta/erro conforme resultado.

---

## 6. Contrato API `lookup-existing-code-conflict/`

### 6.1 Com conflito **(ITEMCEX-15)**

```json
{
  "ok": true,
  "has_conflict": true,
  "code_digits": "...",
  "code_display": "...",
  "message_html": "<fragmento ITEMCEX-04>",
  "message": "texto sem tags",
  "conflict": {
    "pk": "...",
    "display_label": "...",
    "link_url": "...",
    "vigencia_inicio": "...",
    "vigencia_fim": "..."
  }
}
```

### 6.2 Sem conflito **(ITEMCEX-16)**

`{ "ok": true, "has_conflict": false }`

### 6.3 Erro técnico **(ITEMCEX-17)**

`{ "ok": false, "message": "..." }`

---

## 7. UX e renderização **(ITEMCEX-18**–**ITEMCEX-20)**

- **(ITEMCEX-18):** classes de alerta/erro; mesmo HTML interno.
- **(ITEMCEX-19):** sem flicker sem mudança de critérios CE.
- **(ITEMCEX-20):** código conflitante → nova aba; próximo código → mesma página.

---

## 8. Pipeline de submit **(ITEMCEX-21**, **ITEMCEX-22)**

**(ITEMCEX-21):** após validações de formato e hierarquia existentes → verificar CE → cancelar ou continuar.

**(ITEMCEX-22):** cliente antecipa; servidor valida em `clean()` antes de persistir.

---

## 9. Decisões de produto **(ITEMCEX-23**–**ITEMCEX-28)**

| ID         | Decisão                                                |
| ---------- | ------------------------------------------------------ |
| ITEMCEX-23 | Severidade dual: alerta na edição, erro no submit      |
| ITEMCEX-24 | Fragmento HTML único                                   |
| ITEMCEX-25 | Link do conflito em nova aba                           |
| ITEMCEX-26 | Próximo código local com pipeline completo             |
| ITEMCEX-27 | Exibir apenas **CE★**                                  |
| ITEMCEX-28 | Banner global removido ao resolver CE sem outros erros |

---

## 10. Casos de teste **(ITEMCEX-29)**

1. Código com CE → alerta amarelo com link + «Clique aqui».
2. Ajuste de vigência elimina CE → aviso some sem submit.
3. Submit com CE → erro vermelho; sem gravação.
4. «Clique aqui» → pipeline completo (`nivel_id`, classificação, nomenclatura).
5. Link do código → change em nova aba.
6. Múltiplos CE → mensagem só **CE★**.
7. Alterar só datas → reprocessa CE.
8. Sem CE → sem mensagem.
9. POST direto sem JS com CE → backend bloqueia.
10. Resolver CE após submit bloqueado → some erro e banner se sem outros erros.

---

## Manutenção

Alterações em lookup, vigência, desempate **CE★** ou integração com próximo código **devem** manter alinhados:

- `classification_item_existing_code.py`;
- `change_form.html` (mensagens e preenchimento programático);
- validações cliente e `ItemClassificacaoForm.clean()`.
