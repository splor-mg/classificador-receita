"""
Middleware do app ``core``.

``AdminChangelistSkipDefaultScopeMiddleware`` limita o alcance da flag de sessão
«lista sem filtro padrão» à visita corrente à changelist — ver
``_dev/spec_django.md``, secção «Padrões de Changelist».
"""

from apps.core.admin_mixins import (
    clear_stale_changelist_skip_default_flags,
    parse_admin_changelist_model_key,
)


class AdminChangelistSkipDefaultScopeMiddleware:
    """Invalida flags ``admin_changelist_skip_default:*`` ao sair da changelist."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/admin/"):
            active = parse_admin_changelist_model_key(request.path)
            clear_stale_changelist_skip_default_flags(
                request, active_model_key=active
            )
        return self.get_response(request)
