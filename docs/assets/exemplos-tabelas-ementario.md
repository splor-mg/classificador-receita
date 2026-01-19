# Exemplos de Tabelas Baseados no Ementário Real

Este documento apresenta exemplos de registros para cada tabela do modelo de dados, baseados nos códigos reais do ementário de receita de Minas Gerais.

## Estrutura do Código

O código segue o padrão: **C.O.E.D.DD.D.T.II.SSS**

- **C** = Categoria (1 dígito) - Nível 1
- **O** = Origem (1 dígito) - Nível 2
- **E** = Espécie (1 dígito) - Nível 3
- **D** = Desdobramento 1 (1 dígito) - Nível 4
- **DD** = Desdobramento 2 (2 dígitos) - Nível 5
- **D** = Desdobramento 3 (1 dígito) - Nível 6
- **T** = Tipo de Receita (1 dígito) - Nível 7
- **II** = Item de Receita (2 dígitos) - Nível 8
- **SSS** = Subitem de Receita (3 dígitos) - Nível 9

---

## 1. Tabela `serie_classificacao`

**Conceito GSIM:** `ClassificationSeries` — agrupa classificações relacionadas.

### Exemplo de Registro

| serie_id | serie_nome | descricao | orgao_responsavel | data_vigencia_inicio | data_vigencia_fim | data_registro_inicio | data_registro_fim |
|----------|------------|-----------|-------------------|---------------------|-------------------|---------------------|-------------------|
| `SERIE-RECEITA-MG` | Série de Classificações de Receita MG | Série contendo classificações de receita do Estado de Minas Gerais, alinhada com a estrutura nacional | SEFAZ-MG | 2023-01-01 | 9999-12-31 | 2023-01-01 10:00:00 | 9999-12-31 23:59:59 |

---

## 2. Tabela `classificacao_receita`

**Conceito GSIM:** `StatisticalClassification` — classificação estatística específica.

### Exemplo de Registro

| classificacao_id | serie_id | classificacao_nome | tipo_classificacao | numero_niveis | data_vigencia_inicio | data_vigencia_fim | data_registro_inicio | data_registro_fim |
|------------------|----------|-------------------|-------------------|---------------|---------------------|-------------------|---------------------|-------------------|
| `CLASS-RECEITA-MG-2023` | SERIE-RECEITA-MG | Classificação de Receita do Estado de Minas Gerais | hierárquica | 9 | 2023-01-01 | 9999-12-31 | 2023-01-01 10:00:00 | 9999-12-31 23:59:59 |

---

## 3. Tabela `nivel_hierarquico`

**Conceito GSIM:** `ClassificationLevel` — define cada nível da hierarquia.

### Exemplos de Registros (9 níveis)

| nivel_id | classificacao_id | nivel_numero | nivel_nome | estrutura_codigo | tipo_codigo | data_vigencia_inicio | data_vigencia_fim | data_registro_inicio | data_registro_fim |
|----------|------------------|-------------|------------|------------------|-------------|---------------------|-------------------|---------------------|-------------------|
| `NIVEL-1-CATEGORIA` | CLASS-RECEITA-MG-2023 | 1 | Categoria Econômica | C | numérico | 2023-01-01 | 9999-12-31 | 2023-01-01 10:00:00 | 9999-12-31 23:59:59 |
| `NIVEL-2-ORIGEM` | CLASS-RECEITA-MG-2023 | 2 | Origem | C.O | numérico | 2023-01-01 | 9999-12-31 | 2023-01-01 10:00:00 | 9999-12-31 23:59:59 |
| `NIVEL-3-ESPECIE` | CLASS-RECEITA-MG-2023 | 3 | Espécie | C.O.E | numérico | 2023-01-01 | 9999-12-31 | 2023-01-01 10:00:00 | 9999-12-31 23:59:59 |
| `NIVEL-4-DESDOB-1` | CLASS-RECEITA-MG-2023 | 4 | Desdobramento 1 | C.O.E.D | numérico | 2023-01-01 | 9999-12-31 | 2023-01-01 10:00:00 | 9999-12-31 23:59:59 |
| `NIVEL-5-DESDOB-2` | CLASS-RECEITA-MG-2023 | 5 | Desdobramento 2 | C.O.E.D.DD | numérico | 2023-01-01 | 9999-12-31 | 2023-01-01 10:00:00 | 9999-12-31 23:59:59 |
| `NIVEL-6-DESDOB-3` | CLASS-RECEITA-MG-2023 | 6 | Desdobramento 3 | C.O.E.D.DD.D | numérico | 2023-01-01 | 9999-12-31 | 2023-01-01 10:00:00 | 9999-12-31 23:59:59 |
| `NIVEL-7-TIPO` | CLASS-RECEITA-MG-2023 | 7 | Tipo de Receita | C.O.E.D.DD.D.T | numérico | 2023-01-01 | 9999-12-31 | 2023-01-01 10:00:00 | 9999-12-31 23:59:59 |
| `NIVEL-8-ITEM` | CLASS-RECEITA-MG-2023 | 8 | Item de Receita | C.O.E.D.DD.D.T.II | numérico | 2023-01-01 | 9999-12-31 | 2023-01-01 10:00:00 | 9999-12-31 23:59:59 |
| `NIVEL-9-SUBITEM` | CLASS-RECEITA-MG-2023 | 9 | Subitem de Receita | C.O.E.D.DD.D.T.II.SSS | numérico | 2023-01-01 | 9999-12-31 | 2023-01-01 10:00:00 | 9999-12-31 23:59:59 |

