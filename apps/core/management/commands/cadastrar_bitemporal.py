"""
Cadastro genérico para recursos bitemporais (ADR-004).

Novo registro: data_registro_inicio = data da operação, data_registro_fim = sentinela.
Campos e FKs definidos em core.bitemporal_registry.
"""
import json
from datetime import date

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.bitemporal_registry import (
    RESOURCES,
    get_resource,
    get_model_for_resource,
    get_sentinela_date,
    resolve_fk,
)
from core.models import VALID_TIME_SENTINEL


class Command(BaseCommand):
    help = (
        "Cadastra um novo registro em um recurso bitemporal. "
        "Use --recurso e --data (JSON com os campos do recurso). "
        "data_vigencia_inicio e data_vigencia_fim podem vir em --data; "
        "data_registro_* são preenchidos automaticamente."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--recurso",
            choices=sorted(RESOURCES.keys()),
            required=True,
            help="Recurso bitemporal (ex.: nivel_hierarquico, serie_classificacao).",
        )
        parser.add_argument(
            "--data",
            required=True,
            help='JSON com os campos do registro (ex.: {"nivel_id":"NIVEL-1","nivel_ref":1,...}).',
        )
        parser.add_argument(
            "--data-vigencia-inicio",
            default=None,
            help="Data de início da vigência (AAAA-MM-DD). Se omitido, deve constar em --data.",
        )
        parser.add_argument(
            "--data-vigencia-fim",
            default=VALID_TIME_SENTINEL,
            help=f"Data de fim da vigência (padrão: {VALID_TIME_SENTINEL}).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Apenas valida e exibe o que seria criado, sem gravar.",
        )

    def handle(self, *args, **options):
        resource_name = options["recurso"]
        try:
            data = json.loads(options["data"])
        except json.JSONDecodeError as e:
            raise CommandError(f"--data JSON inválido: {e}") from e

        if not isinstance(data, dict):
            raise CommandError("--data deve ser um objeto JSON (dict).")

        res = get_resource(resource_name)
        model = get_model_for_resource(resource_name)
        data_op = date.today()
        sentinela = get_sentinela_date()

        # Vigência: argumentos ou --data
        data_vig_ini = options.get("data_vigencia_inicio") or data.get("data_vigencia_inicio")
        data_vig_fim = data.get("data_vigencia_fim") or options.get("data_vigencia_fim")
        if not data_vig_ini:
            raise CommandError("Informe data_vigencia_inicio em --data ou --data-vigencia-inicio.")
        if isinstance(data_vig_ini, str):
            data_vig_ini = date.fromisoformat(data_vig_ini)
        if isinstance(data_vig_fim, str):
            data_vig_fim = date.fromisoformat(data_vig_fim)
        if data_vig_ini > data_vig_fim:
            raise CommandError("data_vigencia_inicio deve ser <= data_vigencia_fim.")

        payload = {}
        for f in res["fields"]:
            name = f["name"]
            required = f.get("required", False)
            default = f.get("default")
            val = data.get(name)
            if val is None and default is not None:
                val = default
            if required and val is None and val != 0:
                raise CommandError(f"Campo obrigatório ausente em --data: {name}")

            if f.get("type") == "fk" and val not in (None, ""):
                payload[name] = resolve_fk(resource_name, f, val)
            elif f.get("type") == "integer" and val is not None:
                payload[name] = int(val)
            elif f.get("type") == "boolean":
                payload[name] = bool(val) if val is not None else default or False
            elif f.get("type") == "date" and val is not None:
                payload[name] = date.fromisoformat(val) if isinstance(val, str) else val
            elif val is not None:
                payload[name] = val

        payload["data_vigencia_inicio"] = data_vig_ini
        payload["data_vigencia_fim"] = data_vig_fim
        payload["data_registro_inicio"] = data_op
        payload["data_registro_fim"] = sentinela

        if options["dry_run"]:
            self.stdout.write(self.style.WARNING("Dry-run: nenhuma alteração no banco."))
            for k, v in payload.items():
                self.stdout.write(f"  {k}: {v}")
            return

        with transaction.atomic():
            model.objects.create(**payload)
        self.stdout.write(
            self.style.SUCCESS(
                f"Registro cadastrado em {resource_name} (vigência {data_vig_ini} a {data_vig_fim})."
            )
        )
