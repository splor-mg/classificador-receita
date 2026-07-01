# Especificação local — classificador-receita

Normas de **processo SDD** deste repositório que complementam ou divergem do catálogo sincronizado em `_dev/` (`spec_agents`, `spec_commits`, `spec_issues`, …). **Não substitui** specs de domínio (`spec_itemClassificacao_*.md`, `spec_django.md`, …) nem entradas **sync** do manifest — estas permanecem read-only (**AGENTS-07**).

## Objetivo

Registrar overrides locais de **como** trabalhar (idioma de commits e issues, escopos, inventário `code_*`, layout de dados, hub de prefixos de domínio) e a ordem de leitura para tarefas no **Classificador de Natureza de Receita**.

Premissa: regras de **negócio** e comportamento funcional permanecem nas specs temáticas locais ou no contrato maduro futuro — não neste arquivo (**CLREC-02**, **AGENTS-26**).

## Referências

- [`_dev/spec_agents.md`](spec_agents.md) — precedência SDD (**AGENTS-22**, **AGENTS-25**), specs locais (**AGENTS-04**), `*_new.md` § **10**.
- [`_dev/spec_commits.md`](spec_commits.md) — Conventional Commits, `See`, staging § **8** (baseline genérica).
- [`_dev/spec_issues.md`](spec_issues.md) — padrão `.github/issues/`, sentence case (**ISSUES-01**–**04**).
- [`_dev/spec_conventions.md`](spec_conventions.md) — RFC 2119, modelo de documento § **9** (**CONV-32**–**38**).
- [`_dev/.specs-sync.yaml`](.specs-sync.yaml) — chaves sync do catálogo no consumidor.
- ADRs em `docs/adr/` — **ADR-001** a **ADR-005** (índice § **7**).
- Specs de domínio locais — índice § **7**; prefixos § **5.8**.

Termos *deve* / *não deve* / *pode* conforme RFC 2119 (ver `_dev/spec_conventions.md` **Referências**).

**Migração de símbolos legados:**

| Legado | ID atual |
| ------ | -------- |
| Secções `## Agents` / `## Commits` / `## Issues` / `## Convenções` | § **2** / **3** / **4** / **5** (títulos preservam o nome temático) |
| Citações `§ **Agents**` no corpo | § **2** (equivalente semântico) |

## Como citar este documento

| Mecanismo          | Uso                                                                 |
| ------------------ | ------------------------------------------------------------------- |
| **Seção numerada** | `§ N` / `§ N.M` — navegação neste arquivo.                          |
| **ID normativo**   | `CLREC-NN` — citação estável de processo local.                     |
| **Prefixo domínio**| Ver § **5.8** — hub de prefixos (`ITEMNOM`, `DJANGO`, …); não usar `CLREC` para domínio. |

**Índice de IDs normativos deste arquivo:**

