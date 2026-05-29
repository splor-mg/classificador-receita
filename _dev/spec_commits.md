# Convenção de mensagens de commit (Semantic Commits)

Commits neste repositório seguem **[Conventional Commits](https://www.conventionalcommits.org/)**
adaptado às especificidades desse repositório.

**Regra central para LLM/IDE:** o trabalho padrão é **sugerir** (`git add`, mensagens,
comandos copy-paste) — **não** executar `git commit`, `git push` nem equivalentes “por detrás
do pano”. Execução real só após pedido **explícito** do operador e confirmação com opções
clicáveis (§ Modo execução).

---

## Modo sugestão (padrão) vs modo execução

| Modo         | Quando                                                                           | O que a LLM/IDE faz                                                | O que **não** faz                                     |
| ------------ | -------------------------------------------------------------------------------- | ------------------------------------------------------------------ | ----------------------------------------------------- |
| **Sugestão** | Pedido genérico ou “ajuda com commit” (§ Pedidos genéricos)                      | Protocolo § Sugestão de staging; mensagens; `git add` para copiar  | `git add` / `git commit` / `git push` sem autorização |
| **Execução** | Operador **explícito**: “pode fazer o commit”, “executa o commit completo”, etc. | § Modo execução — confirmações com clique antes de correr comandos | Commitar sem confirmar qual proposta e se inclui push |

### Pedidos genéricos → só protocolo de sugestão

Frases como as abaixo **não** autorizam commit real; disparam **apenas** o protocolo de sugestão
(§ Sugestão de staging):

- «quero ajuda com o commit»
- «me ajude com o commit»
- «vamos fazer o commit»
- «sugestão de commit», «mensagem de commit», «o que commitar», congêneres

Ao final da resposta em modo sugestão, **perguntar com opção clicável** se o operador deseja que
a LLM/IDE **execute o commit completo** (ver § Encerramento da sugestão).

### Modo execução (commit real)

Só após o operador ser **explícito** no sentido de executar (ex.: «pode fazer o commit»,
«faz o commit completo», «pode commitar»):

1. Se houve **várias propostas numeradas** (Commit A, B, …), **perguntar com clique** qual(is)
   executar — não assumir a primeira.
2. **Confirmar com opções clicáveis** (mutuamente exclusivas onde couber):
   - Executar **`git add` + `git commit`** com a mensagem acordada? (Sim / Não)
   - Executar também **`git push`**? (Sim / Não)
3. Só então correr os comandos no terminal, na ordem acordada.

Se o pedido for ambíguo («commit isso» sem ter pedido execução antes), tratar como **modo
sugestão** e oferecer execução no final com clique.

### Encerramento da sugestão (obrigatório se não for execução)

Depois de entregar `git add` + mensagem(ns), incluir pergunta clicável do tipo:

- **A)** Só usar as sugestões manualmente (não executar nada na IDE)  
- **B)** Executar o commit completo na IDE (sem push)  
- **C)** Executar commit completo **e** push  

Se existirem várias propostas de commit, a pergunta deve referir **qual proposta** (A/B/C da
lista numerada) antes ou junto da escolha B/C.

---

## Estrutura da mensagem

```
<tipo>(<escopo opcional>): <título — ver § Composição do título>

<linhas See * — obrigatório; copiar de _dev/_dev.md>

<corpo opcional — parágrafos em PT-BR; detalhe do que mudou>
```

Linha em branco entre o título e as linhas `See`; linha em branco entre o bloco `See` e o corpo.

### Composição do título (Conventional Commits)

O título é **uma linha** com três partes:

```text
<tipo>(<escopo>): <mensagem resumida>
```

| Parte                   | Função                                                                                                                  |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| **`tipo`**              | Natureza da mudança (§ Tipos) — o que o commit *é* (documentação, feature, fix, …).                                     |
| **`escopo`**            | Módulo ou tema afetado (§ Escopo), entre parênteses — opcional mas recomendado.                                         |
| **`mensagem resumida`** | Texto **após** `(<escopo>): ` — o que o repositório/projeto **passa a ter ou a conseguir** se este commit for aplicado. |

**Ideia da mensagem resumida:** responder implicitamente: *«Se o utilizador aplicar este commit,
o projeto vai …»* — em poucas palavras, sem ponto final no fim da linha.

**Redação em português (este repositório):**

- Começar a mensagem (após os dois pontos do escopo) com **verbo no infinitivo**: *implementar*,
  *adicionar*, *corrigir*, *documentar*, *renomear*, *atualizar*, …
