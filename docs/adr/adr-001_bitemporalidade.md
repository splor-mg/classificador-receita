---
title: ADR-001 - Bitemporalidade
description: Estratégia de Bitemporalidade no Banco de Dados do Classificador
---

# ADR-001 — Estratégia de Bitemporalidade no Banco de Dados do Classificador

## Status

- **Estado**: Proposta
- **Data**: 2025-12-16
- **Decisor(es)**: DCAF e AID
- **Participantes**: DCAF e AID

## Contexto

O Classificador de Natureza de Receita de Minas Gerais é usado há muitos anos como base para registro, controle e análise das receitas, mas a forma como seu histórico é armazenado hoje torna a evolução das classificações **irrastreável de forma sistemática**. O SISOR conserva apenas as classificações ativas do ano corrente e, eventualmente, do ano seguinte, sem o histórico completo de versões anteriores. Em paralelo, o Ementário Excel mantido pela DCAF tenta suprir essa lacuna acumulando códigos vigentes e inativos ao longo do tempo, porém sem um modelo formal de dados temporais e sem garantias de integridade ou consistência entre períodos.

Nesse cenário, responder perguntas como **“qual era a situação exata deste código em uma data específica?”** ou **“quando o sistema passou a conhecer determinada mudança?”** depende de buscas manuais em planilhas e da memória institucional, em vez de consultas reprodutíveis ao banco de dados. Sem um modelo bitemporal, o sistema não consegue representar de forma estruturada **quando** uma classificação era válida no mundo real (tempo de validade) e **quando** essa informação foi registrada, alterada ou corrigida no sistema (tempo de transação), o que compromete auditoria, transparência e reprodutibilidade de análises históricas.

Para resolver esse problema, este ADR propõe a adoção explícita de um **modelo de banco de dados bitemporal**, em que cada registro relevante das classificações passa a carregar dois eixos de tempo: o `valid_time` (`data_vigencia_inicio` / `data_vigencia_fim`), que representa o período em que aquela informação vale no domínio orçamentário, e o `transaction_time` (`data_registro_inicio` / `data_registro_fim`), que registra o período em que o sistema tomou conhecimento da alteração.

## Decisão

Adotar um **modelo bitemporal implementado diretamente no banco de dados PostgreSQL**, com as seguintes diretrizes:

1 - **Camada de dados bitemporal (núcleo do modelo)**

Cada entidade temporalmente sensível (ex.: itens de classificação, versões, variantes) terá, no mínimo:
  
  - Colunas de **tempo de validade (valid_time)**: por exemplo, `data_vigencia_inicio` e `data_vigencia_fim`, representando o período em que a informação é válida e é capaz de surtir efeitos no domínio orçamentário.
  - Colunas de **tempo de transação (transaction_time)**: por exemplo, `data_registro_inicio` e `data_registro_fim`, registrando o período em que o sistema considerou aquela informação como verdadeira, diferente de `data_vigencia_fim`, que representa quando a informação deixou de ser válida no mundo real. O `data_registro_fim` é fechado quando o sistema atualiza ou corrige aquela informação, permitindo auditoria completa do que o sistema "sabia" em cada momento.
   
Adotar convenção de intervalos "abertos à direita" (ex.: `data_vigencia_fim` e `data_registro_fim`), utilizando um **valor sentinela** (_sentinel value_) para representar intervalos que permanecem abertos no futuro. O valor sentinela escolhido é `9999-12-31`, que representa uma data suficientemente distante no futuro para ser tratada como "indefinida" ou "até o momento presente". Algumas implementações tratam intervalos abertos usando `NULL` em vez de um valor sentinela. Optamos por não adotar `NULL` porque: (1) simplifica consultas SQL ao evitar condições `IS NULL` em cláusulas `WHERE` e comparações de intervalo; (2) permite índices mais eficientes em colunas de data sem necessidade de lógica especial para `NULL`; (3) facilita operações de comparação temporal (ex.: `data_vigencia_fim >= CURRENT_DATE`) sem tratamento de casos especiais; (4) mantém consistência com a literatura de bancos temporais que recomenda valores sentinela para intervalos abertos.