| ID        | Tema        | Seção | Resumo                                                                                                                                 |
| --------- | ----------- | ----- | -------------------------------------------------------------------------------------------------------------------------------------- |
| CLREC-01  | Precedência | 1.1   | Processo: contrato maduro → **este arquivo** → cópia sync → `toolkit/<tool>/specs/` (**AGENTS-22**, **AGENTS-25**).                    |
| CLREC-02  | Escopo      | 1.2   | Overrides de **processo** aqui; regras de **negócio** em `spec_<domínio>.md` ou contrato maduro (**AGENTS-26**).                        |
| CLREC-03  | Escopo      | 1.3   | Seções vazias **podem** ser omitidas; criar seção ao documentar o primeiro tema; alinhar títulos às chaves do manifest quando aplicável. |
| CLREC-10  | Identidade  | 2.1   | Repositório implementa Classificador de Natureza de Receita (Django Admin, bitemporal, classificação orçamentária).                      |
| CLREC-11  | Processo    | 2.2   | Modelo SDD: convenções transversais neste arquivo + specs locais + implementação assistida por IA rastreável.                          |
| CLREC-12  | Override    | 2.3   | Commits e issues em **pt-BR** — § **3** e § **4** prevalecem sobre sync (**AGENTS-25**); **não** reeditar entradas sync para PT-BR.     |
| CLREC-13  | Leitura     | 2.4   | Ordem local pós-`spec_agents.md` § **1.2**: § **5** → spec temática → `spec_django.md` → ADRs → import → `*_new.md` se manifest.       |
| CLREC-14  | Lacuna      | 2.5   | **Não** inventar regra de domínio sem spec ou código; sinalizar lacunas (**AGENTS-09**).                                               |
| CLREC-15  | Registro    | 2.6   | Tabela «Onde registrar mudanças» — Admin/spec temática, `code_*`, ADR, layout, overrides, `toDo.md`.                                   |
| CLREC-16  | Code        | 2.7   | Negócio reutilizável → `code_*.py`; orquestração Admin/JSON/templates → fluxo sem prefixo `code_`; specs citam caminhos, não duplicam.   |
| CLREC-17  | Sync        | 2.8   | `*_new.md`: genérico no sync; regras deste projeto aqui ou specs domínio; merge § **10** `spec_agents.md`; remover sidecar quando OK.  |
| CLREC-18  | Idioma      | 2.9   | `_dev/`, ADRs, `docs/`, README em **pt-BR**; tabela preferir/evitar pt-PT § **2.9**; UI Admin pt-BR salvo spec em contrário.          |
| CLREC-19  | Idioma      | 2.10  | Respostas IDE em **inglês** (**AGENTS-07**); código e comentários Python em **inglês** (**AGENTS-08**).                                |
| CLREC-30  | Commit      | 3.1   | Título e corpo de commit em **pt-BR** — override **COMMITS-05** / § **3.1** sync (**AGENTS-25**).                                      |
| CLREC-31  | Commit      | 3.2   | Linhas `See …` iguais à baseline — copiar de `_dev/_dev.md` (**COMMITS-06**).                                                          |
| CLREC-32  | Commit      | 3.3   | Após `(<escopo>): `: verbo no **infinitivo**; corpo claro, foco no *porquê*.                                                           |
| CLREC-33  | Commit      | 3.4   | `_dev/toDo.md`: título fixo `dev(toDo): atualizar anotações`.                                                                           |
| CLREC-34  | Commit      | 3.5   | Escopo: tabela local → derivar do basename `spec_*` (regras § **3.3**) → rename usa nome antigo.                                       |
| CLREC-35  | Commit      | 3.6   | `feat` reservado a mudança **implementada** em código/Admin/JS visível; só docs → `docs`.                                              |
| CLREC-36  | Commit      | 3.7   | Vários arquivos no mesmo commit só com **uma causa**; temas independentes → commits separados (**COMMITS** § **5.4**).                  |
| CLREC-40  | Issue       | 4.1   | Título e corpo de issue em **pt-BR** — override **ISSUES-05** (**AGENTS-25**).                                                         |
| CLREC-41  | Issue       | 4.2   | Prefixo temático raiz `(classificador)`; módulos `(django)`, `(itemClassificacao)`, …; separador ` - `; sentence case.                  |
| CLREC-42  | Issue       | 4.3   | Coerência issue ↔ commit: `See`/`Closes`/`Refs`; escopo issue alinhado ao escopo do commit quando aplicável.                            |
| CLREC-50  | Convenção   | 5.1   | Ao introduzir/renomear `code_*`, domínio YAML ou tema transversal, **deve** atualizar § **5**; specs funcionais só paths, sem duplicar. |
| CLREC-51  | Convenção   | 5.2   | Normas toolkit shell / manifest multinível (**CONV** § **6**–**8**) **não** se aplicam a este repo Django.                             |
| CLREC-52  | Layout      | 5.3   | Política de paths `docs/assets/referencias/`, `data-raw/`, `data/`, seeds — **ADR-005**; detalhe import em `spec_importar.md`.          |
| CLREC-53  | Layout      | 5.4   | **Carga** (seeds → BD) ≠ **importação** (externo → `data-raw/` → `data/` → BD); Django **não** lê `data/` nos fluxos de carga atuais.  |
| CLREC-54  | Idioma      | 5.5   | Camadas: produto pt-BR, schema PT permitido, implementação EN, persistência como schema, UI pt-BR — tabela § **5.5**.                  |
| CLREC-55  | Domínio     | 5.6   | Cada `schemas/dominios/*.yaml` espelha `code_<inglês>.py`; nova linha na tabela § **5.6** e inventário § **5.10**.                    |
| CLREC-56  | Code        | 5.7   | Arquivos `.py`/testes: nomes EN; docstrings de regra pt-BR; mensagens usuário pt-BR; JS Admin nomes EN, textos por spec domínio.       |
| CLREC-57  | Temporal    | 5.8   | `valid_time` ↔ `data_vigencia_*`; `transaction_time` ↔ `data_registro_*`; módulos EN, rótulos UI podem ser pt.                        |
| CLREC-58  | Code        | 5.9   | Prefixo `code_*`: regras testáveis sem HTTP/templates; consumido por models/admin/handlers; documentado nas specs correspondentes.       |
| CLREC-59  | Code        | 5.10  | Fora de `code_*`: models, migrações, admin, templates, static, `scripts/`, schemas, orquestração `classification_item_*`, handlers.    |
| CLREC-60  | Code        | 5.11  | Par `code_valid_time_fk_validation` + `code_valid_time_fk_resolution` — spec `spec_foreignKeys_vigencia.md` (**FKVIG**).             |
| CLREC-70  | Versão      | 6.1   | Repo **não** mantém `manifest.yaml` nem `CHANGELOG.md` no momento; avaliar `_dev/spec_version.md` quando adotado (**AGENTS-13**).      |
| CLREC-71  | Versão      | 6.2   | Inventário de tags Git **nesta** § **6** — não em `spec_conventions.md` sync (**CONV-07**, **AGENTS-20**).                               |
| CLREC-72  | Versão      | 6.3   | Tags `v` + SemVer (**CONV-06**); tag anotada preferida; **não** executar `git tag`/`push` tag sem pedido explícito (**VERSION-08**).    |
| CLREC-80  | Domínio     | 7.2   | Índice leve de specs locais e ADRs — comportamento detalhado permanece em cada arquivo.                                                  |
| CLREC-81  | Lacuna      | 7.3   | `spec_import_*.md` operacional pendente; contrato maduro `docs/specs/` ainda inexistente (**AGENTS-01**).                                |

**Índice por tema:**