- **Evitar** título só com substantivos («convenção de commits …») sem verbo inicial.
- ≤ ~72 caracteres no título completo, quando possível.

**Exemplos de título:**

| Fraco (evitar)                                  | Melhor                                                      |
| ----------------------------------------------- | ----------------------------------------------------------- |
| `feat(commits): convenção de commits e staging` | `docs(commits): implementar convenção de commits e staging` |
| `refact(code): pacote code_*`                   | `refact(code): renomear módulos para pacote code_*`         |

**Corpo da mensagem (após o bloco `See`):** parágrafos opcionais; listar ficheiros ou resumir
alterações; foco no *porquê* e no efeito — não repetir o título em prosa.

### Linhas `See` e corpo

- **Logo abaixo do título:** copiar **todas** as linhas `See …` de **`_dev/_dev.md`**, uma por linha.
- **Depois do `See`:** corpo opcional (§ acima).

### Tipo vs ficheiros alterados

| Diff principal                                    | Tipo usual                                    | Nota                                                                                          |
| ------------------------------------------------- | --------------------------------------------- | --------------------------------------------------------------------------------------------- |
| Só `_dev/spec_*.md`, `docs/`, README (sem código) | **`docs`**                                    | Mesmo que a spec descreva um processo novo — não usar `feat` só por ser “feature” conceptual. |
| Código + specs alinhadas ao mesmo comportamento   | `feat` / `fix` / `refact` + escopo do domínio | Specs no mesmo commit quando mesma causa.                                                     |
| Só `toDo.md`                                      | **`dev`**                                     | Título fixo § Commit só de toDo.                                                              |

`feat` reserva-se a mudança **implementada** em código (ou JS/CSS do Admin) visível ou comportamental.

---

## Tipos (`<tipo>`)

| Tipo     | Quando usar                                                    |
| -------- | -------------------------------------------------------------- |
| `feat`   | Comportamento novo ou extensão em **código** / Admin / API     |
| `fix`    | Correção de bug em código ou comportamento                     |
| `refact` | Mudança interna em código sem alterar comportamento observável |
| `docs`   | Só documentação (`_dev/spec_*.md`, `docs/`, README, ADR)       |
| `dev`    | Anotações de desenvolvimento (`toDo`, rascunhos em `_dev/`)    |
| `test`   | Só testes                                                      |
| `chore`  | Build, deps, tooling, tarefas sem impacto de produto           |

Evitar tipos genéricos quando um tipo acima couber. Não usar `feat` quando o diff for **apenas**
documentação (usar `docs`).

---

## Escopo (`<escopo>`)

Opcional, em **camelCase** ou **kebab-case** quando já usado no histórico (`code-name`,
`changelist-filters`). Ao sugerir escopo, seguir **nesta ordem**:

### 1. Aderência temática em `spec_convencoes.md`

Consultar subfamílias, inventário `code_*` e tabelas de domínio em **`_dev/spec_convencoes.md`**.
Se o commit for claramente um tema já nomeado lá, usar esse escopo:

| Tema do commit                                                                              | Escopo sugerido                               | Tipo usual                                              |
| ------------------------------------------------------------------------------------------- | --------------------------------------------- | ------------------------------------------------------- |
| Pacote / rename `code_*`, regras transversais de módulos                                    | `code` ou `code-name` (rename focado em nome) | —                                                       |
| SDD, `spec_agents`, engenharia de contexto                                                  | `sdd`                                         | —                                                       |
| Filtros recolhidos do sidebar do Admin                                                      | `changelist-filters`                          | —                                                       |
| Convenção de commits, staging, modo sugestão/execução (`spec_commits.md`, `spec_agents.md`) | `commits`                                     | `docs(commits)`; `feat` só com código no mesmo commit   |
| Só `spec_convencoes.md` (sem `spec_commits`)                                                | `convencoes`                                  | `docs(convencoes)`                                      |

### 2. Spec funcional que dá sentido à alteração

Se não houver encaixe óbvio em `spec_convencoes.md`, perguntar implicitamente:
**qual arquivo `_dev/spec_*.md` principal justifica o diff?** Derivar o escopo do **nome do
ficheiro** da spec:

**Regra:** prefixo fixo `spec_` + **primeiro segmento** até ao **segundo** sublinhado `_`
(inclusive em camelCase no segmento).

| Ficheiro da spec                          | Escopo              |
| ----------------------------------------- | ------------------- |
| `spec_itemClassificacao_criar_filho.md`   | `itemClassificacao` |
| `spec_itemClassificacao_criar_nome.md`    | `itemClassificacao` |
| `spec_itemClassificacao_editar_codigo.md` | `itemClassificacao` |
| `spec_foreignKeys_vigencia.md`            | `foreignKeys`       |
| `spec_lista_abreviacoes.md`               | `lista`             |
| `spec_django.md`                          | `django`            |
| `spec_validar_codigos.md`                 | `validar`           |

