# Item de classificação — navegação estrutural na tela de alteração (change)

Esta especificação define quatro protocolos de **navegação estrutural** na view **change** de `ItemClassificacao`: percorrer códigos existentes e com vigência compatível com o registro aberto, sem alterar o código canônico do registro atual (distinto da navegação por **blur** em `receita_cod` — ver `_dev/spec_itemClassificacao_editar_codigo.md`).

**Protocolos:**

| ID                     | Nome            |
| ---------------------- | --------------- |
| **(G-nav.next-code)**  | Próximo código  |
| **(G-nav.next-level)** | Próximo nível   |
| **(G-nav.prev-code)**  | Código anterior |
| **(G-nav.prev-level)** | Nível anterior  |

**Implementação de referência (alvo):** `apps/core/templates/admin/core/change_form.html` (barra **(G-nav.ui-toolbar)**, botões **(G-nav.ui-controls)**, `__coreConfirmUnsavedIfDirty`, aviso de classificação); novo endpoint JSON em `ItemClassificacaoAdmin` (família `lookup-*` / `resolve-structural-navigation` em `apps/core/classification_item_code_lookup.py`).

**Specs relacionadas (não substituídas):**

| Spec                                                  | Relação                                                                                                       |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| `_dev/spec_itemClassificacao_editar_codigo.md`        | **(T6)**, **(T7)**, **(T-cod.1)**, **(T-cod.2)**, **V1**, desempate; navegação por digitação (**G-cod.blur**) |
| `_dev/spec_itemClassificacao_criar_filho.md`          | Aviso de alterações não guardadas ao sair da change (**v2**)                                                  |
| `_dev/spec_itemClassificacao_formulario.md`           | Preservar `_changelist_filters` no redirecionamento                                                           |
| `_dev/spec_itemClassificacao_mascara_apresentacao.md` | **B1** — máscara aplicada a `COD-EDIT` na change                                                              |
| `_dev/spec_itemClassificacao_regras_hierarquia.md`    | Zero canônico; vínculo pai–filho (não relaxado na persistência)                                               |

---

## Escopo

| Inclui                                                                         | Não inclui                                                         |
| ------------------------------------------------------------------------------ | ------------------------------------------------------------------ |
| View **change** de `ItemClassificacao`                                         | View **add**                                                       |
| Barra **(G-nav.ui-toolbar)** e quatro botões **(G-nav.ui-controls)** na change | Navegação por **blur** / modais **M2–M4** (`editar_codigo`)        |
| Destino apenas **(T-cod.2)** → `change` do registro desempatado                | Destino **add** ou **(T-cod.3)**                                   |
| Navegação entre `classificacao_id` diferentes (intencional)                    | Alterar `receita_cod` do registro aberto                           |
| Aviso na UI se a classificação do destino divergir                             | Regras de `parent_item_id` na gravação                             |
| Endpoint `resolve-structural-navigation` (recomendado)                         | Atalhos de teclado (fora desta versão)                             |
| **NV-TARGET** e sequência de nível (**(G-nav.level-seq)**)                     | Alterar algoritmo de **(G-nav.next-code)** / **(G-nav.prev-code)** |

---

## Notação

| Símbolo        | Significado                                                                                                                                                                                                                              |
| -------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **COD-EDIT**   | Código canônico do registro em edição (dígitos `0-9`, sem pontuação de máscara). Equivalente a **COD-1** em `editar_codigo` na carga da página (não o valor eventualmente digitado no input).                                            |
| **NV-EDIT**    | Nível hierárquico derivado de **COD-EDIT** (ver abaixo).                                                                                                                                                                                 |
| **NV-TARGET**  | Nível de referência para **(G-nav.next-level)** e **(G-nav.prev-level)** durante uma **sequência de nível** (ver abaixo). Fixado no primeiro clique em próximo/nível anterior da sequência; não muda até a sequência encerrar.           |
| **V1**         | Vigência do registro aberto: `data_vigencia_inicio` e `data_vigencia_fim` do `instance` na change.                                                                                                                                       |
| **MASK-EDIT**  | Máscara de segmentos (larguras por nível) da `estrutura_codigo` **efetivamente utilizada** para formatar/apresentar **COD-EDIT** na change ao iniciar a navegação (mesma fonte que `runCodeDigitValidation` / máscara visível no campo). |
| **`<código>`** | **COD-EDIT** ou destino formatado com **MASK-EDIT** para exibição.                                                                                                                                                                       |

**Normalização:** remover `.` e espaços; comparar e segmentar apenas dígitos, com padding à direita com `0` até o comprimento total `sum(MASK-EDIT)` quando necessário para alinhar segmentos.

---

## Terminologia (alinhada ao projeto)

Definições em `_dev/spec_itemClassificacao_editar_codigo.md` aplicam-se com **COD-EDIT** no papel de código avaliado e **V1** do registro aberto:

- **(T6) Registro ativo:** `data_registro_fim` = sentinela de transação.
- **(T7) Sobreposição de vigência:** intervalos inclusivos: `início_A ≤ fim_B` e `fim_A ≥ início_B`.
- **(T-cod.1) Código existente:** ao menos um registro **(T6)** com `receita_cod` igual ao código alvo.
- **(T-cod.2) Vigência atual (vs. registro aberto):** **(T-cod.1)** e existe registro **(T6)** desse código com **(T7)** em relação a **V1**.

