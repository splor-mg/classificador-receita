from datetime import date, datetime
import json
import logging

from django.contrib import admin, messages
from django.contrib.admin.utils import unquote
from django.db.models import Max
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils import timezone
from apps.core.models import (
    SerieClassificacao,
    Classificacao,
    NivelHierarquico,
    ItemClassificacao,
    VersaoClassificacao,
    VarianteClassificacao,
)
from apps.core.models_base_legal import BaseLegalTecnica
from apps.core.models_alias_lexico import AliasLexico, lista_abreviacoes_registro_inicio_novo
from apps.core.forms import (
    SerieClassificacaoForm,
    ClassificacaoForm,
    NivelHierarquicoForm,
    ItemClassificacaoForm,
    AliasLexicoAdminForm,
)
from apps.core.admin_formatters import (
    format_receita_cod_by_vigencia,
    get_active_vigencia_masks,
)
from apps.core.code_mask import resolve_receita_cod_mask_context
from apps.core.item_classificacao_code_lookup import (
    lookup_hierarchy_by_code_response_data,
    lookup_parent_by_code_response_data,
)
from apps.core.item_classificacao_suggest_child_code import (
    suggest_child_code_by_parent_response_data,
)
from apps.core.parent_item_validation import (
    validate_intermediate_canonical_zeros_json_dict,
    warn_parent_level_jump_json_dict,
)
from apps.core.classification_naming_abbrev import (
    calcular_radical_abreviado,
    radical_com_sufixo_canonico,
)
from apps.core.classification_naming_messages import (
    classification_naming_messages_dict,
    format_lexico_termo_duplicado,
)

from apps.core.admin_filters import (
    AliasLexicoRegistroAtivoFilter,
    BaseLegalTecnicaIdFilter,
    BaseLegalTecnicaSemanticFilter,
    CategoriaOrigemPrefixFilter,
    CategoriaPrefixFilter,
    NivelHierarquicoRecenteFilter,
    SerieIdFilter,
    SerieIdFKFilter,
    ClassificacaoIdFilter,
    ItemIdFilter,
    NivelIdFilter,
    NivelIdFKFilter,
    VarianteIdFilter,
    VersaoIdFilter,
)
from apps.core.admin_mixins import (
    RegistroAtivoFilter,
    CoreChangeSaveFormSubmitMixin,
    BitemporalInactiveReadOnlyMixin,
    BitemporalAdminMixin,
    BitemporalDateFormatMixin,
    AutoExportAdminMixin,
    SemanticForeignKeyAdminMixin,
    BitemporalObjectActionsMixin,
    BitemporalForeignKeyLookupActiveOnlyMixin,
    transaction_time_sentinel_for_query,
)


@admin.register(SerieClassificacao)
class SerieClassificacaoAdmin(
    BitemporalObjectActionsMixin,
    BitemporalAdminMixin,
    BitemporalInactiveReadOnlyMixin,
    BitemporalDateFormatMixin,
    CoreChangeSaveFormSubmitMixin,
    AutoExportAdminMixin,
    BitemporalForeignKeyLookupActiveOnlyMixin,
    admin.ModelAdmin,
):
    list_display = [
        'serie_id',
        'serie_nome',
        'orgao_responsavel_both',
        'data_vigencia_inicio_fmt',
        'data_vigencia_fim_fmt',
        'data_registro_inicio_fmt',
        'data_registro_fim_fmt',
    ]
    ordering = [
        'serie_ref',
        'data_vigencia_inicio',
        'data_registro_inicio',
    ]
    list_filter = [
        RegistroAtivoFilter,
        SerieIdFilter,
        'data_vigencia_inicio',
        'data_registro_inicio',
    ]
    search_fields = [
        'serie_id',
        'serie_nome',
        'serie_descricao',
    ]
    readonly_fields = [
        'serie_ref',
        'data_registro_inicio_fmt',
        'data_registro_fim_fmt',
    ]
    date_hierarchy = 'data_vigencia_inicio'
    fields = [
        ('serie_id', 'serie_ref'),
        'serie_nome',
        'serie_descricao',
        'orgao_responsavel',
        'data_vigencia_inicio',
        'data_vigencia_fim',
        'data_registro_inicio_fmt',
        'data_registro_fim_fmt',
    ]
    form = SerieClassificacaoForm

    class Media:
        js = ("core/admin_bitemporal_date_shortcuts.js",)

    def orgao_responsavel_both(self, obj):
        """
        Mostrar código armazenado (value) e rótulo (label) das choices.
        """
        try:
            label = obj.get_orgao_responsavel_display()
        except Exception:
            label = ''
        if label:
            return f"{obj.orgao_responsavel} — {label}"
        return obj.orgao_responsavel
    orgao_responsavel_both.short_description = 'Órgão Responsável'