Specs com **apenas um** segmento após `spec_` (sem segundo `_`): usar esse segmento inteiro
— ex. `spec_convencoes.md` → `convencoes`, `spec_agents.md` → `agents`, `spec_commits.md` → `commits`.

**Rename de spec:** quando várias alterações existem **porque** um ficheiro `spec_*.md` (ou
módulo) foi renomeado e outros ficheiros só atualizam referências/caminhos, o escopo deve
ser derivado do **nome antigo** do ficheiro que motivou a mudança (regra do segmento após
`spec_` aplicada ao nome **antes** do rename). Ex.: rename `spec_itemClassificacao_foo.md` →
`spec_itemClassificacao_bar.md` + 8 ficheiros com paths atualizados → escopo continua
`itemClassificacao`, não `itemClassificacao` a partir de `bar`.

### 3. Vários ficheiros num único commit (mesma causa)

**Não há problema** em agregar vários caminhos num só commit quando a alteração conjunta tem
**uma causa** — por exemplo:

- rename de uma spec ou módulo `code_*` e atualização de todos os imports/referências;
- introdução de `spec_commits.md` junto com ajustes correlatos em `spec_agents.md` e
  `spec_convencoes.md`;
- refactor mecânico (só caminhos ou nomes) sem mudança de comportamento.

Nesse caso:

- **Escopo:** spec ou artefacto **principal** que dá sentido ao conjunto (§ 1–2); em rename,
  nome **antigo** (acima).
- **Tipo:** `refact` se só rename/paths em código; **`docs`** se só specs/docs; `feat` só com
  código no mesmo commit (§ Tipo vs ficheiros alterados).
- **Corpo:** pode listar ficheiros tocados ou resumir a causa única («alinhamento após
  rename de …»).

`_dev/toDo.md` no mesmo commit **só** se o operador confirmar; por defeito, commit separado
`dev(toDo)` (§ Commit só de toDo).

### 4. Vários temas distintos no mesmo commit

Se o working tree mistura **causas independentes** (ex. `itemClassificacao` + pacote `code_*`
+ `toDo`), preferir **commits separados** (§ Sugestão de staging). Se o operador insistir
num único commit, escolher escopo da causa **dominante** e mencionar no corpo o restante.

### 5. Sem spec nem convenção clara

Omitir escopo ou usar escopo curto descritivo já presente no `git log` da branch; **não**
inventar camelCase novo sem relação com ficheiro ou convenção existente.

---

## Commit só de `_dev/toDo.md`

Quando o operador pedir para **atualizar o toDo** (ou o diff for essencialmente só
`_dev/toDo.md`), a mensagem sugerida é **mínima**:

```
dev(toDo): atualizar anotações

See #18
See https://github.com/splor-mg/classificador-receita/tree/migracao
```

- Título fixo: **`dev(toDo): atualizar anotações`** (ajustar só se o operador pedir outro título).
- Linhas **`See`** copiadas de **`_dev/_dev.md`** (todas as linhas do ficheiro, uma por linha).
- **Sem corpo** (sem parágrafos após o bloco `See`).
- `git add` sugerido: `_dev/toDo.md` (salvo o operador pedir outros ficheiros).

---

## Boas práticas

- **Não** executar `git add`, `git commit` nem `git push` no modo sugestão; execução só § Modo execução.
- Agrupar renomeações/refactors com specs que atualizam os mesmos caminhos.
- Bullets no corpo só quando listarem renomeações ou itens de teste claros.
- Não incluir `Co-authored-by` salvo política do time ou hook do ambiente.
- Não sugerir `git add` de ficheiros com credenciais (`.env`, chaves, tokens).
- Para sugerir `git commit`: usar HEREDOC, ex. `git commit -m "$(cat <<'EOF' … EOF)"`.

---

## Sugestão de staging (`git add`) e commits

Quando o operador pedir **sugestão de commit**, **o que commitar**, **git add** ou equivalente,
entregar um **pacote revisável**: staging proposto + mensagem(ns) — não só o texto do commit.

### Passo 1 — Inventariar alterações

1. Correr (ou equivalente) `git status --short` e, por ficheiro relevante, inspecionar o diff
   (`git diff`, `git diff --staged`, ou diff da IDE).