2 - **Registro de histórico como _append-only_ lógico**

  - Alterações relevantes (inativação, reclassificação, correções) não sobrescrevem registros, mas **criam novas linhas** com novos intervalos de `valid_time` e `transaction_time`.
  - Este padrão é compatível com o **Slowly Changing Dimensions (SCD) Type 2**, indo além ao incorporar também o tempo de transação (`transaction_time`) para suporte completo a auditoria.
  - **Sobre SCD Type 2**: O padrão Slowly Changing Dimensions (SCD) Type 2, proposto por Kimball e Ross para data warehousing, trata de como gerenciar mudanças históricas em dimensões. No SCD Type 2, quando um atributo de uma dimensão muda, em vez de atualizar o registro existente, cria-se um novo registro com uma nova chave substituta e mantém-se o registro antigo para preservar o histórico. O modelo bitemporal adotado aqui segue essa lógica de "append-only" (criar novos registros em vez de sobrescrever), mas estende o SCD Type 2 ao incorporar dois eixos temporais. Isso permite não apenas rastrear "o que era válido em uma data" (como no SCD Type 2 tradicional), mas também "o que o sistema sabia em uma data", essencial para auditoria completa.
  - O estado "corrente" é sempre o registro com:
    - `data_registro_fim` igual ao valor sentinela, e
    - intervalo de `valid_time` que contenha a data de referência (ou "hoje").

2 - **Registro de histórico como _append-only_ lógico**

O Slowly Changing Dimensions (SCD) é uma metodologia/abordagem amplamente utilizada em data warehousing para gerenciar mudanças em dados dimensionais ao longo do tempo, e identifica diferentes modelos de gestão, distinguindo-os em relação à forma de recuperação de um registro histórico vigente no tempo.

O modelo proposto para este projeto segue a lógica do **SCD Type 2**, em que o histórico é preservado por meio da criação de **novas linhas** a cada mudança relevante, em vez de sobrescrever o registro anterior. Em outras palavras, quando algo muda na classificação (por exemplo, um código é inativado, reclassificado ou corrigido), não alteramos a linha antiga: **abrimos uma nova linha**, com novos valores de `valid_time` e `transaction_time`, e fechamos adequadamente os intervalos da linha anterior.

Esse comportamento _append-only_ permite reconstruir, a qualquer momento, **como o dado era considerado válido** (eixo de vigência) e **o que o sistema sabia em cada data** (eixo de transação). Assim, o histórico não é apenas reprodutível, mas também auditável, o que é especialmente importante em um contexto de legalidade estrita.

O **estado "corrente"** de uma classificação, em uma data de referência, é identificado de forma objetiva:  
- é a linha cujo `data_registro_fim` ainda está com o **valor sentinela** (ou seja, o sistema ainda considera aquela versão como verdadeira); e  
- cujo intervalo de `valid_time` (`data_vigencia_inicio` e `data_vigencia_fim`) contém a data de referência. Por exemplo, a data de hoje está entre `data_vigencia_inicio` e `data_vigencia_fim`, considerando também o valor sentinela para vigência em aberto.

Dessa forma, o modelo consegue ao mesmo tempo preservar todas as versões históricas e oferecer uma regra clara para saber **qual linha representa a situação vigente em determinada data**.


