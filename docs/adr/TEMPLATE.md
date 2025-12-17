# ADR-XXX — [Título Descritivo e Específico da Decisão]

## Status

- **Estado**: [Proposta | Decidido | Substituído]
- **Data**: YYYY-MM-DD
- **Decisor(es)**: [DCAF | AID | Equipe responsável]
- **Participantes**: [Outros envolvidos na discussão]

## Contexto

Descrever a situação que levou à necessidade desta decisão, explicando o problema ou necessidade a ser resolvido, a situação atual e suas limitações, as forças em jogo (restrições técnicas, de negócio, políticas, temporais, etc.), os requisitos não-funcionais relevantes (performance, segurança, escalabilidade, manutenibilidade, auditoria, conformidade, etc.) e os stakeholders afetados. É importante explicar a situação organizacional e as prioridades de negócio, incluindo considerações baseadas na composição social e nas habilidades das equipes.

## Decisão

Declaração clara e direta da decisão tomada. A decisão deve ser específica (evitando ambiguidades), ação-orientada (indicando o que será feito, não apenas o que será considerado) e justificada (explicando por que esta escolha foi feita; a justificativa detalhada pode estar na seção de Consequências).

### Diretrizes de implementação

*(Opcional - se aplicável)*

Listar diretrizes, padrões ou convenções que devem ser seguidas:

1. [Diretriz específica 1]
2. [Diretriz específica 2]
3. [Diretriz específica 3]

## Alternativas Consideradas

Listar as alternativas que foram avaliadas, incluindo:

### Alternativa 1: [Nome da alternativa]

- **Descrição**: O que seria feito
- **Prós**: Vantagens
- **Contras**: Desvantagens
- **Razão da rejeição**: Por que não foi escolhida

### Alternativa 2: [Nome da alternativa]

- **Descrição**: O que seria feito
- **Prós**: Vantagens
- **Contras**: Desvantagens
- **Razão da rejeição**: Por que não foi escolhida

### Alternativa 3: [Nome da alternativa - pode ser "Não fazer nada"]

- **Descrição**: O que seria feito (ou não feito)
- **Prós**: Vantagens
- **Contras**: Desvantagens
- **Razão da rejeição**: Por que não foi escolhida

## Consequências

Explicar o que segue da decisão: efeitos, resultados, outputs, follow-ups.

### Positivas

- [Benefício 1]
- [Benefício 2]
- [Benefício 3]

### Negativas / Riscos

- [Desvantagem ou risco 1]
- [Desvantagem ou risco 2]
- [Desvantagem ou risco 3]

### Mitigações

*(Opcional - para cada risco identificado)*

- **Risco**: [Descrição do risco]
  - **Mitigação**: [Como será mitigado]
  - **Responsável**: [Quem monitora/mitiga]

### ADRs Subsequentes

*(Opcional - se esta decisão gerar necessidade de outras decisões)*

Esta decisão pode gerar necessidade de ADRs adicionais:
- [ADR-XXX]: [Descrição da decisão relacionada]

### Impactos em outras áreas

*(Opcional - quando relevante)*

- **Código**: [Mudanças necessárias no código]
- **Infraestrutura**: [Mudanças em deploy, configuração, etc.]
- **Documentação**: [O que precisa ser documentado]
- **Treinamento**: [Conhecimento necessário para a equipe]

## Assumptions

*(Opcional - quando relevante)*

Premissas do ambiente em que a decisão está sendo tomada:

- **Custo**: [Premissas sobre custos]
- **Cronograma**: [Premissas sobre prazos]
- **Tecnologia**: [Premissas sobre tecnologias disponíveis]
- **Equipe**: [Premissas sobre habilidades e disponibilidade da equipe]

## Constraints

*(Opcional - quando relevante)*

Restrições adicionais que a decisão pode impor ao ambiente:

- [Restrição 1]
- [Restrição 2]

## Governance

*(Opcional - quando relevante para auditoria e conformidade)*

Como a decisão será monitorada e como a conformidade será garantida:

- **Monitoramento**: [Como será monitorado]
- **Conformidade**: [Como será garantida]
- **Responsável**: [Quem é responsável pelo monitoramento]

## Referências

- [Link ou referência 1]
- [Link ou referência 2]
- [ADR relacionado: ADR-XXX]

## Notas de Implementação

*(Opcional - para ADRs já decididos, usando abordagem de "documento vivo")*

Adicionar novas informações com timestamp quando houver:
- Resultados reais de uso
- Mudanças de terceiros (ex.: capacidades do SISOR, mudanças de API)
- Novos membros da equipe com informações adicionais

**Exemplo**:
```markdown
**YYYY-MM-DD**: Implementação concluída. Resultados observados:
- [Resultado 1]
- [Resultado 2]

**YYYY-MM-DD**: Atualização pós-[evento]:
- [Mudança observada]
```

## Histórico de Mudanças

*(Opcional - para ADRs que foram atualizados)*

- **YYYY-MM-DD**: [Descrição da mudança e razão]

---

## Notas sobre este Template

Este template segue o formato original proposto por **Michael Nygard** em [Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions), com extensões práticas para o contexto do projeto Classificador de Receita.


### Referências

Para mais informações sobre ADRs e boas práticas, consulte:
- [Anotações sobre ADRs](../referencias/adr_architecture-decision-record_notes.md) — guia específico para este projeto
- [architecture-decision-record](https://github.com/joelparkerhenderson/architecture-decision-record) — repositório de referência
- [MADR (Markdown ADR)](https://adr.github.io/madr/) — formato alternativo com metadados YAML


