# Item de classificação — criação no admin: nome (`receita_nome`) e modos de radical

Esta especificação define **como o fluxo deve funcionar** no formulário Django de **criação** (`add`) de `ItemClassificacao` no admin, para orientar implementação e manutenção. Abrange:

- o campo **Nome da Classificação por Natureza de Receita** (`receita_nome`);
- os **três** modos de apoio ao radical, na **ordem de exibição** definida abaixo;
- **guardrails**: validação antes de gravar, mensagens ao usuário e remoção segura do prefixo derivado do item mãe;
- o **preenchimento automático** do nome disparado a partir do **Código Canônico da Natureza de Receita** (`receita_cod`) e da resolução do item mãe;
- a **paridade** entre os modos **Completo** e **Abreviado**: após o radical, o mesmo sufixo literal de edição **`" - "`** (formalizado em **(N5)** na terminologia), para o usuário completar o nome após o traço.

**Referência no repositório (para alinhar código à spec):** `apps/core/static/core/js/classification_naming.js`, `apps/core/classification_naming_messages.py`, `apps/core/forms.py` (`ItemClassificacaoAdminForm.receita_nome_base_mode`), `apps/core/admin.py` (contexto de mensagens + *media*), fluxo de lookup/hierarquia no `change_form.html` (ex.: `syncHierarchyFromCode`, cadeia que chama `validateClassificationNamingOnSubmit`).

---

## Ordem dos rádios na interface e rótulos (obrigatório)

Na tela de criação, os três rádios **devem** aparecer **nesta ordem**, da esquerda para a direita, alinhados um ao lado do outro:

1. **«Radical Baseado no item mãe - Abreviado»** — após **A1–A8**, o valor sugerido em `receita_nome` **deve** seguir o **mesmo padrão** que o **Completo**: **`(radical abreviado) + sufixo_canônico`** (**(N5)**), *i.e.* o texto abreviado seguido de `" - "` (espaço, hífen ASCII, espaço).
2. **«Radical Baseado no item mãe - Completo»** — **`nome_mae + sufixo_canônico`** (**M1.1** e **(N5)**).
3. **«Sem Nome Base»**

O `name` HTML dos rádios de UI **deve** continuar distinto do `HiddenInput` de `receita_nome_base_mode` (ex.: `__classification_naming_base_mode_ui`), para não quebrar o comportamento nativo de rádio/hidden.

---

## Valores POST (`receita_nome_base_mode`)

*(Chaves `base_pai_*` mantêm o prefixo legado `pai` no identificador POST até a migração do código; semanticamente referem-se ao **item mãe**.)*

- **`base_pai_abrev`** — modo **Abreviado**: radical = resultado de **A1–A8**; sufixo em `receita_nome` = **(N5)** (igual ao **Completo**).
- **`base_pai_completo`** — modo **Completo** (radical = `nome_mae` literal; concatenação inicial em `receita_nome` = **(N5)**).
- **`sem_base`** — modo **Sem Nome Base** (**M2**).

---

## Preenchimento automático a partir do código canônico (`receita_cod`)

- **P1.** Ao preencher o campo **Código Canônico da Natureza de Receita** (`receita_cod`) e concluir-se com **sucesso** a cadeia que resolve o item mãe e atualiza `parent_item_id`, o sistema **deve** disparar o **protocolo do item mãe** (**P-mãe**), o mesmo que na alteração direta de `parent_item_id` (lookup de hierarquia, seleção no admin, etc.). O efeito normativo é o de **P-mãe**, não o de **M1.4** (Completo automático).

### Protocolo ao definir ou alterar o item mãe (`parent_item_id`) — **P-mãe**

Disparado quando `parent_item_id` recebe ou altera valor (incluindo após `syncHierarchyFromCode` / lookup por `receita_cod`, seleção manual do item mãe ou repovoamento equivalente no cliente — ex.: função análoga a `applyReceitaNomeBaseFromParent` no JS legado).

