# Criação no Admin: `receita_nome` e modos de radical

Fluxo do formulário **add** de `ItemClassificacao`: campo `receita_nome`, três modos de radical, protocolo **P-mãe**, abreviação **A1–A9** e guardrails **G0**/**G1**. **Não substitui** `spec_lista_abreviacoes.md` (léxico) nem fluxos da **change** (**ITEMEC**, **DJANGO-28**).

## Objetivo

Definir como o projeto **deve** orientar nomenclatura na criação de itens: sugestão a partir do item mãe e `receita_cod`, modos Abreviado/Completo/Sem base, validação antes de gravar e paridade do sufixo `" - "` **(ITEMNOM-06)**.

Premissa: `code_name.js`, `code_name_messages.py`, `code_name_validation.py`, `ItemClassificacaoAdminForm.receita_nome_base_mode`, `admin.py` (contexto + *media*), `change_form.html` (`syncHierarchyFromCode`, `validateCodeNameOnSubmit`).

## Referências

- `apps/core/static/core/js/code_name.js`, `code_name_messages.py`, `code_name_validation.py`
- `apps/core/code_name_connectives.py` — `LEXICO_CONNECTIVOS_FIXOS`
- `apps/core/alias_lexico_service.py`, `alias_lexico_infer.py`
- [`spec_lista_abreviacoes.md`](spec_lista_abreviacoes.md) — segmentos, abreviações, conectivos
- [`spec_itemClassificacao_foreignKeys_lookup.md`](spec_itemClassificacao_foreignKeys_lookup.md) — `parent.name` no payload
- [`spec_itemClassificacao_criar_filho.md`](spec_itemClassificacao_criar_filho.md) — **(G5)**, sugestão de código filho
- [`spec_itemClassificacao_formulario.md`](spec_itemClassificacao_formulario.md) — UI do formulário
- [`spec_django.md`](spec_django.md) — **DJANGO-25**–**28** (pipeline bitemporal)
- [`spec_classificador-receita.md`](spec_classificador-receita.md) § **Convenções** — prefixo `ITEMNOM`

Termos *deve* / *não deve* / *pode* conforme RFC 2119 (ver `_dev/spec_conventions.md` **Referências**).

**Migração de símbolos legados** (índice completo no corpo; amostra):

| Legado                         | ID atual                    |
| ------------------------------ | --------------------------- |
| `(N5)` sufixo canônico         | `ITEMNOM-06`                |
| `(N7)` separador flexível      | `ITEMNOM-07`                |
| `P-mãe.*`, `P-orq.*`, `P-G5.*` | `ITEMNOM-10`–`ITEMNOM-28`   |
| `M1.*`                         | `ITEMNOM-30`–`ITEMNOM-35`   |
| `M2.*`                         | `ITEMNOM-36`–`ITEMNOM-39`   |
| `B0.*`                         | `ITEMNOM-40`–`ITEMNOM-43`   |
| `G0.*`                         | `ITEMNOM-50`–`ITEMNOM-54`   |
| `G1.*`                         | `ITEMNOM-55`–`ITEMNOM-65`   |
| `A1`–`A9`, `A9.3`              | `ITEMNOM-80`–`ITEMNOM-95`   |
| `I1`–`I5`                      | `ITEMNOM-96`–`ITEMNOM-100`  |
| `E-change.*`                   | `ITEMNOM-101`–`ITEMNOM-104` |
| `D1`–`D10`                     | `ITEMNOM-110`–`ITEMNOM-119` |

## Como citar este documento

| Mecanismo          | Uso                                                                  |
| ------------------ | -------------------------------------------------------------------- |
| **Seção numerada** | `§ N` / `§ N.M` — navegação neste arquivo.                           |
| **ID normativo**   | `ITEMNOM-NN` — citação estável.                                      |
| **Prefixo**        | `ITEMNOM` — ver § **Convenções** em `spec_classificador-receita.md`. |

**Índice de IDs normativos deste arquivo:**

| ID          | Tema         | Seção | Resumo                                                                                                                                |
| ----------- | ------------ | ----- | ------------------------------------------------------------------------------------------------------------------------------------- |
| ITEMNOM-01  | UI           | 2     | Ordem dos rádios (add): **Abreviado** → **Completo** → **Sem Nome Base**.                                                             |
| ITEMNOM-02  | UI           | 2     | `name` HTML dos rádios **distinto** de `receita_nome_base_mode` (ex.: `__code_name_base_mode_ui`).                                    |
| ITEMNOM-03  | POST         | 2     | `base_pai_abrev` — radical **A1–A8** + **ITEMNOM-06**.                                                                                |
| ITEMNOM-04  | POST         | 2     | `base_pai_completo` — `nome_mae` + **ITEMNOM-06**.                                                                                    |
| ITEMNOM-05  | POST         | 2     | `sem_base` — modo sem radical imposto.                                                                                                |
| ITEMNOM-06  | Notação      | 3     | **(N5)** `sufixo_canônico` = literal `" - "` (espaço, hífen ASCII, espaço) em sugestões automáticas.                                  |
| ITEMNOM-07  | Notação      | 3     | **(N7)** separador flexível: espaços opcionais + `-`/`–`/`—` + espaços; usado em **M2**, **G1**.                                      |
| ITEMNOM-08  | Notação      | 3     | **(N6)** `norm`: trim + `casefold`; sem remover acentos (**ITEMNOM-110**).                                                            |
| ITEMNOM-09  | Notação      | 3     | **(N8)** `norm_colapso_espacos`: fallback após **(N6)** (**ITEMNOM-114**).                                                            |
| ITEMNOM-10  | P-mãe        | 4     | **P1:** após resolver mãe com sucesso via `receita_cod`, disparar **P-mãe** (não **M1.4**).                                           |
| ITEMNOM-11  | P-mãe        | 4.1   | Obter `nome_mae` (**ITEMNOM-17**); calcular radical **A1–A8**.                                                                        |
| ITEMNOM-12  | P-mãe        | 4.1   | Atualizar `receita_nome` = `radical_abreviado + ITEMNOM-06`; **ITEMNOM-88** preserva complemento após **ITEMNOM-07**.                 |
| ITEMNOM-13  | P-mãe        | 4.1   | Marcar rádio **Abreviado**; `receita_nome_base_mode` = `base_pai_abrev`.                                                              |
| ITEMNOM-14  | P-mãe        | 4.1   | **Sobrescrever** modo anterior (Completo/Sem base/Abreviado).                                                                         |
| ITEMNOM-15  | P-mãe        | 4.1   | **Completo** só por clique explícito (**ITEMNOM-30**); **Sem base** não permanece após **P-mãe**.                                     |
| ITEMNOM-16  | Orquestração | 4.2   | **P-orq.1:** toda resolução bem-sucedida de mãe após `receita_cod` executa **P-mãe**.                                                 |
| ITEMNOM-17  | Orquestração | 4.2   | **P-orq.2:** `nome_mae` = `parent.name` no JSON, senão rótulo DOM (**M1.2**).                                                         |
| ITEMNOM-18  | Orquestração | 4.2   | **P-orq.3:** invocar **P-mãe** explicitamente (`applyCodeNameAfterParentResolved`); não só `change` no hidden.                        |
| ITEMNOM-19  | Orquestração | 4.2   | **P-orq.4:** reexecutar se `parent.pk` ou `nome_mae` (trim+casefold) mudou.                                                           |
| ITEMNOM-20  | P-mãe        | 4.1   | **P-mãe.2-bis:** sugestão literal da mãe anterior (**G1.5.a**) → não preservar como complemento (**ITEMNOM-89**).                     |
| ITEMNOM-21  | G5           | 4.3   | Durante **(G5)**, **P-mãe** **suspenso** até fechar modal.                                                                            |
| ITEMNOM-22  | G5           | 4.3   | Tabela pós-modal: quando re-aplicar **P-mãe** conforme ação do usuário.                                                               |
| ITEMNOM-23  | G5           | 4.3   | **P-G5.1:** Cancelar/erro — não alterar `nivel_id` nem `classificacao_id`.                                                            |
| ITEMNOM-24  | G5           | 4.3   | **P-G5.2:** **Manter Atual** — **P-mãe** para nova mãe; código inalterado.                                                            |
| ITEMNOM-25  | G5           | 4.3   | **P-G5.3:** listener `change` respeita suspensão durante **(G5)**.                                                                    |
| ITEMNOM-26  | G5           | 4.3   | **P-G5.4:** reversão usa `nome_mae` do snapshot ou rótulo re-fetch.                                                                   |
| ITEMNOM-30  | Completo     | 5     | **M1.1:** com modo Completo, `receita_nome` **deve começar** por `nome_mae + ITEMNOM-06`.                                             |
| ITEMNOM-31  | Completo     | 5     | **M1.2:** extrair `nome_mae` do rótulo de `parent_item_id` (após `" - "`).                                                            |
| ITEMNOM-32  | Completo     | 5     | **M1.3/M1.5:** troca explícita via algoritmo **ITEMNOM-94** (**A9.3**).                                                               |
| ITEMNOM-33  | Completo     | 5     | **M1.4:** **não** aplicar no repovoamento automático (**P-mãe**).                                                                     |
| ITEMNOM-36  | Sem base     | 6     | **M2.1:** remover radical conhecido + **ITEMNOM-07** do início de `receita_nome`.                                                     |
| ITEMNOM-37  | Sem base     | 6     | **M2.2–M2.4:** fallback **ITEMNOM-06** estrito; aviso `remove_base_prefix_mismatch`; `sem_base`.                                      |
| ITEMNOM-40  | Abreviado    | 7     | **B0:** primeiro rádio na UI; radical via **ITEMNOM-80**–**ITEMNOM-87**; sugestão com **ITEMNOM-06** (**B0.3**).                      |
| ITEMNOM-50  | G0           | 8.1   | **Add:** `trim(receita_nome)` vazio → bloquear (**todos** os modos).                                                                  |
| ITEMNOM-51  | G0           | 8.1   | Cliente: **G0** antes de **G1** em `validateCodeNameOnSubmit`.                                                                        |
| ITEMNOM-52  | G0           | 8.1   | Servidor: `clean()` add com mensagem `receita_nome_vazio_error`.                                                                      |
| ITEMNOM-55  | G1           | 8.2   | **G1.2:** `trim(n)` termina com **ITEMNOM-07** → bloquear em **todos** os modos (incl. `sem_base`).                                   |
| ITEMNOM-56  | G1           | 8.2   | Cliente + servidor; mensagem **G1.5.a** (sugestão literal) vs **G1.5.b** (traço pendurado).                                           |
| ITEMNOM-57  | G1           | 8.2   | `n === b` sem traço final → **permitido** (**ITEMNOM-116** regressão).                                                                |
| ITEMNOM-60  | G2           | 8.3   | Mensagem informativa azul enquanto **G1.2** verdadeiro; textos **G2.1**/**G2.2**.                                                     |
| ITEMNOM-61  | G3           | 8.4   | `parent_item_id` vazio → limpar rádios e estado.                                                                                      |
| ITEMNOM-62  | G4           | 8.5   | Reidratar após POST com erro.                                                                                                         |
| ITEMNOM-63  | G5           | 8.6   | Naming após código/hierarquia, antes de submit.                                                                                       |
| ITEMNOM-64  | G6           | 8.7   | Alerta `termo_nome` duplicado no léxico (**A3.2**, **A1.3**); não bloqueia submit.                                                    |
| ITEMNOM-80  | A1–A8        | 9     | Léxico ativo; ordenação **A2**; match exato **A3**; substituição **A4**; **A6** conectivos; **A7** + **ITEMNOM-06**; fallback **A8**. |
| ITEMNOM-88  | A9           | 9     | **A9.2:** preservar complemento após **ITEMNOM-07** ao repor radical.                                                                 |
| ITEMNOM-89  | A9           | 9     | **A9.2-bis** / **ITEMNOM-20:** troca de mãe com sugestão literal anterior.                                                            |
| ITEMNOM-94  | A9.3         | 9     | Algoritmo 4 passos na troca explícita Completo ↔ Abreviado (**ITEMNOM-32**).                                                          |
| ITEMNOM-96  | Impl.        | 10    | **I1:** **A1–A8** em Python com testes; **I4** predicados G0/G1 em `code_name_validation.py`.                                         |
| ITEMNOM-97  | Impl.        | 10    | **I2–I3:** endpoint staff; cliente acrescenta **ITEMNOM-06** se servidor retorna só radical.                                          |
| ITEMNOM-100 | Impl.        | 10    | **I5:** após hierarquia, chamar **ITEMNOM-18** com `parent.name`.                                                                     |
| ITEMNOM-101 | Change       | 11    | **E-change.1:** ocultar `receita_nome_base_mode` na change.                                                                           |
| ITEMNOM-102 | Change       | 11    | **E-change.2:** POST change sem `receita_nome_base_mode`.                                                                             |
| ITEMNOM-103 | Change       | 11    | **E-change.3:** ver **DJANGO-25**–**26**.                                                                                             |
| ITEMNOM-104 | Change       | 11    | **E-change.4:** **G0**/**G1** exclusivos do add.                                                                                      |
| ITEMNOM-110 | Decisão      | 12    | **D1:** **(N6)** sem remover acentos na v1.                                                                                           |
| ITEMNOM-111 | Decisão      | 12    | **D5:** **P-mãe** sempre força Abreviado; Completo só clique.                                                                         |
| ITEMNOM-116 | Decisão      | 12    | **D6:** **G1.2** único predicado; `n===b` sem traço permitido.                                                                        |
| ITEMNOM-119 | Teste        | 13    | Casos § **13** e lista em corpo original **devem** ser respeitados.                                                                   |

**Índice por tema:**

| Tema          | IDs                                            |
| ------------- | ---------------------------------------------- |
| UI / POST     | ITEMNOM-01 … ITEMNOM-05                        |
| Notação       | ITEMNOM-06 … ITEMNOM-09                        |
| P-mãe / G5    | ITEMNOM-10 … ITEMNOM-26                        |
| Modo Completo | ITEMNOM-30 … ITEMNOM-33                        |
| Sem base      | ITEMNOM-36 … ITEMNOM-37                        |
| Abreviado     | ITEMNOM-40                                     |
| Guardrails    | ITEMNOM-50 … ITEMNOM-64                        |
| Protocolo A   | ITEMNOM-80, ITEMNOM-88, ITEMNOM-89, ITEMNOM-94 |
| Implementação | ITEMNOM-96 … ITEMNOM-100                       |
| Change        | ITEMNOM-101 … ITEMNOM-104                      |
| Decisão       | ITEMNOM-110, ITEMNOM-111, ITEMNOM-116          |
| Teste         | ITEMNOM-119                                    |

---

## 1. Escopo
- **Escopo:** tela de **add**; `receita_nome`; `receita_nome_base_mode`; rádios; integração com preenchimento a partir de `receita_cod` / lookup do item mãe (**P-mãe**).
- **Escopo (validação):** **G0** (nome vazio no **add**, independente do rádio) e **G1** (`trim(receita_nome)` terminando com traço **(N7)** (**ITEMNOM-07**), em **todos** os modos do **add** — inclusive `sem_base`) no **cliente** (`validateCodeNameOnSubmit`) **e** no **servidor** (`ItemClassificacaoAdminForm.clean()`), com definições canônicas em **I4**.
- **Fora de escopo:** `INSERT` em `AliasLexico` a partir desta tela; alteração do seed.
- **Fora de escopo (tela de alteração — change view):** ver seção **«Escopo na tela de alteração (change view)»** logo abaixo. `receita_nome_base_mode`, rádios de modo e protocolos **P-mãe** / **A1–A9** / **G0** / **G1** **não** se aplicam à edição de um `ItemClassificacao` existente.

### Escopo na tela de alteração (change view)

A presente spec descreve o **protocolo de criação** (`add`) do nome da classificação. Em sua mesma essência, ela **não rege** a tela de alteração (`change`) de um `ItemClassificacao` já existente. Para manter a coerência entre código, UI e pipeline bitemporal de edição, observam-se as seguintes regras na tela de change:

- **ITEMNOM-101** (**E-change.1**). O `HiddenInput` `receita_nome_base_mode` **não deve** ser renderizado na change view. O template `change_form.html` já guarda a renderização com `{% if adminform.form.receita_nome_base_mode %}`; a implementação **deve** garantir que esse campo seja **removido** do form quando `instance.pk` existir (ex.: `self.fields.pop("receita_nome_base_mode", None)` no `__init__` de `ItemClassificacaoForm`).
- **ITEMNOM-102** (**E-change.2**). Como consequência de **E-change.1**, o POST de uma edição **não deve** conter `receita_nome_base_mode`. Se vier por algum motivo (campo legado, automação externa, *replays* de formulário), ele é tratado como ruído e **não** deve trafegar para o pipeline bitemporal.
- **ITEMNOM-103** (**E-change.3**). O *handler* bitemporal (`BitemporalChangeHandler._apply_user_edits`) e o serviço (`apply_bitemporal_update`) **devem** filtrar `new_values` para conter **apenas atributos concretos do model** (`Model._meta.concrete_fields`). Campos auxiliares de qualquer `ModelForm` (não só `receita_nome_base_mode`) **nunca** podem alcançar `Model.objects.create(**...)`, sob pena de `TypeError: <Model>() got unexpected keyword argument: '<campo>'`. Ver também a seção «Pipeline de atualização bitemporal — apenas campos do model» em [`spec_django.md`](spec_django.md) (**DJANGO-25**–**26**).
- **ITEMNOM-104** (**E-change.4**). **G0** e **G1** **são exclusivos do `add`**; na change view, a validação de `receita_nome` segue apenas os validators do model (`required`, `max_length`, etc.) e demais regras de domínio independentes do modo de radical.

---

### Specs e código relacionados

- **Lista de abreviações:** no modo **Abreviado**, aplicam-se, quando couber, as noções de *segmento*, *abreviação*, *sigla* e *conectivos* de [`spec_lista_abreviacoes.md`](spec_lista_abreviacoes.md). A lista fixa de conectivos (**fonte única**) está em `apps/core/code_name_connectives.py` (`LEXICO_CONNECTIVOS_FIXOS`; alias `NOME_CLASSIFICACAO_CONNECTIVOS_FIXOS`). O motor de inferência (`alias_lexico_infer.py`) importa a mesma lista — não duplicar.
- **Léxico ativo:** `queryset_alias_lexico_ativos()` e `iter_alias_lexico_ativos_ordenados()` em `apps/core/alias_lexico_service.py`.
- **Resolução do item mãe:** [`spec_itemClassificacao_foreignKeys_lookup.md`](spec_itemClassificacao_foreignKeys_lookup.md) (rótulo `receita_cod - receita_nome` para extrair `nome_mae`).
- **Formulário admin (UI):** [`spec_itemClassificacao_formulario.md`](spec_itemClassificacao_formulario.md) (largura de `receita_cod`; limpar formulário na add).

---

## 2. Interface e valores POST (**ITEMNOM-01**–**ITEMNOM-05**)

### 2.1 Ordem dos rádios (**ITEMNOM-01**, **ITEMNOM-02**)

Na tela de criação, os três rádios **devem** aparecer **nesta ordem**, da esquerda para a direita, alinhados um ao lado do outro:

1. **«Radical Baseado no Item Mãe - Abreviado - Abreviado - Abreviado»** — após **A1–A8**, o valor sugerido em `receita_nome` **deve** seguir o **mesmo padrão** que o **Completo**: **`(radical abreviado) + sufixo_canônico`** (**(N5)** (**ITEMNOM-06**)), *i.e.* o texto abreviado seguido de `" - "` (espaço, hífen ASCII, espaço).
2. **«Radical Baseado no Item Mãe - Completo»** — **`nome_mae + sufixo_canônico`** (**M1.1** e **(N5)** (**ITEMNOM-06**)).
3. **«Sem Nome Base»**

O `name` HTML dos rádios de UI **deve** continuar distinto do `HiddenInput` de `receita_nome_base_mode` (ex.: `__code_name_base_mode_ui`), para não quebrar o comportamento nativo de rádio/hidden.

---

### 2.2 Valores POST (**ITEMNOM-03**–**ITEMNOM-05**)

*(Chaves `base_pai_*` mantêm o prefixo legado `pai` no identificador POST até a migração do código; semanticamente referem-se ao **item mãe**.)*

- **`base_pai_abrev`** — modo **Abreviado**: radical = resultado de **A1–A8**; sufixo em `receita_nome` = **(N5)** (**ITEMNOM-06**) (igual ao **Completo**).
- **`base_pai_completo`** — modo **Completo** (radical = `nome_mae` literal; concatenação inicial em `receita_nome` = **(N5)** (**ITEMNOM-06**)).
- **`sem_base`** — modo **Sem Nome Base** (**M2**).

---

## 3. Notação canónica (**ITEMNOM-06**–**ITEMNOM-09**)

- **(N1) `nome_mae`:** nome completo do item mãe, obtido do rótulo de `parent_item_id`, texto à **direita** de `" - "` após o código (vide **M1.2**). Usado na mensagem informativa do modo **Abreviado** (**G2.2**), como entrada do protocolo **A1–A8** e nas regras **M1** / **A9.3** (`prefixo_completo`).
- **(N9) `prefixo_completo` / `prefixo_abreviado`:** para o item mãe atual com `nome_mae` conhecido (*trim* não vazio), seja `ra = trim(radical_abreviado)` a saída de **A1–A8** sobre `nome_mae`. Então: **`prefixo_completo`** = `trim(nome_mae) + sufixo_canônico` (**(N5)** (**ITEMNOM-06**)); **`prefixo_abreviado`** = `ra + sufixo_canônico` (**(N5)** (**ITEMNOM-06**)) quando `ra` não for vazio. Usados em **M1.3**, **M1.5** e **A9.3** para decidir prefixação vs substituição de radical na troca de modo. A detecção «começa por» usa o prefixo com **(N5)** (**ITEMNOM-06**) (hífen ASCII na sugestão); remoção do radical anterior na troca de modo usa **separador flexível** **(N7)** (**ITEMNOM-07**) como em **M2.1**.
- **(N2) `radical` (operacional):** nos modos com base no item mãe, é o **trecho inicial** de `receita_nome` **antes** do primeiro `sufixo_canônico` **(N5)** (**ITEMNOM-06**) — no **Completo**, coincide com `nome_mae` (*trim*); no **Abreviado**, coincide com a saída textual de **A1–A8** (*trim*), **não** com `nome_mae` literal. No modo **sem base**, o sistema não impõe esse prefixo.
- **(N3)** Valores POST: **«Ordem dos rádios»** e seção **Valores POST** acima.
- **(N4) `léxico` / `norm` / substituição:** modo **Abreviado**; ver **Protocolo A1–A9**.
- **(N5) `sufixo_canônico de edição`:** a sequência literal **`" - "`** (espaço, hífen ASCII U+002D, espaço). Nos modos **Completo** e **Abreviado**, sempre que houver radical não vazio a sugerir, o valor inicial (ou reposto) de `receita_nome` **deve** ser **`radical + sufixo_canônico`**, *sem* substituir o hífen ASCII por en dash/em dash na **sugestão automática** — o mesmo padrão visual e de edição nos dois modos; o usuário completa o nome **após** esse sufixo. (Remoção com separadores flexíveis continua a cargo de **M2** ao mudar para **sem base**.)
- **(N6) `norm` (comparação estrita na v1):** usada em **A3.1** (passagem primária), **A1.3** e **A3.2** (detecção de duplicidade). **Definição:** *trim* em cada operando + **case folding** Unicode (em Python: `str.casefold()`; em JavaScript: usar API equivalente a *case fold* quando disponível, ou documentar o desvio se usar apenas `toLowerCase()`). **Espaços internos:** **não** colapsar na passagem estrita. **Acentos:** **não** remover diacríticos; grafias com e sem acento **não** se tratam como iguais (ex.: `Taxa` ≠ `Taxá`).
- **(N8) `norm_colapso_espacos` (fallback de comparação):** aplicar **(N6)** e, em seguida, colapsar **espaços internos** (qualquer sequência de espaços em branco no meio da string vira **um** espaço ASCII). Usada **somente** quando a passagem estrita correspondente **não** produzir resultado (**A3.3**, **A4.1b**). Se dois `termo` distintos no banco colidirem após **(N8)**, tratar como duplicidade conforme **A1.3** / **G6** (**D3**), não como desempate.
- **(N7) `separador flexível`:** imediatamente após o radical `b` **ou** no final do valor de `receita_nome`, a sequência composta por: espaços em branco opcionais; **um** caractere traço entre hífen ASCII U+002D (`-`), en dash U+2013 (`\u2013`) ou em dash U+2014 (`\u2014`); espaços em branco opcionais. **Usado em** **M2.1** (remoção do prefixo ao mudar para **sem base**) e **G1.2** (detecção de bloqueio: `trim(receita_nome)` termina com **(N7)** (**ITEMNOM-07**)). **Distinto de (N5):** a **sugestão automática** do sistema continua a usar apenas **`sufixo_canônico`** **(N5)** (**ITEMNOM-06**) (`" - "` com hífen ASCII); o usuário pode digitar **(N7)** (**ITEMNOM-07**) no campo, e **G1.2** **deve** bloquear qualquer ortografia de **(N7)** (**ITEMNOM-07**) ao final do valor, independente do radical e do modo.

---

## 4. Protocolo P-mãe e orquestração (**ITEMNOM-10**–**ITEMNOM-26**)

- **ITEMNOM-10** (**P1**). Ao preencher o campo **Código Canônico da Natureza de Receita** (`receita_cod`) e concluir-se com **sucesso** a cadeia que resolve o item mãe e atualiza `parent_item_id`, o sistema **deve** disparar o **protocolo do item mãe** (**P-mãe**), o mesmo que na alteração direta de `parent_item_id` (lookup de hierarquia, seleção no admin, etc.). O efeito normativo é o de **P-mãe**, não o de **M1.4** (Completo automático).

### Protocolo ao definir ou alterar o item mãe (`parent_item_id`) — **P-mãe**

Disparado quando `parent_item_id` recebe ou altera valor (incluindo após `syncHierarchyFromCode` / lookup por `receita_cod`, seleção manual do item mãe ou repovoamento equivalente no cliente — ex.: função análoga a `applyReceitaNomeBaseFromParent` no JS legado).

- **ITEMNOM-11** (**P-mãe.1**). **Deve** obter `nome_mae` conforme **P-orq.2** e calcular `radical_abreviado` conforme **B0.2** + protocolo **A1–A8**.
- **ITEMNOM-12** (**P-mãe.2**). **Deve** atualizar `receita_nome` para **`radical_abreviado + sufixo_canônico`** (**(N5)** (**ITEMNOM-06**)), aplicando **A9.2**: se o valor anterior já tiver **complemento** não vazio após o primeiro **separador flexível** **(N7)** (**ITEMNOM-07**), **preservar** esse trecho (ex.: `IPVA - Principal` → novo radical abreviado + `" - "` + `Principal`).
- **ITEMNOM-13** (**P-mãe.3**). **Deve** marcar o rádio **«Radical Baseado no Item Mãe - Abreviado»** e definir `receita_nome_base_mode` = `base_pai_abrev`.
- **ITEMNOM-14** (**P-mãe.4**). **Deve sobrescrever** qualquer modo de radical previamente selecionado (**Completo**, **Sem base** ou **Abreviado** de interação anterior), **mesmo** que o usuário já tivesse escolhido outro rádio antes do repovoamento do item mãe.
- **ITEMNOM-15** (**P-mãe.5**). O modo **Completo** **não** é aplicado por este protocolo; só entra em vigor pelo clique explícito do usuário no rádio **«Radical Baseado no Item Mãe - Completo»** (**M1.1**–**M1.5** / **A9.3**). O modo **Sem base** também **não** permanece após **P-mãe** — o repovoamento do item mãe **sempre** retorna ao **Abreviado** (**P-mãe.3**–**P-mãe.4**).

### Orquestração: `receita_cod` / hierarquia → **P-mãe** (obrigatório)

- **ITEMNOM-16** (**P-orq.1**). **P1** exige que **toda** resolução bem-sucedida do item mãe após alteração de `receita_cod` (`syncHierarchyFromCode` ou equivalente) execute **P-mãe** para o **novo** item mãe, **independentemente** de o evento `change` do campo `parent_item_id` ter sido disparado ou não.
- **ITEMNOM-17** (**P-orq.2**). **Fonte de `nome_mae` (ordem de prioridade):**
  1. **`parent.name`** (ou campo equivalente) no **payload JSON** do lookup de hierarquia, quando presente e não vazio;
  2. **M1.2** — rótulo/`label_link` de `parent_item_id` no DOM (fallback, ex.: seleção manual ou atraso de renderização do admin).
- **ITEMNOM-18** (**P-orq.3**). O cliente **não** deve depender **somente** do `change` de `parent_item_id` nem **somente** de polling do rótulo para cumprir **P1** após lookup por código. A camada que processa a resposta da hierarquia **deve** invocar **P-mãe** explicitamente (ex.: `applyCodeNameAfterParentResolved(parent_pk, nome_mae)`), passando `nome_mae` do payload quando disponível.
- **ITEMNOM-19** (**P-orq.4**). Troca de item mãe: considera-se **nova** resolução quando `parent.pk` mudar **ou** quando `parent.name` (`nome_mae`) for distinto do último aplicado em **P-mãe** (comparação após *trim* + *case fold*). Nesse caso **P-mãe** **deve** rodar de novo mesmo que o `pk` no input já estivesse atualizado antes do `change`.
- **ITEMNOM-20** (**P-mãe.2-bis**). Se `receita_nome` for **sugestão literal** do radical da **mãe anterior** (`bAntigo + (N7)` sem complemento — predicado **G1.5.a** / `receitaNomeEhSugestaoLiteral` no cliente; ex.: `Impostos sobre o Patrimônio - ` após trocar para mãe cujo radical abreviado é `ITCD`), **não** preservar o prefixo antigo como se fosse complemento (**A9.2**): substituir por **`(novo_radical_abreviado) + sufixo_canônico`** (**(N5)** (**ITEMNOM-06**)) apenas. A preservação de **A9.2** aplica-se somente quando há **complemento** não vazio após o traço **e** o valor **não** for só sugestão literal da mãe anterior.

### P-mãe durante confirmação **(G5)** — troca de mãe com código já preenchido

Referência: [`spec_itemClassificacao_criar_filho.md`](spec_itemClassificacao_criar_filho.md), seção **(G5)**.

Quando `receita_cod` **não** está vazio e o usuário troca `parent_item_id`, o cliente chama `suggest-child-code-by-parent/` **antes** de exibir o modal de confirmação. Durante esse intervalo e **enquanto o modal estiver aberto**, **ITEMNOM-21:** **P-mãe** fica **suspenso** (ex.: flag `__blockNamingParentChange` ou equivalente), para que `receita_nome` e rádios de radical **não** sejam alterados antes da decisão do usuário.

Após o fechamento do modal (ou após reversão automática por erro do endpoint):

| Ação do usuário                                               | Quando aplicar **P-mãe**                                                                      | Mãe efetiva | `receita_cod`             |
| ------------------------------------------------------------- | --------------------------------------------------------------------------------------------- | ----------- | ------------------------- |
| Erro do endpoint (**E1**/**E2**/**E3**) — reversão automática | Re-aplicar para a mãe **anterior** (restaurada)                                               | Anterior    | Inalterado                |
| **Cancelar** (incl. Escape / overlay)                         | Re-aplicar para a mãe **anterior** (restaurada)                                               | Anterior    | Inalterado                |
| **Manter Atual**                                              | Aplicar para a **nova** mãe                                                                   | Nova        | Inalterado                |
| **Atualizar**                                                 | Via `applyNamingAfterParentSuggest` após aplicar a sugestão (**Passo 6** de `criar_filho.md`) | Nova        | Substituído pela sugestão |

- **ITEMNOM-23** (**P-G5.1**). Em **Cancelar** e em reversão por erro do endpoint, **não** alterar `nivel_id` nem `classificacao_id`.
- **ITEMNOM-24** (**P-G5.2**). Em **Manter Atual**, **não** alterar `nivel_id` nem `classificacao_id`; **P-mãe** **deve** rodar para a nova mãe, pois o item mãe efetivo mudou mesmo sem recálculo do código.
- **ITEMNOM-25** (**P-G5.3**). O listener genérico de `change` em `parent_item_id` (`code_name.js`) **deve** respeitar a suspensão de **P-mãe** durante **(G5)**; a orquestração explícita após o modal **substitui** qualquer efeito adiado desse listener.
- **ITEMNOM-26** (**P-G5.4**). Na reversão (**Cancelar** ou erro do endpoint), se o snapshot tiver `nome_mae` conhecido, usá-lo em **P-mãe**; senão, obter `nome_mae` do rótulo após o re-fetch semântico do PK (mesmo fluxo do widget de `parent_item_id`).

**Exemplo P-orq / P-mãe.2-bis**  
- Código `…52.0.0…` → mãe `Impostos sobre o Patrimônio`, `receita_nome` = `Impostos sobre o Patrimônio - ` (ou radical abreviado equivalente + traço).  
- Código alterado para `…52.0.9…` → mãe `ITCD`; após hierarquia, **P-mãe** com `nome_mae` = `ITCD` do payload → `receita_nome` = `ITCD - ` (ou radical abreviado de `ITCD` + **(N5)** (**ITEMNOM-06**)), **não** manter `Impostos sobre o Patrimônio - `.

---

## 5. Modo Completo (**ITEMNOM-30**–**ITEMNOM-33**)

### Requisitos (M1)

- **ITEMNOM-30** (**M1.1**). Com este modo selecionado e `nome_mae` conhecido (*trim* não vazio), `receita_nome` **deve começar** por **`prefixo_completo`** (**(N9)** / **(N5)** (**ITEMNOM-06**)), *i.e.* `nome_mae + sufixo_canônico`.
- **ITEMNOM-31** (**M1.2**). `nome_mae` **deve** ser extraído do rótulo de `parent_item_id` (texto após `" - "` no *link*). Se o item mãe não tiver nome, o radical fica vazio e **M1.1** não se aplica.
- **ITEMNOM-32** (**M1.3**). Ao selecionar este modo (clique explícito, **não** **P-mãe**), a substituição do radical existente segue o **algoritmo unificado de A9.3** (4 passos — ver seção «Regra A9»). **M1.3** corresponde ao **passo 4** desse algoritmo: quando nenhum dos passos anteriores casa **e** o valor **não contém** nenhum separador **(N7)** (**ITEMNOM-07**), o valor inteiro é tratado como complemento e **`prefixo_completo`** é prefixado à esquerda. **Não** duplicar prefixos: se o valor já começar por **`prefixo_completo`**, o passo 1 de A9.3 garante no-op.
- **ITEMNOM-33** (**M1.4**). **Não** se aplica ao repovoamento automático do item mãe (**P-mãe**). Quando o **usuário** clica explicitamente neste rádio, valem **M1.1**–**M1.5** (**A9.3** na troca de modo); qualquer nova definição ou troca de `parent_item_id` dispara **P-mãe** (Abreviado), **não** **M1.4**.
- **M1.5 (troca de modo → Completo; caso particular de A9.3).** Corresponde ao **passo 2** do algoritmo de **A9.3** quando a base candidata é o `radical_abreviado` («base do modo oposto»): se `stripLeadingParentRadical(valor, radical_abreviado)` casa (valor começa por `ra + (N7)`), remove-se esse prefixo, preserva-se o complemento e repõe-se **`prefixo_completo`**. **Objetivo:** trocar o radical do modo **Abreviado** pelo de **Completo** sem empilhar `nome_mae` sobre `ITCD - `.

**Exemplo M1.1**  
- `nome_mae` = `Imposto sobre Transmissão "Causa Mortis" e Doação de Bens e Direitos` → `receita_nome` = `Imposto sobre Transmissão "Causa Mortis" e Doação de Bens e Direitos - `.

**Exemplo M1.3 (sem traço — passo 4 de A9.3, prefixa o valor inteiro como complemento)**  
- Modo **Completo**, `nome_mae` = `IPVA`, valor `Principal` (sem traço) → `IPVA - Principal`.
- Modo **Completo**, `nome_mae` = `Imposto sobre a Propriedade Predial e Territorial Urbana`, valor `IPTU` (sem traço) → `Imposto sobre a Propriedade Predial e Territorial Urbana - IPTU`.

**Exemplo passo 1 de A9.3 (no-op — já começa pelo novo prefixo)**  
- Modo **Completo**, valor `Imposto sobre a Propriedade Predial e Territorial Urbana - Principal` → clique no rádio **Completo** mantém o valor inalterado.

**Exemplo M1.5 / A9.3 (Abreviado → Completo — passo 2)**  
- `nome_mae` = `Imposto sobre Transmissão "Causa Mortis" e Doação de Bens e Direitos`, `ra` = `ITCD`, valor `ITCD - ` → após rádio **Completo**: `Imposto sobre Transmissão "Causa Mortis" e Doação de Bens e Direitos - ` (**não** `Imposto… - ITCD - `).

**Exemplo M1.5 / A9.3 (com complemento — passo 2)**  
- Valor `ITCD - Principal` → **Completo**: `Imposto sobre Transmissão "Causa Mortis" e Doação de Bens e Direitos - Principal`.

---

## 6. Modo Sem base (**ITEMNOM-36**–**ITEMNOM-37**)

### Requisitos

- **ITEMNOM-36** (**M2.1**). Ao selecionar este modo, **remover** do início de `receita_nome` o **radical atualmente conhecido** na UI (`currentParentNameBase` ou equivalente — seja ele o `nome_mae` literal do modo **Completo** ou o radical **abreviado** do modo **Abreviado**), seguido do **separador flexível** (**(N7)** (**ITEMNOM-07**)).
- **M2.2.** Se **M2.1** não casar, tentar remoção **estrita** do prefixo `texto_radical_conhecido + sufixo_canônico` (**(N5)** (**ITEMNOM-06**)) quando o valor começar exatamente por essa string — onde `texto_radical_conhecido` é o radical que o modo ativo colocou **antes** do sufixo canônico.
- **M2.3.** Se o valor ainda começar pelo radical conhecido sem separador válido, exibir aviso `remove_base_prefix_mismatch`.
- **M2.4.** `receita_nome_base_mode` = `sem_base`.

**Exemplo M2.1**  
- Radical conhecido = `ICMS`; `receita_nome` = `ICMS\u2013Principal` → `Principal`.

---

## 8. Guardrails (**ITEMNOM-50**–**ITEMNOM-64**)

### G0 — Bloqueio de envio: nome vazio (obrigatório no add)

**Independente dos rádios:** **G0** **não** altera o comportamento de **P-mãe**, **M1**, **M2**, **A9.3** nem a edição manual do campo. O usuário **pode** apagar o texto sugerido (modos **Abreviado** / **Completo**) ou preencher o nome livremente (**Sem base**). O que **não** pode é **gravar** o item novo com `receita_nome` vazio.

- **ITEMNOM-50** (**G0.1**). Na tela **add**, seja `n = trim(receita_nome)`. **Nome vazio** quando `n` não contém nenhum caractere (string vazia ou só espaços em branco). Alinhado a `schemas/item_classificacao.yaml` (`receita_nome`, `required: true`).
- **G0.2 (escopo do modo).** **G0** aplica-se **sempre** no **add**, para **qualquer** valor de `receita_nome_base_mode` (**Abreviado**, **Completo**, **Sem base** ou vazio no POST).
- **G0.3 (cliente).** Em `validateCodeNameOnSubmit`, avaliar **G0** **antes** de **G1**. Se nome vazio, **bloquear** o envio: `setCustomValidity` com **G0.5**, erro no campo e nota no topo.
- **G0.4 (servidor — obrigatório).** Em `ItemClassificacaoAdminForm.clean()` na tela **add**, se **G0.1** for verdadeiro, `ValidationError` em `receita_nome` com **G0.5** (**sem** avaliar **G1** nesse caso).
- **G0.5 (mensagem de erro).** Texto em `code_name_messages.py` (`receita_nome_vazio_error`). Exemplo normativo:  
  `Preencha o Nome da Classificação por Natureza de Receita para concluir o cadastro.`

**Exemplo G0 (Abreviado — usuário apagou tudo)**  
- Rádio **Abreviado**, `receita_nome` = `` (vazio) → **bloqueado** por **G0** (não por **G1**).

**Exemplo G0 (Sem base — nome livre)**  
- Rádio **Sem base**, `receita_nome` = `Taxa municipal de iluminação` → **permitido** por **G0**.  
- Rádio **Sem base**, `receita_nome` vazio → **bloqueado** por **G0**.

**Exemplo G0 vs G1**  
- `receita_nome` = `ITCD - ` (não vazio, termina com traço) → **G0** não bloqueia; **G1** bloqueia (independente do modo, inclusive `sem_base`).  
- `receita_nome` = `ITCD` (não vazio, sem traço final) → **G0** e **G1** **não** bloqueiam, mesmo no modo Abreviado/Completo.

### G1 — Bloqueio de envio: nome terminando com traço (incompleto)

**Paridade entre modos:** **G1** aplica-se a **todos** os modos da tela **add** (`base_pai_completo`, `base_pai_abrev`, `sem_base` e modo vazio) e **não depende** do radical efetivo `b`: bloqueia-se gravar item novo cujo `trim(receita_nome)` termine com um **separador flexível (N7)**. Isso engloba (i) o caso particular em que `receita_nome` é exatamente a sugestão automática (`b + (N5)` para Completo ou Abreviado), (ii) qualquer nome editado pelo usuário que permaneça com traço final pendurado e (iii) entradas livres em `sem_base` terminadas em traço. A diferenciação entre os sub-casos serve apenas para selecionar a mensagem de erro em **G1.5** (G1.5.a vs G1.5.b).

- **G1.1 (cliente).** Na tela **add**, após validações de código e hierarquia, executar `validateCodeNameOnSubmit` (**G0.3** primeiro; depois **G1**). Se **G0** não bloqueou e `trim(receita_nome)` casar o predicado de **G1.2**, **bloquear** o envio no navegador, **em qualquer** valor de `receita_nome_base_mode` (inclusive `sem_base` e vazio).
- **ITEMNOM-55** (**G1.2**). Seja `n = trim(receita_nome)`. **Nome incompleto (G1)** quando, após **right-trim** apenas de espaços em branco em `n`, o **último caractere** de `n` for um traço pertencente a **(N7)** (**ITEMNOM-07**) (`-` U+002D, `–` U+2013, `—` U+2014). Equivalentemente, `n` casa com `^.*` + `(N7)` + `\s*$`, com `(N7)` no sentido de **M2.1** (hífen ASCII, en dash ou em dash, com espaços ASCII opcionais ao redor). **(N5)** (**ITEMNOM-06**) é caso particular de **(N7)** (**ITEMNOM-07**).

  **Escopo de modo.** O predicado **não consulta** `receita_nome_base_mode` nem o radical efetivo `b`: o bloqueio aplica-se em **todos** os modos do **add** (incluindo **`sem_base`**, **`base_pai_completo`**, **`base_pai_abrev`** e legado **`base_pai`**).

  **Casos cobertos automaticamente.**
  1. Sugestão automática literal de qualquer ramo: `b_completo + (N5)` e `b_abreviado + (N5)` (em qualquer ortografia de (N7));
  2. Nomes editados pelo usuário com traço final pendurado (ex.: `IPVA - Cota Única -`);
  3. Nomes no modo **`sem_base`** terminados em traço (ex.: `Taxa municipal -`).

  **Casos liberados** (regressão em relação à versão anterior desta spec).
  - `n` igual a `nome_mae` ou ao radical abreviado, **sem** traço final (ex.: `Imposto sobre a Propriedade Predial e Territorial Urbana`, `IPVA`) → **permitido**.
  - `n` com complemento e sem traço final (ex.: `IPVA - Cota Única`) → **permitido**.

  **Seleção da mensagem (ver G1.5).** Para gerar a mensagem adequada, a validação **deve** ainda calcular `b_completo = trim(nome_mae)` e `b_abreviado = trim(radical_abreviado)` (via **I1**/**I4**) e comparar `n` com `b_completo + (N5)` e `b_abreviado + (N5)` (em todas as ortografias de **(N7)** (**ITEMNOM-07**), com espaços ASCII opcionais ao redor do traço):
  - se casar → **G1.5.a** (sugestão literal);
  - senão → **G1.5.b** (traço final pendurado).
  No modo **`sem_base`** ou quando `b_completo` for vazio (item mãe ausente), pular **G1.5.a** e usar diretamente **G1.5.b**.

  **Requisito:** não gravar item novo em **add** cujo `trim(receita_nome)` termine com traço **(N7)** (**ITEMNOM-07**), qualquer que seja o modo.
