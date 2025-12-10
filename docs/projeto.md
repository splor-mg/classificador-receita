# PROJETO SISTEMA DE GESTÃO DO CLASSIFICADOR DA NATUREZA DE RECEITA


# 1. Contexto

## 1.1 O que é o Classificador de Natureza de Receita

A classificação da receita orçamentária por natureza é de utilização obrigatória para todos os entes da Federação e visa identificar a origem do recurso segundo o fato gerador: o acontecimento real que ocasionou o ingresso da receita nos cofres públicos.

Conforme o Manual de Contabilidade Aplicada ao Setor Público (MCASP), a classificação por Natureza de Receita Orçamentária é composta por um código de oito dígitos numéricos que representam: a Categoria Econômica, a Origem, a Espécie, os Desdobramentos e o Tipo de Receita.

No Estado de Minas Gerais, o Classificador de Natureza de Receita utiliza uma estrutura estendida de **13 dígitos**, organizada em **9 níveis hierárquicos**, permitindo maior granularidade para atender às necessidades gerenciais específicas do ente estadual. Este classificador é utilizado por todos os órgãos e entidades do Poder Executivo Estadual para registro e controle das receitas orçamentárias, sendo fundamental para a execução orçamentária, contabilidade pública e prestação de contas.

## 1.2 Situação Atual

Atualmente, as classificações de natureza de receita são gerenciadas em duas fontes distintas:

### 1.2.1 SISOR (Sistema Oficial)
- **Função:** Sistema oficial que armazena as classificações ativas do ano corrente e do ano futuro.
- **Responsabilidade:** Sistema de referência para execução orçamentária.
- **Limitação:** Não mantém histórico de classificações inativas ou modificações passadas.

### 1.2.2 Ementário da DCAF (Base Consolidada)
- **Função:** Planilha Excel hospedada no OneDrive que funciona como base consolidada.
- **Conteúdo:**
  - Todas as classificações ativas presentes no SISOR.
  - Histórico completo de classificações inativas.
  - Registro de modificações realizadas ao longo do tempo.
- **Responsabilidade:** Gerido pela Diretoria Central de Análise Fiscal (DCAF), vinculada à Superintendência Central de Programação e Normas da SPLOR.

## 1.3 Volume e Complexidade

O Classificador de Natureza de Receita do Estado de Minas Gerais possui:
- **Estrutura:** Código de 13 dígitos organizados em 9 níveis hierárquicos.
- **Escala:** Milhares de códigos ativos e históricos.
- **Frequência de mudanças:** Classificações são alteradas periodicamente para atender necessidades normativas, gerenciais e de planejamento orçamentário.

## 1.4 Usuários e Consumidores

O classificador é utilizado por:
- **Órgãos e Entidades do Poder Executivo Estadual:** Para registro e classificação de receitas orçamentárias.
- **DCAF:** Para gestão, manutenção e atualização do classificador.
- **Órgãos de Controle:** Para auditoria e verificação de conformidade (TCE-MG, CGE-MG).
- **Sociedade Civil:** Para transparência e consulta pública (via dashboard, quando disponível).

---

# 2. Problemas Identificados

## 2.1 Problemas Operacionais

### 2.1.1 Retrabalho na Replicação Manual
**Situação:** Como o SISOR é o sistema oficial, toda alteração realizada no Excel da DCAF precisa ser replicada manualmente nele.

**Impacto:**
- Geração de retrabalho significativo.
- Risco de inconsistências entre as duas fontes.
- Possibilidade de erros na transcrição manual.
- Dificuldade de rastreabilidade das alterações.

**Objetivo do novo sistema:** Criar um banco de dados que sincronize automaticamente com o SISOR para as classificações ativas, eliminando a necessidade de replicação manual.

## 2.2 Problemas Técnicos

### 2.2.1 Ausência de Versionamento e Rastreabilidade Histórica
**Situação:** A modelagem atual do banco de dados de classificadores apresenta deficiências críticas no suporte a versionamento temporal.

**Impacto:**
- Impossibilidade de reconstituir o estado histórico de qualquer classificação em uma data específica.
- Dificuldade em realizar auditorias históricas e análises de evolução.
- Falta de rastreabilidade completa das modificações (quando foi alterado, por quem, qual era o estado anterior).
- Risco de perda de informações históricas importantes para conformidade e prestação de contas.