### 3.1. Update de Nível - Mudança de Nome

**Cenário:** Em 20/08/2024, o nível 2 teve seu nome alterado de "Origem" para "Origem Jurídica". Esta é uma mudança editorial que não altera fronteiras conceituais entre categorias, portanto é tratada como um **update** (conforme ADR-002), não como uma nova versão.

#### Registro Original (mantido para histórico)

| nivel_id | classificacao_id | nivel_numero | nivel_nome | estrutura_codigo | tipo_codigo | data_vigencia_inicio | data_vigencia_fim | data_registro_inicio | data_registro_fim |
|----------|------------------|-------------|------------|------------------|-------------|---------------------|-------------------|---------------------|-------------------|
| `NIVEL-2-ORIGEM` | CLASS-RECEITA-MG-2023 | 2 | Origem | C.O | numérico | 2023-01-01 | 9999-12-31 | 2023-01-01 10:00:00 | **2024-08-20 14:30:00** |

#### Novo Registro (após update)

| nivel_id | classificacao_id | nivel_numero | nivel_nome | estrutura_codigo | tipo_codigo | data_vigencia_inicio | data_vigencia_fim | data_registro_inicio | data_registro_fim |
|----------|------------------|-------------|------------|------------------|-------------|---------------------|-------------------|---------------------|-------------------|
| `NIVEL-2-ORIGEM` | CLASS-RECEITA-MG-2023 | 2 | **Origem Jurídica** | C.O | numérico | 2023-01-01 | 9999-12-31 | **2024-08-20 14:30:00** | 9999-12-31 23:59:59 |

**Observação:** 
- `data_vigencia_inicio` permanece `2023-01-01` (a mudança não altera quando o nível passou a ser válido no mundo real; o nível existia desde 2023-01-01, apenas com nome diferente)
- `data_registro_inicio` muda para `2024-08-20 14:30:00` (quando o sistema registrou a mudança do nome)
- O registro anterior tem `data_registro_fim` atualizado para `2024-08-20 14:30:00` (quando o sistema deixou de considerar "Origem" como o nome correto)
- Esta mudança é um **update** (mudança editorial), não uma nova versão, pois não altera fronteiras conceituais entre categorias (conforme GSIM v1.1 e ADR-002)

---

## 4. Tabela `item_classificacao`

**Conceito GSIM:** `ClassificationItem` — cada código/item da classificação.

### Exemplos de Registros por Nível Hierárquico

#### Nível 1 - Categoria Econômica

| item_id | codigo_completo | codigo_numerico | nivel_id | parent_item_id | nome_oficial | item_gerado | valido_atualmente | data_vigencia_inicio | data_vigencia_fim | data_registro_inicio | data_registro_fim |
|---------|----------------|-----------------|----------|----------------|--------------|-------------|-------------------|---------------------|-------------------|---------------------|-------------------|
| `ITEM-1000-00-0-0-00-0-00-000` | 1000.00.0.0.00.0.00.000 | 1000000000000 | NIVEL-1-CATEGORIA | NULL | Receitas Correntes | false | true | 2023-01-01 | 9999-12-31 | 2023-01-01 10:00:00 | 9999-12-31 23:59:59 |
| `ITEM-2000-00-0-0-00-0-00-000` | 2000.00.0.0.00.0.00.000 | 2000000000000 | NIVEL-1-CATEGORIA | NULL | Receitas de Capital | false | true | 2023-01-01 | 9999-12-31 | 2023-01-01 10:00:00 | 9999-12-31 23:59:59 |
| `ITEM-7000-00-0-0-00-0-00-000` | 7000.00.0.0.00.0.00.000 | 7000000000000 | NIVEL-1-CATEGORIA | NULL | Receita Intraorçamentária | false | true | 2023-01-01 | 9999-12-31 | 2023-01-01 10:00:00 | 9999-12-31 23:59:59 |
| `ITEM-9000-00-0-0-00-0-00-000` | 9000.00.0.0.00.0.00.000 | 9000000000000 | NIVEL-1-CATEGORIA | NULL | Dedução das Receitas | false | true | 2023-01-01 | 9999-12-31 | 2023-01-01 10:00:00 | 9999-12-31 23:59:59 |

#### Nível 2 - Origem (filho de "Receitas Correntes")

| item_id | codigo_completo | codigo_numerico | nivel_id | parent_item_id | nome_oficial | item_gerado | valido_atualmente | data_vigencia_inicio | data_vigencia_fim | data_registro_inicio | data_registro_fim |
|---------|----------------|-----------------|----------|----------------|--------------|-------------|-------------------|---------------------|-------------------|---------------------|-------------------|
| `ITEM-1100-00-0-0-00-0-00-000` | 1100.00.0.0.00.0.00.000 | 1100000000000 | NIVEL-2-ORIGEM | `ITEM-1000-00-0-0-00-0-00-000` | Impostos, Taxas e Contribuições de Melhoria | false | true | 2023-01-01 | 9999-12-31 | 2023-01-01 10:00:00 | 9999-12-31 23:59:59 |

