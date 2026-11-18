"""Testes do pré-filtro padrão na changelist (``ChangelistDefaultFilterRedirectMixin``)."""

from unittest.mock import MagicMock, patch

from django.contrib.admin.sites import AdminSite
from django.contrib.admin.views.main import ChangeList
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.test import RequestFactory, SimpleTestCase

from apps.core.admin import ItemClassificacaoAdmin
from apps.core.admin_mixins import (
    CHANGELIST_SKIP_DEFAULT_PARAM,
    CHANGELIST_SKIP_DEFAULT_VALUE,
    REGISTRO_ATIVO_QUERY_PARAM,
    REGISTRO_ATIVO_VALUE_ANO_CORRENTE,
    ChangelistWithClearAllSkipDefault,
    clear_stale_changelist_skip_default_flags,
    parse_admin_changelist_model_key,
)
from apps.core.models import ItemClassificacao
from apps.core.validity_search import querystring_without_vigencia


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

    def test_parse_admin_changelist_model_key(self) -> None:
        self.assertEqual(
            parse_admin_changelist_model_key("/admin/core/itemclassificacao/"),
            "core.itemclassificacao",
        )
        self.assertIsNone(
            parse_admin_changelist_model_key("/admin/core/itemclassificacao/5/change/")
        )
        self.assertIsNone(parse_admin_changelist_model_key("/admin/"))

    def test_clear_stale_flags_keeps_active_changelist(self) -> None:
        request = self._request()
        request.session[self.session_key] = True
        request.session["admin_changelist_skip_default:core.serieclassificacao"] = True
        clear_stale_changelist_skip_default_flags(
            request, active_model_key="core.itemclassificacao"
        )
        self.assertTrue(request.session.get(self.session_key))
        self.assertNotIn(
            "admin_changelist_skip_default:core.serieclassificacao", request.session
        )

    def test_clear_stale_flags_on_non_changelist_path(self) -> None:
        request = self._request()
        request.session[self.session_key] = True
        clear_stale_changelist_skip_default_flags(request, active_model_key=None)
        self.assertNotIn(self.session_key, request.session)

    def test_reentry_after_leave_changelist_redirects_to_default(self) -> None:
        request = self._request()
        request.session[self.session_key] = True
        clear_stale_changelist_skip_default_flags(request, active_model_key=None)
        response = self.model_admin.changelist_view(request)
        self.assertEqual(response.status_code, 302)
        self.assertIn(
            f"{REGISTRO_ATIVO_QUERY_PARAM}={REGISTRO_ATIVO_VALUE_ANO_CORRENTE}",
            response["Location"],
        )


class VigenciaChangelistParamTests(SimpleTestCase):
    """A pesquisa de Vigência não pode ser lida como lookup de campo."""

    def setUp(self) -> None:
        self.factory = RequestFactory()

    def test_year_search_is_not_an_invalid_lookup(self) -> None:
        request = self.factory.get(
            "/admin/core/classificacao/"
            "?registro_ativo=ativo_historico&vigencia=1&vigencia_ano=2007"
            "&vigencia_mes=&vigencia_dia=&vigencia_versao=&vigencia_registro="
        )
        changelist = ChangelistWithClearAllSkipDefault.__new__(
            ChangelistWithClearAllSkipDefault
        )
        changelist.filter_params = dict(request.GET.lists())
        params = changelist.get_filters_params()
        self.assertEqual(params["registro_ativo"], ["ativo_historico"])
        for key in (
            "vigencia",
            "vigencia_ano",
            "vigencia_mes",
            "vigencia_dia",
            "vigencia_versao",
            "vigencia_registro",
        ):
            self.assertNotIn(key, params)

    def test_clear_all_drops_the_vigencia_search(self) -> None:
        request = self.factory.get("/admin/core/classificacao/")
        changelist = ChangelistWithClearAllSkipDefault.__new__(
            ChangelistWithClearAllSkipDefault
        )
        changelist.clear_all_filters_qs = (
            "?registro_ativo=ativo_historico&vigencia=1&vigencia_ano=2007"
        )

        def keep_clear_link(self, request, exclude_parameters=None):
            return MagicMock()

        with patch.object(ChangeList, "get_queryset", keep_clear_link):
            changelist.get_queryset(request)
        self.assertNotIn("vigencia", changelist.clear_all_filters_qs)
        self.assertIn("registro_ativo=ativo_historico", changelist.clear_all_filters_qs)
        self.assertIn(
            f"{CHANGELIST_SKIP_DEFAULT_PARAM}={CHANGELIST_SKIP_DEFAULT_VALUE}",
            changelist.clear_all_filters_qs,
        )

    def test_querystring_keeps_date_hierarchy_year(self) -> None:
        cleaned = querystring_without_vigencia(
            "?data_vigencia_inicio__year=2002&vigencia=1&vigencia_ano=2007"
        )
        self.assertEqual(cleaned, "?data_vigencia_inicio__year=2002")

    def test_selected_year_survives_the_search_query(self) -> None:
        request = self.factory.get("/admin/core/classificacao/?vigencia=1&vigencia_ano=2007")
        html = render_to_string(
            "admin/core/validity_date_side.html",
            {
                "prefix": "vigencia_",
                "vigencia_years": [2006, 2007, 2008],
                "vigencia_months": [1],
                "vigencia_days": [1],
                "request": request,
            },
        )
        self.assertRegex(html, r'value="2007"\s+selected')
        self.assertNotRegex(html, r'value="2006"\s+selected')
        self.assertNotRegex(html, r'value="2008"\s+selected')
