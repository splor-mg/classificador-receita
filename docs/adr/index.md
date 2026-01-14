---
title: Introdução
description: Sobre Architecture Decision Records - ADRs
---

# Registros de Decisão Arquitetural (ADRs)

Este diretório contém os **Registros de Decisão Arquitetural (Architecture Decision Records - ADRs)** do projeto do **Classificador de Natureza de Receita do Estado de Minas Gerais**.

Os ADRs documentam decisões arquiteturais importantes, capturando o contexto, as alternativas consideradas, a decisão tomada e suas consequências. Isso permite que futuros desenvolvedores e stakeholders compreendam o "porquê" por trás das escolhas técnicas do projeto.

## Sobre ADRs

Cada ADR segue uma estrutura padronizada que inclui:

- **Contexto**: Situação que levou à necessidade de uma decisão
- **Decisão**: Escolha arquitetural tomada
- **Alternativas Consideradas**: Outras opções avaliadas e por que foram rejeitadas
- **Consequências**: Impactos positivos e negativos da decisão
- **Status**: Estado atual da decisão (Proposta, Decidido, Substituído, etc.)

Para mais informações sobre o formato e boas práticas de ADRs, consulte:
- [Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) (Michael Nygard)
- [MADR - Markdown Architecture Decision Records](https://adr.github.io/madr/)

## Quando criar uma ADR

Crie uma ADR quando a decisão arquitetural:
- **Impacta a estrutura de dados ou modelagem do banco de dados** (esquemas, normalização, estratégias temporais, índices)
- **Envolve escolhas de tecnologia de persistência** (SGBD, extensões, ferramentas)
- **Afeta múltiplos componentes ou sistemas** e tem impacto de longo prazo
- **Pode ser questionada no futuro** e requer justificativa documentada
- **Apresenta trade-offs significativos** entre alternativas técnicas

Não crie ADRs para decisões rotineiras, implementações diretas de requisitos funcionais ou escolhas triviais sem alternativas relevantes.

## Rito para aprovação

1. **Elaboração**: Desenvolvedor ou arquiteto redige a ADR com contexto, alternativas e consequências
2. **Revisão técnica**: Equipe técnica responsável pela manutenção do negócio revisa a proposta, sugere ajustes e valida alternativas consideradas
3. **Aprovação**: Stakeholders responsáveis (DCAF e AID) aprovam formalmente a decisão
4. **Status**: ADR é marcada como "Decidido" e data de aprovação é registrada
5. **Comunicação**: Decisão é comunicada à equipe e documentação é atualizada conforme necessário

ADRs em status "Proposta" são rascunhos sujeitos a alterações. Apenas ADRs "Decidido" representam decisões arquiteturais aprovadas e devem ser seguidas.

## Convenção de nomenclatura

Os arquivos ADR seguem o padrão de nomenclatura: `adr-[número]_[nome-resumido-separado-por-hifen].md`


**Diretrizes:**
- Use números sequenciais para manter ordem cronológica
- O nome deve ser curto, descritivo e em português
- Evite caracteres especiais além de hífens e underscore's no nome
- Mantenha consistência na formatação

## ADRs do Projeto

| ID | Título | Status | Data |
|----|--------|--------|------|
| [ADR-001](adr-001_bitemporalidade.md) | Estratégia de Bitemporalidade no Banco de Dados do Classificador | Proposta | - |
| [ADR-002](adr-002_gsim.md) | Adoção do Modelo GSIM para o Classificador de Receita | Proposta | - |

---


