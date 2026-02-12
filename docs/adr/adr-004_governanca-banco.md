---
title: ADR-004 - Governança do banco
description: Regras de operação do banco de dados (edição bitemporal, linha ativa, tipos de edição, fechamento de vigência e de registro)
---

# ADR-004 — Governança do banco

## Status

- **Estado**: Proposta
- **Data**: 2026-02-06
- **Decisor(es)**: DCAF e AID
- **Participantes**: DCAF e AID

## Contexto

O modelo de dados do Classificador adota bitemporalidade (ADR-001) e append-only (novas linhas em vez de atualização in place). Recursos como nível hierárquico e classificação possuem colunas `data_vigencia_inicio`, `data_vigencia_fim`, `data_registro_inicio` e `data_registro_fim` (valor sentinela `9999-12-31` para intervalos em aberto). Para suportar um painel de governança e fluxos de edição consistentes com auditoria e reprodutibilidade, é necessário formalizar **regras gerais** que definam: (1) o que significa "linha ativa" e quantas podem existir por entidade; (2) como o usuário escolhe o que editar; (3) os tipos de edição permitidos; (4) a sequência de operações (fechamento de registro e, quando aplicável, de vigência) e a garantia de que não haja alteração in place do conteúdo das linhas.

As regras abaixo foram auferidas a partir dos exemplos trabalhados nos seeds (ex.: `seed_nivel_hierarquico_t1` a `t4`, `seed_classificacao_t1v1` e `t1v2`) e da análise crítica de adequação ao modelo bitemporal, SCD Type 2 e GSIM. Este ADR consolida essas regras e explicita casos adicionais necessários para implementação e validação.

## Decisão

Adotar as **regras gerais de governança do banco** descritas abaixo, aplicáveis a todos os recursos/tabelas que possuem `data_registro_inicio` e `data_registro_fim` (e, quando aplicável, `data_vigencia_inicio` e `data_vigencia_fim`). A aplicação (painel de governança, APIs, comandos de carga) deve garantir conformidade com estas regras; validações e testes devem verificá-las.

### Convenções preliminares

- **Entidade-objeto (entidade de negócio)**: identificada pela **chave natural** do recurso. Exemplos: em `nivel_hierarquico`, a entidade é o par `(nivel_ref, classificacao_id)`; em `classificacao`, a entidade é identificada por `classificacao_id` (e eventualmente `serie_id` conforme o recurso). Cada recurso bitemporal deve documentar no schema qual é a chave natural que define a entidade.
- **Linha ativa**: linha em que `data_registro_fim` possui o **valor sentinela** (ex.: `9999-12-31`), ou seja, o sistema ainda considera aquela versão como a "verdade atual" para aquele intervalo de vigência.
- **Data da operação**: data em que a edição é registrada no sistema; será usada como `data_registro_inicio` de todas as novas linhas criadas na operação e como valor que fecha o `data_registro_fim` da linha que estava aberta.

---

### Regra 1 — Uma linha ativa por (entidade, período de vigência)

Deve haver **uma, e somente uma**, linha ativa (com `data_registro_fim` igual ao valor sentinela) para cada **par (entidade-objeto, período de vigência)**. Ou seja: para uma mesma entidade podem existir **várias** linhas ativas ao mesmo tempo, desde que cada uma corresponda a um **período de vigência distinto** (ex.: uma linha ativa para vigência 2002–2017 e outra para vigência 2019–9999). Para um mesmo (entidade, período de vigência) não pode haver mais de uma linha com `data_registro_fim` = sentinela.

---

### Regra 2 — Escolha da entidade e da linha a editar

Ao escolher editar um registro pré-existente, o usuário deve: (1) escolher **qual** classificação/entidade-objeto (identificada pela chave natural do recurso); (2) em seguida, escolher **qual** linha com valor sentinela em `data_registro_fim` será alvo da edição — pois, quando há mais de um período de vigência distinto, haverá mais de uma linha/instância ativa para aquela entidade. A interface deve listar apenas linhas com `data_registro_fim` = sentinela para a entidade selecionada. A linha escolhida **não** será alterada in place; ela terá apenas o `data_registro_fim` fechado (Regra 4), e novas linhas serão inseridas conforme o tipo de edição (Regras 5 ou 6).

