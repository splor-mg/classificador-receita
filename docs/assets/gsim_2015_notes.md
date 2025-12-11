# O GSIM - Generic Statistical Information Model - Seção 1 (Introdução)

Este documento fornece uma explicação sobre o GSIM Statistical Classifications Model, com foco na aplicação ao projeto do Classificador de Natureza de Receita do Estado de Minas Gerais.

---

## O que é o GSIM?

**GSIM (Generic Statistical Information Model)** é um **modelo de informação** desenvolvido pela comunidade estatística internacional para padronizar a forma como organizações estatísticas descrevem, estruturam e gerenciam informações ao longo de todo o ciclo de produção estatística, bem como para fornecer liguagem comum e framework conceitual para desenvolvimento de sistemas.

Um **modelo de informação** é uma representação abstrata e conceitual que define objetos, seus atributos, relacionamentos e uma terminologia comum dentro de um domínio — no caso estatístico, por exemplo, classificações, variáveis e conceitos. Suas principais características são a abstração (focando no significado e propósito, e não na implementação técnica), a independência tecnológica, a possibilidade de reutilização por diferentes organizações e a promoção da interoperabilidade entre sistemas, permitindo comunicação clara e compartilhamento eficiente de informações.

Historicamente, a fragmentação de terminologias e sistemas entre organizações motivou sua criação. O GSIM evoluiu a partir do projeto inicial patrocinado pelo High Level Group (HLG) a partir de 2009, incorporando o modelo Neuchâtel (específico para classificações) em 2013, e vem sendo adotado como padrão desde então.

Seu propósito central é promover a padronização e a interoperabilidade, fornecendo uma linguagem comum para que sistemas e organizações "conversem" entre si. Ele atua como um framework conceitual para o desenvolvimento de sistemas, especificando os objetos de informação essenciais. Complementa o GSBPM (Generic Statistical Business Process Model), que descreve os processos, enquanto o GSIM descreve os objetos de informação manipulados nesses processos, sendo crucial para a modernização da produção estatística.

Estruturalmente, o GSIM é organizado em **Groups** (grupos de objetos de informação relacionados). Na versão 2.0 (dezembro 2023), o GSIM está estruturado em cinco grupos principais: Base Group, Business Group, Concept Group, Exchange Group e Structure Group. O GSIM Statistical Classifications Model, foco deste documento, foi originalmente desenvolvido como parte do modelo Neuchâtel e integrado ao GSIM em 2013, fornecendo os conceitos específicos para modelagem de classificações estatísticas. 

Para o projeto do Classificador de Natureza de Receita, o GSIM oferece a estrutura para modelar o classificador como uma Statistical Classification hierárquica e normativa, onde cada código é um Classification Item, os grupos são Levels e o histórico de alterações deve suportar os conceitos de versão, atualização e o princípio da floating classification através da bitemporalidade.

