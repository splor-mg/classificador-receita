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

O modelo de dados do Classificador adota bitemporalidade (ADR-001) e SCD-2, append-only (novas linhas em vez de atualização in place). Em regra, os recursos possuem colunas `data_vigencia_inicio`, `data_vigencia_fim`, `data_registro_inicio` e `data_registro_fim` (valor sentinela `9999-12-31` para intervalos em aberto). Para suportar um painel de governança e fluxos de edição consistentes com auditoria e reprodutibilidade, é necessário formalizar **regras gerais** que definam: (1) o que significa "linha ativa" e quantas podem existir por entidade; (2) como o usuário escolhe o que editar; (3) os tipos de edição permitidos; (4) a sequência de operações (fechamento de registro e, quando aplicável, de vigência) e a garantia de que não haja alteração in place do conteúdo das linhas.

As regras abaixo foram auferidas a partir dos exemplos trabalhados nos seeds (ex.: `seed_nivel_hierarquico_t1` a `t4`, `seed_classificacao_t1v1` e `t1v2`) e da análise crítica de adequação ao modelo bitemporal, SCD Type 2 e GSIM. Este ADR consolida essas regras e explicita casos adicionais necessários para implementação e validação.

## Decisão

Adotar as **regras gerais de governança do banco** descritas abaixo, aplicáveis a todos os recursos gerenciados em tabelas bitemporais, modelo SCD-2 (_append only_). Essas tabelas devem possuir data da transação (que representa a data de conhecimento sobre a classificação,  de registro no sistema, ou mais precisamente, período em que o sistema conhecia daquela informação), chamadas `data_registro_inicio` e `data_registro_fim`, bem como possuem data de vigência (data em que um código pode surtir efeitos no mundo orçamentário, isto é, período em que um código/classificação estava disponível para rotular/classificar em evento orçamentário). A aplicação (painel de governança, APIs, comandos de carga) deve garantir conformidade com estas regras; validações e testes devem verificá-las.

### Convenções preliminares

- **Entidade-objeto (entidade de negócio)**: identificada pela **chave artificial** do recurso (coluna `[nome-da-tabela]_ref`) para fins de operações no banco, e identificada pela **chave natural** (semântica) para fins de iteração com ou usuário. Exemplos: em `nivel_hierarquico`, a entidade-objeto é retradada em `nivel_ref`; em `classificacao`, a entidade-objeto é identificada por `classificacao_ref`. 
- **Linha ativa**: linha em que `data_registro_fim` possui o **valor sentinela**, definido como `9999-12-31`, ou seja, o sistema ainda considera aquela "versão" como a "verdade atual" durante o respectivo intervalo de vigência.
- **Data da operação**: data em que a edição é registrada no sistema; será usada como `data_registro_inicio` de todas as novas linhas criadas na operação e como valor que fecha o `data_registro_fim` da linha que estava aberta.

---

### Regra 1 — Uma linha ativa por (entidade, período de vigência)

Deve haver **uma, e somente uma**, linha ativa (com `data_registro_fim` igual ao valor sentinela) para cada **par (entidade-objeto, período de vigência)**. Ou seja: para uma mesma entidade podem existir **várias** linhas ativas ao mesmo tempo, desde que cada uma corresponda a um **período de vigência distinto** (ex.: uma linha ativa para vigência 2002–2017 e outra para vigência 2016–9999 representa uma inconsistência, já que o período de 2016-2017 conviveram duas vigências ativas). Para um mesmo entidade-objeto não pode haver mais de uma linha com `data_registro_fim` = sentinela com períodos de vigências concorrentes/sobrepostos.

---

### Regra 2 — Escolha da entidade e da linha a editar

Ao escolher editar um registro pré-existente, o usuário deve: 

  - (1) escolher **qual** classificação/entidade-objeto, identificada pela chave natural do recurso.

  - (2) em seguida, escolher **qual** linha/isntância com valor sentinela em `data_registro_fim` será alvo da edição, uma vez que, quando há período de vigência diferentes (leia-se diferentes versões ao longo do tempo), espera-se haver mais de uma linha/instância ativa para aquela entidade-objeto. A interface deve listar,portanto, apenas linhas com `data_registro_fim` = sentinela para a entidade selecionada. A linha escolhida **não** será alterada in place; ela terá apenas a coluna/atributo `data_registro_fim` fechado (Regra 4), e nova(s) linha(s) será(ão) inserida(s) conforme o tipo de edição (Regras 5 ou 6).