3 - **Responsabilidade principal no banco, com apoio da aplicação (modelo híbrido simples)**

  - **Triggers em PostgreSQL** serão usados para:
    - Fechar `data_registro_fim` do registro anterior em uma alteração.
    - Inserir o novo registro com `data_registro_inicio` atual e `data_registro_fim` aberto.
  - A **aplicação/regras de negócio** será responsável por:
    - Decidir _quando_ criar novas "versões temporais" (regras de negócio).
    - Expor APIs e consultas temporais para os consumidores:
      - **Consultas "current"**: Retornam o estado atual dos dados, ou seja, o que é válido e conhecido pelo sistema na data de hoje. Essas são as consultas mais comuns no uso operacional do sistema.
      - **Consultas "as-of"** (também chamadas de _point-in-time queries_): Permitem consultar o estado dos dados em uma data específica do passado, seja do ponto de vista de validade (`valid_time`) ou do conhecimento do sistema (`transaction_time`). Por exemplo: "qual era a classificação vigente em 2023-06-15?" ou "o que o sistema sabia sobre essa classificação em 2023-06-15?". Essas consultas são essenciais para auditoria, reprodução de análises históricas e conformidade legal.
  - Ou seja, a lógica de integridade temporal básica fica no banco; a semântica de negócio (quando considerar mudança relevante) fica na aplicação / regras de negócio da DCAF.

### Por que `data_registro_fim` é diferente de `data_vigencia_fim`?

**Importante**: `data_registro_fim` e `data_vigencia_fim` servem a propósitos completamente diferentes e **não são coincidentes**. A confusão entre esses dois eixos temporais é comum, mas entender a diferença é fundamental para o modelo bitemporal.

#### Diferença conceitual

- **`data_vigencia_fim`** (valid_time): Representa **quando a informação deixa de ser válida no mundo real** (domínio de negócio). Por exemplo, um código pode ter sido válido de 2020-01-01 a 2023-12-31 no contexto orçamentário.

- **`data_registro_fim`** (transaction_time): Representa **quando o sistema deixa de considerar aquela versão como a "verdade atual"** que ele conhece. Isso permite rastrear quando o sistema passou a conhecer uma informação e quando ela foi corrigida ou atualizada. Por exemplo, usando o mesmo código da linha anterior (válido de 2020-01-01 a 2023-12-31): se o sistema registrou essa informação em 2024-03-10 e depois descobriu um erro em 2024-08-15, o `data_registro_fim` do registro original seria 2024-08-15 (quando o sistema deixou de considerar aquela versão como verdadeira), enquanto o `data_vigencia_fim` permaneceria 2023-12-31 (quando a informação realmente deixou de ser válida no mundo real). Assim, `data_registro_fim` = 2024-08-15 ≠ `data_vigencia_fim` = 2023-12-31.

#### Exemplo prático: Correção retrospectiva

Considere o seguinte cenário:

1. **2024-01-15**: O sistema registra que o código "1.1.1.01" foi válido de **2020-01-01 a 2023-12-31**.
   - `data_vigencia_inicio` = 2020-01-01
   - `data_vigencia_fim` = 2023-12-31
   - `data_registro_inicio` = 2024-01-15
   - `data_registro_fim` = 9999-12-31 (aberto)

2. **2024-06-20**: Descobre-se um erro. Na verdade, o código foi válido apenas até **2022-12-31**, não até 2023-12-31. O sistema faz uma correção:
   - O registro anterior é fechado:
     - `data_registro_fim` = 2024-06-20 (fechado)
   - Um novo registro é criado com a informação corrigida:
     - `data_vigencia_inicio` = 2020-01-01
     - `data_vigencia_fim` = 2022-12-31 (corrigido)
     - `data_registro_inicio` = 2024-06-20
     - `data_registro_fim` = 9999-12-31 (aberto)

**Análise do exemplo**:
- `data_vigencia_fim` mudou de 2023-12-31 para 2022-12-31 (correção do período de validade real)
- `data_registro_fim` do primeiro registro foi fechado em 2024-06-20 (quando o sistema deixou de considerar aquela versão como verdadeira)
- Essas datas **não são coincidentes**: a vigência real terminou em 2022-12-31, mas o sistema só descobriu o erro em 2024-06-20

