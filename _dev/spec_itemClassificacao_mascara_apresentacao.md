# Especificação: Apresentação de `receita_cod` com máscara na changelist de `ItemClassificacao`

Este documento define a política de aplicação de **máscara visual** sobre o
campo `receita_cod` na **changelist** do Django Admin de `ItemClassificacao`.
Trata exclusivamente da camada de apresentação dessa coluna; não altera regras
de validação, de criação, de edição, de lookup ou de sugestão de código filho.

Tópicos:

- [Contexto e motivação](#contexto-e-motivação)
- [Decisão](#decisão)
- [Resolução em dois níveis](#resolução-em-dois-níveis)
- [Justificativa de não usar união contígua](#justificativa-de-não-usar-união-contígua)
- [Implementação](#implementação)
- [Casos de teste recomendados](#casos-de-teste-recomendados)
- [Referências cruzadas](#referências-cruzadas)

---

## Contexto e motivação

O `receita_cod` é armazenado em `ItemClassificacao` como **string apenas
numérica** de 8 a 13 dígitos (`max_length=13`, regex `^[0-9]{8,13}$`). A
"máscara" com pontos (`1.1.0.0.00.0.0.00.000`) é uma representação visual
derivada dinamicamente da distribuição de dígitos por nível hierárquico
(`NivelHierarquico.numero_digitos`).

Como `NivelHierarquico` é bitemporal, suas "estruturas de dígitos" podem variar
no tempo: por exemplo, o classificador da União teve 8 dígitos até 2017 e
passou a 13 dígitos em 2018. Cada linha de `NivelHierarquico` tem sua própria
`(data_vigencia_inicio, data_vigencia_fim)`, e a máscara aplicada a um item
depende de **qual versão do nível** vigora durante a vigência daquele item.

A regra estrita aplicada hoje em formulários, lookups e validações
(`format_receita_cod_by_vigencia` em `apps/core/admin_formatters.py`) exige,
**por `nivel_ref`, uma única linha ativa de `NivelHierarquico` cuja vigência
contenha integralmente** a janela do item. Essa é a política correta para
contextos em que precisa-se de **uma resposta inequívoca** sobre qual máscara
aplicar — o motivo está em ["Justificativa de não usar união
contígua"](#justificativa-de-não-usar-união-contígua).

Porém, **na changelist** essa regra estrita gera uma inconsistência visual
indesejável: assim que qualquer `NivelHierarquico` sofre split bitemporal (ex.:
faixa `[2018-01-01, 9999-12-31]` partida em `[2018-01-01, 2026-01-31]` e
`[2026-02-01, 9999-12-31]`), os itens cuja vigência cruzar o ponto de junção
deixam de ter uma única linha do nível cobrindo-os integralmente e passam a
exibir o **código bruto** (sem pontos). Já os itens com vigência inteiramente
contida em uma das novas faixas seguem **com máscara**.

O resultado é uma changelist com algumas linhas formatadas e outras não, sem
que o usuário tenha como inferir o motivo. Esse é o problema desta spec.

## Decisão

A coluna `receita_cod_formatado` na changelist de `ItemClassificacao`
**sempre tenta apresentar `receita_cod` com máscara**. Para isso:

- **D1.** Mantém-se a **regra estrita primária** existente
  (`format_receita_cod_by_vigencia`) como tier 1.
- **D2.** Adiciona-se uma **resolução secundária** específica de changelist
  (`_resolve_secondary_digit_mask_for_changelist`), acionada **apenas quando o
  tier 1 falha**. Detalhada na próxima seção.
- **D3.** Quando ambos os tiers falham, devolve-se o `receita_cod` bruto. Não
  há terceiro fallback nem placeholder explícito (UX discreta).
- **D4.** A resolução secundária é **isolada** ao helper
  `format_receita_cod_for_changelist`. **Não é compartilhada** com formulários,
  lookups, validações, sugestões de código filho, exports ou qualquer outro
  consumidor de máscara — esses seguem usando exclusivamente a regra estrita.

## Resolução em dois níveis

### Tier 1 — Estrito (inalterado)

Igual à regra historicamente aplicada por `format_receita_cod_by_vigencia`:

- Para cada `nivel_ref` distinto presente no sistema:
  - `data_registro_fim = TRANSACTION_TIME_SENTINEL`;
  - `data_vigencia_inicio ≤ registro.data_vigencia_inicio`;
  - `data_vigencia_fim ≥ registro.data_vigencia_fim`.
- Coletam-se `numero_digitos` na ordem de `nivel_ref`.
- A máscara é considerada **compatível** se: não vazia, sem zeros/falsy, e
  `sum(digit_mask) == len(receita_cod)`.

### Tier 2 — Secundário (exclusivo da changelist)

Acionado quando o tier 1 não produz máscara compatível. Para cada `nivel_ref`
distinto presente no sistema:

- **Etapa S1 — Filtro de elegibilidade.** Considerar apenas linhas com:
  - `data_registro_fim = TRANSACTION_TIME_SENTINEL`;
  - `data_vigencia_inicio ≤ registro.data_vigencia_fim`;
  - `data_vigencia_fim ≥ registro.data_vigencia_fim`.

  A âncora aqui é o **`data_vigencia_fim` do registro** (e não o
  `data_vigencia_inicio`), porque a versão semanticamente "canônica" na
  changelist é a que vale do `data_vigencia_fim` em diante — privilegiar o
  passado (`data_vigencia_inicio`) numa listagem orientada ao presente/futuro
  geraria escolha contraintuitiva. Esse ponto é normativo desta spec; vê-lo
  como "data-âncora da apresentação".

- **Etapa S2 — Desempate principal.** Entre as candidatas da Etapa S1, escolher
  a com **maior `data_vigencia_fim`** própria.

- **Etapa S3 — Desempate residual.** Se ainda houver empate, escolher a com
  **`data_registro_inicio` mais recente**.

A máscara resultante é então submetida ao mesmo teste de compatibilidade do
tier 1 (não vazia, sem zeros, soma igual a `len(receita_cod)`). Se passar,
aplica-se; senão, devolve-se bruto.

### Comportamento quando a Etapa S1 não retorna nenhuma candidata para algum `nivel_ref`

Por decisão explícita (alinhamento da spec), **não há relaxamento adicional**.
O `nivel_ref` em questão simplesmente não contribui com `numero_digitos` para
a máscara secundária, o que tipicamente fará `sum(digit_mask) ≠
len(receita_cod)` e levará ao fallback bruto. Esse comportamento é intencional
— manter a regra conservadora e tornar o problema **visível** (linha bruta na
listagem) é preferível a inventar uma máscara potencialmente enganosa.

### Linhas encerradas em transação

Linhas de `NivelHierarquico` com `data_registro_fim ≠ TRANSACTION_TIME_SENTINEL`
(versões historicamente encerradas) **nunca** entram em nenhuma etapa do tier
1 nem do tier 2. Só o estado "transação aberta" é considerado.

## Justificativa de não usar união contígua

A `_dev/spec_foreignKeys_vigencia.md` formaliza outra política temporal — a
**união contígua** de vigências ativas com mesmo `nivel_ref` — usada para
**validar FKs** (etapa 2 daquela spec). Por que essa política não é adotada
aqui?

Porque os dois problemas têm naturezas distintas:

- **Validação de FK.** Pergunta: "as várias versões da FK, juntas, cobrem a
  janela do filho?" — uma resposta booleana, simétrica entre as versões. A
  união contígua resolve isso naturalmente.
- **Resolução de máscara.** Pergunta: "qual `numero_digitos` aplicar para esse
  `nivel_ref`?" — uma resposta singular. Se duas versões ativas contíguas têm
  `numero_digitos` diferentes (cenário possível em transições estruturais), a
  união contígua não tem critério interno para escolher entre elas.

Assim, a regra estrita (uma única linha contém a janela) é o que garante
**inequivocidade**. O tier 2 desta spec não usa união contígua: ele preserva o
princípio de "uma única linha por `nivel_ref`", apenas relaxando o critério de
contenção (de "janela inteira" para "âncora em `data_vigencia_fim`"), com
desempate explícito e determinístico (Etapas S2 e S3).

Em resumo:

- **`spec_foreignKeys_vigencia.md`** → cobertura coletiva → união contígua.
- **Esta spec** → identificação singular → linha única, com âncora pontual no
  tier 2.

São políticas **complementares**, não conflitantes. A escolha entre elas em
cada local do código deve ser explícita.

## Implementação

Arquivos envolvidos:

- `apps/core/admin_formatters.py` — onde vivem `format_receita_cod_by_vigencia`
  (tier 1 puro, para uso geral), `_resolve_secondary_digit_mask_for_changelist`
  (tier 2) e `format_receita_cod_for_changelist` (composição dos dois tiers).
- `apps/core/admin.py`, método `ItemClassificacaoAdmin.receita_cod_formatado` —
  único consumidor de `format_receita_cod_for_changelist` no momento.

Funções utilitárias:

- `_apply_digit_mask(codigo, digit_mask)` — aplica uma máscara em código e
  devolve `None` quando incompatível (não-vazia, sem zeros, soma = `len`).
  Reaproveitada por ambos os tiers.

Caching:

- O atributo `_nivel_digit_cache` (dict mutável) de `ItemClassificacaoAdmin`
  serve a ambos os tiers. As chaves do tier 1 são tuplas
  `(data_vigencia_inicio, data_vigencia_fim)`; as do tier 2 são
  `("secondary-changelist", data_vigencia_fim)`. Não há colisão.

Política de exposição:

- O nome `format_receita_cod_for_changelist` é deliberadamente sufixado com
  `_for_changelist` para sinalizar que **não deve ser chamado fora da
  changelist**. Tentativas futuras de reuso em outros contextos precisam
  primeiro revisitar esta spec.

## Casos de teste recomendados

- **T-1.** Tier 1 sucede: para um registro cuja vigência está integralmente
  contida em linhas únicas de todos os `nivel_ref` ativos, a saída é
  formatada via tier 1 (igual ao histórico anterior). _Regressão._
- **T-2.** Tier 1 falha, tier 2 sucede com candidata única: cenário do print
  histórico de 2026-05-19 — split bitemporal de `NIVEL-3` em
  `[2018-01-01, 2026-01-31]` e `[2026-02-01, 9999-12-31]`. Item com vigência
  `[2026-01-01, 9999-12-31]` deve passar a ser formatado.
- **T-3.** Tier 1 falha, tier 2 sucede com desempate por `data_vigencia_fim`:
  duas linhas elegíveis para o mesmo `nivel_ref`, com `data_vigencia_fim`
  diferentes; deve vencer a maior.
- **T-4.** Tier 1 falha, tier 2 sucede com desempate por `data_registro_inicio`:
  duas linhas elegíveis com `data_vigencia_fim` iguais; deve vencer a mais
  recente em transação.
- **T-5.** Tier 1 falha, tier 2 também falha (algum `nivel_ref` sem candidata
  na Etapa S1): saída é o `receita_cod` bruto. _Garantia do D3 (sem
  inventos)._
- **T-6.** Linhas com `data_registro_fim ≠ sentinela` não influenciam nenhuma
  resolução, em nenhum dos tiers.
- **T-7.** `receita_cod` vazio devolve string vazia sem consultar banco.

## Referências cruzadas

- `_dev/spec_foreignKeys_vigencia.md` — política de **união contígua** usada
  por validação de FK; esta spec **não** a estende para a apresentação.
- `_dev/spec_itemClassificacao_foreignKeys_lookup.md` — endpoints JSON de
  lookup; seguem usando a regra estrita (tier 1 puro).
- `_dev/spec_django.md` — convenções gerais de implementação Django.
