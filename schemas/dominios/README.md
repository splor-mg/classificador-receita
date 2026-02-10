# Domínios compartilhados

Esta pasta contém **catálogos de domínio** (listas de valores) reutilizados por mais de um schema,
evitando `enum` duplicado. Cada domínio é um arquivo YAML cuja **fonte da verdade** são os campos
`values` (lista de códigos) e, opcionalmente, `labels` (mapeamento código → nome por extenso).

## Convenção `custom.domainRef`

Nos schemas principais (ex.: `serie_classificacao.yaml`, `base_legal_tecnica.yaml`), campos que devem
validar contra um domínio compartilhado indicam a referência via `custom.domainRef`:

```yaml
constraints:
  required: true
custom:
  domainRef: "dominios/orgaos_entidades.yaml"
```

- **Validação:** Scripts customizados (ex.: `validate_domains.py`) carregam o arquivo de domínio
  indicado em `domainRef` e aplicam `values` como conjunto de valores válidos para o campo.
- **Caminho:** `domainRef` é relativo à raiz da pasta `schemas/` (ex.: `dominios/orgaos_entidades.yaml`).

## Domínios disponíveis

| Arquivo de domínio               | Uso                                                                 |
|----------------------------------|---------------------------------------------------------------------|
| `dominios/orgaos_entidades.yaml` | `serie_classificacao.orgao_responsavel`, `base_legal_tecnica.orgao_responsavel` |

Ao adicionar um novo domínio:

1. Crie o catálogo em `schemas/dominios/novo_dominio.yaml` com `values` (e opcionalmente `labels`).
2. Nos schemas que devem usá-lo, adicione `custom.domainRef` apontando para esse arquivo.