- **G1.3 (cliente — feedback).** Ao bloquear no navegador: `setCustomValidity` com a chave de mensagem adequada (`receita_nome_submit_sugestao_literal_error` para **G1.5.a**; `receita_nome_submit_traco_final_error` para **G1.5.b**), erro no campo e nota no topo (ex.: «Por favor, corrija o erro abaixo.»).
- **G1.4 (servidor — obrigatório).** Em `ItemClassificacaoAdminForm.clean()` na tela **add**, **deve** repetir **G1.2** sobre `n = trim(receita_nome)`, **independentemente** do modo (inclusive `sem_base`). Se o predicado disparar, escolher entre **G1.5.a** e **G1.5.b** conforme a sub-regra de **G1.2** (comparação com `b_completo + (N5)` / `b_abreviado + (N5)` quando `nome_mae` estiver disponível). Em caso de bloqueio, levantar `ValidationError` em `receita_nome` com o texto correspondente. Obter `nome_mae` de `parent_item_id` resolvido; obter `radical_abreviado` via módulo **I1** / **I4**, sem duplicar **A1–A8** no formulário. Normalizar `base_pai` → `base_pai_completo` apenas para fins de exibição/auditoria (o predicado em si não depende do modo).
- **G1.5 (mensagens de erro — duas variantes).** Textos em `code_name_messages.py`, usados no cliente (**G1.3**) e no servidor (**G1.4**). Redação em português do Brasil.

  - **G1.5.a — sugestão automática literal não completada.**  
    Disparada quando `n` casa com `b_completo + (N5)` **ou** `b_abreviado + (N5)` (com (N7) flexível). Chave sugerida: `receita_nome_submit_sugestao_literal_error`. Texto normativo:  
    `Atualize o nome após o traço para concluir o cadastro, ou remova o traço final se desejar gravar apenas o radical sugerido (completo ou abreviado).`

  - **G1.5.b — nome termina com traço (não é sugestão literal).**  
    Disparada quando `n` termina com **(N7)** (**ITEMNOM-07**) mas **não** casa com **G1.5.a**. Vale também em `sem_base` (em que `b` é indefinido). Chave sugerida: `receita_nome_submit_traco_final_error`. Texto normativo:  
    `O Nome da Classificação por Natureza de Receita não pode terminar com traço (-, – ou —). Adicione um complemento após o último traço ou remova-o.`

