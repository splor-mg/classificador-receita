"""
Handlers para fluxos de Admin.

BitemporalChangeHandler — coordena fluxo de confirmação bitemporal (sobrescrever / nova vigência).
"""
from datetime import date, timedelta
from typing import Any, Dict, List, Tuple

from django.template.response import TemplateResponse
from django.http import HttpResponseRedirect
from django.urls import reverse

from apps.core.bitemporal_registry import get_sentinela_date

VIGENCIA_FIELDS = {"data_vigencia_inicio", "data_vigencia_fim"}


class BitemporalChangeHandler:
    """
    Handler que gerencia o fluxo de confirmação bitemporal no Admin.

    Responsabilidades:
    - Detectar se houve alteração no form.
    - Renderizar página de confirmação com diffs separados (Atributos Gerais vs Vigência).
    - Calcular preview de como ficarão os registros em cada estratégia.
    - Chamar bitemporal_update para aplicar a atualização.
    - Não realiza export — isso é responsabilidade do AutoExportAdminMixin.
    """

    def __init__(self, admin_instance):
        self.admin = admin_instance
        self.model = admin_instance.model

    def _build_diffs(self, form, changed_data: List[str]) -> Tuple[List[Dict], List[Dict]]:
        """Separa diffs em atributos gerais e vigência."""
        general_diffs = []
        vigencia_diffs = []

        for field in changed_data:
            field_meta = self.model._meta.get_field(field)
            label = field_meta.verbose_name.capitalize()
            old = form.initial.get(field)
            new = form.cleaned_data.get(field)
            diff_entry = {"field": label, "field_name": field, "old": old, "new": new}

            if field in VIGENCIA_FIELDS:
                vigencia_diffs.append(diff_entry)
            else:
                general_diffs.append(diff_entry)

        return general_diffs, vigencia_diffs

    def _compute_vigencia_preview(
        self, obj: Any, form, changed_data: List[str]
    ) -> Dict[str, Any]:
        """
        Calcula preview das vigências para ambas estratégias.

        Retorna dict com:
        - current_vig_inicio: data_vigencia_inicio atual do objeto
        - current_vig_fim: data_vigencia_fim atual do objeto
        - new_vig_inicio: nova data_vigencia_inicio (do form ou 1º jan do ano atual)
        - new_vig_fim: nova data_vigencia_fim (do form ou sentinela)
        - nova_vigencia_preview: lista de registros para estratégia "nova_vigencia"
        - sobrescrever_preview: lista de registros para estratégia "sobrescrever"
        """
        sentinela = get_sentinela_date()
        today = date.today()
        first_jan_current_year = date(today.year, 1, 1)

        current_vig_inicio = getattr(obj, "data_vigencia_inicio", None)
        current_vig_fim = getattr(obj, "data_vigencia_fim", None)

        has_vig_inicio_change = "data_vigencia_inicio" in changed_data
        has_vig_fim_change = "data_vigencia_fim" in changed_data

        if has_vig_inicio_change:
            new_vig_inicio = form.cleaned_data.get("data_vigencia_inicio")
        else:
            new_vig_inicio = first_jan_current_year

        if has_vig_fim_change:
            new_vig_fim = form.cleaned_data.get("data_vigencia_fim")
        else:
            new_vig_fim = sentinela

        prev_vig_fim_closed = new_vig_inicio - timedelta(days=1)

        nova_vigencia_preview = [
            {
                "version": "Versão 1",
                "vig_inicio": current_vig_inicio,
                "vig_fim": prev_vig_fim_closed,
                "strikethrough": False,
            },
            {
                "version": "Versão 2",
                "vig_inicio": new_vig_inicio,
                "vig_fim": sentinela,
                "strikethrough": False,
            },
        ]

        if has_vig_inicio_change or has_vig_fim_change:
            sobrescrever_preview = [
                {
                    "version": "Versão 1",
                    "vig_inicio": current_vig_inicio,
                    "vig_fim": current_vig_fim,
                    "strikethrough": True,
                },
                {
                    "version": "Versão 2",
                    "vig_inicio": form.cleaned_data.get("data_vigencia_inicio", current_vig_inicio),
                    "vig_fim": form.cleaned_data.get("data_vigencia_fim", current_vig_fim),
                    "strikethrough": False,
                },
            ]
        else:
            sobrescrever_preview = [
                {
                    "version": "Versão 1",
                    "vig_inicio": current_vig_inicio,
                    "vig_fim": current_vig_fim,
                    "strikethrough": False,
                },
            ]

        return {
            "current_vig_inicio": current_vig_inicio,
            "current_vig_fim": current_vig_fim,
            "new_vig_inicio": new_vig_inicio,
            "new_vig_fim": new_vig_fim,
            "nova_vigencia_preview": nova_vigencia_preview,
            "sobrescrever_preview": sobrescrever_preview,
        }

    def handle(self, request, object_id, form_url, extra_context):
        """
        Processa o fluxo de confirmação bitemporal.

        Retorna:
        - TemplateResponse se deve mostrar página de confirmação.
        - HttpResponseRedirect após aplicar atualização bitemporal.
        - None se deve seguir fluxo normal do Admin.
        """
        if not object_id or request.method != "POST":
            return None

        obj = self.admin.get_object(request, object_id)
        form_class = self.admin.get_form(request, obj)
        form = form_class(request.POST, request.FILES, instance=obj)

        if not form.is_valid():
            return None

        if not form.has_changed():
            return None

        strategy = request.POST.get("edit_strategy")

        if not strategy:
            general_diffs, vigencia_diffs = self._build_diffs(form, form.changed_data)
            vigencia_preview = self._compute_vigencia_preview(obj, form, form.changed_data)

            post_items: List[Tuple[str, str]] = []
            for k in request.POST.keys():
                for v in request.POST.getlist(k):
                    post_items.append((k, v))

            import json
            nova_vigencia_preview_json = json.dumps(
                [
                    {
                        "version": r["version"],
                        "vig_inicio": r["vig_inicio"].isoformat() if r["vig_inicio"] else None,
                        "vig_fim": r["vig_fim"].isoformat() if r["vig_fim"] else None,
                        "strikethrough": r["strikethrough"],
                    }
                    for r in vigencia_preview["nova_vigencia_preview"]
                ]
            )
            sobrescrever_preview_json = json.dumps(
                [
                    {
                        "version": r["version"],
                        "vig_inicio": r["vig_inicio"].isoformat() if r["vig_inicio"] else None,
                        "vig_fim": r["vig_fim"].isoformat() if r["vig_fim"] else None,
                        "strikethrough": r["strikethrough"],
                    }
                    for r in vigencia_preview["sobrescrever_preview"]
                ]
            )

            context = {
                **self.admin.admin_site.each_context(request),
                "title": "Confirmar atualização",
                "opts": self.model._meta,
                "original": obj,
                "object": obj,
                "general_diffs": general_diffs,
                "vigencia_diffs": vigencia_diffs,
                "vigencia_preview": vigencia_preview,
                "nova_vigencia_preview_json": nova_vigencia_preview_json,
                "sobrescrever_preview_json": sobrescrever_preview_json,
                "post_items": post_items,
                "changed_data": form.changed_data,
                "form": form,
            }
            return TemplateResponse(request, "admin/bitemporal_confirm.html", context)

        new_values = {field: form.cleaned_data[field] for field in form.changed_data}

        from apps.core.bitemporal_update import apply_bitemporal_update

        apply_bitemporal_update(
            model=self.model,
            prev_obj=obj,
            new_values=new_values,
            strategy=strategy,
        )

        self.admin.message_user(request, "Atualização bitemporal aplicada com sucesso.")

        if hasattr(self.admin, 'trigger_export'):
            self.admin.trigger_export(request, self.model)

        changelist_url = reverse(
            f'admin:{self.model._meta.app_label}_{self.model._meta.model_name}_changelist'
        )
        return HttpResponseRedirect(changelist_url)