O sistema deve recuperar e disponibilizar ao usuário todos os atributos da instância selecionada (para revisão e edição).

---

### Regra 3 — Tipo de edição (pergunta obrigatória ao usuário)

Após a escolha da instância (entidade + linha ativa) a editar, o usuário deve ser **perguntado** sobre o tipo de edição, com duas opções:

- **Sobrescrever/corrigir vigência anterior**: o usuário está corrigindo o que o sistema registrou para o **mesmo** período de vigência (ex.: correção de atributos ou do próprio intervalo de vigência). Não se cria novo período de vigência no mundo real; apenas se atualiza o conhecimento do sistema sobre aquele período. Nesse caso, haverá o acréscimo de apenas umas uma nova linha, com `data_registro_fim`= valor sentinela, com as novas informações de vigência e metadados da classificação.

- **Registrar nova vigência/edição da classificação**: o usuário está registrando um **novo** período de vigência (nova "versão" no mundo real). Nesse caso, são duas novas linhas/instâncias que devem ser acrescentadas ao banco, uma registrando o fim da vigência anterior, com `data_vigencia_fim` equivalente ao dia imediatametne anterior à `data_vigencia_inicio` do novo registro, e outra linha/instância registrando a nova vigência.


---

### Regra 4 — Fechamento do registro da linha editada (sempre)

**Independente** da escolha pelo tipo de edição, a **data da operação** (que será a `data_registro_inicio` das novas linhas criadas) deve ser usada para **fechar** o `data_registro_fim` da linha/instância que o usuário escolheu editar. Ou seja: a linha que estava "aberta" (com `data_registro_fim` = sentinela) passa a ter `data_registro_fim` = data da operação. Esta é a **única** alteração permitida em uma linha já existente (exceção ao append-only puro); todo o restante do conteúdo das linhas antigas permanece imutável. A implementação pode fazer isso por um único UPDATE apenas na coluna `data_registro_fim` da linha escolhida, ou por convenção de leitura (considerar "fechada" quando existir nova linha com mesmo (entidade, vigência) e `data_registro_inicio` = data da operação); recomenda-se o UPDATE explícito para clareza e consistência em consultas.

---

### Regra 5 — Edição "sobrescrever/corrigir vigência anterior"

Quando o usuário optar por **sobrescrever/corrigir vigência anterior**:

1. Fechar o `data_registro_fim` da linha escolhida com a data da operação (Regra 4).
2. **Inserir uma única** nova linha/instância com os parâmetros corrigidos informados pelo usuário, com `data_registro_inicio` = data da operação e `data_registro_fim` = valor sentinela. Observação: intervalo de vigência (`data_vigencia_inicio`, `data_vigencia_fim`) pode ser o mesmo da linha anterior ou corrigido (ex.: encerramento antecipado da vigência).

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

   **Default para `data_vigencia_inicio`**: o sistema deve oferecer como valor padrão **01/01/AAAA**, em que *AAAA* é o ano da operação de edição (ano da data de registro desta nova vigência) ou o ano explicitamente indicado pelo usuário. A justificativa é que a vigência de uma classificação orçamentária tem relevância sobretudo em termos de **ano fiscal**; o mês exato em que passou a vigorar tem menor peso para fins orçamentários. Como a informação de *quando* a classificação foi registrada no sistema permanece nas colunas de registro (`data_registro_inicio`), e não na vigência, assumir que toda nova vigência começa em **01 de janeiro** do ano correspondente (ao da edição ou ao indicado) é razoável e simplifica a interface, sem perda de rastreabilidade.

Assim, após a operação haverá duas linhas ativas (sentinela) para a mesma entidade: uma para o período de vigência que foi encerrado (até o dia anterior ao início do novo período) e outra para o novo período. Isso está em conformidade com a Regra 1, pois os períodos de vigência são distintos.

**Ordem operacional recomendada**: (1) fechar a linha atual; (2) inserir a linha de encerramento da vigência anterior; (3) inserir a linha da nova vigência. A data da operação deve ser a mesma em todas as novas linhas.

---

### Regra 7 — Validações de integridade temporal

