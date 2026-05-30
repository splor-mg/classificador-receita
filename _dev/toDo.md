----------------------------------------------------------------------------------------------------
# lista 

- **itemClassificacao** - formulário de criação

  - **assistênte de vigência** - verificar criação de protocolo auxiliar para identificar vigência, por período, ou por versão. 
    O que eu pensei foi em criar um script python, chamado `get_valid_code.py`. Deveria ser possível passar como argumento para essa função, ano, data, ou 2 anos ou duas data, ou a versão. 

    Esse protocolo poderia ser utilizado parar criar filtro nas changelists para indentificar vigências  vigência por ano, pegando todos os registros ativos, com vigência. 
    Pensei que poderia ser um "get vigência", cujo comportamento padrão poderia ser o de obter o registro vigênte para cada ano, conforme ativo em dias atuais. No entanto, para além disso, deveria ser possível esse "get vigência" poder ser instruído com argumento de data de registro. Isto é, ele somente consideria o stado do banco conforme atualizado até data x. Para tanto, o script deveria conseguir converter datas de fim de registro em dia futuro em relação à data x, deve ser assumido como se estivesse com "valor sentinela". Assim, resconstituira o estado do banco
    Poderia haver o registro de um campo na parte superior da changelist, chamado Vigência. Um dropdown seria apenas para ano e haveria um campo de data ao lado direito, para "conforme data:...". Caso apenas o campo ano estiver selecionado, ele vai considerar que é o léxico vigente par ao ano informado conforme hoje. Caso o campo conforme data... esteja preenchido, ele deve recuperar o que estava vigente conforme a data informada. Deveria haver pelo menos 3 padrões, fechamento; LDO, LOA, e uma oportunidade de informar. Ao rodar o protocolo de "filtragem" no banco de dados, por exemplo, sem o preenchimento do campo de "conforme data", deve informar que foram selecionados os códigos vigentes em conformidade com seu registro/versão mais recente.

    data início de vigência <= 31/12/<ANO-SELECIONADO>
    data de fim de vigêcia >= 01/01/<ANO-SELECIONADO>
    data de fim de registro = SENTINELA ou instância com maior data de fim de registro, desde que > 31/12/<ANO-SELECIONADO>

    ao lado desse campo de vigência, ele poderia ser 3 na verdade: Ano, Data e Versão. O usuário poderia selecionar cada um dos campo. O campo data, para as opções padrão, deve adatar conforme ano esperado, ou assumir ano corrente. O campo de versão deve ser um campo de dropdown com a lista de versões já publicadas, e eventualmente restritas àquelas compatíveis ao ANO-SELECIONADO. Pensar se no versionamento coloca-se ano ou não
  
  - **mensagem de confirmação de criação** - uma janela pop-up de confirmação de criação, com dados resumidos do que está sendo criado

  - **mensagem de confirmação para sair** de formulário sujo - hoje não pergunta se o usuário clicar para ir, por exemplo, para outra changelist

  - **filtros de FK** - quando se remove filtros em lupa de seleção de FK, não está sendo mais possível selecionar de fato a FK. Clica-se na FK desejada, e nada acontece.

  - **erro nome dedutora** - Tentativa criar: 9112520403000 Nome gerado: Dedução Rec. - ITCD - DA-MJM - ITCD - Imposto sobre o Patrimônio - Nome esperado: Dedução Rec. - ITCD - DA-MJM -

  - **assistente de nomenclatura** - garantir que não haja espaços múltiplos (mais de um espaço entre palavras ou ao final), bem como padrão de maiúsculas (primeira letra maiúsculas, desde que não seja conectivos)
      No code_name_messages.py, implementar limpeza do nome da classificação, removendo espaçamentos múltiplos tanto no meio, como nas extremidades

  - **furo de vigência de FK** - verificar se protocolo permite registrar itemClassificação, mesmo tendo informado campo Classificação, classificacao_id, FK, com vigência que não compreende a vigência que constou nos campos de data de vigência do formulário. Verificar teste de vigência contígua. Além disso, colocar como lista de validações de bancos se há consistência de vigências relacionais (FK-PK).

  - **salto de nível** - implementar regra que alerte caso o usuário esteja registrando código que "salte dígito" em relação ao último código implementado... caso o outro não exista - perguntar DCAF se quer impedir criação de código que salte um dígito ou não
      no submit, garantir/mensagem pop-up de alerta -  que o código que vai ser salvo, não presenta, dentre os registros de mesmo item do pai, um pulo maior que um. por exemplo, o último item salvo com item pai 1151, foi 115102, garantir que não crie 115104 antes de 115103

  - **verificar ajuste de vigência** - considerando o bloqueio de no delete para caso relacionamento ORM existir, verificar uma situação de correção de registro no qual o usuário tentou fazer uma sobreposição de vigência, porém registrou uma "quebra de vigência", com o início de nova vigênica. Quando quiser corrigir esse lançamento, o que o usuário deve fazer? Deve excluir a nova vigência e então corrigir a vigência do registro anterior?

  - **mensagem de alerta de acoplamento** - verificar refinamento da regra de mensagem de alerta para quando há juntção de cod com nivel de uma classificação e mãe com nível pertencente a outra classificação
  A mensagem atual é: "Não existe item mãe vigente para a classificação selecionada, porém existe para CLASS-RECEITA-UNIAO-2018. Certifique-se de que a classificação selecionada está correta."

  - **botão limpar** - o botão falha e não limpa o campo de código canônico quando se chega na página pelo comando "+ Criar Código Filho" a partir da tela change.

  - **consistência FK** - ajustar a construção do link ao lado da lupa de uma FK quando a página de criação/item filho é criado a partir do botão "+Criar Código Filho", uma vez que atualmente está apontando para registro específico.

  - **erro vigência item mãe** - na simulação de preencher código "1.1.1.2.52.0.1.00.000" para ser criado, no momento em que se seleciona `classificacao_id`, há mensagem de que "Não existe item mãe vigente para a classificação selecionada, porém existe para CLASS-RECEITA-UNIAO-2018. Certifique-se de que a classificação selecionada está correta.", mesmo existindo o código "1.1.1.2.52.0.0.00.000"
  
  - **regra de consistência** - nomes - não poder haver dois nomes iguais, no mesmo Nível, com mesmo item_pai, na mesma vigência

  - **definições .env** - considerando que atualmente temos um export, que faz um export automático para o CSV, bem como lista de abreviações que podem ou não serem usadas, verificar implementação de "usos-padrão" para cada um deles, bem como uma forma de configurar para que não funcionem no .env.