**Candidato navegável:** registro **(T6)** cujo `receita_cod` satisfaz **(T-cod.2)** para **V1** do registro em edição. Todos os protocolos consideram **somente** candidatos navegáveis. Códigos inexistentes ou só com vigência diversa **não** são destino; o controle correspondente permanece desabilitado ou inativo.

**Desempate (mesmo `receita_cod`, várias linhas bitemporais com (T-cod.2)):** maior `data_vigencia_fim`; empate → maior `data_vigencia_inicio`; empate → maior `pk`. Mesma regra de `resolve-code-navigation` em `classification_item_code_lookup.py`.

**Navegação entre classificações:** os protocolos **podem** retornar destino com `classificacao_id` diferente do registro aberto, desde que o candidato seja navegável (**(T-cod.2)** vs **V1**). É comportamento **intencional** desta funcionalidade (percorrer classificações estruturalmente compatíveis sob a mesma **MASK-EDIT**). A UI **deve** exibir aviso quando a classificação do destino divergir da do registro aberto (ver **(G-nav.ui-warning-class)**).

---

## Objetivo dos protocolos

Os protocolos retornam o candidato navegável **estruturalmente mais próximo** de **COD-EDIT**, segundo a estratégia de cada **(G-nav.\*)**, e redirecionam para a **change** do PK desempatado.

---

## Derivação de nível e máscara

### **NV-EDIT**

Segmentar **COD-EDIT** (normalizado e padded) com **MASK-EDIT**. **NV-EDIT** é o índice 1-based do **último nível** cujo segmento **não** é zero canônico (todos os dígitos do segmento iguais a `0`, com largura do nível). Se não houver segmento discriminado, a navegação **não** prossegue (controles inativos).

*Nota:* **NV-EDIT** deriva do código e da **MASK-EDIT**, não do `nivel_id` gravado no registro (que pode divergir em dados legados).

### **MASK-EDIT** (estrutura dos candidatos)

Para localizar o destino, **todos** os níveis, larguras de segmento e comprimento total dos códigos candidatos usam **exclusivamente MASK-EDIT** — a mesma `estrutura_codigo` já aplicada à máscara de **COD-EDIT** na change. Não se usa a `estrutura_codigo` da `classificacao_id` do destino nem a do registro aberto para redefinir níveis na busca.

Candidatos com `receita_cod` incompatível com **MASK-EDIT** (comprimento ou segmentação) ficam **fora** do conjunto de busca.

### **RAD-BASE** (prefixo estrutural nas etapas-1)

Em etapas que exigem “mesmo radical que **COD-EDIT**” (varredura abaixo de **NV-EDIT**), o prefixo fixo é **RAD-BASE** = `radical(M)`, onde **M** é o maior nível **L ≤ NV-EDIT** tal que o segmento em **L** não é zero canônico e os níveis **L+1 .. NV-EDIT−1** são zero canônico em **COD-EDIT**. Se **M = 0**, o prefixo é vazio.

Em etapas que fixam os níveis `1 .. NV-EDIT − 1` (irmão no nível **NV-EDIT**), o prefixo é `radical(NV-EDIT − 1)`.

### Comparação de dígitos

“Menor/maior dígito” ou “menor/maior valor” no segmento de um nível: comparação **lexicográfica** do segmento na largura definida por **MASK-EDIT**. “Menor/maior código completo”: comparação lexicográfica da string de dígitos normalizada (mesmo comprimento `sum(MASK-EDIT)`).

---

## Conceitos estruturais

### `radical(N)`

Concatenação dos dígitos dos níveis `1` a `N`, inclusive, segundo **MASK-EDIT**. Níveis posteriores a `N` desconsiderados na comparação do prefixo.

### Zero canônico

Segmento em que todos os dígitos são `0`, com largura do nível em **MASK-EDIT** (ex.: `0`, `00`, `000`). Um nível é considerado como contendo `zero canônico` quando todos os dígitos correspondentes àquele nível assumem o valor zero previsto pela respectiva `estrutura_codigo`.

---

## Sequência de nível **(G-nav.level-seq)**

Protocolos **(G-nav.next-level)** e **(G-nav.prev-level)** percorrem a árvore preferindo **irmãos no mesmo nível hierárquico**. Quando não há mais irmãos e o protocolo **sobe** para um ramo ancestral, o destino pode ficar numa **matriz** com **NV-EDIT** menor que o nível em que o usuário iniciou a sequência. Neste caso, cliques seguintes devem **re-descer** no novo ramo (como **(G-nav.next-code)** / **(G-nav.prev-code)**), **um passo por clique**, até **NV-EDIT = NV-TARGET**, e só então retomar irmãos nessa profundidade.

### **NV-TARGET**

| Regra                   | Descrição                                                                                                                                                                                                 |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **(G-nav.level-seq.1)** | **Início:** no **primeiro** clique em **(G-nav.next-level)** ou **(G-nav.prev-level)** após abrir a change **sem** sequência activa → `NV-TARGET := NV-EDIT` do registro nesse momento.                   |
| **(G-nav.level-seq.2)** | **Manutenção:** enquanto a sequência estiver activa, **NV-TARGET** **não** muda, ainda que **NV-EDIT** do registro aberto varie após redirecionamentos.                                                   |
| **(G-nav.level-seq.3)** | **Fim:** clique em **(G-nav.next-code)** ou **(G-nav.prev-code)**; navegação por **blur** (**G-cod.blur**); abrir change **sem** parâmetro de sequência; ou URL de change que não preserve **NV-TARGET**. |
| **(G-nav.level-seq.4)** | **(G-nav.next-code)** e **(G-nav.prev-code)** **não** recebem nem propagam **NV-TARGET**; encerram qualquer sequência activa.                                                                             |

