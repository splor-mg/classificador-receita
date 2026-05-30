
# Import (MINUTA)

A ideia central desse arquivo, destinado a especificar os comportamentos e atributos de protocolos de import (importer.py), já descritos especialmente na ADR-005. A ideia é que essa especificação fique em `_dev/spec_importar.md` e não atrelado a `itemClassificacao`, pois a intenção é que protocolo de importação seja vista como uma ferramenta de um pouco mais alto escopo. 

Para orientação, enquanto os protocolos de carregamento de dados é destinado a carregar o BD com os dados dos arquivos `docs/assets/seed_*.csv`, o import é um protocolo destinado a ler uma tabela/arquivo de dados brutos, ainda não estruturados, tratados e normalizados conforme parâmetros vigentes para o banco de dados, deve tratar esse arquvo,  prepará-lo para então, cumprirem os protocolos de levar para o banco de dados. 

Qualquer divergência aqui em relação ao ADR-05 


As etapas a serem conduzidas pelo protocolo de im


## 1. ferramentas para leitura de arquivos de excel, ou csv, ou outros formatos de arquivo

  Aqui devemos especificar que o script deve estar pronto para ler arquivos com extensões em excel (xls, xlsx...), e outros formatos usuais para tabela de dados como CSV dentre outros
  Deve-se tentar utilizar bibliotecas já consolidadas para leitura de arquivos com essas extensões
  Verificar implementação desses scripts em arquivo separado, a exemplo de `importer_read.py`; implementar de forma separada apenas se houver ganho 

## 1.2. identificação do modelo de dados
  
  Deve-se criar mecanismo para identificar o código, se estamos falando ou não de codigo hierárquico, por exemplo, ou mesmo saber identificar a máscara, para códigos hierárquicos, para permitir o gerenciamento de estruturas planas
  Saber de qual entidade/changelist estamos importando dará a informação de quais são as colunas essenciais (PK)
  Eventualmente, o importer pode ser pensado para ser definido em alto escopo o suficiente para que ele consiga ser utilizado, eventualmente, para demais classes/entidades do projeto, por mais que o foco maior/fallback é a leitura da itemClassificacao

## 2. normalização de nomes das colunas/atributos

  A intenção é que as colunas existentes nos arquivos brutos sendo importados sejam convertidas para os nomes conforme especificado para o datapackage
  Imagino que talvez o mais simples seja utilizar algum arquivo em separado, para poluir pouco, para mapear as correlações entre os nomes existentes nos dados brutos e como eles devem ser entendidos em relação aos nomes de atributos/colunas já parametrizados para o projeto. A exemplo da listagem de conectivos feita `code_name_connectives.py.` 
  Sugestão de nome
  

## 3. fazer transformações de dados
  - tratamento de campos vazios
    Entendo que precisamos relacionar como serão tratados os campos vazios, tais como NULL, e "-".
    Verificar se não podemos/devemos aproveitar tratamento de campos vazios já feito em `apps/core/code_null_normalization.py`

  - compilação de atributos: 
    Esse protocolo visa gerar atributos necessários a partir de eventuais atributos dos dados brutos
    Um exemplo dessa hipótese ocorre quando um código hierárquico, ao invés de ser registrado como um número único, agregando todos os nívieis, é registrado em cada nível individualizado como uma coluna/atributo individualizado. Nesse caso, todas os atritubos de nível devem ser ordenados e concatenados para gerar um código hierárquico único, individualizado como uma única coluna/atributo
    imagino que o protoclo de compilação de atributos tabém seja interessante estar discriminado em um script separado, sugestão de nome `importer_

  - protocolos de autocomplete

    Devemos produzir informações essenciais, como: 
      - *classificacao_id*: em qual classificacao_id cada um dos registros dos dados brutos de enquadram. Verificar protocolos já implementados para autocomplete e ou definição de classification_id
      - *nivel_id*: em qual `nivel_id`cada um dos registros se enquadram
      - *item mãe*: deve tentar ser identificado o item mãe. Verificar reaproveitamento das especificações já implementadas para definição do item mãe. Aqui provavelmente precisaremos avaliar melhor como tratar o fallback, se deixamos vazio ou forçamos o registro de um item mãe como sendo o primeiro registro superior encontrado, mesmo que não antedam as especificações normais
      - *data_vigência*: definição de comportamento para atribuição de data, pensando no fallback comum de "primeiro de janeiro do ano"
    Caso esses campos já estejam disponíveis nos dados brutos, não precisam ser rodado o autocomplete
    Em ambos os casos, existindo dados anteriores ou sendo aplicado o protoclo de "autocomplete", os protocolos de validação/check de autocomplete devem ser rodados
   

   - protocolo de normalização do campo de ID
     até o momento, temos escrito os campos de id garantindo caixa alta manualmente, mas não existe um protocolo de normalização dos campos de id
     esse protocolo talvez também mereça uma especificação em separado e um arquivo .py separado, talvez não atrelado ao importer. Talvez um script `code_id_normalization.py`, bem como avaliarmos se necessidade de especificação própria para a normalização de id's
     um id não pode ter separação por traço

## 4. fazer normalização da string no campo de nome

  Nesse caso, entendo que precisamos implementar uma especificação, própria, `spec_normalizacao_nomes.md`. Não quero colocar esse protocolo de normalização de nomes como algo apenas de itemClassificação, pois é um protocolo que quero deixar disponível para ser utilizado pelas demais tableas/classes que gerenciamos
  Imagino que vamos criar script `code_name_normalization.py`, o qual deve conter essas regras de normalização
  Regras de normalização dos nomes:
    - Devem ser removidos os espaços múltiplos
    - Somente as siglas e as primeiras letras das palavras devem estar com letra maiúscula
    - Os conectivos já listados aqui no projeto devem permanecer todo em caixa baixa


## 4. verificar existência de campos mínimos (PK)

 

## 5. frictionless validate
  rodar o frictionless validate

## 6. salar o a tabela/arquivo já tratado, transformado, normalizado em `data-raw`
  avaliar se, caso não "salvamos uma cópia" do arquivo/tabela do dado bruto informado como input, caso já não seja `docs/assets/referencias/`"

## evolução de diferenças
  acredito que aqui também estejamos falando de um protocolo implementado em arquivo .py em separado, a princípio `importer_*`. o nome inglês ainda não sei, mas se fosse em português seria algo como `importer_incorporar_db`, ou `importer_evoluir_db`, ou 
  esse protocolo deve verificar se há alguma diferença de vigência em relação ao que já está vigente para o período de vigência em cada uma das instâncias da tabela agora no `data-raw`, já tratada
  salvar arquivo contendo o lançamento das diferenças em `data`
  não versionaremos `data`- verificar se está no ignore e se converge com as melhores práticas
  definição da etapa final para parametrizar quais os registros, levando em consideração: 
    - quando formos fazer eventual sobreposição de registro
    - quando precisaremos encerrar vigência de registro anterior e lançar uma nova vigência