_Referências_
  - [Generic Statistical Information Model (GSIM)](https://unece.org/statistics/modernstats/gsim)
  - [GSIM: Statistical Classifications Model v1.1](https://unstats.un.org/unsd/classifications/expertgroup/egm2015/ac289-22.PDF)
  - [GSIM version v2.0](https://unece.github.io/GSIM-2.0/)
  - [GSIM version v2.0 - User Guide](https://unece.org/sites/default/files/2025-03/GSIM%20User%20Guide.pdf)
  - [GSIM old versions](https://statswiki.unece.org/spaces/gsim/pages/68781449/Old+versions+of+GSIM)


#### Linha do Tempo

**Junho 1999: Origem do Modelo Neuchâtel**
- Reunião em Neuchâtel, Suíça, com escritórios estatísticos da Dinamarca, Noruega, Suécia e Suíça com a participação de desenvolvedores da Run Software-Werkstatt
- **Objetivo inicial**: Criar uma terminologia comum para classificações estatísticas
- **Resultado**: Definição dos conceitos-chave e framework conceitual para desenvolvimento de bancos de dados de classificações
- **Princípios fundamentais estabelecidos**:
  - Foco prático: Todas as organizações participantes planejavam usar o modelo em suas próprias implementações
  - Propósitos principais: Facilitar acesso e manutenção de classificações; garantir uso comum de classificações em diferentes áreas de estatística
  - Princípio central: "Documentar e atualizar uma vez (centralmente), reutilizar onde for relevante"
- **Relevância para o projeto**: O Classificador de Natureza de Receita se beneficia do mesmo princípio: uma fonte única de verdade (banco de dados centralizado) elimina a duplicação entre SISOR e Excel

**2002: Modelo Neuchâtel v2.0**
- Versão 2.0 do modelo Neuchâtel lançada
- Consolidação dos conceitos e terminologia desenvolvidos desde 1999

**2004: Modelo Neuchâtel v2.1**
- Statistics Netherlands juntou-se ao grupo Neuchâtel
- Adicionado um novo objeto e um novo atributo ao modelo
- Versão 2.1 do modelo Neuchâtel lançada
- **Princípios essenciais mantidos**:
  - Flexibilidade: O modelo deve ser adaptável a diferentes necessidades e políticas
  - Independência de tecnologia: Não depende de software ou plataformas específicas
  - Acesso público e gratuito: O trabalho deve estar disponível para qualquer pessoa
- **Resultado prático**: Cada organização implementou o modelo de forma diferente, adaptando às suas necessidades específicas (exemplos: BridgeNA, sistemas nacionais de vários países)
- **Relevância para o projeto**: O modelo GSIM pode ser implementado em PostgreSQL + Django, sem depender de soluções proprietárias; permite adaptação às necessidades específicas do Estado de Minas Gerais (13 dígitos, 9 níveis, integração com SISOR)

**2009-2011: Início do Projeto GSIM**
- Patrocinado pelo **High Level Group for the Modernization of Statistical Production and Services (HLG)**
- HLG é um grupo de alto nível que reúne líderes de organizações estatísticas nacionais e internacionais
- **Objetivo**: Criar um modelo de informação genérico para toda a produção estatística
- **Contexto**: Muitos países já haviam implementado o modelo Neuchâtel (18 países listados: Austria, Belgium, Bulgaria, Canada, Croatia, Czech Republic, Denmark, Estonia, Germany, Greece, Ireland, Norway, Portugal, Slovak Republic, Slovenia, Sweden, Switzerland, Netherlands)
- Após anos de experiência prática, surgiu necessidade de revisão do modelo Neuchâtel
- O grupo Neuchâtel original não existia mais

**2011: Workshop METIS e Início da Revisão**
- Discussão no Workshop METIS sobre possível revisão do modelo Neuchâtel
- METIS: acrônimo para o grupo conjunto UNECE / Eurostat / OECD) para metadados estatísticos
- Criação de grupo de trabalho conjunto: UN Expert Group on International Statistical Classifications + METIS Steering Group
- Grupo reuniu especialistas em classificações e metadados estatísticos

**2011-2013: Desenvolvimento e Integração**
- Integração do modelo Neuchâtel (específico para classificações) no GSIM mais amplo
- Desenvolvimento colaborativo envolvendo múltiplas organizações estatísticas
- **GSIM - O que é**:
  - Framework de objetos de informação que suporta todos os processos de produção estatística
  - Fornece nomes acordados, definições, propriedades essenciais e relacionamentos entre objetos de informação
  - Os objetos relacionados a classificações foram majoritariamente extraídos do modelo Neuchâtel
- Versão 1.0 do GSIM lançada
- Durante o trabalho de revisão, decidiu-se que o modelo Neuchâtel para classificações seria parte do GSIM no futuro

**2013: GSIM Statistical Classifications Model v1.1**
- O modelo Neuchâtel revisado tornou-se parte oficial do GSIM
- Versão 1.1 do GSIM Statistical Classifications Model (dezembro 2013)
- Publicado como anexo ao GSIM principal
- **Resultado**: O modelo revisado é, na prática, um anexo ao GSIM; vários objetos e atributos foram alterados durante o processo de revisão
- **Pesquisa de uso (2013)**:
  - Questionário investigou uso de padrões relevantes a classificações
  - Respostas de 18 países/organizações internacionais: Australia, Austria, Canada, Croatia, Estonia, France, Germany, Ireland, Netherlands, New Zealand, Norway, Portugal, Slovenia, Sweden, Switzerland, United States, Eurostat, ILO
  - Resultados mostram ampla adoção do modelo Neuchâtel
- **Relevância para o projeto**: O GSIM Statistical Classifications Model é a versão mais atual e revisada do modelo Neuchâtel; representa o estado da arte em modelagem de classificações estatísticas; garante alinhamento com padrões internacionais

**2015-2023: Adoção e Evolução**
- Adoção crescente por organizações estatísticas nacionais e internacionais
- Continua evolução baseada em experiência prática
- Integração com outros padrões (SDMX, DDI, etc.)
- O modelo continua sendo mantido e atualizado pela comunidade estatística internacional
- Desenvolvimento de versões intermediárias (v1.2, etc.)

**Dezembro 2023: GSIM v2.0**
- Lançamento do GSIM versão 2.0 (dezembro 2023)
- **Reestruturação organizacional**: O GSIM v2.0 reorganizou-se em cinco **Groups** principais:
  - Base Group
  - Business Group
  - Concept Group
  - Exchange Group
  - Structure Group
- Refatorações significativas em vários grupos, incluindo melhorias em Change Events, Process Steps, Exchange Channels e Referential Metadata
- **Relevância para o projeto**: Embora o projeto utilize o GSIM Statistical Classifications Model (v1.1, 2013) como referência conceitual principal, a estrutura v2.0 representa a evolução contínua do padrão e pode ser consultada para entender o estado atual do GSIM


## Destaques

A classificação, em estatística, geralmente refere-se tanto ao ato de atribuir unidades estatísticas a categorias, quanto ao próprio conjunto estruturado e mutuamente exclusivo dessas categorias (linear ou hierárquico), podendo designar uma lista estruturada específica (como a ISIC Rev.1, válida por um tempo determinado) ou uma família de listas sucessivas ao longo do tempo (como a própria ISIC). A distinção entre uma lista específica e a série de listas nem sempre é explícita; normalmente, a palavra "classificação" é usada para grandes classificações normativas e hierárquicas. Já "nomenclatura" refere-se a uma lista de nomes e entidades, e ao se acrescentar estrutura, aproxima-se do conceito de classificação, embora os termos sejam frequentemente usados como sinônimos. No entanto, "nomenclatura" não faz parte da terminologia do GSIM.
