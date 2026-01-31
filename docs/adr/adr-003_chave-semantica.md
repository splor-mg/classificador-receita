---
title: ADR-003 - Chave semântica e referência numérica
description: Uso combinado de chave semântica e coluna de referência numérica; foreign keys por chave semântica
---

# ADR-003 — Chave semântica e referência numérica

## Status

- **Estado**: Proposta
- **Data**: 2026-01-30
- **Decisor(es)**: DCAF e AID
- **Participantes**: DCAF e AID

## Contexto

Em modelos relacionais, a identificação de entidades e o estabelecimento de vínculos entre tabelas dependem de **chaves**. Duas abordagens clássicas coexistem:

- **Chave natural (semântica)**: identifica a entidade/instância (o registro específico dentro da entidade/tabela) pelo **significado de negócio** (ex.: `serie_id = 'SERIE-RECEITA-MG'`). O valor carrega informação; nomes de colunas e valores ajudam na leitura e na governança.
- **Chave substituta (surrogate)**: identificador **sem significado de negócio** (ex.: inteiro sequencial, UUID). Estável ao longo do tempo; não depende de convenções de nomenclatura ou de mudanças de nome no domínio.

No projeto do classificador, as entidades são bitemporais (ADR-001): uma mesma entidade de negócio (ex.: uma série) pode ter **várias linhas/instâncias** (uma por versão do registro). A chave única da **linha** é composta (ex.: `serie_id` + `data_vigencia_inicio` +  `data_registro_inicio`); a identificação da **entidade** (a série em si) é feita por `serie_id`. Surge a dúvida: usar apenas chave semântica, apenas substituta, ou uma combinação? E **como** referenciar entidades em outras tabelas (foreign keys)?

Forças em jogo: (1) **Governança e clareza** — nomes e códigos legíveis facilitam auditoria, documentação e uso por domínio; (2) **Estabilidade de referência** — se o padrão ou o valor da chave semântica mudar (ex.: renomear `SERIE-RECEITA-MG` para outro padrão), referências que dependem desse valor precisam ser atualizadas; (3) **Integridade referencial** — FKs devem apontar de forma inequívoca para a entidade (ou para a versão correta, conforme o desenho).

## Decisão

Adotar uma **combinação** das duas abordagens, com papéis bem definidos:

1. **Primary key (PK) da linha**: usar a **chave numérica** (`*_ref`) na composição da PK. Nas tabelas bitemporais, a PK da linha é composta por `*_ref`, `data_vigencia_inicio` e `data_registro_inicio`. A identificação técnica da linha fica estável: se o valor ou o padrão da chave semântica mudar, os valores de PK das linhas existentes não mudam.
2. **Foreign keys**: usar **apenas a chave semântica** (`*_id`) como alvo e origem das FKs entre tabelas do classificador. A clareza é mais relevante nas relações entre tabelas (ex.: "classificação pertence à série SERIE-RECEITA-MG", não à serie_id = 1); por isso a chave semântica é reservada para FKs.
3. **Chave semântica** (`*_id`): identifica a **entidade** no domínio; permanece como coluna obrigatória. A tabela referenciada deve ter **UNIQUE (entity_id, data_vigencia_inicio, data_registro_inicio)**, para que FKs que apontem para uma linha específica tenham alvo único. Quando a relação for apenas "pertence à entidade" (e não a uma versão específica da linha), a resolução da linha corrente do pai é feita por critério temporal na consulta (ex.: `data_registro_fim = 9999-12-31`).
4. **Coluna `*_ref`**: (a) mesmo valor para todas as linhas da mesma entidade (mesmo `*_id`); (b) compõe a PK da linha junto com `data_vigencia_inicio` e `data_registro_inicio`; (c) não é usada como alvo de FKs; (d) uso previsto para referência numérica estável fora do grafo de FKs (ex.: exportações, integrações, relatórios).

### Diretrizes de implementação