#### Nível 3 - Espécie (filho de "Impostos, Taxas e Contribuições de Melhoria")

| item_id | codigo_completo | codigo_numerico | nivel_id | parent_item_id | nome_oficial | item_gerado | valido_atualmente | data_vigencia_inicio | data_vigencia_fim | data_registro_inicio | data_registro_fim |
|---------|----------------|-----------------|----------|----------------|--------------|-------------|-------------------|---------------------|-------------------|---------------------|-------------------|
| `ITEM-1110-00-0-0-00-0-00-000` | 1110.00.0.0.00.0.00.000 | 1110000000000 | NIVEL-3-ESPECIE | `ITEM-1100-00-0-0-00-0-00-000` | Impostos | false | true | 2023-01-01 | 9999-12-31 | 2023-01-01 10:00:00 | 9999-12-31 23:59:59 |

#### Nível 4 - Desdobramento 1 (filho de "Impostos")

| item_id | codigo_completo | codigo_numerico | nivel_id | parent_item_id | nome_oficial | item_gerado | valido_atualmente | data_vigencia_inicio | data_vigencia_fim | data_registro_inicio | data_registro_fim |
|---------|----------------|-----------------|----------|----------------|--------------|-------------|-------------------|---------------------|-------------------|---------------------|-------------------|
| `ITEM-1111-00-0-0-00-0-00-000` | 1111.00.0.0.00.0.00.000 | 1111000000000 | NIVEL-4-DESDOB-1 | `ITEM-1110-00-0-0-00-0-00-000` | Impostos sobre o Comércio Exterior | false | true | 2023-01-01 | 9999-12-31 | 2023-01-01 10:00:00 | 9999-12-31 23:59:59 |
| `ITEM-1112-00-0-0-00-0-00-000` | 1112.00.0.0.00.0.00.000 | 1112000000000 | NIVEL-4-DESDOB-1 | `ITEM-1110-00-0-0-00-0-00-000` | Impostos sobre o Patrimônio | false | true | 2023-01-01 | 9999-12-31 | 2023-01-01 10:00:00 | 9999-12-31 23:59:59 |
| `ITEM-1113-00-0-0-00-0-00-000` | 1113.00.0.0.00.0.00.000 | 1113000000000 | NIVEL-4-DESDOB-1 | `ITEM-1110-00-0-0-00-0-00-000` | Impostos sobre a Renda e Proventos de Qualquer Natureza | false | true | 2023-01-01 | 9999-12-31 | 2023-01-01 10:00:00 | 9999-12-31 23:59:59 |
| `ITEM-1114-00-0-0-00-0-00-000` | 1114.00.0.0.00.0.00.000 | 1114000000000 | NIVEL-4-DESDOB-1 | `ITEM-1110-00-0-0-00-0-00-000` | Impostos sobre a Produção e Circulação de Mercadorias e Serviços | false | true | 2023-01-01 | 9999-12-31 | 2023-01-01 10:00:00 | 9999-12-31 23:59:59 |

#### Nível 5 - Desdobramento 2 (filho de "Impostos sobre o Comércio Exterior")

| item_id | codigo_completo | codigo_numerico | nivel_id | parent_item_id | nome_oficial | item_gerado | valido_atualmente | data_vigencia_inicio | data_vigencia_fim | data_registro_inicio | data_registro_fim |
|---------|----------------|-----------------|----------|----------------|--------------|-------------|-------------------|---------------------|-------------------|---------------------|-------------------|
| `ITEM-1111-01-0-0-00-0-00-000` | 1111.01.0.0.00.0.00.000 | 1111010000000 | NIVEL-5-DESDOB-2 | `ITEM-1111-00-0-0-00-0-00-000` | Imposto sobre a Importação | false | true | 2023-01-01 | 9999-12-31 | 2023-01-01 10:00:00 | 9999-12-31 23:59:59 |
| `ITEM-1111-02-0-0-00-0-00-000` | 1111.02.0.0.00.0.00.000 | 1111020000000 | NIVEL-5-DESDOB-2 | `ITEM-1111-00-0-0-00-0-00-000` | Imposto sobre a Exportação | false | true | 2023-01-01 | 9999-12-31 | 2023-01-01 10:00:00 | 9999-12-31 23:59:59 |

#### Nível 6 - Desdobramento 3 (filho de "Imposto sobre a Propriedade Territorial Rural")

| item_id | codigo_completo | codigo_numerico | nivel_id | parent_item_id | nome_oficial | item_gerado | valido_atualmente | data_vigencia_inicio | data_vigencia_fim | data_registro_inicio | data_registro_fim |
|---------|----------------|-----------------|----------|----------------|--------------|-------------|-------------------|---------------------|-------------------|---------------------|-------------------|
| `ITEM-1112-01-1-0-00-0-00-000` | 1112.01.1.0.00.0.00.000 | 1112011000000 | NIVEL-6-DESDOB-3 | `ITEM-1112-01-0-0-00-0-00-000` | Imposto sobre a Propriedade Territorial Rural - Municípios Conveniados | false | true | 2023-01-01 | 9999-12-31 | 2023-01-01 10:00:00 | 9999-12-31 23:59:59 |
| `ITEM-1112-01-2-0-00-0-00-000` | 1112.01.2.0.00.0.00.000 | 1112012000000 | NIVEL-6-DESDOB-3 | `ITEM-1112-01-0-0-00-0-00-000` | Imposto sobre a Propriedade Territorial Rural - Municípios Não-Conveniados | false | true | 2023-01-01 | 9999-12-31 | 2023-01-01 10:00:00 | 9999-12-31 23:59:59 |

