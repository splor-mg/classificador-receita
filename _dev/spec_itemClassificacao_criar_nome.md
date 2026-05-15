# Item de classificação — criação no admin: nome (`receita_nome`) e modos de radical

Esta especificação define **como o fluxo deve funcionar** no formulário Django de **criação** (`add`) de `ItemClassificacao` no admin, para orientar implementação e manutenção. Abrange:

- o campo **Nome da Classificação por Natureza de Receita** (`receita_nome`);
- os **três** modos de apoio ao radical, na **ordem de exibição** definida abaixo;
- **guardrails**: validação antes de gravar, mensagens ao usuário e remoção segura do prefixo derivado do item pai;
- o **preenchimento automático** do nome disparado a partir do **Código Canônico da Natureza de Receita** (`receita_cod`) e da resolução do item pai;
- a **paridade** entre os modos **Completo** e **Abreviado**: após o radical, o mesmo sufixo literal de edição **`" - "`** (formalizado em **(N5)** na terminologia), para o usuário completar o nome após o traço.

**Referência no repositório (para alinhar código à spec):** `apps/core/static/core/js/classification_naming.js`, `apps/core/classification_naming_messages.py`, `apps/core/forms.py` (`ItemClassificacaoAdminForm.receita_nome_base_mode`), `apps/core/admin.py` (contexto de mensagens + *media*), fluxo de lookup/hierarquia no `change_form.html` (ex.: `syncHierarchyFromCode`, cadeia que chama `validateClassificationNamingOnSubmit`).

---

## Ordem dos rádios na interface e rótulos (obrigatório)

Na tela de criação, os três rádios **devem** aparecer **nesta ordem**, da esquerda para a direita, alinhados um ao lado do outro:

1. **«Radical Baseado no Item Pai - Abreviado»** — após **A1–A8**, o valor sugerido em `receita_nome` **deve** seguir o **mesmo padrão** que o **Completo**: **`(radical abreviado) + sufixo_canônico`** (**(N5)**), *i.e.* o texto abreviado seguido de `" - "` (espaço, hífen ASCII, espaço).
2. **«Radical Baseado no Item Pai - Completo»** — **`nome_pai + sufixo_canônico`** (**M1.1** e **(N5)**).
3. **«Sem Nome Base»**

O `name` HTML dos rádios de UI **deve** continuar distinto do `HiddenInput` de `receita_nome_base_mode` (ex.: `__classification_naming_base_mode_ui`), para não quebrar o comportamento nativo de rádio/hidden.

---

## Valores POST (`receita_nome_base_mode`)

- **`base_pai_abrev`** — modo **Abreviado**: radical = resultado de **A1–A8**; sufixo em `receita_nome` = **(N5)** (igual ao **Completo**).
- **`base_pai_completo`** — modo **Completo** (radical = `nome_pai` literal; concatenação inicial em `receita_nome` = **(N5)**).
- **`sem_base`** — modo **Sem Nome Base** (**M2**).

---

## Preenchimento automático a partir do código canônico (`receita_cod`)

- **P1.** Ao preencher o campo **Código Canônico da Natureza de Receita** (`receita_cod`) e concluir-se com **sucesso** a cadeia que resolve o item pai e atualiza o nome (autocomplete / repovoamento de `receita_nome`), o sistema **deve**, por **omissão**, aplicar o modo **«Radical Baseado no Item Pai - Abreviado»**: calcular o radical conforme **B0** + protocolo **A1–A8**; em seguida preencher `receita_nome` com **`(radical abreviado) + sufixo_canônico`** (**(N5)**), *no mesmo formato* que o modo **Completo** usa com `nome_pai`; marcar o **primeiro** rádio e definir `receita_nome_base_mode` = `base_pai_abrev`.
- **P2.** Se o usuário **já tiver escolhido explicitamente** outro modo de radical (rádio) antes do resultado do lookup, **recomenda-se** **não** sobrescrever essa escolha ao receber a resposta do código: atualizar `nome_pai` / estado necessário e, se aplicável, recalcular o radical **no modo já selecionado**. A regra de produto em **P1** vale como padrão do autocomplete quando **não** há escolha prévia conflitante (detalhe de implementação: ver **D5**).

