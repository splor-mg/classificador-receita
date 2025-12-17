# Anotações sobre Architecture Decision Records (ADRs)

Referência principal: [architecture-decision-record](https://github.com/joelparkerhenderson/architecture-decision-record) — repositório mantido por Joel Parker Henderson com templates, exemplos e boas práticas para ADRs.

---

## O que são ADRs

**Architecture Decision Record (ADR)** é um documento que captura uma decisão arquitetural importante junto com seu contexto e consequências.

- **AD (Architecture Decision)**: escolha de design de software que atende a um requisito significativo
- **ADL (Architecture Decision Log)**: coleção de todos os ADRs de um projeto/organização
- **ASR (Architecturally-Significant Requirement)**: requisito com efeito mensurável na arquitetura do sistema

---

## Estratégia para o Projeto Classificador de Receita

### Contexto do Projeto

- **Domínio**: Classificador de Natureza de Receita (13 dígitos, 9 níveis hierárquicos)
- **Stakeholders**: DCAF (Product Owner), AID (Executor Técnico), SPLOR (Patrocinador), órgãos de controle (TCE-MG, CGE-MG)
- **Requisitos críticos**: Bitemporalidade, rastreabilidade histórica, conformidade com MCASP, auditoria

### Abordagem Recomendada

**Formato base: Michael Nygard** (simples e popular), com extensões práticas para o contexto governamental:

1. **Simplicidade inicial**: Começar com formato Nygard (Status, Context, Decision, Consequences)
2. **Extensões conforme necessidade**: Adicionar seções específicas quando relevante (ex.: Assumptions, Constraints, Governance)
3. **Foco em rastreabilidade**: Importante para auditoria e conformidade (órgãos de controle)

---

## Características de um Bom ADR

### Essenciais (do repositório de referência)

- **Rationale**: Explicar os motivos da decisão (contexto, prós/contras, comparações, custo/benefício)
- **Specific**: Um ADR = uma decisão arquitetural (não múltiplas)
- **Timestamps**: Identificar quando cada item foi escrito (importante para custos, escalabilidade, etc.)
- **Immutable**: Não alterar informações existentes; adicionar novas informações ou criar novo ADR que substitua

### Boa Seção de Contexto

Uma boa seção de contexto deve resumir a situação organizacional e as prioridades de negócio, considerando também a composição e as habilidades da equipe envolvida, além de apresentar prós e contras relevantes sempre alinhados às necessidades e objetivos do projeto.

### Boa Seção de Consequências

Uma boa seção de consequências deve explicar de forma clara o que decorre da decisão tomada, detalhando seus efeitos, resultados esperados, outputs e possíveis desdobramentos ou ações de acompanhamento; além disso, é recomendável indicar ADRs subsequentes que formam a cadeia de decisões e abordar processos de revisão pós-implementação (after-action review) para aprendizado contínuo.

---

## Estrutura Recomendada para o Projeto

### Template Base (Nygard + Extensões)

```markdown
# ADR-XXX — [Título Descritivo]

## Status
- Estado: [Proposta | Decidido | Substituído]
- Data: YYYY-MM-DD
- Decisor(es): [DCAF | AID | Equipe]
- Participantes: [Outros envolvidos]

## Contexto
[Problema ou necessidade que motiva a decisão]
[Situação atual e limitações]
[Requisitos não-funcionais relevantes]

## Decisão
[Declaração clara e específica da decisão]
[Diretrizes de implementação, se aplicável]

## Alternativas Consideradas
[Alternativa 1: descrição, prós, contras, razão da rejeição]
[Alternativa 2: ...]
[Alternativa 3: ...]

## Consequências
### Positivas
- [Benefício 1]
- [Benefício 2]

### Negativas / Riscos
- [Risco 1]
- [Risco 2]

### Mitigações
[Como os riscos serão mitigados]

## Referências
- [Links, documentos, outros ADRs relacionados]
```

### Extensões Opcionais (quando relevante)

- **Assumptions**: Premissas do ambiente (custo, cronograma, tecnologia)
- **Constraints**: Restrições adicionais que a decisão pode impor
- **Governance**: Como a decisão será monitorada e como a conformidade será garantida
- **Related ADRs**: ADRs relacionados (cadeia de decisões)

---

## Quando Criar um ADR

### Justifica criar ADR quando:

- Decisão **afeta estrutura**, qualidade, dependências importantes ou técnicas de construção
- Futuros desenvolvedores **precisam entender o "porquê" da escolha**
- Decisão tem **impacto** em múltiplas equipes ou sistemas
- Decisão envolve **trade-offs significativos**
- Decisão é difícil de reverter ou tem custo alto de mudança

### Não justifica ADR quando:

- Decisão é limitada em escopo, tempo, risco e custo
- Decisão já está coberta em padrões, políticas ou documentação existente
- Decisão é temporária (workarounds, PoCs, experimentos)
- Decisão é de baixo risco e auto-contida

---

## Lifecycle de ADRs (Opcional)

Para projetos maiores, considerar estágios:

1. **Initiating**: Decisão identificada, ADR iniciado
2. **Researching**: Pesquisa de alternativas e trade-offs
3. **Evaluating**: Avaliação das opções
4. **Implementing**: Decisão aprovada, em implementação
5. **Maintaining**: Decisão ativa, monitoramento
6. **Sunsetting**: Decisão substituída ou deprecada


---

## Governança e Aprovação

### Processo Recomendado

1. **Propositor**: Qualquer membro da equipe (AID ou DCAF) pode propor ADR
2. **Revisão**: Equipe técnica (AID) + Product Owner (DCAF)
3. **Aprovação**: DCAF (Accountable) para decisões de negócio; AID para decisões técnicas puras
4. **Comunicação**: ADRs aprovados comunicados aos stakeholders (SPLOR, órgãos de controle, se relevante)

### Critérios de Aceite para Aprovação

- Problema claramente articulado
- Alternativas consideradas e documentadas
- Trade-offs compreendidos e documentados
- Contexto relevante presente
- Stakeholders relevantes envolvidos
- Feedback incorporado

---

## Imutabilidade vs. Documentos Vivos

### Abordagem Pragmática (recomendada para este projeto)

**Em teoria**: ADRs são imutáveis (não alterar informações existentes).

**Na prática**: Para este projeto, adotar abordagem de "documento vivo":
- Adicionar novas informações ao ADR existente com timestamp
- Notar que a informação chegou após a decisão
- Permitir atualizações quando houver:
  - Novos membros da equipe com informações adicionais
  - Resultados reais de uso
  - Mudanças de terceiros (ex.: capacidades do SISOR, mudanças de API)

**Exemplo de atualização**:
```markdown
## Notas de Implementação

**2025-01-15**: Implementação concluída. Resultados observados:
- [Resultado 1]
- [Resultado 2]

**2025-02-20**: Atualização pós-SISOR 2026:
- [Mudança observada]
```

---

## Critérios de Sustentabilidade de Decisões

Ao avaliar decisões arquiteturais, considerar:

1. **Strategic**: Impacto de longo prazo (operações futuras, manutenção)
2. **Measurable and Manageable**: Resultados mensuráveis por critérios objetivos (idealmente numéricos)
3. **Achievable and Realistic**: Solução pragmática, evitar over/under-engineering
4. **Rooted in Requirements**: Baseado em experiência de domínio e contexto (MCASP, GSIM, necessidades DCAF)
5. **Timeless**: Baseado em conhecimento que não fica obsoleto rapidamente (padrões, não tecnologias específicas)

---

## Convenções de Nomenclatura

### Arquivos ADR

- Formato: `ADR-XXX-[título-descritivo].md`
- Exemplo: `ADR-001-bitemporalidade.md`, `ADR-002-gsim.md`
- Números sequenciais (001, 002, 003...)
- Título em minúsculas com hífens

### Índice

Manter `docs/adr/index.md` atualizado com:
- Tabela de ADRs (ID, Título, Status, Data)
- Links para cada ADR
- Breve descrição do propósito dos ADRs no projeto

---

## Referências Principais

- **Repositório de referência**: [architecture-decision-record](https://github.com/joelparkerhenderson/architecture-decision-record)
- **Michael Nygard (formato original)**: [Documenting architecture decisions](http://thinkrelevance.com/blog/2011/11/15/documenting-architecture-decisions)
- **MADR (Markdown ADR)**: [adr.github.io/madr](https://adr.github.io/madr/)
- **Jeff Tyree & Art Akerman (formato sofisticado)**: [Architecture Decisions: Demystifying Architecture](https://www.utdallas.edu/~chung/SA/zz-Impreso-architecture_decisions-tyree-05.pdf)
- **AWS Prescriptive Guidance**: [ADR Process](https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html)

*Última atualização: 2025-12-16*

