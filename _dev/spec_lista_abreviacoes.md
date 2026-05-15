# Lista de Abreviações

<Conjunto de regras em relação às quais quero sua avaliação crítica em termos de existir ou não alternativa mais simples para o que pretendo, e se é convergente ou não com as melhores práticas de gestão de um banco de dados.>

A missão aqui é criar um protocolo/script que, analisando o banco de dados, consiga entender/derivar quais abreviações foram de fato implementadas. Aqueles casos que preencherem os requisitos de cada uma das regras, devem gerar um registro na tabela de lista de abreviações. 

O padrão geral é que vamos pesquisar, no banco de dados `ItemClassificacao`, cada **filho** com **registro ativo** (valor sentinela fixo em `data_registro_fim`) e com **vigência orçamentária** que **compreenda o instante de análise T** (ver subsecção em *Design*), e cujo **pai** resolvido esteja **compatível com T** (registro ativo e vigência que também compreenda **T**, com o intervalo do filho contido no do mãe quando a resolução temporal assim o exigir). A análise, para entender se houve alguma abreviação ou não, parte da comparação dos nomes/nomenclatura do item mãe em relação ao do item filho. 

Apesar de essa ser a principal fonte de análise, haverá análises que não dependerão dessa comparação entre mãe e filho. As regras que dependerem de mãe e filho serão identificadas como (PF), e as que não dependerem, serão identificadas como (ND) - "não-dependente".

## Alinhamento terminológico:

- (i) Em uma nomenclatura, como `Nome da Classificação por Natureza de Receita`, deve-se entender por `segmento` cada uma das partes que compõem o nome, separadas entre si pelo caractere traço (-).
  Exemplos:
    - nome/nomenclatura: "Cota Parte dos Municípios"
      quantidade de segmentos: 1
      segmento 1: "Cota Parte dos Municípios"

    - nome/nomenclatura: "Cota Parte dos Municípios - CPM - Fundeb"
      quantidade de segmentos: 3
      segmento 1: "Cota Parte dos Municípios"
      segmento 2: "CPM"
      segmento 3: "Fundeb"

- (ii) Uma `abreviação` é feita por:
  - sigla;
  - encurtamento de uma única palavra/nome;
  - encurtamento de um conjunto de palavras/nomes com a remoção de conectivos tais como "de", "da", "com", "para" etc
    Exemplos: 
      - "Imposto sobre a Propriedade de Veículos Automotores" -> "IPVA" (sigla) 
      - "Principal" -> "Princ." (encurtamento palavara/nome)
      - "Taxas de Inspeção, Controle e Fiscalização" -> "Tx. Insp. Contr. Fisc. " (encurtamento de um conjunto de palavras/nomes)

- (iii) Uma `abreviação simples` deve ser entendida como aquela em que, a única diferença entre sua versão original e sua versão abreviada é a remoção dos conectivos, não existindo nem palavras encurtadas, nem siglas.

- (iv) Uma `abreviação por encurtamento`, ou `palavra/nome encurtados` são todos aqueles termos seguidos de ponto, sem espaço entre o ponto e o termo (exemplo: "Rec.", como encurtamento de "Receita"; "Exec." como encurtamento de "Execução").

- (v) Uma `sigla` deve ser entendida como sendo um conjunto de letras, todas maiúsculas, que não são separadas entre si por espaço, mas que no seu ínterim podem ter traços, pontos ou outros caracteres, desde que não seja espaço em branco.
  Exemplos de siglas:
    - "ICMS"
    - "DA-MJM"
    - "I.T.D.M"
    - "JF_ED"

  Exemplos que NÃO são siglas:
    - "ITCD DA-MJM"
    - "ITCD - DA-MJM"
    - "IuIE"
    - "IuiE"

- (vi) Diz-se que um par candidato `(termo_nome, abreviação)` é **redundante em sentido composicional** quando a abreviação proposta para o **termo frasal** (duas ou mais palavras significativas, no sentido do protocolo) não acrescenta informação além do que já está no **mapa vigente** de pares palavra→token: a `abreviação` coincide, token a token e na mesma ordem, com a junção dos tokens já associados a cada palavra significativa do `termo_nome`. Nesse caso o protocolo **omite** o registro da linha frasal (vide **Regra 7 (ND)**). O mapa vigente inclui **todas** as linhas já persistidas com aquele vocabulário de termos (incluindo registros **desativados** em transaction time, isto é, `data_registro_fim` diferente da sentinela), bem como inferências e manuais aceites na mesma execução, **e** os átomos derivados conforme a **Regra 6** quando aplicável.

- (vii) **`termo_nome` canónico (lexical)** — definição operacional: o valor persistido em `termo` / `termo_nome` deve ser uma **expressão lexical de referência**, composta apenas por **palavras por extenso** (e conectivos, vírgulas, etc., conforme já tratados no protocolo) **e/ou siglas** no sentido **(v)**, **sem** incorporar **abreviação por encurtamento** no sentido **(iv)** no interior do `termo_nome`, salvo excepção explícita na subsecção *Excepções ao termo_nome canónico*.

- (viii) **`termo_nome` inválido para persistência (só encurtamento (iv))** — critério booleano: decomponha o `termo_nome` em **tokens lexicais** delimitados por **espaços em branco**; após remover **pontuação de fronteira** comum de cada token **sem** retirar o ponto final que integra um token no padrão **(iv)** (isto é: retiram-se vírgulas, `;`, `:`, `!`, `?`, parênteses/chevrons/aspas, etc., das extremidades do token; o padrão **(iv)** continua a ser `^[letras]{1,8}\.$` sobre o token assim normalizado), se **qualquer** token restante for classificável como **abreviação por encurtamento** no sentido **(iv)** no papel de forma curta (ex.: `Contrib.`, `Princ.`), o par candidato **não** pode ser objecto de **INSERT** na lista (protocolo automático, carga a partir de seed, criação via admin, e inserções da fase `--print-conflicts-resolve`). **Siglas (v)** no interior do `termo_nome` **não** por si só violam (viii). Exemplos: **inválido** — `Contrib. Patronal` (token `Contrib.`); **válido** — `Contribuição Patronal` (sem token (iv)); **válido** — segmento que inclua `ICMS` como sigla **(v)** sem token terminado em ponto (iv).

### Excepções ao termo_nome canónico

