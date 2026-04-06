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

O modelo de dados do Classificador adota bitemporalidade (ADR-001) e SCD-2, _append-only_ (novas linhas em vez de atualização _in place_). Em regra, os recursos possuem colunas `data_vigencia_inicio`, `data_vigencia_fim`, `data_registro_inicio` e `data_registro_fim` (valor sentinela `9999-12-31` para intervalos em aberto).

??? info "Por que formalizar regras gerais de governança?"
    Para suportar um painel de governança e fluxos de edição consistentes com auditoria e reprodutibilidade, é necessário formalizar **regras gerais** que definam:
      
      * o que significa "linha ativa" e quantas podem existir por entidade;
      * como o usuário escolhe o que editar;
      * os tipos de edição permitidos;
      * a sequência de operações (fechamento de registro e, quando aplicável, de vigência) e a garantia de que não haja alteração in place do conteúdo das linhas.

As regras a seguir foram derivadas de uma análise crítica de aderência ao modelo bitemporal, ao padrão SCD-2 e ao GSIM, tomando como referência exemplos de implementação constantes em `assets/referencias/exemplo_nivel_hierarquico_t*.csv`. Este ADR consolida essas diretrizes e explicita casos adicionais necessários à sua correta implementação e validação.


## Decisão

Adotar as **regras gerais de governança do banco** descritas abaixo, aplicáveis a todos os recursos gerenciados em tabelas bitemporais, modelo SCD‑2 (_append‑only_). 

Essas tabelas devem possuir campos de data da transação (_transaction time_), `data_registro_inicio`, `data_registro_fim`[^1], e o período de vigência (_valid time_), `data_vigencia_inicio`, `data_vigencia_fim`[^2]. 

A aplicação (painel de governança, APIs, comandos de carga) deve garantir conformidade com estas regras; validações e testes devem verificá‑las.

### Convenções preliminares

- **Entidade-objeto (entidade de negócio)**: em um sistema taxonômico como este, corresponde ao objeto efetivamente classificado ou registrado em cada tabela, cujos dados e metadados evoluem ao longo do tempo segundo a lógica *append-only*.
   
> Nesse contexto, aquilo que está sendo registrado ou classificado é identificado de duas formas complementares:

> - pela **chave artificial** do recurso (coluna `[nome-da-tabela]_ref`), utilizada para operações internas no banco de dados;
> - pela **chave natural (semântica)** (coluna `[nome-da-tabela]_id`), empregada para interação com o usuário e para estabelecer relações entre diferentes entidades (por meio de chaves estrangeiras).

??? info "Exemplo:"
    No banco de dados de Classificação (*Statistical Classification*, `schemas/classificacao.yaml`), que representa as diferentes versões da estrutura geral do classificador, a primeira versão registrada foi a da União.

    Essa versão recebeu:

    * **chave artificial**: `1`;
    * **chave semântica**: `CLASS-RECEITA-UNIAO-2001`.

    Assim, para referenciamento interno na própria tabela, utiliza-se `classificacao_ref = 1`; já para referenciamento em outras tabelas — privilegiando maior inteligibilidade e estabilidade semântica — utiliza-se `classificacao_id = CLASS-RECEITA-UNIAO-2001`.

- **Linha ativa**: linha em que `data_registro_fim` possui o **valor sentinela**, definido como `9999-12-31`, ou seja, o sistema ainda considera aquela "versão" como a "verdade atual" durante o respectivo intervalo de vigência.

- **Data da operação**: data em que a edição é registrada no sistema; será usada como `data_registro_inicio` de todas as novas linhas criadas na operação e como valor que fecha o `data_registro_fim` da linha que estava aberta.

---

### Regra 01 — Uma linha ativa por entidade-período de vigência

Deve haver **uma, e somente uma**, linha ativa (com `data_registro_fim` igual ao valor sentinela) para cada **par (entidade-objeto x período de vigência)**. 