---

## Relação com outras specs e código

- **Lista de abreviações:** no modo **Abreviado**, aplicam-se, quando couber, as noções de *segmento*, *abreviação*, *sigla* e *conectivos* de `_dev/spec_lista_abreviacoes.md`. A lista fixa de conectivos para compactação está em `apps/core/classification_naming_connectives.py` (`NOME_CLASSIFICACAO_CONNECTIVOS_FIXOS`).
- **Léxico ativo:** `queryset_alias_lexico_ativos()` e `iter_alias_lexico_ativos_ordenados()` em `apps/core/alias_lexico_service.py`.
- **Resolução do item pai:** `_dev/spec_lookup_hierarquia_por_codigo_admin.md` (rótulo `receita_cod - receita_nome` para extrair `nome_pai`).

---

## Escopo e fora de escopo

- **Escopo:** tela de **add**; `receita_nome`; `receita_nome_base_mode`; rádios; integração com preenchimento a partir de `receita_cod` / lookup de pai.
- **Escopo (validação):** a regra **G1** no cliente (`setCustomValidity` + bloqueio do envio). **Recomenda-se** espelhar **G1** em `clean()` ou no `ModelAdmin`.
- **Fora de escopo:** `INSERT` em `AliasLexico` a partir desta tela; alteração do seed.

---

## Alinhamento terminológico

- **(N1) `nome_pai`:** nome completo do item pai, obtido do rótulo de `parent_item_id`, texto à **direita** de `" - "` após o código (vide **M1.2**). Usado na mensagem informativa do modo **Abreviado** (**G2**) e como entrada do protocolo **A1–A8**.
- **(N2) `radical` (operacional):** nos modos com base no pai, é o **trecho inicial** de `receita_nome` **antes** do primeiro `sufixo_canônico` **(N5)** — no **Completo**, coincide com `nome_pai` (*trim*); no **Abreviado**, coincide com a saída textual de **A1–A8** (*trim*), **não** com `nome_pai` literal. No modo **sem base**, o sistema não impõe esse prefixo.
- **(N3)** Valores POST: **«Ordem dos rádios»** e secção **Valores POST** acima.
- **(N4) `léxico` / `norm` / substituição:** modo **Abreviado**; ver **Protocolo A1–A9**.
- **(N5) `sufixo_canônico de edição`:** a sequência literal **`" - "`** (espaço, hífen ASCII U+002D, espaço). Nos modos **Completo** e **Abreviado**, sempre que houver radical não vazio a sugerir, o valor inicial (ou reposto) de `receita_nome` **deve** ser **`radical + sufixo_canônico`**, *sem* substituir o hífen ASCII por en dash/em dash na **sugestão automática** — o mesmo padrão visual e de edição nos dois modos; o usuário completa o nome **após** esse sufixo. (Remoção com separadores flexíveis continua a cargo de **M2** ao mudar para **sem base**.)
- **(N6) `norm` (comparação de strings na v1):** usada em **A3.1** (e em qualquer outra igualdade «exata» que referencie `norm` nesta spec). **Definição:** aplicar *trim* em cada operando e comparar com **case folding** Unicode (em Python: `str.casefold()`; em JavaScript: `String.prototype.toLowerCase()` **não** substitui totalmente o *case fold* do Unicode — a implementação **deve** usar API equivalente a `casefold` quando disponível, ou documentar o desvio). **Acentos:** **não** remover diacríticos nem aplicar descomposição NFD/NFC além da exigida pela própria API de *case fold* do runtime; grafias com e sem acento **não** se tratam como iguais só por **(N6)** (ex.: `Taxa` ≠ `Taxá` para efeito de match). **Racional:** manter correspondência com o texto tal como gravado no léxico e em `nome_pai`, evitando *matches* espúrios e ambiguidade na v1. **Evolução (opcional):** ver *Melhorias futuras opcionais*.