| Tema        | IDs                                      |
| ----------- | ---------------------------------------- |
| Precedência | CLREC-01 … CLREC-03                      |
| Agents      | CLREC-10 … CLREC-19                      |
| Commits     | CLREC-30 … CLREC-36                      |
| Issues      | CLREC-40 … CLREC-42                      |
| Convenções  | CLREC-50 … CLREC-60                      |
| Versão      | CLREC-70 … CLREC-72                      |
| Domínio     | CLREC-80, CLREC-81                       |

---

## 1. Precedência e escopo do repo-spec **(CLREC-01**–**CLREC-03)**

### 1.1 Precedência de processo **(CLREC-01)**

**Precedência** (mesmo tema de processo): contrato maduro em `docs/specs/` ou `specs/` → **este arquivo** (seção correspondente) → cópia sync do manifest → `toolkit/<tool>/specs/`. Ver `_dev/spec_agents.md` § **1.2** (**AGENTS-22**, **AGENTS-25**).

### 1.2 Escopo **(CLREC-02)**

Registre aqui overrides de **como** trabalhar (idioma de commits, escopos, convenções de equipe, …). Regras de **negócio** e comportamento de domínio ficam em `spec_<domínio>.md` locais ou no contrato maduro — não neste arquivo (**AGENTS-26**).

### 1.3 Secções opcionais **(CLREC-03)**

Seções vazias podem ser omitidas; crie uma seção ao documentar a primeira regra daquele tema. Alinhe os títulos às chaves do manifest do catálogo.

---

## 2. Agents — identidade e modelo de trabalho **(CLREC-10**–**CLREC-19)**

### 2.1 Identidade **(CLREC-10)**

Este repositório implementa o **Classificador de Natureza de Receita** (Django Admin, modelos bitemporais, regras de classificação orçamentária).

### 2.2 Modelo de trabalho **(CLREC-11)**

SDD com convenções transversais neste arquivo (§ **5. Convenções**) e implementação assistida por IA, **rastreável** às specs de domínio em `_dev/spec_*.md` locais.

### 2.3 Overrides pós-sync **(CLREC-12)**

Commits e issues em **português do Brasil** — § **3. Commits** e § **4. Issues** prevalecem sobre `_dev/spec_commits.md` e `_dev/spec_issues.md` (**AGENTS-25**). Não reeditar entradas sync do manifest para reintroduzir PT-BR.

### 2.4 Ordem de leitura local **(CLREC-13)**

Após `_dev/spec_agents.md` § **1.2** e **este arquivo** (seção do tema):

1. **`spec_classificador-receita.md` § Convenções** (§ **5**) — nomenclatura, `code_*`, idioma, layout de dados.
2. **Specs temáticas** ligadas à tarefa (ex.: nome no add → `spec_itemClassificacao_criar_nome.md`).
3. **`spec_django.md`** — Admin, models bitemporais, estrutura Django.
4. **ADRs em `docs/adr/`** — bitemporalidade (**ADR-001**), chaves (**ADR-003**), governança de BD (**ADR-004**), layout de dados (**ADR-005**).
5. **`spec_importar.md`** / futuros `spec_import_*.md` — protocolo de importação *(detalhe operacional ainda em elaboração)*.
6. Par entrada sync + `*_new.md` — só para chaves do manifest; aplicar `_dev/spec_agents.md` § **10**; exceções locais vão para **este arquivo**, não para `spec_agents.md` sync.

### 2.5 Lacunas de domínio **(CLREC-14)**

Não inventar regra de domínio sem base em spec ou código; sinalizar lacunas ao desenvolvedor (**AGENTS-09**).

### 2.6 Onde registrar mudanças **(CLREC-15)**

| Tipo de mudança                                      | Onde documentar                                              |
| ---------------------------------------------------- | ------------------------------------------------------------ |
| Comportamento, fluxo Admin, mensagens ao usuário     | Spec temática `_dev/spec_<domínio>.md` (trechos afetados)    |
| Novo módulo `code_*` ou rename                       | Inventário em § **5. Convenções** (neste arquivo)            |
| Decisão arquitetural duradoura                       | ADR em `docs/adr/`                                           |
| Layout `docs/assets/`, `data-raw/`, `data/`          | **ADR-005** + § **5**; import em `spec_importar.md`          |
| Overrides SDD (commits, escopos, idioma de processo) | **Este arquivo**                                             |
| Anotações pessoais                                   | `_dev/toDo.md` (`dev(toDo)` — § **3. Commits**)              |

### 2.7 Implementação: `code_*` vs Admin **(CLREC-16)**

- Regras de negócio **reutilizáveis** e testáveis → `apps/core/code_*.py` (ver § **5**).
- Orquestração Admin, endpoints JSON, templates, static/JS → módulos de fluxo (`classification_item_*`, `admin_handlers.py`, `admin.py`, …); podem **importar** `code_*`, mas **não** usam o prefixo `code_`.
- Não duplicar a política global de `code_*` em cada spec funcional; citar caminhos ou IDs.

### 2.8 Protocolo `*_new.md` **(CLREC-17)**

Sidecars `spec_<chave>_new.md` são snapshot do catálogo para comparação. Após pull que substitui cópias híbridas:

1. Conteúdo **genérico** do catálogo permanece na entrada sync (read-only).
2. Regras **deste projeto** (Django, `code_*`, ADRs, PT-BR) ficam em **`spec_classificador-receita.md`** ou em specs de domínio locais — **não** regravar em `spec_agents.md`, `spec_conventions.md`, etc.
3. Fundir ou elevar trechos genéricos conforme `_dev/spec_agents.md` § **10**; remover `*_new.md` quando o merge estiver completo.