**Exemplo G1.2 (Completo — sugestão literal)**  
- Item mãe `Receita de Imposto`; `n = "Receita de Imposto - "` → **bloqueado** com **G1.5.a**.

**Exemplo G1.2 (Abreviado — sugestão literal)**  
- Radical abreviado `Receita Imposto`; `n = "Receita Imposto - "` → **bloqueado** com **G1.5.a**.

**Exemplo G1.2 (sugestão sem espaço final)**  
- `n = "Receita de Imposto -"`; `n = "Receita Imposto -"` → **bloqueado** com **G1.5.a** (predicado **G1.2** captura `^.* (N7) \s*$`; a comparação com `b + (N5)` admite espaços ASCII opcionais ao redor do traço, então casa como sugestão literal).

**Exemplo G1.2 (complemento + traço pendurado)**  
- `n = "Receita de Imposto - Carro -"`; `n = "Receita Imposto - Carro - "` → **bloqueado** com **G1.5.b** (termina com traço, mas não é sugestão literal).

**Exemplo G1.2 (radical igual sem traço — regressão, agora permitido)**  
- `n = "Receita de Imposto"`; `n = "Receita Imposto"` → **permitido** (não termina com traço, mesmo coincidindo com `b`).

**Exemplo G1.2 (complemento normal)**  
- `n = "Receita de Imposto - Carro"`; `n = "Receita Imposto - Carro"`; `n = "Rec. Imposto - Carro"` → **permitido**.