- **P-mãe.1.** **Deve** obter `nome_mae` do rótulo de `parent_item_id` (**M1.2**) e calcular `radical_abreviado` conforme **B0.2** + protocolo **A1–A8**.
- **P-mãe.2.** **Deve** atualizar `receita_nome` para **`radical_abreviado + sufixo_canônico`** (**(N5)**), aplicando **A9.2**: se o valor anterior já tiver **complemento** não vazio após o primeiro **separador flexível** **(N7)**, **preservar** esse trecho (ex.: `IPVA - Principal` → novo radical abreviado + `" - "` + `Principal`).
- **P-mãe.3.** **Deve** marcar o rádio **«Radical Baseado no item mãe - Abreviado»** e definir `receita_nome_base_mode` = `base_pai_abrev`.
- **P-mãe.4.** **Deve sobrescrever** qualquer modo de radical previamente selecionado (**Completo**, **Sem base** ou **Abreviado** de interação anterior), **mesmo** que o usuário já tivesse escolhido outro rádio antes do repovoamento do item mãe.
- **P-mãe.5.** O modo **Completo** **não** é aplicado por este protocolo; só entra em vigor pelo clique explícito do usuário no rádio **«Radical Baseado no item mãe - Completo»** (**M1.1**–**M1.3**). O modo **Sem base** também **não** permanece após **P-mãe** — o repovoamento do item mãe **sempre** retorna ao **Abreviado** (**P-mãe.3**–**P-mãe.4**).

---

## Relação com outras specs e código

- **Lista de abreviações:** no modo **Abreviado**, aplicam-se, quando couber, as noções de *segmento*, *abreviação*, *sigla* e *conectivos* de `_dev/spec_lista_abreviacoes.md`. A lista fixa de conectivos para compactação está em `apps/core/classification_naming_connectives.py` (`NOME_CLASSIFICACAO_CONNECTIVOS_FIXOS`).
- **Léxico ativo:** `queryset_alias_lexico_ativos()` e `iter_alias_lexico_ativos_ordenados()` em `apps/core/alias_lexico_service.py`.
- **Resolução do item mãe:** `_dev/spec_lookup_hierarquia_por_codigo_admin.md` (rótulo `receita_cod - receita_nome` para extrair `nome_mae`).

---

## Escopo e fora de escopo

- **Escopo:** tela de **add**; `receita_nome`; `receita_nome_base_mode`; rádios; integração com preenchimento a partir de `receita_cod` / lookup do item mãe (**P-mãe**).
- **Escopo (validação):** a regra **G1** no **cliente** (`validateClassificationNamingOnSubmit` / `setCustomValidity`) **e** no **servidor** (`ItemClassificacaoAdminForm.clean()` na tela **add**), com a **mesma** definição de sugestão incompleta (**G1.2**, **I4**).
- **Fora de escopo:** `INSERT` em `AliasLexico` a partir desta tela; alteração do seed.

---

## Alinhamento terminológico

