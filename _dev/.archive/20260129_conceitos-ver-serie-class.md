---
title: Conceitos GSIM - Série, Classificação e Versão
description: Responsabilidades e diferenças entre Série de Classificações, Classificação Estatística e Versão da Classificação
---

# Conceitos GSIM: Série, Classificação e Versão

Este documento registra as **responsabilidades** e a **razão de ser** das três entidades centrais do modelo de dados do classificador de receita, alinhadas ao [GSIM Statistical Classifications Model](referencias/gsim_v1_1_unece_ONU_2015.md). A adoção explícita desses conceitos está registrada no [ADR-002](adr/adr-002_gsim.md).

---

## Tabela de responsabilidades

| Entidade          | Pergunta que responde                             | O que guarda                                                                                                                                        |
| ----------------- | ------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Série**         | "Qual é o produto/conceito?"                      | Identidade do classificador ao longo do tempo (nome do "produto", órgão, propósito). Não guarda estrutura nem datas de lançamento.                  |
| **Classificação** | "Qual é a edição/estrutura em vigor?"             | Uma edição concreta: tipo (hierárquica), número de níveis, vigência no mundo real. É a entidade que **tem** níveis e itens (códigos).               |
| **Versão**        | "Como se chama e quando foi lançada esta edição?" | Metadado de lançamento: número da versão (2023, 2024), nome, data de publicação, descrição das mudanças (sobretudo de fronteiras entre categorias). |

---

## Por que as três são separadas

### Responsabilidades diferentes

Cada entidade responde a uma pergunta distinta e guarda um tipo de informação diferente. Juntar tudo numa só tabela misturaria "o que é o produto", "qual é a estrutura desta edição" e "como rotulamos e publicamos esta edição", gerando redundância ou muitos campos opcionais.

### Cardinalidades diferentes (1 × N)

- **Uma Série** → **várias Classificações** (ex.: Série "Receita MG" tem a classificação 2023, 2024, 2025…).
- **Uma Classificação** → **uma ou mais Versões** (no tempo; ex.: a classificação 2023 tem o registro de versão "Versão 2023", que pode ter atualizações bitemporais).

Separar permite que cada tabela tenha só os campos que fazem sentido para aquele conceito e que a relação 1–N fique explícita (FKs).

### Ciclos de vida diferentes

- **Série:** nasce uma vez ("criamos o classificador de receita MG") e pode só ter *atualizações* (ex.: mudança de nome ou de órgão). Não "lança" nova série a cada ano.
- **Classificação:** nova *edição* quando a estrutura muda de forma relevante (novos níveis, nova vigência). Ex.: "edição 2023", "edição 2024". Cada edição tem sua própria vigência (valid_time).
- **Versão:** está ligada a *uma* classificação e descreve o "lançamento" dessa edição (número, data, texto). Pode ter *atualizações* (ex.: corrigir a descrição da versão) sem criar nova classificação.

### Reuso e consistência

- **Série** é o ponto único de verdade para "qual classificador é este". Se o órgão responsável mudar, atualiza na série; não precisa alterar cada "versão" ou "edição".
- **Classificação** é o ponto único de verdade para "esta edição tem 9 níveis, vigência 2023–9999". Níveis e itens (códigos) pertencem a uma classificação.
- **Versão** é o ponto único para "esta edição se chama Versão 2023, foi lançada em 2023-01-01 e teve estas mudanças". Relatórios e documentos citam "Versão 2023"; esse rótulo e a data de lançamento ficam na tabela de versão.

---

## Resumo visual

```
Série (serie_classificacao)
  "Classificador de Receita MG"
  │
  ├── Classificação (classificacao_receita)  →  "Edição 2023" (estrutura + vigência)
  │       │
  │       └── Versão (versao_classificacao)  →  "Versão 2023" (número, lançamento, descrição)
  │
  └── Classificação (classificacao_receita)  →  "Edição 2024"
            │
            └── Versão (versao_classificacao)  →  "Versão 2024"
```

---

## Em uma frase

- **Série** = "qual classificador?" (conceito/produto; 1 por produto).
- **Classificação** = "qual edição/estrutura?" (uma por "ano/edição"; tem níveis e itens).
- **Versão** = "como rotulamos e quando lançamos esta edição?" (metadado de lançamento de uma classificação).

