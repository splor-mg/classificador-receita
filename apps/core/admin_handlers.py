"""
Handlers para fluxos de Admin.

BitemporalChangeHandler — coordena fluxo de confirmação bitemporal (sobrescrever / nova vigência).
"""
from typing import List, Tuple

from django.template.response import TemplateResponse
from django.http import HttpResponseRedirect


class BitemporalChangeHandler:
    """
    Handler que gerencia o fluxo de confirmação bitemporal no Admin.

    Responsabilidades:
    - Detectar se houve alteração no form.
    - Renderizar página de confirmação com diffs.
    - Chamar bitemporal_service para aplicar a atualização.
    - Não realiza export — isso é responsabilidade do AutoExportAdminMixin.
    """

    def __init__(self, admin_instance):
        self.admin = admin_instance
        self.model = admin_instance.model

    def handle(self, request, object_id, form_url, extra_context):
        """
        Processa o fluxo de confirmação bitemporal.

        Retorna:
        - TemplateResponse se deve mostrar página de confirmação.
        - HttpResponseRedirect após aplicar atualização bitemporal.
        - None se deve seguir fluxo normal do Admin.
        """
        # Só intercepta POST para objetos existentes (edição)
        if not object_id or request.method != "POST":
            return None

        obj = self.admin.get_object(request, object_id)
        form_class = self.admin.get_form(request, obj)
        form = form_class(request.POST, request.FILES, instance=obj)

        if not form.is_valid():
            return None

        if not form.has_changed():
            return None

        # Houve mudança. Se não há strategy no POST, renderiza confirmação.
        strategy = request.POST.get("edit_strategy")

        if not strategy:
            diffs = []
            for field in form.changed_data:
                field_meta = self.model._meta.get_field(field)
                label = field_meta.verbose_name.capitalize()
                old = form.initial.get(field)
                new = form.cleaned_data.get(field)
                diffs.append({"field": label, "old": old, "new": new})

            # Preservar POST items para re-postar após confirmação
            post_items: List[Tuple[str, str]] = []
            for k in request.POST.keys():
                for v in request.POST.getlist(k):
                    post_items.append((k, v))

            context = {
                **self.admin.admin_site.each_context(request),
                "title": "Confirmar atualização",
                "opts": self.model._meta,
                "original": obj,
                "object": obj,
                "diffs": diffs,
                "post_items": post_items,
                "changed_data": form.changed_data,
                "form": form,
            }
            return TemplateResponse(request, "admin/bitemporal_confirm.html", context)

        # Strategy presente: aplicar atualização bitemporal
        new_values = {field: form.cleaned_data[field] for field in form.changed_data}

        from apps.core.bitemporal_service import apply_bitemporal_update

        apply_bitemporal_update(
            model=self.model,
            prev_obj=obj,
            new_values=new_values,
            strategy=strategy,
        )

        self.admin.message_user(request, "Atualização bitemporal aplicada com sucesso.")
        return HttpResponseRedirect("..")
