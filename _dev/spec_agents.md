# Orientações para agentes de IA (engenharia de contexto)

Este documento define **como agentes de IA** (Cursor, assistentes em IDE, automações)
devem trabalhar neste repositório ao implementar, refatorar ou documentar o
Classificador de Natureza de Receita.

**Não substitui** as specs de domínio nem as convenções de código — complementa-as
com protocolo operacional. Leia sempre em conjunto com:

- `_dev/spec_conventions.md` — nomenclatura, idioma, prefixo `code_`, inventário
- `_dev/spec_commits.md` — **obrigatório em qualquer pedido sobre commit** (Conventional Commits, staging, modo sugestão vs execução)
- `_dev/_dev.md` — linhas `See` imediatamente abaixo do título do commit
- `_dev/spec_*.md` — comportamento e regras por tema (domínio)

---

## Como citar este documento

| Mecanismo           | Uso                                                         |
| ------------------- | ----------------------------------------------------------- |
| **Seção numerada**  | `§ 10.3` — navegação neste arquivo.                         |
| **ID normativo**    | `AGENTS-18` — citação estável (catálogo compartilhado).     |
| **Índice completo** | `_dev/spec_conventions.md` § **2** (catálogo upstream).     |

---

## Modelo de trabalho: SDD (Spec-Driven Development)

O projeto adota **desenvolvimento orientado a especificações de domínio**:

- Especificações em linguagem natural em `_dev/spec_*.md` descrevem o que deve
  ser verdadeiro no domínio e nos fluxos (Admin, validações, mensagens).
- Convenções transversais em `_dev/spec_conventions.md` garantem consistência
  estrutural (módulos `code_*`, vocabulário temporal, nomes de arquivos).
- A implementação em Python, templates e JavaScript é produzida ou revisada com
  **assistência de IA**, desde que permaneça **rastreável** às specs.

Em resumo: **SDD com convenções transversais e implementação assistida por IA**.

**Variante de sync:** este repositório usa **`specs-trb`** (variant `trb` no catálogo).
`_dev/spec_commits.md` e `_dev/spec_issues.md` trazem normas **PT-BR** (upstream
`spec_commits-trb`, `spec_issues-trb`); `spec_agents` e `spec_conventions` seguem
fallback `default` do catálogo quando não há ficheiro `-trb` dedicado.

Quando existir contrato maduro em `docs/specs/` ou `specs/` (raiz), ele **prevalece**
sobre `_dev/` onde houver sobreposição; `_dev/` complementa por lacuna (**AGENTS-02**–**04**).

---

## Gatilho: pedidos sobre commit (obrigatório) **(AGENTS-10)**

Sempre que o operador mencionar **commit**, **git add**, **mensagem de commit**, **o que
commitar**, **push**, **staging** ou frases equivalentes («ajuda com o commit», «vamos
commitar», «sugestão de commit», «pode fazer o commit», etc.):

1. **Ler na íntegra** **`_dev/spec_commits.md`** antes de responder — não improvisar formato,
   escopo, modo sugestão vs execução nem regras de `dev(toDo)` só a partir deste arquivo.
2. **Ler** **`_dev/_dev.md`** para as linhas `See` (quando for redigir mensagem).
3. **Seguir** o protocolo de `spec_commits.md` (inventário/diff → agrupamento → `git add`
   sugerido → mensagem → encerramento com opções clicáveis; execução real só § Modo execução).
4. **Não** substituir `spec_commits.md` por hábitos genéricos de Conventional Commits ou por
   mensagens de commits antigos do repo sem verificar o diff atual.

Em dúvida, **`spec_commits.md` prevalece** (**AGENTS-12**).

O assistente **não deve** executar `git commit`, `git push` nem equivalentes sem pedido
**explícito** do operador (**AGENTS-11**).

---

## Ordem de leitura antes de alterar código

1. **`_dev/spec_conventions.md`** — obrigatório para nomenclatura e organização.
2. **Specs temáticas** ligadas à tarefa (ex.: nome no add → `spec_itemClassificacao_criar_nome.md`).
3. **`_dev/spec_django.md`** — quando a tarefa envolver Admin, models bitemporais ou estrutura Django.
4. **ADRs em `docs/adr/`** — quando a decisão arquitetural (bitemporalidade, chaves, layout de dados) for relevante; papéis de `docs/assets/`, `data-raw/` e `data/` → **ADR-005**.
5. **`_dev/spec_import_*.md`** — quando a tarefa envolver o protocolo de importação *(spec a redigir)*.
6. Par `_dev/spec_<tema>.md` + `_dev/spec_<tema>_new.md` — se o pedido for atualização de specs
   do catálogo, aplicar § **10** antes de editar o local.

