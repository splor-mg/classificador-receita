# ADR-001 — Estratégia de Bitemporalidade no Banco de Dados do Classificador

## Status

- **Estado**: Proposta
- **Data**: 2025-12-16
- **Decisor(es)**: DCAF e AID
- **Participantes**: DCAF e AID

## Contexto

O Classificador de Natureza de Receita de Minas Gerais é usado há muitos anos como base para registro, controle e análise das receitas, mas a forma como seu histórico é armazenado hoje torna a evolução das classificações **irrastreável de forma sistemática**. O SISOR conserva apenas as classificações ativas do ano corrente e, eventualmente, do ano seguinte, sem o histórico completo de versões anteriores. Em paralelo, o Ementário Excel mantido pela DCAF tenta suprir essa lacuna acumulando códigos vigentes e inativos ao longo do tempo, porém sem um modelo formal de dados temporais e sem garantias de integridade ou consistência entre períodos.

Nesse cenário, responder perguntas como “qual era a situação exata deste código em uma data específica?” ou “quando o sistema passou a conhecer determinada mudança?” depende de buscas manuais em planilhas e da memória institucional, em vez de consultas reprodutíveis ao banco de dados. Sem um modelo bitemporal, o sistema não consegue representar de forma estruturada **quando** uma classificação era válida no mundo real (tempo de validade) e **quando** essa informação foi registrada, alterada ou corrigida no sistema (tempo de transação), o que compromete auditoria, transparência e reprodutibilidade de análises históricas.

Para resolver esse problema, este ADR propõe a adoção explícita de um **modelo de banco de dados bitemporal**, em que cada registro relevante das classificações passa a carregar dois eixos de tempo: o `valid_time` (`data_vigencia_inicio` / `data_vigencia_fim`), que representa o período em que aquela informação vale no domínio orçamentário, e o `transaction_time` (`data_registro`), que registra o período em que o sistema tomou conhecimento da alteração.

## Decisão

Adotar um **modelo bitemporal implementado diretamente no banco de dados PostgreSQL**, com as seguintes diretrizes:

1. **Camada de dados bitemporal (núcleo do modelo)**
   - Cada entidade temporalmente sensível (ex.: itens de classificação, versões, variantes) terá, no mínimo:
     - Colunas de **tempo de validade (valid_time)**: por exemplo, `data_vigencia_inicio` e `data_vigencia_fim`, representando o período em que a informação é válida e é capaz de surtir efeitos no domínio orçamentário.
     - Colunas de **tempo de transação (transaction_time)**: por exemplo, `data_registro_inicio` e `data_registro_fim`, registrando o período em que o sistema considerou aquela informação como verdadeira.
   - Adotar convenção de intervalos “abertos à direita” (ex.: `[data_vigencia_inicio, data_vigencia_fim)` e `[sys_from, data_registro_fim)`), com um valor sentinela para “aberto” (ex.: `9999-12-31`).

2. **Registro de histórico como _append-only_ lógico**
   - Alterações relevantes (inativação, reclassificação, correções) não sobrescrevem registros, mas **criam novas linhas** com novos intervalos de `valid_time` e `transaction_time`.
   - Este padrão é compatível com o **Slowly Changing Dimensions (SCD) Type 2**, indo além ao incorporar também o tempo de transação (transaction_time) para suporte completo a auditoria.
   - **Sobre SCD Type 2**: O padrão Slowly Changing Dimensions (SCD) Type 2, proposto por Kimball e Ross para data warehousing, trata de como gerenciar mudanças históricas em dimensões. No SCD Type 2, quando um atributo de uma dimensão muda, em vez de atualizar o registro existente, cria-se um novo registro com uma nova chave substituta e mantém-se o registro antigo para preservar o histórico. O modelo bitemporal adotado aqui segue essa lógica de "append-only" (criar novos registros em vez de sobrescrever), mas estende o SCD Type 2 ao incorporar dois eixos temporais: o tempo de validade (valid_time), e o tempo de transação (transaction_time). Isso permite não apenas rastrear "o que era válido em uma data" (como no SCD Type 2 tradicional), mas também "o que o sistema sabia em uma data", essencial para auditoria completa.
   - O estado "corrente" é sempre o registro com:
     - `data_registro_fim` igual ao valor sentinela, e
     - intervalo de `valid_time` que contenha a data de referência (ou "hoje").

3. **Responsabilidade principal no banco, com apoio da aplicação (modelo híbrido simples)**
   - **Triggers em PostgreSQL** serão usados para:
     - Fechar `data_registro_fim` do registro anterior em uma alteração.
     - Inserir o novo registro com `data_registro_inicio` atual e `data_registro_fim` aberto.
   - A **aplicação/regras de negócio** será responsável por:
     - Decidir _quando_ criar novas “versões temporais” (regras de negócio).
     - Expor APIs e consultas já “as-of” / “current” para os consumidores.
   - Ou seja, a lógica de integridade temporal básica fica no banco; a semântica de negócio (quando considerar mudança relevante) fica na aplicação / regras de negócio da DCAF.

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
- [ADR-002: Adoção do Modelo GSIM para o Classificador de Receita](ADR-002-gsim.md)


