---
title: Apresentação
description: Sistema de Gestão do Classificador de Natureza de Receita do Estado de Minas Gerais
---

# Classificador de Natureza de Receita - MG

Sistema de gestão voltado para organização, classificação e versionamento histórico de informações do Classificador de Natureza de Receita do Estado de Minas Gerais em um banco de dados taxonômico, relacional e normalizado, permitindo rastreabilidade e consulta eficiente das categorias e alterações ao longo do tempo.

O Classificador de Natureza de Receita do Estado de Minas Gerais utiliza uma estrutura estendida de **13 dígitos**, organizada em **9 níveis hierárquicos**, permitindo maior granularidade para atender às necessidades gerenciais específicas do ente estadual.

??? info "Estrutura do código (13 dígitos): `C.0.E.D.DD.D.T.II.SSS`"
    - **C**: Categoria econômica
    - **0**: Origem
    - **E**: Espécie
    - **D**: Desdobramento 1
    - **DD**: Desdobramento 2
    - **D**: Desdobramento 3
    - **T**: Tipo da receita
    - **II**: Item da receita (exclusivo MG)
    - **SSS**: Subitem da receita (exclusivo MG)


## Documentação

### [📋 Projeto](projeto.md)
Documentação completa do projeto, incluindo contexto, escopo, requisitos e plano de trabalho.

### [🗺️ Diagrama ERD](erd/)
Visão geral do modelo entidade-relacionamento (ERD) do banco de dados do Classificador de Natureza de Receita - MG.

### [📝 ADRs - Architecture Decision Records](adr/)
Registros de decisões arquiteturais importantes do projeto:
- [ADR-001: Bitemporalidade](adr/adr-001_bitemporalidade.md)
- [ADR-002: GSIM](adr/adr-002_gsim.md)

### [📚 Referências](referencias/)
Documentação de referência e padrões utilizados:
- GSIM (Generic Statistical Information Model)
- Best Practices para Classificações Estatísticas
- Documentação sobre ADRs


