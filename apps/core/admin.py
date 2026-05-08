from datetime import date, datetime
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
from apps.core.parent_item_validation import digit_mask_for_classificacao_vigencia

from apps.core.admin_filters import (
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
            "semantic_value_resolver": lambda obj: format_receita_cod_by_vigencia(
                obj.receita_cod or "",
                getattr(obj, "data_vigencia_inicio", None),
                getattr(obj, "data_vigencia_fim", None),
                {},
            ),
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
        context["item_hierarchy_lookup_url"] = reverse(
            f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_lookup_hierarchy_by_code"
        )
        context["item_classificacao_digit_limit_lookup_url"] = reverse(
            f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_lookup_classificacao_digit_limit"
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
        return super().render_change_form(request, context, add, change, form_url, obj)

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
                "semantic_value": format_receita_cod_by_vigencia(
                    obj.receita_cod or "",
                    getattr(obj, "data_vigencia_inicio", None),
                    getattr(obj, "data_vigencia_fim", None),
                    {},
                ),
                "display_label": f"{obj.receita_cod} - {obj.receita_nome or obj.item_id or ''}".strip(" -"),
                "link_url": link_url,
            }
        )

    def lookup_hierarchy_by_code_view(self, request):
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

        def classificacao_identity_filters(class_obj, fallback_pk=None):
            identity = {}
            class_ref = getattr(class_obj, "classificacao_ref", None) if class_obj else None
            class_semantic = getattr(class_obj, "classificacao_id", None) if class_obj else None
            if class_ref not in (None, ""):
                identity["classificacao_id__classificacao_ref"] = class_ref
            elif class_semantic not in (None, ""):
                identity["classificacao_id__classificacao_id"] = class_semantic
            elif fallback_pk is not None:
                identity["classificacao_id"] = fallback_pk
            return identity

        def classificacao_payload_from_obj(class_obj):
            if not class_obj:
                return None
            try:
                link_url = reverse(
                    f"admin:{class_obj._meta.app_label}_{class_obj._meta.model_name}_change",
                    args=[class_obj.pk],
                )
            except Exception:
                link_url = ""
            return {
                "pk": str(class_obj.pk),
                "classificacao_id": getattr(class_obj, "classificacao_id", "") or "",
                "display_label": (
                    f"{getattr(class_obj, 'classificacao_id', '')} - "
                    f"{getattr(class_obj, 'classificacao_nome', '')}"
                ).strip(" -"),
                "link_url": link_url,
            }

        raw_code = (request.GET.get("code") or "").replace(".", "").strip()
        classificacao_pk = (request.GET.get("classificacao_pk") or "").strip()
        vigencia_inicio = parse_date(request.GET.get("vigencia_inicio"))
        vigencia_fim = parse_date(request.GET.get("vigencia_fim"))

        if not raw_code:
            return JsonResponse({"ok": False, "message": "Informe o código canônico."})
        if not vigencia_inicio or not vigencia_fim:
            return JsonResponse({"ok": False, "message": "Informe o período de vigência para derivar nível e item pai."})
        if vigencia_fim < vigencia_inicio:
            return JsonResponse({"ok": False, "message": "Período de vigência inválido: data fim anterior à data de início."})
        if not raw_code.isdigit():
            return JsonResponse({"ok": False, "message": "Código canônico inválido: utilize apenas dígitos."})

        class_pk = None
        class_identity_filters = None
        class_obj = None
        effective_vigencia_inicio = vigencia_inicio
        effective_vigencia_fim = vigencia_fim
        vigencia_overridden = False
        if classificacao_pk:
            try:
                class_pk = int(classificacao_pk)
            except ValueError:
                return JsonResponse({"ok": False, "message": "Classificação inválida."})
            class_obj = Classificacao.objects.filter(pk=class_pk).only(
                "pk",
                "classificacao_ref",
                "classificacao_id",
                "classificacao_nome",
                "data_vigencia_inicio",
                "data_vigencia_fim",
            ).first()
            if not class_obj:
                return JsonResponse({"ok": False, "message": "Classificação inválida."})
            class_identity_filters = classificacao_identity_filters(class_obj, fallback_pk=class_pk)
            class_vig_inicio = getattr(class_obj, "data_vigencia_inicio", None)
            class_vig_fim = getattr(class_obj, "data_vigencia_fim", None)
            if class_vig_inicio and class_vig_fim:
                if not (class_vig_inicio <= vigencia_inicio and class_vig_fim >= vigencia_fim):
                    effective_vigencia_inicio = class_vig_inicio
                    effective_vigencia_fim = class_vig_fim
                    vigencia_overridden = True

        mask = None
        if class_pk is not None:
            mask = digit_mask_for_classificacao_vigencia(
                class_pk, effective_vigencia_inicio, effective_vigencia_fim
            )
        if not mask:
            # Fallback default: estrutura vigente mais recente no contexto atual.
            ctx = resolve_receita_cod_mask_context(None, input_length=len(raw_code), on_date=date.today())
            mask = ctx.get("digit_mask") if ctx else None
        if not mask:
            return JsonResponse(
                {
                    "ok": False,
                    "message": (
                        "Não foi possível determinar a estrutura de níveis para o contexto informado."
                    ),
                }
            )

        total_digits = sum(mask)
        normalized_code = raw_code
        if len(normalized_code) < total_digits:
            normalized_code = normalized_code.ljust(total_digits, "0")
        elif len(normalized_code) > total_digits:
            extra_tail = normalized_code[total_digits:]
            if extra_tail and set(extra_tail) != {"0"}:
                return JsonResponse(
                    {
                        "ok": False,
                        "message": (
                            f"Código canônico com {len(normalized_code)} dígitos excede o limite "
                            f"de {total_digits} para a classificação e vigência informadas."
                        ),
                    }
                )
            normalized_code = normalized_code[:total_digits]

        segments = []
        pos = 0
        for width in mask:
            segments.append(normalized_code[pos : pos + width])
            pos += width

        def is_zero_segment(seg):
            return bool(seg) and set(seg) == {"0"}

        deepest_index = -1
        for idx, seg in enumerate(segments):
            if not is_zero_segment(seg):
                deepest_index = idx
        if deepest_index < 0:
            return JsonResponse(
                {
                    "ok": False,
                    "message": "Código canônico inválido: não há nível detalhado diferente de zero.",
                }
            )

        for idx in range(deepest_index + 1, len(segments)):
            if not is_zero_segment(segments[idx]):
                return JsonResponse(
                    {
                        "ok": False,
                        "message": (
                            "Código canônico inválido: há detalhamento após o nível derivado. "
                            "Ajuste os zeros canônicos."
                        ),
                    }
                )

        derived_level_number = deepest_index + 1
        level_base_filters = {
            "nivel_numero": derived_level_number,
            "data_vigencia_inicio__lte": effective_vigencia_fim,
            "data_vigencia_fim__gte": effective_vigencia_inicio,
        }
        level_selected_filters = dict(level_base_filters)
        if class_identity_filters:
            level_selected_filters.update(class_identity_filters)
        level_obj = (
            NivelHierarquico.objects.select_related("classificacao_id")
            .filter(**level_selected_filters)
            .order_by("-data_vigencia_inicio", "-data_registro_inicio", "-pk")
            .first()
        )
        alt_level_obj = None
        if not level_obj:
            alt_qs = (
                NivelHierarquico.objects.select_related("classificacao_id")
                .filter(**level_base_filters)
                .order_by("-data_vigencia_inicio", "-data_registro_inicio", "-pk")
            )
            if class_obj is not None:
                alt_qs = alt_qs.exclude(classificacao_id_id=class_obj.pk)
            alt_level_obj = alt_qs.first()

        derived_level_payload = {
            "number": derived_level_number,
            "pk": str(level_obj.pk) if level_obj else "",
            "display_label": (
                f"{level_obj.nivel_id} - {level_obj.nivel_nome}" if level_obj else ""
            ),
            "status": {"severity": "ok", "message": "", "alternative": None},
        }
        if not level_obj:
            if alt_level_obj:
                alt_class = getattr(alt_level_obj, "classificacao_id", None)
                alt_class_payload = classificacao_payload_from_obj(alt_class)
                alt_class_id = (
                    alt_class_payload.get("classificacao_id", "") if alt_class_payload else ""
                )
                derived_level_payload["status"] = {
                    "severity": "warning",
                    "message": (
                        f"Não existe nível hierárquico vigente para o nível {derived_level_number} "
                        "na classificação informada, porém existe para outra classificação compatível."
                    ),
                    "alternative": {
                        "classificacao": alt_class_payload,
                        "message": (
                            "Não existe nível hierárquico vigente para a classificação selecionada, "
                            f"porém existe para {alt_class_id}. "
                            "Certifique-se de que a classificação selecionada está correta."
                        ),
                    },
                }
            else:
                derived_level_payload["status"] = {
                    "severity": "error",
                    "message": (
                        f"Não existe nível hierárquico vigente para o nível {derived_level_number} "
                        "na classificação informada nem em classificações alternativas compatíveis."
                    ),
                    "alternative": None,
                }

        parent_payload = {
            "required": derived_level_number > 1,
            "found": False,
            "pk": "",
            "code": "",
            "display_label": "",
            "link_url": "",
            "status": {"severity": "ok", "message": "", "alternative": None},
        }

        if derived_level_number > 1:
            parent_segments = list(segments)
            for idx in range(deepest_index, len(parent_segments)):
                parent_segments[idx] = "0" * mask[idx]
            parent_code = "".join(parent_segments)
            parent_payload["code"] = parent_code

            parent_filters = {
                "receita_cod": parent_code,
                "matriz": True,
                "nivel_id__nivel_numero": derived_level_number - 1,
                "data_vigencia_inicio__lte": effective_vigencia_fim,
                "data_vigencia_fim__gte": effective_vigencia_inicio,
            }
            if class_identity_filters:
                parent_filters.update(class_identity_filters)
            elif level_obj and getattr(level_obj, "classificacao_id_id", None):
                parent_filters["classificacao_id"] = level_obj.classificacao_id_id

            parent_obj = (
                ItemClassificacao.objects.select_related("classificacao_id").filter(**parent_filters)
                .order_by("-data_vigencia_inicio", "-data_registro_inicio", "-pk")
                .first()
            )

            if parent_obj:
                parent_payload["found"] = True
                parent_payload["pk"] = str(parent_obj.pk)
                parent_payload["display_label"] = (
                    f"{parent_obj.receita_cod} - {parent_obj.receita_nome or parent_obj.item_id or ''}".strip(" -")
                )
                parent_payload["link_url"] = reverse(
                    f"admin:{parent_obj._meta.app_label}_{parent_obj._meta.model_name}_change",
                    args=[parent_obj.pk],
                )
            else:
                parent_alt_filters = {
                    "receita_cod": parent_code,
                    "matriz": True,
                    "nivel_id__nivel_numero": derived_level_number - 1,
                    "data_vigencia_inicio__lte": effective_vigencia_fim,
                    "data_vigencia_fim__gte": effective_vigencia_inicio,
                }
                parent_alt_qs = ItemClassificacao.objects.select_related("classificacao_id").filter(
                    **parent_alt_filters
                ).order_by("-data_vigencia_inicio", "-data_registro_inicio", "-pk")
                if class_obj is not None:
                    parent_alt_qs = parent_alt_qs.exclude(classificacao_id_id=class_obj.pk)
                parent_alt_obj = parent_alt_qs.first()
                if parent_alt_obj:
                    alt_class_payload = classificacao_payload_from_obj(
                        getattr(parent_alt_obj, "classificacao_id", None)
                    )
                    alt_class_id = (
                        alt_class_payload.get("classificacao_id", "") if alt_class_payload else ""
                    )
                    parent_payload["status"] = {
                        "severity": "warning",
                        "message": (
                            "Não existe item pai ativo e vigente para o código informado na "
                            "classificação selecionada, porém existe em outra classificação compatível."
                        ),
                        "alternative": {
                            "classificacao": alt_class_payload,
                            "item": {
                                "pk": str(parent_alt_obj.pk),
                                "display_label": (
                                    f"{parent_alt_obj.receita_cod} - "
                                    f"{parent_alt_obj.receita_nome or parent_alt_obj.item_id or ''}"
                                ).strip(" -"),
                                "link_url": reverse(
                                    f"admin:{parent_alt_obj._meta.app_label}_{parent_alt_obj._meta.model_name}_change",
                                    args=[parent_alt_obj.pk],
                                ),
                            },
                            "message": (
                                "Não existe item pai vigente para a classificação selecionada, "
                                f"porém existe para {alt_class_id}. "
                                "Certifique-se de que a classificação selecionada está correta."
                            ),
                        },
                    }
                else:
                    parent_payload["status"] = {
                        "severity": "error",
                        "message": (
                            "Não existe item pai ativo e vigente para o código informado na "
                            "classificação selecionada nem em classificações alternativas compatíveis."
                        ),
                        "alternative": None,
                    }

        return JsonResponse(
            {
                "ok": True,
                "normalized_code": normalized_code,
                "effective_vigencia": {
                    "inicio": effective_vigencia_inicio.isoformat() if effective_vigencia_inicio else "",
                    "fim": effective_vigencia_fim.isoformat() if effective_vigencia_fim else "",
                    "overridden": vigencia_overridden,
                },
                "derived_level": derived_level_payload,
                "parent": parent_payload,
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
