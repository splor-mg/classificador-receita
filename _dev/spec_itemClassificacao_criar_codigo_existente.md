# Item de classificação — criação (add): alerta/erro para código já existente e ação "próximo código"

Esta especificação define o comportamento na tela **add** de `ItemClassificacao` quando o usuário informa em `receita_cod` um código que **já existe ativo** e com vigência **sobreposta** à vigência do formulário.

O objetivo é orientar o usuário sem bloquear a edição inicial (estado de **alerta**), permitindo ajuste de vigência no próprio formulário; e, no **submit**, bloquear a gravação caso o conflito permaneça (estado de **erro**).

**Implementação (repositório):** `apps/core/classification_item_existing_code.py`; endpoint
`lookup-existing-code-conflict/` em `ItemClassificacaoAdmin`; validação na add em
`ItemClassificacaoForm.clean()`; alerta amarelo e reavaliação por vigência em
`change_form.html` (`scheduleExistingCodeConflictCheck`, classe
`existing-code-conflict-warning`).

**Referências de contexto já implementado:**

- `_dev/spec_itemClassificacao_criar_filho.md` (protocolo canônico de "próximo código disponível", conceitos **T6/T7**, notificações, integração com `change_form.html`);
- `_dev/spec_itemClassificacao_foreignKeys_lookup.md` (padrão visual/contratual de mensagens inline e links semânticos no admin);
- `_dev/spec_itemClassificacao_criar_nome.md` (autocompletes e protocolo de nomenclatura após alteração de código/mãe);
- `_dev/spec_itemClassificacao_validar_hierarquia.md` (pipeline de validações no submit e padrão de mensagens de bloqueio).

---

## Objetivo

Na add de `ItemClassificacao`:

1. detectar conflito quando `receita_cod` informado coincide com registro já existente, ativo e com vigência sobreposta;
2. exibir **mensagem de alerta amarela inline** associada ao campo de código;
3. oferecer dois caminhos no próprio alerta:
   - abrir o registro conflitante em **nova aba**;
   - aplicar "próximo código disponível" **na própria página**, reutilizando o protocolo de sugestão já definido;
4. no submit, se o conflito persistir, transformar o estado em **erro vermelho** e bloquear gravação.

---

## Escopo e fora de escopo

### Escopo (v1)

- Tela **add** de `ItemClassificacao` no admin.
- Campo **Código Canônico da Natureza de Receita** (`receita_cod`).
- Estado visual **alerta** (amarelo) durante edição.
- Estado visual **erro** (vermelho) no submit com conflito remanescente.
- Link do código conflitante para tela change em nova aba.
- Ação "Clique aqui" para próximo código disponível no mesmo formulário.
- Escolha do conflito por registro ativo mais recente quando houver múltiplos.

### Fora de escopo (v1)

- Fluxos da tela **change** (já cobertos por `_dev/spec_itemClassificacao_editar_codigo.md`).
- Alteração do algoritmo canônico de "próximo código disponível" (reuso semânticamente idêntico ao `_dev/spec_itemClassificacao_criar_filho.md`).
- Mudança de regras de domínio de unicidade/bitemporalidade no backend além do bloqueio no submit aqui definido.

---

## Terminologia (alinhada às specs existentes)

- **(T6) Registro ativo:** `data_registro_fim = TRANSACTION_TIME_SENTINEL`.
- **(T7) Sobreposição de vigência (inclusiva):** `inicio_form <= fim_item` e `fim_form >= inicio_item`.
- **Conflito de código existente (CE):** existe ao menos um registro com:
  - `receita_cod` igual ao código informado (normalizado em dígitos),
  - `data_registro_fim = sentinela`,
  - vigência em **(T7)** com a vigência efetiva do formulário.
- **Conflito mais recente (CE★):** entre conflitos CE, selecionar o mais recente por:
  `-data_vigencia_inicio`, depois `-data_registro_inicio`, depois `-pk`.

---

## Regra funcional principal

### (CE-1) Detecção durante preenchimento

Ao preencher/alterar `receita_cod` na add (blur/change e eventos equivalentes de validação já existentes), o sistema deve resolver se há **CE** para a vigência efetiva do formulário.

Se houver CE:

- renderizar mensagem **amarela** inline no campo `receita_cod`;
- a mensagem referencia apenas **CE★**;
- manter a mensagem enquanto o conflito permanecer.

Se não houver CE:

- remover aviso/erro CE do campo.

### (CE-2) Mensagem canônica (alerta e erro)

Existe **um único fragmento HTML** de mensagem CE, gerado no servidor
(`existing_code_conflict_message_html`) e reutilizado em todos os canais.

Formato orientativo:

> Já existe o [<código informado>](<link-change>) com vigência de <data-início> até <data-fim>. [Clique aqui](ação-local-próximo-código) para ir para o próximo código disponível ou ajuste a data de vigência do código atual.

Requisitos do fragmento:

