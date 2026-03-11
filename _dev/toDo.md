# lista-toDO
- criação de novo registro
  - definir padrão de conversão/registro de identificador
  - verificar validação de data de vigência fim menor que início
  - impedir criação de novo identificador com nome idêntico a um identificador ainda ativo
- remover protocolo de ação de exclusão física que existe na tela inicial e substituir por exportar
- verificar comportamento para reativar receita já bloqueada/inativada

- reorganizar issues - modelagem dados antigos etc, fechar issues antigos

- criar protocolo de incorporação de bases
  - tratamento excel/csv anos
  - gerar script que vai considerar alteração nos metadados d
- implementar schemas/correspondence-table
- ver description de chave semântica de todas tabelas
- funcionalidade exportar
- revisar datapackage.yaml
  - avaliar menção à mensão à estrutura
- garantir que, para cada entidade de negócio, haja um e somente um período de "ativo". Isto é, um mesmo código somente pode constar um registro ativo por
- implementar atualizador de base_legal_tecnica

CRIAR ORIENTAÇÕES PARA INSTALAÇÃO DO POETRY E DO PYTHON E MELHORAR PARA WSL OU WINDOWS

-------- feito

x na página de edição, implementar protocolo de exclusão e bloqueio
x verificar edição de norma cujo início de vigência seja o ano corrente -> sem prejuízo de registro


-------------------------------------------------------------------------------------------------------

--- VERSIONAMENTO
- versões alterações que fazem versionamente e por quê




- numero_niveis
- numero_digitos
- nivel_maximo



A alternativa implementda foi a de harmonizar os conceitos de versionamento semântico com os conceitos de versionamentos sugeridos pelo GSIM. De acordo com o GSIM, uma nova versão do classificador deve ser gerada toda vez que uma alteração/atualização modifique as fronteiras entre códigos. Isso ocorre basicamente em dois momentos: 
 - quando um objeto/entidade de negócio/conteúdo lógico que antes estava registrado em um código, passa a ser registrado em outro código. Por exemplo, o ICMS que antes era classificado no código X, passou a ser registrado no código Z,
 - quando algo de novo começa a ser classificado, como ocorre na maior parte dos casos em que se inclui um novo código no classificador. Por exemplo, com o advento dos acordos do Desastre de Brumadinho, passou a ingressar nos cofres públicos um recurso totalmente novo para o Estado, que eram os repasses decorrentes dos acertos judiciais.

Do ponto de vista do versionamento semântico (senVer), em que o número da versão consegue comunicar qual tipo de alteração houve, nos apropriamos, com ligeiras adaptações, dos conceitos de uma alterações:
 - Major, em que queremos identificar alteração na compatibilidade de uma versão com a outra;
 - Minor, em que não há quebra de compatibilidade, apenas novas funcionalidades; e
 - Patch, em que, sem mudar funcionaliades, faz algum tipo de correção/ajuste. 

Portanto, o versionamento do banco de dados será identificado em 3 campos, [colocar aqui expressão que simboliza essas alterações]

Portanto, a proposta de registro de versões: 

 - Major: toda vez que houver uma alteração na estrutura de um banco, de forma que o novo formato/estrutura atual do banco precisa ser alterada para conseguir receber novas instâncias/novo classificador

   - alteração no somatório do número de níveis existentes. Essa alteração é observada pela alteração no somatório de número de níveis, coluna `numero_niveis` de todas as instâncias com campo `data_vigência_fim` =valor sentinela (9999-12-31) na tabela `seed_classificacao.csv`.
   - alteração no somatório do número de dígitos existentes. Essa alteração é observada pela alteração no somatório de número de dígitos, coluna `numero_digitos` de todas as instâncias com campo `data_vigência_fim` =valor sentinela (9999-12-31) na tabela `seed_classificacao.csv`.
   - alteração no valor máximo da coluna `nivel_numero` entre todas as instâncias com campo `data_vigência_fim` =valor sentinela (9999-12-31) na tabela `seed_classificacao.csv`.

  - Minor: implementação do conceito GSIM em estrito, sendo gerada nova "Minor" toda vez que um houver alterações nas fronteiras, inclusive com o surgimento de um novo código
   - alteração na quantidade de entidades-objetos existentes de forma ativa no banco. Essa alteração é observada toda vez que houver alteração no maior valor do campo `item_ref` entre as instâncias com campo `data_vigência_fim` =valor sentinela (9999-12-31) na tabela `seed_item_classificacao.csv`.
   - alteração na quantidade de entidades-objetos

   - alterações que impactarem na estrutura da receita. Considerando que esse conceito se assemelhe com o da tabela de classificador, a qual é responsável pela descrição dos qualificadores básicos da **estrutura** vigente, indicando tipo do classificador, número de níveis, se, no arquivo seed_classificao, houver a alteração na quantidade de instâncias com data_vigencia_fim = ao valor sentinela (9999-12-31),  


----

- Como saber quais são as classificações ativas **hoje**?
  - data_vigencia_fim = 9999-12-31 & 
  - data_registro_fim = 9999-12-31
  -> regra: quando  `data_vigencia_fim` = 9999-12-31 e `data_registro_fim` = 9999-12-31, somente pode haver 1 entidade-objeto (coluna `[nome-da-tabela]_id`). Isto é, para o mesmo período de vigência, somente pode existir uma classificação disponível para cada entidade-objeto na tabela.

 

 - Como saber quantas versões/edições/vigências uma entidade-objeto (coluna `[nome-da-tabela]_id`) teve?
  - filtrar a entidade-objeto desejada e contar quantas instâncias com `data_registro_fim` estiverem com valores sentinla (31/12/9999)
  -> regra: para cada entidade-objeto, pode haver somente uma instância ativa (`data_registro_fim` = 31/12/9999) por *período* . Isto é, para a mesma entidade-objeto cuja classificação está sendo evoluída no banco de dados, não pode haver duas linhas ativas para períodos que, mesmo que não exatamente iguais em termos de início e fim de vigência, representem períodos que se sobrebõe. 

  ```
  cod: 10
  nome: "receita tributária"
  data_vigencia_inicio: 01/01/2002
  dafa_vigencia_fim: 01/01/2010

  cod: 10
  nome: "receita tributária e de taxas"
  data_vigencia_inicio: 01/01/2009
  dafa_vigencia_fim: 31/12/9999
  ```

  Nesse caso, duarante o período de 01/01/2009 e 01/01/2010, seria possível que o cod 10 tivesse 2 descrições possíveis


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