@admin.register(Classificacao)
class ClassificacaoAdmin(
    SemanticForeignKeyAdminMixin,
    BitemporalObjectActionsMixin,
    BitemporalAdminMixin,
    BitemporalInactiveReadOnlyMixin,
    BitemporalDateFormatMixin,
    CoreChangeSaveFormSubmitMixin,
    AutoExportAdminMixin,
    BitemporalForeignKeyLookupActiveOnlyMixin,
    admin.ModelAdmin,
):
    model = Classificacao
    list_display = [
        "classificacao_id",
        "classificacao_nome",
        "serie_id_raw",
        "tipo_classificacao",
        "numero_niveis",
        "numero_digitos",
        "data_vigencia_inicio_fmt",
        "data_vigencia_fim_fmt",
        "data_registro_inicio_fmt",
        "data_registro_fim_fmt",
    ]
    ordering = [
        'classificacao_ref',
        'data_vigencia_inicio',
        'data_registro_inicio',
    ]
    list_filter = [
        RegistroAtivoFilter,
        ClassificacaoIdFilter,
        "tipo_classificacao",
        "numero_niveis",
        SerieIdFKFilter,
        "data_vigencia_inicio",
        "data_registro_inicio",
    ]
    search_fields = ["classificacao_id", "classificacao_nome", "classificacao_descricao"]
    readonly_fields = ["data_registro_inicio_fmt", "data_registro_fim_fmt"]
    date_hierarchy = "data_vigencia_inicio"
    raw_id_fields = ["serie_id", "base_legal_tecnica_id"]
    fields = [
        ("classificacao_id", "classificacao_ref"),
        "classificacao_nome",
        "serie_id",
        "classificacao_descricao",
        "tipo_classificacao",
        "numero_niveis",
        "numero_digitos",
        "base_legal_tecnica_id",
        "data_vigencia_inicio",
        "data_vigencia_fim",
        "data_registro_inicio_fmt",
        "data_registro_fim_fmt",
    ]
    form = ClassificacaoForm
    semantic_fk_config = {
        "serie_id": {
            "kind": "serie",
            "model": SerieClassificacao,
            "semantic_field": "serie_id",
            "display_label": lambda obj: f"{obj.serie_id} - {obj.serie_nome}",
            "popup_default_registro_ativo_ano_corrente": True,
        },
        "base_legal_tecnica_id": {
            "kind": "base_legal_tecnica",
            "model": BaseLegalTecnica,
            "semantic_field": "base_legal_tecnica_id",
            "display_label": lambda obj: str(obj),
        },
    }

    class Media:
        js = ("core/admin_bitemporal_date_shortcuts.js",)


@admin.register(NivelHierarquico)
class NivelHierarquicoAdmin(
    SemanticForeignKeyAdminMixin,
    BitemporalObjectActionsMixin,
    BitemporalAdminMixin,
    BitemporalInactiveReadOnlyMixin,
    BitemporalDateFormatMixin,
    CoreChangeSaveFormSubmitMixin,
    AutoExportAdminMixin,
    BitemporalForeignKeyLookupActiveOnlyMixin,
    admin.ModelAdmin,
):
    model = NivelHierarquico
    list_display = [
        'nivel_id',
        'nivel_nome',
        'classificacao_id_raw',
        'data_vigencia_inicio_fmt',
        'data_vigencia_fim_fmt',
        'data_registro_inicio_fmt',
        'data_registro_fim_fmt',
    ]
    ordering = [
        'nivel_numero',
        'data_vigencia_inicio',
        'data_registro_inicio',
    ]
    list_filter = [
        RegistroAtivoFilter,
        NivelIdFilter,
        'tipo_codigo',
        NivelIdFKFilter,
        'data_vigencia_inicio',
        'data_registro_inicio',
    ]
    search_fields = ['nivel_id', 'nivel_nome', 'nivel_descricao']
    readonly_fields = ['data_registro_inicio_fmt', 'data_registro_fim_fmt']
    date_hierarchy = 'data_vigencia_inicio'
    raw_id_fields = ['classificacao_id']
    fields = [
        ('nivel_id', 'nivel_ref'),
        'nivel_numero',
        'nivel_nome',
        'classificacao_id',
        'nivel_descricao',
        'estrutura_codigo',
        'numero_digitos',
        'tipo_codigo',
        'data_vigencia_inicio',
        'data_vigencia_fim',
        'data_registro_inicio_fmt',
        'data_registro_fim_fmt',
    ]
    form = NivelHierarquicoForm
    semantic_fk_config = {
        "classificacao_id": {
            "kind": "classificacao",
            "model": Classificacao,
            "semantic_field": "classificacao_id",
            "display_label": lambda obj: f"{obj.classificacao_id} - {obj.classificacao_nome}",
            "popup_default_registro_ativo_ano_corrente": True,
        },
    }

    class Media:
        js = ("core/admin_bitemporal_date_shortcuts.js",)


