from django import forms
from django.forms import TextInput, Textarea

from apps.core.models import SerieClassificacao
from apps.core.domain_choices import ORGAOS_ENTIDADES_GROUPED_CHOICES


class SerieClassificacaoForm(forms.ModelForm):
    """Formulário do Admin para SerieClassificacao com widgets ajustados."""

    orgao_responsavel = forms.ChoiceField(
        choices=ORGAOS_ENTIDADES_GROUPED_CHOICES,
        label="Órgão Responsável",
        help_text=(
            "Órgão ou entidade responsável pela manutenção da série de "
            "classificações. Valores válidos em dominios/orgaos_entidades.yaml "
            "(domainRef)."
        ),
    )

    class Meta:
        model = SerieClassificacao
        fields = "__all__"
        widgets = {
            "serie_nome": TextInput(attrs={"style": "width:60ch;"}),
            "serie_descricao": Textarea(
                attrs={"style": "width:60ch; height:8em;"},
            ),
        }