#### Nível 7 - Tipo de Receita (filho de "Imposto sobre a Propriedade de Veículos Automotores")

| item_id | codigo_completo | codigo_numerico | nivel_id | parent_item_id | nome_oficial | item_gerado | valido_atualmente | data_vigencia_inicio | data_vigencia_fim | data_registro_inicio | data_registro_fim |
|---------|----------------|-----------------|----------|----------------|--------------|-------------|-------------------|---------------------|-------------------|---------------------|-------------------|
| `ITEM-1112-51-0-1-00-0-00-000` | 1112.51.0.1.00.0.00.000 | 1112510100000 | NIVEL-7-TIPO | `ITEM-1112-51-0-0-00-0-00-000` | IPVA - Principal | false | true | 2023-01-01 | 9999-12-31 | 2023-01-01 10:00:00 | 9999-12-31 23:59:59 |
| `ITEM-1112-51-0-2-00-0-00-000` | 1112.51.0.2.00.0.00.000 | 1112510200000 | NIVEL-7-TIPO | `ITEM-1112-51-0-0-00-0-00-000` | IPVA - Multas e Juros de Mora | false | true | 2023-01-01 | 9999-12-31 | 2023-01-01 10:00:00 | 9999-12-31 23:59:59 |
| `ITEM-1112-51-0-3-00-0-00-000` | 1112.51.0.3.00.0.00.000 | 1112510300000 | NIVEL-7-TIPO | `ITEM-1112-51-0-0-00-0-00-000` | IPVA - Dívida Ativa | false | true | 2023-01-01 | 9999-12-31 | 2023-01-01 10:00:00 | 9999-12-31 23:59:59 |
| `ITEM-1112-51-0-4-00-0-00-000` | 1112.51.0.4.00.0.00.000 | 1112510400000 | NIVEL-7-TIPO | `ITEM-1112-51-0-0-00-0-00-000` | IPVA - Dívida Ativa - Multas e Juros de Mora | false | true | 2023-01-01 | 9999-12-31 | 2023-01-01 10:00:00 | 9999-12-31 23:59:59 |

#### Nível 8 - Item de Receita (filho de "IPVA - Principal")

| item_id | codigo_completo | codigo_numerico | nivel_id | parent_item_id | nome_oficial | item_gerado | valido_atualmente | data_vigencia_inicio | data_vigencia_fim | data_registro_inicio | data_registro_fim |
|---------|----------------|-----------------|----------|----------------|--------------|-------------|-------------------|---------------------|-------------------|---------------------|-------------------|
| `ITEM-1112-51-0-1-01-0-00-000` | 1112.51.0.1.01.0.00.000 | 1112510101000 | NIVEL-8-ITEM | `ITEM-1112-51-0-1-00-0-00-000` | IPVA - Princ. - Cota Parte do Estado | false | true | 2023-01-01 | 9999-12-31 | 2023-01-01 10:00:00 | 9999-12-31 23:59:59 |
| `ITEM-1112-51-0-1-02-0-00-000` | 1112.51.0.1.02.0.00.000 | 1112510102000 | NIVEL-8-ITEM | `ITEM-1112-51-0-1-00-0-00-000` | IPVA - Princ. - Cota Parte dos Municípios | false | true | 2023-01-01 | 9999-12-31 | 2023-01-01 10:00:00 | 9999-12-31 23:59:59 |
| `ITEM-1112-51-0-1-03-0-00-000` | 1112.51.0.1.03.0.00.000 | 1112510103000 | NIVEL-8-ITEM | `ITEM-1112-51-0-1-00-0-00-000` | IPVA - Princ. - Cota Parte do Estado para o FUNDEB | false | true | 2023-01-01 | 9999-12-31 | 2023-01-01 10:00:00 | 9999-12-31 23:59:59 |

#### Nível 9 - Subitem de Receita (filho de "ICMS - Princ. - Cota Parte do Estado")

| item_id | codigo_completo | codigo_numerico | nivel_id | parent_item_id | nome_oficial | item_gerado | valido_atualmente | data_vigencia_inicio | data_vigencia_fim | data_registro_inicio | data_registro_fim |
|---------|----------------|-----------------|----------|----------------|--------------|-------------|-------------------|---------------------|-------------------|---------------------|-------------------|
| `ITEM-1114-50-1-1-01-0-01-001` | 1114.50.1.1.01.0.01.001 | 1114501101001 | NIVEL-9-SUBITEM | `ITEM-1114-50-1-1-01-0-00-000` | ICMS - Princ. - Cota Parte Estado | false | true | 2023-01-01 | 9999-12-31 | 2023-01-01 10:00:00 | 9999-12-31 23:59:59 |
| `ITEM-1114-50-1-1-01-0-01-002` | 1114.50.1.1.01.0.01.002 | 1114501101002 | NIVEL-9-SUBITEM | `ITEM-1114-50-1-1-01-0-00-000` | ICMS - Princ. - Cota Parte Estado - Cessão de Direitos Creditórios - Lei Estadual nº 19.266/10 | false | true | 2023-01-01 | 9999-12-31 | 2023-01-01 10:00:00 | 9999-12-31 23:59:59 |
| `ITEM-1114-50-1-1-01-0-01-003` | 1114.50.1.1.01.0.01.003 | 1114501101003 | NIVEL-9-SUBITEM | `ITEM-1114-50-1-1-01-0-00-000` | ICMS - Princ. - Cota Parte Estado - Cessão de Direitos Creditórios - Lei Estadual nº 23.090/18 | false | true | 2023-01-01 | 9999-12-31 | 2023-01-01 10:00:00 | 9999-12-31 23:59:59 |

