# Configurar PostgreSQL

Este guia descreve como instalar e configurar o PostgreSQL para usar no projeto **sem** a variável `USE_SQLITE=1`. O Django continuará usando PostgreSQL conforme `classificador/settings.py` (bloco `else`).

Ambiente considerado: **WSL2** ou **Linux** (Ubuntu/Debian). Em outros sistemas, os comandos de instalação mudam (ex.: Windows com instalador oficial, macOS com Homebrew).

---

## 1. Instalar o PostgreSQL e o cliente

No terminal (WSL/Ubuntu/Debian):

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib libpq-dev
```

- **postgresql**: servidor e cluster padrão
- **postgresql-contrib**: extensões úteis
- **libpq-dev**: bibliotecas e cabeçalhos para compilar o driver Python `psycopg2` (caso use a versão não-binary)

---

## 2. Iniciar o serviço

```bash
sudo service postgresql start
```

Para verificar se está rodando:

```bash
sudo service postgresql status
```

Deve aparecer algo como `active (running)`. Para iniciar automaticamente no boot (opcional):

```bash
sudo systemctl enable postgresql
```

---

## 3. Criar o usuário e o banco do projeto

O Django está configurado para usar:

- **Banco:** `classificador_receita`
- **Usuário:** `postgres`
- **Senha:** `postgres`
- **Host:** `localhost`
- **Porta:** `5432`

O usuário `postgres` já existe após a instalação; a senha padrão costuma ser do sistema. Para usar exatamente essa configuração, defina a senha do usuário `postgres` e crie o banco.

Para fazer tal definição, abra o shell do PostgreSQL como o usuário do sistema `postgres`:

```bash
sudo -u postgres psql
```

Dentro do `psql`, rode (uma linha por vez ou todas juntas):

```sql
-- Definir senha do usuário postgres (use a senha que quiser; o settings usa 'postgres')
ALTER USER postgres WITH PASSWORD 'postgres';

-- Criar o banco usado pelo Django
CREATE DATABASE classificador_receita;

-- Dar todos os privilégios no banco ao usuário postgres (geralmente já é dono)
GRANT ALL PRIVILEGES ON DATABASE classificador_receita TO postgres;

-- Sair
\q
```

Se preferir outro usuário (ex.: `classificador`) em vez de `postgres`:

```sql
CREATE USER classificador WITH PASSWORD 'postgres';
CREATE DATABASE classificador_receita OWNER classificador;
GRANT ALL PRIVILEGES ON DATABASE classificador_receita TO classificador;
\q
```

Nesse caso, altere em `classificador/settings.py` o `USER` para `classificador` (e a senha, se mudar).

---

## 4. Permitir conexão via localhost (TCP)

Por padrão o PostgreSQL em Ubuntu/Debian costuma aceitar conexões locais. Se o Django disser que a conexão foi recusada em `localhost:5432`, confira:

1. **Arquivo de configuração** (caminho típico):

   ```bash
   sudo nano /etc/postgresql/16/postgresql.conf
   ```

   (Substitua `16` pela versão instalada, ex.: `15` ou `14`.)

2. Garanta que existe uma linha assim (e não comentada com `#`):

   ```ini
   listen_addresses = 'localhost'
   ```

3. **Arquivo de autenticação** (quem pode conectar):

   ```bash
   sudo nano /etc/postgresql/16/pg_hba.conf
   ```

   No final do arquivo, deve haver uma linha permitindo usuário `postgres` em conexões locais. Exemplo:

   ```
   # IPv4 local connections:
   host    all    all    127.0.0.1/32    scram-sha-256
   ```

   Ou, só para o banco e usuário do projeto:

   ```
   host    classificador_receita    postgres    127.0.0.1/32    scram-sha-256
   ```

4. Após alterar `postgresql.conf` ou `pg_hba.conf`, reinicie o serviço:

   ```bash
   sudo service postgresql restart
   ```

---

## 5. Testar a conexão a partir do projeto

Com o Postgres rodando e o banco criado:

1. **Não** defina `USE_SQLITE=1` (nem no terminal nem no `.env`), ou remova do `.env` se estiver lá.

2. Rode as migrações:

   ```bash
   ptt migrate
   ```

   Ou, se usar Poetry sem alias:

   ```bash
   poetry run python manage.py migrate
   ```

Se aparecer algo como "Applying core.0001_initial... OK", a configuração do PostgreSQL está correta.

---

## 6. Resumo dos comandos (copiar e colar)

```bash
# Instalar
sudo apt update
sudo apt install postgresql postgresql-contrib libpq-dev

# Iniciar
sudo service postgresql start

# Criar banco e usuário (entrar no psql)
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'postgres';"
sudo -u postgres psql -c "CREATE DATABASE classificador_receita;"

# No projeto (sem USE_SQLITE)
ptt migrate
```

---

## Referência rápida

| O quê              | Valor                 |
|--------------------|-----------------------|
| Banco              | `classificador_receita` |
| Usuário            | `postgres`           |
| Senha (settings)   | `postgres`           |
| Host               | `localhost`          |
| Porta              | `5432`               |

Esses valores estão em `classificador/settings.py` no bloco `else` da configuração de `DATABASES`. Para usar outro usuário, senha ou banco, altere apenas esse bloco (ou use variáveis de ambiente, se você estender o settings para lê-las).
