# Domínios compartilhados

Esta pasta contém **conjuntos únicos de valores** reutilizados por mais de um schema (evitando enum duplicado).

## Convenção `domainRef`

Nos schemas (ex.: `serie_classificacao.yaml`, `base_legal.yaml`), campos que devem validar contra um domínio compartilhado usam:

```yaml
constraints:
  domainRef: dominios/nome_do_dominio.yaml
```

- **Validação:** Um validador que entenda `domainRef` deve carregar o arquivo referenciado e aplicar o array `values` como se fosse `enum` naquele campo.
- **Caminho:** Relativo à raiz da pasta `schemas/`.
- **Estrutura do arquivo de domínio:** Deve conter ao menos `values` (lista de códigos permitidos). Opcionalmente `labels` (código → nome por extenso) para documentação/UI.

## Domínios disponíveis

| Arquivo | Uso |
|---------|-----|
| `orgaos_entidades.yaml` | `serie_classificacao.orgao_responsavel`, `base_legal.orgao_responsavel` |

Ao adicionar um novo domínio, documente aqui e use o mesmo `domainRef` em todos os schemas que compartilham o conjunto de valores.
