# O GSIM - Generic Statistical Information Model - Seção 1 (Introdução)

Este documento fornece uma explicação sobre o GSIM Statistical Classifications Model, com foco na aplicação ao projeto do Classificador de Natureza de Receita do Estado de Minas Gerais.

---

## O que é o GSIM?

**GSIM (Generic Statistical Information Model)** é um **modelo de informação** desenvolvido pela comunidade estatística internacional para padronizar a forma como organizações estatísticas descrevem, estruturam e gerenciam informações ao longo de todo o ciclo de produção estatística, bem como para fornecer liguagem comum e framework conceitual para desenvolvimento de sistemas. 

Seu propósito central é promover a padronização e a interoperabilidade, fornecendo uma linguagem comum para que sistemas e organizações "conversem" entre si.

Um **modelo de informação** é uma representação abstrata e conceitual que define objetos, seus atributos, relacionamentos e uma terminologia comum dentro de um domínio — no caso estatístico, por exemplo, classificações, variáveis e conceitos. Suas principais características são a abstração (focando no significado e propósito, e não na implementação técnica), a independência tecnológica, a possibilidade de reutilização por diferentes organizações e a promoção da interoperabilidade entre sistemas, permitindo comunicação clara e compartilhamento eficiente de informações.

Historicamente, a fragmentação de terminologias e sistemas entre organizações motivou sua criação. O GSIM evoluiu a partir do projeto inicial patrocinado pelo High Level Group (HLG) a partir de 2009, incorporando o modelo Neuchâtel (específico para classificações) em 2013, e vem sendo adotado como padrão desde então.

Estruturalmente, o GSIM é organizado em **Groups** (grupos de objetos de informação relacionados). Na versão 2.0 (dezembro 2023), o GSIM está estruturado em cinco grupos principais: Base Group, Business Group, Concept Group, Exchange Group e Structure Group. O Statistical Classifications Model faz parte do **Concept Group**, pois trata de objetos relacionados a conceitos, classificações estatísticas e itens que descrevem o significado das informações estatísticas.

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

## Termos relevantes

O **GSIM Statistical Classifications Model** organiza os conceitos de classificações estatísticas em uma estrutura de dois níveis principais:

- **Tipos de objetos**: definem os componentes de um banco de dados de classificações (por exemplo, séries de classificações, classificações estatísticas, versões, variantes, itens de classificação, níveis hierárquicos).
- **Atributos**: descrevem as propriedades desses objetos (por exemplo, códigos, rótulos, datas de validade, relação com outras classificações).

Essa estrutura funciona ao mesmo tempo como:

- **Modelo terminológico** → fornece um vocabulário padronizado (nomes e definições dos objetos e atributos), alinhado a outras referências internacionais.
- **Modelo conceitual** → explicita como esses objetos se relacionam entre si e como devem ser estruturados em um banco de dados de classificações.

No contexto do projeto do Classificador de Natureza de Receita de Minas Gerais, este modelo é utilizado como referência conceitual para o desenho do banco de dados. **Nem todos os conceitos estão ainda implementados de forma plena na solução atual**, mas o objetivo é que a modelagem caminhe progressivamente na direção desse padrão (especialmente no que diz respeito a versões, variantes e gerenciamento de histórico).

### Terminologia básica

Segundo a norma **ISO 704:1987 (E) – Principles and methods of terminology**, um **termo** é uma palavra ou expressão que designa um conceito. O GSIM adota essa abordagem terminológica e a aplica a objetos e atributos de classificações estatísticas, de modo que cada termo (por exemplo, *Statistical Classification*, *Classification Series*, *Classification Item*, *Version*) corresponde a um conceito claramente definido.

Alguns termos centrais para o projeto:

- **Série de Classificações (Classification Series)**  
  Conjunto nomeado que reúne várias classificações estatísticas relacionadas ao mesmo domínio, ao longo do tempo. Cada série pode conter várias versões normativas (oficiais) e, eventualmente, variantes.  
  
  ***Exemplo***: A “Série do Classificador de Natureza de Receita Orçamentária” reunindo todas as versões e variantes oficiais desse classificador ao longo dos anos.

- **Classificação Estatística (Statistical Classification)**  
  Uma única lista estruturada de categorias mutuamente exclusivas e exaustivas, válida para um período específico. Pode ser linear (plana) ou hierárquica (em níveis).  
  
  No projeto, cada versão normativa do Classificador de Natureza de Receita deve ser modelada como uma *Statistical Classification* específica.

- **Versão da Classificação (Classification Version)**  
  Uma classificação estatística é considerada uma **versão** quando:
  - é normativa (oficial),  
  - está associada a uma data de início de validade clara e, opcionalmente, uma data de término,  
  - e incorpora mudanças que **alteram as fronteiras entre categorias** 

  Mudanças meramente editoriais, como ajustes de rótulos, notas explicativas, inclusão de exemplos, **não justificam** por si só uma nova versão.  
  - **Crítica para o projeto**: é comum, na prática, tratar qualquer alteração como “nova versão” do classificador, o que dificulta a rastreabilidade de mudanças conceituais reais. A modelagem proposta busca separar formalmente versões, mudanças conceituais, de atualizações menores.