- **Primary key da linha**: composta por `*_ref`, `data_vigencia_inicio` e `data_registro_inicio` (ex.: `(serie_ref, data_vigencia_inicio, data_registro_inicio)`). A chave semântica (`*_id`) não compõe a PK.
- **Unicidade para FKs**: a tabela deve ter **UNIQUE (entity_id, data_vigencia_inicio, data_registro_inicio)** (ex.: `UNIQUE (serie_id, data_vigencia_inicio, data_registro_inicio)`), para que FKs que referenciem a chave semântica possam apontar para uma linha específica quando necessário. Quando a FK for apenas por entidade (filha guarda só `serie_id`), a implementação em SQL pode exigir tabela de entidades (uma linha por entidade, PK = `*_id`) ou resolução por consulta.
- **Foreign keys**: sempre referenciar a **chave semântica** da entidade referida (e, se a relação for para uma versão específica da linha, incluir `data_vigencia_inicio` e `data_registro_inicio` no alvo e na origem). Não usar `*_ref` como alvo de FK.
- **Coluna `*_ref`**: (a) mesmo valor para todas as linhas que pertencem à mesma entidade (mesmo `*_id`); (b) atribuição sequencial ou controlada por domínio, de forma que a entidade mantenha o mesmo `*_ref` mesmo que o valor ou o padrão da chave semântica venha a mudar no futuro; (c) uso previsto para cenários em que se deseja uma referência numérica estável **fora** do grafo de FKs (ex.: exportações, integrações, relatórios que gravam “série 1” em vez do código semântico).

### Por que foreign key por chave semântica?

- **Legibilidade e governança**: consultas, scripts e documentação mostram vínculos explícitos (ex.: “classificação X pertence à série SERIE-RECEITA-MG”). Facilita revisão por domínio e auditoria.
- **Consistência com o modelo**: a entidade é conceitualmente identificada pelo `*_id`; as FKs espelham esse conceito.
- **Trade-off aceito**: se no futuro o **valor** ou o **padrão** da chave semântica for alterado (ex.: renomear `SERIE-RECEITA-MG` para outro identificador), será necessário atualizar o valor em todas as linhas da tabela de origem e em **todas as tabelas que referenciam essa chave**. A coluna `*_ref` **não mitiga** esse custo nas FKs, pois as FKs não a utilizam. Ela serve a outros fins (referência estável em contextos externos ao grafo de FKs). Portanto, a decisão de usar chave semântica nas FKs prioriza clareza e governança em detrimento da estabilidade do valor referenciado; mudanças de nomenclatura ou de convenção terão impacto em todas as tabelas que referenciam a entidade.

### Por que primary key numérica (`*_ref`, `data_vigencia_inicio`, `data_registro_inicio`)?

- **Estabilidade da PK**: se o valor ou o padrão da chave semântica mudar (ex.: renomear `SERIE-RECEITA-MG`), os valores de PK das linhas existentes **não mudam** — a PK é (`serie_ref`, `data_vigencia_inicio`, `data_registro_inicio`), não (`serie_id`, ...). Logs, auditoria ou qualquer referência interna que armazene o identificador da linha permanecem válidos.
- **Separação de papéis**: a PK identifica a **linha** de forma técnica e estável; a chave semântica identifica a **entidade** e é usada onde a clareza importa mais (FKs, consultas, governança).

### Por que manter a coluna `*_ref`?

- **Referência estável fora do banco**: sistemas externos, planilhas ou relatórios que precisem guardar “qual série” sem depender do string semântico podem usar o número (`serie_ref = 1`). Se o `serie_id` for renomeado ou o padrão mudar, o número pode permanecer, reduzindo impacto nesses usos.
- **Continuidade de identificação da entidade**: deixa explícito no modelo que a entidade (e não apenas a linha) tem um identificador numérico estável, alinhado à discussão de governança (um ref por entidade, não por linha).

## Alternativas Consideradas

### Alternativa 1: Apenas chave semântica (sem `*_ref`)

- **Descrição**: Usar somente `*_id` como identificador da entidade; não criar coluna `*_ref`.
- **Prós**: Modelo mais simples; menos colunas; sem ambiguidade sobre “qual é a chave”.
- **Contras**: Nenhuma referência numérica estável para uso externo; se no futuro for necessário expor um identificador que não mude com renomeação semântica, não haveria suporte no modelo.
- **Razão da rejeição**: O projeto optou por manter a opção de uma referência numérica estável por entidade (ref), mesmo que as FKs não a utilizem.

