# Especificação: validação de qualidade (validate_quality.py)

## Objetivo

Aplicar as regras de **quality dimensions** definidas em `quality/quality_rules.yaml` aos **dados** dos recursos do Data Package cujos schemas declaram `custom.qualityDimensions` (com `rulesRef` e `ruleSets`).

## Alinhamento

- **Independência de validate_schemas.py:** O script `validate_schemas.py` valida apenas a **estrutura** dos schemas (descriptors) e do datapackage, sem depender de dados. O `validate_quality.py` **depende de dados** (CSVs dos recursos) e não é acionado pelo `validate_schemas.py`; é um comando independente.
- **Regras auto-contidas:** As regras em `quality_rules.yaml` são expressões que usam apenas campos da **própria linha** (ex.: `data_vigencia_fim >= data_vigencia_inicio`). O script avalia cada linha do recurso no contexto daquela linha.

## Comportamento

1. **Datapackage:** Carrega `datapackage.yaml` e percorre os `resources`.
2. **Schema por recurso:** Para cada recurso, lê o schema indicado em `schema` e verifica se existe `custom.qualityDimensions` com `rulesRef` e `ruleSets`.
3. **Arquivo de regras:** Carrega o arquivo de regras referenciado (ex.: `quality/quality_rules.yaml`) e obtém os `ruleSets` indicados.
4. **Dados:** Carrega o CSV do recurso (caminho em `path` do recurso, relativo à raiz do projeto). Se o arquivo não existir, o recurso é pulado com aviso.
5. **Avaliação:** Para cada regra em cada ruleSet aplicável, avalia a `expression` da regra para cada linha, usando os nomes dos campos da linha como variáveis. Qualquer falha (expressão falsa ou erro de avaliação) é registrada.
6. **Saída:** Relatório por recurso/regra/linha; exit 1 se houver pelo menos um erro.

## Dependências

- **PyYAML:** Necessário para ler `datapackage.yaml` e `quality_rules.yaml`. Declarado nas dependências do projeto.

## Script e tasks

- **Script:** `scripts/validate_quality.py`.
- **Tasks:** `poetry run task validar-qualidade` (somente qualidade); `poetry run task validar-tudo` (schemas + códigos + qualidade).
- **Argumentos:** `--datapackage` e `--quality-rules` permitem alterar os caminhos do datapackage e do arquivo de regras.

## Referência nos schemas

Os schemas que possuem `custom.qualityDimensions` (ex.: `schemas/item_classificacao.yaml`, `schemas/classificacao.yaml`) indicam `rulesRef: quality/quality_rules.yaml` e `ruleSets: [temporal_consistency_bitemporal]` (ou outro conjunto). O script respeita essa configuração para decidir em quais recursos aplicar quais regras.