- **Importar Bases**
criar protocolo de incorporação/importação de bases
  - tratamento Excel/csv por ano
  - tratamento de campos para modular formatação de texto, por exemplo, ao invés de Caixa Alta, especialmente os nomes devem passar para o modelo de primeira letra maiúscula, à exceção dos conectivos
  - identificação de máscara para preenchimento de valores derivados de 
  - gerar script que vai considerar alteração nos metadados

- **itemClassificacao** - opção de gerar automaticamente códigos correlatos - estruturas fixas
  - quando estiver criando uma receita, verificar implementação de opção a geração de registros de estrutura fixa automaticamente, tal como o são os Tipos de Receita, Receita Dedutora e Receita Intraorçamentária
  - uma das alternativas poderia ser criar uma tabela bitemporal para EstruturasFixas. Nessa, você poderia cadastrar todos os valores de estrutura fixa por nível da estrutura. Por exemplo, poderia haver o registro para a estrutura de NIVEL-7, toda vez que seu código for 1, ele vai ter um nome/descrição. Ela seria bitemporal, para poder registrar sua evolução ao longo do mtepmo
  - além de, ao criar um itemClassificacao, poder gerar automaticamente um registro, deve ser pensada alternativa para, aquele registro que antes não era replicado automaticamente, poder ser. 
  - considero raozável pensar que exista uma necessidade de harmonização de comportamentos entre estruturas irmãs de comportamento "espelahado", tal como o Tipo da Receita. O que poderíamos fazer para garantir que esses códigos tenham algum vínculo? mapear isso em algum banco?
  - quando o usuário desejar criar uma subdivisão, uma vez garantida a consistência de ajustes mencionados acima, seria desejável um protocolo de alteração de um registro de alteração da classificação mãe de detalhe para matriz?