- **Regra 1.2 (PF):** quando o par candidato provém da **Regra 1.2** e o `termo_nome` é o **`receita_nome` integral do item mãe** (1.2.5), o protocolo **pode persistir** esse `termo_nome` mesmo que contenha tokens de encurtamento **(iv)** no interior (ex.: `Princ.` em `Outras Transf. Convênios União Entidades - Princ. - Cultura`), porque o termo não é uma forma lexical inventada na inferência — é a nomenclatura oficial do item de classificação. A excepção aplica-se **apenas** a termos marcados como isentos de **(viii)** na passagem de inferência (conjunto devolvido com os candidatos da Regra 1.2).
- Entradas históricas inválidas fora desta excepção devem ser corrigidas manualmente ou por migração de dados se a governança o exigir.


## Fluxo de dados e artefactos

- A **fonte de verdade** operacional da lista de abreviações é a **tabela** `lista_abreviacoes` no PostgreSQL (modelo `AliasLexico` no código Django). O ficheiro `docs/assets/seed_lista_abreviacoes.csv` é um **artefacto derivado**: deve refletir o conteúdo persistido após export, pelo **mesmo caminho técnico** que o admin usa (`export_resource` para o recurso `lista_abreviacoes` definido em `apps/core/bitemporal_registry.py`, alinhado ao `datapackage.yaml`).
- A **carga inicial** ou reposição de ambiente a partir de ficheiros segue a **mesma política** que as demais tabelas do classificador (comando de carga do datapackage, p.ex. `carregar_classificador`, e metadados em `datapackage.yaml`). Não há segunda verdade paralela ao BD após adoção deste fluxo; o seed versionado existe como **export** do estado persistido, não como origem paralela de mutações correntes.


## Design e regras de negócio

- (A) *atributos* - a tabela de listagem de abreviações deve ter as seguintes colunas no modelo persistido: `termo`, `alias_lexico_ref`, `abreviacao`, `data_registro_inicio`, `data_registro_fim`. No CSV de seed (`seed_lista_abreviacoes.csv`), o campo `termo` é exportado com o cabeçalho `termo_nome` (equivalência semântica usada nesta spec).

- (A′) *validade do `termo`* — todo **INSERT** (e criação equivalente via ORM/admin) deve satisfazer **(vii)** e **(viii)**. Candidatos inferidos ou derivados que falhem **(viii)** são **omitidos** (não persistidos); recomenda-se contagem e `logger.info` distinta de omissões por redundância composicional (Regra 7). O fluxo `--print-conflicts-resolve` **não** deve gravar par escolhido se o `termo` for inválido por **(viii)** (registar aviso e continuar).

- (B) *update (protocolo automático)* - ao identificar um par `termo`/`abreviacao` (no CSV: `termo_nome`/`abreviacao`), o protocolo **só insere** nova linha se **não existir** ainda qualquer linha com esse **mesmo** `termo` na tabela — **incluindo** linhas com `data_registro_fim` **diferente** da sentinela (registos desativados em transaction time). O protocolo automático **não** remove nem altera linhas existentes por omissão (**nunca** `DELETE` nem `UPDATE` na fase automática de inferência). A unicidade do `termo` deve ser **garantida ao nível da base de dados** (ver subsecção *Unicidade do termo*). Exceção à proibição de actualização in-place: apenas o fluxo interativo `--print-conflicts-resolve`, conforme *(F)* (com confirmação explícita quando já existe linha para o `termo`).

- (C) *conflito* - se o mesmo `termo` recebe mais de uma `abreviacao` candidata entre pares distintos **numa mesma execução** do protocolo automático, **nenhuma** dessas candidatas entra nas novidades daquela execução (fica em **conflito silencioso** no modo servidor).

- (D) *fonte* - a fonte de dados para **inferência** é o **Banco de Dados** (`ItemClassificacao` e `lista_abreviacoes`). O ficheiro `docs/assets/seed_lista_abreviacoes.csv` é **subsidiário**: artefacto de export; carga inicial segue o datapackage e o comando de carga, como nas demais tabelas.