@admin.register(ItemClassificacao)
class ItemClassificacaoAdmin(
    SemanticForeignKeyAdminMixin,
    BitemporalObjectActionsMixin,
    BitemporalAdminMixin,
    BitemporalInactiveReadOnlyMixin,
    BitemporalDateFormatMixin,
    CoreChangeSaveFormSubmitMixin,
    AutoExportAdminMixin,
    BitemporalForeignKeyLookupActiveOnlyMixin,
    admin.ModelAdmin,
):
    model = ItemClassificacao
    list_display = [
        'receita_cod_formatado',
        'receita_nome',
        'matriz_display',
        'data_vigencia_inicio_fmt',
        'data_vigencia_fim_fmt',
        'data_registro_inicio_fmt',
        'data_registro_fim_fmt',
    ]
    ordering = [
        'item_id',
        'data_vigencia_inicio',
        'data_registro_inicio',
    ]
    list_filter = [
        RegistroAtivoFilter,
        NivelHierarquicoRecenteFilter,
        CategoriaPrefixFilter,
        CategoriaOrigemPrefixFilter,
        'matriz',
        ItemIdFilter,
        BaseLegalTecnicaSemanticFilter,
        'item_gerado',
        'data_vigencia_inicio',
        'data_registro_inicio',
    ]
    search_fields = ['receita_cod', 'receita_nome', 'item_id']
    readonly_fields = ['data_registro_inicio_fmt', 'data_registro_fim_fmt']
    date_hierarchy = 'data_vigencia_inicio'
    raw_id_fields = ['classificacao_id', 'nivel_id', 'parent_item_id', 'base_legal_tecnica_id']
    fields = [
        ('receita_cod', 'item_ref', 'item_id'),
        'receita_nome',
        'receita_descricao',
        'classificacao_id',
        'matriz',
        'nivel_id', 
        'base_legal_tecnica_id',
        'base_legal_tecnica_referencia',
        'destinacao_legal',
        'informacoes_gerenciais',
        'item_gerado',
        'parent_item_id',
        'data_vigencia_inicio',
        'data_vigencia_fim',
        'data_registro_inicio_fmt',
        'data_registro_fim_fmt',
    ]
    form = ItemClassificacaoForm
    
    semantic_fk_config = {
        "classificacao_id": {
            "kind": "classificacao",
            "model": Classificacao,
            "semantic_field": "classificacao_id",
            "display_label": lambda obj: f"{obj.classificacao_id} - {obj.classificacao_nome}",
            "popup_default_registro_ativo_ano_corrente": True,
        },
        "nivel_id": {
            "kind": "nivel",
            "model": NivelHierarquico,
            "semantic_field": "nivel_id",
            "display_label": lambda obj: f"{obj.nivel_id} - {obj.nivel_nome}",
            "popup_default_registro_ativo_ano_corrente": True,
        },
        "base_legal_tecnica_id": {
            "kind": "base_legal_tecnica",
            "model": BaseLegalTecnica,
            "semantic_field": "base_legal_tecnica_id",
            "display_label": lambda obj: str(obj),
        },
        "parent_item_id": {
            "kind": "item",
            "model": ItemClassificacao,
            "semantic_field": "receita_cod",
            "semantic_value_resolver": lambda obj: format_receita_cod_by_vigencia(
                obj.receita_cod or "",
                getattr(obj, "data_vigencia_inicio", None),
                getattr(obj, "data_vigencia_fim", None),
                {},
            ),
            "display_label": lambda obj: f"{obj.receita_cod} - {obj.receita_nome or obj.item_id or ''}".strip(
                " -"
            ),
            "popup_default_registro_ativo_ano_corrente": True,
        },
    }

    def get_fields(self, request, obj=None):
        # Aplica ordem específica apenas na tela de criação (add view).
        if obj is None:
            return [
                ('receita_cod', 'item_ref', 'item_id'),
                'classificacao_id',
                'parent_item_id',
                'nivel_id',
                'matriz',
                'receita_nome',
                'receita_descricao',
                'base_legal_tecnica_id',
                'base_legal_tecnica_referencia',
                'destinacao_legal',
                'informacoes_gerenciais',
                'item_gerado',
                'data_vigencia_inicio',
                'data_vigencia_fim',
            ]
        return super().get_fields(request, obj)

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "lookup-hierarchy-by-code/",
                self.admin_site.admin_view(self.lookup_hierarchy_by_code_view),
                name=f"{self.model._meta.app_label}_{self.model._meta.model_name}_lookup_hierarchy_by_code",
            ),
            path(
                "lookup-classificacao-digit-limit/",
                self.admin_site.admin_view(self.lookup_classificacao_digit_limit_view),
                name=f"{self.model._meta.app_label}_{self.model._meta.model_name}_lookup_classificacao_digit_limit",
            ),
            path(
                "lookup-parent-by-code/",
                self.admin_site.admin_view(self.lookup_parent_by_code_view),
                name=f"{self.model._meta.app_label}_{self.model._meta.model_name}_lookup_parent_by_code",
            ),
            path(
                "warn-parent-level-jump/",
                self.admin_site.admin_view(self.warn_parent_level_jump_view),
                name=f"{self.model._meta.app_label}_{self.model._meta.model_name}_warn_parent_level_jump",
            ),
            path(
                "validate-intermediate-canonical-zeros/",
                self.admin_site.admin_view(self.validate_intermediate_canonical_zeros_view),
                name=f"{self.model._meta.app_label}_{self.model._meta.model_name}_validate_intermediate_canonical_zeros",
            ),
            path(
                "lookup-abbreviated-radical/",
                self.admin_site.admin_view(self.lookup_abbreviated_radical_view),
                name=f"{self.model._meta.app_label}_{self.model._meta.model_name}_lookup_abbreviated_radical",
            ),
            path(
                "suggest-child-code-by-parent/",
                self.admin_site.admin_view(self.suggest_child_code_by_parent_view),
                name=f"{self.model._meta.app_label}_{self.model._meta.model_name}_suggest_child_code_by_parent",
            ),
        ]
        return custom + urls

    def get_queryset(self, request):
        self._nivel_digit_cache = {}
        qs = super().get_queryset(request)
        return qs.select_related("classificacao_id")

    def render_change_form(self, request, context, add=False, change=False, form_url="", obj=None):
        context["item_receita_cod_masks_json"] = json.dumps(get_active_vigencia_masks())
        context["item_parent_lookup_url"] = reverse(
            f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_lookup_parent_by_code"
        )
        context["item_hierarchy_lookup_url"] = reverse(
            f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_lookup_hierarchy_by_code"
        )
        context["item_classificacao_digit_limit_lookup_url"] = reverse(
            f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_lookup_classificacao_digit_limit"
        )
        context["item_parent_level_jump_warn_url"] = reverse(
            f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_warn_parent_level_jump"
        )
        context["item_validate_intermediate_zeros_url"] = reverse(
            f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_validate_intermediate_canonical_zeros"
        )
        if obj is not None:
            masked_codigo = format_receita_cod_by_vigencia(
                obj.receita_cod or "",
                getattr(obj, "data_vigencia_inicio", None),
                getattr(obj, "data_vigencia_fim", None),
                {},
            )
            nome = obj.receita_nome or obj.item_id or ""
            context["subtitle"] = f"{masked_codigo} - {nome}".strip(" -")
        else:
            context["classification_naming_messages"] = classification_naming_messages_dict()
            context["item_abbreviated_radical_lookup_url"] = reverse(
                f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_lookup_abbreviated_radical"
            )
            context["item_suggest_child_code_url"] = reverse(
                f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_suggest_child_code_by_parent"
            )
        return super().render_change_form(request, context, add, change, form_url, obj)

    def lookup_abbreviated_radical_view(self, request):
        nome_mae = (request.GET.get("nome_mae") or "").strip()
        parent_pk = (request.GET.get("parent_item_id") or "").strip()
        if parent_pk.isdigit() and not nome_mae:
            parent = ItemClassificacao.objects.filter(pk=int(parent_pk)).only("receita_nome").first()
            if parent:
                nome_mae = (parent.receita_nome or "").strip()
        if not nome_mae:
            return JsonResponse({"ok": False, "message": "nome_mae ou parent_item_id obrigatório."})
        result = calcular_radical_abreviado(nome_mae)
        radical = (result.radical or "").strip()
        return JsonResponse(
            {
                "ok": True,
                "radical": radical,
                "receita_nome_sugerido": radical_com_sufixo_canonico(radical),
                "lexico_alertas": [
                    format_lexico_termo_duplicado(t) for t in result.lexico_termo_duplicado
                ],
            }
        )

    def lookup_classificacao_digit_limit_view(self, request):
        classificacao_pk = (request.GET.get("classificacao_pk") or "").strip()
        input_length_raw = (request.GET.get("input_length") or "").strip()
        input_length = int(input_length_raw) if input_length_raw.isdigit() else None
        target = None

        if classificacao_pk:
            target = Classificacao.objects.filter(pk=classificacao_pk).only(
                "pk", "classificacao_ref", "classificacao_id"
            ).first()
        ctx = resolve_receita_cod_mask_context(target, input_length=input_length, on_date=date.today())

        return JsonResponse(
            {
                "numero_digitos": ctx["numero_digitos"],
                "digit_mask": ctx["digit_mask"],
                "estrutura_codigo": ctx["estrutura_codigo"],
                "source": ctx["source"],
                "warning": ctx["warning"],
                "match_count": ctx["match_count"],
            }
        )

    def lookup_parent_by_code_view(self, request):
        return JsonResponse(lookup_parent_by_code_response_data(request))

    def suggest_child_code_by_parent_view(self, request):
        return JsonResponse(suggest_child_code_by_parent_response_data(request))

    def warn_parent_level_jump_view(self, request):
        def parse_date(raw):
            value = (raw or "").strip()
            if not value:
                return None
            for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
                try:
                    return datetime.strptime(value, fmt).date()
                except ValueError:
                    continue
            return None

        parent_pk = (request.GET.get("parent_item_id") or "").strip()
        nivel_pk = (request.GET.get("nivel_id") or "").strip()
        class_pk_raw = (request.GET.get("classificacao_id") or "").strip()
        vig_inicio = parse_date(request.GET.get("vigencia_inicio"))
        vig_fim = parse_date(request.GET.get("vigencia_fim"))

        if not parent_pk or not nivel_pk or not class_pk_raw or not vig_inicio or not vig_fim:
            return JsonResponse({"ok": True, "level_jump": False})
        try:
            parent_id_int = int(parent_pk)
            nivel_id_int = int(nivel_pk)
            class_id_int = int(class_pk_raw)
        except ValueError:
            return JsonResponse({"ok": False, "level_jump": False})

        parent = (
            ItemClassificacao.objects.filter(pk=parent_id_int)
            .select_related("nivel_id", "classificacao_id")
            .first()
        )
        nivel = NivelHierarquico.objects.filter(pk=nivel_id_int).first()
        if not parent or not nivel:
            return JsonResponse({"ok": True, "level_jump": False})

        child_cod_raw = (request.GET.get("receita_cod") or "").replace(".", "").strip()
        reg_sent = transaction_time_sentinel_for_query()
        payload = warn_parent_level_jump_json_dict(
            request,
            parent_item=parent,
            child_nivel=nivel,
            vig_inicio=vig_inicio,
            vig_fim=vig_fim,
            classificacao_form_pk=class_id_int,
            child_receita_cod_digits=child_cod_raw,
            reg_sent=reg_sent,
        )
        return JsonResponse(payload)

    def validate_intermediate_canonical_zeros_view(self, request):
        def parse_date(raw):
            value = (raw or "").strip()
            if not value:
                return None
            for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
                try:
                    return datetime.strptime(value, fmt).date()
                except ValueError:
                    continue
            return None

        parent_pk = (request.GET.get("parent_item_id") or "").strip()
        nivel_pk = (request.GET.get("nivel_id") or "").strip()
        class_pk_raw = (request.GET.get("classificacao_id") or "").strip()
        vig_inicio = parse_date(request.GET.get("vigencia_inicio"))
        vig_fim = parse_date(request.GET.get("vigencia_fim"))
        receita_cod = (request.GET.get("receita_cod") or "").replace(".", "").strip()

        if (
            not parent_pk
            or not nivel_pk
            or not class_pk_raw
            or not vig_inicio
            or not vig_fim
            or not receita_cod
        ):
            return JsonResponse({"ok": True})
        try:
            parent_id_int = int(parent_pk)
            nivel_id_int = int(nivel_pk)
            class_id_int = int(class_pk_raw)
        except ValueError:
            return JsonResponse({"ok": True})

        parent = (
            ItemClassificacao.objects.filter(pk=parent_id_int)
            .select_related("nivel_id", "classificacao_id")
            .first()
        )
        nivel = NivelHierarquico.objects.filter(pk=nivel_id_int).first()
        if not parent or not nivel:
            return JsonResponse({"ok": True})

        payload = validate_intermediate_canonical_zeros_json_dict(
            parent_item=parent,
            child_nivel=nivel,
            receita_cod_digits=receita_cod,
            vig_inicio=vig_inicio,
            vig_fim=vig_fim,
            classificacao_pk=class_id_int,
        )
        return JsonResponse(payload)

    def lookup_hierarchy_by_code_view(self, request):
        return JsonResponse(lookup_hierarchy_by_code_response_data(request))

    @admin.display(
        description=ItemClassificacao._meta.get_field("receita_cod").verbose_name,
        ordering="receita_cod",
    )
    def receita_cod_formatado(self, obj):
        return format_receita_cod_by_vigencia(
            obj.receita_cod or "",
            getattr(obj, "data_vigencia_inicio", None),
            getattr(obj, "data_vigencia_fim", None),
            getattr(self, "_nivel_digit_cache", {}),
        )

    @admin.display(
        description=ItemClassificacao._meta.get_field("matriz").verbose_name,
        ordering="matriz",
    )
    def matriz_display(self, obj):
        return "Matriz" if obj.matriz else "Detalhe"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        try:
            if change and hasattr(form, "has_changed") and not form.has_changed():
                return
        except Exception:
            pass
        log = logging.getLogger(__name__)
        try:
            from apps.core.alias_lexico_run import (
                maybe_export_seed_after_item_save_protocol,
                run_alias_lexico_infer_persist,
            )

            res = run_alias_lexico_infer_persist(
                t_instant=timezone.now(),
                items_csv_fallback=False,
                alias_seed_fallback=True,
            )
            try:
                out = maybe_export_seed_after_item_save_protocol(res.n_inserted)
                if out is not None:
                    self.message_user(
                        request,
                        f"Lista de abreviações: {res.n_inserted} novo(s) registo(s). Seed exportado.",
                        level=messages.SUCCESS,
                    )
            except Exception:
                log.exception("Export seed lista_abreviacoes após inferência (ItemClassificacao)")
                self.message_user(
                    request,
                    "Novas abreviações gravadas, mas o export do seed falhou (ver logs).",
                    level=messages.WARNING,
                )
        except Exception:
            log.exception("Inferência lista_abreviacoes após save de ItemClassificacao")
            self.message_user(
                request,
                "Aviso: falhou a atualização automática da lista de abreviações (ver logs).",
                level=messages.WARNING,
            )

    class Media:
        js = (
            "core/admin_bitemporal_date_shortcuts.js",
            "core/js/classification_naming.js",
        )


