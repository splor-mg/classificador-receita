# ADR-001 — Estratégia de Bitemporalidade no Banco de Dados do Classificador

## Contexto

O Classificador de Natureza de Receita de Minas Gerais é usado há muitos anos como base para registro, controle e análise das receitas, mas a forma como seu histórico é armazenado hoje torna a evolução das classificações **irrastreável de forma sistemática**. O SISOR conserva apenas as classificações ativas do ano corrente e, eventualmente, do ano seguinte, sem o histórico completo de versões anteriores. Em paralelo, o Ementário Excel mantido pela DCAF tenta suprir essa lacuna acumulando códigos vigentes e inativos ao longo do tempo, porém sem um modelo formal de dados temporais e sem garantias de integridade ou consistência entre períodos.

Nesse cenário, responder perguntas como “qual era a situação exata deste código em uma data específica?” ou “quando o sistema passou a conhecer determinada mudança?” depende de buscas manuais em planilhas e da memória institucional, em vez de consultas reprodutíveis ao banco de dados. Sem um modelo bitemporal, o sistema não consegue representar de forma estruturada **quando** uma classificação era válida no mundo real (tempo de validade) e **quando** essa informação foi registrada, alterada ou corrigida no sistema (tempo de transação), o que compromete auditoria, transparência e reprodutibilidade de análises históricas.

Para resolver esse problema, este ADR propõe a adoção explícita de um **modelo de banco de dados bitemporal**, em que cada registro relevante das classificações passa a carregar dois eixos de tempo: o `valid_time` (`data_inicio_vigencia` / `data_fim_vigencia`), que representa o período em que aquela informação vale no domínio orçamentário, e o `transaction_time` (`data_registro`), que registra o período em que o sistema tomou conhecimento da alteração.

## Decisão

Adotar um **modelo bitemporal implementado diretamente no banco de dados PostgreSQL**, com as seguintes diretrizes:

1. **Camada de dados bitemporal (núcleo do modelo)**
   - Cada entidade temporalmente sensível (ex.: itens de classificação, versões, variantes) terá, no mínimo:
     - Colunas de **tempo de validade (valid_time)**: por exemplo, `data_inicio_vigencia` e `data_fim_vigencia`, representando o período em que a informação é válida no domínio orçamentário.
     - Colunas de **tempo de transação (transaction_time)**: por exemplo, `sys_from` e `sys_to`, registrando o período em que o sistema considerou aquela informação como verdadeira.
   - Adotar convenção de intervalos “abertos à direita” (ex.: `[data_inicio_vigencia, data_fim_vigencia)` e `[sys_from, sys_to)`), com um valor sentinela para “aberto” (ex.: `9999-12-31`).

2. **Registro de histórico como _append-only_ lógico**
   - Alterações relevantes (inativação, reclassificação, correções) não sobrescrevem registros, mas **criam novas linhas** com novos intervalos de `valid_time` e `transaction_time`.
   - O estado “corrente” é sempre o registro com:
     - `sys_to` igual ao valor sentinela, e
     - intervalo de `valid_time` que contenha a data de referência (ou “hoje”).

3. **Responsabilidade principal no banco, com apoio da aplicação (modelo híbrido simples)**
   - **Triggers em PostgreSQL** serão usados para:
     - Fechar `sys_to` do registro anterior em uma alteração.
     - Inserir o novo registro com `sys_from` atual e `sys_to` aberto.
   - A **aplicação** será responsável por:
     - Decidir _quando_ criar novas “versões temporais” (regras de negócio).
     - Expor APIs e consultas já “as-of” / “current” para os consumidores.
   - Ou seja, a lógica de integridade temporal básica fica no banco; a semântica de negócio (quando considerar mudança relevante) fica na aplicação / regras de negócio da DCAF.

4. **Consultas padrão**
   - Definir _views_ ou _functions_ padrão para:
     - **Estado atual**: `WHERE current_date BETWEEN valid_from AND valid_to AND sys_to = '9999-12-31'`.
     - **Consultas “as-of” (valid-time)**: data de interesse no eixo de validade.
     - **Consultas “point-in-time” (bitemporal)**: combinação de data de validade e data de conhecimento (transaction_time).
   - Documentar exemplos concretos de consultas (incluídos na documentação técnica desta ADR).

## Alternativas Consideradas

1. **Somente valid_time (modelo monotemporal simples)**
   - Apenas `valid_from` / `valid_to`, sem controle de `transaction_time`.
   - **Rejeitada**: não atende plenamente a requisitos de auditoria (não permite saber “quando o sistema passou a saber” de uma mudança).

2. **Implementar toda a lógica temporal apenas na aplicação**
   - Manter histórico em tabelas comuns, deixando para a aplicação garantir integridade e consistência temporal.
   - **Rejeitada**: aumenta complexidade da aplicação; risco maior de inconsistências; perde o potencial do PostgreSQL para garantir invariantes no próprio banco.

3. **Extensões específicas de temporalidade ou bancos especializados**
   - Uso de extensões externas ou bancos de dados temporais dedicados.
   - **Rejeitada no MVP**: eleva complexidade operacional; reduz portabilidade; não é necessário para o escopo atual se PostgreSQL for bem utilizado.

## Consequências

- **Positivas**
  - Suporte robusto a auditoria e consultas históricas (“o que o classificador dizia em tal data” e “o que o sistema sabia em tal data”).
  - Maior alinhamento com literatura de bancos temporais (*Temporal Data & the Relational Model*).
  - Clareza de responsabilidades: banco garante integridade temporal básica; aplicação define semântica de mudança.

- **Negativas / Riscos**
  - Maior complexidade de modelagem e consultas SQL (necessidade de capacitação da equipe).
  - Custo adicional de implementação de triggers e _views_ específicas.
  - Necessidade de documentação rigorosa para evitar uso incorreto das tabelas temporais.

## Status

- **Proposta** — a ser revisada e aprovada pela DCAF.