Posto de outra forma, isso implica que para uma mesma entidade podem existir **várias** linhas ativas ao mesmo tempo, desde que cada uma corresponda a um **período de vigência distinto** (ex.: uma linha ativa para vigência 2002–2017 e outra para vigência 2016–9999 representa uma inconsistência, já que o período de 2016-2017 conviveram duas vigências ativas). 

Para uma **mesma entidade-objeto não pode haver mais de uma linha com `data_registro_fim` = sentinela**, isto é, com períodos de vigências concorrentes/sobrepostos.

---

### Regra 2 — Escolha da entidade e da linha/instância/registro a editar

Ao escolher editar um registro pré-existente, o usuário deve: 

  - (1) escolher **qual** classificação/entidade-objeto, identificada pela chave natural do recurso.

  - (2) em seguida, escolher **qual** linha/instância com valor sentinela em `data_registro_fim` será alvo da edição. Quando coexistem períodos de vigência distintos (versões ao longo do tempo), pode haver várias linhas ativas para a mesma entidade-objeto. A interface deve, portanto, listar apenas as linhas com `data_registro_fim` = sentinela para a entidade selecionada. A linha escolhida **não** será alterada in place; apenas `data_registro_fim` será fechado (Regra 04) e nova(s) linha(s) será(ão) inserida(s) conforme o tipo de edição (Regras 5 ou 6).

---

### Regra 3 — Tipo de atualização

Após a escolha da instância (entidade + linha ativa) a editar, o usuário deve ser **perguntado** sobre o tipo de edição, com as seguintes opções:

 - **Registrar nova vigência/edição da classificação** (A): o usuário está registrando um **novo período de vigência** (nova "versão" no mundo real). Nesse caso, são duas novas linhas/instâncias que devem ser acrescentadas ao banco: uma registrando o fim da vigência anterior (com `data_vigencia_fim` igual ao dia imediatamente anterior à `data_vigencia_inicio` do novo registro) e outra linha/instância registrando a nova vigência.

 - **Sobrescrever/corrigir vigência anterior** (B): o usuário está corrigindo o que o sistema registrou para o **mesmo** período de vigência (por exemplo, correção de atributos ou do próprio intervalo de vigência). Não se cria novo período de vigência no mundo real; apenas se atualiza o conhecimento do sistema sobre aquele período. Nesse caso, haverá o acréscimo de apenas uma nova linha ao banco, com `data_registro_fim` = valor sentinela, contendo as novas informações de vigência e metadados da classificação; o registro anterior terá `data_registro_fim` fechado na data da operação (`data_registro_inicio` da nova linha).

 - **Bloquear** (C): o usuário quer **encerrar a vigência** de uma classificação. Esse tipo de evento pressupõe uma classificação/entidade que esteja ativa (`data_vigencia_fim` = valor sentinela) e cujo período de vigência deva ser reduzido/encerrado. Nesse caso, além do fechamento do registro anterior (fechando `data_registro_fim`), insere‑se **uma única** nova linha de encerramento, com `data_registro_inicio` = data da operação, `data_registro_fim` = valor sentinela e `data_vigencia_fim` definida com valor anterior ao sentinela.

 - **Excluir** (D): o usuário quer tratar aquela classificação como se nunca tivesse surtido efeitos de vigência no universo orçamentário. Nesse caso, procede‑se à desativação da respectiva classificação/instância, fechando o `data_registro_fim` da linha ativa (valor sentinela).

Por padrão, o sistema deve assumir que o usuário deseja fazer o registro de nova vigência/edição da classificação (A).

Durante o processo de edição/ajustes deve ser permitido ao usuário alterar o tipo de atualização que deseja.

---

### Regra 04 — Data da transação e fechamento do registro da linha editada