### Persistência (cliente e endpoint)

- O cliente **deve** enviar `nv_target` em pedidos `next_level` / `prev_level` quando a sequência já estiver activa.
- A `change_url` de destino **deve** incluir query `structural_nav_nv_target=<int>` (preservar juntamente com `_changelist_filters` quando existir).
- Na carga da change, se `structural_nav_nv_target` estiver presente e for inteiro ≥ 1, a sequência considera-se **activa** com esse **NV-TARGET** (não redefinir no primeiro clique de nível até **(G-nav.level-seq.3)**).
- **Disponibilidade dos botões:** avaliar **(G-nav.next-level)** / **(G-nav.prev-level)** com **NV-TARGET** da sequência (activa ou hipotética `NV-TARGET := NV-EDIT` na pré-visualização quando inactiva).

### Reutilização de **(G-nav.next-code)** / **(G-nav.prev-code)**

Nas fases de **descida** / **subida** de profundidade (ver **Fase L3** abaixo), aplica-se o resolvedor de **(G-nav.next-code)** ou **(G-nav.prev-code)** **exactamente uma vez** por clique — o mesmo algoritmo das três etapas de cada protocolo de código, produzindo **um** candidato. **Não** confundir com o botão «Próximo código»: é reutilização do **algoritmo**, não do eixo de navegação nem da sequência de nível.

### Casos de borda **(G-nav.level-seq)**

| Situação                                                       | Comportamento                                                                                                    |
| -------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| L3 sem candidato **(G-nav.next-code)** / **(G-nav.prev-code)** | Botão de nível desabilitado; **não** saltar silenciosamente para outro ramo.                                     |
| **NV-EDIT = NV-TARGET** após L2                                | Próximo clique usa L1 (irmãos no nível alvo).                                                                    |
| Código «não navegável» na descida L3                           | Ignorar; aplicar **(G-nav.next-code)** ao conjunto restante (equivalente a candidato inexistente naquele passo). |
| **NV-TARGET** inválido na URL                                  | Ignorar parâmetro; tratar como sequência inactiva.                                                               |
| Registro inactivo (**não** **(T6)**)                           | Sequência não inicia; botões de nível desabilitados.                                                             |

---

## Regras gerais

- Buscar apenas candidatos navegáveis (**(T-cod.2)** vs **V1**).
- Segmentar e comparar candidatos somente com **MASK-EDIT**.
- “Menor dígito superior” / “maior dígito inferior”: menor ou maior valor **existente** entre candidatos, não ±1 aritmético.
- Destino: `change` do registro após desempate; preservar `_changelist_filters` quando existir (`spec_itemClassificacao_formulario.md`).

---

## Nomes dos códigos encontrados

| Protocolo              | Código encontrado | Nível do destino |
| ---------------------- | ----------------- | ---------------- |
| **(G-nav.next-code)**  | `COD-PROX`        | `NV-COD-PROX`    |
| **(G-nav.next-level)** | `COD-PROX-NV`     | `NV-COD-PROX-NV` |
| **(G-nav.prev-code)**  | `COD-ANT`         | `NV-COD-ANT`     |
| **(G-nav.prev-level)** | `COD-NV-ANT`      | `NV-COD-NV-ANT`  |

`NV-*` do destino: **NV-EDIT** calculado para o `receita_cod` destino com a mesma **MASK-EDIT**.

---

## UI na change

### **(G-nav.ui-toolbar)** Posição no layout

Barra de navegação estrutural **somente** na view **change** de `ItemClassificacao`, **não** na add.

| Regra                    | Descrição                                                                                                                                                                                                                                            |
| ------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **(G-nav.ui-toolbar.1)** | Inserir uma faixa horizontal **entre** o cabeçalho do objeto (título `h1` com código e nome do registro) e o primeiro `.form-row` do formulário (campo `receita_cod`).                                                                               |
| **(G-nav.ui-toolbar.2)** | Na **mesma faixa vertical** que `ul.object-tools` («+ Criar Código Filho», «Histórico»): alinhar a barra de navegação **à esquerda** e manter `object-tools` **à direita** (layout `flex`, `justify-content: space-between`, `align-items: center`). |
| **(G-nav.ui-toolbar.3)** | **Não** colocar os controlos dentro de `ul.object-tools`, na linha do input `receita_cod` (reservada a **(R-revert)**) nem na `submit-row` inferior.                                                                                                 |
| **(G-nav.ui-toolbar.4)** | Margem inferior da faixa suficiente para separar visualmente o grupo de ícones do rótulo «Código Canônico da Natureza de Receita».                                                                                                                   |
| **(G-nav.ui-toolbar.5)** | Em viewport estreita, a faixa pode quebrar linha abaixo do título, mantendo-se **acima** do campo `receita_cod`.                                                                                                                                     |

**Implementação (alvo):** bloco dedicado em `change_form.html` (ex.: `div.core-structural-nav-toolbar`) injectado após o título do registro / antes do formulário, com CSS de especificidade sobre o tema do admin.

---

### **(G-nav.ui-controls)** Botões — símbolos, ordem e estilo

