# Schemas do Classificador de Receita

Nesta pasta há **dois tipos de artefatos**: i) os **descritores de recursos/tabelas**, que são os arquivos YAML na **raiz**, responsáveis por defir as tabelas e seus atributos, campos, chaves, FKs. Cada um descreve uma entidade persistida no banco; e ii) os **domínios compartilhados**, que são os arquivos na subpasta **`dominios/`** e se tratam de **catálogos de códigos** reutilizados por múltiplos schemas. Não representam definição de tabela e servem ao propósito de validação dos campos das tabelas e evitam `constraint.enum` duplicado.

---

## Descritores de tabela (raiz)

**serie_classificacao** — Guarda a **IDENTIDADE** do classificador/série ao longo do tempo (produto/conceito, órgão responsável, propósito). Não guarda estrutura nem datas de lançamento.

**classificacao_receita** — Guarda a **EDIÇÃO** do classificador: estrutura vigente, tipo, número de níveis, vigência no mundo real.

**nivel_hierarquico** — Guarda o **EIXO** hierárquico: nomes, ordem e formato do código (numérico, alfabético, alfanumérico) em cada nível.

**item_classificacao** — Guarda os **CÓDIGOS** do ementário: nome oficial, item pai, vigência, flags (item gerado, válido atualmente).

**variante_classificacao** — Guarda extensões, **agregações** e **reagrupamentos** sobre uma classificação/versão: propósito (LOA, relatório, norma estadual), tipo e vigência.

**versao_classificacao** — Guarda **METADADO** de lançamento da edição: número da versão, data de publicação, descrição das mudanças (fronteiras entre categorias). Vincula-se a uma classificação.

**base_legal** — Guarda **BASE LEGAL**: normas, atos e arcabouço legal (tipo, esfera, casa legislativa, vigência, ementa).

---

## Domínios compartilhados (`dominios/`)

**orgaos_entidades** — Catálogo de códigos de órgãos e entidades (União e MG). Usado em `serie_classificacao.orgao_responsavel` e `base_legal.orgao_responsavel`.

Detalhes da convenção `domainRef` e uso dos domínios: ver [dominios/README.md](dominios/README.md).