### 2.9 Idioma da documentação **(CLREC-18)**

Specs em `_dev/`, ADRs, páginas em `docs/` e README: **português do Brasil** (não português de Portugal).

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

Termos técnicos em inglês (`foreignKey`, `valid_time`, identificadores de código) permanecem como estão. **Mensagens ao usuário final no Admin** (templates, `ValidationError`, textos de UI): **português do Brasil**, salvo spec em contrário.

### 2.10 Idioma IDE e código **(CLREC-19)**

| Tema                           | Onde no repositório                                                    |
| ------------------------------ | ---------------------------------------------------------------------- |
| Commits e staging              | `spec_classificador-receita.md` § **Commits** (§ **3**) + `_dev/spec_commits.md` |
| Nomenclatura, `code_*`, idioma | **Este arquivo** § **Convenções** (§ **5**)                            |
| Admin, models, migrações       | `spec_django.md`, ADRs                                                 |
| Python (estilo)                | `apps/core/` — PEP 8; seguir o arquivo tocado                          |
| Contratos JSON no Admin        | ex. `spec_itemClassificacao_foreignKeys_lookup.md`                     |
| RFC 2119 em specs              | `deve` / `não deve` / `pode` nas specs normativas                      |

Respostas do assistente na IDE: **inglês** (**AGENTS-07**). Código e comentários em arquivos Python: **inglês** (**AGENTS-08**).

---

## 3. Commits **(CLREC-30**–**CLREC-36)**

Override de **COMMITS-05** e § **3.1** (redação): título e corpo das mensagens em **português do Brasil** — prevalece sobre `_dev/spec_commits.md` § **3** (**AGENTS-25**) **(CLREC-30)**.

| Parte                               | Idioma                                                  |
| ----------------------------------- | ------------------------------------------------------- |
| Título `(<tipo>)(<escopo>): …`      | **Português do Brasil**                                 |
| Corpo (após bloco `See`, se houver) | **Português do Brasil**                                 |
| Linhas `See …`                      | Igual à baseline — copiar de `_dev/_dev.md` (§ **3.2**) **(CLREC-31)** |

- Após `(<escopo>): `: verbo no **infinitivo** (*adicionar*, *corrigir*, *documentar*, *renomear*, *atualizar*, …); corpo em português claro, foco no *porquê* **(CLREC-32)**.
- Estrutura Conventional Commits, `See` (**COMMITS-06**), modo sugestão vs execução, staging § **8**: `_dev/spec_commits.md` — **não** repetir aqui.

Override § **6** (`_dev/toDo.md`): título fixo `dev(toDo): atualizar anotações` **(CLREC-33)**.

### 3.1 Escopos locais **(CLREC-34)**

Consultar **nesta ordem** ao sugerir escopo:

1. Temas já nomeados na tabela abaixo ou em § **5. Convenções**.
2. Spec funcional principal do diff: prefixo `spec_` + **primeiro segmento** até ao **segundo** `_` (ex.: `spec_itemClassificacao_criar_nome.md` → `itemClassificacao`).
3. Spec com um só segmento após `spec_`: usar o segmento inteiro (ex.: `spec_django.md` → `django`, `spec_importar.md` → `importar`).
4. **Rename de spec:** escopo do **nome antigo** do arquivo que motivou a mudança.

| Tema do commit                                           | Escopo sugerido                               | Tipo usual                  |
| -------------------------------------------------------- | --------------------------------------------- | --------------------------- |
| Pacote / rename `code_*`, regras transversais de módulos | `code` ou `code-name` (rename focado em nome) | `refactor` / `docs`         |
| Item de classificação (fluxos Admin)                     | `itemClassificacao`                           | `feat` / `fix` / `docs`     |
| FK e vigência temporal                                   | `foreignKeys`                                 | `feat` / `fix` / `docs`     |
| Validação de códigos / hierarquia                        | `validar`                                     | `feat` / `fix` / `test`     |
| Estrutura Django, Admin, models                          | `django`                                      | `feat` / `fix` / `refactor` |
| Filtros recolhidos do sidebar do Admin                   | `changelist-filters`                          | `feat` / `fix`              |
| Convenções transversais (este arquivo)                   | `convencoes`                                  | `docs(convencoes)`          |
| SDD, sync catálogo, `spec_agents`                        | `sdd`                                         | `docs(sdd)`                 |
| Commits, staging, agents (norma de processo)             | `commits`                                     | `docs(commits)`             |

| Arquivo da spec                                    | Escopo              |
| -------------------------------------------------- | ------------------- |
| `spec_itemClassificacao_criar_filho.md`            | `itemClassificacao` |
| `spec_itemClassificacao_criar_nome.md`             | `itemClassificacao` |
| `spec_itemClassificacao_editar_codigo.md`          | `itemClassificacao` |
| `spec_itemClassificacao_regras_hierarquia.md`      | `itemClassificacao` |
| `spec_itemClassificacao_formulario.md`             | `itemClassificacao` |
| `spec_itemClassificacao_foreignKeys_lookup.md`     | `itemClassificacao` |
| `spec_itemClassificacao_mascara_apresentacao.md`   | `itemClassificacao` |
| `spec_itemClassificacao_criar_codigo_existente.md` | `itemClassificacao` |
| `spec_itemClassificacao_validar_hierarquia.md`     | `itemClassificacao` |
| `spec_foreignKeys_vigencia.md`                     | `foreignKeys`       |
| `spec_lista_abreviacoes.md`                        | `lista`             |
| `spec_django.md`                                   | `django`            |
| `spec_validar_codigos.md`                          | `validar`           |
| `spec_validar_qualidade.md`                        | `validar`           |
| `spec_importar.md`                                 | `importar`          |