Não inventar regra de domínio que não esteja nas specs ou no código existente sem
sinalizar ao operador (**AGENTS-09**).

---

## Versionamento

Antes de concluir tarefa que alterou specs ou código normativo, **avaliar** impacto
conforme `_dev/spec_version.md` (SemVer, tags). Commits neste repositório seguem
`spec_commits.md`. Alterações em `_dev/spec_*.md` que sejam **padrão genérico**
reutilizável são candidatas a elevação ao catálogo upstream (**AGENTS-14**); não publicar
automaticamente.

---

## Padrões técnicos de referência (não duplicar aqui)

Normas externas aplicam-se **quando a tarefa as tocar**; regra de domínio e
comportamento continuam nas `spec_*.md` temáticas. Este bloco é um **índice** —
não repetir o conteúdo de `spec_commits.md`, `spec_conventions.md` nem das specs
funcionais.

| Tema                               | Referência externa                                                                                                                                                                                   | Onde no repositório                                                            |
| ---------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| Commits e staging                  | [Conventional Commits](https://www.conventionalcommits.org/) (adaptado)                                                                                                                              | `_dev/spec_commits.md` — **obrigatório** em pedidos de commit (§ Gatilho)      |
| Nomenclatura, `code_*`, idioma     | Convenções do projeto                                                                                                                                                                                | `_dev/spec_conventions.md`                                                     |
| Admin, models, migrações Django    | Estrutura e bitemporalidade                                                                                                                                                                          | `_dev/spec_django.md`, ADRs em `docs/adr/`                                     |
| Python (estilo, docstrings, types) | [PEP 8](https://peps.python.org/pep-0008/); [PEP 257](https://peps.python.org/pep-0257/) em APIs públicas não óbvias; [PEP 484](https://peps.python.org/pep-0484/) quando o módulo já usa type hints | `apps/core/` — seguir o estilo do arquivo tocado                               |
| Linguagem normativa em specs       | [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) (MUST / SHOULD / MAY)                                                                                                                             | `_dev/spec_*.md` ao redigir ou interpretar requisitos                          |
| Contratos JSON no Admin            | Spec do fluxo                                                                                                                                                                                        | ex. `_dev/spec_itemClassificacao_foreignKeys_lookup.md`                        |
| API HTTP com erros estruturados    | [RFC 7807](https://www.rfc-editor.org/rfc/rfc7807) (problem details)                                                                                                                                 | Só se a tarefa criar ou alterar endpoint HTTP público; caso contrário, ignorar |

### Documentação (SDD primeiro)

| Tipo de mudança                                               | Onde documentar                                                                                           |
| ------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| Comportamento, fluxo Admin, mensagens ao usuário              | Atualizar a **`_dev/spec_*.md` temática** (trechos afetados)                                              |
| Novo módulo `code_*` ou rename                                | Inventário em **`_dev/spec_conventions.md`**                                                               |
| Decisão arquitetural duradoura                                | ADR em **`docs/adr/`**                                                                                    |
| Layout de pastas de dados (`data`, `data-raw`, `docs/assets`) | **ADR-005** + índice em **`spec_conventions.md`**; detalhe operacional do import em **`spec_import_*.md`** |
| Anotações pessoais de desenvolvimento                         | `_dev/toDo.md` (commit `dev(toDo)` — ver `spec_commits.md`)                                               |

#### Idioma da documentação (português do Brasil)

Sempre que redigir ou revisar texto em **português** no repositório — specs em
`_dev/spec_*.md`, **ADRs** em `docs/adr/`, páginas em `docs/`, comentários
normativos em README — usar **português do Brasil**, não português de Portugal.

Orientações práticas (lista não exaustiva):

| Preferir (pt-BR) | Evitar (pt-PT)                           |
| ---------------- | ---------------------------------------- |
| arquivo          | ficheiro                                 |
| artefato         | artefacto                                |
| usuário          | utilizador                               |
| registro         | registo                                  |
| seção            | secção                                   |
| conceitual       | conceptual                               |
| intermediário    | intermédio                               |
| refatoração      | refactor (como substantivo de documento) |

Termos técnicos em **inglês** (`foreignKey`, `valid_time`, `commit`, nomes de
pastas e identificadores de código) permanecem como já estão. Mensagens ao
usuário final no Admin: **português do Brasil** (ver também
`_dev/spec_conventions.md`, § Idioma e nomenclatura).

**Não** exigir página em `docs/` para cada alteração de código. **Não** inventar
SemVer de release, pastas `up.sql`/`down.sql`, pipelines genéricos ou tabelas
`schema_version` / `automation_log` salvo existirem no repositório ou pedido
explícito do operador.

### O que não listar em toda resposta

Em tarefas triviais (typo, ajuste pontual), **não** repetir checklist de PEP/RFC.
Em tarefas não triviais, mencionar PEP/RFC **só** se a implementação os tiver
aplicado (ver § Saída esperada).

---

## Nomenclatura e novos arquivos

Ao **sugerir ou criar** arquivos Python, funções, classes, métodos, módulos JS
do núcleo do classificador ou testes espelhados:

- Consultar **`_dev/spec_conventions.md`** (camadas de idioma, prefixo `code_`,
  inventário, tabela `schemas/dominios/` → módulo `code_*`).
- Novo catálogo em `schemas/dominios/*.yaml`: módulo espelho em **inglês**
  (`code_organizations_entities.py` para `orgaos_entidades.yaml`); atualizar a tabela na spec de convenções.
- Em dúvida entre traduzir o slug do domínio ou espelhá-lo no nome do arquivo `.py`,
  **perguntar ao operador** ou seguir a tabela domínio → módulo já registrada.
- Respeitar padrões já usados no pacote (`code_*`, `classification_item_*`, `tests_code_*`, `tests_classification_item_*`).
- Após introduzir ou renomear módulo `code_*`, **atualizar o inventário** em
  `spec_conventions.md`.

Mensagens exibidas ao usuário final no Admin permanecem em **português do Brasil**,
conforme cada spec funcional — salvo pedido explícito em contrário.

---

## Protocolo de contradição (obrigatório) **(AGENTS-15)**

Se uma instrução do operador **contradizer** texto normativo em `_dev/spec_*.md`,
`_dev/spec_conventions.md` ou ADR citado pelo projeto:

1. **Não implementar silenciosamente** a parte contraditória.
2. **Alertar o operador** de forma explícita, citando:
   - o que foi pedido;
   - o que a spec/ convenção diz (nome do arquivo, § ou ID, se possível);
   - o conflito em uma frase clara.
3. Perguntar se deve **priorizar o pedido** (e então sugerir atualizar a spec) ou
   **seguir a spec** (e ajustar o pedido).

O mesmo protocolo aplica-se quando **código e spec divergem**: reportar
«spec diz X, código faz Y» e pedir alinhamento antes de refactors amplos.

---

## Sugestão de commit e staging (`git add`)

**Pré-requisito:** § Gatilho: pedidos sobre commit (ler `spec_commits.md` na íntegra).

Resumo do que `spec_commits.md` exige (detalhes e exemplos lá):

### Modo sugestão (padrão)

Pedidos como «ajuda com o commit», «vamos fazer o commit», «sugestão de commit», etc.:

1. **Inventariar** — `git status` / diff; resumir conteúdo alterado.
2. **Agrupar** — proposta(s) numerada(s): arquivos → `git add` (copy-paste) → mensagem.
3. **Dúvidas** (vários commits, incluir `toDo`, …) — opções **clicáveis**; não adivinhar.
4. **`See`** — copiar **`_dev/_dev.md`** (linha a linha). Atualizar toDo → `dev(toDo): atualizar anotações`, sem corpo.
5. **Encerrar** perguntando com clique se deve **executar commit completo** (e qual proposta).
6. **Nunca** executar `git commit` / `git push` neste modo — só texto e comandos sugeridos.

### Modo execução (só se explícito)

Só quando o operador pedir claramente para **fazer/executar o commit** (ex.: «pode fazer o commit»):

1. Se houver várias propostas, **perguntar com clique** qual executar.
2. **Confirmar** com clique: executar `git add`+`git commit`? fazer **push**?
3. Só então executar no terminal.

---

## Protocolo de implementação

- Regras de negócio reutilizáveis → módulos `apps/core/code_*.py` (ver convenções).
- Orquestração Admin / endpoints / templates → módulos e arquivos já existentes
  do fluxo (`admin.py`, `classification_item_*`, `change_form.html`, etc.).
- Alterar specs funcionais apenas nos trechos afetados; **não duplicar** em cada
  spec a política global do prefixo `code_` (manter em `spec_conventions.md`).
- **Não criar commit** nem push salvo pedido explícito do operador (**AGENTS-11**).
- Preferir diff mínimo e alinhado ao estilo do arquivo tocado.

---

## Saída esperada em tarefas não triviais

Quando útil, resumir brevemente:

- quais specs foram consideradas;
- suposições feitas;
- pontos sem spec (incerteza);
- contradições encontradas (se houver), com § ou ID;
- avaliação de versionamento (impacto ou «sem bump»), se alterou specs ou releases;
- PEP/RFC ou ADR relevantes **apenas** se a tarefa os tiver tocado (§ Padrões técnicos de referência);
- integração conservadora ou análise reversa com par `*_new.md` em `_dev/`, se aplicável (§ **10**).

---

## 10. Sincronização em `_dev/` e arquivo `*_new.md` (protocolo conservador)

Este protocolo aplica-se **somente** a arquivos sob **`_dev/`** sincronizados do
**catálogo compartilhado** (`.specs-sync.yaml`). **Não** se estende a specs de
domínio (`spec_itemClassificacao_*.md`, `spec_django.md`, …) nem a `docs/adr/`.
**(AGENTS-17)**

### 10.1 O que cada arquivo representa em `_dev/`

| Artefato                           | Papel                                                                                                                                                                                                                                  |
| ---------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `_dev/spec_<tema>.md` (sem `_new`) | **Cópia de trabalho neste repositório** — adaptações Django, `code_*`, ADRs, cortes locais.                                                                                                                                              |
| `_dev/spec_<tema>_new.md`          | **Referência do catálogo canónico** — espelho para comparar; **não** substitui o local nem atualiza sozinho `.specs-sync.yaml`.                                                                                                        |

### 10.2 Quando aplicar este protocolo (gatilhos de pedido)

O assistente **deve** seguir § **10** quando o operador pedir **atualização de especificações**,
**sincronizar com o catálogo**, **merge do catálogo**, **revisar o `_new`**, ou equivalente —
**e** existir par local + `*_new.md`.

### 10.3 Integração catálogo → local (fluxo principal)

1. Ler **os dois** arquivos; usar `specs <chave> -df` se o operador pedir diff explícito.
2. **Preservar** no **local** trechos de domínio Django, `code_*`, ADRs, paths e exceções deste projeto.
3. **Incorporar** do `*_new.md` apenas norma genérica do catálogo compatível com este repo.
4. **Não** substituir o local inteiro pelo `*_new`, salvo pedido **explícito**. **(AGENTS-18)**
5. Sugerir remover o `*_new.md` quando merge completo; `specs commit` / `specs ci` para reconciliar
   `.specs-sync.yaml`; **não** executar `specs -ps`, `git commit` ou `push` sem pedido (**AGENTS-11**).

### 10.4 Análise reversa (local → catálogo)

Quando pedido **elevar padrão ao catálogo**: identificar trechos **genéricos** (**AGENTS-14**);
atualizar `*_new.md` como rascunho; **manter no local** regras Django/`code_*`/splor-mg.
**Não** publicar no catálogo canónico sem pedido explícito (**AGENTS-19**).

### 10.5 Saída esperada (merge ou análise reversa)

- O que permaneceu só no local e por quê.
- O que entrou no local a partir do catálogo.
- Decisões em aberto (conflitos, bump de catálogo).
- Lembrete: não commitar `*_new.md` por engano se a intenção era só o local.

---

## Manutenção deste documento

Ao mudar o processo de trabalho com IA (novas pastas obrigatórias, nova spec hub,
ferramenta de agente), atualizar **`spec_agents.md`** e, se necessário, uma linha
de referência em `spec_conventions.md`. Alterações genéricas reutilizáveis: elevação
ao catálogo (**AGENTS-14**).
