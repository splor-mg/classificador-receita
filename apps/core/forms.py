from django import forms
from django.forms import TextInput, Textarea

from apps.core.models import SerieClassificacao


class SerieClassificacaoForm(forms.ModelForm):
    """Formulário do Admin para SerieClassificacao com widgets ajustados."""

    class Meta:
        model = SerieClassificacao
        fields = "__all__"
        widgets = {
            "serie_nome": TextInput(attrs={"style": "width:60ch;"}),
            "descricao": Textarea(attrs={"style": "width:60ch; height:8em;"}),
        }