- **(N1) `nome_mae`:** nome completo do item mãe, obtido do rótulo de `parent_item_id`, texto à **direita** de `" - "` após o código (vide **M1.2**). Usado na mensagem informativa do modo **Abreviado** (**G2**) e como entrada do protocolo **A1–A8**.
- **(N2) `radical` (operacional):** nos modos com base no item mãe, é o **trecho inicial** de `receita_nome` **antes** do primeiro `sufixo_canônico` **(N5)** — no **Completo**, coincide com `nome_mae` (*trim*); no **Abreviado**, coincide com a saída textual de **A1–A8** (*trim*), **não** com `nome_mae` literal. No modo **sem base**, o sistema não impõe esse prefixo.
- **(N3)** Valores POST: **«Ordem dos rádios»** e seção **Valores POST** acima.
- **(N4) `léxico` / `norm` / substituição:** modo **Abreviado**; ver **Protocolo A1–A9**.
- **(N5) `sufixo_canônico de edição`:** a sequência literal **`" - "`** (espaço, hífen ASCII U+002D, espaço). Nos modos **Completo** e **Abreviado**, sempre que houver radical não vazio a sugerir, o valor inicial (ou reposto) de `receita_nome` **deve** ser **`radical + sufixo_canônico`**, *sem* substituir o hífen ASCII por en dash/em dash na **sugestão automática** — o mesmo padrão visual e de edição nos dois modos; o usuário completa o nome **após** esse sufixo. (Remoção com separadores flexíveis continua a cargo de **M2** ao mudar para **sem base**.)
- **(N6) `norm` (comparação estrita na v1):** usada em **A3.1** (passagem primária), **A1.3** e **A3.2** (detecção de duplicidade). **Definição:** *trim* em cada operando + **case folding** Unicode (em Python: `str.casefold()`; em JavaScript: usar API equivalente a *case fold* quando disponível, ou documentar o desvio se usar apenas `toLowerCase()`). **Espaços internos:** **não** colapsar na passagem estrita. **Acentos:** **não** remover diacríticos; grafias com e sem acento **não** se tratam como iguais (ex.: `Taxa` ≠ `Taxá`).
- **(N8) `norm_colapso_espacos` (fallback de comparação):** aplicar **(N6)** e, em seguida, colapsar **espaços internos** (qualquer sequência de espaços em branco no meio da string vira **um** espaço ASCII). Usada **somente** quando a passagem estrita correspondente **não** produzir resultado (**A3.3**, **A4.1b**). Se dois `termo` distintos no banco colidirem após **(N8)**, tratar como duplicidade conforme **A1.3** / **G6** (**D3**), não como desempate.
- **(N7) `separador flexível`:** imediatamente após o radical `b`, a sequência composta por: espaços em branco opcionais; **um** caractere traço entre hífen ASCII U+002D (`-`), en dash U+2013 (`\u2013`) ou em dash U+2014 (`\u2014`); espaços em branco opcionais. **Usado em** **M2.1** (remoção do prefixo ao mudar para **sem base**) e **G1.2** (detecção de sugestão incompleta). **Distinto de (N5):** a **sugestão automática** do sistema continua a usar apenas **`sufixo_canônico`** **(N5)** (`" - "` com hífen ASCII); o usuário pode digitar **(N7)** no campo, e **G1.2** **deve** tratá-lo como «só radical + separador, sem complemento», à mesma lógica de **M2.1**.

---

## Modo «Radical Baseado no item mãe - Completo» (`base_pai_completo`)

### Requisitos (M1)

- **M1.1.** Com este modo selecionado e `nome_mae` conhecido (*trim* não vazio), `receita_nome` **deve começar** por `nome_mae + sufixo_canônico` (**(N5)**).
- **M1.2.** `nome_mae` **deve** ser extraído do rótulo de `parent_item_id` (texto após `" - "` no *link*). Se o item mãe não tiver nome, o radical fica vazio e **M1.1** não se aplica.
- **M1.3.** Ao selecionar de novo este modo com o campo já editado: se o valor **não** começar por `nome_mae + sufixo_canônico` (**(N5)**), o sistema **deve prefixar** esse prefixo ao valor atual.
- **M1.4.** **Não** se aplica ao repovoamento automático do item mãe (**P-mãe**). Quando o **usuário** clica explicitamente neste rádio, valem **M1.1**–**M1.3**; qualquer nova definição ou troca de `parent_item_id` dispara **P-mãe** (Abreviado), **não** **M1.4**.

**Exemplo M1.1**  
- `nome_mae` = `Imposto sobre Transmissão "Causa Mortis" e Doação de Bens e Direitos` → `receita_nome` = `Imposto sobre Transmissão "Causa Mortis" e Doação de Bens e Direitos - `.

**Exemplo M1.3**  
- Valor `ICMS - Principal`, modo Completo com item mãe `ICMS` e valor que não começa por `ICMS - ` → prefixação → `ICMS - ICMS - Principal` (efeito colateral documentado).

---

## Modo «Sem Nome Base» (`sem_base`) — M2

### Requisitos

- **M2.1.** Ao selecionar este modo, **remover** do início de `receita_nome` o **radical atualmente conhecido** na UI (`currentParentNameBase` ou equivalente — seja ele o `nome_mae` literal do modo **Completo** ou o radical **abreviado** do modo **Abreviado**), seguido do **separador flexível** (**(N7)**).
- **M2.2.** Se **M2.1** não casar, tentar remoção **estrita** do prefixo `texto_radical_conhecido + sufixo_canônico` (**(N5)**) quando o valor começar exatamente por essa string — onde `texto_radical_conhecido` é o radical que o modo ativo colocou **antes** do sufixo canônico.
- **M2.3.** Se o valor ainda começar pelo radical conhecido sem separador válido, exibir aviso `remove_base_prefix_mismatch`.
- **M2.4.** `receita_nome_base_mode` = `sem_base`.