- `[<código informado>]` abre em **nova aba** (`target="_blank"` e `rel="noopener noreferrer"`).
- `[Clique aqui]` usa `class="js-existing-code-conflict-next"`, `href="#"` e ação local (sem navegação externa).
- Datas em `DD/MM/YYYY` no texto visível.

**Modo alerta (edição):** renderizar o fragmento em `<ul class="messagelist existing-code-conflict-warning">` com `<li class="warning">`.

O aviso deve persistir enquanto houver CE em edição e só desaparecer quando:

- vigência e/ou código deixarem de conflitar; ou
- usuário acionar "próximo código" e o novo resultado deixar de conflitar.

### (CE-3) Transição para erro no submit

No submit da add:

- se CE ainda existir, bloquear gravação;
- exibir o **mesmo fragmento HTML** de **(CE-2)** como **erro vermelho** em `receita_cod` (`errorlist` do Django no servidor; `errorlist` cliente antes do POST em **(CE-5)**);
- **manter** link do código e ação "Clique aqui" com o mesmo comportamento.

### (CE-3a) Exclusividade visual alerta × erro

**Não** exibir alerta amarelo CE e erro vermelho CE **simultaneamente** no mesmo campo.

| Fase | Exibição |
| ---- | -------- |
| Edição (sem submit pendente) | Somente alerta amarelo |
| Submit bloqueado (cliente ou POST com erro) | Somente erro vermelho (com links) |
| Conflito resolvido | Nenhuma mensagem CE |
| Novo conflito após correção | Somente alerta amarelo (até novo submit) |

Ao passar para erro de submit, o cliente **deve remover** `.existing-code-conflict-warning`.

### (CE-3b) Erro no servidor (`clean()`)

`ItemClassificacaoForm.clean()` na add deve usar `existing_code_conflict_message_html` (HTML seguro via `format_html`), **não** texto plano alternativo.

### (CE-3c) Pós-submit / `init`

Quando a add recarregar com `errorlist` de CE em `receita_cod` (POST rejeitado):

1. **remover** qualquer `.existing-code-conflict-warning`;
2. **não** chamar `scheduleExistingCodeConflictCheck` para repor o amarelo;
3. **vincular** `js-existing-code-conflict-next` no `errorlist` do servidor (mesmo handler do alerta).

### (CE-3d) Banner global «Por favor, corrija o erro abaixo.»

Quando o submit é bloqueado por CE (cliente ou POST), o admin exibe o banner genérico (`p.errornote`) no topo do formulário, além do erro em `receita_cod`.

Ao **resolver** o conflito CE **sem novo POST** (próximo código, ajuste de vigência ou código que deixe de conflitar):

1. remover alerta amarelo, erro vermelho CE no campo e `errorlist` do servidor que contenha `js-existing-code-conflict-next`;
2. se **não** restar nenhum `ul.errorlist` com itens no formulário, remover também:
   - `p.errornote.client-submit-errornote` (banner injetado no submit cliente);
   - `p.errornote` do Django no topo do formulário (banner após POST rejeitado).

Se ainda houver outros erros de campo no formulário, o banner global **permanece**.

Implementação: `onExistingCodeConflictResolved()` + `syncFormErrorSummary(form)` no `change_form.html`.

### (CE-5) Bloqueio no submit (cliente)

Antes do POST nativo, após `syncHierarchyFromCode('submit')`:

1. consultar o endpoint CE;
2. se `has_conflict` → remover alerta amarelo, exibir erro vermelho com `message_html` e **cancelar** submit;
3. servidor repete validação em `clean()` (**CE-12**).

---

## Reuso do protocolo "próximo código disponível"

### (CE-4) Ação "Clique aqui"

Ao acionar "próximo código disponível", reutilizar o protocolo de `_dev/spec_itemClassificacao_criar_filho.md` para cálculo e aplicação de código sugerido.

### (CE-5) Efeitos obrigatórios após aplicar próximo código

A aplicação deve disparar os mesmos efeitos normativos do preenchimento programático de código na add:

- atualização/reconciliação de `nivel_id`;
- atualização/reconciliação de `classificacao_id` quando aplicável ao fluxo vigente;
- execução do protocolo de nomenclatura/autocomplete vinculado ao código/mãe (ex.: `P-mãe` e correlatos de `_dev/spec_itemClassificacao_criar_nome.md`);
- reaplicação das validações de `receita_cod` e hierarquia que normalmente rodam após mudança do código.

Em outras palavras, "próximo código" **não** é atalho parcial: ele deve equivaler a um preenchimento de código completo no mesmo pipeline já existente.

---

## Vigência de referência para detecção de conflito

### (CE-6) Fonte de vigência

Usar a vigência efetiva já adotada nos fluxos de lookup/sugestão:

1. se formulário tiver `data_vigencia_inicio` e `data_vigencia_fim`, usar esse par;
2. onde houver fallback normativo de contexto no fluxo atual (ex.: mãe selecionada), respeitar a mesma regra já vigente no módulo correspondente;
3. comparação de conflito sempre por **(T7)**.

### (CE-7) Atualização reativa