---

## Modo «Radical Baseado no Item Pai - Completo» (`base_pai_completo`)

### Requisitos (M1)

- **M1.1.** Com este modo selecionado e `nome_pai` conhecido (*trim* não vazio), `receita_nome` **deve começar** por `nome_pai + sufixo_canônico` (**(N5)**).
- **M1.2.** `nome_pai` **deve** ser extraído do rótulo de `parent_item_id` (texto após `" - "` no *link*). Se o pai não tiver nome, o radical fica vazio e **M1.1** não se aplica.
- **M1.3.** Ao selecionar de novo este modo com o campo já editado: se o valor **não** começar por `nome_pai + sufixo_canônico` (**(N5)**), o sistema **deve prefixar** esse prefixo ao valor atual.
- **M1.4.** Ao alterar o item pai, após ler o rótulo com sucesso: atualizar estado do radical do pai, preencher `receita_nome` com o prefixo **M1.1**, marcar o rádio **Completo** e `receita_nome_base_mode` = `base_pai_completo`.

**Exemplo M1.1**  
- `nome_pai` = `Imposto sobre Transmissão "Causa Mortis" e Doação de Bens e Direitos` → `receita_nome` = `Imposto sobre Transmissão "Causa Mortis" e Doação de Bens e Direitos - `.

**Exemplo M1.3**  
- Valor `ICMS - Principal`, modo Completo com pai `ICMS` e valor que não começa por `ICMS - ` → prefixação → `ICMS - ICMS - Principal` (efeito colateral documentado).

---

## Modo «Sem Nome Base» (`sem_base`) — M2

### Requisitos

- **M2.1.** Ao selecionar este modo, **remover** do início de `receita_nome` o **radical atualmente conhecido** na UI (`currentParentNameBase` ou equivalente — seja ele o literal do pai do modo **Completo** ou o radical **abreviado** do modo **Abreviado**), seguido do **separador flexível**: espaços opcionais, hífen ASCII, en dash (`\u2013`) ou em dash (`\u2014`), espaços opcionais.
- **M2.2.** Se **M2.1** não casar, tentar remoção **estrita** do prefixo `texto_radical_conhecido + sufixo_canônico` (**(N5)**) quando o valor começar exatamente por essa string — onde `texto_radical_conhecido` é o radical que o modo ativo colocou **antes** do sufixo canônico.
- **M2.3.** Se o valor ainda começar pelo radical conhecido sem separador válido, exibir aviso `remove_base_prefix_mismatch`.
- **M2.4.** `receita_nome_base_mode` = `sem_base`.

**Exemplo M2.1**  
- Radical conhecido = `ICMS`; `receita_nome` = `ICMS\u2013Principal` → `Principal`.

---

## Modo «Radical Baseado no Item Pai - Abreviado» (`base_pai_abrev`) — B0

### Requisitos gerais

- **B0.1.** Este modo corresponde ao **primeiro** rádio na ordem da UI.
- **B0.2.** O **radical abreviado** (trecho que alimenta **(N2)** no modo **Abreviado**) **deve** ser calculado pelo protocolo **A1–A8** a partir de `nome_pai` e do léxico ativo. As etapas **A1–A6** produzem apenas esse texto (sem o sufixo de edição).
- **B0.3.** **Paridade com o modo Completo:** após obter o radical abreviado (*trim* não vazio), o valor colocado em `receita_nome` **deve** ser **`radical_abreviado + sufixo_canônico`** (**(N5)**) — o **mesmo** literal `" - "` que em **M1.1**; **não** basta o radical sozinho no campo quando o sistema sugere o nome.
- **B0.4.** Ao alterar o item pai com este modo selecionado, **deve** recalcular-se o radical abreviado e repor `receita_nome` com **`(novo radical abreviado) + sufixo_canônico`**, salvo política de não sobrescrever texto manual (**A9**, análogo a **M1.3**).