- **itemClassificacao** - changelist
  - a ferramenta de busca do Django não está encontrando match quando o código, ou parte dele, é informado com a mácara/pontos separadores de campos

- **itemClassificacao** - alteração de registro entre Matriz/Detalhe
  - considerando que na estrutura hierárquica há regras de negócio inerentes à natureza matricial e capilaridade de um código, é necessário revisar quais protocolos de consistência e eventuais travas/guardrails são necessários para garantir consistência

- **itemClassificacao** - códigos de espelhamento
  - Atualmente existe uma regra de negócio que prevê a criação de categorias de códigos que se baseiam no espelhamento de um código já existente, como é o caso das receitas intraorçamentárias e das dedutoras. Qual o melhor tratamento conferir para essas receitas no banco de dados?
  Acrescentar coluna em itemClassificacao para identificar qual é a intra/dedutora associada? 
  No processo de criação de uma nova codificação, perguntar se tem ou não intra/dedudora?
  Como fazer para editar esse parâmetro de espelhamento em registro?
  Criar um issue de criações automatizadas de intra/dedutora?

- **nivelHierarquico**
  - verificar travamento da semântica de nível (ex.: NIVEL-1), já que necessariamente ela vai ser 1, 2, 3, 4... Pensar em uma forma de não ter NIVEL-2 associado a "Número do Nível" diferente de 2, por exemplo
  - na changelist, alterar barra de filtro, no filtro "Por Classificação", que está repetindo entidades idênticas

- **ListaAbreviacoes - Abreviaturas**
  - remover ITCD -> HY
  - Revisar o atual protocolo automatizado de atualização das abreviações e a pertinência das abreviações geradas
  - botão cancelar
  - Verificar, de forma mais ampla, criação de nomes de convênios
  - Verificar edição para permitir "reativar" e alterar conteúdo/valor da abreviação
  - Implementar um "on/off" na changelist, para poder ativar e desativar registro sem precisar entrar no registro
  - incluir abreviação "MDE" - Manutenção e Desenvolvimento do Ensino
  - ? fazer uma flag -para --print-conflicts-resolve-hard para forçar atualização conforme mais recente
  - Adaptação para, no processo de abreviação, quando o último termo após o traço do nome do item pai, for exatamente o primerio termo antes do primeiro traço do nome do item filho, isso quer dizer que o nome do item pai inteiro, dever ser registrado como sendo abreviado pelo nome do primeiro termo antes do primeiro traço no nome do item filho, ou o último termo, após último traço no nome do item pai:

   Exemplo

   Outras Transf. Convênios União Entidades - Princ. - Agropecuária -> Agropecuária
   1.7.1.7.99.0.1.05.000	Outras Transf. Convênios União Entidades - Princ. - Agropecuária
   1.7.1.7.99.0.1.05.001	Agropecuária - Secretaria de Agricultura Familiar e Cooperativismo do Governo Federal

- **DJANGO**
  - na navegação para próximo irmão/mãe, deve-se, uma vez voltado na hierarquia, tentar buscar os irmãos de mesmo nível em mãe subsequente. 
  - implementar protocolo de navegação para as demais changelists. Verificar aumento de escopo da atual regra de forma a permitir navegação plana se código não for hierárquico.
  - **caixas de diálogo** - substituir o primeiro padrão implementado de `window.confirm()` nativo do navegador (que renderiza o modal genérico com o título "127.0.0.1:8000 diz" e botões padrão "OK / Cancelar") por um **modal HTML estilizado**, no mesmo padrão visual dos demais modais já implementados no gerenciador (ex.: confirmação bitemporal, navegação por blur, navegação estrutural). O novo modal deve preservar a regra de negócio atual — alertar o usuário sobre perda de alterações ao sair da página/formulário sem salvar — mas com título, mensagem e rótulos de botões customizados (ex.: "Sair sem salvar" / "Continuar editando"), além de manter a coerência visual e de acessibilidade com os demais diálogos do sistema.
  - Na tela de edição (change), uma sugestão a avaliar seria, ao cliar no botão "Histórico" que navegasse para a correspondente changelist e filtrasse todos os registros ativos do correspondente código

