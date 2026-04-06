from django import forms
from django.forms import TextInput, Textarea

from apps.core.models import (
    SerieClassificacao,
    Classificacao,
    NivelHierarquico,
    ItemClassificacao,
    item_semantic_id_from_receita_cod,
)
from apps.core.domain_choices import ORGAOS_ENTIDADES_GROUPED_CHOICES


class SerieClassificacaoForm(forms.ModelForm):
    """Formulário do Admin para SerieClassificacao com widgets ajustados."""

    orgao_responsavel = forms.ChoiceField(
        choices=[("", "---------")] + ORGAOS_ENTIDADES_GROUPED_CHOICES,
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


class ClassificacaoForm(forms.ModelForm):
    """Formulário do Admin para Classificacao com widgets ajustados."""

    class Meta:
        model = Classificacao
        fields = "__all__"
        widgets = {
            # Mantém a largura alinhada visualmente ao textarea de descrição.
            "classificacao_nome": TextInput(
                attrs={"class": "vLargeTextField", "style": "width:87ch;"}
            ),
        }


class NivelHierarquicoForm(forms.ModelForm):
    """Formulário padrão do Admin para NivelHierarquico."""

    class Meta:
        model = NivelHierarquico
        fields = "__all__"


class ItemClassificacaoForm(forms.ModelForm):
    """Formulário do Admin para ItemClassificacao com widgets ajustados."""

    item_id = forms.CharField(
        disabled=True,
        required=False,
        widget=TextInput(attrs={"style": "width:20em; background-color:#f4f4f4; color:#555;"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        receita_cod = ""
        if self.instance and getattr(self.instance, "pk", None):
            receita_cod = self.instance.receita_cod or ""
            self.fields["item_id"].initial = self.instance.item_id or item_semantic_id_from_receita_cod(receita_cod)
        else:
            initial_receita_cod = self.initial.get("receita_cod") or ""
            self.fields["item_id"].initial = item_semantic_id_from_receita_cod(initial_receita_cod) if initial_receita_cod else ""

        parent_field = self.fields.get("parent_item_id")
        nivel = getattr(self.instance, "nivel_id", None) if self.instance else None
        if parent_field is not None and nivel is not None and getattr(nivel, "nivel_numero", None) == 1:
            parent_field.required = False
            parent_field.initial = None
            parent_field.widget.attrs["data_readonly_root"] = "1"
            parent_field.widget.attrs["data_empty_display"] = ""
            parent_field.widget.attrs["data_root_message"] = "Item raiz, de nível 1, não possui item pai."

    class Meta:
        model = ItemClassificacao
        fields = "__all__"
        widgets = {
            "receita_nome": TextInput(attrs={"style": "width:110em;"}),
        }