Quatro `button type="button"` em grupo contíguo (`role="group"`, `aria-label="Navegação estrutural do código canônico"`).

**Ordem fixa (esquerda → direita):**

| #   | Símbolo visível | Protocolo              | `id` sugerido         |
| --- | --------------- | ---------------------- | --------------------- |
| 1   | `«` ou `<<`     | **(G-nav.prev-level)** | `core-nav-prev-level` |
| 2   | `<`             | **(G-nav.prev-code)**  | `core-nav-prev-code`  |
| 3   | `>`             | **(G-nav.next-code)**  | `core-nav-next-code`  |
| 4   | `»` ou `>>`     | **(G-nav.next-level)** | `core-nav-next-level` |

**Metáfora:** seta **simples** = deslocamento ao longo da árvore (código anterior / próximo código); seta **dobrada** = deslocamento entre **irmãos** preferencialmente no nível **NV-TARGET** (sequência de nível), subindo ou descendo ramos quando necessário. **Não** representam «primeiro/último» nem paginação do admin.

**Estilo visual (distinto de `object-tools`):**

- Botões **ícone** neutros (fundo claro ou transparente, borda subtil cinza), **sem** pastilha verde de «Criar Código Filho».
- Área clicável ~28–32 px; `gap` uniforme entre os quatro; opcional separador vertical fino entre `<` e `>`.
- `:hover` / `:focus-visible`: realce discreto (borda ou fundo `#f5f5f5`).
- **Desabilitado:** `disabled`, `aria-disabled="true"`, opacidade reduzida (paridade com `core-create-child-code-link[aria-disabled="true"]`), cursor `not-allowed`.

**`title` e `aria-label` (obrigatórios em cada botão):**

| Botão           | `aria-label`      | `title` (ativo)                                                             | `title` (desabilitado)                                                   |
| --------------- | ----------------- | --------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| Nível anterior  | `Nível anterior`  | `Nível anterior — abrir o código irmão anterior no mesmo nível hierárquico` | `Nível anterior — não há código irmão anterior navegável nesta vigência` |
| Código anterior | `Código anterior` | `Código anterior — abrir o código estruturalmente anterior na árvore`       | `Código anterior — não há código anterior navegável nesta vigência`      |
| Próximo código  | `Próximo código`  | `Próximo código — abrir o código estruturalmente seguinte na árvore`        | `Próximo código — não há código seguinte navegável nesta vigência`       |
| Próximo nível   | `Próximo nível`   | `Próximo nível — abrir o código irmão seguinte no mesmo nível hierárquico`  | `Próximo nível — não há código irmão seguinte navegável nesta vigência`  |

O texto visível do botão pode ser apenas o símbolo (`<`, `>`, `<<`, `>>` ou entidades tipográficas `«` `»`); a semântica acessível vem de `aria-label` / `title`, não do glifo isolado.

**Estados e pré-condições:**

| Estado                               | Comportamento                                                                                                           |
| ------------------------------------ | ----------------------------------------------------------------------------------------------------------------------- |
| Sem candidato para o protocolo       | Botão desabilitado; `title` da coluna «desabilitado»; não dispara navegação.                                            |
| Registro inactivo (**não** **(T6)**) | Todos os quatro desabilitados (navegação só a partir de registo activo em edição).                                      |
| Candidato disponível                 | Clique → pipeline **(G-nav.ui-unsaved)** → **(G-nav.ui-warning-class)** (se aplicável) → `location.assign(change_url)`. |

Os botões **não** submetem o formulário. Não duplicar handlers em `guardedLinks` do aviso global de saída.

### **(G-nav.ui-unsaved)** Alterações não guardadas

Paridade com `_dev/spec_itemClassificacao_criar_filho.md` (**Alterações não guardadas**):

1. No clique de qualquer **(G-nav.\*)**, se o formulário tiver alterações não guardadas pelo usuário, chamar `window.__coreConfirmUnsavedIfDirty(go)` **antes** de redirecionar.
2. Um único canal por botão (evitar `confirm` duplicado com `guardedLinks`).
3. Rebaseline de dirty state: `__coreRebaselineFormDirtySnapshot()` após init da change (e `setTimeout` ~750 ms), como em **criar filho**, para não disparar falso positivo só por máscara/FK init.
4. Se **apenas** `receita_cod` / `item_id` estiverem «sujos» por navegação por blur não confirmada, aplicar o mesmo critério de `editar_codigo` (**M2–M4**) quando fizer sentido; caso contrário, aviso antes de sair.

Após confirmação (ou se não houver dirty), `location.assign` para a `change_url` do destino.

**Sequência de nível na UI:** botões **(G-nav.next-level)** e **(G-nav.prev-level)** leem/gravam `structural_nav_nv_target` (URL ou estado equivalente). Botões **(G-nav.next-code)** e **(G-nav.prev-code)** **não** incluem o parâmetro e **encerram** a sequência no destino.

### **(G-nav.ui-warning-class)** Classificação diferente

Se o `classificacao_id` do destino desempatado for diferente do registro aberto, exibir aviso **antes** do redirecionamento (modal `showCoreAttentionModal` ou equivalente), com sentido obrigatório:

> O próximo/anterior código pertence à classificação **&lt;id/nome&gt;**, diferente da classificação **&lt;id/nome&gt;** do registro atual. Deseja continuar?

Botões: **Cancelar** | **Continuar**. **Cancelar** mantém a change atual. **Continuar** prossegue o redirecionamento (após **(G-nav.ui-unsaved)** quando aplicável).