Separar os três permite responsabilidades claras, cardinalidades 1–N corretas, ciclos de vida distintos e um único lugar para cada tipo de informação, em linha com o GSIM.

---

## Série: por que dois registros com vigência ativa (9999-12-31)?

No exemplo em `docs/assets/db_serie_classificacao.csv`, a mesma `serie_id` (SERIE-RECEITA-MG) aparece em dois registros em que **ambos** têm `data_vigencia_fim = 9999-12-31` (vigência "ativa"). Isso não significa "duas séries ativas" nem "duas vigências diferentes" para a mesma série. Segue o porquê, alinhado ao GSIM e à bitemporalidade (ADR-001).

### Dois eixos de tempo (bitemporalidade)

- **Valid time (vigência):** "Quando este fato é verdade no mundo real?" — ex.: "a série existe e é válida de 2023-01-01 a 9999-12-31".
- **Transaction time (registro):** "Quando o sistema passou a considerar esta informação como verdade?" — ex.: "desde 2024-08-20 14:30:00 nós registramos que o nome/descrição da série é X".

Para a **Série**, o "fato" no mundo real é a **identidade/conceito** do classificador (que ele existe, com certo nome, descrição e órgão). Quando fazemos apenas uma **atualização** (mudança de nome ou descrição, sem criar nova série):

- No mundo real, a série **não** "começou" nem "terminou" em outra data; ela segue válida no mesmo intervalo (2023-01-01 a 9999-12-31).
- O que mudou foi **nosso registro** (o que colocamos no sistema): primeiro tínhamos "nome A, descrição B"; depois corrigimos para "nome A′, descrição B′".

Por isso **os dois registros têm o mesmo intervalo de vigência** (2023-01-01 a 9999-12-31): estamos representando o **mesmo** período de validade da série, em **duas revisões** do nosso conhecimento sobre ela. A diferença está só no **registro** (`data_registro_inicio` / `data_registro_fim`):

- **Primeiro registro:** "O que tínhamos registrado até 2024-08-20 14:30:00" — `data_registro_fim` fechada nessa data.
- **Segundo registro:** "O que passamos a registrar a partir de 2024-08-20 14:30:00" — `data_registro_fim = 9999-12-31 23:59:59` (registro "atual").

Ou seja: há **uma** série, **um** intervalo de vigência; os dois linhas são duas **versões do registro** (transaction time), não duas vigências distintas.

### Boa prática: "vigência ativa" vs "registro ativo"

- **Vigência ativa** (`data_vigencia_fim = 9999-12-31`): "Este fato é válido no mundo real até hoje (e adiante)". Vários registros podem ter vigência ativa se forem **revisões** do mesmo fato (como no update da série).
- **Registro ativo** (`data_registro_fim = 9999-12-31 23:59:59`): "Esta é a versão **atual** do que o sistema considera verdade". Para um dado `serie_id`, em um dado momento só deve existir **um** registro ativo.

Assim, para "qual é a série hoje?" ou "qual é a identidade do classificador?", a consulta deve usar **registro ativo** (por exemplo `data_registro_fim = '9999-12-31 23:59:59'`). Nesse critério, continua existindo **uma única** "série ativa" por `serie_id`; os outros registros são histórico de alterações (ex.: nome/descrição antigos).

### Resumo

| Pergunta                                                             | Critério                                  | Resultado no exemplo                                                                              |
| -------------------------------------------------------------------- | ----------------------------------------- | ------------------------------------------------------------------------------------------------- |
| "Quantas séries SERIE-RECEITA-MG estão vigentes (no mundo real)?"    | `data_vigencia_fim = 9999-12-31`          | Dois registros — mas representam o **mesmo** intervalo de vigência (duas revisões do mesmo fato). |
| "Qual é a série SERIE-RECEITA-MG **atualmente** (visão do sistema)?" | `data_registro_fim = 9999-12-31 23:59:59` | **Um** registro (nome/descrição atualizados em 2024).                                             |

Em conformidade com o GSIM e com boas práticas bitemporais: a **identidade** da série (uma por conceito) é preservada; múltiplos registros com vigência 9999-12-31 para o mesmo `serie_id` são **atualizações** (transaction time) do mesmo fato, não "duas vigências ativas" em conflito.