### 3.2 Tipo vs arquivos **(CLREC-35)**

| Diff principal                                    | Tipo usual                                      |
| ------------------------------------------------- | ----------------------------------------------- |
| Só `_dev/spec_*.md`, `docs/`, README (sem código) | **`docs`**                                      |
| Código + specs alinhadas ao mesmo comportamento   | `feat` / `fix` / `refactor` + escopo do domínio |
| Só `apps/core/tests_*.py`                         | **`test`**                                      |
| Só `_dev/toDo.md`                                 | **`dev`**                                       |

`feat` reserva-se a mudança **implementada** em código, Admin ou JS/CSS visível.

### 3.3 Exemplos **(CLREC-36)**

```
refactor(code): renomear módulos para pacote code_*

See #18
See https://github.com/splor-mg/classificador-receita/tree/migracao

Consolidar regras reutilizáveis em apps/core/code_*.py; atualizar inventário em spec_classificador-receita.md.
```

```
feat(itemClassificacao): bloquear submit quando código já existe na add

See #18
See https://github.com/splor-mg/classificador-receita/tree/migracao

Validação no cliente e no servidor; mensagem alinhada ao endpoint JSON.
```

```
docs(convencoes): documentar inventário code_* no repo-spec

See #18
See https://github.com/splor-mg/classificador-receita/tree/migracao

Migrar convenções locais para spec_classificador-receita.md após sync do catálogo.
```

Vários arquivos no **mesmo commit** quando houver **uma causa** (ex.: rename `code_*` + atualização de imports + inventário neste arquivo). Temas independentes → commits separados (§ **5.4** em `spec_commits.md`).

---

## 4. Issues **(CLREC-40**–**CLREC-42)**

Override de **ISSUES-05**: título e corpo do issue em **português do Brasil** — prevalece sobre `_dev/spec_issues.md` § **3** (**AGENTS-25**) **(CLREC-40)**.

- Padrão `.github/issues/`, sentence case, ligação a commits (**ISSUES-01**–**04**, **ISSUES-08**): `_dev/spec_issues.md` — **não** repetir aqui.

### 4.1 Prefixo temático **(CLREC-41)**

Quando o repositório usar escopo entre parênteses:

```text
(classificador) - Refatorar validação de código em componentes modulares
```

- Escopo raiz do produto: **`(classificador)`** — tema transversal do repositório.
- Escopos de módulo ou fluxo (minúsculas): `(django)`, `(itemClassificacao)`, `(foreignKeys)`, `(validar)`, `(specs)`, …
- Separador: ` - ` (espaço, hífen, espaço).
- Descrição: **sentence case** — ver `spec_issues.md` § **2.1**.

### 4.2 Coerência issue ↔ commit **(CLREC-42)**

Ao implementar trabalho rastreado por issue:

- Referência no commit conforme `spec_commits.md` (`See …`, `Closes #NN`, `Refs #NN`).
- Manter coerência entre escopo do issue (`(django)`) e escopo do commit (`django`), quando aplicável.

---

## 5. Convenções **(CLREC-50**–**CLREC-60)**

Convenções **organizadoras e semânticas** do Classificador de Natureza de Receita. Comportamento funcional permanece nas specs temáticas (`spec_itemClassificacao_*.md`, `spec_foreignKeys_vigencia.md`, …).

**Manutenção (CLREC-50):** ao introduzir ou renomear módulo `code_*`, domínio YAML ou tema transversal, atualizar **esta seção**. Nas specs funcionais, alterar apenas **caminhos de arquivo** quando necessário; não duplicar a política de `code_*` em cada documento.

**Nota (CLREC-51):** normas de **toolkit shell**, entry point `toolkit/<tool>/<tool>.sh`, manifest multinível e migrations do catálogo (`spec_conventions.md` § **6**–**8**) **não se aplicam** a este repositório Django.

**Referências relacionadas:**

- **ADR-001** — `docs/adr/adr-001_bitemporalidade.md`
- **ADR-003** — `docs/adr/adr-003_chave-semantica.md`
- **ADR-004** — `docs/adr/adr-004_governanca-banco.md`
- **ADR-005** — `docs/adr/adr-005_layout-dados.md`
- `spec_django.md` — estrutura Django, mapeamento de campos temporais

### 5.1 Layout de artefatos de dados **(CLREC-52**, **CLREC-53**)

Política completa: **`docs/adr/adr-005_layout-dados.md`**. Importação operacional: `spec_importar.md` *(protocolo `spec_import_*.md` a detalhar)*.

| Local                      | Missão resumida                                                            |
| -------------------------- | -------------------------------------------------------------------------- |
| `docs/assets/referencias/` | Fontes externas de referência; entrada típica do import                    |
| `data-raw/`                | Primeiro tratamento do import: normalização tabular do arquivo bruto       |
| `data/`                    | Lançamentos apurados a partir de `data-raw/`; gravação no BD pelo import   |
| `docs/assets/seed_*.csv`   | Recursos do `datapackage.yaml`; carga inicial via `carregar_classificador` |
| PostgreSQL                 | Fonte operacional em runtime (Admin, governança ADR-004)                   |