**Independente** da escolha pelo tipo de atualização, a **data da operação**, que deverá ser a `data_registro_inicio` das novas linhas criadas, deve ser usada para **fechar** a `data_registro_fim` da linha/instância que o usuário escolheu editar. Ou seja: a linha que estava "aberta", com `data_registro_fim` = valor sentinela, passa a ter `data_registro_fim` = data da operação. 

Esta é a **única** alteração permitida em uma linha já existente (exceção ao append-only puro), todo o restante do conteúdo das linhas antigas permanece imutável. A implementação pode fazer isso por um único UPDATE apenas na coluna `data_registro_fim` da linha escolhida, ou por convenção de leitura: ex.: considerar "fechada" quando existir nova linha com mesmo "entidade-vigência" e `data_registro_inicio` = data da operação. 

Recomenda-se o UPDATE explícito para clareza e consistência em consultas.

---

### Regra 5 — Atualização para "registrar nova vigência/edição da classificação (A)"

Uma vez feita a escolha do tipo de atualização, caso opte por (A), isto é, caso não se altere o padrão do sistema, desconsideradas as datas de transação, o sistema deve recuperar e disponibilizar ao usuário todos os atributos da instância selecionada para edição, porém com valores pré-definidos para os seguintes campos:

>  **`data_vigencia_inicio`**: valor padrão, passível de ser editado pelo usuário, de **01/01/AAAA**, em que **AAAA** é o ano da operação de edição (ano da data de operação desta nova vigência). A justificativa é que a vigência de uma classificação orçamentária tem relevância sobretudo sob o viés do **ano fiscal**; o mês exato em que passou a vigorar tem menor peso para fins orçamentários. Como a informação de *quando* a classificação foi registrada no sistema permanece nas colunas de registro (`data_registro_inicio`), e não na vigência, assumir que toda nova vigência começa em **01 de janeiro** do ano correspondente (ao da edição ou ao indicado) é razoável e simplifica a interface, sem perda de rastreabilidade.

> **`data_vigencia_fim`**: valor padrão, passível de ser editado pelo usuário, conforme valor sentinela, `9999-12-31`.

Concluídas as atualizações, caso o usuário clique em "Salvar", os protocolos devem ser:

1. Verificar se o novo período de vigência dessa entidade-objeto vai **conflitar/sobrepor a outro período de vigência ativo** para essa mesma entidade-objeto que não o registro/instância que está sendo editada e, em caso afirmativo de conflito, impedir o registro no banco, informando qual(is) instância(s) tem(têm) período de vigência conflitante com a nova edição.
2. Verificar **se de fato houve alteração** de pelo menos um dos atributos da entidade-objeto em relação à edição anterior e, em caso negativo, impedir o registro e informar que não foi identificada nenhuma alteração na classificação.
3. Ultrapassadas a primeira e segunda etapas, **fechar** o `data_registro_fim` da linha que o usuário escolheu editar, com a data da operação (Regra 04).
4. **Inserir** uma linha de **encerramento da vigência anterior**: nova linha com os **mesmos** parâmetros da linha que estava sendo atualizada, antes da atualização, exceto:
   - `data_vigencia_fim` = dia imediatamente **anterior** ao `data_vigencia_inicio` do novo período de vigência que será registrado;
   - `data_registro_inicio` = data da operação;
   - `data_registro_fim` = valor sentinela.
5. Se, e somente se, o período de vigência da linha de "encerramento da vigência anterior" **não for igual** ao período da vigência da classificação/instância que está sendo editada, **inserir** uma linha da **nova vigência**: nova linha com os **novos** parâmetros da classificação/entidade-objeto, com data de vigência conforme definidos pelo usuário em última lugar, sendo a `data_registro_inicio` = data da operação e `data_registro_fim` = valor sentinela. Caso a vigência anterior seja igual ao novo período de vigência, essa segunda linha "nova vigência" não deve ser registrada.

  
Assim, caso haja alteração no período de vigência inicial, após a operação haverá duas linhas ativas (sentinela) para a mesma entidade: uma para o período de vigência que foi encerrado (até o dia anterior ao início do novo período) e outra para o novo período.  