Mudanças em `data_vigencia_inicio` e/ou `data_vigencia_fim` devem reavaliar CE para o `receita_cod` atual:

- conflito resolvido -> remover alerta/erro CE;
- conflito mantido -> manter (alerta em edição; erro no submit bloqueado).

---

## Contrato de dados (proposto)

Para manter paridade com endpoints existentes de lookup JSON:

- Pode-se adotar endpoint dedicado (ex.: `lookup-existing-code-conflict/`) ou ampliar endpoint já existente, desde que preserve contrato claro.

### Resposta com conflito (`ok: true`, `has_conflict: true`)

Campos recomendados:

- `ok: true`
- `has_conflict: true`
- `code_digits`
- `code_display`
- `message_html` — fragmento canônico **(CE-2)** (mesmo HTML do `clean()`)
- `message` — texto sem tags (fallback / acessibilidade)
- `conflict`:
  - `pk`
  - `display_label`
  - `link_url` (change URL do CE★)
  - `vigencia_inicio`
  - `vigencia_fim`

### Resposta sem conflito (`ok: true`, `has_conflict: false`)

- `ok: true`
- `has_conflict: false`

### Resposta de erro técnico (`ok: false`)

- `ok: false`
- `message` com causa (`vigência inválida`, `código inválido`, etc.).

---

## UX e renderização

### (CE-8) Padrão visual

- **Alerta:** `messagelist existing-code-conflict-warning` + `li.warning`.
- **Erro de submit:** `errorlist` (servidor ou `existing-code-conflict-submit-error` no cliente), **mesmo HTML** interno que o alerta.
- **Exclusividade:** ver **(CE-3a)**.

### (CE-9) Persistência de mensagem

A mensagem não deve "piscar" ou desaparecer por efeitos colaterais de polling/refresh sem mudança real dos critérios CE.

### (CE-10) Abertura de link

- Link do código conflitante: **nova aba**.
- Ação "próximo código": **mesma aba/página**, sem navegar.

---

## Regras de bloqueio no submit

### (CE-11) Ordem no pipeline

Na submissão da add, após validações de formato de código e pré-condições de hierarquia já existentes:

1. verificar CE com dados finais do formulário;
2. se CE -> erro em `receita_cod` e **cancelar submit**;
3. se não CE -> fluxo normal continua.

### (CE-12) Coerência servidor + cliente

- Cliente pode antecipar bloqueio para UX imediata.
- Servidor deve repetir validação CE antes de persistir (defesa em profundidade).

---

## Casos de teste recomendados

1. **Alerta básico:** informar código existente com CE -> aparece aviso amarelo com link + "Clique aqui".
2. **Ajuste de vigência resolve:** manter código, alterar datas para eliminar sobreposição -> aviso desaparece sem submit.
3. **Submit bloqueado:** manter CE e clicar salvar -> mensagem vira erro vermelho e gravação não ocorre.
4. **Próximo código aplica pipeline completo:** clicar "Clique aqui" -> novo código aplicado e autocompletes (`nivel_id`, `classificacao_id`, nomenclatura) executados.
5. **Link em nova aba:** clicar no código do alerta abre change em aba nova.
6. **Múltiplos conflitos:** quando houver vários CE, mensagem referencia apenas CE★ (mais recente pelo desempate normativo).
7. **Reavaliação por data:** alterar somente `data_vigencia_inicio`/`fim` reprocessa CE do código atual.
8. **Sem conflito:** código inexistente ou sem sobreposição -> nenhuma mensagem CE.
9. **Paridade cliente/servidor:** forçar submit direto (sem JS) com CE -> backend também bloqueia.
10. **Banner após resolver CE:** submit bloqueado por CE -> «Clique aqui» ou ajuste que elimine CE -> some erro em `receita_cod` **e** o banner «Por favor, corrija o erro abaixo.» (se não houver outros erros).

---

## Decisões de produto registradas nesta spec

- **DP1. Severidade dual:** edição = alerta; submit = erro bloqueante.
- **DP2. Fragmento único:** alerta e erro usam o mesmo `message_html`; muda só o container (amarelo vs vermelho) e a exclusividade **(CE-3a)**.
- **DP3. Navegação:** link do código conflitado abre em nova aba.
- **DP4. Ação local:** "próximo código" atua no formulário atual e reaproveita pipeline completo já existente.
- **DP5. Múltiplos conflitos:** exibir o conflito ativo sobreposto mais recente (CE★).
- **DP6. Banner global:** ao resolver CE localmente, retirar «Por favor, corrija o erro abaixo.» se não houver outros erros (**CE-3d**).

---

## Manutenção

Qualquer mudança de contrato de lookup, critérios de vigência, ordenação de conflito CE★ ou integração com o protocolo de "próximo código" deve manter este documento alinhado a:

- módulo de lookup/sugestão de código de `ItemClassificacao`;
- JavaScript do `change_form.html` que orquestra mensagens e preenchimentos programáticos;
- validações de submit no cliente e no servidor.