**Exemplo M2.1**  
- Radical conhecido = `ICMS`; `receita_nome` = `ICMS\u2013Principal` → `Principal`.

---

## Modo «Radical Baseado no item mãe - Abreviado» (`base_pai_abrev`) — B0

### Requisitos gerais

- **B0.1.** Este modo corresponde ao **primeiro** rádio na ordem da UI.
- **B0.2.** O **radical abreviado** (trecho que alimenta **(N2)** no modo **Abreviado**) **deve** ser calculado pelo protocolo **A1–A8** a partir de `nome_mae` e do léxico ativo. As etapas **A1–A6** produzem apenas esse texto (sem o sufixo de edição).
- **B0.3.** **Paridade com o modo Completo:** após obter o radical abreviado (*trim* não vazio), o valor colocado em `receita_nome` **deve** ser **`radical_abreviado + sufixo_canônico`** (**(N5)**) — o **mesmo** literal `" - "` que em **M1.1**; **não** basta o radical sozinho no campo quando o sistema sugere o nome.
- **B0.4.** Quando **P-mãe** recalcula o item mãe, o radical abreviado e `receita_nome` seguem **P-mãe.2** e **A9.2** (preservar complemento após o separador). Com este modo já selecionado **sem** troca de item mãe, recálculos internos obedecem **A9**.

---

## Guardrails — validação, mensagens e ciclo de vida

### G1 — Bloqueio de envio: nome só com radical + separador (incompleto)

**Paridade entre modos:** **G1** aplica-se nos modos **Completo** e **Abreviado** de forma **simétrica**: em cada um, `b` é o radical que o sistema sugeriria **antes** do traço; bloqueia-se gravar item novo cujo `receita_nome` seja **igual** a esse radical ou **igual** à sugestão automática incompleta (`b` + separador **(N7)** sem complemento). No modo **Sem base** (**M2**), **G1** **não** se aplica.

- **G1.1 (cliente).** Na tela **add**, após validações de código e hierarquia, executar `validateClassificationNamingOnSubmit`. Se existir radical do item mãe conhecido (**G4**), `receita_nome_base_mode` for **Completo** ou **Abreviado**, e `trim(receita_nome)` for **sugestão incompleta** (**G1.2**), **bloquear** o envio no navegador.
- **G1.2 (definição canônica).** Seja `b` o *trim* do **radical efetivo** conforme `receita_nome_base_mode` e o item mãe resolvido:  
  - **`base_pai_completo`** ou legado **`base_pai`:** `b = trim(nome_mae)` do `parent_item_id`;  
  - **`base_pai_abrev`:** `b = trim(radical_abreviado)` (saída de **A1–A8** / **B0.2**, **não** o `nome_mae` literal);  
  - **`sem_base`** ou vazio: **não** avaliar **G1** (`b` indefinido).  
  Seja `n = trim(receita_nome)`. **Sugestão incompleta** quando:  
  1. `n` for **igual** a `b` (nome **exatamente** o radical sugerido, sem traço); **ou**  
  2. `n` corresponder a **`b` + separador flexível (N7)**, opcionalmente seguido **apenas** de espaços em branco até o fim — **sem** caractere não branco após o traço do **(N7)** (radical + traço, sem complemento).  
  A detecção **deve** usar a **mesma** definição de separador que **M2.1** (hífen ASCII, en dash, em dash; espaços opcionais à volta do traço). **(N5)** é caso particular de **(N7)**.  
  **Requisito:** não gravar item novo em **add** cujo nome esteja em qualquer um desses estados incompletos, quer o radical seja o **nome completo** da mãe ou o **abreviado**.
