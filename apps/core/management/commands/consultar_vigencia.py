"""Ask the same validity window used by the changelist search."""

from datetime import date

from django.core.management.base import BaseCommand, CommandError

from apps.core.models import (
    Classificacao,
    ItemClassificacao,
    NivelHierarquico,
    SerieClassificacao,
)
from apps.core.vigencia_search import apply_vigencia_window, describe_window
from apps.core.vigencia_window import resolve_vigencia_window

MODELS = {
    "serie": SerieClassificacao,
    "classificacao": Classificacao,
    "nivel": NivelHierarquico,
    "item": ItemClassificacao,
}


class Command(BaseCommand):
    help = (
        "Mostra a janela de vigência assumida para uma data, um período ou LDO. "
        "Versão cadastrada e LOA-PPAG continuam sem resposta na concepção."
    )

    def add_arguments(self, parser):
        parser.add_argument("--ano", default="")
        parser.add_argument("--mes", default="")
        parser.add_argument("--dia", default="")
        parser.add_argument("--ano2", default="")
        parser.add_argument("--mes2", default="")
        parser.add_argument("--dia2", default="")
        parser.add_argument("--versao", default="")
        parser.add_argument("--registro", default="")
        parser.add_argument(
            "--modelo",
            choices=sorted(MODELS),
            help="Conta as linhas desse modelo que cabem na janela.",
        )

    def handle(self, *args, **options):
        window = resolve_vigencia_window(
            today=date.today(),
            ano=options["ano"],
            mes=options["mes"],
            dia=options["dia"],
            ano2=options["ano2"],
            mes2=options["mes2"],
            dia2=options["dia2"],
            versao=options["versao"],
            registro=options["registro"],
        )
        if not window.searches:
            raise CommandError(window.messages[0] if window.messages else "A pesquisa não parte.")
        for message in window.messages:
            self.stdout.write(message)
        self.stdout.write(describe_window(window))
        model = options.get("modelo")
        if model:
            count = apply_vigencia_window(MODELS[model].objects.all(), window).count()
            self.stdout.write(f"{model}: {count}")
