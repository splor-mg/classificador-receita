# Especificação: Regras de Foreign Keys (FKs) entre entidades do classificador

Este documento centraliza as regras transversais de Foreign Key (FK) que se
aplicam entre tabelas do projeto, especialmente entre modelos bitemporais.

**Escopo.** Esta spec trata exclusivamente de **validação de cobertura
temporal de FK** (filho cuja vigência precisa estar contida na vigência da
mãe). A política aqui — união contígua de vigências de mesma entidade — é
**complementar e distinta** das políticas de **resolução de máscara visual**
em apresentação, formulários, lookups e sugestão de código filho. Para esses
contextos, ver `_dev/spec_itemClassificacao_mascara_apresentacao.md`
(apresentação na changelist, com tier estrito + tier secundário) e os pontos
no código que usam diretamente `format_receita_cod_by_vigencia` (regra
estrita pura, sem fallback).

Tópicos:

- [Definição de Vigência por União Contígua de Mesma Entidade Semântica](#definição-de-vigência-por-união-contígua-de-mesma-entidade-semântica)

---

## Definição de Vigência por União Contígua de Mesma Entidade Semântica

### Contexto

No projeto, os modelos `SerieClassificacao`, `Classificacao`, `NivelHierarquico`,
`ItemClassificacao`, `VersaoClassificacao` e `VarianteClassificacao` herdam de
`BitemporalModel` (`apps/core/models.py`). Em conformidade com o ADR-001
(bitemporalidade) e com o ADR-003 (chave semântica + `*_ref`), uma mesma
**entidade de negócio** (mesmo `*_id` semântico, mesmo `*_ref` surrogado) pode
ter **múltiplas linhas físicas** na tabela: uma por janela de
`[data_vigencia_inicio, data_vigencia_fim]`, somadas a um eixo de
`transaction_time` (`data_registro_inicio`, `data_registro_fim`).

O Django, porém, ao representar uma FK, armazena na coluna apenas a PK de **uma
linha física** do alvo. Esse desencontro entre "FK para linha" e "FK para
entidade" gera o seguinte cenário ao salvar um registro filho:

- O filho tem vigência `[ini_filho, fim_filho]`.
- A entidade mãe (mesmo `*_id`) tem várias linhas ativas em transaction-time
  (cada uma com `data_registro_fim = sentinela`), cada uma com vigência menor
  que `[ini_filho, fim_filho]`.
- Nenhuma linha sozinha cobre `[ini_filho, fim_filho]`, mas a **união** das
  vigências das linhas ativas, na prática, cobre.

A validação anterior comparava `[ini_filho, fim_filho]` apenas com a vigência
da **linha apontada** pela FK e reprovava o salvamento mesmo quando a entidade
mãe, vista como um todo, cobria integralmente o filho.

### Decisão

Promover, na validação de contenção temporal entre modelos bitemporais, a
unidade de comparação de "linha física" para **entidade de negócio**,
identificada pelo `*_ref` (chave surrogada). A vigência da entidade passa a ser
a **união contígua** das vigências de todas as linhas com
`data_registro_fim = sentinela` que compartilham o mesmo `*_ref`.

A FK física continua armazenando o ponteiro para uma linha (limitação do ORM).
O reaponte automático (`apply_temporal_fk_resolution`) mantém o comportamento
atual:

- Se houver **uma única linha ativa** cuja vigência sozinha contenha
  `[ini_filho, fim_filho]`, a FK pousa nessa linha.
- Caso contrário, a FK pousa na **linha ativa mais recente** da mesma entidade
  (maior `data_vigencia_inicio`, com desempate por `data_registro_inicio` e
  depois `pk`). É essa linha que aparece no link à direita da lupa no Admin.

### Identidade da entidade

A varredura das "linhas ativas da mesma entidade" usa exclusivamente o `*_ref`
do modelo-alvo, quando existir. Justificativas:

- Estabilidade frente a renomeações da chave semântica (`*_id`), conforme
  ADR-003.
- Garante que a união consolidada represente uma única entidade conceitual
  mesmo após eventuais ajustes de nomenclatura.

Quando o modelo-alvo não tiver coluna `*_ref` (caso raro entre modelos
bitemporais), o fallback é o primeiro `*_id` semântico não-relacional; e, se
ainda assim não houver identidade, a PK da linha apontada.

A UI do Django Admin continua exibindo o `*_id` semântico para legibilidade —
a substituição da chave de varredura é interna à validação.

### Aplicabilidade

A nova regra aplica-se exclusivamente quando o modelo-alvo da FK **herda de
`BitemporalModel`**. FKs para modelos não bitemporais (ex.: `BaseLegalTecnica`)
permanecem validadas pela regra clássica de "linha única": a vigência do filho
deve estar contida na vigência da linha apontada.

Sem mecanismo de exclusão por modelo: a validação por união cobre toda FK
many-to-one cujo destino seja bitemporal. Se no futuro houver necessidade de
excluir uma FK específica, criaremos override próprio
(ex.: `temporal_fk_union_validation_exclude_fields`); **não reutilizar** os
existentes `temporal_fk_include_fields` / `temporal_fk_exclude_fields`, que
controlam o reaponte automático e são conceito ortogonal a esta validação.

### Algoritmo de validação (duas etapas)

Para cada FK declarada em `fk_fields` no `clean()` do modelo:

1. **Resolução do alvo.** Carrega a linha do alvo a partir do valor da FK.
   Se for `None` (FK opcional), ignora silenciosamente.

2. **Etapa 1 — linha única apontada.** Se a vigência da linha apontada sozinha
   já contém `[ini_filho, fim_filho]`, a validação passa imediatamente. Esse
   é o caminho mais comum e o mais barato.

3. **Etapa 2 — união contígua das linhas ativas da entidade.** Aplicada
   apenas se o alvo herda de `BitemporalModel` e a Etapa 1 não passou.

   3.1. Monta o filtro de identidade priorizando `*_ref` do alvo.

   3.2. Consulta todas as linhas com esse `*_ref` e
   `data_registro_fim = sentinela`. Coleta `(data_vigencia_inicio,
   data_vigencia_fim)` de cada uma.

   3.3. Calcula a **união contígua** das janelas. Definição estrita de
   contiguidade: dois intervalos vizinhos `[a, b]` e `[c, d]`, ordenados por
   início ascendente, fundem-se em um único `[a, d]` **somente quando**
   `c == b + 1 dia`. Sobreposições (`c <= b`) não fundem — viram entradas
   separadas na união consolidada (sobreposições entre linhas ativas da mesma
   entidade são inconsistência de dados detectada por outras camadas).

   3.4. Verifica se `[ini_filho, fim_filho]` está **integralmente coberto**
   pela união. Se sim, a validação passa.

4. **Etapa 3 — falha com diagnóstico.** Se a Etapa 1 e a Etapa 2 falharam,
   levanta `ValidationError` mostrando:

   - A vigência do filho.
   - O `*_id` semântico do alvo (para o usuário, que vê semântica).
   - A união consolidada das vigências ativas.
   - A lista de **gaps** (faixas de `[ini_filho, fim_filho]` que ficaram
     descobertas), quando houver.

### Formato da mensagem de erro

Sem gaps explícitos (ex.: união completamente vazia ou completamente fora da
janela do filho), a mensagem traz apenas as duas primeiras linhas. Com gaps,
inclui-se a seção "Faltas:" em lista. Exemplo com dois gaps:

```text
O período de vigência deste registro (2018-01-01 a 9999-12-31) não está
integralmente coberto pela união das vigências ativas de classificação
selecionada (CLASS-RECEITA-UNIAO-2018). União consolidada: 2018-01-01 a
2021-12-31; 2024-01-01 a 2024-12-31; 2026-01-01 a 9999-12-31. Faltas:
  - 2022-01-01 a 2023-12-31
  - 2025-01-01 a 2025-12-31
```

Quando a união cobre integralmente o filho, **nenhum erro é levantado** — a
mensagem nunca aparece nesse caso.

### Tratamento do valor sentinela `9999-12-31`

A operação de "próximo dia" não é aplicada quando `data_vigencia_fim` é igual
ao sentinela `VALID_TIME_SENTINEL` (9999-12-31). Por convenção do projeto,
nenhum intervalo pode começar depois do sentinela; portanto:

- Em fusão contígua: se `b == 9999-12-31`, o intervalo `[a, b]` é "aberto à
  direita" e não há `c == b + 1 dia` válido para fundir.
- Em cálculo de gaps: se algum intervalo da união tem `fim == sentinela` e
  cobre o cursor, todo o restante de `[ini_filho, fim_filho]` é considerado
  coberto.

### Casos de uso (regressão e aceite)

- **Caso 0 (regressão real).** `CLASS-RECEITA-UNIAO-2018` reversionada em
  duas linhas ativas: `[2018-01-01, 2025-12-31]` e `[2026-01-01, 9999-12-31]`.
  Filho `NivelHierarquico` com vigência `[2018-01-01, 9999-12-31]`. Etapa 1
  falha (linha apontada cobre apenas 2026 em diante). Etapa 2 funde as duas
  janelas em `[2018-01-01, 9999-12-31]`. Validação passa. **Salvamento
  permitido.**

- **Caso 1.** Uma única linha ativa cuja vigência contém o filho. Etapa 1
  passa; Etapa 2 nem é executada.

- **Caso 2.** Duas linhas ativas com gap real: `[2018-01-01, 2020-12-31]` e
  `[2024-01-01, 9999-12-31]`. Filho com vigência `[2018-01-01, 9999-12-31]`.
  Etapa 2 não funde (não há contiguidade estrita). Gap reportado:
  `2021-01-01 a 2023-12-31`. **Salvamento rejeitado.**

- **Caso 3.** FK para `BaseLegalTecnica` (modelo não bitemporal). Apenas
  regra clássica de "linha única" se aplica. Comportamento idêntico ao
  anterior à mudança.

- **Caso 4.** FK opcional não preenchida (`None`). Ignorada silenciosamente.

- **Caso 5.** Auto-FK (`parent_item_id` em `ItemClassificacao`). A entidade
  varrida é o `item_ref` da linha apontada; aplica-se a Etapa 2 normalmente.

- **Caso 6.** Linhas inativas em transaction-time
  (`data_registro_fim != sentinela`) **não entram** na união. Mesmo que
  cobrissem a vigência do filho, são desconsideradas porque representam
  estados passados do conhecimento do sistema.

### Pontos de implementação

- A reescrita concentra-se em `apps/core/vigencia_fk_validation.py`. Os
  cinco `clean()` de modelos bitemporais que já chamam
  `validate_vigencia_contained_in_fk_targets` herdam a nova semântica sem
  modificação.
- Refinamento auxiliar em `apps/core/temporal_fk_resolution.py`: a função
  `_build_identity_filter` passa a usar **apenas** o(s) campo(s) `*_ref` do
  alvo, com fallback para `*_id` somente quando nenhum `*_ref` estiver
  preenchido.
- A varredura das linhas ativas usa o sentinela de `data_registro_fim`
  adequado ao tipo do campo (aware/naive conforme `USE_TZ`), reaproveitando a
  convenção já utilizada em `apply_temporal_fk_resolution`.

### Consequências e trade-offs

- **Vantagens.** Coerência da semântica de FK com o conceito de entidade
  bitemporal; reduz reprovações falsas após reversionamentos do mãe; mensagem
  de erro mais útil (mostra exatamente o que falta cobrir).
- **Trade-offs.** A FK física pode apontar para uma linha cuja vigência
  sozinha não cobre o filho (caso típico do fallback "mais recente"). Esse
  desencontro entre "linha apontada" e "entidade coberta" é intencional e
  decorre da limitação do ORM; a auditoria temporal verdadeira é feita
  consultando a união das linhas ativas, não a linha apontada.
- **Compatibilidade.** Não há migração de banco; é mudança apenas de regra
  de validação em `clean()`. Dados existentes não são afetados.