---

## 5. Tabela `versao_classificacao`

**Conceito GSIM:** `ClassificationVersion` — versão da classificação (mudanças conceituais).

### Exemplos de Registros

#### Versão 2023 (Inicial)

| versao_id | classificacao_id | versao_numero | versao_nome | descricao | data_lancamento | data_vigencia_inicio | data_vigencia_fim | data_registro_inicio | data_registro_fim |
|-----------|------------------|---------------|-------------|-----------|----------------|---------------------|-------------------|---------------------|-------------------|
| `VERSAO-2023` | CLASS-RECEITA-MG-2023 | 2023 | Versão 2023 | Classificação de Receita MG - Versão 2023. Estrutura inicial com 9 níveis hierárquicos conforme ementário oficial | 2023-01-01 | 2023-01-01 | 9999-12-31 | 2023-01-01 10:00:00 | 9999-12-31 23:59:59 |

#### Versão 2024 (Nova versão - exemplo de mudança conceitual)

**Cenário:** Em 2024, houve uma reestruturação significativa na categoria de Receita Intraorçamentária, com divisão de itens e criação de novos códigos. Isso justifica uma nova versão.

| versao_id | classificacao_id | versao_numero | versao_nome | descricao | data_lancamento | data_vigencia_inicio | data_vigencia_fim | data_registro_inicio | data_registro_fim |
|-----------|------------------|---------------|-------------|-----------|----------------|---------------------|-------------------|---------------------|-------------------|
| `VERSAO-2024` | CLASS-RECEITA-MG-2023 | 2024 | Versão 2024 | Classificação de Receita MG - Versão 2024. Reestruturação da Receita Intraorçamentária (categoria 7) com divisão de itens e criação de novos códigos para melhor granularidade. Inclusão de novos subitens para contribuições previdenciárias. | 2024-01-01 | 2024-01-01 | 9999-12-31 | 2024-01-01 10:00:00 | 9999-12-31 23:59:59 |

**Nota:** A versão 2023 teria `data_vigencia_fim` atualizada para `2023-12-31` quando a versão 2024 for criada.

---

## 6. Tabela `variante_classificacao`

**Conceito GSIM:** `ClassificationVariant` — variante da classificação (extensões, agregações, reagrupamentos).

### Exemplos de Registros

#### Variante para LOA (Lei Orçamentária Anual)

| variante_id | classificacao_id | versao_id | variante_nome | tipo_variante | descricao | proposito | data_vigencia_inicio | data_vigencia_fim | data_registro_inicio | data_registro_fim |
|-------------|------------------|-----------|---------------|---------------|-----------|-----------|---------------------|-------------------|---------------------|-------------------|
| `VAR-AGREGACAO-LOA-2024` | CLASS-RECEITA-MG-2023 | VERSAO-2024 | Variante para LOA 2024 | agregação | Agregação de itens da classificação para relatórios da Lei Orçamentária Anual. Agrupa receitas por categoria econômica e origem para apresentação simplificada. | relatório específico | 2024-01-01 | 9999-12-31 | 2024-01-01 10:00:00 | 9999-12-31 23:59:59 |

#### Variante Extensão Estadual

| variante_id | classificacao_id | versao_id | variante_nome | tipo_variante | descricao | proposito | data_vigencia_inicio | data_vigencia_fim | data_registro_inicio | data_registro_fim |
|-------------|------------------|-----------|---------------|---------------|-----------|-----------|---------------------|-------------------|---------------------|-------------------|
| `VAR-EXTENSAO-ESTADUAL-2024` | CLASS-RECEITA-MG-2023 | VERSAO-2024 | Variante Extensão Estadual | extensão | Extensão da classificação nacional com códigos específicos de MG. Inclui subitens adicionais para receitas próprias do estado não contempladas na classificação nacional. | norma estadual | 2024-01-01 | 9999-12-31 | 2024-01-01 10:00:00 | 9999-12-31 23:59:59 |

#### Variante Reagrupamento para Análise Fiscal

| variante_id | classificacao_id | versao_id | variante_nome | tipo_variante | descricao | proposito | data_vigencia_inicio | data_vigencia_fim | data_registro_inicio | data_registro_fim |
|-------------|------------------|-----------|---------------|---------------|-----------|-----------|---------------------|-------------------|---------------------|-------------------|
| `VAR-REAGRUPAMENTO-FISCAL-2024` | CLASS-RECEITA-MG-2023 | VERSAO-2024 | Variante Reagrupamento Fiscal | reagrupamento | Reagrupamento de receitas para análise fiscal consolidada. Agrupa receitas tributárias e não-tributárias por natureza econômica para relatórios gerenciais. | análise específica | 2024-01-01 | 9999-12-31 | 2024-01-01 10:00:00 | 9999-12-31 23:59:59 |

