"""
Exporta recurso bitemporal para CSV no formato do seed (ADR-004).

Aplica-se apenas aos recursos do bitemporal_registry (Regras 1 a 7);
base_legal_tecnica (SCD-1) não está no registry e não é exportada por este comando.
Colunas e ordem definidas em core.bitemporal_registry (export_columns).
"""
import csv
import sys
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.core.bitemporal_registry import (
    RESOURCES,
    get_resource,
    get_model_for_resource,
    get_export_value,
)


class Command(BaseCommand):
    help = (
        "Exporta um recurso bitemporal para CSV no formato do seed. "
        "Use --recurso e opcionalmente o caminho de saída (se omitido, imprime na saída padrão)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "output",
            nargs="?",
            default=None,
            help="Caminho do arquivo CSV de saída. Se omitido, imprime na saída padrão.",
        )
        parser.add_argument(
            "--recurso",
            choices=sorted(RESOURCES.keys()),
            required=True,
            help="Recurso bitemporal a exportar.",
        )
        parser.add_argument(
            "--ordenar",
            choices=["registro", "vigencia"],
            default="registro",
            help="Ordenação: por data_registro_inicio (registro) ou por data_vigencia_inicio (vigencia).",
        )

    def handle(self, *args, **options):
        resource_name = options["recurso"]
        res = get_resource(resource_name)
        model = get_model_for_resource(resource_name)
        columns = res["export_columns"]
        order = res.get("order_by", [])
        order_key = "data_registro_inicio" if options["ordenar"] == "registro" else "data_vigencia_inicio"
        if order:
            order = [o for o in order if "data_registro" not in o and "data_vigencia" not in o] + [order_key]
        else:
            order = [order_key]

        qs = model.objects.all()
        if res.get("select_related"):
            qs = qs.select_related(*res["select_related"])
        qs = qs.order_by(*order)

        fields_by_name = {f["name"]: f for f in res["fields"]}

        rows = []
        for obj in qs:
            row = {}
            for col in columns:
                field_meta = fields_by_name.get(col)
                val = get_export_value(obj, col, field_meta, resource_name)
                if val is None and (not field_meta or field_meta.get("type") != "fk"):
                    val = ""
                if hasattr(val, "isoformat"):
                    val = val.isoformat()
                row[col] = val
            rows.append(row)

        output_path = options.get("output")
        if output_path:
            path = Path(output_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=columns)
                writer.writeheader()
                writer.writerows(rows)
            self.stdout.write(self.style.SUCCESS(f"Exportadas {len(rows)} linhas para {path}."))
        else:
            writer = csv.DictWriter(sys.stdout, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)
