"""
Exporta qualquer recurso definido em core.bitemporal_registry para CSV.

Suporta recursos SCD-2 (bitemporais) e SCD-1 (monotemporais) definidos no registry.
- Para SCD-2 (bitemporal): --scope all|current (default all)
- Para SCD-1: exporta todas as linhas atuais.
"""
import csv
import sys
from datetime import date
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.core.bitemporal_registry import (
    get_resource,
    get_model_for_resource,
    get_sentinela_date,
    get_export_value,
    RESOURCES,
)


class Command(BaseCommand):
    help = "Exporta recurso (bitemporal ou monotemporal) para CSV. Usa definições em core.bitemporal_registry."

    def add_arguments(self, parser):
        parser.add_argument("output", nargs="?", default=None, help="Caminho do CSV de saída (stdout se omitido).")
        parser.add_argument("--recurso", required=True, choices=sorted(RESOURCES.keys()), help="Nome do recurso a exportar.")
        parser.add_argument("--scope", choices=["all", "current"], default="all", help="Escopo para bitemporal (all=current).")
        parser.add_argument("--dry-run", action="store_true", help="Somente simula, sem gravar.")
        parser.add_argument("--backup", action="store_true", help="Se presente, faz backup do seed alvo antes de sobrescrever.")
        parser.add_argument("--backup-dir", default=None, help="Diretório onde gravar backups (padrão: mesma pasta do destino).")

    def handle(self, *args, **options):
        recurso = options["recurso"]
        output = options["output"]
        scope = options["scope"]
        dry_run = options["dry_run"]
        do_backup = options.get("backup", False)
        backup_dir = options.get("backup_dir")

        res = get_resource(recurso)
        model = get_model_for_resource(recurso)
        columns = res["export_columns"]
        sentinela = get_sentinela_date()

        qs = model.objects.all()
        # If bitemporal resource (has data_registro_inicio in model), handle scope
        is_bitemporal = hasattr(model, "data_registro_inicio")
        if is_bitemporal and scope == "current":
            qs = qs.filter(data_registro_fim=sentinela)

        order = res.get("order_by", [])
        if order:
            qs = qs.order_by(*order)

        if dry_run:
            self.stdout.write(f"Dry-run: {qs.count()} linhas selecionadas para recurso '{recurso}'.")
            self.stdout.write(f"Colunas: {columns}")
            return

        # Delegate to exporter function (uses COPY internally)
        from core.exporter import export_resource

        result = export_resource(recurso=recurso, output=output, scope=scope, do_backup=do_backup, backup_dir=backup_dir, dry_run=dry_run)
        if dry_run:
            self.stdout.write(f"Dry-run: {result.get('rows')} rows would be exported.")
            return
        self.stdout.write(self.style.SUCCESS(f"Export finished: output={result.get('output')} backup={result.get('backup')}"))