- **G1.3 (cliente — feedback).** Ao bloquear no navegador: `setCustomValidity` com `receita_nome_submit_incompleto_error`, erro no campo e nota no topo (ex.: «Por favor, corrija o erro abaixo.»).
- **G1.4 (servidor — obrigatório).** Em `ItemClassificacaoAdminForm.clean()` na tela **add**, **deve** repetir **G1.2** com os mesmos `b`, `n` e modo (normalizar `base_pai` → `base_pai_completo`). Se incompleto, `ValidationError` em `receita_nome` com o texto **G1.5**. Obter `nome_mae` de `parent_item_id` resolvido; obter `radical_abreviado` via módulo **I1** / **I4**, sem duplicar **A1–A8** no formulário.
- **G1.5 (mensagem de erro).** Texto único em `classification_naming_messages.py` (`receita_nome_submit_incompleto_error`), usado no cliente (**G1.3**) e no servidor (**G1.4**). Redação em português do Brasil, citando **item mãe** e a necessidade de completar o nome **após o traço** (ou remover o traço se o usuário quiser repetir só o radical). Exemplo normativo:  
  `Atualize o nome da classificação após o traço para concluir o cadastro, ou remova o traço se não quiser um complemento além do radical sugerido (completo ou abreviado) com base no item mãe.`

**Exemplo G1.2 (Abreviado — só radical)**  
- `b` = `Rest. Progressiva IPVA`; `n` = `Rest. Progressiva IPVA` → **bloqueado** (igual a `b`).

**Exemplo G1.2 (Abreviado — radical + traço)**  
- `nome_mae` longo, `b` = `Rest. Progressiva IPVA`; `n` = `Rest. Progressiva IPVA - ` → **bloqueado**.

**Exemplo G1.2 (Completo)**  
- `b` = `IPVA`; `n` = `IPVA - Principal` → **permitido**.

**Exemplo G1.2 (separador flexível — alinhado a M2.1)**  
- `b` = `IPVA`; `n` = `IPVA - ` → **bloqueado** (caso **(N5)** / ASCII).  
- `b` = `IPVA`; `n` = `IPVA\u2013` (en dash, sem complemento) → **bloqueado**.  
- `b` = `IPVA`; `n` = `IPVA\u2013Principal` → **permitido**.

**Exemplo G1.2 (fora de G1)**  
- Modo **Abreviado**, `b` = `IPVA`, `n` = nome longo literal da mãe (diferente de `b`) → **permitido** por **G1** (não confundir com regra de duplicidade semântica entre itens).

### G2 — Mensagens informativas (antes do envio)

- **G2.0.** Enquanto o predicado de **sugestão incompleta** de **G1.2** for verdadeiro e houver radical conhecido, **deve** exibir-se mensagem informativa azul; o **texto** depende do modo:

- **G2.1 — Modo Completo (`base_pai_completo`):**  
  **Texto fixo:**  
  `Nome sugerido com base no item mãe selecionado.`  
  (Chave sugerida na implementação: ex. `receita_nome_sugestao_info_completo`.)

- **G2.2 — Modo Abreviado (`base_pai_abrev`):**  
  **Texto:**  
  `Nome sugerido com base no item mãe selecionado. Complete o nome desta classificação após o traço. O nome do item mãe é "` + **valor literal de `nome_mae`** + `"`  
  (aspas delimitadoras literais ao redor do nome do item mãe para clareza; escapar aspas internas de `nome_mae` na implementação se necessário). Chave sugerida: `receita_nome_sugestao_info_abrev` como *template* com placeholder `{nome_mae}`.

- **G2.3.** No evento `input` de `receita_nome`, limpar *customValidity*, mensagens locais de naming e *errornote* associada.

**Exemplo G2.2**  
- `nome_mae` = `Imposto sobre Transmissão "Causa Mortis" e Doação de Bens e Direitos` → fragmento final: `... O nome do item mãe é "Imposto sobre Transmissão "Causa Mortis" e Doação de Bens e Direitos"` (com regras de escape definidas no código).

### G3 — Limpeza ao remover o item mãe

- **G3.1.** Se `parent_item_id` ficar vazio, limpar rádios, oculto `receita_nome_base_mode`, estado do radical e mensagens.

### G4 — Hidratação após POST com erro

- **G4.1.** Se o formulário retornar com `parent_item_id` e `receita_nome` preenchidos, reidratar o estado do radical pelo rótulo ou, se necessário, inferir o prefixo antes do primeiro separador flexível (**M2.1**), **em consistência** com `receita_nome_base_mode` salvo. No modo **Abreviado**, o valor de `b` usado em **G1.2** **deve** corresponder ao radical abreviado associado ao prefixo atual de `receita_nome`, coerente com **`base_pai_abrev`**.