---

## 7. Exemplos de Updates (Mudanças Bitemporais)

### 7.1. Update de Item - Mudança de Nome

**Cenário:** Em 15/04/2023, o item `1112.51.0.1.01.000` teve seu nome alterado de "IPVA - Princ. - Cota Parte do Estado" para "IPVA - Principal - Cota Parte do Estado".

#### Registro Original (mantido para histórico)

| item_id | codigo_completo | codigo_numerico | nivel_id | parent_item_id | nome_oficial | item_gerado | valido_atualmente | data_vigencia_inicio | data_vigencia_fim | data_registro_inicio | data_registro_fim |
|---------|----------------|-----------------|----------|----------------|--------------|-------------|-------------------|---------------------|-------------------|---------------------|-------------------|
| `ITEM-1112-51-0-1-01-0-00-000` | 1112.51.0.1.01.0.00.000 | 1112510101000 | NIVEL-8-ITEM | `ITEM-1112-51-0-1-00-0-00-000` | IPVA - Princ. - Cota Parte do Estado | false | true | 2023-01-01 | 9999-12-31 | 2023-01-01 10:00:00 | **2023-04-15 09:00:00** |

#### Novo Registro (após update)

| item_id | codigo_completo | codigo_numerico | nivel_id | parent_item_id | nome_oficial | item_gerado | valido_atualmente | data_vigencia_inicio | data_vigencia_fim | data_registro_inicio | data_registro_fim |
|---------|----------------|-----------------|----------|----------------|--------------|-------------|-------------------|---------------------|-------------------|---------------------|-------------------|
| `ITEM-1112-51-0-1-01-0-00-000` | 1112.51.0.1.01.0.00.000 | 1112510101000 | NIVEL-8-ITEM | `ITEM-1112-51-0-1-00-0-00-000` | **IPVA - Principal - Cota Parte do Estado** | false | true | 2023-01-01 | 9999-12-31 | **2023-04-15 09:00:00** | 9999-12-31 23:59:59 |

**Observação:** 
- `data_vigencia_inicio` permanece `2023-01-01` (a mudança não altera quando o item passou a ser válido no mundo real)
- `data_registro_inicio` muda para `2023-04-15 09:00:00` (quando o sistema registrou a mudança)
- O registro anterior tem `data_registro_fim` atualizado para `2023-04-15 09:00:00`

### 7.2. Update de Item - Mudança de Vigência

**Cenário:** Em 19/11/2024, o item `7215.53.1.1.02.000` teve sua vigência alterada (foi criado um novo registro com nova data de vigência).

#### Registro Original

| item_id | codigo_completo | codigo_numerico | nivel_id | parent_item_id | nome_oficial | item_gerado | valido_atualmente | data_vigencia_inicio | data_vigencia_fim | data_registro_inicio | data_registro_fim |
|---------|----------------|-----------------|----------|----------------|--------------|-------------|-------------------|---------------------|-------------------|---------------------|-------------------|
| `ITEM-7215-53-1-1-02-0-00-000` | 7215.53.1.1.02.0.00.000 | 7215531102000 | NIVEL-8-ITEM | `ITEM-7215-53-1-1-00-0-00-000` | Rec. Intra. - Contrib. Patron. - Militar Ativo - Princ. - Pensão | false | true | 2023-01-01 | **2024-11-18** | 2023-01-01 10:00:00 | **2024-11-19 10:00:00** |

#### Novo Registro (com nova vigência)

| item_id | codigo_completo | codigo_numerico | nivel_id | parent_item_id | nome_oficial | item_gerado | valido_atualmente | data_vigencia_inicio | data_vigencia_fim | data_registro_inicio | data_registro_fim |
|---------|----------------|-----------------|----------|----------------|--------------|-------------|-------------------|---------------------|-------------------|---------------------|-------------------|
| `ITEM-7215-53-1-1-02-0-00-000` | 7215.53.1.1.02.0.00.000 | 7215531102000 | NIVEL-8-ITEM | `ITEM-7215-53-1-1-00-0-00-000` | Rec. Intra. - Contrib. Patron. - Militar Ativo - Princ. - Pensão | false | true | **2024-11-19** | 9999-12-31 | **2024-11-19 10:00:00** | 9999-12-31 23:59:59 |

**Observação:** 
- O item teve sua `data_vigencia_inicio` alterada de `2023-01-01` para `2024-11-19`
- O registro anterior tem `data_vigencia_fim` atualizado para `2024-11-18` e `data_registro_fim` para `2024-11-19 10:00:00`

### 7.3. Update de Item - Inativação

**Cenário:** Em 24/01/2025, o item `7121.04.0.1.04.000` foi inativado (não é mais válido).

#### Registro Original