- **Atualização de Classificação (Classification Update)**  
  Uma classificação sofre uma **atualização** quando substitui uma instância anterior, mas **sem alterar as fronteiras entre categorias**. São ajustes menores, tais como correções de nomes, ajustes em notas explicativas, inclusão de elementos auxiliares (exemplos, remissivas, referências legais).  

  Se as mudanças menores forem muito numerosas ou significativas, pode-se optar por publicar uma nova versão oficial, mesmo sem alteração formal de fronteiras. 

  ***Ponto de atenção***: o projeto precisa de regras claras de governança para decidir quando algo é “apenas atualização” e quando deve ser tratada como nova versão normativa.

- **Variante de Classificação (Classification Variant)**  
  Alteração de uma classificação estatística padrão, normalmente para atender necessidades específicas de uso, mantendo o vínculo conceitual com a classificação de origem, mas alterando o **nível de detalhe/agregação** das categorias.  
  No GSIM, variantes são particularmente importantes para permitir granularidade adicional ou agregações diferentes, isso sem perder a rastreabilidade em relação à classificação padrão.

  Três tipos principais:

  - **Variante de extensão**  
    Mantém toda a estrutura original e acrescenta **novos níveis inferiores** (mais detalhados). É usada quando há necessidade de granularidade adicional em um determinado ramo da classificação, sem alterar a hierarquia original.  
    
    ***Exemplo típico***: acrescentar subcódigos específicos para necessidades estaduais ou setoriais, mantendo o código nacional como nível superior.

  - **Variante de agregação**  
    Parte de uma lista linear/plana para criar um ou mais **níveis agregados superiores**, formando uma hierarquia. É útil para relatórios em níveis mais macro (por exemplo, grupos de natureza de receita).  
    
    ***Exemplo***: agrupar códigos detalhados em grandes grupos temáticos para relatórios de alto nível.

  - **Variante de reagrupamento (rearrangement)**  
    Agrupa categorias existentes de modo diferente do desenho padrão. Pode ser:
    - **Que não violam a estrutura base**: mantêm todos os níveis e relações hierárquicas originais; novos níveis são inseridos acima ou entre níveis existentes, respeitando os agrupamentos da classificação de origem. Todos os itens e níveis originais são retidos.  
    - **Que violam a estrutura base**: substituem a hierarquia superior aos itens reagrupados, criando novos níveis que podem agrupar itens de ramos diferentes. Apenas os itens e níveis abaixo dos novos níveis são retidos.  
    
    
  ***Crítica para o projeto***: O GSIM recomenda que esses arranjos sejam registrados explicitamente como variantes, para manter rastreabilidade e comparabilidade, o que não é feito atualmente.

- **Base prescritiva vs. descritiva**  
  Há um debate importante sobre se um banco de dados de classificações deve conter apenas as classificações padrão (base **prescritiva**) ou também variantes, reagrupamentos e usos alternativos (base **descritiva**).  
  - **Base prescritiva**: foca nas classificações oficiais, normativas, definidas por um órgão padrão (por exemplo, Secretaria do Tesouro Nacional).  
  - **Base descritiva**: registra também como as classificações são efetivamente usadas na prática (variantes, agregações alternativas, recortes temáticos).  
  No caso do Estado de Minas Gerais, a proposta de modelagem aponta para uma **base predominantemente descritiva**, que:
  - mantém as classificações padrão como referência conceitual,  
  - documenta as variantes criadas para atender relatórios operacionais e indicadores legais subnacionais, apesar de não explicitá-las como tal.


- **Classificação Flutuante (Floating Classification)**  
  Abordagem em que o sistema de classificação permite atualizações e alterações relevantes **sem necessidade de criar novas versões formais**, utilizando datas de validade em todos os elementos para incorporar mudanças de forma ágil.  
  
  Em termos de modelagem, isso exige suporte a **bitemporalidade** ou, no mínimo, a registro de validade dos objetos (vigência no mundo real e, idealmente, vigência no sistema).


  ***Crítica para o projeto***: embora a documentação já mencione o princípio de classificação flutuante, sua implementação completa depende de decisões técnicas (por exemplo, desenho de tabelas de histórico e chaves substitutas) que ainda estão em evolução.

### Articulação com outros glossários e boas práticas

O texto base do GSIM ressalta que existem diversos glossários e terminologias sobre classificações estatísticas, como:

- o **Glossário de Termos de Classificação** da ONU,  
- o grupo **METIS** da UNECE (metadados estatísticos),  
- além de documentos de **boas práticas** publicados por diferentes organismos internacionais.

O **GSIM Statistical Classifications Model** deve ser visto como **complementar** a essas outras fontes. Há amplo alinhamento conceitual, mas o GSIM faz algumas escolhas terminológicas próprias (por exemplo, uso preciso de “Statistical Classification” e “Classification Series”), em função do seu foco mais restrito em classificações estatísticas dentro do framework GSIM,  
- seus objetivos específicos de servir como modelo de informação para bancos de dados de classificações.

Para o projeto de Minas Gerais, isso significa que a terminologia do GSIM é adotada como referência principal para o desenho do modelo de dados, mas continua sendo importante consultar glossários e boas práticas da ONU/UNECE para garantir compatibilidade terminológica e conceitual com o ecossistema internacional.
