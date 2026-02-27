from django import forms
from django.forms import TextInput, Textarea

from apps.core.models import SerieClassificacao
from apps.core.domain_choices import ORGAOS_ENTIDADES_CHOICES


class SerieClassificacaoForm(forms.ModelForm):
    """Formulário do Admin para SerieClassificacao com widgets ajustados."""

    orgao_responsavel = forms.ChoiceField(
        choices=[
            (value, f"{value} - {label}")
            for value, label in ORGAOS_ENTIDADES_CHOICES
        ],
        label="Órgão Responsável",
        help_text="Órgão ou entidade responsável pela manutenção da série de classificações. Valores válidos em domínio/orgaos_entidades.yaml (domínio/Ref).",
    )

    class Meta:
        model = SerieClassificacao
        fields = "__all__"
        widgets = {
            "serie_nome": TextInput(attrs={"style": "width:60ch;"}),
            "descricao": Textarea(attrs={"style": "width:60ch; height:8em;"}),
        }