---

## Endpoint `resolve-structural-navigation` (recomendado)

`GET …/admin/core/itemclassificacao/resolve-structural-navigation/`

| Parâmetro   | Obrigatório | Descrição                                                                                                                       |
| ----------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `pk`        | Sim         | PK do registro em edição (origem).                                                                                              |
| `direction` | Sim         | `next_code` \| `next_level` \| `prev_code` \| `prev_level`                                                                      |
| `nv_target` | Condicional | Obrigatório para `next_level` / `prev_level` quando a sequência já está activa; omitir ou ignorar em `next_code` / `prev_code`. |

O servidor obtém **COD-EDIT**, **V1**, **MASK-EDIT** e **NV-EDIT** a partir do `instance` e da máscara efetiva na change. Para `next_level` / `prev_level`, usar **NV-TARGET** conforme **(G-nav.level-seq)**.

**Resposta com destino (campos adicionais para sequência de nível):**

```json
{
  "ok": true,
  "direction": "next_level",
  "nv_target": 6,
  "level_seq_active": true,
  "codigo_display": "1.1.1.4.01.0.0.00.000",
  "target": {
    "pk": "456",
    "receita_cod": "…",
    "change_url": "/admin/core/itemclassificacao/456/change/?structural_nav_nv_target=6",
    "classificacao_id": "…",
    "classificacao_display": "…",
    "classificacao_changed": false,
    "origin_classificacao_display": "…"
  }
}
```

**Sem destino:** `{ "ok": false, "reason": "no_candidate", "message": "…" }`.

---

## Base de exemplos

Para os exemplos abaixo, considerar **MASK-EDIT** da base fictícia (9 níveis como na lista), todos os códigos como candidatos navegáveis e vigentes:

```txt
1.0.0.0.00.0.0.00.000 Receitas Correntes 
1.1.0.0.00.0.0.00.000 Impostos, Taxas e Contribuições de Melhoria
1.1.1.0.00.0.0.00.000 Impostos 
1.1.1.1.00.0.0.00.000 Impostos sobre o Comércio Exterior 
1.1.1.1.01.0.0.00.000 Imposto sobre a Importação 
1.1.1.1.02.0.0.00.000 Imposto sobre a Exportação 
1.1.1.2.00.0.0.00.000 Impostos sobre o Patrimônio
1.1.1.2.00.0.0.00.001 Código Fictício Exemplo Navegação 1
1.1.1.2.00.0.0.00.002 Código Fictício Exemplo Navegação 2
1.1.1.2.00.0.0.00.003 Código Fictício Exemplo Navegação 3
1.1.1.2.52.0.0.00.000 Imposto sobre Transmissão “Causa Mortis” e Doação de Bens e Direitos 
1.1.1.2.52.0.1.00.000 ITCD - Principal 
1.1.1.2.52.0.1.01.000 ITCD - Princ. - Cota Parte do Estado 
1.1.1.2.52.0.1.02.000 ITCD - Princ. - Cota Parte do FUNDEB 
1.1.1.2.52.0.2.00.000 ITCD - Multas e Juros de Mora
1.1.1.2.52.0.2.01.000 ITCD - MJM - Cota Parte do Estado
1.1.1.2.52.0.2.02.000 ITCD - MJM - Cota Parte do FUNDEB
1.1.1.2.52.0.3.00.000 ITCD - Dívida Ativa
1.1.1.2.52.0.3.01.000 ITCD - DA - Cota Parte do Estado 
1.1.1.2.52.0.3.02.000 ITCD - DA - Cota Parte do FUNDEB 
1.1.1.2.52.0.4.00.000 ITCD - Dívida Ativa - Multas e Juros de Mora 
1.1.1.2.52.0.4.01.000 ITCD - DA-MJM - Cota Parte do Estado 
1.1.1.2.52.0.4.02.000 ITCD - DA-MJM - Cota Parte do FUNDEB 
1.1.1.2.53.0.0.00.000 Impostos sobre Transmissão "Inter Vivos" de Bens Imóveis e de Direitos Reais sobre Imóveis 
1.1.1.3.00.0.0.00.000 Impostos sobre a Renda e Proventos de Qualquer Natureza
1.1.1.3.00.0.0.03.000 Código Fictício Exemplo Navegação 4
1.1.1.3.00.0.0.03.001 Código Fictício Exemplo Navegação 5
1.1.1.4.00.0.0.00.000 Código Fictício Exemplo Navegação 6
1.1.1.5.00.0.0.00.000 Código Fictício Exemplo Navegação 7
```

---

## **(G-nav.next-code)** — Próximo código

### etapa-1

Procurar candidato com prefixo **RAD-BASE**, varrendo do último nível até o nível imediatamente posterior a **NV-EDIT**, no primeiro nível (de baixo para cima) cujo segmento **não** é zero canônico, com segmentos estritamente entre **NV-EDIT** e esse nível em zero canônico no candidato. Entre candidatos válidos no nível encontrado, escolher o de **menor** código completo.

#### Ex.: 1.1

- `COD-EDIT`: `1.1.1.2.00.0.0.00.000` (NV-EDIT=4)
- **RAD-BASE**: `"1.1.1.2"` (K=4)
- `COD-PROX`: `1.1.1.2.00.0.0.00.001` (NV-COD-PROX=9)

Obs.: níveis 5–8 com zeros canônicos no candidato.

