from django.apps import AppConfig
from django.contrib import admin


class CoreConfig(AppConfig):
    name = "apps.core"
    label = "core"

    def ready(self):
        """
        Ajusta a ordenação dos modelos exibidos na seção 'CORE' do Django Admin.

        Implementa um monkeypatch leve em AdminSite.get_app_list para reordernar
        os itens do app 'core' conforme a sequência desejada. É uma abordagem
        simples e local (executada no ready do app) que evita ter que substituir
        o AdminSite em todo o projeto.
        """
        orig_get_app_list = admin.AdminSite.get_app_list

        def get_app_list(self_site, request):
            app_list = orig_get_app_list(self_site, request)
            for app in app_list:
                if app.get("app_label") == "core":
                    models = app.get("models", [])
                    # Ordem desejada (use os nomes das classes dos models)
                    desired_order = [
                        "BaseLegalTecnica",
                        "SerieClassificacao",
                        "Classificacao",
                        "NivelHierarquico",
                        "ItemClassificacao",
                        "VarianteClassificacao",
                        "VersaoClassificacao",
                    ]
                    # Mapear por object_name (fallback para 'name' se necessário)
                    by_name = {}
                    for m in models:
                        key = m.get("object_name") or m.get("name")
                        if key:
                            by_name[key] = m
                    new_models = [by_name.pop(n) for n in desired_order if n in by_name]
                    # manter o restante na ordem original
                    remaining = [m for m in models if (m.get("object_name") or m.get("name")) not in desired_order]
                    app["models"] = new_models + remaining
                    break
            return app_list

        admin.AdminSite.get_app_list = get_app_list