| item_id | codigo_completo | codigo_numerico | nivel_id | parent_item_id | nome_oficial | item_gerado | valido_atualmente | data_vigencia_inicio | data_vigencia_fim | data_registro_inicio | data_registro_fim |
|---------|----------------|-----------------|----------|----------------|--------------|-------------|-------------------|---------------------|-------------------|---------------------|-------------------|
| `ITEM-7121-04-0-1-04-0-00-000` | 7121.04.0.1.04.0.00.000 | 7121040104000 | NIVEL-8-ITEM | `ITEM-7121-04-0-1-00-0-00-000` | Rec. Intra. - Tx. Contr. Fisc. Ambient. - Princ. - Taxa de Regularização Ambiental | false | true | 2025-01-24 | 9999-12-31 | 2025-01-24 10:00:00 | **2025-01-25 10:00:00** |

#### Novo Registro (inativado)

| item_id | codigo_completo | codigo_numerico | nivel_id | parent_item_id | nome_oficial | item_gerado | valido_atualmente | data_vigencia_inicio | data_vigencia_fim | data_registro_inicio | data_registro_fim |
|---------|----------------|-----------------|----------|----------------|--------------|-------------|-------------------|---------------------|-------------------|---------------------|-------------------|
| `ITEM-7121-04-0-1-04-0-00-000` | 7121.04.0.1.04.0.00.000 | 7121040104000 | NIVEL-8-ITEM | `ITEM-7121-04-0-1-00-0-00-000` | Rec. Intra. - Tx. Contr. Fisc. Ambient. - Princ. - Taxa de Regularização Ambiental | false | **false** | 2025-01-24 | **2025-01-25** | **2025-01-25 10:00:00** | 9999-12-31 23:59:59 |

**Observação:** 
- `valido_atualmente` mudou para `false`
- `data_vigencia_fim` mudou de `9999-12-31` para `2025-01-25` (data de inativação)
- `data_registro_inicio` mudou para `2025-01-25 10:00:00` (quando o sistema registrou a inativação)

---

## 8. Exemplos de Nova Versão com Mudanças Conceituais

### 8.1. Cenário: Divisão de Item em Múltiplos Itens

**Cenário:** Em 2024, o item `1114.50.1.1.01.000` (ICMS - Princ. - Cota Parte do Estado) foi dividido em dois itens distintos para melhor granularidade:
- `1114.50.1.1.01.001` - ICMS - Princ. - Cota Parte Estado (mantido)
- `1114.50.1.1.01.004` - ICMS - Princ. - Cota Parte Estado - Novo Item (criado)

#### Versão 2023 - Item Original

| item_id | codigo_completo | codigo_numerico | nivel_id | parent_item_id | nome_oficial | item_gerado | valido_atualmente | data_vigencia_inicio | data_vigencia_fim | data_registro_inicio | data_registro_fim |
|---------|----------------|-----------------|----------|----------------|--------------|-------------|-------------------|---------------------|-------------------|---------------------|-------------------|
| `ITEM-1114-50-1-1-01-0-00-000` | 1114.50.1.1.01.0.00.000 | 1114501101000 | NIVEL-8-ITEM | `ITEM-1114-50-1-1-00-0-00-000` | ICMS - Princ. - Cota Parte do Estado | false | true | 2023-01-01 | **2023-12-31** | 2023-01-01 10:00:00 | **2024-01-01 10:00:00** |

#### Versão 2024 - Item Dividido (mantido)

| item_id | codigo_completo | codigo_numerico | nivel_id | parent_item_id | nome_oficial | item_gerado | valido_atualmente | data_vigencia_inicio | data_vigencia_fim | data_registro_inicio | data_registro_fim |
|---------|----------------|-----------------|----------|----------------|--------------|-------------|-------------------|---------------------|-------------------|---------------------|-------------------|
| `ITEM-1114-50-1-1-01-0-01-001` | 1114.50.1.1.01.0.01.001 | 1114501101001 | NIVEL-9-SUBITEM | `ITEM-1114-50-1-1-01-0-00-000` | ICMS - Princ. - Cota Parte Estado | false | true | **2024-01-01** | 9999-12-31 | **2024-01-01 10:00:00** | 9999-12-31 23:59:59 |

#### Versão 2024 - Novo Item (criado na divisão)

| item_id | codigo_completo | codigo_numerico | nivel_id | parent_item_id | nome_oficial | item_gerado | valido_atualmente | data_vigencia_inicio | data_vigencia_fim | data_registro_inicio | data_registro_fim |
|---------|----------------|-----------------|----------|----------------|--------------|-------------|-------------------|---------------------|-------------------|---------------------|-------------------|
| `ITEM-1114-50-1-1-01-0-01-004` | 1114.50.1.1.01.0.01.004 | 1114501101004 | NIVEL-9-SUBITEM | `ITEM-1114-50-1-1-01-0-00-000` | ICMS - Princ. - Cota Parte Estado - Novo Item | false | true | **2024-01-01** | 9999-12-31 | **2024-01-01 10:00:00** | 9999-12-31 23:59:59 |

**Observação:** 
- A versão 2023 tem `data_vigencia_fim` = `2023-12-31`
- A versão 2024 tem `data_vigencia_inicio` = `2024-01-01`
- O item original foi "encerrado" na versão 2023 e "dividido" em dois novos itens na versão 2024

### 8.2. Cenário: Fusão de Itens

**Cenário:** Em 2024, dois itens foram fundidos em um único item:
- `1112.51.0.4.01.000` - IPVA - DA - Cota Parte do Estado (mantido)
- `1112.51.0.4.02.000` - IPVA - DA - Cota Parte dos Municípios (fundido no item acima)

