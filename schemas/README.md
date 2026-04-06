# Schemas do Classificador de Receita

Nesta pasta há **dois tipos de artefatos**:
    i) os **descritores de recursos/tabelas principais**, que são os arquivos YAML na **raiz**, responsáveis por definir as tabelas e seus atributos, campos, chaves, FKs. Cada um descreve uma entidade persistida no banco; e
    ii) os **domínios compartilhados**, que são os arquivos na subpasta **`dominios/`** e se tratam de **catálogos de códigos** reutilizados por múltiplos schemas. Não representam definição de tabela de dados; servem ao propósito de validação de campos e evitam `constraint.enum` duplicado. São referenciados a partir dos schemas principais via `custom.domainRef`.

---

| Tabela | Pergunta que responde | O que guarda | Campos/Colunas |
|--------|------------------------------------------|-----------|----------------|
| **serie_classificacao** | Qual é o produto/conceito/conjunto observado? | **IDENTIDADE** do classificador/série ao longo do tempo. Neste escopo, responde a questões de alto nível, como quem é a unidade institucional responsável, qual o propósito da série. Não guarda estrutura nem datas de lançamento. | `serie_id`, `serie_ref`, `serie_nome`, `descricao`, `orgao_responsavel` |
| **classificacao** | Qual é a edição e a estrutura da classificação em vigor? | **EDIÇÃO** do classificador, com a descrição dos qualificadores básicos da **estrutura** vigente, indicando tipo do classificador, número de níveis, tempo de vigência no mundo real. | `classificacao_id`, `serie_id`, `classificacao_nome`, `descricao`, `tipo_classificacao`, `numero_niveis` |
| **nivel_hierarquico** | Qual é a estrutura de níveis (eixos) da classificação? | **EIXO** hierárquico, descrevendo nomes, ordem e formato do código (numérico, alfabético, alfanumérico) em cada nível. | `nivel_id`, `classificacao_id`, `nivel_numero`, `nivel_nome`, `descricao`, `estrutura_codigo`, `tipo_codigo` |
| **item_classificacao** | Quais são os itens (códigos) de cada nível? | **CÓDIGOS** do ementário, com nome oficial, item pai na hierarquia, vigência, informações gerenciais, dentre outros. Inclui flags como item gerado e válido atualmente. | `item_id`, `codigo_completo`, `codigo_numerico`, `nivel_id`, `parent_item_id`, `nome_oficial`, `descricao`, `item_gerado`, `valido_atualmente` |
| **variante_classificacao** | Quais variantes (extensões, agregações, reagrupamentos) existem sobre uma classificação/versão e para que propósito? | Extensões, agregações ou reagrupamentos sobre uma classificação/versão: propósito (ex.: LOA, relatório específico, norma estadual), tipo (extensão, agregação, reagrupamento) e vigência. | `variante_id`, `classificacao_id`, `versao_id`, `variante_nome`, `tipo_variante`, `descricao`, `proposito` |
| **versao_classificacao** | Como se chama e quando foi lançada esta edição? | **METADADO** de lançamento de uma versão/edição, com número da versão, data de publicação, descrição das mudanças (sobretudo de fronteiras entre categorias). Não guarda a estrutura; vincula-se a uma classificação. | `versao_id`, `classificacao_id`, `versao_numero`, `versao_nome`, `descricao`, `data_lancamento` |

---

## Domínios compartilhados (`dominios/`)

**orgaos_entidades** — Catálogo de códigos de órgãos e entidades responsáveis.
É definido em `schemas/dominios/orgaos_entidades.yaml` e referenciado por:

- `serie_classificacao.orgao_responsavel`
- `base_legal_tecnica.orgao_responsavel`

Campos que usam esse domínio indicam a referência via `custom.domainRef`.
Detalhes sobre a convenção e validação: ver [dominios/README.md](dominios/README.md).