**Exemplo G1.2 (separadores Unicode)**  
- `n = "Receita Imposto\u2013"` (en dash) → **bloqueado** com **G1.5.a** (sugestão literal abreviada com (N7) en dash).  
- `n = "Receita Imposto\u2014Carro\u2014"` (em dashes) → **bloqueado** com **G1.5.b** (termina com em dash; tem complemento intermediário).  
- `n = "Receita Imposto\u2013Carro"` → **permitido** (não termina com traço).

**Exemplo G1.2 (modo `sem_base`)**  
- Modo `sem_base`, `n = "Taxa municipal de iluminação"` → **permitido**.  
- Modo `sem_base`, `n = "Taxa municipal -"` → **bloqueado** com **G1.5.b**.

### G2 — Mensagens informativas (antes do envio)

- **G2.0.** Enquanto o predicado **G1.2** for verdadeiro (`trim(receita_nome)` termina com **(N7)** (**ITEMNOM-07**)) e houver radical conhecido, **deve** exibir-se mensagem informativa azul; o **texto** depende do modo. A mensagem **deve** apresentar as duas saídas válidas (completar após o traço **ou** remover o traço final).

- **G2.1 — Modo Completo (`base_pai_completo`):**  
  **Texto fixo:**  
  `Nome sugerido com base na versão completa do item mãe selecionado. Complete o nome após o traço, ou remova o traço final para gravar apenas o radical.`  
  (Chave sugerida na implementação: ex. `receita_nome_sugestao_info_completo` — **sem** interpolar `nome_mae`; o radical exibido em `receita_nome` já é o nome completo da mãe.)

