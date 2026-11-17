--------------------------------------------------------------------------------------
# 2026-02-24

## 1) Terminar conexões (execute antes de dropar)

- com psql (recomendado)

```
PGPASSWORD='postgres' 
psql -h localhost -p 5432 -U postgres -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'classificador_receita' AND pid <> pg_backend_pid();"
```
_obs.: se preferir, omita PGPASSWORD e digite a senha quando solicitado_


## 2) Dropar o banco

- via usuário do sistema (local, precisa de sudo):

```
sudo -u postgres dropdb classificador_receita
```

- via cliente dropdb (usa as credenciais do settings):

```
PGPASSWORD='postgres'
dropdb -h localhost -p 5432 -U postgres classificador_receita
```

- via psql (mesma ação em SQL):

```
PGPASSWORD='postgres'
psql -h localhost -p 5432 -U postgres -d postgres -c "DROP DATABASE classificador_receita;"
```

3) Recriar o banco
- via usuário do sistema:

```
sudo -u postgres createdb classificador_receita
```

- via cliente createdb:

```
PGPASSWORD='postgres'
createdb -h localhost -p 5432 -U postgres classificador_receita
```

- equivalente em psql (se preferir usar SQL em vez de createdb):

```
PGPASSWORD='postgres'
psql -h localhost -p 5432 -U postgres -d postgres -c "CREATE DATABASE classificador_receita;"
```