- **Validações de banco**
  - **códigos por espelhamento** - protcolo para garantir que as vigências sobrepostas de um código com seu espelhamento estejam em conformidade com a "replicação" esperada para o espelhamento, especialmente quanto ao nome do espelho.
  - verificar 2 nomes iguais com vigências sobrepostas em códigos irmaõs

- **Versionamento**
  - criar issue para versionamento do conteúdo taxonômico (versionamento do banco?)
  - avaliar implementação de campo de vigência na parte superior do ementário.
  - criar issue para produzir versão do datapackage
    > - associar as versões do datapackage a migrations, por exemplo?

- **Glossário**
criar glossário para site estático com conteceitos centrais no projeto, tais como:
  - bitemporalidade: falar onde ponde encontrar mais detalhes
  - sentinela [valor sentinela / data sentinela]
  - natureza de receita
  - data de vigência [vigência] vs data de registro


- classificação com vigência ativa tem que ter níveis hierárquicos cadastrados para, com vigência que abrança todo perído da vigencia da classificação, com a quantidade de níveis detalhados equivalentes aquele

- **Base Legal**
  - verificar possibilidade de excluir registro
  - formato de edição de data com lápis, tal como modelo bitemporal
  - travar edição do campo *_ref
  - operações de cancelar, registrar
  - colocar legendas no filtro da changelist

- **itemClassificacao** - **criação automática** - pensar em critério para perguntar se quer criação automática de principal, mjm, dA etc

- **Consistência de Banco** - **validação**
  - verificar se todo registro ativo tem item pai que está identificado como matriz
  - validação de garantir que toda classificação com vigência ativa tem que ter níveis hierárquicos cadastrados para, com vigência que abrança todo perído da vigencia da classificação, com a quantidade de níveis detalhados equivalentes aquele
  - 

- funcionalidade exportar para excel, csv, pdf
- implementar schemas/correspondence-table (variant?)
- revisar description de chave semântica de todas tabelas
- revisar datapackage.yaml
  - avaliar menção à estrutura
- garantir que, para cada entidade de negócio, haja um e somente um período de "ativo". Isto é, um mesmo código somente pode constar um registro ativo por
- implementar atualizador de base_legal_tecnica
- remover protocolo de ação de exclusão física que existe na tela inicial e substituir por exportar
- reorganizar issues - modelagem dados antigos etc, fechar issues antigos
- criar oreintações para instalação do poetry e python e melhorar para wsl/windows

- avaliar dicionário de palavras abreviadas, para poder serem reaproveitadas especialmente quando da criação do detalhamento - entendo que, a princípio, isso envolveria a implementação de uma tabela para manutenção dessas palavras abreviadas. Essa implementação, além de facilitar/agilizar a implementação -> feita a 

- avaliar estratégia de documentação das áreas de intervenção que classificam as áreas dos convênios

- avaliar a "justificativa de alteração" não apenas como parâmetro de registro, mas como parâmetro de documentação 

- **datapackage** — decidido: seeds permanecem em `docs/assets/seed_*.csv`; `data-raw/` e `data/` para o protocolo de import (ver ADR-005). Spec do import: `_dev/spec_import_*.md` *(a redigir)*.


