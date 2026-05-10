"""
Remove todas as tabelas físicas do app ``core`` e os registros em ``django_migrations``
para esse app (mesmo banco indicado por ``--database``).

Útil quando o schema ficou inconsistente com o histórico de migrações (ex.: ``lista_abreviacoes``
nunca criada, mas ``0001_initial`` já marcada como aplicada).

Depois::

    poetry run python manage.py migrate core
"""

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.db import connections

# Tabela antiga do model AliasLexico; pode permanecer no PG após renomear db_table.
_LEGACY_CORE_TABLES = frozenset({"alias_lexico"})


class Command(BaseCommand):
    help = (
        "DROP CASCADE de todas as tabelas gerenciadas do app core + DELETE em django_migrations "
        "para app 'core'. Em seguida rode migrate core."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--database",
            default="default",
            help="Alias Django do banco (default: default).",
        )
        parser.add_argument(
            "--noinput",
            action="store_true",
            help="Não pedir confirmação interativa.",
        )

    def handle(self, *args, **options):
        alias = options["database"]
        noinput = options["noinput"]

        if alias not in connections:
            raise CommandError(f"Database alias '{alias}' não está configurado.")

        conn = connections[alias]

        core_tables = {
            model._meta.db_table
            for model in apps.get_app_config("core").get_models()
            if model._meta.managed
        }

        existing = set(conn.introspection.table_names())
        to_drop = sorted((core_tables | _LEGACY_CORE_TABLES) & existing)

        self.stdout.write(self.style.WARNING(f"Banco: {alias}"))
        if to_drop:
            self.stdout.write("Tabelas do app core que serão removidas (CASCADE):")
            for t in to_drop:
                self.stdout.write(f"  - {t}")
        else:
            self.stdout.write(self.style.NOTICE("Nenhuma tabela do app core encontrada no banco."))

        if "django_migrations" in existing:
            self.stdout.write(
                self.style.WARNING(
                    "Registros em django_migrations para app 'core' também serão removidos."
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    "Tabela django_migrations não encontrada; apenas DROP de tabelas core (se houver)."
                )
            )

        if not noinput:
            confirm = input("Continuar? [y/N] ").strip().lower()
            if confirm not in {"y", "yes", "s", "sim"}:
                self.stdout.write(self.style.NOTICE("Cancelado."))
                return

        with conn.cursor() as cursor:
            if to_drop:
                quoted = ", ".join(conn.ops.quote_name(t) for t in to_drop)
                cursor.execute(f"DROP TABLE IF EXISTS {quoted} CASCADE")
                self.stdout.write(self.style.SUCCESS(f"DROP TABLE executado ({len(to_drop)} tabela(s))."))

            deleted = 0
            if "django_migrations" in existing:
                cursor.execute("DELETE FROM django_migrations WHERE app = %s", ["core"])
                deleted = cursor.rowcount if cursor.rowcount is not None and cursor.rowcount >= 0 else 0

        if "django_migrations" in existing:
            self.stdout.write(
                self.style.SUCCESS(
                    f"django_migrations: removidos registros do app 'core' "
                    f"(rowcount={deleted}). Execute: python manage.py migrate core"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("Execute: python manage.py migrate core")
            )