---

### Regra 3 — Tipo de edição (pergunta obrigatória ao usuário)

Após a escolha da instância (entidade + linha ativa) a editar, o usuário deve ser **perguntado** sobre o tipo de edição, com duas opções:

- **Sobrescrever/corrigir vigência anterior**: o usuário está corrigindo o que o sistema registrou para o **mesmo** período de vigência (ex.: correção de atributos ou do próprio intervalo de vigência). Não se cria novo período de vigência no mundo real; apenas se atualiza o conhecimento do sistema sobre aquele período.
- **Registrar nova vigência/edição da classificação**: o usuário está registrando um **novo** período de vigência (nova "versão" no mundo real). A vigência anterior deve ser encerrada de forma explícita e a nova vigência registrada em nova linha.

*(Caso futuro: "Apenas encerrar vigência" — encerrar o período de vigência sem abrir outro — pode ser tratado como variante de "registrar nova vigência" com vigência que termina em data definida e sem linha sucessora, ou como terceiro tipo de edição; fica fora do escopo formal desta ADR até que o fluxo seja exigido.)*

---

### Regra 4 — Fechamento do registro da linha editada (sempre)

**Independente** da escolha pelo tipo de edição, a **data da operação** (que será a `data_registro_inicio` das novas linhas criadas) deve ser usada para **fechar** o `data_registro_fim` da linha/instância que o usuário escolheu editar. Ou seja: a linha que estava "aberta" (com `data_registro_fim` = sentinela) passa a ter `data_registro_fim` = data da operação. Esta é a **única** alteração permitida em uma linha já existente (exceção ao append-only puro); todo o restante do conteúdo das linhas antigas permanece imutável. A implementação pode fazer isso por um único UPDATE apenas na coluna `data_registro_fim` da linha escolhida, ou por convenção de leitura (considerar "fechada" quando existir nova linha com mesmo (entidade, vigência) e `data_registro_inicio` = data da operação); recomenda-se o UPDATE explícito para clareza e consistência em consultas.

---

### Regra 5 — Edição "sobrescrever/corrigir vigência anterior"

Quando o usuário optar por **sobrescrever/corrigir vigência anterior**:

1. Fechar o `data_registro_fim` da linha escolhida com a data da operação (Regra 4).
2. **Inserir uma única** nova linha/instância com os parâmetros corrigidos informados pelo usuário, com `data_registro_inicio` = data da operação e `data_registro_fim` = valor sentinela. O intervalo de vigência (`data_vigencia_inicio`, `data_vigencia_fim`) pode ser o mesmo da linha anterior ou corrigido (ex.: encerramento antecipado da vigência).

Não se insere linha de "encerramento de vigência" separada; a correção substitui o conhecimento anterior para aquele período de vigência.

---

### Regra 6 — Edição "registrar nova vigência/edição da classificação"

Quando o usuário optar por **registrar nova vigência/edição da classificação**:

1. **Fechar** o `data_registro_fim` da linha que o usuário escolheu editar, com a data da operação (Regra 4).
2. **Inserir** uma linha de **encerramento da vigência anterior**: nova linha com os **mesmos** parâmetros da linha que estava sendo atualizada, exceto:
   - `data_vigencia_fim` = dia **anterior** ao `data_vigencia_inicio` do novo período de vigência que será registrado;
   - `data_registro_inicio` = data da operação;
   - `data_registro_fim` = valor sentinela.
3. **Inserir** a linha da **nova vigência**: nova linha com os **novos** parâmetros da classificação/entidade-objeto, com `data_vigencia_inicio` (e eventualmente `data_vigencia_fim`) definidos pelo usuário, `data_registro_inicio` = data da operação e `data_registro_fim` = valor sentinela.

Assim, após a operação haverá duas linhas ativas (sentinela) para a mesma entidade: uma para o período de vigência que foi encerrado (até o dia anterior ao início do novo período) e outra para o novo período. Isso está em conformidade com a Regra 1, pois os períodos de vigência são distintos.

**Ordem operacional recomendada**: (1) fechar a linha atual; (2) inserir a linha de encerramento da vigência anterior; (3) inserir a linha da nova vigência. A data da operação deve ser a mesma em todas as novas linhas.