#### Versão 2023 - Itens Separados

| item_id | codigo_completo | codigo_numerico | nivel_id | parent_item_id | nome_oficial | item_gerado | valido_atualmente | data_vigencia_inicio | data_vigencia_fim | data_registro_inicio | data_registro_fim |
|---------|----------------|-----------------|----------|----------------|--------------|-------------|-------------------|---------------------|-------------------|---------------------|-------------------|
| `ITEM-1112-51-0-4-01-0-00-000` | 1112.51.0.4.01.0.00.000 | 1112510401000 | NIVEL-8-ITEM | `ITEM-1112-51-0-4-00-0-00-000` | IPVA - DA - Cota Parte do Estado | false | true | 2023-01-01 | **2023-12-31** | 2023-01-01 10:00:00 | **2024-01-01 10:00:00** |
| `ITEM-1112-51-0-4-02-0-00-000` | 1112.51.0.4.02.0.00.000 | 1112510402000 | NIVEL-8-ITEM | `ITEM-1112-51-0-4-00-0-00-000` | IPVA - DA - Cota Parte dos Municípios | false | true | 2023-01-01 | **2023-12-31** | 2023-01-01 10:00:00 | **2024-01-01 10:00:00** |

#### Versão 2024 - Item Fundido

| item_id | codigo_completo | codigo_numerico | nivel_id | parent_item_id | nome_oficial | item_gerado | valido_atualmente | data_vigencia_inicio | data_vigencia_fim | data_registro_inicio | data_registro_fim |
|---------|----------------|-----------------|----------|----------------|--------------|-------------|-------------------|---------------------|-------------------|---------------------|-------------------|
| `ITEM-1112-51-0-4-01-0-00-000` | 1112.51.0.4.01.0.00.000 | 1112510401000 | NIVEL-8-ITEM | `ITEM-1112-51-0-4-00-0-00-000` | IPVA - DA - Cota Parte do Estado e Municípios | false | true | **2024-01-01** | 9999-12-31 | **2024-01-01 10:00:00** | 9999-12-31 23:59:59 |

**Observação:** 
- Os dois itens da versão 2023 foram "encerrados" com `data_vigencia_fim` = `2023-12-31`
- Um novo item foi criado na versão 2024 com `data_vigencia_inicio` = `2024-01-01`, fundindo os dois anteriores

---

## 9. Resumo das Relações Hierárquicas

### Exemplo Completo: Hierarquia do IPVA

```
Nível 1: 1000.00.0.0.00.0.00.000 - Receitas Correntes
  └─ Nível 2: 1100.00.0.0.00.0.00.000 - Impostos, Taxas e Contribuições de Melhoria
      └─ Nível 3: 1110.00.0.0.00.0.00.000 - Impostos
          └─ Nível 4: 1112.00.0.0.00.0.00.000 - Impostos sobre o Patrimônio
              └─ Nível 5: 1112.51.0.0.00.0.00.000 - Imposto sobre a Propriedade de Veículos Automotores
                  └─ Nível 6: 1112.51.0.1.00.0.00.000 - IPVA - Principal
                      └─ Nível 7: 1112.51.0.1.01.0.00.000 - IPVA - Princ. - Cota Parte do Estado
                          └─ Nível 8: 1112.51.0.1.01.001.000 - (Subitem, se existir)
```

### Exemplo Completo: Hierarquia do ICMS

```
Nível 1: 1000.00.0.0.00.0.00.000 - Receitas Correntes
  └─ Nível 2: 1100.00.0.0.00.0.00.000 - Impostos, Taxas e Contribuições de Melhoria
      └─ Nível 3: 1110.00.0.0.00.0.00.000 - Impostos
          └─ Nível 4: 1114.00.0.0.00.0.00.000 - Impostos sobre a Produção e Circulação
              └─ Nível 5: 1114.50.0.0.00.0.00.000 - (Desdobramento 2)
                  └─ Nível 6: 1114.50.1.0.00.0.00.000 - ICMS
                      └─ Nível 7: 1114.50.1.1.00.0.00.000 - ICMS - Principal
                          └─ Nível 8: 1114.50.1.1.01.0.00.000 - ICMS - Princ. - Cota Parte do Estado
                              └─ Nível 9: 1114.50.1.1.01.0.01.001 - ICMS - Princ. - Cota Parte Estado
```

---

## 10. Observações Importantes

1. **Bitemporalidade**: Todas as tabelas mantêm histórico completo através de `data_vigencia_*` (valid_time) e `data_registro_*` (transaction_time).

2. **Chaves Primárias Compostas**: Todas as PKs incluem `data_registro_inicio` para suportar múltiplas versões do mesmo registro.

3. **Hierarquia**: A tabela `item_classificacao` usa auto-relacionamento (`parent_item_id`) para representar a hierarquia de 9 níveis.

4. **Versões vs. Updates**: 
   - **Versões** são criadas para mudanças conceituais (divisões, fusões, realocações significativas)
   - **Updates** são registrados no mesmo item com novos `data_registro_inicio` para mudanças pontuais (nomes, descrições, vigências)

5. **Valores Sentinelas**: 
   - `9999-12-31` em `data_vigencia_fim` indica vigência ativa
   - `9999-12-31 23:59:59` em `data_registro_fim` indica registro ativo no sistema
