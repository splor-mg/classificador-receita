# Anotações sobre Implementação do Django no Projeto

## Estrutura de Arquivos e Pastas

Ao seguir as orientações do curso [CS50's Web Programming - Week 3: Django](https://cs50.harvard.edu/web/weeks/3/), foi executado o comando `django-admin startproject classificador` dentro do repositório `classificador-receita`, que já continha uma estrutura pré-existente com `schemas`, `scripts`, `docs/` dentre outros.

Isso resultou na criação de uma estrutura aninhada, confusa de  `classificador-receita/classificador/classificador/`, onde:
- `classificador/` (pasta externa) contém `manage.py` e a pasta de configurações
- `classificador/classificador/` (pasta interna) contém `settings.py`, `urls.py`, `wsgi.py`, etc.

### Decisão: Django na Raiz

Tomando como referência [cookiecutter-django](https://cookiecutter-django.readthedocs.io/en/latest/index.html), foi decidido implementar o **Django na raiz** para reestruturar o projeto, movendo:
- `manage.py` para a raiz do repositório
- `classificador/classificador/` → `classificador/` (configurações do projeto Django)

Optar por Django na raiz simplifica o acesso direto aos recursos já existentes no projeto (`schemas/`, `scripts/` e `docs/`), proporciona uma estrutura plana e intuitiva ao eliminar pastas aninhadas desnecessárias, segue as práticas recomendadas por projetos modernos, facilita o uso dos comandos com `manage.py` na raiz e faz sentido já que Django será a principal interface de gerenciamento do classificador.


Estrutura pensada: 

```
classificador-receita/              # Repositório raiz
├── manage.py                       # Django na raiz
├── pyproject.toml                  # Poetry
├── classificador/                  # Configurações do projeto Django
│   ├── __init__.py
│   ├── settings.py                 # BASE_DIR aponta para raiz
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/                           # Apps Django (criar quando necessário)
│   └── core/                       # App principal
├── scripts/                        # Scripts utilitários (mantém)
│   ├── validate_schemas.py
│   └── (...)
|   
├── schemas/                        # Schemas Frictionless (mantém)
├── docs/                           # Documentação (mantém)
└── README.md

```

### Observação: Organização de Apps em `apps/`

Os apps Django foram organizados dentro da pasta `apps/` visando **escalabilidade** e **padronização**, seguindo recomendações para projetos Django. Esta estrutura permite adicionar múltiplos apps de forma organizada (ex: `apps/core/`, `apps/api/`, `apps/dashboard/`) sem poluir a raiz do repositório.

No entanto, para criar novos apps nesta estrutura, o comando deve ser adaptado para especificar o caminho completo:

```bash
poetry run python manage.py startapp <nome_do_app> apps/<nome_do_app>
```

Além disso, o arquivo `classificador/settings.py` precisa ser configurado para que o Django encontre os apps dentro de `apps/`. Para isso, é necessário adicionar as seguintes linhas logo após a definição de `BASE_DIR`:

```python
import sys

# Add apps directory to Python path
sys.path.insert(0, str(BASE_DIR / "apps"))
```

Com essa configuração, os apps podem ser referenciados diretamente no `INSTALLED_APPS` (ex: `"core"`) sem necessidade de usar o prefixo `apps.` (ex: `"apps.core"`).