### Alternativa 2: Apenas chave substituta (surrogate) para entidade e FKs

- **Descrição**: Uma única coluna numérica (ex.: `serie_id`) como identificador da entidade; FKs referenciariam essa coluna.
- **Prós**: Referências estáveis; renomeação de códigos semânticos não afetaria FKs; valores compactos.
- **Contras**: Perda de legibilidade nas FKs (ex.: “classificação pertence a 1” em vez de “a SERIE-RECEITA-MG”); governança e auditoria ficam mais dependentes de joins ou de aplicação para recuperar o significado; desalinhamento com a orientação de chave semântica para governança.
- **Razão da rejeição**: Prioridade do projeto é governança e clareza nas relações; FKs por chave semântica atendem melhor a esse objetivo.

### Alternativa 3: FK por chave semântica e por `data_registro_inicio` (versão específica)

- **Descrição**: Em tabelas que referenciam entidades bitemporais, a FK poderia apontar para (entidade_id, data_vigencia_inicio, data_registro_inicio) para fixar uma versão específica da linha.
- **Prós**: Permite referenciar uma versão concreta do registro (ex.: “esta classificação refere-se à versão da série registrada em 2024-08-20”).
- **Contras**: Aumenta complexidade das FKs e das regras de negócio (geralmente queremos “esta classificação pertence à série X”, não “à versão da série X registrada em tal data”); pode ser considerado em cenários futuros se houver requisito explícito de vínculo a versão específica.
- **Razão da rejeição**: Para o escopo atual, FKs referenciam a **entidade** (via chave semântica); a resolução da versão corrente (registro ativo) é feita por critério temporal na consulta (ex.: `data_registro_fim = 9999-12-31`), não pela FK.

## Consequências

### Positivas

- **Governança e clareza**: FKs e consultas permanecem legíveis e alinhadas ao domínio (chave semântica).
- **Referência numérica estável**: Coluna `*_ref` disponível para integrações, exportações e relatórios que precisem de um identificador estável por entidade.
- **Papéis claros**: PK da linha = (`*_ref`, `data_vigencia_inicio`, `data_registro_inicio`); FKs = chave semântica (`*_id`); `*_ref` = referência estável por entidade e parte da PK, não usada como alvo de FKs.

### Negativas / Riscos

- **Impacto em renomeação**: Alteração do valor ou do padrão da chave semântica exige atualização em todas as tabelas que referenciam a entidade; `*_ref` não reduz esse impacto nas FKs.
- **Duas noções de “identificador”**: Equipe deve entender que a PK da linha é (`*_ref`, `data_vigencia_inicio`, `data_registro_inicio`); `*_id` identifica a entidade e é usada nas FKs; `*_ref` identifica a entidade de forma numérica e compõe a PK, mas não é usada como alvo de FKs.
- **Consistência de `*_ref`**: Garantir que todas as linhas da mesma entidade recebam o mesmo `*_ref` (regra de negócio ou constraint); documentar no schema e nos exemplos (ex.: `docs/assets/exemplo_serie_classificacao.csv`).

### Mitigações

- **Renomeação de chave semântica**: Evitar mudanças de valor ou padrão sem processo de mudança formal; em caso de alteração, planejar migração em todas as tabelas referenciadoras e documentar na ADR ou em nota de implementação.
- **Clareza dos papéis**: Manter este ADR e a documentação de exemplos (ex.: `docs/assets/exemplo_serie_classificacao_analise.md`) atualizados para que `*_id` (e PK composta) e `*_ref` não sejam confundidos com “chave por linha” PK da linha = (`*_ref`, `data_vigencia_inicio`, `data_registro_inicio`); FKs usam chave semântica (`*_id`); `*_ref` é por entidade (mesmo valor em todas as linhas da mesma entidade).

## Referências

- [ADR-001: Estratégia de Bitemporalidade no Banco de Dados do Classificador](adr-001_bitemporalidade.md)
- [ADR-002: Adoção do Modelo GSIM para o Classificador de Receita](adr-002_gsim.md)
- Documento de análise do exemplo de série: `docs/assets/exemplo_serie_classificacao_analise.md`
