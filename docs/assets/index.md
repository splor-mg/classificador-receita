# Documentos e dados em `docs/assets`

## Entidades/tabelas

A tabela abaixo discrimina o propósito e respectivo conteúdo de cada uma das entidades/tabelas da pasta `schemas`.



## Exemplos de Lançamentos

### Série de Classificação

Exemplos de registros para descrever a série de classificação, conforme demonstrado em `docs/assets/referencias`,  doc [exemplo_serie_classificacao.csv](referencias/exemplo_serie_classificacao.csv).

1. Em 01/01/2023, faz-se o registro inicial do classificador de receita do Estado de Minas Gerais, cuja vigência se inicia na mesma data, sendo o órgão responsável pelo gerenciado é a SEF/MG.

??? info "Campos do registro/instância"
    - serie_id: `SERIE-RECEITA-MG`
    - serie_ref: 1
    - serie_nome: `Série de Classificações de Natureza de Receita - MG`
    - serie_descricao: `Série contendo classificações de receita orçamentária do Estado de Minas Gerais.`
    - orgao_responsavel: `SEF/MG`
    - data_vigencia_inicio: `2023-01-01`
    - data_vigencia_fim: `9999-12-31`
    - data_registro_inicio: `2023-01-01`
    - data_registro_fim: `9999-12-31`

2. Em 20/02/2024, registra-se a alteração do órgão responsável pela série Receita-MG, de SEF/MG para SEPLAG/MG, com vigência a partir de 21/02/2024.

??? info "Campos do registro/instância"
    O registro anterior deve ser fechado

      - data_vigencia_fim: `2024-02-20`
      - data_registro_fim: `2024-02-20`
    
    Um novo registro é criado com a informação corrigida:

      - serie_id: `SERIE-RECEITA-MG`
      - serie_ref: 1
      - serie_nome: `Série de Classificações de Natureza de Receita - MG`
      - serie_descricao: `Série contendo classificações de receita orçamentária do Estado de Minas Gerais.`
      - orgao_responsavel: `SEPLAG/MG`
      - data_vigencia_inicio: `2024-02-21`
      - data_vigencia_fim: `9999-12-31`
      - data_registro_inicio: `2024-02-20`
      - data_registro_fim: `9999-12-31`

3. Em 01/03/2024, decide-se fazer o registro inicial da série de classificador de receita da União, com vigência retroativa a 01/01/2023; órgão responsável STN/BRA.

??? info "Campos do registro/instância"
    Não há registro anterior desta entidade (nova série). Um novo registro é criado:

      - serie_id: `SERIE-RECEITA-UNIAO`
      - serie_ref: 2
      - serie_nome: `Série de Classificações de Natureza de Receita - União`
      - serie_descricao: `Série contendo classificações de natureza de receita orçamentária da União.`
      - orgao_responsavel: `STN/BRA`
      - data_vigencia_inicio: `2023-01-01`
      - data_vigencia_fim: `9999-12-31`
      - data_registro_inicio: `2024-03-01`
      - data_registro_fim: `9999-12-31`

4. Em 02/03/2024, registra-se uma atualização na descrição (`descricao`) da série Receita-MG vigente a partir de 03/03/2024.

??? info "Campos do registro/instância"
    O registro anterior da série Receita-MG (`serie_ref`=1) deve ser fechado:

      - data_vigencia_fim: `2024-03-02`
      - data_registro_fim: `2024-03-02`
    
    Um novo registro é criado com a informação vigente a partir de 03/03/2024:

      - serie_id: `SERIE-RECEITA-MG`
      - serie_ref: 1
      - serie_nome: `Série de Classificações de Natureza de Receita - MG`
      - serie_descricao: `Série contendo classificações de natureza de receita orçamentária do Estado de Minas Gerais.`
      - orgao_responsavel: `SEPLAG/MG`
      - data_vigencia_inicio: `2024-03-03`
      - data_vigencia_fim: `9999-12-31`
      - data_registro_inicio: `2024-03-02`
      - data_registro_fim: `9999-12-31`