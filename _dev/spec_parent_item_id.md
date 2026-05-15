# Especificação: regra de `parent_item_id` em `item_classificacao`

## Objetivo

Definir a regra de negócio para o campo `parent_item_id` na hierarquia de `item_classificacao`, garantindo coerência estrutural, semântica e temporal entre item filho e item mãe.

## Alinhamento

- **Hierarquia por nível:** o vínculo pai-filho deve respeitar o nível imediatamente anterior.
- **Semântica do código:** o mãe representa a versão não detalhada do filho no nível subsequente, com uso de zeros canônicos.
- **Bitemporalidade:** a validação deve considerar vigência (tempo válido) e registro (tempo de transação), não apenas status ativo no momento atual.

## Regras obrigatórias

- Para todo item com `nivel_numero > 1`, `parent_item_id` é obrigatório.
- Para item com `nivel_numero = 1`, `parent_item_id` deve ser nulo.
- O `parent_item_id` deve ter `matriz = true` (não pode ser detalhe).
- O `parent_item_id` deve estar no nível imediatamente anterior (`nivel_numero_mãe = nivel_numero_filho - 1`).
- mãe e filho devem pertencer à mesma `classificacao_id`.
- Campos com "zeros canônicos" são considerados como não discriminados ("não detalhados").
- O `parent_item_id` deve referenciar registro com vigência compatível com o filho: **a vigência do mãe deve conter integralmente a vigência do filho** (único eixo temporal exigido para este vínculo na validação de domínio).

## Regra semântica por segmentos de código

Para um filho no nível `N`:

- Segmentos correspondentes aos níveis `1..N-1` no mãe devem ser iguais aos do filho.
- Segmentos correspondentes aos níveis `N..fim` no mãe devem estar com zero canônico do nível (ex.: `0`, `00`, `000`, conforme máscara do nível).
- No filho, o segmento do nível `N` deve estar discriminado (diferente de zero canônico).
- No filho, segmentos correspondentes aos níveis `N+1..fim` devem estar em zero canônico (respeitando a máscara da classificação).

## Casos de aceite mínimos

- Filho nível 1 com mãe informado -> rejeita.
- Filho nível 3 sem mãe -> rejeita.
- Filho nível 4 com mãe nível 2 -> rejeita.
- Filho nível 5 com mãe `matriz=false` -> rejeita.
- Filho nível 7 com prefixo diferente do mãe até nível 6 -> rejeita.
- Filho nível 7 com mãe correto, mas sem zeros canônicos de 8..fim -> rejeita.
- Filho nível 7 com mãe correto e vigência incompatível -> rejeita.
- Filho nível 7 com mãe correto e vigência compatível -> aceita.
- Filho nível 7 com mãe correto, mas com nível 7..fim do mãe sem zeros canônicos -> rejeita.
- Filho nível 7 com segmento do próprio nível 7 em zero canônico -> rejeita.
- Filho nível 7 com segmentos 8..fim sem zeros canônicos -> rejeita.
- Filho nível 7 com mãe semanticamente correto, mas vigência incompatível -> rejeita.
- Filho nível 7 com mãe semanticamente correto e vigência compatível -> aceita.
- Filho cujo mãe não está com registro ativo no sistema hoje, mas cuja vigência ainda contém a vigência do filho -> aceita.

Ver também: `_dev/spec_validar_item_pai.md` (admin: aviso de salto de nível e listagem de itens intermediários antes do submit); `_dev/spec_lookup_hierarquia_por_codigo_admin.md` (endpoints JSON de lookup de código e hierarquia no admin).