-------- feito
- **itemClassificacao** - formulário de criação
  x **dígitos ignorados ao digitar código** - deve ser permitido digitar ponto, para facilitar UX quando quiser preencher manualmente o código desejado
  x **criar código já existente** => implementado conforme `_dev/spec_itemClassificacao_criar_codigo_existente.md`
    
    Na tela de criação (add) de itemClassificacao, se o campo de "Código Canônico da Natureza de Receita:" for preenchido com código que já existir de forma ativa, isto é, com data_registro_fim = SENTINELA, e cuja vigência abranja, integral ou parcialmente, a vigência que está informada nos campos de data de vigência do formulário de criação, deve aparecer mensagem de alerta em amarelo associada ao campo de código canônico de receita.

    A mensagem de erro que deve aparecer deve ser algo assim: 

    "Já existe o [código informado](link-para-codigo-informado), com vigência de <data-inicio-vigencia> até <data-fim-vigencia>. [Clique aqui](protocolo-encontrar-proximo-código-disponível) para ir para o próximo código disponível ou ajuste a data de vigência do código atual."

    Essa mensagem deve ficar sendo exibida enquanto o usuário não alterar a data de vigência do formulário, ou não clicar no `Clique aqui` da mensagem. 

    O `Clique aqui` da mensagem deve identificar o "próximo código disponível" nos mesmos termos do protocolo de criar filho a partir do item mãe já implementado, e descrito em `_dev/spec_itemClassificacao_criar_filho.md`. 
x **itemClassificacao** - criar a partir de item pai - 
x **visualização** - **changelist** - implementar padrão de, em todas changelist's, a visualização inicial vir, por padrão, como Ativos (Ano Corrente) 
x **visualização** - **changelist** - filtros do sidebar com estado inicial recolhido, à exceção de «Por Status do Registro» e «Por Data de Início do Registro» (`ChangelistSidebarFilterCollapseMixin` + override `apps/core/templates/admin/filter.html`; ver `_dev/spec_django.md` — «Estado inicial dos filtros do sidebar»). Stateless: estado recomputado a cada GET, sobrepondo escolha do utilizador. Aplicado em todos os admins bitemporais com >3 filtros. 
x verificar a ordenação do db de ItemClassificação, já que as novas receitas criadas, independente do código, estão vindo por último
x verificar consistência de não permitir a criação de item sem que exista matriz anterior existente?. Seria pelo campo `item_pai`?
      x pré-preenchimento de códigos até chegar a 13 dígitos e erro se houver mais dígitos que o máximo
      x considerando que foi implementada máscara conforme última estrutura vigente, avaliar a adição de item de classificação vir com campo "Classificacao" pré preenchida com a última classificação vigente.
      x não permitir FK de Nivel tenha classificacao_id diferente da Classificacao_id do registro -> revogado, já que, na interseção de dois classificadores, o primeiro nível de detalhamento da segunda necessariamente se referenciará na classificação anterior
      x Nivel 1 tem sempre que ser Matriz
      x Filtro por categoria e categoria-origem
      x investigar o porquê a FK Nivel está fazendo associação espúria com registro inativo -> resolvido com vigencia_fk_validation.py, para revolver classificação ativa e vigente

x avaliar estrutura de booleano para edição. Por exemplo, matriz seria "Sim/Não", assim como item gerado
x garantir protocolo de normalização/padronização de campo id para quando editar/reativar registro
x verificar comportamento para reativar receita já bloqueada/inativada
x na página de edição, implementar protocolo de exclusão e bloqueio
x verificar edição de norma cujo início de vigência seja o ano corrente -> sem prejuízo de registro

x criação de novo registro
  x definir padrão de conversão/registro de identificador
  x verificar validação de data de vigência fim menor que início
  x impedir criação de novo identificador com nome idêntico a um identificador ainda ativo

----------------------------------------------------------------------------------------------------

--- VERSIONAMENTO
- versões alterações que fazem versionamento e por quê




- numero_niveis
- numero_digitos
- nivel_maximo



A alternativa implementada foi a de harmonizar os conceitos de versionamento semântico com os conceitos de versionamentos sugeridos pelo GSIM. De acordo com o GSIM, uma nova versão do classificador deve ser gerada toda vez que uma alteração/atualização modifique as fronteiras entre códigos. Isso ocorre basicamente em dois momentos: 
 - quando um objeto/entidade de negócio/conteúdo lógico que antes estava registrado em um código, passa a ser registrado em outro código. Por exemplo, o ICMS que antes era classificado no código X, passou a ser registrado no código Z,
 - quando algo de novo começa a ser classificado, como ocorre na maior parte dos casos em que se inclui um novo código no classificador. Por exemplo, com o advento dos acordos do Desastre de Brumadinho, passou a ingressar nos cofres públicos um recurso totalmente novo para o Estado, que eram os repasses decorrentes dos acertos judiciais.