---

#### Ex.: 1.2

- `COD-EDIT`: `1.1.1.3.00.0.0.00.000` (NV-EDIT=4)
- **RAD-BASE**: `"1.1.1.3"` (K=4)
- `COD-PROX`: `1.1.1.3.00.0.0.03.000` (NV-COD-PROX=8)

Obs.: `1.1.1.3.00.0.0.03.001` não é `COD-PROX`, pois entre **NV-EDIT** (=4) e o nível 9 candidato há o nível 8 com segmento `"03"` (não é zero canônico na faixa intermediária).

---

### etapa-2

Se etapa-1 não encontrar candidato: no nível **NV-EDIT**, manter `radical(NV-EDIT − 1)` e o **menor** dígito de nível **NV-EDIT** existente **superior** ao segmento atual; níveis posteriores em zero canônico.

#### Ex.: 2.1

- `COD-EDIT`: `1.1.1.4.00.0.0.00.000` (NV-EDIT=4)
- prefixo: `"1.1.1"` (nível 3)
- `COD-PROX`: `1.1.1.5.00.0.0.00.000` (NV-COD-PROX=4)

---

### etapa-3

Se etapa-2 não encontrar: para cada nível `L` de `NV-EDIT − 1` até `1`, descartar o segmento do nível `L` do prefixo, procurar o **menor** segmento no nível `L` **superior** ao descartado entre candidatos com níveis posteriores a `L` em zero canônico.

#### Ex.: 3.1

- `COD-EDIT`: `1.1.1.2.52.0.4.02.000` (NV-EDIT=8)
- prefixo: `"1.1.1.2"` (nível 4); dígito descartado no nível 5: `"52"`
- `COD-PROX`: `1.1.1.2.53.0.0.00.000` (NV-COD-PROX=5)

Obs.: `1.1.1.2.52.0.0.00.000` não é `COD-PROX` (dígito `52` não é superior a `52`).

---

## **(G-nav.next-level)** — Próximo nível

Resolver **uma** destino por clique, com **NV-TARGET** da sequência activa ou **NV-TARGET := NV-EDIT** no início da sequência. Ordem de fases (**parar na primeira** que produzir candidato):

### Fase L1 — Irmão no nível efectivo

Quando **NV-EDIT ≥ NV-TARGET**:

- Prefixo `radical(NV-EDIT − 1)`; no nível **NV-EDIT**, **menor** segmento existente **superior** ao actual entre candidatos navegáveis; níveis posteriores a **NV-EDIT** em zero canônico no candidato.
- Equivalente à antiga **etapa-1**.

#### Ex.: L1.1

- `COD-EDIT`: `1.1.1.2.52.0.0.00.000` (NV-EDIT=5); **NV-TARGET**=5
- `COD-PROX-NV`: `1.1.1.2.53.0.0.00.000` (NV-COD-PROX-NV=5)

#### Ex.: L1.2

- `COD-EDIT`: `1.1.1.1.00.0.0.00.000` (NV-EDIT=4); **NV-TARGET**=4
- `COD-PROX-NV`: `1.1.1.2.00.0.0.00.000` (NV-COD-PROX-NV=4)

---

### Fase L2 — Subir: próximo irmão ancestral

Quando L1 não encontra candidato:

- Repetição ascendente (nível `L` de `NV-EDIT − 1` até `1`): **menor** segmento no nível **L** **superior** ao descartado em **COD-EDIT**, com níveis posteriores a **L** em zero canônico no candidato (mesma lógica da etapa-3 de **(G-nav.next-code)**).
- **Um degrau por clique** — o destino pode ter **NV-EDIT < NV-TARGET** (matriz ancestral).
- **Não** exigir que o destino final esteja em **NV-TARGET**.

#### Ex.: L2.1

- `COD-EDIT`: `1.1.1.2.52.0.4.02.000` (NV-EDIT=8); **NV-TARGET**=8
- `COD-PROX-NV`: `1.1.1.2.53.0.0.00.000` (NV-COD-PROX-NV=5)

#### Ex.: L2.2 (troca de ramo)

- `COD-EDIT`: `1.1.1.3.03.4.0.00.000` (NV-EDIT=6); **NV-TARGET**=6
- `COD-PROX-NV`: `1.1.1.4.00.0.0.00.000` (NV-COD-PROX-NV=4)

#### Ex.: L2.3 (irmão ancestral intermédio)

- `COD-EDIT`: `1.1.1.4.01.5.0.00.000` (NV-EDIT=6); **NV-TARGET**=6
- `COD-PROX-NV`: `1.1.1.4.50.0.0.00.000` (NV-COD-PROX-NV=5) — **não** saltar directamente para `1.1.1.5.00…` enquanto existir irmão no nível 5 sob `1.1.1.4`.

---

### Fase L3 — Descer: um passo de **(G-nav.next-code)**

Quando L2 produz destino com **NV-EDIT < NV-TARGET**:

- Substituir o destino da L2 por **exactamente um** candidato de **(G-nav.next-code)** aplicado a **COD-EDIT** actual (mesmas regras de candidatos, **MASK-EDIT** e ordem estrutural).
- **Um clique = um passo** de descida; cliques seguintes repetem L1 (se já **NV-EDIT = NV-TARGET**) ou L3 (se ainda **NV-EDIT < NV-TARGET**) até igualar **NV-TARGET**.

#### Ex.: L3.1

