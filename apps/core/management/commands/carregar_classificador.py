from django.core.management.base import BaseCommand
from core.models import SerieClassificacao  # ajuste para os models que quer popular
from django.utils import timezone


class Command(BaseCommand):
    help = "Carrega dados iniciais do classificador de receita no banco"

    def handle(self, *args, **options):
        # Exemplo simples para mostrar a estrutura
        if SerieClassificacao.objects.exists():
            self.stdout.write(self.style.WARNING(
                "Já existem registros em SerieClassificacao. Nada foi feito."
            ))
            return

        agora = timezone.now().date()
        # Aqui você colocaria os dados reais, vindos de CSV/YAML/etc.
        SerieClassificacao.objects.create(
            serie_id="CLASS_REC_MG",
            serie_nome="Classificador de Natureza de Receita - MG",
            descricao="Série principal do classificador de natureza de receita do Estado de Minas Gerais.",
            orgao_responsavel="SPLOR/MG",
            data_vigencia_inicio=agora,
            data_vigencia_fim="9999-12-31",
            data_registro_inicio=timezone.now(),
            data_registro_fim="9999-12-31 23:59:59",
        )

        self.stdout.write(self.style.SUCCESS(
            "Dados iniciais do classificador carregados com sucesso."
        ))