---

### Regra 7 — Validações de integridade temporal

- Para qualquer nova linha: `data_vigencia_inicio` ≤ `data_vigencia_fim` (considerando valor sentinela como "infinito"); `data_registro_inicio` ≤ `data_registro_fim`.
- No fluxo "registrar nova vigência", o `data_vigencia_inicio` da nova linha deve ser **posterior** ao `data_vigencia_fim` da linha de encerramento (ou imediatamente seguinte, sem sobreposição). O `data_vigencia_fim` da linha de encerramento deve ser exatamente o dia anterior ao `data_vigencia_inicio` da nova vigência.
- A aplicação deve garantir que, após cada operação de edição, não exista mais de uma linha ativa para o mesmo (entidade, período de vigência), conforme Regra 1.

---

### Regra 8 — Escopo por recurso

Cada recurso bitemporal (ex.: `nivel_hierarquico`, `classificacao`, `versao_classificacao`, `item_classificacao`) deve documentar no schema ou em anexo a esta ADR: (a) a **chave natural** que identifica a entidade-objeto; (b) se as Regras 1 a 7 se aplicam integralmente ou com adaptações (ex.: nomes de colunas). Recursos que não possuem `data_vigencia_*` mas possuem `data_registro_*` seguem as regras que não dependem de vigência (ex.: Regras 1 reduzida a "uma linha ativa por entidade", 2, 4; os tipos de edição podem ser simplificados conforme o modelo do recurso).

---

## Alternativas Consideradas

### Alternativa 1: Não formalizar regras (apenas exemplos)

- **Descrição**: Manter apenas os seeds e documentação informal, sem ADR.
- **Prós**: Menos burocracia.
- **Contras**: Risco de interpretações divergentes na implementação do painel e em validações; difícil garantir conformidade e auditoria.
- **Razão da rejeição**: A governança e a implementação exigem regras explícitas e estáveis.

### Alternativa 2: Um único tipo de edição (sempre "nova linha" sem perguntar)

- **Descrição**: Sempre inserir nova linha e fechar a anterior, sem distinguir "correção" de "nova vigência".
- **Prós**: Fluxo mais simples; menos perguntas ao usuário.
- **Contras**: Perde a semântica de "correção do mesmo período" vs "novo período"; no caso de nova vigência, não fica explícito o encerramento da vigência anterior (linha com `data_vigencia_fim` definido), podendo gerar ambiguidade ou inconsistência no histórico de valid time.
- **Razão da rejeição**: A distinção entre os dois tipos de edição é necessária para o modelo bitemporal correto (encerramento explícito de vigência vs correção no mesmo período).

---

## Consequências

### Positivas

- Regras únicas e canônicas para implementação do painel de governança, validações e testes.
- Alinhamento explícito com ADR-001 (bitemporalidade, append-only) e com os exemplos já validados (t1–t4, t1v1/t1v2).
- Rastreabilidade e auditoria preservadas; "uma linha ativa por (entidade, período de vigência)" evita ambiguidade na leitura do estado corrente.

### Negativas / Riscos

- A interface deve sempre perguntar o tipo de edição e listar corretamente as linhas ativas por entidade; maior complexidade de UX.
- A exceção de atualizar apenas `data_registro_fim` (Regra 4) deve ser documentada e implementada com cuidado para não abrir espaço a outros updates in place.

### Mitigações

- Incluir nas specs do painel de governança os fluxos correspondentes às Regras 2 e 3; testes automatizados que verifiquem as Regras 1, 4, 5 e 6 após cada operação de edição.
- Documentar no schema (ou em anexo) a chave natural de cada recurso bitemporal (Regra 8).

---

## Referências

- [ADR-001: Estratégia de Bitemporalidade no Banco de Dados do Classificador](adr-001_bitemporalidade.md)
- [ADR-003: Chave semântica e referência numérica](adr-003_chave-semantica.md)
- Seeds de exemplo: `docs/assets/seed_nivel_hierarquico_t1.csv` a `seed_nivel_hierarquico_t4.csv`, `docs/assets/seed_classificacao_t1v1.csv`, `seed_classificacao_t1v2.csv`