---

## Guardrails — validação, mensagens e ciclo de vida

### G1 — Bloqueio de envio: nome só com radical + separador (incompleto)

- **G1.1.** Antes do envio (após validações de código e hierarquia), executar validação equivalente a `validateClassificationNamingOnSubmit`. Se existir radical de pai conhecido (**G4**) **e** `trim(receita_nome)` for **sugestão incompleta** (**G1.2**), **bloquear** o envio.
- **G1.2.** Seja `b` o *trim* do **radical efetivo** do modo ativo — o texto **antes** do primeiro **`sufixo_canônico`** (**(N5)**) que o sistema colocaria na sugestão:  
  - modo **Completo:** `b = trim(nome_pai)`;  
  - modo **Abreviado:** `b = trim(radical_abreviado)` (saída de **A1–A8** / **B0.2**, não o `nome_pai` literal).  
  Seja `S` o literal de **(N5)** e `n = trim(receita_nome)`. **Sugestão incompleta** se `n` for **igual** a `(b + S).trimEnd()`, a `b + " -"` (traço sem segundo espaço) ou a `b + S` (equivalente a `b + " - "`).  
  **Requisito:** não gravar item novo cujo nome seja apenas `b` seguido só do separador canônico ou variantes acima, **sem** complemento após `S`.
- **G1.3.** Ao bloquear: `setCustomValidity` com `receita_nome_submit_incompleto_error`, erro no campo e nota no topo (ex.: «Por favor, corrija o erro abaixo.»).

**Exemplo G1.2 (Abreviado)**  
- `nome_pai` longo, radical abreviado calculado `Rest. Progressiva IPVA`; `n` = `Rest. Progressiva IPVA - ` → **bloqueado**.

**Exemplo G1.2 (Completo)**  
- `b` = `IPVA`; `n` = `IPVA - Principal` → **permitido**.

**Exemplo G1.2 (traços Unicode)**  
- **Recomendação:** alinhar detecção de «só radical + separador» em **G1.2** aos separadores de **M2.1**.

### G2 — Mensagens informativas (antes do envio)

- **G2.0.** Enquanto **G1.2** for verdadeiro e houver radical conhecido, **deve** exibir-se mensagem informativa azul; o **texto** depende do modo:

- **G2.1 — Modo Completo (`base_pai_completo`):**  
  **Texto fixo:**  
  `Nome sugerido com base no item pai selecionado.`  
  (Chave sugerida na implementação: ex. `receita_nome_sugestao_info_completo`.)

- **G2.2 — Modo Abreviado (`base_pai_abrev`):**  
  **Texto:**  
  `Nome sugerido com base no item pai selecionado. Complete o nome desta classificação após o traço. O nome do item pai é "` + **valor literal de `nome_pai`** + `"`  
  (aspas delimitadoras literais ao redor do nome do pai para clareza; escapar aspas internas de `nome_pai` na implementação se necessário). Chave sugerida: `receita_nome_sugestao_info_abrev` como *template* com placeholder `{nome_pai}`.

- **G2.3.** No evento `input` de `receita_nome`, limpar *customValidity*, mensagens locais de naming e *errornote* associada.

**Exemplo G2.2**  
- `nome_pai` = `Imposto sobre Transmissão "Causa Mortis" e Doação de Bens e Direitos` → fragmento final: `... O nome do item pai é "Imposto sobre Transmissão "Causa Mortis" e Doação de Bens e Direitos"` (com regras de escape definidas no código).

### G3 — Limpeza ao remover o item pai

- **G3.1.** Se `parent_item_id` ficar vazio, limpar rádios, oculto `receita_nome_base_mode`, estado do radical e mensagens.

### G4 — Hidratação após POST com erro