@admin.register(VersaoClassificacao)
class VersaoClassificacaoAdmin(
    CoreChangeSaveFormSubmitMixin,
    BitemporalInactiveReadOnlyMixin,
    AutoExportAdminMixin,
    BitemporalForeignKeyLookupActiveOnlyMixin,
    admin.ModelAdmin,
):
    list_display = ['versao_id', 'versao_numero', 'versao_nome', 'classificacao', 'data_lancamento', 'data_vigencia_inicio']
    list_filter = [RegistroAtivoFilter, VersaoIdFilter, 'classificacao', 'data_lancamento', 'data_vigencia_inicio']
    search_fields = ['versao_id', 'versao_numero', 'versao_nome', 'versao_descricao']
    readonly_fields = ['data_registro_inicio', 'data_registro_fim']
    date_hierarchy = 'data_vigencia_inicio'
    raw_id_fields = ['classificacao']


@admin.register(VarianteClassificacao)
class VarianteClassificacaoAdmin(
    CoreChangeSaveFormSubmitMixin,
    BitemporalInactiveReadOnlyMixin,
    AutoExportAdminMixin,
    BitemporalForeignKeyLookupActiveOnlyMixin,
    admin.ModelAdmin,
):
    list_display = ['variante_id', 'variante_nome', 'tipo_variante', 'classificacao', 'versao', 'data_vigencia_inicio']
    list_filter = [RegistroAtivoFilter, VarianteIdFilter, 'tipo_variante', 'classificacao', 'versao', 'data_vigencia_inicio']
    search_fields = ['variante_id', 'variante_nome', 'variante_descricao', 'proposito']
    readonly_fields = ['data_registro_inicio', 'data_registro_fim']
    date_hierarchy = 'data_vigencia_inicio'
    raw_id_fields = ['classificacao', 'versao']


