from __future__ import annotations

from typing import Any

from django.contrib.admin.widgets import ForeignKeyRawIdWidget


class ForeignKeySemanticDisplayRawIdWidget(ForeignKeyRawIdWidget):
    """
    Variante do ForeignKeyRawIdWidget que mantém o valor submetido como PK
    (para o Django continuar conseguindo validar/limpar o form), mas exibe
    ao usuário o identificador semântico do objeto relacionado (*_id).

    Observação: a exibição é calculada no render do form (GET). Se o usuário
    alterar via popup do "lookup", a exibição pode não atualizar automaticamente
    (o valor submetido continuará correto pois o campo real (hidden) é o PK).
    """

    template_name = "admin/widgets/foreign_key_semantic_raw_id.html"

    def __init__(
        self,
        rel,
        admin_site,
        *,
        semantic_field: str,
        attrs: dict[str, Any] | None = None,
        using: str | None = None,
    ):
        super().__init__(rel, admin_site, attrs=attrs, using=using)
        self.semantic_field = semantic_field

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)

        semantic_value = ""
        if context["widget"].get("value"):
            try:
                key = self.rel.get_related_field().name
                obj = (
                    self.rel.model._default_manager.using(self.db).get(
                        **{key: context["widget"]["value"]}
                    )
                )
                semantic_value = getattr(obj, self.semantic_field, "") or ""
            except Exception:
                semantic_value = ""

        context["widget"]["semantic_value"] = semantic_value
        return context