**Solução proposta:** Implementar modelo de dados bitemporal que permita rastrear tanto o tempo de validade (quando a informação estava vigente) quanto o tempo de transação (quando foi registrada no sistema), conforme detalhado na seção de Arquitetura de Dados.

### 2.2.2 Limitações de Ferramentas de Versionamento
**Situação:** Atualmente dispomos de poucas ferramentas de versionamento voltadas para esse tipo de domínio, contando apenas com o banco de dados do SISOR e os sistemas de recuperação do OneDrive.

**Impacto:**
- Dependência de ferramentas genéricas não especializadas em dados temporais.
- Dificuldade em garantir integridade referencial temporal entre entidades relacionadas.
- Limitações na consulta e análise de dados históricos.

## 2.3 Problemas de Negócio

### 2.3.1 Riscos de Conformidade e Auditoria
**Situação:** A falta de rastreabilidade histórica completa pode comprometer a capacidade de responder a auditorias e demandas de órgãos de controle.

**Impacto:**
- Dificuldade em comprovar conformidade com normas em períodos específicos.
- Risco de não conformidade em prestações de contas.
- Limitações na capacidade de análise de tendências e evolução das receitas.

### 2.3.2 Qualidade e Consistência dos Dados
**Situação:** A gestão em duas fontes distintas (SISOR + Excel) sem sincronização automática aumenta o risco de inconsistências.

**Impacto:**
- Possibilidade de divergências entre SISOR e Ementário DCAF.
- Dificuldade em garantir que todas as alterações sejam corretamente replicadas.
- Risco de uso de informações desatualizadas ou incorretas.


# 3. Escopo

## 3.1 Objetivo do Projeto

Implementar sistema de gestão do Classificador de Natureza de Receita do Estado de Minas Gerais, baseado em banco de dados relacional normalizado e reprodutível, com suporte a versionamento bitemporal, inclusive de seus metadados e suas transformações ao longo do tempo, e validação via datapackage Frictionless.


## 3.1 Requisitos - MVP

### 3.2.1 Banco de Dados em Database Operacional

  - Classificador de receita estruturado no formado de database operacional, por meio da normalização e modelagem relacional do banco de dados.

  - Banco de dados estruturado de forma a permitir consulta direta à versão mais recente de cada classificação, com o status atual correspondente.

  - Estrutura de dados que permita auditoria histórica e reconstrução do estado de qualquer código em qualquer data - consultas "as-of" e "point-in-time queries".

### 3.2.2 Aplicações Web

  - App de gestão para operacionalização de alterações no ementário.

  - Dashboard público para consulta ao classificador.

### 3.2.3 Integração

  - Sincronização automática com SISOR para classificações ativas.

## 3.3 Não-Escopo (Fora do MVP)

- Integração com sistemas externos além do SISOR.
- Módulos de análise avançada e relatórios customizados.
- Gerenciamento do SGDB e manutenção do banco de dados.
- Migração de dados históricos de outros sistemas além do Ementário DCAF.

## 3.4 Premissas e Restrições

### Premissas
- Dados históricos do Ementário Excel estão disponíveis e acessíveis.
- SISOR atual mantém disponibilidade durante o desenvolvimento.
- Prodemge fornecerá informações sobre o novo SISOR (2026) em tempo hábil.

### Restrições
- Conformidade com padrões MCASP para classificação de receita.
- Necessidade de interoperabilidade com SISOR (atual e futuro).
- Requisitos de auditoria e rastreabilidade de órgãos de controle.

---

### 4.1 Matriz RACI

| Stakeholder      | R (Responsible) | A (Accountable) | C (Consulted) | I (Informed) |
|------------------|-----------------|-----------------|---------------|--------------|
| DCAF             |                 | x               | x             |              |
| AID              | x               |                 |               |              |
| SPLOR            |                 |                 |               | x            |
| Prodemge         |                 |                 | x             | x            |
| Órgãos setoriais |                 |                 | x             | x            |
| Cidadão          |                 |                 |               | x            |