Do ponto de vista do versionamento semântico (SemVer), em que o número da versão consegue comunicar qual tipo de alteração houve, nos apropriamos, com ligeiras adaptações, dos conceitos de alterações:
 - Major, em que queremos identificar alteração na compatibilidade de uma versão com a outra;
 - Minor, em que não há quebra de compatibilidade, apenas novas funcionalidades; e
 - Patch, em que, sem mudar funcionalidades, faz algum tipo de correção/ajuste. 

Portanto, o versionamento do banco de dados será identificado em 3 campos, [colocar aqui expressão que simboliza essas alterações]

Portanto, a proposta de registro de versões: 

 - Major: toda vez que houver uma alteração na estrutura de um banco, de forma que o novo formato/estrutura atual do banco precisa ser alterada para conseguir receber novas instâncias/novo classificador

   - alteração no somatório do número de níveis existentes. Essa alteração é observada pela alteração no somatório de número de níveis, coluna `numero_niveis` de todas as instâncias com campo `data_vigência_fim` =valor sentinela (9999-12-31) na tabela `seed_classificacao.csv`.
   - alteração no somatório do número de dígitos existentes. Essa alteração é observada pela alteração no somatório de número de dígitos, coluna `numero_digitos` de todas as instâncias com campo `data_vigência_fim` =valor sentinela (9999-12-31) na tabela `seed_classificacao.csv`.
   - alteração no valor máximo da coluna `nivel_numero` entre todas as instâncias com campo `data_vigência_fim` =valor sentinela (9999-12-31) na tabela `seed_classificacao.csv`.

  - Minor: implementação do conceito GSIM em estrito, sendo gerada nova "Minor" toda vez que houver alterações nas fronteiras, inclusive com o surgimento de um novo código
   - alteração na quantidade de entidades-objetos existentes de forma ativa no banco. Essa alteração é observada toda vez que houver alteração no maior valor do campo `item_ref` entre as instâncias com campo `data_vigência_fim` =valor sentinela (9999-12-31) na tabela `seed_item_classificacao.csv`.
   - alteração na quantidade de entidades-objetos

   - alterações que impactarem na estrutura da receita. Considerando que esse conceito se assemelhe com o da tabela de classificador, a qual é responsável pela descrição dos qualificadores básicos da **estrutura** vigente, indicando tipo do classificador, número de níveis, se, no arquivo seed_classificacao, houver a alteração na quantidade de instâncias com data_vigencia_fim = ao valor sentinela (9999-12-31),  


----

- Como saber quais são as classificações ativas **hoje**?
  - data_vigencia_fim = 9999-12-31 & 
  - data_registro_fim = 9999-12-31
  -> regra: quando  `data_vigencia_fim` = 9999-12-31 e `data_registro_fim` = 9999-12-31, somente pode haver 1 entidade-objeto (coluna `[nome-da-tabela]_id`). Isto é, para o mesmo período de vigência, somente pode existir uma classificação disponível para cada entidade-objeto na tabela.

 

 - Como saber quantas versões/edições/vigências uma entidade-objeto (coluna `[nome-da-tabela]_id`) teve?
  - filtrar a entidade-objeto desejada e contar quantas instâncias com `data_registro_fim` estiverem com valores sentinela (31/12/9999)
  -> regra: para cada entidade-objeto, pode haver somente uma instância ativa (`data_registro_fim` = 31/12/9999) por *período* . Isto é, para a mesma entidade-objeto cuja classificação está sendo evoluída no banco de dados, não pode haver duas linhas ativas para períodos que, mesmo que não exatamente iguais em termos de início e fim de vigência, representem períodos que se sobrepõem. 

  ```
  cod: 10
  nome: "receita tributária"
  data_vigencia_inicio: 01/01/2002
  data_vigencia_fim: 01/01/2010

  cod: 10
  nome: "receita tributária e de taxas"
  data_vigencia_inicio: 01/01/2009
  data_vigencia_fim: 31/12/9999
  ```

  Nesse caso, durante o período de 01/01/2009 e 01/01/2010, seria possível que o cod 10 tivesse 2 descrições possíveis


