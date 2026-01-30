# Documentos e dados em `docs/assets`

Cada tabela abaixo corresponde a um schema em `schemas/` e responde a uma pergunta de negócio do classificador de receita.

| Tabela | Pergunta que responde | O que guarda |
|--------|------------------------------------------|-----------|
| **serie_classificacao** | Qual é o produto/conceito/conjunto observado? | **IDENTIDADE** do classificador/série ao longo do tempo. Neste escopo, responde a questões de alto nível, como quem é a unidade institucional responsável, qual o propósito da série. Não guarda estrutura nem datas de lançamento. |
| **classificacao_receita** | Qual é a edição e a estrutura da classificação em vigor? | **EDIÇÃO** do classificador, com a descrição dos qualificadores básicos da **estrutura** vigente, indicando tipo do classificador, número de níveis, tempo de vigência no mundo real. |
| **nivel_hierarquico** | Qual é a estrutura de níveis (eixos) da classificação? | **EIXO** hierárquico, descrevendo nomes, ordem e formato do código (numérico, alfabético, alfanumérico) em cada nível. |
| **item_classificacao** | Quais são os itens (códigos) de cada nível? | **CÓDIGOS** do ementário, com nome oficial, item pai na hierarquia, vigência, informações gerenciais, dentre outros. Inclui flags como item gerado e válido atualmente. |
| **variante_classificacao** | Quais variantes (extensões, agregações, reagrupamentos) existem sobre uma classificação/versão e para que propósito? | Extensões, agregações ou reagrupamentos sobre uma classificação/versão: propósito (ex.: LOA, relatório específico, norma estadual), tipo (extensão, agregação, reagrupamento) e vigência. |
| **versao_classificacao** | Como se chama e quando foi lançada esta edição? | Metadado de lançamento de uma edição, com número da versão, data de publicação, descrição das mudanças (sobretudo de fronteiras entre categorias). Não guarda a estrutura; vincula-se a uma classificação. |

## Exemplos de Lançamentos

### Série de Classificação

Relato dos lançamentos em `exemplo_serie_classificacao.csv`, na ordem em que aparecem:

1. Em 01/01/2023, faz-se o registro inicial do classificador de receita do Estado de Minas Gerais, cuja vigência se inicia na mesma data, sendo o órgão responsável pelo gerenciado é a SEF/MG
  - serie_id: `SERIE-RECEITA-MG`
  - serie_ref: 1
  - serie_nome: `Série de Classificações de Natureza de Receita - MG`
  - descricao: `Série contendo classificações de receita orçamentária do Estado de Minas Gerais.`
  - orgao_responsavel: `SEF/MG`
  - data_vigencia_inicio: `2023-01-01`
  - data_vigencia_fim: `9999-12-31`
  - data_registro_inicio: `2023-01-01`
  - data_registro_fim: `2024-02-20`

2. 
   

2. **SERIE-RECEITA-MG (serie_ref=1), segunda linha**  
   Órgão alterado para SEPLAG/MG; vigência 2024-02-21 a 2024-03-01; registro 2024-02-20 a 2024-03-02. Atualização de responsável (SEF/MG → SEPLAG/MG) e novo intervalo de vigência; este registro foi "fechado" em 2024-03-02 (data_registro_fim).

3. **SERIE-RECEITA-UNIAO (serie_ref=2)**  
   Nova série (União), órgão STN/BRA; vigência 2023-01-01 a 9999-12-31; registro 2024-03-01 a 9999-12-31. Entrada em vigência e registro em 2024-03-01; registro ativo (data_registro_fim = 9999-12-31).

4. **SERIE-RECEITA-MG (serie_ref=1), terceira linha**  
   Órgão SEPLAG/MG; vigência 2024-03-03 a 9999-12-31; registro 2024-03-02 a 9999-12-31. Nova versão da série MG a partir de 2024-03-03 (vigência) e 2024-03-02 (registro); registro ativo — é a versão corrente da série MG no exemplo.