- Após L2.2: `COD-EDIT`=`1.1.1.4.00.0.0.00.000` (NV-EDIT=4); **NV-TARGET**=6
- Próximo clique (L3): `1.1.1.4.01.0.0.00.000` (NV-COD-PROX-NV=5)

#### Ex.: L3.2

- `COD-EDIT`=`1.1.1.4.01.0.0.00.000` (NV-EDIT=5); **NV-TARGET**=6
- Próximo clique (L3): `1.1.1.4.01.1.0.00.000` (NV-COD-PROX-NV=6) — retoma L1 nos cliques seguintes.

---

### Sequência ilustrativa (base IRPJ / IPI)

**NV-TARGET = 6** fixado em `1.1.1.3.03.1.0.00.000`. Códigos vigentes incluem (entre outros):

```txt
1.1.1.3.02.0.0.00.000 … IRPJ …
1.1.1.3.03.0.0.00.000 … Retido na Fonte …
1.1.1.3.03.1.0.00.000 … Retido — Trabalho …
1.1.1.3.03.2.0.00.000 … Retido — Capital …
1.1.1.3.03.3.0.00.000 … Retido — Remessa …
1.1.1.3.03.4.0.00.000 … Retido — Outros …
1.1.1.4.00.0.0.00.000 … Produção e Circulação …
1.1.1.4.01.0.0.00.000 … IPI …
1.1.1.4.01.1.0.00.000 … IPI — Fumo …
1.1.1.4.01.2.0.00.000 … IPI — Bebidas …
… 4.01.3 … 4.01.4 … 4.01.5 …
1.1.1.4.50.0.0.00.000 …
1.1.1.5.00.0.0.00.000 …
1.1.2.0.00.0.0.00.000 … Taxas …
1.2.0.0.00.0.0.00.000 … Contribuições …
2.0.0.0.00.0.0.00.000 … Receitas de Capital …
```

| #    | Acção (prox nível) | Código destino          | NV destino | Fase                    |
| ---- | ------------------ | ----------------------- | ---------- | ----------------------- |
| 0    | —                  | `1.1.1.3.03.1.0.00.000` | 6          | início (`NV-TARGET:=6`) |
| 1    | prox nível         | `1.1.1.3.03.2.0.00.000` | 6          | L1                      |
| 2    | prox nível         | `1.1.1.3.03.3.0.00.000` | 6          | L1                      |
| 3    | prox nível         | `1.1.1.3.03.4.0.00.000` | 6          | L1                      |
| 4    | prox nível         | `1.1.1.4.00.0.0.00.000` | 4          | L2                      |
| 5    | prox nível         | `1.1.1.4.01.0.0.00.000` | 5          | L3                      |
| 6    | prox nível         | `1.1.1.4.01.1.0.00.000` | 6          | L3                      |
| 7–10 | prox nível         | `4.01.2` … `4.01.5`     | 6          | L1                      |
| 11   | prox nível         | `1.1.1.4.50.0.0.00.000` | 5          | L2                      |
| 12   | prox nível         | `1.1.1.5.00.0.0.00.000` | 4          | L2                      |
| 13   | prox nível         | `1.1.2.0.00.0.0.00.000` | 3          | L2                      |
| 14   | prox nível         | `1.2.0.0.00.0.0.00.000` | 2          | L2                      |
| 15   | prox nível         | `2.0.0.0.00.0.0.00.000` | 1          | L2                      |

**Comportamento anterior (obsoleto):** após o passo 4, saltos directos `4.00 → 5.00 → 1.1.2…` sem reentrar em `4.01…`, `4.01.1…`, etc.

**Nota:** códigos marcados como não navegáveis (ex.: «Classificação exemplo para não navegação») ficam **fora** do conjunto de candidatos **(T-cod.2)**; **(G-nav.next-code)** na L3 **salta** para o próximo existente.

---

## **(G-nav.prev-level)** — Nível anterior

Espelho de **(G-nav.next-level)** com **NV-TARGET** e fases L1–L3 invertidas:

| Fase   | **(G-nav.next-level)**                                            | **(G-nav.prev-level)**                                             |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------ |
| **L1** | Irmão **superior** no nível efectivo (`NV-EDIT ≥ NV-TARGET`)      | Irmão **inferior** no nível efectivo                               |
| **L2** | Subir: próximo irmão ancestral (etapa-3 de **(G-nav.next-code)**) | Subir: irmão ancestral anterior (etapa-3 de **(G-nav.prev-code)**) |
| **L3** | Se **NV-EDIT < NV-TARGET**: **um** passo de **(G-nav.next-code)** | Se **NV-EDIT > NV-TARGET**: **um** passo de **(G-nav.prev-code)**  |

### Exemplos L1 (inalterados em espírito)

#### Ex.: L1.1

- `COD-EDIT`: `1.1.1.2.53.0.0.00.000` (NV-EDIT=5); **NV-TARGET**=5
- `COD-NV-ANT`: `1.1.1.2.52.0.0.00.000` (NV-COD-NV-ANT=5)

#### Ex.: L1.2

- `COD-EDIT`: `1.1.1.2.00.0.0.00.000` (NV-EDIT=4); **NV-TARGET**=4
- `COD-NV-ANT`: `1.1.1.1.00.0.0.00.000` (NV-COD-NV-ANT=4)

### Ex.: L2 (ascendente)