**Distinção obrigatória:** **carga** (seeds → BD) ≠ **importação** (fonte externa → `data-raw/` → `data/` → BD). O Django **não** lê `data/` nem `data-raw/` nos fluxos de carga existentes.

### 5.2 Camadas de idioma **(CLREC-54)**

| Camada                    | Onde                                               | Idioma                                                    | Notas                               |
| ------------------------- | -------------------------------------------------- | --------------------------------------------------------- | ----------------------------------- |
| **Semântica de produto**  | `_dev/spec_*.md`, ADRs, `docs/`                    | **Português do Brasil**                                   | Tabela pt-BR vs pt-PT: § **2.9**    |
| **Contrato de dados**     | `schemas/`, `schemas/dominios/*.yaml`              | Identificador de domínio pode ser PT (`orgaos_entidades`) | `custom.domainRef`                  |
| **Implementação**         | `apps/core/code_*.py`, funções, testes             | **Inglês**                                                | PEP 8                               |
| **Persistência / modelo** | campos (`orgao_responsavel`, …)                    | **Como no schema**                                        | Não renomear por i18n sem migração  |
| **Mensagens Admin / UI**  | templates, `ValidationError`, `code_name_messages` | **Português do Brasil**                                   | Ver specs de domínio                |

Códigos de valor no catálogo (`SEF-MG`, `STN-BRA`) são dados/contrato, não nomenclatura de módulo.

### 5.3 Catálogos `schemas/dominios/` ↔ módulos `code_*` **(CLREC-55)**

- Cada YAML define `identifier` e `values` (códigos permitidos).
- Nome do arquivo YAML pode permanecer em português: `orgaos_entidades.yaml`.
- Implementação Django: `apps/core/code_<nome_em_inglês>.py`. Constantes Python podem usar prefixo do domínio (ex.: `ORGAOS_ENTIDADES_CHOICES`).

| YAML (`schemas/dominios/`) | Módulo Python (`apps/core/`)     | Campos que consomem                                             |
| -------------------------- | -------------------------------- | --------------------------------------------------------------- |
| `orgaos_entidades.yaml`    | `code_organizations_entities.py` | `orgao_responsavel` em `SerieClassificacao`, `BaseLegalTecnica` |

Ao acrescentar domínio: criar YAML, módulo `code_*` espelho, linha nesta tabela e entrada no inventário § **5.10**.

### 5.4 Código Python **(CLREC-56)**

| Artefato                                        | Idioma / convenção                                                    |
| ----------------------------------------------- | --------------------------------------------------------------------- |
| Nome de arquivo (`.py`, testes espelhados)      | **Inglês** (`snake_case`), alinhado ao inventário `code_*`            |
| Funções, classes, métodos, constantes           | **Inglês**, salvo constantes ligadas a identificador de domínio em PT |
| Comentários e docstrings de regra de negócio    | **Português do Brasil** em primeira instância                         |
| Mensagens ao usuário (Admin, `ValidationError`) | **Português do Brasil**                                               |

Termos técnicos em comentários (`ForeignKey`, `valid_time`, `queryset`, …) podem permanecer em inglês.

**JavaScript do Admin** (`static/core/js/`): nomes de funções e arquivos em **inglês** (`code_name.js`, `initCodeName`); textos de UI seguem specs de domínio.

### 5.5 Glossário temporal **(CLREC-57)**

| Termo (inglês)       | Campos no modelo                            | Uso no domínio                                                |
| -------------------- | ------------------------------------------- | ------------------------------------------------------------- |
| **valid_time**       | `data_vigencia_inicio`, `data_vigencia_fim` | Período em que a informação vale no orçamento / classificador |
| **transaction_time** | `data_registro_inicio`, `data_registro_fim` | Período em que o sistema considerou o registro verdadeiro     |

Nomes de módulos em inglês (`valid_time_fk`, …) alinham-se ao ADR-001 e a `spec_django.md`. Rótulos de interface podem permanecer em português («vigência», «registro»).

### 5.6 Prefixo `code_` em `apps/core/` **(CLREC-58**, **CLREC-59**)

**Definição:** arquivos Python cujo nome começa por **`code_`** formam o pacote de **regras e helpers de negócio reutilizáveis**:

- Lógica testável sem acoplar a HTTP, templates ou rotas do Admin
- Consumida por `models`, `forms`, `admin`, handlers e módulos `classification_item_*`
- Documentada nas specs `_dev/spec_*` correspondentes

O prefixo inclui nome, hierarquia, máscara, FK temporal, normalização de entrada no Admin e catálogos espelhados de `schemas/dominios/`.

**Fora de `code_`:** `models.py`, migrações, `admin.py`, templates, static/JS, `scripts/`, schemas Frictionless, módulos de orquestração por fluxo (`classification_item_code_lookup.py`, `admin_handlers.py`, …).

#### Subfamílias