- **G4.1.** Se o formulário retornar com `parent_item_id` e `receita_nome` preenchidos, reidratar o estado do radical pelo rótulo ou, se necessário, inferir o prefixo antes do primeiro separador flexível (**M2.1**), **em consistência** com `receita_nome_base_mode` salvo. No modo **Abreviado**, o valor de `b` usado em **G1.2** **deve** corresponder ao radical abreviado associado ao prefixo atual de `receita_nome`, coerente com **`base_pai_abrev`**.

### G5 — Ordem na cadeia de envio

- **G5.1.** Validação de naming **depois** de validação de código e `syncHierarchyFromCode` com sucesso, **antes** de confirmações adicionais e *submit* nativo.

---

## Protocolo do modo Abreviado (regras A1–A9)

*(ND) = transformação sobre `nome_pai` e léxico.*

- **Paridade com o modo Completo (sufixo):** o valor sugerido em `receita_nome` nos dois modos com base no pai **sempre** observa **`radical + sufixo_canônico`** (**(N5)**). No **Abreviado**, o protocolo abaixo define só o **radical**; a regra **A7** fecha o contrato concatenando **(N5)** ao resultado de **A1–A6**, em espelho de **M1.1**.

### Regra A1 (ND) — Léxico e registro ativo

- **A1.1.** Só `AliasLexico` com `data_registro_fim` = sentinela (ativo).
- **A1.2.** Ignorar `termo` ou `abreviacao` vazios após *strip*.

**Exemplo A1.1**  
- `Principal` / `Princ.` ativo → entra no léxico; `Secundário` / `Sec.` com registro encerrado → fora.

### Regra A2 (ND) — Ordenação dos candidatos a `termo`

- **A2.1.** Multi-palavra antes de mono-palavra; comprimento de `termo` decrescente; desempate lexicográfico.

**Exemplo A2.1**  
- Frase longa do IPVA antes de `Restituição`.

### Regra A3 (ND) — Match exato do nome completo do pai

- **A3.1.** Se `norm(termo) == norm(nome_pai)` → o radical interno = `abreviacao` (*strip*), sem A4–A6; em seguida **A7** aplica **`+ sufixo_canônico`** em `receita_nome`.

### Regra A4 (ND) — Substituição por substring não sobreposta

- **A4.1a:** `casefold`; sem colapsar espaços internos.
- **A4.2–A4.3:** Greedy global: maior `(end-start)`, menor `start`, ordem **A2**.
- **A4.4.** Substituir na string original do pai.

### Regra A5 (ND) — Remanescentes literais

- **A5.1.** Trechos não cobertos permanecem como no `nome_pai`.

### Regra A6 (ND) — Conectivos

- **A6.1–A6.3.** Tokenizar por espaços; remover tokens em `NOME_CLASSIFICACAO_CONNECTIVOS_FIXOS`; reunir com um espaço.

### Regra A7 (ND) — Concatenação do sufixo canônico (igual ao Completo)

- **A7.1.** Se o radical produzido por **A1–A6** (ou por **A3** / **A8** conforme o ramo) for **não vazio** após *trim*, o valor a atribuir a `receita_nome` na sugestão **deve** ser **`radical + sufixo_canônico`** (**(N5)**), *i.e.* o mesmo padrão **`… + " - "`** que **M1.1** no modo **Completo**.
- **A7.2.** Se o radical for vazio, **não** aplicar sufixo canônico por omissão (alinhado à exceção de **M1.1** quando não há `nome_pai`).

### Regra A8 (ND) — Nenhuma substituição

- **A8.1.** Sem A3 nem A4 → o radical interno = `nome_pai.strip()`; em seguida **A7** aplica **`+ sufixo_canônico`**; recomenda-se aviso de léxico não aplicável.

### Regra A9 (ND) — Mudança de modo ou pai

- **A9.1.** Recalcular sugestão.
- **A9.2.** Preservar edição manual quando as heurísticas de prefixo / incompleto permitirem (análogo a **M1.3**).

---

## Implementação canônica do radical abreviado