- **G2.2 — Modo Abreviado (`base_pai_abrev`):**  
  **Texto** (*template* com placeholder `{nome_mae}`):  
  `Nome sugerido com base na versão abreviada do item mãe selecionado. Complete o nome após o traço, ou remova o traço final para gravar apenas o radical. O nome do item mãe é "` + **valor literal de `nome_mae`** + `"`  
  (aspas delimitadoras literais ao redor do nome do item mãe; escapar aspas internas de `nome_mae` na implementação se necessário). Chave sugerida: `receita_nome_sugestao_info_abrev_template` com placeholder `{nome_mae}`.

- **G2.3.** No evento `input` de `receita_nome`, limpar *customValidity*, mensagens locais de naming e *errornote* associada.

**Exemplo G2.1**  
- Qualquer item mãe → mensagem fixa:  
  `Nome sugerido com base na versão completa do item mãe selecionado. Complete o nome após o traço, ou remova o traço final para gravar apenas o radical.`

**Exemplo G2.2**  
- `nome_mae` = `Impostos sobre o Patrimônio` → mensagem completa:  
  `Nome sugerido com base na versão abreviada do item mãe selecionado. Complete o nome após o traço, ou remova o traço final para gravar apenas o radical. O nome do item mãe é "Impostos sobre o Patrimônio"`.

### G3 — Limpeza ao remover o item mãe

- **G3.1.** Se `parent_item_id` ficar vazio, limpar rádios, oculto `receita_nome_base_mode`, estado do radical e mensagens.

### G4 — Hidratação após POST com erro

- **G4.1.** Se o formulário retornar com `parent_item_id` e `receita_nome` preenchidos, reidratar o estado do radical pelo rótulo ou, se necessário, inferir o prefixo antes do primeiro separador flexível (**M2.1**), **em consistência** com `receita_nome_base_mode` salvo. **Nota:** o predicado de **G1.2** **não** depende de `b`; a reidratação de `b_completo` / `b_abreviado` continua relevante para outros protocolos (**P-mãe**, **A9.2**, **A9.3**, **M1.3**, **M1.5**) e para a **seleção** entre **G1.5.a** e **G1.5.b** no servidor, mas não condiciona o bloqueio de **G1**.

### G5 — Ordem na cadeia de envio

