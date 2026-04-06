# Especificação: validação de códigos (validate_code.py)

## Alinhamento

- **GSIM:** O código canônico (receita_cod) é atributo do Classification Item; a quantidade de dígitos é definida na Statistical Classification (e nos níveis). A validação usa metadados da classificação para o período apropriado.
- **SCD-2 / bitemporal:** O script considera **duas dimensões temporais**: vigência (quando o fato vale no mundo) e registro (quando o sistema considerou o fato verdadeiro). A resolução da classificação segue a ordem abaixo.
- **Fonte de dados:** Instâncias em `item_classificacao` (itens) e tabela/CSV de **classificação** (ex.: `schemas/classificacao.yaml` / `docs/assets/seed_classificacao.csv`), com campos de vigência e registro.

## Ponto de partida: período de registro

A validação **começa** pelo **período de registro** (transaction time), não pela vigência.

Para cada linha de item (código) em `item_classificacao`:

1. **Registro do item:** usa-se `data_registro_inicio` e `data_registro_fim` dessa linha.
2. **Busca na tabela de classificação:** consideram-se apenas linhas da mesma `classificacao_id` cujo **período de registro** **compreenda** o período de registro do item. Ou seja: o intervalo de registro da classificação deve conter o intervalo de registro do item (classificação “ativa no sistema” durante todo o tempo em que essa versão do item esteve ativa no sistema).

## Em seguida: vigência

A **vigência** é obrigatória e não deve ser desconsiderada.

Entre as linhas de classificação já filtradas por registro (passo anterior), mantêm-se apenas aquelas cuja **vigência** **compreenda** a vigência do item. Ou seja: a vigência da classificação deve conter a vigência do item (`data_vigencia_inicio` e `data_vigencia_fim` do item dentro do intervalo de vigência da classificação).

Assim, a ordem é: (1) filtrar por registro; (2) filtrar por vigência.

## Múltiplas linhas de classificação

É possível que, para um mesmo item, exista **mais de uma** linha na tabela de classificação que atenda aos dois critérios (registro compreende o registro do item; vigência compreende a vigência do item). Isso é aceitável.

Para o teste ser considerado **válido**:

- A quantidade de dígitos de `receita_cod` deve ser **correspondente a cada uma** das linhas de classificação encontradas.
- Ou seja: **todas** essas linhas devem ter o **mesmo** `numero_digitos`, e `len(receita_cod)` deve ser igual a esse valor.

O teste **falha** se:

- **Não** for encontrada nenhuma linha de classificação com registro e vigência compatíveis; ou
- Forem encontradas duas ou mais linhas de classificação com **valores diferentes** de `numero_digitos`; ou
- O `numero_digitos` vigente (e com registro compatível) for único, mas `len(receita_cod)` for **diferente** desse valor.

## Script e entrada de dados

- **Script:** `scripts/validate_code.py`.
- **Tasks:** `poetry run task validar-codigos` (somente códigos); `poetry run task validar-tudo` (schemas + códigos + qualidade).
- **Entradas:** CSV de itens (ex.: `data/item_classificacao.csv`) e CSV de classificação (ex.: `docs/assets/seed_classificacao.csv`). Argumentos `--items` e `--classificacao` permitem alterar os caminhos.
- Se o arquivo de itens não existir, o script termina com sucesso (exit 0) e mensagem informativa, sem falhar o pipeline.

## Referência no schema

A regra e o script estão documentados em `schemas/item_classificacao.yaml` em `custom.codeValidation`.
