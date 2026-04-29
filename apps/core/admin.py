from datetime import date
import json

from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, reverse
from django.utils import timezone

from apps.core.models import (
    SerieClassificacao,
    Classificacao,
    NivelHierarquico,
    ItemClassificacao,
    TRANSACTION_TIME_SENTINEL,
    VersaoClassificacao,
    VarianteClassificacao,
)
from apps.core.models_base_legal import BaseLegalTecnica
from apps.core.forms import (
    SerieClassificacaoForm,
    ClassificacaoForm,
    NivelHierarquicoForm,
    ItemClassificacaoForm,
)
from apps.core.admin_formatters import (
    format_receita_cod_by_vigencia,
    get_active_vigencia_masks,
)
from apps.core.code_mask import (
    resolve_receita_cod_mask_context,
)

from apps.core.admin_filters import (
    BaseLegalTecnicaIdFilter,
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
        'item_ref',
        'data_vigencia_inicio',
        'data_registro_inicio',
    ]
    list_filter = [
        RegistroAtivoFilter,
        ItemIdFilter,
        'matriz',
        'nivel_id',
        'base_legal_tecnica_id',
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
        },
        "nivel_id": {
            "kind": "nivel",
            "model": NivelHierarquico,
            "semantic_field": "nivel_id",
            "display_label": lambda obj: f"{obj.nivel_id} - {obj.nivel_nome}",
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
            "display_label": lambda obj: f"{obj.receita_cod} - {obj.receita_nome or obj.item_id or ''}".strip(
                " -"
            ),
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
                "lookup-classificacao-digit-limit/",
                self.admin_site.admin_view(self.lookup_classificacao_digit_limit_view),
                name=f"{self.model._meta.app_label}_{self.model._meta.model_name}_lookup_classificacao_digit_limit",
            ),
            path(
                "lookup-parent-by-code/",
                self.admin_site.admin_view(self.lookup_parent_by_code_view),
                name=f"{self.model._meta.app_label}_{self.model._meta.model_name}_lookup_parent_by_code",
            )
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
        context["item_classificacao_digit_limit_lookup_url"] = reverse(
            f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_lookup_classificacao_digit_limit"
        )
        return super().render_change_form(request, context, add, change, form_url, obj)

    def lookup_classificacao_digit_limit_view(self, request):
        classificacao_pk = (request.GET.get("classificacao_pk") or "").strip()
        input_length_raw = (request.GET.get("input_length") or "").strip()
        input_length = int(input_length_raw) if input_length_raw.isdigit() else None
        target = None

        if classificacao_pk:
            target = Classificacao.objects.filter(pk=classificacao_pk).only("pk", "numero_digitos").first()
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
        code = (request.GET.get("code") or "").replace(".", "").strip()
        vigencia_inicio = request.GET.get("vigencia_inicio")
        vigencia_fim = request.GET.get("vigencia_fim")
        if not code or not vigencia_inicio or not vigencia_fim:
            return JsonResponse({"pk": "", "semantic_value": "", "display_label": "", "link_url": ""})

        sentinel = TRANSACTION_TIME_SENTINEL
        if timezone.is_naive(sentinel):
            sentinel = timezone.make_aware(sentinel, timezone.get_current_timezone())

        qs = ItemClassificacao.objects.filter(
            receita_cod=code,
            data_registro_fim=sentinel,
            data_vigencia_inicio__lte=vigencia_inicio,
            data_vigencia_fim__gte=vigencia_fim,
        ).order_by("pk")
        obj = qs.first()
        if not obj:
            return JsonResponse({"pk": "", "semantic_value": "", "display_label": "", "link_url": ""})

        link_url = reverse(
            f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change",
            args=[obj.pk],
        )
        return JsonResponse(
            {
                "pk": str(obj.pk),
                "semantic_value": obj.receita_cod or "",
                "display_label": f"{obj.receita_cod} - {obj.receita_nome or obj.item_id or ''}".strip(" -"),
                "link_url": link_url,
            }
        )

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

    class Media:
        js = ("core/admin_bitemporal_date_shortcuts.js",)


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