| Subfamília             | Exemplos                      | Tema                                                     |
| ---------------------- | ----------------------------- | -------------------------------------------------------- |
| Nome / radical         | `code_name_*`                 | Protocolo de `receita_nome`, abreviação, validação G0–G1 |
| Máscara e apresentação | `code_mask`                   | Máscara e formatação de código por vigência              |
| Hierarquia do item     | `code_parent_item_validation` | Mãe, nível, saltos, zeros canônicos, endpoints JSON    |
| FK + valid_time        | `code_valid_time_fk_*`        | Contenção de vigência em FK; reaponte da linha apontada  |
| Entrada / placeholders | `code_null_normalization`     | `NULL` e `-` → ausência canônica em campos texto         |
| Catálogo de domínio    | `code_organizations_entities` | Choices de `orgaos_entidades` → `orgao_responsavel`      |

#### Par valid_time + FK **(CLREC-60)**

Dois módulos, spec `spec_foreignKeys_vigencia.md`:

| Módulo                             | Responsabilidade                                                               |
| ---------------------------------- | ------------------------------------------------------------------------------ |
| `code_valid_time_fk_validation.py` | Valida que a vigência do filho está contida na do alvo da FK                   |
| `code_valid_time_fk_resolution.py` | Reaponta a FK para linha compatível ao gravar (`apply_temporal_fk_resolution`) |

Segmento **`valid_time_fk`** no nome do arquivo, alinhado ao eixo **valid_time** (ADR-001).

### 5.7 Inventário atual de módulos `code_*`

| Módulo                             | Responsabilidade resumida                                      |
| ---------------------------------- | -------------------------------------------------------------- |
| `code_mask.py`                     | Máscara de `receita_cod` por classificação/vigência            |
| `code_name_abbrev.py`              | Radical abreviado, modo base, compactação A6                   |
| `code_name_connectives.py`         | Conectivos e pontuação (SSOT para abreviação e léxico)         |
| `code_name_messages.py`            | Textos do fluxo de nome no Admin (`code_name_messages_dict`)   |
| `code_name_validation.py`          | Guardrails G0/G1 e predicados de `receita_nome`                |
| `code_null_normalization.py`       | Placeholders `NULL` / `-` → `None` em CharField/TextField      |
| `code_parent_item_validation.py`   | Regras de `parent_item_id`, hierarquia, saltos, intermediários |
| `code_valid_time_fk_resolution.py` | Reaponte automático de FK por vigência                         |
| `code_valid_time_fk_validation.py` | Contenção temporal filho ⊆ alvo(s) da FK                       |
| `code_organizations_entities.py`   | Catálogo `orgaos_entidades` (choices / optgroup no Admin)      |

**Testes espelhados:** `tests_code_name.py`, `tests_code_parent_item_validation.py`, `tests_classification_item_*.py` (fluxos `classification_item_*`).

**Front-end Admin:** `static/core/js/code_name.js` — `initCodeName`, `validateCodeNameOnSubmit`, …; ver `spec_itemClassificacao_criar_nome.md`.

### 5.8 Prefixos de ID normativos (domínio local)

| Arquivo                                            | Prefixo    | Escopo                                                   |
| -------------------------------------------------- | ---------- | -------------------------------------------------------- |
| `spec_classificador-receita.md`                    | `CLREC`    | Processo SDD local, commits, issues, hub de prefixos     |
| `spec_validar_codigos.md`                          | `VALCOD`   | Script `validate_code.py` e validação de `receita_cod`   |
| `spec_validar_qualidade.md`                        | `VALQUAL`  | Script `validate_quality.py` e quality dimensions        |
| `spec_itemClassificacao_regras_hierarquia.md`      | `ITEMRH`   | Regras de `parent_item_id` e hierarquia semântica        |
| `spec_foreignKeys_vigencia.md`                     | `FKVIG`    | Contenção temporal de FK e união contígua bitemporal     |
| `spec_importar.md`                                 | `IMPORT`   | Protocolo de importação (MINUTA; pipeline ADR-005)       |
| `spec_itemClassificacao_formulario.md`             | `ITEMFORM` | Formulário admin: largura `receita_cod` e limpar add     |
| `spec_itemClassificacao_foreignKeys_lookup.md`     | `ITEMLKP`  | Endpoints JSON lookup-parent / lookup-hierarchy no Admin |
| `spec_itemClassificacao_editar_codigo.md`          | `ITEMEC`   | Edição de `receita_cod` na change (blur, save, revert)   |
| `spec_itemClassificacao_mascara_apresentacao.md`   | `ITEMMASK` | Máscara visual admin (tier 1/2) e protocolo B1           |
| `spec_itemClassificacao_criar_codigo_existente.md` | `ITEMCEX`  | Alerta/erro CE e próximo código na add                   |
| `spec_itemClassificacao_validar_hierarquia.md`     | `ITEMVH`   | Salto de nível, zeros intermediários e submit na add     |
| `spec_django.md`                                   | `DJANGO`   | Layout Django, Admin changelist e pipeline bitemporal    |
| `spec_itemClassificacao_criar_nome.md`             | `ITEMNOM`  | Criação add: `receita_nome`, modos de radical, P-mãe     |
| `spec_itemClassificacao_criar_filho.md`            | `ITEMCF`   | Sugestão de código filho na add e atalho change → add    |
| `spec_itemClassificacao_navegacao.md`              | `ITEMNAV`  | Navegação estrutural na change (`<< < > >>`)             |
| `spec_lista_abreviacoes.md`                        | `LISTABR`  | Protocolo `lista_abreviacoes` / inferência `AliasLexico` |

### 5.9 Renomeações históricas (`classification_*` → `code_*`)