### G5 — Ordem na cadeia de envio

- **G5.1.** Validação de naming **depois** de validação de código e `syncHierarchyFromCode` com sucesso, **antes** de confirmações adicionais e *submit* nativo.

### G6 — Alerta: `termo_nome` duplicado na Lista de Abreviações

- **G6.1.** Quando **A3.2** ou **A1.3** se aplicar, o sistema **deve** exibir alerta **visível** ao usuário (ex.: mensagem de aviso amarela junto ao campo `receita_nome` ou nota no topo do formulário, no mesmo espírito de `remove_base_prefix_mismatch`), **sem** substituir silenciosamente uma abreviação por outra.
- **G6.2.** **Texto obrigatório** (pode ser *template* em `classification_naming_messages.py`, chave sugerida `receita_nome_lexico_termo_duplicado`):  
  `Verifique na Lista de Abreviações: o termo_nome «{termo_nome}» está duplicado (há mais de um registro ativo).`  
  O placeholder `{termo_nome}` **deve** ser preenchido com o valor acordado em **A3.2** (`nome_mae`) ou **A1.3** (campo `termo` da linha em conflito).
- **G6.3.** Este alerta **não** bloqueia por si só o envio do formulário de criação do item (diferente de **G1**); informa inconsistência de dados para correção na **Lista de Abreviações** no admin.

**Exemplo G6.2**  
- `nome_mae` = `Principal`; duas linhas ativas com `norm(termo)` igual → alerta: `Verifique na Lista de Abreviações: o termo_nome «Principal» está duplicado (há mais de um registro ativo).`

---

## Protocolo do modo Abreviado (regras A1–A9)

*(ND) = transformação sobre `nome_mae` e léxico.*

- **Paridade com o modo Completo (sufixo):** o valor sugerido em `receita_nome` nos dois modos com base no item mãe **sempre** observa **`radical + sufixo_canônico`** (**(N5)**). No **Abreviado**, o protocolo abaixo define só o **radical**; a regra **A7** fecha o contrato concatenando **(N5)** ao resultado de **A1–A6**, em espelho de **M1.1**.

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

- **A3.1.** **Passagem estrita:** se existir **exatamente uma** linha ativa em que `norm(termo) == norm(nome_mae)` (**(N6)**), o radical interno = `abreviacao` dessa linha (*strip*), sem A4–A6; em seguida **A7** aplica **`+ sufixo_canônico`** em `receita_nome`.
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

### Regra A6 (ND) — Conectivos

- **A6.1–A6.3.** Tokenizar por espaços; remover tokens em `NOME_CLASSIFICACAO_CONNECTIVOS_FIXOS`; reunir com um espaço.

### Regra A7 (ND) — Concatenação do sufixo canônico (igual ao Completo)

- **A7.1.** Se o radical produzido por **A1–A6** (ou por **A3** / **A8** conforme o ramo) for **não vazio** após *trim*, o valor a atribuir a `receita_nome` na sugestão **deve** ser **`radical + sufixo_canônico`** (**(N5)**), *i.e.* o mesmo padrão **`… + " - "`** que **M1.1** no modo **Completo**.
- **A7.2.** Se o radical for vazio, **não** aplicar sufixo canônico por omissão (alinhado à exceção de **M1.1** quando não há `nome_mae`).

### Regra A8 (ND) — Nenhuma substituição

- **A8.1.** Sem A3 nem A4 → o radical interno = `nome_mae.strip()`; em seguida **A7** aplica **`+ sufixo_canônico`**; recomenda-se aviso de léxico não aplicável.

### Regra A9 (ND) — Mudança de modo ou item mãe

- **A9.1.** Recalcular sugestão.
- **A9.2.** Ao repor o radical (mudança de modo, **P-mãe** ou recálculo do abreviado): se `receita_nome` contiver um **separador flexível** **(N7)** seguido de **complemento** não vazio (texto após o traço, com pelo menos um caractere não branco), o novo valor **deve** ser **`(novo_radical) + sufixo_canônico`** (**(N5)**) **concatenado ao complemento preservado** — o mesmo trecho que estava após o separador, sem reinterpretar nem descartar (ex.: `… - Principal` mantém `Principal` quando o item mãe muda e **P-mãe** força Abreviado). Se **não** houver complemento (sugestão incompleta conforme **G1.2** ou valor vazio após o separador), aplicar apenas **`novo_radical + sufixo_canônico`** (**(N5)**).