### 4.2 Detalhamento

#### Patrocinador (Sponsor)
- **SPLOR** — Subsecretaria de Planejamento e Orçamento
  - Interesse: Modernização da gestão orçamentária.

#### Dono do Produto (Product Owner)
- **DCAF** — Diretoria Central de Análise Fiscal
  - Interesse: Gestão eficiente do classificador, redução de retrabalho.
  - Responsabilidade: Definir requisitos de negócio, validar entregas, priorizar backlog.
  - Ponto focal: Laura Dilly.

#### Executor Técnico
- **AID** — Assessoria de Inteligência de Dados
  - Interesse: Entregar solução técnica de qualidade.
  - Responsabilidade: Arquitetura, modelagem, implementação, documentação.

#### Parceiro Tecnológico
- **Prodemge**
  - Interesse: Garantir interoperabilidade com novo SISOR (2026).
  - ⚠️ **Crítico**: Estabelecer canal de comunicação para alinhar schemas e APIs.

#### Usuários Internos (Consumidores)
- **Órgãos e Entidades do Poder Executivo Estadual**
  - Interesse: Consultar classificações corretas para execução orçamentária.
  - Papel:
    - Participar de testes de usabilidade e validação de interfaces.
    - Fornecer feedback sobre navegabilidade e eficiência do app e dashboard.
    - Reportar dúvidas e gargalos durante uso inicial (pilotos).

#### Sociedade Civil
- **Cidadão / Imprensa / Pesquisadores**
  - Interesse: Transparência orçamentária.
  - Canal: Dashboard público (se validado como requisito).

---

# 5. Riscos e Dependências

## 5.1 Dependências Críticas

| ID | Dependência                                        |
|----|----------------------------------------------------|
| D1 | Definição de requisitos pela DCAF                  |
| D2 | Acesso aos dados históricos do Ementário Excel     |
| D3 | Alinhamento técnico com Prodemge sobre novo SISOR  |
| D4 | Infraestrutura para hospedagem (Docker/PostgreSQL) |

## 5.2 Matriz de Riscos

| ID | Risco                            | Score       |
|----|----------------------------------|-------------|
| R1 | Substituição do SISOR (2026)     | 🔴 Crítico  |
| R2 | Qualidade dos dados do Excel     | 🟠 Alto     |
| R3 | Capacitação técnica insuficiente | 🟡 Moderado |


### 🔴 R1 — Substituição do SISOR (2026)
- **Categoria:** Externo
- **Probabilidade:** Alta
- **Impacto:** Alto
- **Descrição:** Novo sistema pode ter schema incompatível, invalidando integrações desenvolvidas
- **Mitigação:** Estabelecer canal formal com Prodemge; adotar arquitetura desacoplada
- **Responsável:** AID

---

### 🟠 R2 — Qualidade dos dados do Excel
- **Categoria:** Técnico
- **Probabilidade:** Média
- **Impacto:** Alto
- **Descrição:** Inconsistências, duplicidades ou lacunas temporais no Ementário podem comprometer migração
- **Mitigação:** Análise exploratória prévia; scripts de validação; regras de tratamento com DCAF
- **Responsável:** AID + DCAF

---

### 🟡 R3 — Capacitação técnica insuficiente
- **Categoria:** Organizacional
- **Probabilidade:** Média
- **Impacto:** Médio
- **Descrição:** Curva de aprendizado em SQL/PostgreSQL pode atrasar entregas
- **Mitigação:** Priorizar capacitação nas primeiras sprints
- **Responsável:** AID


# 6. Plano de Trabalho

| Fase | Entrega Principal                         | Dependências | Validação                   |
|------|-------------------------------------------|--------------|-----------------------------|
| F1   | Arquitetura de Dados                      | D1           | ADR aprovado pela DCAF      |
| F2   | Modelo Lógico (DER)                       | F1           | DER validado pela DCAF      |
| F3   | Banco de Dados Operacional                | F2, D2, D4   | Consultas as-of funcionando |
| F4   | Migração de Dados (vigentes + históricos) | F3           | Dados validados pela DCAF   |
| F5   | SGDB (APP de gestão do ementário)         | F4           | Testes de integração        |
| F6   | Dashboard Público                         | F4           | Homologação com SPLOR       |
| F7   | Integração Bidirecional com SISOR         | F5, D3       | Sincronização funcionando   |