- `COD-EDIT`: `1.1.1.2.00.0.0.00.000` (NV-EDIT=4); **NV-TARGET**=4
- prefixo reduzido: `"1.1.1"` (nível 3); dígito descartado: `"2"`
- `COD-NV-ANT`: `1.1.1.1.00.0.0.00.000` (NV-COD-NV-ANT=4)

### Sequência inversa (espelho da tabela IRPJ)

Com **NV-TARGET = 6** em `1.1.1.4.01.2.0.00.000`, **prev nível** percorre L1 (`4.01.1`), depois L3 ascendente (`4.01.0`, `4.00`) se necessário, L2 para ramo anterior (`3.03.4`, …), com descida espelhada via **prev-code** quando **NV-EDIT > NV-TARGET** após subida.

---

## **(G-nav.prev-code)** — Código anterior

### etapa-1

Como etapa-1 de **(G-nav.next-code)**, mas varredura do maior para o menor segmento no nível encontrado e, entre candidatos no nível, o de **maior** código completo (candidato estruturalmente **anterior** a **COD-EDIT**).

#### Ex.: 1.1

- `COD-EDIT`: `1.1.1.2.00.0.0.00.003` (NV-EDIT=9)
- **RAD-BASE**: `"1.1.1.2"` (K=4)
- `COD-ANT`: `1.1.1.2.00.0.0.00.002` (NV-COD-ANT=9)

---

#### Ex.: 1.2

- `COD-EDIT`: `1.1.1.2.52.0.2.00.000` (NV-EDIT=6)
- **RAD-BASE**: `"1.1.1.2.52"` (K=5)
- `COD-ANT`: `1.1.1.2.52.0.1.02.000` (NV-COD-ANT=8)

Obs.: `1.1.1.2.52.0.1.00.000` não é `COD-ANT` (existe candidato estruturalmente mais próximo no ramo anterior).

---

### etapa-2

Se etapa-1 não encontrar: manter `radical(NV-EDIT − 1)`; entre candidatos com segmento no nível **NV-EDIT** **inferior** ao atual, escolher o de **maior** código canônico completo (não apenas o template com zeros canônicos posteriores).

#### Ex.: 2.1

- `COD-EDIT`: `1.1.1.5.00.0.0.00.000` (NV-EDIT=4)
- prefixo: `"1.1.1"` (nível 3)
- `COD-ANT`: `1.1.1.4.00.0.0.00.000` (NV-COD-ANT=4)

#### Ex.: 2.2

- `COD-EDIT`: `1.1.1.2.53.0.0.00.000` (NV-EDIT=5)
- prefixo: `"1.1.1.2"` (nível 4)
- `COD-ANT`: `1.1.1.2.52.0.4.02.000` (NV-COD-ANT=8) — maior código no ramo `52` anterior a `53`

---

### etapa-3

Se etapa-2 não encontrar: repetição ascendente (nível `L` de `NV-EDIT − 1` até `1`), **maior** segmento no nível `L` **inferior** ao descartado, posteriores em zero canônico.

#### Ex.: 3.1

- `COD-EDIT`: `1.1.1.2.00.0.0.00.000` (NV-EDIT=4) — sem candidato nas etapas 1–2 no exemplo reduzido
- prefixo: `"1.1.1"`; dígito descartado no nível 4: `"2"`
- `COD-ANT`: `1.1.1.1.00.0.0.00.000` (NV-COD-ANT=4)

*(O caso `1.1.1.2.53…` → `1.1.1.2.52.0.4.02…` é coberto pela etapa-2 — Ex. 2.2.)*

---

## Testes manuais recomendados (change)

1. **Próximo código** nos Ex. 1.1 e 1.2 da base fictícia → `change` correta; botão inativo no último código global se não houver candidato.
2. **Código anterior** Ex. 1.2 e 2.2 → destino mais próximo no ramo (não apenas matriz `52.0.0.00.000`).
3. **Próximo / nível anterior** Ex. L1 e base IRPJ (tabela sequencial) — incluir re-descida L3 após L2 (`4.00 → 4.01 → 4.01.1`) e irmão intermédio `4.50` antes de `5.00`.
4. **Sequência de nível:** primeiro clique fixa **NV-TARGET**; clique em **próximo código** limpa `structural_nav_nv_target` da URL; parâmetro repassado nos redirects de nível.
5. Registro com vigência sem candidato **(T-cod.2)** → botão desabilitado (sem redirecionamento).
6. Mesmo `receita_cod`, duas linhas **(T-cod.2)** → desempate para vigência mais recente (`data_vigencia_fim`, depois início, depois `pk`).
7. Destino com outra `classificacao_id` → modal **(G-nav.ui-warning-class)**; Cancelar permanece; Continuar navega.
8. Formulário com `receita_nome` alterado → clique em navegação → `__coreConfirmUnsavedIfDirty` antes de qualquer redirect.
9. Change sem edição após carga → navegação **sem** `confirm` de alterações não guardadas.
10. Preservar `_changelist_filters` e `structural_nav_nv_target` no `change_url` retornado.
11. **UI:** barra `<<` `<` `>` `>>` à esquerda, `object-tools` à direita, acima do `.form-row` de `receita_cod`; ausente na add.
12. **UI:** hover/foco mostra `title` descritivo; leitor de ecrã recebe `aria-label`; desabilitado usa `title` da coluna «desabilitado».
13. **UI:** estilo neutro dos botões de navegação — não confundir visualmente com «+ Criar Código Filho» (verde).