---- DAMA

## Principais recomendações do DMBOK aplicáveis ao projeto (priorizadas)

Abaixo estão as recomendações mais relevantes do DMBOK para este repositório, ordenadas por impacto e com uma ação prática sugerida.

1. Data governance — políticas e papéis (alto impacto)
   - Definir papéis (ex.: Data Owner, Data Steward, Data Admin, CDO) e mapear permissões no Django (Groups/Permissions).
   - Criar um documento mínimo de governança (responsabilidades, escalonamento, regras para alteração de esquema).
   - Benefício: maior responsabilização; custo: esforço organizacional.

2. Metadata / glossário de negócios (alto impacto)
   - Implementar um Business Glossary / Metadata Registry (modelo Django + admin) para termos como `classificacao_id`, `nivel_id`, `item_id`.
   - Expor API/endpoint para consulta de metadados (útil ao front-end e integrações).
   - Benefício direto: redução de ambiguidades e suporte à validação manual.

3. Repositório de metadados e rastreabilidade (médio)
   - Registrar proveniência das cargas (quem carregou, timestamp, versão do datapackage, origem dos arquivos).
   - Mapear um data lineage mínimo (datapackage → loader → modelo → registro).
   - Ajuda em auditoria e debugging dos carregamentos.

4. Regras de qualidade de dados e automação (alto)
   - Consolidar as validações Frictionless (`ptt validar-datapackage`) como checks em CI.
   - Implementar validações de negócio como testes automatizados e validações no Django (uniqueness, patterns).
   - Publicar um scorecard simples no Admin com contagem de falhas e histórico de execuções.

5. Processo de carregamento resiliente (médio)
   - Tornar o loader idempotente e transacional por recurso; manter `--dry-run + report`.
   - Garantir que `--clear` seja seguro em dev e documentar o procedimento.
   - Melhorar logs diagnósticos (incluindo tracebacks detalhados quando Frictionless falha).

6. Controle de versão e bitemporalidade (médio/alto)
   - Documentar políticas bitemporais: chave semântica, política de conflito, retenção de versões.
   - Registrar essas decisões em README/ADR para desenvolvedores e operações.

7. Auditoria / histórico de mudanças (médio)
   - Adicionar audit trail (models/triggers) para alterações manuais no Admin e cargas automáticas.
   - Útil para compliance e investigação de incidentes.

8. Catálogo de dados / descoberta (opcional)
   - Criar uma página/endpoint que liste datasets, esquemas, última carga e métricas de qualidade.
   - Facilita descoberta por usuários internos e integrações.

9. Segurança e controle de acesso (essencial)
   - Definir quem pode executar cargas (`ptt carregar`), editar seeds e criar superusers.
   - Aplicar permissões no Admin e proteger endpoints sensíveis.

10. Operacionalização / observabilidade (médio)
   - Registrar runs de carregamento (tempo, sucesso/erros) e integrar com logs/alertas (ex.: Sentry).

### Relação com o estado atual do projeto
- Pontos fortes: validação Frictionless, datapackage, seeds bitemporais e Admin customizado — boa base técnica.
- Pontos fracos detectados: falta de governança/documentação central (glossário, políticas), ambiguidade em seeds (duplicatas) e necessidade de robustez no loader.
- Risco prático: alterações em constraints ou limpeza de dados exigem migrações coordenadas e testes.

### Sugestão de próximo passo (análise — sem implementar)
- Posso gerar um backlog priorizado com tarefas concretas e estimativas, por exemplo:
  1. Modelo `BusinessGlossary` + admin (alto impacto, baixo esforço)
  2. Grupos/permissions iniciais (médio)
  3. CI que executa `ptt validar-datapackage` (médio)
  4. Audit trail básico para cargas (médio)

Quer que eu gere esse backlog detalhado (tarefas, estimativas e checklist de implementação)?