---

## F1 - Arquitetura de Dados
**Objetivo:** Definir princípios e padrões que guiarão toda a modelagem.

**Atividades:**
- Definir estratégia de bitemporalidade (valid_time × transaction_time).
- Definir estratégia para gerenciar mudanças em dados dimensionais ao longo do tempo - padrão SCD 2-6 para versionamento.
- Estudar e adotar GSIM Statistical Classifications Model como referência conceitual.
- Documentar decisões em ADRs (Architecture Decision Records).

**Entregas:**
- ADR-001: Estratégia de bitemporalidade.
- ADR-002: Adoção do modelo GSIM.
- ADR-003: Padrão de versionamento (SCD).

**Critério de aceite:** ADRs revisados e aprovados pela DCAF.

**Dependências:** D1 (requisitos da DCAF)

---

## F2 — Modelagem de Dados
**Objetivo:** Construir estrutura lógica das entidades e seus relacionamentos.

**Atividades:**
- Definir entidades principais, tais como `classificacao_receita`, `nivel_hierarquico`, `versao_classificacao`.
- Definir atributos essenciais de cada entidade (conforme GSIM).
- Estruturar relacionamentos, PKs, FKs e cardinalidade.
- Aplicar normalização (3FN).
- Incorporar colunas temporais.
- Configurar validação Frictionless para schemas (`frictionless validate schemas/*.yaml`).

**Entregas:**
- Diagrama Entidade-Relacionamento (DER).
- Dicionário de dados estruturado em arquivo `datapackage.yaml`.
- Schemas das entidades em `schemas/*.*`.
- Pipeline de validação Frictionless funcional.

**Critério de aceite:** DER validado pela DCAF; entidades cobrem 100% dos campos do Ementário Excel; schemas validam sem erros via Frictionless.

**Dependências:** F1 concluída

---

## F3 — Implementação do Banco de Dados
**Objetivo:** Criar esquema físico em PostgreSQL.