@admin.register(BaseLegalTecnica)
class BaseLegalTecnicaAdmin(CoreChangeSaveFormSubmitMixin, AutoExportAdminMixin, admin.ModelAdmin):
    list_display = ['base_legal_tecnica_id', 'titulo_norma', 'tipo_legal', 'esfera_federativa', 'data_edicao']
    list_filter = [BaseLegalTecnicaIdFilter, 'tipo_legal', 'esfera_federativa', 'data_edicao']
    search_fields = ['base_legal_tecnica_id', 'titulo_norma', 'ementa']
    date_hierarchy = 'data_edicao'


def _alias_lexico_registro_ativo(obj: AliasLexico) -> bool:
    if obj is None or getattr(obj, "pk", None) is None:
        return True
    fim = obj.data_registro_fim
    sent = transaction_time_sentinel_for_query()
    if fim is None:
        return False
    if timezone.is_naive(fim):
        fim = timezone.make_aware(fim, timezone.get_current_timezone())
    return fim == sent


_ALIAS_LEXICO_SENTINEL_DISPLAY = "9999-12-31 00:00:00"


def _alias_lexico_format_registro_dt(dt) -> str:
    """Exibição no admin: YYYY-MM-DD HH:mm:ss no fuso local."""
    if dt is None:
        return "—"
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone.get_current_timezone())
    return timezone.localtime(dt).strftime("%Y-%m-%d %H:%M:%S")


