from django import forms
from django.forms import RadioSelect, TextInput, Textarea

from apps.core.models import (
    SerieClassificacao,
    Classificacao,
    NivelHierarquico,
    ItemClassificacao,
    item_semantic_id_from_receita_cod,
)
from apps.core.domain_choices import ORGAOS_ENTIDADES_GROUPED_CHOICES
from apps.core.null_normalization import normalize_text_field_value


class PlaceholderNullNormalizationFormMixin:
    """
    Normaliza placeholders textuais ("NULL"/"-") para ausência de dado.

    - Na renderização inicial: exibe vazio no formulário.
    - No clean: canoniza para None, evitando falso-positivo em comparação.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        model = getattr(getattr(self, "_meta", None), "model", None)
        if not model:
            return
        for field_name in self.fields.keys():
            if field_name not in self.initial:
                continue
            normalized = normalize_text_field_value(model, field_name, self.initial.get(field_name))
            if normalized is None and self.initial.get(field_name) is not None:
                self.initial[field_name] = ""
                self.fields[field_name].initial = ""

    def clean(self):
        cleaned = super().clean()
        model = getattr(getattr(self, "_meta", None), "model", None)
        if not model:
            return cleaned
        for field_name in list(cleaned.keys()):
            cleaned[field_name] = normalize_text_field_value(model, field_name, cleaned.get(field_name))
        return cleaned


class SerieClassificacaoForm(PlaceholderNullNormalizationFormMixin, forms.ModelForm):
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


class ClassificacaoForm(PlaceholderNullNormalizationFormMixin, forms.ModelForm):
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


class NivelHierarquicoForm(PlaceholderNullNormalizationFormMixin, forms.ModelForm):
    """Formulário padrão do Admin para NivelHierarquico."""

    class Meta:
        model = NivelHierarquico
        fields = "__all__"


class ItemClassificacaoForm(PlaceholderNullNormalizationFormMixin, forms.ModelForm):
    """Formulário do Admin para ItemClassificacao com widgets ajustados."""

    item_id = forms.CharField(
        disabled=True,
        required=False,
        widget=TextInput(attrs={"style": "width:20em; background-color:#f4f4f4; color:#555;"}),
    )
    matriz = forms.ChoiceField(
        choices=[
            ("matriz", "Matriz"),
            ("detalhe", "Detalhe"),
        ],
        widget=RadioSelect,
        required=True,
    )
    item_gerado = forms.ChoiceField(
        choices=[
            ("sim", "Sim"),
            ("nao", "Não"),
        ],
        widget=RadioSelect,
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        mf = ItemClassificacao._meta.get_field("matriz")
        self.fields["matriz"].label = mf.verbose_name
        self.fields["matriz"].help_text = mf.help_text or ""
        # ModelForm pode manter initial["matriz"] como bool da instância, enquanto
        # o ChoiceField trafega strings ("matriz"/"detalhe"). Normalizamos sempre
        # para evitar falso positivo de alteração em POST sem mudanças.
        raw = self.initial.get("matriz")
        if isinstance(raw, bool):
            use_matriz = raw
        elif raw == "matriz":
            use_matriz = True
        elif raw == "detalhe":
            use_matriz = False
        else:
            use_matriz = bool(getattr(self.instance, "matriz", False))
        key = "matriz" if use_matriz else "detalhe"
        self.initial["matriz"] = key
        self.fields["matriz"].initial = key

        ig = ItemClassificacao._meta.get_field("item_gerado")
        self.fields["item_gerado"].label = ig.verbose_name
        self.fields["item_gerado"].help_text = ig.help_text or ""
        raw_ig = self.initial.get("item_gerado")
        if isinstance(raw_ig, bool):
            use_gerado = raw_ig
        elif raw_ig == "sim":
            use_gerado = True
        elif raw_ig == "nao":
            use_gerado = False
        else:
            use_gerado = bool(getattr(self.instance, "item_gerado", False))
        ig_key = "sim" if use_gerado else "nao"
        self.initial["item_gerado"] = ig_key
        self.fields["item_gerado"].initial = ig_key

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

    def clean_matriz(self):
        return self.cleaned_data["matriz"] == "matriz"

    def clean_item_gerado(self):
        return self.cleaned_data["item_gerado"] == "sim"

    class Meta:
        model = ItemClassificacao
        fields = "__all__"
        widgets = {
            "receita_nome": TextInput(attrs={"style": "width:110em;"}),
        }