Caso os períodos de vigência da nova versão e da versão anterior seja idênticos, o comportamento deve ser tal como prescrito na Regra 05, com acréscimo de apenas uma nova linha com a nova vigência.


??? info "Exemplo prático (registrar nova vigência):"
    Suponha uma classificação com vigência atual 2002-01-01 — 9999-12-31 (linha ativa). O usuário registra uma nova vigência que começará em 2018-01-01. Sucessão de eventos:

    1. Data da operação = 2026-02-10 (exemplo).
    2. Fecha-se a linha ativa original: define-se `data_registro_fim = 2026-02-10` nessa linha.
    3. Insere-se uma linha de encerramento da vigência anterior com:
       - `data_vigencia_inicio = 2002-01-01` (mesmo que antes);
       - `data_vigencia_fim = 2017-12-31` (dia anterior ao novo início);
       - `data_registro_inicio = 2026-02-10`, `data_registro_fim = 9999-12-31`.
    4. Insere-se a linha da nova vigência:
       - `data_vigencia_inicio = 2018-01-01`;
       - `data_vigencia_fim = 9999-12-31` (ou outro valor indicado);
       - `data_registro_inicio = 2026-02-10`, `data_registro_fim = 9999-12-31`.

    Esse fluxo preserva o histórico e torna explícito o fim da vigência anterior e o início da nova.

---

### Regra 6 — Atualização para "sobrescrever/corrigir vigência anterior (B)"

Caso opte por (B), desconsideradas as datas de transação, o sistema deve recuperar e disponibilizar ao usuário todos os atributos da instância selecionada (para revisão e edição), com `data_vigencia_inicio` e `data_vigencia_fim` pré‑preenchidas exatamente conforme constantes na instância/registro selecionado para edição.

Concluídas as atualizações, caso o usuário clique em "Salvar", os protocolos devem ser:

1. Verificar se o novo período de vigência dessa entidade-objeto vai **conflitar/sobrepor a outro período de vigência ativo** para essa mesma entidade-objeto que não o registro/instância que está sendo editada e, em caso afirmativo de conflito, impedir o registro no banco, informando qual(is) instância(s) tem(têm) período de vigência conflitante com a nova edição.
2. Verificar **se de fato houve alteração** de pelo menos um dos atributos da entidade-objeto em relação à edição anterior e, em caso negativo, impedir o registro e informar que não foi identificada nenhuma alteração na classificação.
3. Ultrapassadas a primeira e segunda etapas, **fechar** o `data_registro_fim` da linha escolhida para atualização com a data da operação (Regra 04).
4. **Inserir uma única** nova linha/instância no banco com os parâmetros corrigidos informados pelo usuário, com `data_registro_inicio` = data da operação e `data_registro_fim` = valor sentinela.

Observação: no tipo de atualização de sobrescrição da vigência anterior, o usuário pode querer, inclusive, reduzir ou expandir o período de vigência anterior. Dessa forma, o novo intervalo de vigência (`data_vigencia_inicio`, `data_vigencia_fim`) pode tanto ser o mesmo do anterior, como maior ou menor.

---

### Regra 7 - Atualização para "bloquear (C)"

Quando o usuário optar por **bloquear** (encerrar a vigência de uma classificação) o objetivo é tornar explícito o fim do *valid time* dessa instância, sem criar uma nova vigência subsequente. Aplica‑se quando se deseja que a classificação deixe de produzir efeitos a partir de uma data específica.

Procedimentos e validações:

