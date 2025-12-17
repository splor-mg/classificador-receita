# ADR-002 — Adoção do Modelo GSIM para o Classificador de Receita

## Status

- **Estado**: Proposta
- **Data**: 2025-01-XX
- **Decisor(es)**: AID
- **Participantes**: DCAF

## Contexto

O projeto visa implementar um **sistema de gestão do Classificador de Natureza de Receita** alinhado a padrões internacionais de classificações estatísticas. O modelo de dados atual é ad hoc, sem alinhamento explícito a padrões internacionais, o que dificulta tratar de forma consistente séries de classificações, versões normativas versus atualizações menores, variantes (extensão, agregação, reagrupamento) e classificação flutuante com histórico. Referências já adotadas em `docs/referencias/` incluem o GSIM Statistical Classifications Model v1.1 (2015), GSIM v2.0 (2023) e as Best Practice Guidelines for Developing International Statistical Classifications (2022).

## Decisão

Adotar o **GSIM Statistical Classifications Model v1.1** como **modelo conceitual de referência** para o domínio de classificações de receita, com as seguintes diretrizes:

1. **Adoção de objetos centrais do GSIM**
   - Modelar explicitamente, no banco de dados, pelo menos os seguintes conceitos:
     - `ClassificationSeries` (Série de Classificações).
     - `StatisticalClassification` (Classificação Estatística).
     - `ClassificationVersion` (Versão da Classificação).
     - `ClassificationVariant` (Variante de Classificação).
     - `ClassificationItem` (Item/Código de Classificação).
     - `ClassificationLevel` (Nível hierárquico).
   - Outras entidades do GSIM poderão ser adicionadas conforme necessidade (por exemplo, correspondências entre classificações, notas explicativas, remissivas).

2. **Terminologia padronizada**
   - Utilizar a terminologia do GSIM nas tabelas, documentação e APIs, sempre que possível:
     - Ex.: “versão da classificação” ≈ `ClassificationVersion`; “série de classificações” ≈ `ClassificationSeries`.
   - Quando houver conflito com termos do MCASP ou legislações nacionais, registrar claramente os mapeamentos e diferenças na documentação (`docs/referencias`).

3. **Tratamento formal de versões, atualizações e variantes**
   - **Versão (Version)**:
     - Reservada para mudanças que alteram **fronteiras conceituais** entre categorias (divisões, fusões, realocações significativas).
   - **Atualização (Update)**:
     - Para mudanças editoriais ou incrementais que **não** alteram fronteiras de categorias (ajustes de texto, notas, exemplos).
   - **Variantes (Variants)**:
     - Modeladas explicitamente para extensões, agregações e reagrupamentos necessários a relatórios e normas específicas de MG, mantendo vínculo conceitual com a classificação de origem.
   - Essa distinção deve ser refletida no schema e na governança (fluxos de aprovação da DCAF).

4. **Base predominantemente descritiva com referência prescritiva**
   - O banco de dados será uma **base descritiva**:
     - Registra não apenas as classificações padrão, mas também variantes e usos reais (relatórios, exigências legais subnacionais).
   - As classificações padrão (nacionais/internacionais) serão tratadas como **núcleo prescritivo**, servindo como referência conceitual e ponto de ancoragem para as variantes de MG.

5. **Alinhamento com GSIM v2.0 e boas práticas**
   - Usar o GSIM v1.1 como **modelo principal** para classificações,
   - Mas consultar o **GSIM v2.0** e as **Best Practice Guidelines** para:
     - Governança de alterações,
     - Documentação de decisões,
     - Integração com outros metadados estatísticos (quando relevante).

## Alternativas Consideradas

### Alternativa 1: Modelo ad hoc específico para MG (sem GSIM)

- **Descrição**: Construir um modelo "sob medida" apenas com base em necessidades atuais.
- **Prós**: Flexibilidade total para atender necessidades específicas de MG; sem dependência de padrões externos.
- **Contras**: Dificulta alinhamento com padrões internacionais; aumenta risco de inconsistências conceituais (por exemplo, mistura de versões, atualizações e variantes sem distinção formal).
- **Razão da rejeição**: Dificulta alinhamento com padrões internacionais; aumenta risco de inconsistências conceituais (por exemplo, mistura de versões, atualizações e variantes sem distinção formal).

### Alternativa 2: Adoção total do GSIM v2.0 sem adaptação

- **Descrição**: Tentar transpor diretamente todo o GSIM v2.0 para o banco de dados.
- **Prós**: Alinhamento completo com o padrão mais recente; cobertura abrangente de conceitos.
- **Contras**: Escopo excessivo; complexidade desnecessária para o domínio atual; foco do projeto é o subdomínio de classificações.
- **Razão da rejeição**: Escopo excessivo; complexidade desnecessária para o domínio atual; foco do projeto é o subdomínio de classificações.

### Alternativa 3: Uso apenas de boas práticas, sem modelo conceitual explícito

- **Descrição**: Seguir apenas as diretrizes de boas práticas da ONU, mantendo o modelo atual.
- **Prós**: Menor esforço de implementação; mantém modelo existente.
- **Contras**: Perde os benefícios de um vocabulário e estrutura conceitual bem definidos (objetos, atributos e relacionamentos).
- **Razão da rejeição**: Perde os benefícios de um vocabulário e estrutura conceitual bem definidos (objetos, atributos e relacionamentos).

## Consequências

### Positivas

- Alinhamento com o **estado da arte internacional** em classificações estatísticas.
- Modelo de dados mais claro e extensível (facilita futuras integrações e comparações).
- Melhor governança de versões, variantes e histórico, em sinergia com a bitemporalidade (ADR-001).

### Negativas / Riscos

- Curva de aprendizado para equipe (GSIM e terminologia relacionada).
- Necessidade de adaptações cuidadosas para respeitar especificidades do classificador de MG (13 dígitos, 9 níveis).
- Possível necessidade de ajustes no futuro para acompanhar evoluções do GSIM v2.0.

## Referências

- UNECE. (2015). *GSIM: Statistical Classifications Model v1.1*. Disponível em `docs/referencias/`.
- UNECE. (2023). *GSIM v2.0 – Generic Statistical Information Model*. Disponível em `docs/referencias/`.
- UNSD. (2022). *Best Practice Guidelines for Developing International Statistical Classifications*. Disponível em `docs/referencias/`.
- [ADR-001: Estratégia de Bitemporalidade no Banco de Dados do Classificador](ADR-001-bitemporalidade.md)