- **G5.1.** Validação de naming **depois** de validação de código e `syncHierarchyFromCode` com sucesso, **antes** de confirmações adicionais e *submit* nativo.

### G6 — Alerta: `termo_nome` duplicado na Lista de Abreviações

- **G6.1.** Quando **A3.2** ou **A1.3** se aplicar, o sistema **deve** exibir alerta **visível** ao usuário (ex.: mensagem de aviso amarela junto ao campo `receita_nome` ou nota no topo do formulário, no mesmo espírito de `remove_base_prefix_mismatch`), **sem** substituir silenciosamente uma abreviação por outra.
- **G6.2.** **Texto obrigatório** (pode ser *template* em `code_name_messages.py`, chave sugerida `receita_nome_lexico_termo_duplicado`):  
  `Verifique na Lista de Abreviações: o termo_nome «{termo_nome}» está duplicado (há mais de um registro ativo).`  
  O placeholder `{termo_nome}` **deve** ser preenchido com o valor acordado em **A3.2** (`nome_mae`) ou **A1.3** (campo `termo` da linha em conflito).
- **G6.3.** Este alerta **não** bloqueia por si só o envio do formulário de criação do item (diferente de **G1**); informa inconsistência de dados para correção na **Lista de Abreviações** no admin.

**Exemplo G6.2**  
- `nome_mae` = `Principal`; duas linhas ativas com `norm(termo)` igual → alerta: `Verifique na Lista de Abreviações: o termo_nome «Principal» está duplicado (há mais de um registro ativo).`

---

## 7. Modo Abreviado (**ITEMNOM-40**)

### 7.1 Requisitos gerais B0

### Requisitos gerais

- **ITEMNOM-40** (**B0.1**). Este modo corresponde ao **primeiro** rádio na ordem da UI.
- **B0.2.** O **radical abreviado** (trecho que alimenta **(N2)** no modo **Abreviado**) **deve** ser calculado pelo protocolo **A1–A8** a partir de `nome_mae` e do léxico ativo. As etapas **A1–A6** produzem apenas esse texto (sem o sufixo de edição).
- **B0.3.** **Paridade com o modo Completo:** após obter o radical abreviado (*trim* não vazio), o valor colocado em `receita_nome` **deve** ser **`radical_abreviado + sufixo_canônico`** (**(N5)** (**ITEMNOM-06**)) — o **mesmo** literal `" - "` que em **M1.1**; **não** basta o radical sozinho no campo quando o sistema sugere o nome.
- **B0.4.** Quando **P-mãe** recalcula o item mãe, o radical abreviado e `receita_nome` seguem **P-mãe.2** e **A9.2** (preservar complemento após o separador). Com este modo já selecionado **sem** troca de item mãe, recálculos internos obedecem **A9**. Ao **clicar** neste rádio vindo do modo **Completo**, a troca de radical obedece **A9.3** (espelho de **M1.5**).

---

### 7.2 Protocolo A1–A9 (**ITEMNOM-80**–**ITEMNOM-94**)

*(ND) = transformação sobre `nome_mae` e léxico.*

- **Paridade com o modo Completo (sufixo):** o valor sugerido em `receita_nome` nos dois modos com base no item mãe **sempre** observa **`radical + sufixo_canônico`** (**(N5)** (**ITEMNOM-06**)). No **Abreviado**, o protocolo abaixo define só o **radical**; a regra **A7** fecha o contrato concatenando **(N5)** (**ITEMNOM-06**) ao resultado de **A1–A6**, em espelho de **M1.1**.

### Regra A1 (ND) — Léxico e registro ativo

- **A1.1.** Só `AliasLexico` com `data_registro_fim` = sentinela (ativo).
- **A1.2.** Ignorar `termo` ou `abreviacao` vazios após *strip*.

**Exemplo A1.1**  
- `Principal` / `Princ.` ativo → entra no léxico; `Secundário` / `Sec.` com registro encerrado → fora.

### Regra A2 (ND) — Ordenação dos candidatos a `termo`

- **A2.1.** Multi-palavra antes de mono-palavra; comprimento de `termo` decrescente; desempate lexicográfico.

**Exemplo A2.1**  
- Frase longa do IPVA antes de `Restituição`.

### Regra A3 (ND) — Match exato do nome completo do item mãe

- **A3.1.** **Passagem estrita:** se existir **exatamente uma** linha ativa em que `norm(termo) == norm(nome_mae)` (**(N6)**), o radical interno = `abreviacao` dessa linha (*strip*), **sem A4–A5**; em seguida aplica-se **A6** e **A7** (`+ sufixo_canônico` em `receita_nome`).
- **A3.2.** Se existirem **duas ou mais** linhas ativas com `norm(termo) == norm(nome_mae)` na **mesma passagem** (**(N6)** ou **(N8)**), tratar como **erro de dados no banco**. **Não** há desempate: **não** aplicar **A3.1** nem **A3.3** para esse match. O sistema **deve** exibir **alerta** conforme **G6**, com `termo_nome` = valor de `nome_mae` (no match exato do item mãe) ou do `termo` em conflito. Em seguida, o protocolo **deve** continuar por **A4**–**A6**, ou **A8** se não houver substituições.
- **A3.3.** **Passagem fallback (espaços):** somente se **A3.1** **não** tiver encontrado **exatamente uma** linha: repetir o critério de **A3.1** usando `norm_colapso_espacos(termo) == norm_colapso_espacos(nome_mae)` (**(N8)**), com as mesmas regras de unicidade e **A3.2** em caso de duplicidade.

**Exemplo A3.1**  
- Uma linha ativa: `termo` = nome longo do IPVA, `norm(termo) == norm(nome_mae)` → radical = `IPVA` + **A7**.

**Exemplo A3.2**  
- Duas linhas ativas distintas com `norm(termo) == norm(nome_mae)` e `abreviacao` diferentes → alerta **G6** com `termo_nome` = texto de `nome_mae`; não usar **A3.1**; seguir **A4** se houver substrings no léxico.

**Exemplo A3.3**  
- `termo` no léxico = `Imposto  sobre` (dois espaços); `nome_mae` = `Imposto sobre` (um espaço) → **A3.1** falha; **A3.3** com **(N8)** encontra **uma** linha → radical = `abreviacao` dessa linha + **A7**.

### Regra A1 (complemento) — Duplicidade de `termo_nome` no léxico ativo

- **A1.3.** Ao montar o léxico ativo, se **duas ou mais** linhas ativas compartilharem o mesmo `norm(termo)` (**(N6)**) **ou** o mesmo `norm_colapso_espacos(termo)` (**(N8)**), tratar como **erro de dados** (**D3**). **Não** escolher linha por desempate. O sistema **deve** exibir **alerta** conforme **G6**, com `termo_nome` = valor do campo `termo` de qualquer linha em conflito. O protocolo **pode** prosseguir, mas o alerta **deve** permanecer visível até correção na **Lista de Abreviações**.

### Regra A4 (ND) — Substituição por substring não sobreposta

- **A4.1a (passagem estrita):** o `termo` (após *trim*) deve ocorrer como **substring contígua** de `nome_mae`, com comparação **case-insensitive** (`casefold`); **sem** colapsar espaços internos.
- **A4.1b (passagem fallback — espaços):** somente se **A4.1a** **não** tiver produzido nenhum intervalo aceito em **A4.3**: considerar match quando `norm_colapso_espacos(termo)` for substring de `norm_colapso_espacos(nome_mae)` (**(N8)**). O intervalo para **A4.4** **deve** ser mapeado de volta para a string **original** de `nome_mae` (substituição sempre na cópia literal do item mãe, não na string colapsada).
- **A4.2–A4.3.** Greedy global: maior `(end-start)`, menor `start`, ordem **A2** (válido na passagem estrita; na fallback, mesma prioridade entre candidatos da **A4.1b**).
- **A4.4.** Substituir cada intervalo aceite na string **original** do item mãe pela `abreviacao` correspondente.

### Regra A5 (ND) — Remanescentes literais

- **A5.1.** Trechos não cobertos permanecem como no `nome_mae`.

### Regra A6 (ND) — Conectivos e pontuação

