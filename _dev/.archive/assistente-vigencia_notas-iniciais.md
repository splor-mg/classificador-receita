1. Ideia de criação de protocolo auxiliar para identificar vigência, por data (ano, ano-mês, ou ano-mês-dia), período (entre duas datas) ou por versão, ou entre duas versões;
  2. O que eu pensei foi em criar um script python, sugestão de nome `get_valid_code.py`, sendo que esse script deveria ser desenhado para receber como argumento data (ou apenas uma data, ou duas datas), ou versão (apenas uma versão, ou duas versões);
  3. Caso se passe data(s) como argumento, não deve ser possível passar o argumento de versão, da mesma forma que, se passada versão(ões) como argumento, não deveria receber o argumento de data;
  4. Esse protocolo é intuído a ser utilizado parar criar filtro nas changelists ('Séries de Classificações', 'Classificações de Receita', 'Níveis Hierárquicos', 'Itens de Classificação'), para indentificar códigos que estão ativos (data-registro-fim = sentinela) e cuja vigência esteja compreendida ou na data, ou no período (quando duas datas), ou na versão, ou no conjunto de versões entre duas referências de versão passadas (quando informada 2 versões); 
  5. Para além dos 2 argumentos, data ou versão, deve ser possível passar uma flag (--system-date AAAA-MM-DD) para recuperar a o que estava vigente em conformidade com `data-início-registro` <= `AAAA-MM-DD` e `data-fim-registro >= `AAAA-MM-DD`;
  6. Deve ser criado um campo na parte superior de cada changelist, campo chamado "Vigência" com 3 subcampos: a) subcampo de "Data Vigência"; b) subcampo "Versão"; c) "Data Registro". 
   6.1. Deve haver um botão de lupa para ser clicado, como sendo um "Pesquisar", de forma a se aplicar os filtros;
  7. O subcampo "Data Vigência" deve ter 3 campos de seleção, dropdown: a) "Ano"; b) "Mês"; c) "Dia". Separados por dois pontos "..", deve haver, na mesma linha, porém em fren aos últimos 3 campos discriminados, os mesmos 3 campos de seleção, para informação de eventual segunda data e formação do "período de vigência
   7.1. Caso o campo "dia" não seja preenchido, deve-se assumir como sendo o último dia possível do mês selecionado;
   7.2. Caso o campo "mês" não seja preenchido, deve-se assumir como sendo dezembro do ano selecionado;
   7.3. Caso o campo "ano" não seja preenchido, deve-se assumir como sendo o ano corrente;
  8. O subcampo "Versão" deve conter apenas um dropdown, contendo as versões que estiverem registradas como ativa na tabela "Versões da Classificação";
  9. No subcampo "Versão", deve existir, fixadas no topo, as opções de LDO e LOA-PPAG, que devem considerar como sendo "datas prefixadas", passíveis de sobrescrever os campos "Mês" e "Dia" do subcampo "Data Vigência". Os efeitos esperados para LDO e LOA-PPAG devem ser:
     1.  LDO => deve obter, para o valor "Ano" de "Data Vigência", assumido ano corrente se vazio, aqueles códigos que estiverem válidos conforme 15 de maio do ano assumido, bem como deve ser assumido que o campo "Data Registro" para a mesma data, de `15 de maio do ano assumido`;
     2.  LOA-PPAG => deve obter, para o valor "Ano" de "Data Vigência", assumido ano corrente se vazio, aqueles códigos que estiverem válidos conforme 31 de setembro do ano assumido, bem como deve ser assumido que o campo "Data Registro" para a mesma data, de `31 de setembro do ano assumido`;
  10. Caso ambos subcampos "Data Vigência" e "Versão" estejam em branco, deve-se assumir "Data Vigência" como sendo 31 de dezembro do ano atual;
  11. O subcampo "Data Registro" deve ser um campo em cujo lado deve haver um ícone de calendário, tal como já existe implementado na tela de "Adicionar Item Classificação", campo "Data de Início da Vigência". 

  12. Exemplos de preenchimento, onde "[ ]" simboliza o campo disponível no layout

      1.  Tudo em branco. Vigência e versão vazias caem em 31/12 do ano corrente.
    ```
    Vigência
    Data Vigência                                                       |  Versão           |  Data Registro
      Ano: [ ]  Mês: [ ]  Dia: [ ] .. Ano: [ ]  Mês: [ ]  Dia: [ ]      |    [ ] .. [ ]     |    [ ]
    ```
  => "Data Vigência assumida": `31/12/2026`
  => "Versão assumida": NULL (qualquer versão)
  => "Data de Registro Assumida": 31/12/9999 (valor sentinela)
  => Filtro a ser aplicado: "Data de Início da Vigência" <= `31/12/2026` e "Data de Fim da Vigência" >= `31/12/2026` e "Data do Fim do Registro" = `valor-sentinela`

      2.  Só o mês.
    ```
    Vigência
    Data Vigência                                                       |  Versão           |  Data Registro
      Ano: [ ]  Mês: [ 03 ]  Dia: [ ] .. Ano: [ ]  Mês: [ ]  Dia: [  ]  |    [ ] .. [ ]     |    [ ]    
    ```
  => "Data Vigência assumida": `31/03/2026`
  => "Versão assumida": NULL (qualquer versão)
  => "Data de Registro Assumida": 31/12/9999 (valor sentinela)
  => Filtro a ser aplicado: todas as codificações cuja "Data de Início da Vigência" <= "Data Vigência assumida" e "Data de Fim da Vigência" >= "Data Vigência assumida" e "Data do Fim do Registro" = `valor-sentinela` (31/12/9999)


      3. Só o ano.
    ```
    Vigência
    Data Vigência                                                       |  Versão           |  Data Registro
      Ano: [ 2024 ]  Mês: [ ]  Dia: [ ] .. Ano: [ ]  Mês: [ ]  Dia: [ ] |    [ ] .. [ ]     |    [ ]
    ```
  => "Data Vigência assumida": `31/12/2024`
  => "Versão assumida": NULL (qualquer versão)
  => "Data de Registro Assumida": 31/12/9999 (valor sentinela)
  => Filtro a ser aplicado: "Data de Início da Vigência" <= `31/12/2024` e "Data de Fim da Vigência" >= `31/12/2024` e "Data do Fim do Registro" = `valor-sentinela`

      4. Ano e mês.
    ```
    Vigência
    Data Vigência                                                          |  Versão           |  Data Registro
      Ano: [ 2024 ]  Mês: [ 03 ]  Dia: [ ] .. Ano: [ ]  Mês: [ ]  Dia: [ ] |    [ ] .. [ ]     |    [ ]
    ```
  => "Data Vigência assumida": `31/03/2024`
  => "Versão assumida": NULL (qualquer versão)
  => "Data de Registro Assumida": 31/12/9999 (valor sentinela)
  => Filtro a ser aplicado: "Data de Início da Vigência" <= `31/03/2024` e "Data de Fim da Vigência" >= `31/03/2024` e "Data do Fim do Registro" = `valor-sentinela`

      5. Ano, mês e dia.
    ```
    Vigência
    Data Vigência                                                       |  Versão           |  Data Registro
      Ano: [ 2024 ]  Mês: [ 03 ]  Dia: [ 15 ] .. Ano: [ ]  Mês: [ ]  Dia: [ ] |    [ ] .. [ ]     |    [ ]
    ```
  => "Data Vigência assumida": `15/03/2024`
  => "Versão assumida": NULL (qualquer versão)
  => "Data de Registro Assumida": 31/12/9999 (valor sentinela)
  => Filtro a ser aplicado: "Data de Início da Vigência" <= `15/03/2024` e "Data de Fim da Vigência" >= `15/03/2024` e "Data do Fim do Registro" = `valor-sentinela`

      6. Mês e dia, ano vazio.
    ```
    Vigência
    Data Vigência                                                       |  Versão           |  Data Registro
      Ano: [ ]  Mês: [ 03 ]  Dia: [ 15 ] .. Ano: [ ]  Mês: [ ]  Dia: [ ] |    [ ] .. [ ]     |    [ ]
    ```
  => "Data Vigência assumida": `15/03/2026`
  => "Versão assumida": NULL (qualquer versão)
  => "Data de Registro Assumida": 31/12/9999 (valor sentinela)
  => Filtro a ser aplicado: "Data de Início da Vigência" <= `15/03/2026` e "Data de Fim da Vigência" >= `15/03/2026` e "Data do Fim do Registro" = `valor-sentinela`

      7. Só o dia. Mês vazio vira dezembro; ano vazio vira o ano corrente.
    ```
    Vigência
    Data Vigência                                                       |  Versão           |  Data Registro
      Ano: [ ]  Mês: [ ]  Dia: [ 15 ] .. Ano: [ ]  Mês: [ ]  Dia: [ ]   |    [ ] .. [ ]     |    [ ]
    ```
  => "Data Vigência assumida": `15/12/2026`
  => "Versão assumida": NULL (qualquer versão)
  => "Data de Registro Assumida": 31/12/9999 (valor sentinela)
  => Filtro a ser aplicado: "Data de Início da Vigência" <= `15/12/2026` e "Data de Fim da Vigência" >= `15/12/2026` e "Data do Fim do Registro" = `valor-sentinela`

      8. Ano e dia, mês vazio.
    ```
    Vigência
    Data Vigência                                                          |  Versão           |  Data Registro
      Ano: [ 2024 ]  Mês: [ ]  Dia: [ 15 ] .. Ano: [ ]  Mês: [ ]  Dia: [ ] |    [ ] .. [ ]     |    [ ]
    ```
  => "Data Vigência assumida": `15/12/2024`
  => "Versão assumida": NULL (qualquer versão)
  => "Data de Registro Assumida": 31/12/9999 (valor sentinela)
  => Filtro a ser aplicado: "Data de Início da Vigência" <= `15/12/2024` e "Data de Fim da Vigência" >= `15/12/2024` e "Data do Fim do Registro" = `valor-sentinela`

      9. Fevereiro sem dia, ano não bissexto. O dia assumido é o último do mês.
    ```
    Vigência
    Data Vigência                                                          |  Versão           |  Data Registro
      Ano: [ 2026 ]  Mês: [ 02 ]  Dia: [ ] .. Ano: [ ]  Mês: [ ]  Dia: [ ] |    [ ] .. [ ]     |    [ ]
    ```
  => "Data Vigência assumida": `28/02/2026`
  => "Versão assumida": NULL (qualquer versão)
  => "Data de Registro Assumida": 31/12/9999 (valor sentinela)
  => Filtro a ser aplicado: "Data de Início da Vigência" <= `28/02/2026` e "Data de Fim da Vigência" >= `28/02/2026` e "Data do Fim do Registro" = `valor-sentinela`

      10. Fevereiro sem dia, ano bissexto.
    ```
    Vigência
    Data Vigência                                                          |  Versão           |  Data Registro
      Ano: [ 2024 ]  Mês: [ 02 ]  Dia: [ ] .. Ano: [ ]  Mês: [ ]  Dia: [ ] |    [ ] .. [ ]     |    [ ]
    ```
  => "Data Vigência assumida": `29/02/2024`
  => "Versão assumida": NULL (qualquer versão)
  => "Data de Registro Assumida": 31/12/9999 (valor sentinela)
  => Filtro a ser aplicado: "Data de Início da Vigência" <= `29/02/2024` e "Data de Fim da Vigência" >= `29/02/2024` e "Data do Fim do Registro" = `valor-sentinela`

      11. Dia impossível no mês informado.
    ```
    Vigência
    Data Vigência                                                             |  Versão           |  Data Registro
      Ano: [ 2026 ]  Mês: [ 04 ]  Dia: [ 31 ] .. Ano: [ ]  Mês: [ ]  Dia: [ ] |    [ ] .. [ ]     |    [ ]
    ```
  => "Data Vigência assumida": nenhuma (`31/04/2026` não existe)
  => "Versão assumida": NULL (qualquer versão)
  => "Data de Registro Assumida": 31/12/9999 (valor sentinela)
  => Filtro a ser aplicado: nenhum; a pesquisa não parte enquanto o dia não existir no mês. Deve ser apresentada mensagem de erro quanto ao campo "Dia".

      12. Período com as duas datas completas. O código precisa cobrir o intervalo inteiro.
    ```
    Vigência
    Data Vigência                                                       |  Versão           |  Data Registro
      Ano: [ 2024 ]  Mês: [ 01 ]  Dia: [ 01 ] .. Ano: [ 2024 ]  Mês: [ 06 ]  Dia: [ 30 ] |    [ ] .. [ ]     |    [ ]
    ```
  => "Data Vigência assumida": `01/01/2024` .. `30/06/2024`
  => "Versão assumida": NULL (qualquer versão)
  => "Data de Registro Assumida": 31/12/9999 (valor sentinela)
  => Filtro a ser aplicado: "Data de Início da Vigência" <= `01/01/2024` e "Data de Fim da Vigência" >= `30/06/2024` e "Data do Fim do Registro" = `valor-sentinela`

      13. Período só com os meses, nos dois lados.
    ```
    Vigência
    Data Vigência                                                        |  Versão           |  Data Registro
      Ano: [ ]  Mês: [ 01 ]  Dia: [ ] .. Ano: [ ]  Mês: [ 06 ]  Dia: [ ] |    [ ] .. [ ]     |    [ ]
    ```
  => "Data Vigência assumida": `31/01/2026` .. `30/06/2026`
  => "Versão assumida": NULL (qualquer versão)
  => "Data de Registro Assumida": 31/12/9999 (valor sentinela)
  => Filtro a ser aplicado: "Data de Início da Vigência" <= `31/01/2026` e "Data de Fim da Vigência" >= `30/06/2026` e "Data do Fim do Registro" = `valor-sentinela`

      14. Só o lado direito da data. Um lado só continua sendo uma data, não um período.
    ```
    Vigência
    Data Vigência                                                       |  Versão           |  Data Registro
      Ano: [ ]  Mês: [ ]  Dia: [ ] .. Ano: [ ]  Mês: [ 06 ]  Dia: [ ]   |    [ ] .. [ ]     |    [ ]
    ```
  => "Data Vigência assumida": `30/06/2026`
  => "Versão assumida": NULL (qualquer versão)
  => "Data de Registro Assumida": 31/12/9999 (valor sentinela)
  => Filtro a ser aplicado: "Data de Início da Vigência" <= `30/06/2026` e "Data de Fim da Vigência" >= `30/06/2026` e "Data do Fim do Registro" = `valor-sentinela`

      15. Período invertido: a data assumida da esquerda fica depois da da direita. O script ordena da mais antiga para a mais recente e informa o ajuste.
    ```
    Vigência
    Data Vigência                                                                  |  Versão           |  Data Registro
      Ano: [ 2026 ]  Mês: [ 08 ]  Dia: [ ] .. Ano: [ 2026 ]  Mês: [ 03 ]  Dia: [ ] |    [ ] .. [ ]     |    [ ]
    ```
  => "Data Vigência assumida": `31/03/2026` .. `31/08/2026`
  => "Versão assumida": NULL (qualquer versão)
  => "Data de Registro Assumida": 31/12/9999 (valor sentinela)
  => Aviso: o período informado foi reordenado de `31/08/2026` .. `31/03/2026` para `31/03/2026` .. `31/08/2026`
  => Filtro a ser aplicado: "Data de Início da Vigência" <= `31/03/2026` e "Data de Fim da Vigência" >= `31/08/2026` e "Data do Fim do Registro" = `valor-sentinela`

      16. Data pontual e Data Registro preenchida. O registro deixa de ser a sentinela e passa a ser o que se sabia naquela data.
    ```
    Vigência
    Data Vigência                                                       |  Versão           |  Data Registro
      Ano: [ ]  Mês: [ 03 ]  Dia: [ ] .. Ano: [ ]  Mês: [ ]  Dia: [ ]   |    [ ] .. [ ]     |    [ 15/05/2024 ]
    ```
  => "Data Vigência assumida": `31/03/2026`
  => "Versão assumida": NULL (qualquer versão)
  => "Data de Registro Assumida": `15/05/2024`
  => Filtro a ser aplicado: "Data de Início da Vigência" <= `31/03/2026` e "Data de Fim da Vigência" >= `31/03/2026` e "Data do Início do Registro" <= `15/05/2025` e "Data do Fim do Registro" >= `15/05/2024`

      17.  Só a Data Registro. Vigência e versão vazias continuam caindo em 31/12 do ano corrente.
    ```
    Vigência
    Data Vigência                                                       |  Versão           |  Data Registro
      Ano: [ ]  Mês: [ ]  Dia: [ ] .. Ano: [ ]  Mês: [ ]  Dia: [ ]      |    [ ] .. [ ]     |    [ 15/05/2024 ]
    ```
  => "Data Vigência assumida": `31/12/2026`
  => "Versão assumida": NULL (qualquer versão)
  => "Data de Registro Assumida": `15/05/2024`
  => Filtro a ser aplicado: "Data de Início da Vigência" <= `31/12/2026` e "Data de Fim da Vigência" >= `31/12/2026` e "Data do Início do Registro" <= `15/05/2024` e "Data do Fim do Registro" >= `15/05/2024`

      18.  Uma versão cadastrada. Data e versão cadastrada não se combinam; a data fica de fora.
    ```
    Vigência
    Data Vigência                                                       |  Versão                         |  Data Registro
      Ano: [ ]  Mês: [ ]  Dia: [ ] .. Ano: [ ]  Mês: [ ]  Dia: [ ]      |    [ VERSAO-BRA-2018 ] .. [ ]   |    [ ]
    ```
  => "Data Vigência assumida": não usada
  => "Versão assumida": `VERSAO-BRA-2018`
  => "Data de Registro Assumida": 31/12/9999 (valor sentinela)
  => Filtro a ser aplicado: codificações cuja vigência esteja compreendida na versão `VERSAO-BRA-2018` e "Data do Fim do Registro" = `valor-sentinela`

      19.  Duas versões cadastradas.
    ```
    Vigência
    Data Vigência                                                       |  Versão                                              |  Data Registro
      Ano: [ ]  Mês: [ ]  Dia: [ ] .. Ano: [ ]  Mês: [ ]  Dia: [ ]      |    [ VERSAO-BRA-ATE2017 ] .. [ VERSAO-BRA-2018 ]     |    [ ]
    ```
  => "Data Vigência assumida": não usada
  => "Versão assumida": `VERSAO-BRA-ATE2017` .. `VERSAO-BRA-2018`
  => "Data de Registro Assumida": 31/12/9999 (valor sentinela)
  => Filtro a ser aplicado: codificações cuja vigência esteja compreendida no conjunto de `VERSAO-BRA-ATE2017` até `VERSAO-BRA-2018` e "Data do Fim do Registro" = `valor-sentinela`

      20.  LDO, ano vazio. Mês e dia são cravados em 15 de maio; o registro assume a mesma data.
    ```
    Vigência
    Data Vigência                                                       |  Versão           |  Data Registro
      Ano: [ ]  Mês: [ ]  Dia: [ ] .. Ano: [ ]  Mês: [ ]  Dia: [ ]      |    [ LDO ] .. [ ] |    [ ]
    ```
  => "Data Vigência assumida": `15/05/2026`
  => "Versão assumida": `LDO`
  => "Data de Registro Assumida": `15/05/2026`
  => Filtro a ser aplicado: "Data de Início da Vigência" <= `15/05/2026` e "Data de Fim da Vigência" >= `15/05/2026` e "Data de Início do Registro" <= `15/05/2026` e "Data do Fim do Registro" >= `15/05/2026`

      21.  LDO com ano, mês e dia preenchidos. Mês e dia informados são sobrescritos.
    ```
    Vigência
    Data Vigência                                                             |  Versão           |  Data Registro
      Ano: [ 2025 ]  Mês: [ 03 ]  Dia: [ 01 ] .. Ano: [ ]  Mês: [ ]  Dia: [ ] |    [ LDO ] .. [ ] |    [ ]
    ```
  => "Data Vigência assumida": `15/05/2025`
  => "Versão assumida": `LDO`
  => "Data de Registro Assumida": `15/05/2025`
  => Filtro a ser aplicado: "Data de Início da Vigência" <= `15/05/2025` e "Data de Fim da Vigência" >= `15/05/2025` e "Data de Início do Registro" <= `15/05/2025` e "Data do Fim do Registro" >= `15/05/2025`

      22.  LOA-PPAG com ano. A data cravada é a da regra, 31 de setembro.
    ```
    Vigência
    Data Vigência                                                       |  Versão                |  Data Registro
      Ano: [ 2025 ]  Mês: [ ]  Dia: [ ] .. Ano: [ ]  Mês: [ ]  Dia: [ ] |    [ LOA-PPAG ] .. [ ] |    [ ]
    ```
  => "Data Vigência assumida": `31/09/2025`
  => "Versão assumida": `LOA-PPAG`
  => "Data de Registro Assumida": `31/09/2025`
  => Filtro a ser aplicado: "Data de Início da Vigência" <= `31/09/2025` e "Data de Fim da Vigência" >= `31/09/2025` e "Data de Início do Registro" <= `31/09/2025` e "Data do Fim do Registro" >= `31/09/2025`

      23.  LDO com Data Registro preenchida à parte. A data assumida do registro continua sendo 15 de maio do ano.
    ```
    Vigência
    Data Vigência                                                       |  Versão           |  Data Registro
      Ano: [ 2025 ]  Mês: [ ]  Dia: [ ] .. Ano: [ ]  Mês: [ ]  Dia: [ ] |    [ LDO ] .. [ ] |    [ 01/01/2025 ]
    ```
  => "Data Vigência assumida": `15/05/2025`
  => "Versão assumida": `LDO`
  => "Data de Registro Assumida": `15/05/2025`
  => Filtro a ser aplicado: "Data de Início da Vigência" <= `15/05/2025` e "Data de Fim da Vigência" >= `15/05/2025` e "Data de Início do Registro" <= `15/05/2025` e "Data do Fim do Registro" >= `15/05/2025`

     24.  Versão cadastrada e Data Vigência preenchidas juntas.
    ```
    Vigência
    Data Vigência                                                       |  Versão                         |  Data Registro
      Ano: [ ]  Mês: [ 03 ]  Dia: [ ] .. Ano: [ ]  Mês: [ ]  Dia: [ ]   |    [ VERSAO-BRA-2018 ] .. [ ]   |    [ ]
    ```
  => "Data Vigência assumida": não usada
  => "Versão assumida": não usada
  => "Data de Registro Assumida": não usada
  => Filtro a ser aplicado: nenhum; a pesquisa não parte com data e versão cadastrada ao mesmo tempo. Informar erro. 