- (E) *ordem das regras* - as regras abaixo devem ser aplicadas nessa ordem, sendo que a primeira que se aplicar, encerra a tentativa **na passagem PF por par mãe–filho** (regras **ND** por item, **Regra 4**, **Regra 5** e pós-processamento **6**/**7** seguem o desenho de cada secção). Na passagem PF, ordem recomendada: **Regra 1** (1.1–1.4), **Regra 1.2**, **Regra 4**, **Regra 5**.

- (F) *ferramentas, flags e conflitos*
  - **`--print-conflicts`:** no fim da execução, **lista** os conflitos que permaneceram **silenciosos** durante a corrida (mesmo `termo`, múltiplas `abreviacao` candidatas na mesma execução, sem gravação automática). Não altera o BD.
  - **`--print-conflicts-resolve`:** após a gravação normal da execução, entra em **modo interativo** no terminal: para cada conflito pendente, apresenta **numeradas** as opções de `abreviacao` obtidas pelas heurísticas alinhadas à spec e solicita que o utilizador escolha uma opção válida ou abandone (`n`). Destina-se a **operadores com shell**; não é o caminho padrão de workers agendados sem stdin.
  - **Efeito no BD quando o conflito envolve `termo` ainda não mapeado:** após escolha válida, **cria-se** nova linha com esse `termo` e a `abreviacao` escolhida, `data_registro_fim` = sentinela, e demais campos conforme *(L)* e *(K)*.
  - **Efeito no BD quando o conflito envolve `termo` já mapeado** (linha existente **ativa ou desativada** em transaction time): **não** se cria nova linha; após a escolha numérica das abreviações candidatas, o comando deve solicitar **segunda confirmação explícita** ([y/N]) antes de **atualizar** a linha existente: campo `abreviacao` ← abreviação escolhida; `data_registro_fim` ← **valor sentinela** (registo passa a **Ativo** após a correção); **`data_registro_inicio` mantém-se**. Se o operador recusar, **mantém-se** o registo inalterado (protecção de entradas manuais ou já curadas). O `alias_lexico_ref` **mantém-se** salvo contratação explícita futura.
  - O *task* `atualizar-abreviacoes` pode invocar o mesmo comando **com** `--print-conflicts-resolve` quando se pretender sessão interativa (ex.: post-release); em CI/workers deve usar-se apenas `--print-conflicts` ou execução sem flags.
  - **Log mínimo:** recomenda-se `logger.info` (ou equivalente) com contagem de conflitos e termos omitidos, sem exigência de auditoria pesada.

- (G) *carga banco* - ao ler o CSV, valida `alias_lexico_ref` numérico de forma que, duplicata de `termo_nome` (segunda ocorrência) é ignorada na lista reconstruída, mas o termo continua no conjunto que bloqueia inferência/derivação. Linhas cujo `termo_nome` viole **(viii)** devem ser **omitidas** na carga (sem abortar o recurso completo) e o operador deve poder inspeccionar contagem em log; não persistir entradas inválidas.

- (H) *conectivos* - no scopo/topo do script, deve haver lista fixa de conectivos ignorados na extração de palavras significativas.

- (I) *trigger de atualização* - os protocolos automatizados de atualização da lista de abreviações devem ser acionados toda vez que houver um **Create** ou **Update** de um item de classificação na tabela `ItemClassificacao` (disparando inferência; o **export** do seed segue a subsecção *Export do seed* abaixo).

- (J) *ordenação registros* - todo novo registro na lista de abreviações deve garantir uma ordenação alfabética crescente da coluna `termo_nome` do bd/seed

- (Ia) *changelist no Django* - apesar de não existir uma coluna no banco de dados/seed para `status`, uma coluna status deveria existir na tela inicial do `changelist` da `Lista de Abreviações`, sendo que deve constar, nessa coluna `status`, como `Ativo`, todos aqueles registros com `data_registro_fim` igual ao valor sentinela, e como `Desativado` para todos os demais registros. Além disso, nessa tela inicial no `changelist` da `Lista de Abreviações` do Django, as colunas que devem aparecer são: `termo_nome`, `abreviacao` e `status`, ignoradas as colunas de datas e de `alias_lexico_ref`

- (Ja) *exclusão* - deve ser possível, Desativar/Reativar um registro, bem como excluir um registro. A exclusão deve remover fisicamente o registro anterior.

- (K) *criação* - ao acrescentar um novo registro na tabela/banco de lista de abreviações, o script deve garantir que o respectivo `alias_lexico_ref` seja correspondente ao último `alias_lexico_ref` cadastrado + 1, isto é, garantir comportamento incremental do `alias_lexico_ref`, levando em consideração que, eventual delete/exclusão de algum registro anterior pode ter deixado "buracos" no `alias_lexico_ref`.
- (K′) *renumeração opcional (`--new-ref`)* — o comando ``manage.py atualizar_lista_abreviacoes --new-ref`` (e a task Poetry ``atualizar-abreviacoes-ref``) executa o mesmo protocolo que a execução sem flags (inferência, INSERTs, export **(iii)** quando há mutações) e, **em seguida**, faz ``UPDATE`` de **todas** as linhas em ``lista_abreviacoes`` para que `alias_lexico_ref` seja **1, 2, …, N** na ordem do export (`LOWER(termo)`, `data_registro_inicio`); o CSV exportado reflecte essa ordem. Não altera `termo` nem `abreviacao`.

- (L) *vigência novo registro* - todo novo registro feito na lista de abreviações deve ser registrado como `data_registro_início` = 01/01/<ano-corrente> (ex.: 2026-01-01 00:00:00) e `data_registro_fim` = valor sentinela (ex.: 9999-12-31 00:00:00). Função canónica: `lista_abreviacoes_registro_inicio_novo()` em `apps/core/models_alias_lexico.py` (fuso local do Django, 00:00:00).
- (La) *admin — tela de adicionar* - na criação manual no Django Admin (`AliasLexico`), os campos só leitura `data_registro_inicio_fmt` e `data_registro_fim_fmt` **devem** antecipar os valores que serão gravados em `save_model`: início = **(L)** (`01/01/<ano-corrente> 00:00:00` local), fim = sentinela (`9999-12-31 00:00:00`). **Não** usar `timezone.now()` na pré-visualização do início.


### Export do seed `seed_lista_abreviacoes.csv`

O seed `seed_lista_abreviacoes.csv` é atualizado pelo mesmo caminho de export que o admin (`export_resource` para o recurso `lista_abreviacoes`). A substituição do ficheiro no disco **não** altera a tabela na BD. O comando ``manage.py atualizar_lista_abreviacoes --export-seed`` deve, por omissão, criar **cópia de segurança** do CSV anterior (``*.backup.<timestamp>`` no mesmo directório) antes de sobrescrever, para recuperar edições manuais ao ficheiro que ainda não tenham sido carregadas na BD; as exportações automáticas (ii) e (iii) podem omitir essa cópia para não acumular ficheiros em execuções frequentes. O export corre: (i) após `save_model` em `AliasLexico`; (ii) após `save_model` em `ItemClassificacao` que dispare o protocolo de atualização da lista **e** este resulte em **pelo menos uma** nova linha na tabela/banco de lista de abreviações; (iii) após o comando de atualização em lote concluir as escritas na tabela. Em (iii), uma única exportação consolidada é disparada ao terminar o lote (equivalente a uma transação de negócio concluída), não intercalada por linha.

**Nova linha (critério para (ii)):** conta-se como **nova linha** qualquer **`INSERT`** bem-sucedido em `lista_abreviacoes` durante a execução do protocolo disparada pelo `save_model` em `ItemClassificacao` (isto é, contagem de linhas criadas com novo `id` / novo PK). Duplicata do mesmo termo em sentido **case-insensitive** (violando a constraint `unique_lista_abrev_termo_ci` em `LOWER(termo)`) **não** conta como nova linha: a implementação deve usar o mesmo critério que `insert_alias_lexico_if_new` em `apps/core/alias_lexico_protocol.py` (retorno `inserted is True` após tentativa de `INSERT` isolada em `transaction.atomic`, mapeando `IntegrityError` para “não houve insert”). **Não** contam: apenas `UPDATE` em linhas já existentes (incl. reativação ou correção de `abreviacao` sem insert); execuções do protocolo que não persistem alterações; falhas silenciosas ou conflitos sem gravação. Se o protocolo correr mas o número de linhas da tabela **não** aumentar em relação ao estado lido no início daquele disparo, **não** se exporta ao abrigo de (ii). Opcionalmente, a implementação pode usar o retorno explícito do serviço de inferência (`inseridos > 0`) em vez de comparar contagens globais, desde que seja **equivalente** a esta definição.


### Instante de análise (T) e vigência (`ItemClassificacao`)

- **T** é o instante “agora” usado para filtrar itens, expresso em **UTC** de forma consistente com `USE_TZ` / `timezone.now()` na implementação Django, salvo parâmetro explícito de comando documentado.
- **Registo ativo:** apenas linhas com `data_registro_fim` igual ao **valor sentinela** fixo do projeto (transaction time).
- **Filho (candidato a inferência):** além de registo ativo, a **vigência orçamentária** do filho deve **conter T**, isto é, `data_vigencia_inicio ≤ T ≤ data_vigencia_fim`, com comparação de datas definida de forma **inclusiva** nas duas extremidades, salvo decisão explícita contrária no código (deve ser única e documentada no repositório).
- **mãe (resolvido):** deve estar com **registo ativo** e com vigência que **compreenda T** (`data_vigencia_inicio ≤ T ≤ data_vigencia_fim`, mesma regra de inclusão). Onde a resolução temporal de FK exigir, o intervalo de vigência do filho (em T) deve permanecer **contido** no intervalo de vigência do pai.


### Unicidade do termo

- Existe **constraint de unicidade** em **PostgreSQL** sobre `LOWER(termo)` (`UniqueConstraint` com expressão `Lower("termo")`, nome `unique_lista_abrev_termo_ci` na migração `0001_initial` do app `core`): **não** podem coexistir duas linhas cujo `termo` coincida **sem distinguir maiúsculas/minúsculas**, **independentemente** de `data_registro_fim` (ativa ou desativada). Isto implica que correções por `--print-conflicts-resolve` são **UPDATE** na linha existente quando o termo já está mapeado (após confirmação explícita [y/N] pelo operador), e não um segundo insert.
- O modelo aplica também validação em `clean()` com `termo__iexact` para mensagem de erro amigável antes do `INSERT`.


### Convenção `date` vs `datetime` no código

- Os campos de **vigência orçamentária** em `ItemClassificacao` são **`DateField`**: o instante **T** (`timezone.now()` em UTC) deve ser **normalizado** para **data de calendário** em UTC antes de comparar com `data_vigencia_inicio` / `data_vigencia_fim`, de modo que a regra “contém T” use **o mesmo tipo** nos dois membros da comparação (data com data).
- Evitar comparar `datetime` a `date` sem conversão explícita; a implementação canónica é `calendar_date_utc` + `budget_period_contains_instant` em `apps/core/alias_lexico_protocol.py` (reutilizar **apenas** estas funções na inferência e na resolução de FK temporal).


### Testes automatizados (v1)

- Recomenda-se pelo menos: (1) cenário pai/filho em BD que dispara uma regra PF e **assert** de que `AliasLexico` contém o par esperado; (1b) par **Regra 1.2** caminho A (eco literal) com `termo_nome` = nome integral da mãe; (1c) par **Regra 1.2** caminho B (cobertura lexical), p.ex. `Cota-Parte IOF-Ouro` → nome integral da mãe IOF-Ouro / Comercialização do Ouro; (1d) par **Regra 4** cabeça + sigla da cauda, p.ex. `Atenção MAC` → `Atenção de Média e Alta Complexidade`; (2) segunda execução do comando **sem** `--print-conflicts-resolve` **não** aumenta o número de linhas para o mesmo termo; (3) opcionalmente, smoke de que o ficheiro exportado contém o `termo_nome` esperado após `export_resource`.


### Evolução — desempenho (documentação em código)

- **v1:** varredura completa (*full scan*) de itens e de abreviações em cada execução do comando de atualização em lote; documentar essa escolha na **docstring** do comando (ou do serviço de orquestração), explicitando que otimizações incrementais (watermark / `updated_at` / fila de alterações) ficam para **evolução futura** se o volume o justificar.


## Regra 1 (PF)

- 1.1. item mãe tem nome de segmento único, isto é, a nomenclatura não contém nenhum traço " - " no seu nome
- 1.2. item filho tem pelo menos 2 segmentos
- 1.3. o primeiro segmento do nome do filho é uma abreviação, por sigla, ou por encurtamento de palavra, mas não é uma `abreviação simples`
- 1.4. o primeiro segmento do nome do item filho deve ser registrado como abreviação do nome completo do item mãe
  
  1.1.1.2.51.0.0.00.000 "Imposto sobre a Propriedade de Veículos Automotores"
  1.1.1.2.51.0.1.00.000 "IPVA - Principal"
 
  "IPVA" deve ser registrado como abreviação de "Imposto sobre a Propriedade de Veículos Automotores"

  ---

  1.1.2.1.01.0.0.00.000	"Taxas de Inspeção, Controle e Fiscalização"
  1.1.2.1.01.0.1.00.000	"Tx. Insp. Contr. Fisc. - Principal"
  
  "Tx. Insp. Contr. Fisc" deve ser registrado como abreviação de "Taxas de Inspeção, Controle e Fiscalização"


## Regra 1.2 (PF) — abreviação do nome integral da mãe pelo primeiro segmento do filho

Regra para pares mãe–filho em que o **primeiro segmento major** do filho condensa, de forma reconhecível, a nomenclatura **completa** da mãe (vários segmentos major), e não apenas um segmento isolado da mãe. Há **dois caminhos** de candidatura (A e B); basta **um** deles. A contagem de segmentos major usa o separador ` - ` (espaços–traço–espaços), alinhada à **Regra 4** — **não** confundir com traços **internos** a um segmento (ex.: `Cota-Parte`, `IOF-Ouro`).

### Pré-requisitos (1.2.1–1.2.2)

- 1.2.1. o item mãe tem **pelo menos 2** segmentos major no `receita_nome`
- 1.2.2. o item filho tem **pelo menos 2** segmentos major no `receita_nome`

### Caminho A — eco literal do último segmento da mãe (1.2.3)

- 1.2.3. o **último** segmento major do nome do item mãe, após *trim*, é **exactamente igual** ao **primeiro** segmento major do nome do item filho, após *trim* — **comparação sem distinção de maiúsculas/minúsculas** (*case fold* Unicode). Isto vale **independentemente** de esse segmento ser, ou não, uma `abreviação` (sigla, encurtamento ou `abreviação simples`) de qualquer outra parte do nome da mãe: basta a **igualdade literal** dos dois segmentos na posição indicada.

  **Exemplo (caminho A):**

  1717990109000	`Outras Transf. Convênios União Entidades - Princ. - Cultura`  
  1717990109001	`Cultura - Ministério da Cidadania`

  último segmento da mãe (`Cultura`) = primeiro segmento do filho (`Cultura`) → `Cultura` abrevia o nome integral da mãe.

### Caminho B — cobertura lexical por segmento da mãe (1.2.4)

Quando **1.2.3** **não** se verifica, candidato alternativo:

- 1.2.4.1. seja `S_f` o **primeiro** segmento major do filho (após *trim*) e `S_{m,1} … S_{m,N}` os **N** segmentos major da mãe (`N ≥ 2`, por 1.2.1)
- 1.2.4.2. extraia o conjunto de **palavras significativas** `W_f` de `S_f` e, para cada `i`, o conjunto `W_{m,i}` de `S_{m,i}`, conforme o algoritmo **1.2.8**
- 1.2.4.3. para **cada** `i` de `1` a `N`, a intersecção `W_f ∩ W_{m,i}` (comparação *case-insensitive*) deve ser **não vazia** — isto é: o primeiro segmento do filho contém **pelo menos uma** palavra significativa **de cada** segmento da mãe (não é necessário que **todas** as palavras de `W_f` apareçam na mãe; palavras só no filho, como `IOF` no exemplo abaixo, **não** invalidam o candidato)
- 1.2.4.4. **não** se exige igualdade literal entre `S_f` e qualquer `S_{m,i}` nem entre `S_f` e o último segmento da mãe

  **Exemplo (caminho B):**

  1711550000000	`Cota-Parte do Imposto sobre Operações de Crédito, Câmbio e Seguro, ou Relativas a Títulos ou Valores Mobiliários - Comercialização do Ouro`  
  1711550100000	`Cota-Parte IOF-Ouro - Principal`

  | Papel | Segmento |
  |-------|----------|
  | mãe 1 | `Cota-Parte do Imposto sobre Operações de Crédito, Câmbio e Seguro, ou Relativas a Títulos ou Valores Mobiliários` |
  | mãe 2 | `Comercialização do Ouro` |
  | filho 1 | `Cota-Parte IOF-Ouro` |

  Em `S_f`, os subtermos separados por espaço são `Cota-Parte` e `IOF-Ouro`; subdividindo cada um pelo hífen ASCII interno, `W_f` inclui pelo menos `Cota`, `Parte`, `IOF`, `Ouro` (conectivos excluídos).  
  - Em `W_{m,1}`: `Cota`, `Parte` (entre outras) → intersecção com `W_f` não vazia.  
  - Em `W_{m,2}`: `Comercialização`, `Ouro` → `Ouro` ∈ `W_f`.  

  `Cota-Parte IOF-Ouro` deve ser registrado como abreviação do **nome integral** da mãe (não apenas do primeiro ou do último segmento).

  *Nota:* a **Regra 2** (ND) no item de nomenclatura única `… Ouro - IOF-Ouro` regista `IOF-Ouro` como abreviação do primeiro segmento **daquele** item; a **Regra 1.2** caminho B regista o **primeiro segmento do filho** como abreviação do **nome completo multi-segmento** da mãe — geometrias distintas.

### Registro e política (1.2.5–1.2.7)

- 1.2.5. quando **1.2.3** (caminho A) **ou** **1.2.4** (caminho B) se verifica, o **primeiro** segmento major do filho (`S_f`) deve ser registrado como `abreviacao` do **nome completo** do item mãe (`termo_nome` = string integral do `receita_nome` da mãe). Esse `termo_nome` está **isento de (viii)** quando contiver tokens **(iv)** como parte da nomenclatura oficial da mãe (ver *Excepções ao termo_nome canónico*)
- 1.2.6. **não** se exige o critério **1.3** da Regra 1 (primeiro segmento do filho como sigla/encurtamento formal): nos caminhos A e B o par é candidato mesmo com palavra por extenso repetida (caminho A, ex.: `Cultura`) ou com condensação lexical (caminho B)
- 1.2.7. **ordem (PF):** na implementação, avaliar **depois** das heurísticas da **Regra 1** (1.1–1.4) e **antes** da **Regra 4**; dentro da Regra 1.2, testar **primeiro** o caminho A (1.2.3) e **só se falhar** o caminho B (1.2.4); se outra regra PF tiver sido aplicada ao mesmo par mãe–filho na mesma execução, aplica-se **(E)**

### Algoritmo de palavras significativas (1.2.8)

Usado no caminho B (e alinhado ao vocabulário “significativo” da **Regra 7** / `_significant_words_ordered` na implementação):

- 1.2.8.1. **Entrada:** texto de um segmento major `S` (uma única peça entre delimitadores ` - `).
- 1.2.8.2. **Normalização superficial:** substituir vírgulas `,` por espaço; colapsar espaços; *trim*.
- 1.2.8.3. **Tokens por espaço:** dividir o resultado em tokens contíguos separados por espaços em branco.
- 1.2.8.4. **Subdivisão por hífen:** para cada token, subdividir pelo caractere hífen ASCII `-` (um ou mais hífens consecutivos tratam-se como um separador); cada subparte não vazia que contenha pelo menos uma letra latina (incl. acentuadas) é candidata a palavra.
- 1.2.8.5. **Conectivos:** excluir tokens classificados como conectivos do protocolo (lista usada na implementação: `de`, `da`, `do`, `das`, `dos`, `e`, `ou`, `em`, … — ver `_CONNECTIVES` em `alias_lexico_infer.py`).
- 1.2.8.6. **Chave de comparação:** *case fold* Unicode em cada palavra restante; duas palavras coincidem se as chaves forem iguais.
- 1.2.8.7. **Siglas com hífen** (ex.: `IOF-Ouro` no filho): **não** são tratadas como sigla indivisível **(v)** neste passo — aplicam-se 1.2.8.3–1.2.8.4, produzindo `IOF` e `Ouro` como palavras distintas (coerente com o exemplo IOF-Ouro acima).

### Exemplos negativos

**Não aplica caminho A nem B (mãe monosegmento — Regra 1):**

1.1.1.2.51.0.0.00.000	`Imposto sobre a Propriedade de Veículos Automotores`  
1.1.1.2.51.0.1.00.000	`IPVA - Principal`

último segmento da mãe ≠ primeiro do filho; caminho B falha porque a mãe não tem ≥ 2 segmentos major → candidato **1.2** não se forma; pode aplicar-se **Regra 1**.

**Não aplica caminho B (falta cobertura de algum segmento da mãe):**

Mãe `Segmento Alfa - Segmento Beta`, filho `Só Alfa - Principal` — `W_f` não intersecta `W_{m,2}` → caminho B falha (caminho A só se `Beta` = `Só Alfa`, o que não é o caso).


## Regra 2 (ND)

- 2.1. item de classificação tem nome com 2 segmentos
- 2.2. o segundo segmento do nome é uma sigla
- 2.3. o segundo segmento deve ser registrado como abreviação do primeiro segmento
- 2.4. **refinamento (sigla já mapeada):** se o texto do segundo segmento (a sigla no sentido **(v)**), após normalização de espaços extremos, coincidir **exactamente** com o valor de `abreviacao` de **qualquer** entrada **já** presente no mapa vigente da lista (valores carregados da BD e/ou do seed de fallback **antes** da passagem de inferência na mesma execução do comando), **comparação case-insensitive**, então **não** se regista o par da Regra 2 para esse item: o candidato é **omitido** (não entra no conjunto de inferências unívocas nem gera conflito **só** por este motivo). Exemplo negativo: item ``Alienação Bens Mercadorias Apreendidos - MJM`` quando já existir noutra linha ``Multas e Juros de Mora`` → ``MJM`` (token exacto ``MJM`` como `abreviacao`), não se adiciona ``Alienação Bens Mercadorias Apreendidos`` → ``MJM``. Nota: ``DA-MJM`` **não** coincide com ``MJM``; a regra compara o valor **integral** da coluna `abreviacao`.

  1.1.1.3.01.0.0.00.000 "Imposto sobre a Renda de Pessoa Física - IRPF"

  "IRPF" deve ser registrado como abreviação de "Imposto sobre a Renda de Pessoa Física"

  ---

  1.1.1.5.01.1.0.00.000	"Imposto sobre Operações Financeiras Incidente sobre o Ouro - IOF-Ouro"

  "IOF-Ouro" deve ser registrado como abreviação de "Imposto sobre Operações Financeiras Incidente sobre o Ouro" (primeiro segmento antes de ` - IOF-Ouro`)


## Regra 3 (ND)

- 3.1. item mãe tem nome de segmento único e é terminado com uma sigla entre parênteses
- 3.2. a sigla entre parênteses deve ser entendida como sendo abreviação do restante do nome do item mãe (desconsiderado a parte entre parênteses ao final)

  1.1.1.4.52.0.0.00.000	"Imposto sobre Vendas a Varejo de Combustíveis Líquidos e Gasosos (IVVC)"
  
  "IVVC" deve ser registrado como abreviação de "Imposto sobre Vendas a Varejo de Combustíveis Líquidos e Gasosos"


## Regra 4 (PF)

- 4.1. item mãe tem nome com X segmentos, sendo X maior ou igual a 2
- 4.2. o item filho tem X+1 segmentos
- 4.3. cada um dos segmentos do item filho, até o segmento X, deve ser registrado como sendo uma abreviação do correspondente segmento do item mãe, desde que:
  - o segmento do item filho seja uma abreviação
  - o segmento do item filho não seja uma `abreviação simples` do correspondente segmento do item mãe
  - o segmento do item filho não seja igual ao correspondente segmento do item mãe

  1.1.1.4.50.1.1.00.000	"ICMS - Principal"
  1.1.1.4.50.1.1.01.000	"ICMS - Princ. - Cota Parte do Estado"
  
  segmento 1 do item filho ("ICMS") -> apesar de ser uma abreviação, por sigla, não deve ser registrada como abreviação, já que é igual ao correspondente segmento 1 do item mãe ("ICMS")
  segmento 2 do item filho ("Princ.") -> considerando que é uma abreviação (por encurtamento de palavra), é diferente do correspondente segmento 2 do item mãe ("Principal"), deve sim ser considerado como abreviação

  "Princ." deve ser registrado como abreviação de "Principal"

  ---

  1.1.1.4.50.1.2.00.000	"ICMS - Multas e Juros de Mora"
  1.1.1.4.50.1.2.01.000	"ICMS - MJM - Cota Parte do Estado"

  segmento 1 do item filho ("ICMS") -> apesar de ser uma abreviação, por sigla, não deve ser registrada como abreviação, já que é igual ao correspondente segmento 1 do item mãe ("ICMS")
  segmento 2 do item filho ("MJM") -> considerando que é uma abreviação (por sigla), é diferente do correspondente segmento 2 do item mãe ("Multas e Juros de Mora"), deve sim ser considerado como abreviação

  "MJM" deve ser registrado como abreviação de "Multas e Juros de Mora"

  ---

  1.1.1.4.50.1.1.01.000	"ICMS - Cota Parte do Estado"
  1.1.1.4.50.1.1.01.001	"ICMS - Cota Parte Estado - Devolução"

  segmento 1 do item filho ("ICMS") -> apesar de ser uma abreviação, por sigla, não deve ser registrada como abreviação, já que é igual ao correspondente segmento 1 do item mãe ("ICMS")
  segmento 2 do item filho ("Cota Parte Estado") -> apesar de ser diferente do correspondente segmento 2 do item mãe ("Cota Parte do Estado"), a única diferença é a remoção do conectivo "de"

  "Cota Parte Estado", por se tratar de mera `abreviação simples`, não deve ser registrado como abreviação de "Cota Parte do Estado"

  ---

  1.1.2.1.01.0.1.00.000	"Tx. Insp. Contr. Fisc. - Principal"
  1.1.2.1.01.0.1.01.000	"Tx. Insp. Contr. Fisc. - Princ. - Taxa de Segurança Pública"

  segmento 1 do item filho ("Tx. Insp. Contr. Fisc") -> apesar de ser uma abreviação, por encurtamento de palavra, não deve ser registrada como abreviação, já que é igual ao correspondente segmento 1 do item mãe ("Tx. Insp. Contr. Fisc")
  segmento 2 do item filho ("Princ.") -> deve ser registrado como abreviação do correspondente segmento 2 do item mãe ("Principal")

  "Princ." deve ser registrado como abreviação de "Principal"

  ---

  1.1.2.1.01.0.1.01.000	"Tx. Insp. Contr. Fisc. - Princ. - Taxa de Segurança Pública"
  1.1.2.1.01.0.1.01.001	"Tx. Insp. Contr. Fisc. - Princ. - Tx. Segurança Pública - Polícia Civil do Estado de Minas Gerais - PCMG e Coordenadoria Estadual de Gestão do Trânsito - CET"

  segmento 1 do item filho ("Tx. Insp. Contr. Fisc") -> apesar de ser uma abreviação, por encurtamento de palavra, não deve ser registrada como abreviação, já que é igual ao correspondente segmento 1 do item mãe ("Tx. Insp. Contr. Fisc")
  segmento 2 do item filho ("Princ.") -> apesar de ser uma abreviação, por encurtamento de palavra, não deve ser registrada como abreviação, já que é igual ao correspondente segmento 2 do item mãe ("Princ.")
  segmento 3 do item filho ("Tx. Segurança Pública") -> deve ser registrado como abreviação do correspondente segmento 3 do item mãe ("Taxa de Segurança Pública")

  "Tx. Segurança Pública" deve ser registrado como abreviação de "Taxa de Segurança Pública"

  ---

  **Cabeça preservada + sigla da cauda (refinamento 4.3):**

  Além dos padrões já cobertos (sigla de todo o segmento, encurtamento com ponto, alinhamento token-a-token com pontos), o segmento do filho pode abreviar o da mãe quando:

  - o segmento do filho se decompõe em **exactamente dois** tokens lexicais separados por espaço: **cabeça** + **sigla** (sentido **(v)**);
  - a **cabeça** coincide, *case-insensitive*, com a **primeira palavra significativa** do segmento da mãe;
  - a **sigla** coincide com as iniciais das **demais** palavras significativas do segmento da mãe (conectivos excluídos), na ordem — **não** com as iniciais de **todas** as palavras do segmento (que daria, p.ex., `AMAC` e não `MAC`);
  - o segmento da mãe tem **pelo menos três** palavras significativas (cabeça + cauda com ≥ 2 palavras), para evitar falsos positivos do tipo `Atenção` + `E` → `Atenção Especializada`;
  - a sigla tem **pelo menos 2** caracteres e satisfaz **(v)**.

  1.7.1.3.50.2.1.01.000	`Transf. Bloco Manut. ASPS - Atenção Especializada - Princ. - Atenção de Média e Alta Complexidade`  
  1.7.1.3.50.2.1.01.001	`Transf. Bloco Manut. ASPS - Atenção Especializada - Princ. - Atenção MAC - Prestadores Ambulatoriais e Hospitalares`

  segmentos 1–3 do filho iguais aos da mãe → não registam par.  
  segmento 4 do filho (`Atenção MAC`) abrevia o segmento 4 da mãe (`Atenção de Média e Alta Complexidade`): cabeça `Atenção`; cauda da mãe `Média`, `Alta`, `Complexidade` → sigla `MAC`.

  `Atenção MAC` deve ser registrado como abreviação de `Atenção de Média e Alta Complexidade` (par **por segmento**, como `Principal` → `Princ.`).


## Regra 5 (PF)

- 5.1. item mãe tem nome com X segmentos, sendo X maior ou igual a 2
- 5.2. o item filho tem, igualmente, X segmentos
- 5.3. um dos segmentos, chamado aqui de segmento Y, do item filho corresponde à juntação, com traço ou sem traço, da versão abreviada de 2 seguimentos do item mãe, chamados aqui de segmentos A e B
- 5.4. o segmento Y deve ser registrado como sendo a abreviação da junção dos segmentos A e B

  1.1.1.2.52.0.4.00.000	"ITCD - Dívida Ativa - Multas e Juros de Mora"
  1.1.1.2.52.0.4.01.000	"ITCD - DA-MJM - Cota Parte do Estado"

  ambos mãe e filho possuem 3 segmentos
  contexto: já existe abreviação de "Dívida Ativa" como sendo "DA" (assumido para exemplo)
  contexto: já existe abreviação de "Multas e Juros de Mora" como sendo "MJM" (assumido para exemplo)
  o semento 2 do item filho, "DA-MJM" corresponde à junção de "DA" (segmento 2 do item mãe), com "MJM" (segmento 3 do item mãe), separados por traço "DA-MJM"

  "DA-MJM" deve ser registrado como abreviação de "Dívida Ativa - Multas e Juros de Mora"


## Regra 6 (ND) - Derivação atômica

- 6.1. a derivação atômica é um **pós-processamento**: opera sobre pares `(termo_nome, abreviação)` que **já constam** na lista de abreviações (seed ou tabela) ou que acabaram de ser **aceitos** na mesma execução do protocolo por outras regras — **sem** nova leitura comparativa pai/filho naquele passo (daí a marcação (ND))
- 6.2. somente pares cuja `abreviação` seja interpretável como **cabeça alinhada** ao `termo_nome`, isto é: a `abreviação` se decompõe em **dois ou mais** tokens separados por espaço; existe correspondência **um a um**, na mesma ordem, entre cada token da cabeça e cada **palavra significativa** extraída do `termo_nome` (vide conectivos ignorados alinhados ao protocolo); há **pelo menos** um token no formato de `abreviação por encurtamento` conforme (iv) (letras imediatas + ponto final). Para cada posição, **compatibilidade** token↔palavra é avaliada assim (token **com** ponto final: compara-se a parte **sem** o ponto com a palavra): (a) se a parte sem ponto tem **mais de duas** letras, deve ser **prefixo** da palavra (comparação sem distinção de maiúsculas/minúsculas); (b) se tem **exatamente uma** letra, essa letra deve ser o **início** da palavra (ex.: `G.` com `Geral`); (c) se tem **exatamente duas** letras e a palavra tem **três ou mais** letras, vale o padrão **1.ª e 3.ª** letras da palavra iguais, na ordem, às duas letras do token (ex.: `Tx` com `Taxas` → `Tx.`). Token **sem** ponto naquela posição só é válido se for **igual** por extenso à palavra correspondente do `termo_nome` (repetição literal da mesma palavra do nome longo)
- 6.3. quando 6.2 se verifica, o protocolo **acrescenta** registros adicionais, um por **par atômico** elegível: a **palavra significativa** do `termo_nome` como novo `termo_nome`, e o **token pontilhado** correspondente (incluindo o ponto) como sua `abreviação`
- 6.4. se **todos** os tokens da `abreviação` forem do tipo (iv), **todas** as posições alinhadas geram candidatos à derivação; se a cabeça for **mista** (tokens pontilhados e tokens literais iguais às palavras do `termo_nome`), geram candidatos **apenas** os pares em que o token é de `abreviação por encurtamento` (iv); **não** se registra par atômico para o caso em que abreviação e palavra seriam idênticas (ex.: literal `Civil` → não cria linha `Civil` como abreviação de `Civil`)
- 6.5. se o `termo_nome` tiver **apenas uma** palavra significativa, **não** há derivação atômica a partir desse par (não há decomposição útil)
- 6.6. para cada candidato `(palavra, token.)`, só se grava nova linha se o `termo_nome` igual a essa **palavra** **ainda não existir** em nenhuma linha da lista (independentemente de vigência de registro ou de outras colunas); **não** se altera `abreviação` de linhas já existentes para o mesmo termo **no protocolo automático de derivação atômica** — **exceto** o fluxo interativo `--print-conflicts-resolve` quando aplicável à sobreescrita acordada em *(F)* do *Design*
- 6.7. a derivação atômica alimenta o **mapa vigente** usado na **Regra 7 (ND)** e referido em **(vi)**: cada par atômico aceite entra no mapa (sem sobrescrever mapeamento já fixado para a mesma palavra), permitindo detectar **redundância composicional** antes de aceitar um par frasal candidato

  (contexto) supõe-se que, por uma regra (PF), já exista o registro na lista de abreviações em que o `termo_nome` é o **segmento único** do nome do item mãe e a `abreviação` é exatamente a **primeira parte** (primeiro segmento) do nome do item filho, já validada pelo alinhamento token a palavra descrito em 6.2:

  `termo_nome`: "Contribuição para os Serviços Sociais Gerais"
  `abreviação`: "Contrib. Serv. Sociais Gerais"

  tokens literais na cabeça (iguais por extenso às palavras correspondentes do `termo_nome`): "Sociais", "Gerais" — por 6.4, **não** geram linhas atômicas adicionais; apenas os tokens (iv) geram registros novos

  "Contrib." deve ser registrado (se ainda inexistente) como abreviação de "Contribuição"
  "Serv." deve ser registrado (se ainda inexistente) como abreviação de "Serviços"

  ---

  (contexto) supõe-se par já aceito em que a cabeça é **mista** (tokens (iv) e literal final sem ponto):

  `termo_nome`: "Taxa sobre Serviços de Qualquer Natureza"
  `abreviação`: "Tx. Serv. Qualq. Natureza"

  "Tx." deve ser registrado (se ainda inexistente) como abreviação de "Taxa"
  "Serv." deve ser registrado (se ainda inexistente) como abreviação de "Serviços"
  "Qualq." deve ser registrado (se ainda inexistente) como abreviação de "Qualquer"

  o token literal "Natureza", por coincidir com a palavra homónima do `termo_nome`, não gera linha atômica adicional por 6.4

  ---

  (contexto) supõe-se par em que o `termo_nome` contém **apenas uma** palavra significativa no sentido do protocolo (conectivos ignorados):

  `termo_nome`: "Principal"
  `abreviação`: "Princ."

  não há derivação atômica adicional por 6.5 (não há conjunto de átomos a registrar além do par já existente)


## Regra 7 (ND) - Redundância composicional

- 7.0. **Independente** da redundância composicional, candidatos cujo `termo_nome` viole **(viii)** (encurtamento (iv) como token lexical no termo) são sempre **omitidos** da persistência; ver **(A′)** e **(vii)**.

- 7.1. a redundância composicional é um critério de **omissão**: não compara mãe e filho; apenas decide se um par candidato `(termo_nome, abreviação)` **não** deve ser acrescentado à lista porque seria **derivável sem ambiguidade** a partir de mapeamentos já presentes no **mapa vigente** (vide **(vi)**)
- 7.2. o **mapa vigente** é uma estrutura lógica `palavra_significativa → token` (o token é o valor de `abreviação` guardado para aquela palavra como `termo_nome` atômico). Inicialmente contém todos os pares das linhas **já existentes** no seed; ao longo da execução do protocolo, passa a incluir também cada par **aceite** na mesma ordem de processamento (inferências resolvidas, entradas manuais não colidentes) e os **átomos** inferidos pela **Regra 6** assim que o par frasal que os originou é aceite (cada átomo entra com `setdefault`, ou seja, **não** altera token já associado à mesma palavra)
- 7.3. **Pré-condições** para aplicar o teste: o `termo_nome` candidato deve ter **duas ou mais** palavras significativas (mesma extração que o restante do protocolo: conectivos ignorados, vírgulas tratadas como separação equivalente a espaço); a `abreviação` candidata, após remoção de espaços extremos, deve ser **não vazia**
- 7.4. **Critério decisório:** decomponha o `termo_nome` na lista ordenada de palavras significativas `w₁, w₂, …, wₙ` (`n ≥ 2`). Para cada `wᵢ`, consulte o mapa vigente: deve existir entrada com chave exatamente `wᵢ` (igualdade de string conforme o protocolo). Seja `tᵢ` o token (`abreviação`) associado a `wᵢ`. O par é **redundante em sentido composicional** se, e somente se, **para todo** `i` existe `tᵢ` e a concatenação `t₁ + " " + t₂ + … + " " + tₙ` (um espaço entre tokens consecutivos, **sem** espaço extra à esquerda/direita da string final) é **igual**, como string única, à `abreviação` candidata já normalizada (espaços extremos removidos)
- 7.5. se o critério de 7.4 for verdadeiro, **não** se cria linha nova para esse `(termo_nome, abreviação)` candidato; contadores de “omitidos por redundância composicional” incrementam-se em conformidade
- 7.6. se **qualquer** `wᵢ` não tiver entrada no mapa, ou a concatenação dos `tᵢ` obtidos **não** for igual à `abreviação` candidata, o par **não** é considerado redundantemente composicional por este teste (pode ser aceite pelas demais regras e filtros)
- 7.7. a **ordem** em que candidatos entram no mapa importa: primeiro o seed e a ordem de processamento das inferências/manuais; só depois os átomos da **Regra 6** relativos a um par frasal já aceite enriquecem o mapa para candidatos **posteriores** na mesma execução

  (contexto) no mapa vigente já constam, entre outras, as linhas atômicas: `"Contribuição" → "Contrib."` e `"Serviços" → "Serv."`

  candidato a ser avaliado (por exemplo vindo de uma inferência PF):

  `termo_nome`: "Contribuição para os Serviços"
  `abreviação`: "Contrib. Serv."

  palavras significativas: "Contribuição", "Serviços" — tokens no mapa: "Contrib.", "Serv." — junção igual à `abreviação` → **omissão** por redundância composicional (7.4–7.5)

  ---

  (contexto) no mapa vigente **não** existe entrada para a palavra "Qualquer"

  `termo_nome`: "Taxa sobre Serviços de Qualquer Natureza"
  `abreviação`: "Tx. Serv. Qualq. Natureza"

  falha a exigência de 7.4 para `wᵢ` faltante → o par **não** é tratado como redundante **só** por este teste (7.6); outras regras do protocolo continuam a aplicar-se

  ---

  (contexto) mesmo mapa com átomos, mas a `abreviação` candidata usa token **diferente** para uma mesma palavra (ex.: sinónimo de abreviação)

  `termo_nome`: "Contribuição Serviços"
  `abreviação`: "Contrib. Serviços"

  duas palavras significativas, duas partes na abreviação, mas a segunda parte `"Serviços"` **não** coincide com o token mapeado `"Serv."` para a palavra "Serviços" — junção dos tokens do mapa seria `"Contrib. Serv."` ≠ candidata → **não** é redundância composicional por 7.4 (7.6)