- Para qualquer nova linha: `data_vigencia_inicio` ≤ `data_vigencia_fim` (considerando valor sentinela como "infinito"); `data_registro_inicio` ≤ `data_registro_fim`.
- No fluxo "registrar nova vigência", o `data_vigencia_inicio` da nova linha deve ser **posterior** ao `data_vigencia_fim` da linha de encerramento (ou imediatamente seguinte, sem sobreposição). Como padrão, `data_vigencia_fim` da linha de encerramento deve ser exatamente o dia anterior ao `data_vigencia_inicio` da nova vigência.
- A aplicação deve garantir que, após cada operação de edição, não exista mais de uma linha ativa para o mesmo (entidade-objeto, período de vigência), conforme Regra 1.

---

### Regra 8 — Escopo por recurso

**Tabelas bitemporais** (ex.: `nivel_hierarquico`, `classificacao`, `versao_classificacao`, `item_classificacao`): em todas elas vale a metodologia **append-only** (SCD-2). A entidade-objeto é identificada pela **chave artificial** da própria tabela, ou seja, pela coluna `[nome-da-tabela]_ref`. Todas devem respeitar a regra central de que **não pode haver períodos de vigência sobrepostos para uma mesma entidade-objeto**, bem como as Regras 1 a 7 desta ADR. 

**Tabelas com modelo temporal simples** (apenas vigência, sem colunas de registro de transação): seguem o modelo **SCD-1**, com **alteração in-place**. Ou seja, atualizações modificam a linha existente, sem append-only nem múltiplas linhas por entidade para um mesmo período. Exemplo: recurso cujo schema é o de `base_legal_tecnica` (colunas `data_vigencia_inicio` e `data_vigencia_fim`, sem `data_registro_*`). As Regras 1 a 7 desta ADR **não se aplicam** a esses recursos; a governança e a interface de edição devem tratar explicitamente o modelo SCD-1 quando houver esse tipo de tabela.

---

## Alternativas Consideradas

Esta ADR documenta **comportamentos que o sistema assume ao operacionalizar** o banco bitemporal. As alternativas abaixo são as que foram consideradas em relação a esses comportamentos.

### Alternativa 1: Operar sem parâmetro de tipo de edição

- **Descrição**: Um único fluxo de edição (sempre fechar a linha atual e inserir uma nova), sem exigir que o usuário ou o chamador declare se a operação é "correção do mesmo período" ou "registro de nova vigência". O sistema poderia inferir o comportamento ou tratar tudo da mesma forma.
- **Prós**: Interface ou API mais simples; menos um parâmetro obrigatório.
- **Contras**: Sem o parâmetro, não há como garantir o encerramento explícito da vigência anterior quando a mudança é de fato uma nova vigência no mundo orçamentário. O histórico de *valid time* deixa de refletir corretamente a realidade orçamentária: períodos de vigência podem ficar sobrepostos, ausentes ou ambíguos.
- **Razão da rejeição**: **Sem o parâmetro, corre-se o risco de corromper a estrutura de vigência esperada para a realidade orçamentária.** A distinção entre "sobrescrever/corrigir" e "registrar nova vigência" é necessária para que o banco mantenha integridade temporal e correspondência com os períodos em que cada classificação vigorou de fato.

### Alternativa 2: Não documentar os comportamentos (apenas implementar)

- **Descrição**: Implementar as regras (dois tipos de edição, fechamento de registro, encerramento de vigência) sem formalizá-las em ADR; manter apenas exemplos em seeds e documentação informal.
- **Prós**: Menos documentação a manter.
- **Contras**: Comportamentos críticos ficam implícitos; painel, APIs e validações podem divergir; auditoria e conformidade tornam-se difíceis de verificar. Ao não formalizar as regras, deixa-se de externalizar o conhecimento sobre como operar o banco e qual é sua lógica, permanecendo esse conhecimento apenas em linguagem e artefatos mais acessíveis a quem lida com código e programação.
- **Razão da rejeição**: A operacionalização exige que os comportamentos assumidos pelo sistema estejam explícitos e estáveis, para implementação consistente e validação.

---

## Consequências

### Positivas

- Regras únicas e canônicas para implementação do painel de governança, validações e testes.
- Alinhamento explícito com ADR-001 (bitemporalidade, append-only) e com os exemplos já validados.
- Rastreabilidade e auditoria preservadas; "uma linha ativa por (entidade-objeto, período de vigência)" evita ambiguidade na leitura do estado corrente.

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