---

## Implementação canônica do radical abreviado e de **G1**

- **I1.** Lógica **A1–A8** em um módulo Python com testes (a parte **A1–A6** / ramos **A3** e **A8** produz o **radical**; **A7** documenta a concatenação obrigatória de **(N5)** no valor sugerido).
- **I2.** O admin obtém o radical (ou o texto já com **(N5)**) via endpoint *staff* ou payload embutido, sem duplicar regras de abreviação no JS.
- **I3.** Se a camada Python expuser **apenas** o radical sem **(N5)**, o cliente **deve** acrescentar **`sufixo_canônico`** ao montar `receita_nome`, de forma que o usuário veja sempre **`radical + " - "`** nos modos **Completo** e **Abreviado**, como em **(N5)**.
- **I4.** Predicado **G1.2** em funções Python reutilizáveis (ex.: módulo `classification_naming_validation.py`), exportando no mínimo:  
  - `radical_efetivo_para_guardrail(receita_nome_base_mode, nome_mae, radical_abreviado)` → `b` ou `None` (**sem_base**);  
  - `receita_nome_eh_sugestao_incompleta(nome, radical)` → bool, com **(N7)** idêntico a **M2.1**.  
  **Uso obrigatório:** `ItemClassificacaoAdminForm.clean()` (**G1.4**); **recomenda-se** o mesmo contrato no cliente (paridade com `validateClassificationNamingOnSubmit`), sem segunda implementação divergente de **(N7)** ou de `b` no modo **Abreviado**.

---

## Testes automatizados (recomendados)

- **Ordem dos rádios:** Abreviado → Completo → Sem base.
- **P-mãe / P1:** após sucesso no lookup pelo código ou alteração de `parent_item_id`, modo **Abreviado** marcado, `receita_nome_base_mode` = `base_pai_abrev`, `receita_nome` com radical abreviado + **`" - "`** (**(N5)**).
- **P-mãe.4:** com rádio **Completo** ou **Sem base** já selecionado, nova resolução do item mãe **força** Abreviado de novo.
- **A9.2 / P-mãe.2:** `receita_nome` = `IPVA - Principal` antes da troca do item mãe; após **P-mãe**, mantém `Principal` após o novo radical abreviado + `" - "`.
- **M1 / Completo:** valor inicial `nome_mae + sufixo_canônico` (**(N5)**); **G2.1** com texto fixo.
- **Abreviado:** **G2.2** contém `nome_mae` literal; **G1** com `b` = radical abreviado.
- **M2:** remoção com traços Unicode; aviso **M2.3**.
- **G1.2 / (N7):** bloqueio de envio com `IPVA - `, `IPVA\u2013` e liberação com `IPVA - Principal` (mesma lógica de separador que **M2.1**), nos modos **Completo** e **Abreviado**.
- **G1.2:** `n === b` (só radical, sem traço) → bloqueado em ambos os modos.
- **G1.4 (servidor):** `ItemClassificacaoAdminForm` em **add** rejeita POST com `receita_nome` incompleto mesmo sem JS; modo **Abreviado** usa `b` abreviado, não `nome_mae` longo.
- **G1 / sem_base:** POST com `sem_base` e `IPVA - ` → **não** falha **G1**.
- **G4:** POST com erro + modo Abreviado: `b` em **G1.2** coerente com prefixo abreviado.
- **A3, A4+A6, A8.**
- **A3.2 / A1.3 / G6:** com duas linhas ativas em conflito por `norm(termo)`, alerta com `termo_nome` e **sem** aplicação de **A3.1**.
- **A3.3 / A4.1b:** `nome_mae` com um espaço e `termo` com dois espaços internos — match na passagem fallback **(N8)**; **A4.1a** sem intervalos antes do fallback.

---

## Decisões alinhadas