**Habilitação:**
- Estudo de SQL:
  - Sintaxe básica (SELECT, INSERT, UPDATE, DELETE).
  - DDL (CREATE TABLE, ALTER, constraints).
  - Consultas avançadas (JOIN, GROUP BY, subconsultas).
  - Referências:
    > [Curso FGV SQL](https://educacao-executiva.fgv.br/cursos/online/curta-media-duracao-online/sql-structured-query-language)
    > [CS50's Introduction to Databases with SQL](https://pll.harvard.edu/course/cs50s-introduction-databases-sql)

- Estudo de PostgreSQL:
  - Tipos de dados (TEXT, TIMESTAMP, JSONB).
  - Triggers e funções (BEFORE INSERT, AFTER UPDATE).
  - Extensões úteis (temporal_tables, pg_partman).
  - Dockerização do ambiente.
  - Referênciaas:
      [Curso completo de PostgreSQL](https://www.udemy.com/course/curso-de-postgresql/?couponCode=CP251120G2V2)
      [Curso de FastAPI 2025 - Dockerizando a nossa aplicação e introduzindo o PostgreSQL - Eduardo Mendes](https://www.youtube.com/watch?v=faf7jhti5tg)

**Atividades:**
- Traduzir DER para DDL (CREATE TABLE, constraints).
- Implementar triggers para bitemporalidade.
- Configurar ambiente Docker (PostgreSQL + volumes).
- Criar scripts de migração versionados.
- Criar testes SQL para validar triggers de bitemporalidade.
- Configurar CI/CD básico (GitHub Actions) para validação automática.

**Entregas:**
- Esquema SQL (`src/sql/ddl/`).
- Docker Compose funcional.
- Scripts de inicialização.
- Testes SQL (`tests/sql/`).
- Pipeline CI/CD (`.github/workflows/validate.yml`).

**Critério de aceite:** Banco aceita inserções e responde consultas as-of corretamente; testes SQL passam; pipeline CI/CD executa validações automaticamente.

**Dependências:** F2 concluída, D2 (acesso aos dados), D4 (infraestrutura).

---

## F4 — Migração de Dados
**Objetivo:** Carregar dados vigentes e históricos do Ementário Excel.

**Atividades:**
- Mapear campos Excel → modelo relacional.
- Desenvolver pipeline ETL (extração, transformação, carga).
- Validar integridade: duplicidades, hierarquia, lacunas temporais.
- Carregar histórico de modificações com transaction_time.
- Criar testes de validação pós-migração (integridade referencial, consistência temporal).
- Executar validação Frictionless nos dados migrados.

**Entregas:**
- Scripts ETL (`src/scripts/etl/`).
- Relatório de validação de migração.
- Banco populado com dados vigentes + históricos.
- Scripts de validação pós-migração (`tests/etl/`).

**Critério de aceite:** DCAF valida que dados migrados correspondem ao Ementário Excel; testes de validação pós-migração passam; dados validam via Frictionless.

**Dependências:** F3 concluída, D2 (acesso aos dados Excel)

---

## F5 — SGDB - App Web de Gestão do Classificador
**Objetivo:** Criar um Sistema de Gestão de Banco de Dados (SGDB) com interface web para operacionalização de alterações no classificador, utilizando Django como framework.

**Habilitação:**
- Estudo de Django:
  - Fundamentos do framework (MVC/MVT, apps, settings).
  - Models e ORM (mapeamento de tabelas, relacionamentos, queries).
  - Views e Templates (class-based views, forms, template tags).
  - Autenticação e autorização (usuários, grupos, permissões).
  - Admin interface (customização do Django Admin).
  - Integração com PostgreSQL (psycopg2, conexão, SQL raw).
  - Management commands (criação de comandos customizados).
  - Testes (unittest, pytest-django).
  - Referências:
    > [Django Documentation](https://docs.djangoproject.com/)
    > [Django for Beginners](https://djangoforbeginners.com/)
    > [Two Scoops of Django](https://www.feldroy.com/books/two-scoops-of-django-3-x)

- Estudo de integração Django + PostgreSQL bitemporal:
  - Uso de SQL raw para consultas temporais complexas.
  - Models com `managed=False` (tabelas criadas via SQL).
  - Custom Managers e QuerySets para consultas as-of.
  - Integração com triggers PostgreSQL.
  - Signals Django vs Triggers PostgreSQL.
  - Referências:
    > [Django-tenants - Deep dive with Django and PostgreSQL!](https://www.youtube.com/watch?v=seTUY18ge38&t)

**Atividades:**
- Configurar projeto Django e estrutura de apps.
- Definir requisitos funcionais com DCAF.
- Criar models Django mapeando tabelas do banco bitemporal (managed=False).
- Desenvolver interface CRUD para classificações usando Django (views, forms, templates).
- Implementar autenticação e controle de acesso (perfis DCAF, auditores).
- Implementar fluxo de aprovação de alterações (workflow).
- Integrar com banco bitemporal (usar SQL raw para consultas temporais complexas).
- Customizar Django Admin para gestão administrativa.
- Criar management commands para operações ETL e sincronização.
- Criar testes de integração (app Django + banco bitemporal).

**Entregas:**
- App web Django funcional.
- Models, views, templates e forms implementados.
- Sistema de autenticação e autorização configurado.
- Django Admin customizado.
- Documentação de uso.
- Testes de integração (`tests/integration/`).

**Critério de aceite:** DCAF consegue criar, alterar e inativar classificações via app Django; consultas bitemporais funcionam corretamente; testes de integração passam.

**Dependências:** F4 concluída

---

## F6 — Dashboard Público
**Objetivo:** Interface de consulta pública ao classificador, desenvolvida como aplicação Django separada ou módulo do mesmo projeto.

**Atividades:**
- Definir requisitos com SPLOR (confirmar se está no MVP).
- Criar app Django para dashboard público (ou módulo no projeto existente).
- Desenvolver visualização hierárquica do classificador (árvore de 9 níveis) usando templates Django.
- Implementar busca e filtros (forms Django, queries otimizadas).
- Implementar consultas históricas (point-in-time) usando SQL raw.
- Criar views Django para consultas as-of e reconstrução histórica.
- Implementar materialized views no PostgreSQL para consultas frequentes.
- Otimizar performance (cache, índices, select_related/prefetch_related).
- Desenvolver interface responsiva (CSS/JavaScript ou framework frontend).
- Configurar rotas públicas (sem autenticação obrigatória).

**Entregas:**
- Dashboard web Django funcional.
- Visualização hierárquica implementada.
- Sistema de busca e filtros operacional.
- Consultas históricas funcionando.
- Materialized views criadas e atualizadas.
- Documentação de uso.

**Critério de aceite:** Usuário externo consegue consultar classificação vigente e histórica via dashboard; consultas point-in-time retornam resultados corretos; performance adequada para consultas públicas.

**Dependências:** F4 concluída

---

## F7 — Integração Bidirecional com SISOR
**Objetivo:** Implementar sincronização automática bidirecional entre o novo sistema e o SISOR, garantindo que alterações realizadas no sistema de gestão sejam automaticamente replicadas no SISOR (sistema oficial), eliminando retrabalho manual.

**Habilitação:**
- Estudo de integração de sistemas:
  - APIs REST e SOAP.
  - Autenticação e autorização em APIs (tokens, OAuth).
  - Tratamento de erros e retry logic.
  - Webhooks e polling.
  - Referências:
    > [Django REST Framework](https://www.django-rest-framework.org/)
    > [Celery Documentation](https://docs.celeryproject.org/)

- Estudo de Celery para tarefas assíncronas:
  - Configuração de Celery com Django.
  - Tarefas periódicas (Celery Beat).
  - Retry automático e tratamento de falhas.
  - Monitoramento de tarefas (Flower).
  - Filas e workers.
  - Referências:
    > [Celery with Django](https://docs.celeryproject.org/en/stable/django/first-steps-with-django.html)

- Estudo de integração com SISOR:
  - Documentação da API do SISOR (atual e futura)
  - Protocolos de comunicação disponíveis
  - Mapeamento de dados entre sistemas
  - Tratamento de conflitos e resolução

**Atividades:**
- Alinhar com Prodemge sobre interface de integração do SISOR (API, endpoints, autenticação).
- Definir protocolo de comunicação (REST API, SOAP, ou outro).
- Mapear campos do novo sistema → campos do SISOR.
- Implementar detecção de mudanças no novo sistema (Django signals ou triggers PostgreSQL).
- Criar serviço de sincronização usando Celery (tarefas assíncronas).
- Implementar envio de atualizações para SISOR (criação, alteração, inativação).
- Implementar tratamento de erros e retry logic (tentativas automáticas em caso de falha).
- Criar sistema de fila para sincronizações pendentes.
- Implementar sincronização unidirecional inicial (SISOR → novo sistema) para importação inicial.
- Criar dashboard de monitoramento de sincronizações (status, logs, erros).
- Implementar notificações para DCAF em caso de falhas críticas.
- Criar mecanismo de reconciliação para detectar e corrigir divergências.
- Documentar protocolo de integração e mapeamento de dados.
- Criar testes de integração (mock do SISOR para testes).

**Entregas:**
- Serviço de sincronização bidirecional funcional.
- Tarefas Celery configuradas e operacionais.
- Dashboard de monitoramento de sincronizações.
- Documentação de integração com SISOR.
- Scripts de reconciliação e detecção de divergências.
- Testes de integração (`tests/integration/sisor/`).
- Plano de contingência para falhas de sincronização.

**Critério de aceite:**
- Alterações realizadas no novo sistema são automaticamente replicadas no SISOR.
- Sistema detecta e trata erros de sincronização automaticamente.
- Dashboard mostra status de todas as sincronizações.
- DCAF recebe notificações em caso de falhas críticas.
- Testes de integração passam.
- Sincronização unidirecional (SISOR → novo sistema) funciona para importação inicial.

**Dependências:** F5 concluída, D3 (alinhamento técnico com Prodemge sobre SISOR).

---

## Atividades de Suporte (paralelas)

### Documentação Contínua.
- Manter `CHANGELOG.md` atualizado.
- Registrar decisões em `docs/adr/`.
- Registrar conceitos relevantes em `docs/conceitos`.