| Antes                            | Depois                                                                    |
| -------------------------------- | ------------------------------------------------------------------------- |
| `classification_naming_*`        | `code_name_*`                                                             |
| `parent_item_validation.py`      | `code_parent_item_validation.py`                                          |
| `temporal_fk_resolution.py`      | `code_valid_time_fk_resolution.py` (via `code_temporal_fk_resolution.py`) |
| `code_temporal_fk_resolution.py` | `code_valid_time_fk_resolution.py`                                        |
| `vigencia_fk_validation.py`      | `code_valid_time_fk_validation.py`                                        |
| `null_normalization.py`          | `code_null_normalization.py`                                              |
| `domain_choices.py`              | `code_organizations_entities.py`                                          |

APIs públicas (`validate_vigencia_contained_in_fk_targets`, códigos `ValidationError`) podem manter vocabulário anterior após rename de arquivo.

---

## 6. Versionamento **(CLREC-70**–**CLREC-72)**

Este repositório **não** mantém `manifest.yaml` nem `CHANGELOG.md` no momento. Avaliar impacto conforme `_dev/spec_version.md` quando normas ou releases forem adotadas (**AGENTS-13**) **(CLREC-70)**.

### 6.1 Inventário de tags Git **(CLREC-71**, **CLREC-72**)

Manter **nesta seção** (não em `_dev/spec_conventions.md` sync). Atualizar ao criar tag `vX.Y.Z` (**AGENTS-20**, **VERSION-07**).

| Tag                                  | Commit (curto) | Data | Notas |
| ------------------------------------ | -------------- | ---- | ----- |
| *(nenhuma tag `v*` publicada ainda)* | —              | —    | —     |

Convenção de nome: prefixo `v` + SemVer (**CONV-06**). Tag anotada preferida: `git tag -a vX.Y.Z -m "Release X.Y.Z"`. Não executar `git tag` / `git push` de tag sem pedido explícito (**VERSION-08**, **AGENTS-11**).

---

## 7. Domínio **(CLREC-80**, **CLREC-81**)

Índice leve das specs **locais** (fora do manifest do catálogo) e ADRs. Comportamento detalhado permanece em cada arquivo **(CLREC-80)**.

### 7.1 ADRs (`docs/adr/`)

| ADR                                                                                                             | Tema                                               |
| --------------------------------------------------------------------------------------------------------------- | -------------------------------------------------- |
| [ADR-001](https://github.com/splor-mg/classificador-receita/blob/migracao/docs/adr/adr-001_bitemporalidade.md)  | Bitemporalidade (`valid_time`, `transaction_time`) |
| [ADR-002](https://github.com/splor-mg/classificador-receita/blob/migracao/docs/adr/adr-002_gsim.md)             | GSIM                                               |
| [ADR-003](https://github.com/splor-mg/classificador-receita/blob/migracao/docs/adr/adr-003_chave-semantica.md)  | Chave semântica                                    |
| [ADR-004](https://github.com/splor-mg/classificador-receita/blob/migracao/docs/adr/adr-004_governanca-banco.md) | Governança do banco                                |
| [ADR-005](https://github.com/splor-mg/classificador-receita/blob/migracao/docs/adr/adr-005_layout-dados.md)     | Layout `docs/assets/`, `data-raw/`, `data/`        |

### 7.2 Specs de domínio (`_dev/`)

| Spec                                               | Foco                                              |
| -------------------------------------------------- | ------------------------------------------------- |
| `spec_django.md`                                   | Admin, models bitemporais, estrutura do projeto   |
| `spec_itemClassificacao_criar_codigo_existente.md` | Bloqueio de código duplicado na add               |
| `spec_itemClassificacao_criar_filho.md`            | Criação de filho na hierarquia                    |
| `spec_itemClassificacao_criar_nome.md`             | Protocolo de `receita_nome`, abreviação, JS Admin |
| `spec_itemClassificacao_editar_codigo.md`          | Edição de código                                  |
| `spec_itemClassificacao_formulario.md`             | Formulário de item                                |
| `spec_itemClassificacao_foreignKeys_lookup.md`     | Lookup JSON de FK no Admin                        |
| `spec_itemClassificacao_mascara_apresentacao.md`   | Máscara e apresentação de código                  |
| `spec_itemClassificacao_navegacao.md`              | Navegação na árvore                               |
| `spec_itemClassificacao_regras_hierarquia.md`      | Regras de hierarquia                              |
| `spec_itemClassificacao_validar_hierarquia.md`     | Validação de hierarquia                           |
| `spec_foreignKeys_vigencia.md`                     | FK e contenção de vigência                        |
| `spec_lista_abreviacoes.md`                        | Lista de abreviações                              |
| `spec_validar_codigos.md`                          | Validação de códigos                              |
| `spec_validar_qualidade.md`                        | Validação de qualidade                            |
| `spec_importar.md`                                 | Importação (rascunho)                             |

### 7.3 Lacunas conhecidas **(CLREC-81)**

- **`spec_import_*.md`** — protocolo operacional de importação (CLI, naming, gravação) a detalhar; índice transversal em § **5. Convenções** (layout ADR-005) e rascunho em `spec_importar.md`.
- Contrato maduro em `docs/specs/` ou `specs/` — **ainda não existe**; `_dev/spec_*.md` locais são a fonte de domínio até promoção (**AGENTS-01**).