- **I1.** Lógica **A1–A8** em um módulo Python com testes (a parte **A1–A6** / ramos **A3** e **A8** produz o **radical**; **A7** documenta a concatenação obrigatória de **(N5)** no valor sugerido).
- **I2.** O admin obtém o radical (ou o texto já com **(N5)**) via endpoint *staff* ou payload embutido, sem duplicar regras de abreviação no JS.
- **I3.** Se a camada Python expuser **apenas** o radical sem **(N5)**, o cliente **deve** acrescentar **`sufixo_canônico`** ao montar `receita_nome`, de forma que o usuário veja sempre **`radical + " - "`** nos modos **Completo** e **Abreviado**, como em **(N5)**.

---

## Testes automatizados (recomendados)

- **Ordem dos rádios:** Abreviado → Completo → Sem base.
- **Paridade sufixo:** após sucesso no lookup pelo código (**P1**), `receita_nome` termina com **`" - "`** (**(N5)**) após o radical abreviado.
- **M1 / Completo:** valor inicial `nome_pai + sufixo_canônico` (**(N5)**); **G2.1** com texto fixo.
- **Abreviado:** **G2.2** contém `nome_pai` literal; **G1** com `b` = radical abreviado.
- **M2:** remoção com traços Unicode; aviso **M2.3**.
- **G4:** POST com erro + modo Abreviado: `b` em **G1.2** coerente com prefixo abreviado.
- **A3, A4+A6, A8.**

---

## Decisões pendentes e refinamentos

| ID | Tema | Decisão recomendada |
|----|------|---------------------|
| D1 | `norm` e acentos | `casefold` sem remover acentos na v1. |
| D2 | **G1.2** e traços Unicode | Alinhar a **M2.1**. |
| D3 | Vários `termo` com mesmo `norm` | Desempate por `alias_lexico_ref`. |
| D4 | Espaços em `norm` | Não colapsar na v1. |
| D5 | **P2** conflito escolha manual vs autocomplete | Documentar decisão no JS (forçar Abreviado só no «primeiro» autocomplete ou respeitar rádio). |
| D6 | **G1** no servidor | Duplicar em `clean()` / admin. |

---

## Melhorias futuras opcionais

- Internacionalização em `classification_naming_messages.py`.
- Cache do léxico por requisição.

---

## Notas de desenvolvimento (alterações em relação ao código legado)

Esta seção **não** faz parte do contrato normativo; serve só para quem migra ou compara com o repositório **antes** das mudanças alinhadas a esta spec.

- **Rótulo e valor POST do modo «literal do pai»:** no código legado, o rádio aparecia como *«Radical Baseado no item pai»* e o valor POST costumava ser `base_pai`. A spec passa a exigir o rótulo **«Radical Baseado no Item Pai - Completo»** e o valor **`base_pai_completo`**. Convém aceitar `base_pai` como sinônimo na leitura do POST e normalizar internamente para `base_pai_completo`, até remover o legado.

- **Autocomplete ao preencher `receita_cod`:** o fluxo que, após sucesso na hierarquia/lookup, sugeria o nome no padrão de radical **completo** (nome longo do pai + ` - `) deve passar a usar por **omissão** o modo **Abreviado** (**P1** da spec).

- **Mensagem informativa única no legado:** `RECEITA_NOME_SUGESTAO_INFO` juntava a frase curta com *«Complete o nome…»*. A spec **separa**: **G2.1** (só a primeira frase no modo **Completo**) e **G2.2** (texto longo com `{nome_pai}` no modo **Abreviado**).

- **Guardrail G1:** no legado, o predicado de «só radical + traço» aplicava-se ao radical **literal** do pai. Com o modo **Abreviado**, o mesmo critério deve usar `b` = radical **abreviado** calculado (**G1.2**), não o `nome_pai` inteiro.

- **Ordem dos rádios no HTML:** a spec exige Abreviado primeiro, depois Completo, depois Sem Nome Base; o legado tinha só dois rádios (Completo e Sem base) noutra ordem — ajustar markup e lógica de *default* / *checked*.