- **A6.0.** **Sempre** após o radical produzido por **A3**, **A4**/**A5** ou **A8** (e **antes** de **A7**): aplicar compactação **A6** ao texto do radical, **independentemente** de haver correspondência no léxico.
- **A6.1 (pontuação nas extremidades).** Tokenizar por espaços; em cada token, remover das **extremidades** (repetir até fixar) os caracteres em `LEXICO_PONTUACAO_OMITIR_NAS_EXTREMIDADES` (`,`, `;`, `:`, `!` — sozinhos ou colados à palavra). Omitir tokens que fiquem vazios ou compostos **apenas** por esses caracteres e/ou `.` solto.
- **A6.2 (conectivos lexicais).** Remover tokens cujo *casefold* está em `LEXICO_CONNECTIVOS_FIXOS` (mesmo módulo SSOT).
- **A6.3 (ponto final).** Se o token **integral** casa com abreviação por encurtamento **(iv)** da spec de abreviações (`^[letras]{1,8}\.$`, ex.: `Princ.`, `Contrib.`), **não** alterar o token. Caso contrário, remover `.` das extremidades do token (não remover ponto **interior**, ex. separadores em siglas).
- **A6.4.** Reunir tokens restantes com um espaço ASCII.

**Exemplo A6 (pontuação + conectivos)**  
- `Tx. Insp. Contr. Fisc., Princ.` → `Tx. Insp. Contr. Fisc. Princ.` (vírgula omitida; tokens **(iv)** preservados).  
- `Imposto, sobre a Propriedade` → `Imposto Propriedade` (após **A6.2**).

### Regra A7 (ND) — Concatenação do sufixo canônico (igual ao Completo)

- **A7.1.** Se o radical produzido após **A6** (em qualquer ramo **A3**, **A4** ou **A8**) for **não vazio** após *trim*, o valor a atribuir a `receita_nome` na sugestão **deve** ser **`radical + sufixo_canônico`** (**(N5)** (**ITEMNOM-06**)), *i.e.* o mesmo padrão **`… + " - "`** que **M1.1** no modo **Completo**.
- **A7.2.** Se o radical for vazio, **não** aplicar sufixo canônico por omissão (alinhado à exceção de **M1.1** quando não há `nome_mae`).

### Regra A8 (ND) — Nenhuma substituição

- **A8.1.** Sem A3 nem A4 → o radical interno intermédio = `nome_mae.strip()`; em seguida **A6** remove conectivos; **A7** aplica **`+ sufixo_canônico`**; recomenda-se aviso de léxico não aplicável.

**Exemplo A8 + A6 (sem léxico)**  
- `nome_mae` = `Imposto sobre a Propriedade Predial e Territorial Urbana` → radical após **A6** = `Imposto Propriedade Predial Territorial Urbana` → sugestão `… Urbana - ` (**(N5)** (**ITEMNOM-06**)).

### Regra A9 (ND) — Mudança de modo ou item mãe

- **A9.1.** Recalcular sugestão.
- **A9.2.** Ao repor o radical (mudança de modo, **P-mãe** ou recálculo do abreviado): se `receita_nome` contiver um **separador flexível** **(N7)** (**ITEMNOM-07**) seguido de **complemento** não vazio (texto após o traço, com pelo menos um caractere não branco), o novo valor **deve** ser **`(novo_radical) + sufixo_canônico`** (**(N5)** (**ITEMNOM-06**)) **concatenado ao complemento preservado** — o mesmo trecho que estava após o separador, sem reinterpretar nem descartar (ex.: `… - Principal` mantém `Principal` quando o item mãe muda e **P-mãe** força Abreviado). Se **não** houver complemento (sugestão incompleta conforme **G1.2** ou valor vazio após o separador), aplicar apenas **`novo_radical + sufixo_canônico`** (**(N5)** (**ITEMNOM-06**)).
- **A9.2-bis.** Na **troca** de item mãe (**P-mãe** com `nome_mae` novo), se o valor atual for **sugestão literal** (`bAntigo + (N7)` sem complemento — predicado **G1.5.a**) do radical da mãe **anterior**, tratar como **sem complemento** (**P-mãe.2-bis**), mesmo que o texto contiver um traço no final.

### A9.3 — Troca de modo Completo ↔ Abreviado (algoritmo unificado de 4 passos)

Disparada pelo clique explícito no rádio **Completo** ou **Abreviado** (**M1.4** / **B0.4**), **não** por **P-mãe**. Com `nome_mae` e `ra` (**(N9)**) conhecidos, e dadas as variáveis:

- `novo_prefixo` = `prefixo_completo` (`nome_mae + (N5)`) ou `prefixo_abreviado` (`ra + (N5)`), conforme o rádio clicado;
- `bases_remover` = lista ordenada das bases candidatas a strip **exato**, com o radical do **modo oposto** ao clicado em primeiro lugar e o do **modo destino** em segundo (para também tolerar separadores **(N7)** (**ITEMNOM-07**) não canônicos no início do valor).

O cliente **deve** aplicar os passos abaixo em ordem, parando no primeiro que casar:

| Passo      | Condição                                                                                                                                                                                                        | Ação                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| ---------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **A9.3-1** | `valor` já começa por `novo_prefixo` (literal **(N5)** (**ITEMNOM-06**) com hífen ASCII e espaços canônicos).                                                                                                   | **No-op** — não duplicar prefixos.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| **A9.3-2** | Para alguma `base ∈ bases_remover`, `stripLeadingParentRadical(valor, base)` casa (**(N7)** (**ITEMNOM-07**) flexível como em **M2.1**: hífen ASCII, en dash ou em dash, com espaços ASCII opcionais ao redor). | Remove esse prefixo, preserva o resto como **complemento**, retorna `novo_prefixo + complemento` (ou só `novo_prefixo` se complemento vazio). Aplica **A9.2** sobre o complemento. **M1.5** é o caso particular `Abreviado → Completo` (`base = ra`); o caso simétrico `Completo → Abreviado` usa `base = nome_mae`.                                                                                                                                                                                                                               |
| **A9.3-3** | Nenhum strip exato bateu, **e** `valor` contém pelo menos um separador **(N7)** (**ITEMNOM-07**).                                                                                                               | Strip de **tudo até o primeiro (N7) inclusive**. Em seguida, **limpar resíduo**: enquanto o que sobrou começar com **(N7)** (**ITEMNOM-07**) (com espaços ASCII opcionais ao redor), strip mais um **(N7)** (**ITEMNOM-07**). O resultado trimado é o **complemento**. Retorna `novo_prefixo + complemento` (ou só `novo_prefixo` se complemento vazio). **Corrige** o cenário em que o usuário **editou** o radical sugerido (ex.: removeu conectivos) — o passo 2 falha por não haver match exato, mas o passo 3 garante a substituição correta. |
| **A9.3-4** | Nenhum dos anteriores casou (em particular, `valor` **não** contém nenhum **(N7)** (**ITEMNOM-07**)).                                                                                                           | **Trata o valor inteiro como complemento.** Retorna `novo_prefixo + trim(valor)`. Equivale ao antigo **M1.3** (prepend sem remover).                                                                                                                                                                                                                                                                                                                                                                                                               |

**A9.3-5 (independência da regra).** O algoritmo **não** consulta `receita_nome_base_mode` (o modo previamente selecionado) para decidir o ramo; só usa `nome_mae`, `ra` e o radical conhecido para construir `bases_remover`. Isso garante que o resultado depende **somente** do valor atual de `receita_nome` e do rádio recém-clicado.

**A9.3-6 (não interpretar radical anterior como complemento).** Os passos 2 e 3 garantem que o texto **antes** do separador é descartado como «tentativa de radical», nunca preservado como complemento. **A9.2** aplica-se ao texto **após** essa remoção.

**A9.3-7 (paridade com P-mãe).** A função `extrairComplementoPreservado` usada por **P-mãe** (`complementoPreservadoNaTrocaItemMae`) implementa o **passo 3** sem a limpeza iterativa de resíduo. Para os fluxos atuais de P-mãe isso não causa divergência porque a entrada em P-mãe é controlada pelo sistema (sugestões automáticas + edições leves do usuário). Caso o cliente venha a adotar o mesmo helper em P-mãe, herdará automaticamente a limpeza de resíduo do passo 3.

**Exemplos A9.3** (item mãe `Imposto sobre a Propriedade Predial e Territorial Urbana`, `ra` = `IPTU`)

| Valor antes                                                                                     | Rádio clicado | Passo                                 | Resultado                                                                  |
| ----------------------------------------------------------------------------------------------- | ------------- | ------------------------------------- | -------------------------------------------------------------------------- |
| `IPTU - Principal`                                                                              | Completo      | A9.3-2 (`base = ra`)                  | `Imposto sobre a Propriedade Predial e Territorial Urbana - Principal`     |
| `Imposto sobre a Propriedade Predial e Territorial Urbana - Principal`                          | Abreviado     | A9.3-2 (`base = nome_mae`)            | `IPTU - Principal`                                                         |
| `Imposto sobre Prop. Predial Terretorial Urbana - Complemento 1` (radical editado pelo usuário) | Abreviado     | A9.3-3 (strip até primeiro `-`)       | `IPTU - Complemento 1`                                                     |
| `IPTUs - Complemento 2` (typo, não casa `ra` exato)                                             | Abreviado     | A9.3-3                                | `IPTU - Complemento 2`                                                     |
| `IPTUs - Complemento 2`                                                                         | Completo      | A9.3-3                                | `Imposto sobre a Propriedade Predial e Territorial Urbana - Complemento 2` |
| `IPTU` (sem traço, regressão liberada por **G1.2**)                                             | Completo      | A9.3-4 (passo de fallback)            | `Imposto sobre a Propriedade Predial e Territorial Urbana - IPTU`          |
| `Foo` (sem traço, sem relação com radicais)                                                     | Abreviado     | A9.3-4                                | `IPTU - Foo`                                                               |
| `X -- Y` (traço duplicado consecutivo)                                                          | Abreviado     | A9.3-3 (limpeza de resíduo)           | `IPTU - Y`                                                                 |
| `X -` (traço sem complemento)                                                                   | Abreviado     | A9.3-3 (complemento vazio)            | `IPTU - `                                                                  |
| `Imposto sobre a Propriedade Predial e Territorial Urbana - `                                   | Completo      | A9.3-1 (já começa por `novo_prefixo`) | (inalterado) `Imposto sobre a Propriedade Predial e Territorial Urbana - ` |

**Exemplo A9.3-2 (Completo → Abreviado, nome_mae longo)**  
- `nome_mae` = `Imposto sobre Transmissão "Causa Mortis" e Doação de Bens e Direitos`, `ra` = `ITCD`, valor = `Imposto sobre Transmissão "Causa Mortis" e Doação de Bens e Direitos - Principal` → **Abreviado**: `ITCD - Principal`.

---

## 9. Implementação (**ITEMNOM-96**–**ITEMNOM-100**)

- **I1.** Lógica **A1–A8** em um módulo Python com testes (a parte **A1–A6** / ramos **A3** e **A8** produz o **radical**; **A7** documenta a concatenação obrigatória de **(N5)** (**ITEMNOM-06**) no valor sugerido).
- **I2.** O admin obtém o radical (ou o texto já com **(N5)** (**ITEMNOM-06**)) via endpoint *staff* ou payload embutido, sem duplicar regras de abreviação no JS.
- **I3.** Se a camada Python expuser **apenas** o radical sem **(N5)** (**ITEMNOM-06**), o cliente **deve** acrescentar **`sufixo_canônico`** ao montar `receita_nome`, de forma que o usuário veja sempre **`radical + " - "`** nos modos **Completo** e **Abreviado**, como em **(N5)** (**ITEMNOM-06**).
- **I4.** Predicados em `code_name_validation.py`, exportando no mínimo:  
  - `receita_nome_vazio_no_add(nome)` → bool (**G0.1**);  
  - `validar_receita_nome_guardrail_g0(receita_nome)` → bool (True = bloquear);  
  - `receita_nome_termina_com_traco(nome)` → bool (**G1.2** — predicado **único** de bloqueio: `^.*` + `(N7)` + `\s*$`; idêntico a **M2.1**);  
  - `radical_efetivo_para_guardrail(receita_nome_base_mode, nome_mae, radical_abreviado)` → `b` ou `None` (auxiliar para escolher a mensagem entre **G1.5.a** e **G1.5.b**; `None` em `sem_base`);  
  - `receita_nome_eh_sugestao_literal(nome, b)` → bool (True quando `n` casa com `b + (N7)` (com espaços ASCII opcionais ao redor do traço, em qualquer ortografia de **(N7)** (**ITEMNOM-07**)); usado para selecionar **G1.5.a**);  
  - `validar_receita_nome_guardrail_g1(receita_nome, nome_mae=None, radical_abreviado=None)` → tupla `(bloquear: bool, chave_mensagem: 'receita_nome_submit_sugestao_literal_error' | 'receita_nome_submit_traco_final_error' | None)`, agregando o predicado **G1.2** com a seleção entre **G1.5.a** e **G1.5.b**. **Não** depende de `receita_nome_base_mode` para bloquear; consulta `nome_mae` / `radical_abreviado` apenas para escolher a mensagem.  
  **Uso obrigatório:** `ItemClassificacaoAdminForm.clean()` em **add** — **G0.4** antes de **G1.4**; **recomenda-se** o mesmo contrato no cliente (`validateCodeNameOnSubmit`: **G0** depois **G1**).
- **I5.** Após `syncHierarchyFromCode` com `parent.found` e `parent.name`, o `change_form` (ou módulo equivalente) **deve** chamar a API JS de **P-orq.3** com `parent.pk` e `parent.name`, sem depender do disparo de `change` em `parent_item_id`.

---

## 11. Testes recomendados (**ITEMNOM-119**)

- **Ordem dos rádios:** Abreviado → Completo → Sem base.
- **P-mãe / P1:** após sucesso no lookup pelo código ou alteração de `parent_item_id`, modo **Abreviado** marcado, `receita_nome_base_mode` = `base_pai_abrev`, `receita_nome` com radical abreviado + **`" - "`** (**(N5)** (**ITEMNOM-06**)).
- **P-mãe.4:** com rádio **Completo** ou **Sem base** já selecionado, nova resolução do item mãe **força** Abreviado de novo.
- **A9.2 / P-mãe.2:** `receita_nome` = `IPVA - Principal` antes da troca do item mãe; após **P-mãe**, mantém `Principal` após o novo radical abreviado + `" - "`.
- **P-orq / P-mãe.2-bis:** após `…52.0.0…` com `Impostos sobre o Patrimônio - `, alterar `receita_cod` para `…52.0.9…` (mãe `ITCD`) → `receita_nome` = `ITCD - ` (não permanece o prefixo da mãe anterior).
- **M1 / Completo:** valor inicial `nome_mae + sufixo_canônico` (**(N5)** (**ITEMNOM-06**)); **G2.1** com «versão completa» e instrução após o traço.
- **M1.3:** valor `Principal` sem prefixo → após **Completo**, `nome_mae - Principal`; valor `ICMS - Principal` com mãe `ICMS` → **sem** duplicar `ICMS - `.
- **M1.5 / A9.3:** após **P-mãe** com `ITCD - `, clique em **Completo** → apenas `nome_mae - ` (nome longo da mãe), **sem** `ITCD` no meio; com `ITCD - Principal` → `nome_mae - Principal`.
- **A9.3.2:** nome longo da mãe + ` - Principal` → rádio **Abreviado** → `ITCD - Principal` (ou `ra` correspondente).
- **Abreviado:** **G2.2** com «versão abreviada» no início **e** `nome_mae` literal no final entre aspas; seleção de **G1.5.a** usa `b_abreviado` (saída de A1–A8) para comparação `b + (N5)`, **não** o `nome_mae` literal.
- **M2:** remoção com traços Unicode; aviso **M2.3**.
- **G1.2 / (N7) — sugestão literal Completo:** `n = nome_mae + " - "` (e variações `nome_mae + " -"`, `nome_mae + "\u2013"`, `nome_mae + "\u2014"`) → bloqueio com **G1.5.a**.
- **G1.2 / (N7) — sugestão literal Abreviado:** `n = radical_abreviado + " - "` (e variações com (N7) Unicode) → bloqueio com **G1.5.a**.
- **G1.2 — radical igual sem traço (regressão):** `n = nome_mae` ou `n = radical_abreviado` (sem traço final) → **permitido** (cobre regressão do antigo bloqueio `n === b`).
- **G1.2 — modificado com traço pendurado:** `n = "IPVA - Cota Única -"` → bloqueio com **G1.5.b** (não é sugestão literal).
- **G1.2 — `sem_base` com traço final:** modo `sem_base`, `n = "Taxa municipal -"` → bloqueio com **G1.5.b**.
- **G1.2 — `sem_base` sem traço final:** modo `sem_base`, `n = "Taxa municipal de iluminação"` → permitido.
- **G1.2 — complemento normal:** `n = "IPVA - Cota Única"`; `n = "Rec. Imposto - Carro"` → permitido nos três modos (Completo, Abreviado, Sem base).
- **G1.4 (servidor — Completo, mensagem G1.5.a):** POST em `base_pai_completo` com `n = nome_mae + " - "` → `ValidationError` em `receita_nome` com `receita_nome_submit_sugestao_literal_error`, mesmo sem JS.
- **G1.4 (servidor — `sem_base`, mensagem G1.5.b):** POST em `sem_base` com `n` terminado em traço → `ValidationError` com `receita_nome_submit_traco_final_error`.
- **G0:** POST em **add** com `receita_nome` vazio ou só espaços → rejeitado em **todos** os modos (`base_pai_abrev`, `base_pai_completo`, `sem_base`, modo vazio).
- **G0 vs G1:** `ITCD - ` → **G0** não bloqueia; **G1** bloqueia (independente do modo). `ITCD` (sem traço) → **G0** e **G1** **não** bloqueiam, mesmo em Abreviado/Completo.
- **G4:** POST com erro + modo Abreviado: `b` reidratado coerente com prefixo abreviado **só** para fins de seleção entre G1.5.a/G1.5.b e demais protocolos (P-mãe, A9.\*, M1.\*); o bloqueio **G1.2** independe de `b`.
- **A3+A6, A4+A6, A8+A6** (A6 em todos os ramos).
- **A3.2 / A1.3 / G6:** com duas linhas ativas em conflito por `norm(termo)`, alerta com `termo_nome` e **sem** aplicação de **A3.1**.
- **A3.3 / A4.1b:** `nome_mae` com um espaço e `termo` com dois espaços internos — match na passagem fallback **(N8)**; **A4.1a** sem intervalos antes do fallback.

---

## 10. Decisões de produto (**ITEMNOM-110**–**ITEMNOM-118**)

| ID  | Tema                                                     | Decisão                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| --- | -------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| D1  | `norm` e acentos                                         | **(N6):** *trim* + *case fold* Unicode; **não** remover acentos na v1.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| D2  | **G1.2** e traços Unicode                                | **(N7):** mesma noção de **separador flexível** que **M2.1**; **G1.2** obrigatório (não só recomendação).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| D3  | Duplicidade de `termo_nome` no léxico                    | **Sem desempate** (erro de BD). **A3.2**, **A1.3**, **G6**: alerta pedindo verificação na **Lista de Abreviações**.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| D4  | Espaços em comparações                                   | **(N6)** estrito na passagem primária; **(N8)** `norm_colapso_espacos` **só como fallback** em **A3.3** e **A4.1b**.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| D5  | Item mãe vs rádio (**P-mãe**)                            | Ao definir/alterar `parent_item_id`: **sempre** forçar **Abreviado** (**P-mãe.3**–**P-mãe.4**), recalcular radical (**A1–A8**), repor `receita_nome` com **A9.2** (preservar complemento após **(N7)** (**ITEMNOM-07**)). **Sobrescreve** rádio anterior (incl. **Sem base**). **Completo** só por clique (**M1**); **não** usar **M1.4** no autocomplete.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| D6  | **G1** no servidor (**I4**)                              | **Uma** definição (**G1.2**: `trim(n)` termina com **(N7)** (**ITEMNOM-07**)) aplicada em **todos** os modos do **add** (inclusive `sem_base`). Predicado de bloqueio **independe** de `receita_nome_base_mode` e do radical efetivo `b`. **Duas** mensagens em **G1.5**: **G1.5.a** quando `n` coincide com sugestão literal (`b_completo + (N5)` ou `b_abreviado + (N5)`, com (N7) flexível); **G1.5.b** caso contrário. Validação em dois pontos: cliente (**G1.1**–**G1.3**) e `ItemClassificacaoAdminForm.clean()` em **add** (**G1.4**). `radical_efetivo_para_guardrail(...)` e `receita_nome_eh_sugestao_literal(...)` continuam em **I4** para alimentar a escolha entre G1.5.a e G1.5.b. **Regressão proposital:** `n === b` (sem traço final) deixa de ser bloqueio.                                                                                                  |
| D7  | Orquestração hierarquia → **P-mãe**                      | **P-orq.1**–**P-orq.4**, **P-mãe.2-bis**, **A9.2-bis**, **I5**: após lookup por `receita_cod`, invocar **P-mãe** com `parent.name` do JSON; não depender só de `change` + rótulo DOM; na troca de mãe, não manter prefixo de sugestão literal da mãe anterior (predicado **G1.5.a**).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| D8  | **A9.3** (algoritmo unificado de troca de modo) e **G2** | **A9.3** (4 passos, indep. de `receita_nome_base_mode`): **1)** no-op se `valor` já começa por `novo_prefixo`; **2)** strip exato de qualquer base em `[radical_oposto, radical_destino]` (com **(N7)** (**ITEMNOM-07**) flexível) — **M1.5** é caso particular `Abreviado → Completo`; **3)** strip «tudo até o primeiro **(N7)** (**ITEMNOM-07**) inclusive» com limpeza iterativa de **(N7)** (**ITEMNOM-07**) residual — **corrige duplicação** quando o usuário editou o radical sugerido; **4)** se valor não tem **(N7)** (**ITEMNOM-07**), trata o valor inteiro como complemento e prepende `novo_prefixo` (regra **M1.3** antiga). Nunca empilhar prefixos. **G2.1:** «versão completa» + duas saídas (completar após o traço **ou** remover o traço final) — texto fixo. **G2.2:** «versão abreviada» + duas saídas + `nome_mae` entre aspas (template `{nome_mae}`). |
| D9  | Conectivos (SSOT + **A6**)                               | `LEXICO_CONNECTIVOS_FIXOS` e `LEXICO_PONTUACAO_OMITIR_NAS_EXTREMIDADES` em `code_name_connectives.py`; infer importa só conectivos lexicais. **A6** (pontuação + conectivos) aplica-se **sempre** ao radical (**A3**, **A4**, **A8**) antes de **A7**; ponto preservado só em token **(iv)**.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| D10 | **G0** — nome obrigatório no **add**                     | `trim(receita_nome)` vazio → bloquear **sempre** (**G0**), **independente** do rádio; **não** altera sugestão/remoção dos rádios. **G1** continua, em todos os modos (inclusive `sem_base`), para nomes terminando em **(N7)** (**ITEMNOM-07**) (ver **D6**). Ordem: **G0** → **G1**. Alinhado a `item_classificacao.yaml` (`required: true`).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |

---

### 10.1 Decisões pendentes

*(Nenhuma decisão de produto pendente.)*

---

## 12. Melhorias futuras (não normativas)

- Internacionalização em `code_name_messages.py`.
- Cache do léxico por requisição.

---