| ID | Tema | Decisão |
|----|------|---------|
| D1 | `norm` e acentos | **(N6):** *trim* + *case fold* Unicode; **não** remover acentos na v1. |
| D2 | **G1.2** e traços Unicode | **(N7):** mesma noção de **separador flexível** que **M2.1**; **G1.2** obrigatório (não só recomendação). |
| D3 | Duplicidade de `termo_nome` no léxico | **Sem desempate** (erro de BD). **A3.2**, **A1.3**, **G6**: alerta pedindo verificação na **Lista de Abreviações**. |
| D4 | Espaços em comparações | **(N6)** estrito na passagem primária; **(N8)** `norm_colapso_espacos` **só como fallback** em **A3.3** e **A4.1b**. |
| D5 | Item mãe vs rádio (**P-mãe**) | Ao definir/alterar `parent_item_id`: **sempre** forçar **Abreviado** (**P-mãe.3**–**P-mãe.4**), recalcular radical (**A1–A8**), repor `receita_nome` com **A9.2** (preservar complemento após **(N7)**). **Sobrescreve** rádio anterior (incl. **Sem base**). **Completo** só por clique (**M1**); **não** usar **M1.4** no autocomplete. |
| D6 | **G1** no servidor (**I4**) | **Uma** definição (**G1.2**); **dois** pontos de aplicação: cliente (**G1.1**–**G1.3**) e `ItemClassificacaoAdminForm.clean()` em **add** (**G1.4**). **Paridade Completo / Abreviado:** `b` = `nome_mae` ou `radical_abreviado`; bloqueia `n === b` e `n === b + (N7)` sem complemento. **`sem_base`:** fora de **G1**. Mensagem única **G1.5**. |

---

## Decisões pendentes e refinamentos

*(Nenhuma decisão de produto pendente nesta spec; implementação no código conforme seções acima.)*

---

## Melhorias futuras opcionais

- Internacionalização em `classification_naming_messages.py`.
- Cache do léxico por requisição.

---

## Notas de desenvolvimento (alterações em relação ao código legado)

Esta seção **não** faz parte do contrato normativo; serve só para quem migra ou compara com o repositório **antes** das mudanças alinhadas a esta spec.

- **Terminologia item mãe:** a spec e a UI usam **item mãe** / `nome_mae`; o código legado ainda fala em «pai», `nome_pai`, `applyReceitaNomeBaseFromParent`, etc. A migração de scripts fica fora desta spec; até lá, mapear mentalmente `parent_item_id` → item mãe.

- **Rótulo e valor POST do modo «literal da mãe»:** no código legado, o rádio aparecia como *«Radical Baseado no item mãe»* e o valor POST costumava ser `base_pai`. A spec exige **«Radical Baseado no item mãe - Completo»** e **`base_pai_completo`**. Convém aceitar `base_pai` como sinônimo na leitura do POST até remover o legado.

- **`applyReceitaNomeBaseFromParent` (legado):** hoje preenche `nome_mae` literal + ` - `, marca modo completo e grava `base_pai`. A spec exige **P-mãe**: radical **abreviado**, rádio **Abreviado**, `base_pai_abrev`, com **A9.2** no complemento.

- **Autocomplete / `receita_cod`:** após sucesso na hierarquia, dispara **P-mãe** (**P1**), não o fluxo completo legado nem **M1.4**.

- **Mensagem informativa única no legado:** `RECEITA_NOME_SUGESTAO_INFO` juntava a frase curta com *«Complete o nome…»*. A spec **separa**: **G2.1** (só a primeira frase no modo **Completo**) e **G2.2** (texto longo com `{nome_mae}` no modo **Abreviado**).

- **Guardrail G1:** no legado, o predicado de incompleto usava só `nome_mae` literal e separador ASCII fraco. A spec exige **G1.2** + **(N7)** nos modos **Completo** e **Abreviado**, cliente e servidor (**D6** / **I4**). `ItemClassificacaoAdminForm.clean()` ainda **não** valida — implementar **G1.4**.

- **Ordem dos rádios no HTML:** a spec exige Abreviado primeiro, depois Completo, depois Sem Nome Base; o legado tinha só dois rádios (Completo e Sem base) noutra ordem — ajustar markup e lógica de *default* / *checked*.