1. Identificar a linha ativa selecionada (chave da entidade + `data_registro_fim` = sentinela). Se não houver linha ativa, abortar e informar ao usuário.
2. Receber a **data de encerramento de vigência** proposta (`data_vigencia_fim_nova`) e validar: `data_vigencia_inicio` ≤ `data_vigencia_fim_nova` < sentinela. Caso inválida, rejeitar.
3. Verificar se o encerramento criaria sobreposição com outras vigências da mesma entidade; se houver conflito, rejeitar e listar as instâncias conflitantes.
4. Fechar o `data_registro_fim` da linha escolhida com a **data da operação** (Regra 4).
5. Inserir **uma nova linha de encerramento** com os mesmos atributos da linha anterior, exceto:
   - `data_vigencia_fim` = `data_vigencia_fim_nova`;
   - `data_registro_inicio` = data da operação;
   - `data_registro_fim` = valor sentinela.

---

??? Info "Exemplo prático (bloquear vigência):"
    Considere uma classificação atualmente ativa com vigência `2002-01-01` — `9999-12-31`. O usuário deseja encerrar a vigência em `2017-12-31`. Procedimento:
 
    1. Data da operação = 2026-02-10.
    2. Fecha-se a linha ativa original: `data_registro_fim = 2026-02-10`.
    3. Insere-se uma linha de encerramento com `data_vigencia_fim = 2017-12-31`, `data_registro_inicio = 2026-02-10`, `data_registro_fim = 9999-12-31`.
    4. Não se insere nova vigência posterior.
 
    O resultado deixa explícito que a classificação vigorou até 2017-12-31 e não tem vigência ativa subsequente.

---

### Regra 8 - Atualização para "excluir (D)"

A operação **excluir** tem semântica de anulação de efeito: a instância passa a ser considerada como não tendo surtido efeitos no domínio orçamentário. Trata‑se de uma alteração do *transaction time* que preserva o histórico para fins de auditoria.

Procedimentos e validações:

1. Identificar a linha ativa a ser excluída (chave da entidade + `data_registro_fim` = sentinela). Se não existir, abortar.
2. Verificar integridade referencial: se há registros dependentes cuja existência pressupõe a vigência desta instância, impedir a exclusão e listar conflitos, ou exigir confirmação explícita do usuário para aplicar ações encadeadas (reatribuição/cascade).
3. Fechar o `data_registro_fim` da linha escolhida com a **data da operação** (Regra 4). Não inserir novas linhas de vigência.
4. Opcionalmente, registrar metadados de auditoria (`motivo_exclusao`, `usuario_exclusao`) para rastreabilidade.

Efeitos:

- A instância deixa de aparecer em consultas de estado corrente; o histórico permanece com `data_registro_fim` fechado.  
- Exclusão não remove dados históricos; preserva‑se rastreabilidade e prova de decisão.

??? Info "Exemplo prático (excluir / anular efeito):"
    Suponha que uma classificação foi cadastrada por engano e nunca deveria ter produzido efeitos. Data da operação = 2026-02-10.
 
    1. Fecha-se a linha ativa: `data_registro_fim = 2026-02-10`.
    2. Opcionalmente, grava-se metadado de auditoria: `motivo_exclusao = "cadastrado por engano"`, `usuario_exclusao = "analistaX"`.
    3. Registros dependentes devem ser verificados; se existirem, bloquear a exclusão até resolução.
 
    Após a operação, a instância não aparece em consultas correntes; o histórico permanece para auditoria.

---

### Regra 9 — Validações de integridade temporal

- Para qualquer nova linha: `data_vigencia_inicio` ≤ `data_vigencia_fim` (considerando valor sentinela como "infinito"); `data_registro_inicio` ≤ `data_registro_fim`.
- No fluxo "registrar nova vigência", o `data_vigencia_inicio` da nova linha deve ser **posterior** ao `data_vigencia_fim` da linha de encerramento (ou imediatamente seguinte, sem sobreposição). Como padrão, `data_vigencia_fim` da linha de encerramento deve ser exatamente o dia anterior ao `data_vigencia_inicio` da nova vigência.
- A aplicação deve garantir que, após cada operação de edição, não exista mais de uma linha ativa para o mesmo "entidade-objeto"-"período de vigência", conforme Regra 01.

