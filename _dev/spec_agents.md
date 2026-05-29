# Orientações para agentes de IA (engenharia de contexto)

Este documento define **como agentes de IA** (Cursor, assistentes em IDE, automações)
devem trabalhar neste repositório ao implementar, refatorar ou documentar o
Classificador de Natureza de Receita.

**Não substitui** as specs de domínio nem as convenções de código — complementa-as
com protocolo operacional. Leia sempre em conjunto com:

- `_dev/spec_convencoes.md` — nomenclatura, idioma, prefixo `code_`, inventário
- `_dev/spec_*.md` — comportamento e regras por tema (domínio)

---

## Modelo de trabalho: SDD (Spec-Driven Development)

O projeto adota **desenvolvimento orientado a especificações de domínio**:

- Especificações em linguagem natural em `_dev/spec_*.md` descrevem o que deve
  ser verdadeiro no domínio e nos fluxos (Admin, validações, mensagens).
- Convenções transversais em `_dev/spec_convencoes.md` garantem consistência
  estrutural (módulos `code_*`, vocabulário temporal, nomes de arquivos).
- A implementação em Python, templates e JavaScript é produzida ou revisada com
  **assistência de IA**, desde que permaneça **rastreável** às specs.

Em resumo: **SDD com convenções transversais e implementação assistida por IA**.

---

## Ordem de leitura antes de alterar código

1. **`_dev/spec_convencoes.md`** — obrigatório para nomenclatura e organização.
2. **Specs temáticas** ligadas à tarefa (ex.: nome no add → `spec_itemClassificacao_criar_nome.md`).
3. **`_dev/spec_django.md`** — quando a tarefa envolver Admin, models bitemporais ou estrutura Django.
4. **ADRs em `docs/adr/`** — quando a decisão arquitetural (bitemporalidade, chaves) for relevante.

Não inventar regra de domínio que não esteja nas specs ou no código existente sem
sinalizar ao operador.

---

## Nomenclatura e novos arquivos

Ao **sugerir ou criar** arquivos Python, funções, classes, métodos, módulos JS
do núcleo do classificador ou testes espelhados:

- Consultar **`_dev/spec_convencoes.md`** (camadas de idioma, prefixo `code_`,
  inventário, tabela `schemas/dominios/` → módulo `code_*`).
- Novo catálogo em `schemas/dominios/*.yaml`: módulo espelho em **inglês**
  (`code_organizations_entities.py` para `orgaos_entidades.yaml`); atualizar a tabela na spec de convenções.
- Em dúvida entre traduzir o slug do domínio ou espelhá-lo no nome do arquivo `.py`,
  **perguntar ao operador** ou seguir a tabela domínio → módulo já registrada.
- Respeitar padrões já usados no pacote (`code_*`, `item_classificacao_*`, `tests_code_*`).
- Após introduzir ou renomear módulo `code_*`, **atualizar o inventário** em
  `spec_convencoes.md`.

Mensagens exibidas ao usuário final no Admin permanecem em **português do Brasil**,
conforme cada spec funcional — salvo pedido explícito em contrário.

---

## Protocolo de contradição (obrigatório)

Se uma instrução do operador **contradizer** texto normativo em `_dev/spec_*.md`,
`_dev/spec_convencoes.md` ou ADR citado pelo projeto:

1. **Não implementar silenciosamente** a parte contraditória.
2. **Alertar o operador** de forma explícita, citando:
   - o que foi pedido;
   - o que a spec/ convenção diz (nome do arquivo e trecho ou seção, se possível);
   - o conflito em uma frase clara.
3. Perguntar se deve **priorizar o pedido** (e então sugerir atualizar a spec) ou
   **seguir a spec** (e ajustar o pedido).

O mesmo protocolo aplica-se quando **código e spec divergem**: reportar
«spec diz X, código faz Y» e pedir alinhamento antes de refactors amplos.

---

## Protocolo de implementação

- Regras de negócio reutilizáveis → módulos `apps/core/code_*.py` (ver convenções).
- Orquestração Admin / endpoints / templates → módulos e arquivos já existentes
  do fluxo (`admin.py`, `item_classificacao_*`, `change_form.html`, etc.).
- Alterar specs funcionais apenas nos trechos afetados; **não duplicar** em cada
  spec a política global do prefixo `code_` (manter em `spec_convencoes.md`).
- **Não criar commit** nem push salvo pedido explícito do operador.
- Preferir diff mínimo e alinhado ao estilo do arquivo tocado.

---

## Saída esperada em tarefas não triviais

Quando útil, resumir brevemente:

- quais specs foram consideradas;
- suposições feitas;
- pontos sem spec (incerteza);
- contradições encontradas (se houver).

---

## Manutenção deste documento

Ao mudar o processo de trabalho com IA (novas pastas obrigatórias, nova spec hub,
ferramenta de agente), atualizar **`spec_agents.md`** e, se necessário, uma linha
de referência em `spec_convencoes.md`.