#### Utilidade do `data_registro_fim`

O `data_registro_fim` permite:

1. **Auditoria completa**: Saber exatamente o que o sistema "sabia" em qualquer momento do passado. Por exemplo: "O que o sistema mostrava em 2024-03-01?" → O primeiro registro (ainda com erro), pois `data_registro_fim` ainda estava aberto.

2. **Consultas "as-of"**: Consultar o estado do sistema em uma data específica, não apenas o que era válido naquela data. Isso é essencial para reproduzir análises históricas exatamente como foram feitas na época.

3. **Rastreamento de correções**: Identificar quando e como informações foram corrigidas, permitindo entender a evolução do conhecimento do sistema sobre os dados.

4. **Conformidade e transparência**: Demonstrar que o sistema mantém histórico completo de todas as versões que já foram consideradas verdadeiras, mesmo após correções.

Sem `data_registro_fim`, seria impossível distinguir entre "o que era válido" e "o que o sistema sabia", comprometendo a capacidade de auditoria e reprodução de análises históricas.

## Alternativas Consideradas

### Alternativa 1: Somente valid_time (modelo monotemporal simples)

- **Descrição**: Implementar apenas `valid_from` / `valid_to`, sem controle de `transaction_time`.
- **Prós**: Simplicidade de implementação; menor complexidade de consultas.
- **Contras**: Não permite saber "quando o sistema passou a saber" de uma mudança; não atende plenamente a requisitos de auditoria.
- **Razão da rejeição**: Não atende plenamente a requisitos de auditoria (não permite saber "quando o sistema passou a saber" de uma mudança).

### Alternativa 2: Implementar toda a lógica temporal apenas na aplicação

- **Descrição**: Manter histórico em tabelas comuns, deixando para a aplicação garantir integridade e consistência temporal.
- **Prós**: Flexibilidade na implementação; controle total pela aplicação.
- **Contras**: Aumenta complexidade da aplicação; risco maior de inconsistências; perde o potencial do PostgreSQL para garantir invariantes no próprio banco.
- **Razão da rejeição**: Aumenta complexidade da aplicação; risco maior de inconsistências; perde o potencial do PostgreSQL para garantir invariantes no próprio banco.

### Alternativa 3: Extensões específicas de temporalidade ou bancos especializados

- **Descrição**: Uso de extensões externas ou bancos de dados temporais dedicados.
- **Prós**: Funcionalidades especializadas; possível melhor performance para consultas temporais.
- **Contras**: Eleva complexidade operacional; reduz portabilidade; pode não ser necessário para o escopo atual.
- **Razão da rejeição**: Eleva complexidade operacional; reduz portabilidade; não é necessário para o escopo atual se PostgreSQL for bem utilizado.

## Consequências

### Positivas

- Suporte robusto a auditoria e consultas históricas ("o que o classificador dizia em tal data" e "o que o sistema sabia em tal data").
- Maior alinhamento com literatura de bancos temporais (*Temporal Data & the Relational Model*).
- Clareza de responsabilidades: banco garante integridade temporal básica; aplicação define semântica de mudança.

### Negativas / Riscos

- Maior complexidade de modelagem e consultas SQL (necessidade de capacitação da equipe).
- Custo adicional de implementação de triggers e _views_ específicas.
- Necessidade de documentação rigorosa para evitar uso incorreto das tabelas temporais.

## Referências

- Snodgrass, R. T. (2014). *Temporal Data & the Relational Model: A Detailed Investigation into the Application of Interval and Relation Theory to the Problem of Temporal Database Management*. Morgan Kaufmann.
- Kimball, R., & Ross, M. (2013). *The Data Warehouse Toolkit: The Definitive Guide to Dimensional Modeling* (3rd ed.). Wiley. (Slowly Changing Dimensions - SCD Type 2)
- [ADR-002: Adoção do Modelo GSIM para o Classificador de Receita](adr-002_gsim.md)
