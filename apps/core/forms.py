from datetime import date

from django import forms
from django.forms import RadioSelect, TextInput, Textarea

from apps.core.models import (
    SerieClassificacao,
    Classificacao,
    NivelHierarquico,
    ItemClassificacao,
    TRANSACTION_TIME_SENTINEL,
    item_semantic_id_from_receita_cod,
)
from apps.core.code_mask import (
    get_latest_active_vigente_classificacao,
    get_mask_from_classificacao_estrutura,
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
        # Voltar da confirmação bitemporal: syncCancelFormWithEdits copia o valor do
        # <select> da confirmação, cujas options usam "True"/"False" (bool do Django),
        # para os hiddens com o mesmo nome do form — incompatível com sim/nao e matriz/detalhe.
        data = kwargs.get("data")
        if data is not None and hasattr(data, "copy"):
            data = data.copy()
            _ig = data.get("item_gerado")
            if _ig in ("True", "true", "False", "false"):
                data["item_gerado"] = "sim" if str(_ig).lower() == "true" else "nao"
            _mz = data.get("matriz")
            if _mz in ("True", "true", "False", "false"):
                data["matriz"] = "matriz" if str(_mz).lower() == "true" else "detalhe"
            kwargs["data"] = data

        super().__init__(*args, **kwargs)
        mf = ItemClassificacao._meta.get_field("matriz")
        self.fields["matriz"].label = mf.verbose_name
        self.fields["matriz"].help_text = mf.help_text or ""
        is_change_form = bool(self.instance and getattr(self.instance, "pk", None))
        if is_change_form:
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
        else:
            # No add, não pré-seleciona Matriz/Detalhe.
            self.initial.pop("matriz", None)
            self.fields["matriz"].initial = None

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

    def _get_receita_cod_digit_rule(self, classificacao):
        if classificacao is None:
            classificacao = get_latest_active_vigente_classificacao(date.today())
        mask, estrutura = get_mask_from_classificacao_estrutura(classificacao, date.today())
        expected_digits = sum(mask) if mask else None
        return expected_digits, estrutura

    def clean(self):
        cleaned = super().clean()

        nivel = cleaned.get("nivel_id")
        is_matriz = cleaned.get("matriz")
        if nivel is not None and getattr(nivel, "nivel_numero", None) == 1 and is_matriz is False:
            self.add_error(
                "matriz",
                "Itens de nível 1 só podem ser salvos como Matriz.",
            )

        receita_cod = (cleaned.get("receita_cod") or "").strip().replace(".", "")
        classificacao = cleaned.get("classificacao_id")
        expected_digits, estrutura = self._get_receita_cod_digit_rule(classificacao)

        if receita_cod and not expected_digits:
            self.add_error(
                "receita_cod",
                (
                    "Não foi possível determinar a estrutura ativa da classificação "
                    "(`estrutura_codigo`) para validar o código canônico."
                ),
            )
            return cleaned

        if receita_cod and expected_digits:
            current_len = len(receita_cod)
            if current_len > expected_digits:
                self.add_error(
                    "receita_cod",
                    (
                        f"Código informado tem {current_len} dígitos, mas a classificação "
                        f"selecionada exige {expected_digits} dígitos pela estrutura "
                        f"{estrutura or 'vigente'}. Ajuste o código para continuar."
                    ),
                )
            elif current_len < expected_digits:
                # Submit resiliente: completa com zeros canônicos para manter consistência
                # com o limite vigente/selecionado.
                receita_cod = receita_cod.ljust(expected_digits, "0")

            cleaned["receita_cod"] = receita_cod

        return cleaned

    class Meta:
        model = ItemClassificacao
        fields = "__all__"
        widgets = {
            "receita_nome": TextInput(attrs={"style": "width:110em;"}),
        }