@admin.register(AliasLexico)
class AliasLexicoAdmin(
    CoreChangeSaveFormSubmitMixin,
    BitemporalDateFormatMixin,
    AutoExportAdminMixin,
    admin.ModelAdmin,
):
    form = AliasLexicoAdminForm
    fieldsets = (
        (
            None,
            {
                "fields": (
                    ("termo", "alias_lexico_ref"),
                    "abreviacao",
                    "data_registro_inicio_fmt",
                    "data_registro_fim_fmt",
                )
            },
        ),
    )
    readonly_fields = ("data_registro_inicio_fmt", "data_registro_fim_fmt")
    list_display = ("termo", "abreviacao", "status_registro")
    list_filter = (AliasLexicoRegistroAtivoFilter,)
    search_fields = ("termo", "abreviacao")

    @admin.display(description="Status")
    def status_registro(self, obj):
        return "Ativo" if _alias_lexico_registro_ativo(obj) else "Desativado"

    def data_registro_inicio_fmt(self, obj):
        if obj is None or not getattr(obj, "pk", None):
            return _alias_lexico_format_registro_dt(lista_abreviacoes_registro_inicio_novo())
        return super().data_registro_inicio_fmt(obj)

    data_registro_inicio_fmt.short_description = "Data do Início do Registro"
    data_registro_inicio_fmt.admin_order_field = "data_registro_inicio"

    def data_registro_fim_fmt(self, obj):
        if obj is None or not getattr(obj, "pk", None):
            return _ALIAS_LEXICO_SENTINEL_DISPLAY
        if _alias_lexico_registro_ativo(obj):
            return _ALIAS_LEXICO_SENTINEL_DISPLAY
        return super().data_registro_fim_fmt(obj)

    data_registro_fim_fmt.short_description = "Data do Fim do Registro"
    data_registro_fim_fmt.admin_order_field = "data_registro_fim"

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        mx = AliasLexico.objects.aggregate(m=Max("alias_lexico_ref"))["m"] or 0
        initial.setdefault("alias_lexico_ref", mx + 1)
        return initial

    def get_urls(self):
        info = self.model._meta.app_label, self.model._meta.model_name
        return [
            path(
                "<path:object_id>/desativar/",
                self.admin_site.admin_view(self.desativar_view),
                name="%s_%s_desativar" % info,
            ),
            path(
                "<path:object_id>/reativar/",
                self.admin_site.admin_view(self.reativar_view),
                name="%s_%s_reativar" % info,
            ),
        ] + super().get_urls()

    def render_change_form(self, request, context, add=False, change=False, form_url="", obj=None):
        if change and obj is not None:
            context["alias_lexico_is_active"] = _alias_lexico_registro_ativo(obj)
            context["alias_lexico_deactivate_url"] = reverse(
                "admin:core_aliaslexico_desativar",
                args=[obj.pk],
            )
            context["alias_lexico_reactivate_url"] = reverse(
                "admin:core_aliaslexico_reativar",
                args=[obj.pk],
            )
            context["alias_lexico_delete_url"] = reverse(
                "admin:core_aliaslexico_delete",
                args=[obj.pk],
            )
        return super().render_change_form(request, context, add, change, form_url, obj)

    def desativar_view(self, request, object_id):
        obj = get_object_or_404(self.model, pk=unquote(object_id))
        if not self.has_change_permission(request, obj):
            return redirect("admin:index")

        change_url = reverse(
            "admin:core_aliaslexico_change",
            args=[obj.pk],
        )

        if not _alias_lexico_registro_ativo(obj):
            self.message_user(request, "Este registro já está desativado.", level=messages.WARNING)
            return redirect(change_url)

        if request.method == "POST":
            obj.data_registro_fim = timezone.now()
            obj.save(update_fields=["data_registro_fim"])
            self.trigger_export(request, self.model)
            self.message_user(request, "Registro desativado (data de fim = agora).", level=messages.SUCCESS)
            return redirect(change_url)

        context = {
            **self.admin_site.each_context(request),
            "title": "Desativar abreviação léxica",
            "subtitle": (
                "A data de fim do registro passará a ser o instante atual. "
                "O termo e a abreviação permanecem no histórico."
            ),
            "object": obj,
            "cancel_url": change_url,
            "opts": self.opts,
        }
        return TemplateResponse(
            request,
            "admin/core/alias_lexico_confirm.html",
            context,
        )

    def reativar_view(self, request, object_id):
        obj = get_object_or_404(self.model, pk=unquote(object_id))
        if not self.has_change_permission(request, obj):
            return redirect("admin:index")

        change_url = reverse(
            "admin:core_aliaslexico_change",
            args=[obj.pk],
        )

        if _alias_lexico_registro_ativo(obj):
            self.message_user(request, "Este registro já está ativo.", level=messages.WARNING)
            return redirect(change_url)

        if request.method == "POST":
            obj.data_registro_fim = transaction_time_sentinel_for_query()
            obj.save(update_fields=["data_registro_fim"])
            self.trigger_export(request, self.model)
            self.message_user(request, "Registro reativado (data de fim = sentinela).", level=messages.SUCCESS)
            return redirect(change_url)

        context = {
            **self.admin_site.each_context(request),
            "title": "Reativar abreviação léxica",
            "subtitle": (
                "A data de fim do registro voltará ao valor sentinela (registro ativo)."
            ),
            "object": obj,
            "cancel_url": change_url,
            "opts": self.opts,
        }
        return TemplateResponse(
            request,
            "admin/core/alias_lexico_confirm.html",
            context,
        )

    def save_model(self, request, obj, form, change):
        if change:
            prev = (
                self.model.objects.filter(pk=obj.pk)
                .only(
                    "data_registro_inicio",
                    "data_registro_fim",
                    "alias_lexico_ref",
                )
                .first()
            )
            if prev:
                obj.data_registro_inicio = prev.data_registro_inicio
                obj.alias_lexico_ref = prev.alias_lexico_ref
                obj.data_registro_fim = prev.data_registro_fim
        else:
            obj.data_registro_inicio = lista_abreviacoes_registro_inicio_novo()
            obj.data_registro_fim = transaction_time_sentinel_for_query()
            mx = self.model.objects.aggregate(m=Max("alias_lexico_ref"))["m"] or 0
            obj.alias_lexico_ref = mx + 1

        super().save_model(request, obj, form, change)
