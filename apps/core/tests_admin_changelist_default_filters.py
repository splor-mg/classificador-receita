"""Testes do pré-filtro padrão na changelist (``ChangelistDefaultFilterRedirectMixin``)."""

from unittest.mock import MagicMock, patch

from django.contrib.admin.sites import AdminSite
from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase

from apps.core.admin import ItemClassificacaoAdmin
from apps.core.admin_mixins import (
    CHANGELIST_SKIP_DEFAULT_PARAM,
    CHANGELIST_SKIP_DEFAULT_VALUE,
    REGISTRO_ATIVO_QUERY_PARAM,
    REGISTRO_ATIVO_VALUE_ANO_CORRENTE,
)
from apps.core.models import ItemClassificacao


class ChangelistDefaultFilterRedirectTests(SimpleTestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.model_admin = ItemClassificacaoAdmin(ItemClassificacao, AdminSite())
        self.changelist_path = "/admin/core/itemclassificacao/"
        self.session_key = self.model_admin._changelist_skip_default_session_key()

    def _request(self, query: str = ""):
        path = self.changelist_path
        if query:
            path = f"{path}?{query}"
        request = self.factory.get(path)
        request.session = {}
        request.user = MagicMock(is_active=True, is_staff=True)
        return request

    def test_empty_get_redirects_to_default(self) -> None:
        request = self._request()
        response = self.model_admin.changelist_view(request)
        self.assertEqual(response.status_code, 302)
        self.assertIn(
            f"{REGISTRO_ATIVO_QUERY_PARAM}={REGISTRO_ATIVO_VALUE_ANO_CORRENTE}",
            response["Location"],
        )

    def test_empty_get_with_skip_session_does_not_redirect(self) -> None:
        request = self._request()
        request.session[self.session_key] = True
        with patch(
            "apps.core.admin_mixins.admin.ModelAdmin.changelist_view",
            return_value=HttpResponse("ok"),
        ) as super_view:
            response = self.model_admin.changelist_view(request)
        self.assertEqual(response.status_code, 200)
        super_view.assert_called_once()

    def test_skip_param_sets_session_and_redirects_to_bare_path(self) -> None:
        request = self._request(
            f"{CHANGELIST_SKIP_DEFAULT_PARAM}={CHANGELIST_SKIP_DEFAULT_VALUE}"
        )
        response = self.model_admin.changelist_view(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], self.changelist_path)
        self.assertTrue(request.session.get(self.session_key))

    def test_filter_param_clears_skip_session(self) -> None:
        request = self._request(
            f"{REGISTRO_ATIVO_QUERY_PARAM}={REGISTRO_ATIVO_VALUE_ANO_CORRENTE}"
        )
        request.session[self.session_key] = True
        with patch(
            "apps.core.admin_mixins.admin.ModelAdmin.changelist_view",
            return_value=HttpResponse("ok"),
        ):
            self.model_admin.changelist_view(request)
        self.assertNotIn(self.session_key, request.session)

    def test_pagination_only_keeps_skip_session(self) -> None:
        request = self._request("p=2")
        request.session[self.session_key] = True
        with patch(
            "apps.core.admin_mixins.admin.ModelAdmin.changelist_view",
            return_value=HttpResponse("ok"),
        ):
            self.model_admin.changelist_view(request)
        self.assertTrue(request.session.get(self.session_key))

    def test_get_changelist_returns_custom_class(self) -> None:
        from apps.core.admin_mixins import ChangelistWithClearAllSkipDefault

        request = self._request()
        self.assertIs(
            self.model_admin.get_changelist(request),
            ChangelistWithClearAllSkipDefault,
        )