2. Classificar cada caminho: **código**, **spec `_dev/`**, **schema/docs**, **anotações pessoais**
   (`toDo.md`, rascunhos), **ruído** (espaços, ficheiros `Untitled`, alterações não relacionadas).
3. Ligar cada grupo ao **tema** (§ Escopo): spec principal, `spec_convencoes`, pacote `code_*`, etc.

### Passo 2 — Propor um ou mais commits

**Preferência:** um commit por **causa** coerente (§ Escopo § 3); vários ficheiros no mesmo
commit são bem-vindos quando partilham essa causa. Se o working tree misturar **temas distintos**,
propor **vários commits** numerados (Commit A, Commit B, …), cada um com:

| Bloco              | Conteúdo                                                                                   |
| ------------------ | ------------------------------------------------------------------------------------------ |
| **Ficheiros**      | Lista de caminhos (e nota `git mv`/rename se aplicável)                                    |
| **Resumo do diff** | 1–3 frases do que mudou no conteúdo (não só nomes de ficheiro)                             |
| **`git add`**      | Comandos copy-paste (`git add path1 path2` ou `git add -p` se pedirem granularidade)       |
| **Mensagem**       | Título + linhas `See` de `_dev/_dev.md` + corpo (exceto `dev(toDo)` — § Commit só de toDo) |

**Exemplo de bloco para um commit:**

```bash
# Commit 1 — pacote code_* (código + specs de caminho)
git add apps/core/code_*.py apps/core/tests_code_*.py \
  apps/core/admin.py apps/core/forms.py apps/core/models.py \
  _dev/spec_convencoes.md _dev/spec_foreignKeys_vigencia.md
```

```
refactor(code): consolidar pacote code_* de regras de negócio reutilizáveis

See #18
See https://github.com/splor-mg/classificador-receita/tree/migracao

…
```

### Passo 3 — Ficheiros frequentemente à parte

| Situação                                     | Sugestão usual                                                   |
| -------------------------------------------- | ---------------------------------------------------------------- |
| Só `_dev/toDo.md` ou pedido «atualizar toDo» | § Commit só de toDo; ou **não** incluir até o operador confirmar |
| Spec de commits/agents sem código            | `docs(sdd): …` ou `docs(convencoes): …`                          |
| Alterações já staged + unstaged misturadas   | Explicar o que está em cada estado antes de sugerir `add`        |

### Passo 4 — Dúvida sobre abordagem → perguntar com opções clicáveis

Se não estiver claro se o operador quer **um commit único**, **vários commits temáticos** ou
**excluir** certos ficheiros (ex. `toDo.md`), **não adivinhar**. Perguntar com **2–4 opções
mutuamente exclusivas**, formuladas para resposta por **um clique** na IDE (ferramenta de
pergunta estruturada / múltipla escolha do agente), por exemplo:

- **A)** Um único commit com tudo listado  
- **B)** Dois commits: (1) código `apps/` (2) só `_dev/spec_*.md`  
- **C)** Três commits conforme proposta numerada abaixo  
- **D)** Excluir `toDo.md` e rascunhos; commitar o restante  

Incluir na pergunta um **resumo de uma linha** por opção (quantos ficheiros / qual escopo).
Após a escolha, gerar só os blocos `git add` + mensagens correspondentes.

### Passo 5 — Formato da resposta ao operador

Ordem sugerida na mensagem (modo sugestão):

1. **Resumo** (1 parágrafo): o que o diff faz no conjunto.  
2. **Pergunta com opções** (se houver dúvida material sobre agrupamento).  
3. **Proposta de commits** (numerada): ficheiros → `git add` → mensagem completa cada uma.  
4. **Encerramento** — § Encerramento da sugestão (pergunta clicável: executar commit/push ou não).  
5. Lembrete explícito: **a IDE não commitou nada** nesta resposta, salvo modo execução confirmado.

---

## Exemplo mínimo (só mensagem)

```
feat(itemClassificacao): bloquear submit quando código já existe na add

See #18
See https://github.com/splor-mg/classificador-receita/tree/migracao

Validação CE no cliente e no servidor; mensagem compartilhada com o endpoint.
```

Exemplo só documentação:

```
docs(commits): implementar convenção de commits e staging para agentes

See #18
See https://github.com/splor-mg/classificador-receita/tree/migracao

Adiciona spec_commits.md; reforça spec_agents.md e spec_convencoes.md.
```

---

## Referências

- Linhas `See *` obrigatórias (fonte única): **`_dev/_dev.md`**
- Escopo e temas transversais: **`_dev/spec_convencoes.md`**
- Agentes de IA: **`_dev/spec_agents.md`** (fluxo completo: status/diff → `git add` → mensagem)
