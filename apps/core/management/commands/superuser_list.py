"""
List superusers (username, email).

Usage examples:
  # Human-readable output (requires DEBUG=True in `classificador/settings.py` or ALLOW_ADMIN_LIST=1 in the `.env` file, as described in `.env.example`)
  poetry run python manage.py superuser_list

  # JSON output (useful for scripts)
  poetry run python manage.py superuser_list --json

  # Only count
  poetry run python manage.py superuser_list --count

Notes:
  - For safety, this command only runs when Django `DEBUG` is True OR when the
    environment variable `ALLOW_ADMIN_LIST=1` is set. This prevents accidental
    exposure of admin accounts in production.
  - To allow this in non-debug environments, set `ALLOW_ADMIN_LIST=1` (see .env.example).
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings
import json
import os


class Command(BaseCommand):
    help = "Lista superusers (username, email). Somente para uso em DEBUG ou com ALLOW_ADMIN_LIST=1."

    def add_arguments(self, parser):
        parser.add_argument("--json", action="store_true", help="Saída em JSON")
        parser.add_argument("--count", action="store_true", help="Mostra apenas a contagem")
        parser.add_argument(
            "--require-debug",
            action="store_true",
            help="Requer settings.DEBUG True para executar (proteção extra).",
        )

    def handle(self, *args, **options):
        # Proteção: só permitir em DEBUG ou quando variável explícita for definida
        allow = settings.DEBUG or os.environ.get("ALLOW_ADMIN_LIST") == "1"
        if options.get("require_debug") and not settings.DEBUG:
            self.stderr.write("Execução abortada: settings.DEBUG deve ser True quando --require-debug é passado.")
            return
        if not allow:
            self.stderr.write(
                "Execução abortada: listar superusers está restrito (DEBUG=False). "
                "Defina ALLOW_ADMIN_LIST=1 para permitir explicitamente."
            )
            return

        U = get_user_model()
        qs = U.objects.filter(is_superuser=True).values("username", "email", "is_active", "date_joined")
        rows = list(qs)
        if options["count"]:
            self.stdout.write(str(len(rows)))
            return
        if options["json"]:
            # Serialize dates
            def _d(obj):
                if hasattr(obj, "isoformat"):
                    return obj.isoformat()
                raise TypeError

            self.stdout.write(json.dumps(rows, default=_d))
            return

        if not rows:
            self.stdout.write("Nenhum superuser encontrado.")
            return

        for r in rows:
            self.stdout.write(
                f'{r["username"]} — {r["email"]} — active={r["is_active"]} joined={r["date_joined"]}'
            )