---

### Regra 10 — Escopo por recurso

**Tabelas bitemporais** (ex.: `nivel_hierarquico`, `classificacao`, `versao_classificacao`, `item_classificacao`): em todas elas vale a metodologia **append-only** (SCD-2). A entidade-objeto é identificada pela **chave artificial** da própria tabela, ou seja, pela coluna `[nome-da-tabela]_ref`. Todas devem respeitar a regra central de que **não pode haver períodos de vigência sobrepostos para uma mesma entidade-objeto**, bem como as Regras 1 a 7 desta ADR. 

**Tabelas com modelo temporal simples** (apenas vigência, sem colunas de registro de transação): seguem o modelo **SCD-1**, com **alteração _in-place_**. Ou seja, atualizações modificam a linha existente, sem append-only nem múltiplas linhas por entidade para um mesmo período. Exemplo: recurso  `base_legal_tecnica` (colunas `data_vigencia_inicio` e `data_vigencia_fim`, sem `data_registro_*`). As Regras 1 a 7 desta ADR **não se aplicam** a esses recursos; a governança e a interface de edição devem tratar explicitamente o modelo SCD-1 quando houver esse tipo de tabela.

---

### Recomendações de UX (para a interface de edição)

As recomendações abaixo são essenciais para reduzir erros do usuário e preservar a integridade temporal no banco:

- Exigir seleção explícita do **tipo de edição** (A | B | C | D) antes de permitir alterações; apresentar breve descrição dos impactos e link para esta ADR.
- Exibir, antes da confirmação, a **pré-visualização (dry-run)** das alterações propostas: linhas que serão fechadas e novas linhas que serão criadas, com todas as datas e campos alterados visíveis.
- Mostrar claramente a **lista de linhas ativas** para a entidade selecionada (com `data_registro_inicio`, `data_vigencia_inicio`, `data_vigencia_fim`) para que o usuário confirme a instância correta.
- Detectar e **bloquear automaticamente** alterações que gerariam sobreposição de vigência; quando houver conflito, apresentar as instâncias conflitantes e orientação para resolução.
- Ao escolher **excluir (D)**, exigir confirmação explícita, preenchimento de motivo para auditoria e exibição dos impactos (dependências e consequências).
- Para operações de **bloquear (C)** e **nova vigência (A)**, mostrar impacto em registros dependentes (itens, variantes, versões) e exigir resolução prévia ou confirmação explícita do usuário.
- Registrar logs de auditoria estruturados (quem, quando, tipo de operação, motivo) e disponibilizá‑los em painel de auditoria ou exportação.
- Fornecer mensagens contextuais e tooltips que expliquem diferença entre `data_vigencia` e `data_registro`.

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
- A exceção de atualizar apenas `data_registro_fim` (Regra 04) deve ser documentada e implementada com cuidado para não abrir espaço a outros updates in place.

### Mitigações

- Incluir nas specs do painel de governança os fluxos correspondentes às Regras 2 e 3; testes automatizados que verifiquem as Regras 1, 4, 5 e 6 após cada operação de edição.
- Documentar no schema (ou em anexo) a chave natural de cada recurso bitemporal (Regra 8).

---

[^1]: Por **"transaction time"** (data de registro) entende‑se o intervalo durante o qual o sistema *conhecia* a informação — isto é, a data em que a alteração foi registrada no sistema (registro/transação).
[^2]: Por **"valid time"** (vigência) entende‑se a data ou período em que um código/classificação produz efeitos no domínio orçamentário — isto é, o intervalo em que a classificação estava disponível para rotular/classificar eventos orçamentários. Referências [ADR-001: Estratégia de Bitemporalidade no Banco de Dados do Classificador](adr-001_bitemporalidade.md) e  [ADR-003: Chave semântica e referência numérica](adr-003_chave-semantica.md)
