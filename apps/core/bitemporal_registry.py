"""
Registro de metadados dos recursos bitemporais (ADR-001, ADR-004).

RESOURCES contém apenas recursos bitemporais (SCD-2, append-only), aos quais se
aplicam as Regras 1 a 7 da ADR-004. O recurso base_legal_tecnica é modelo temporal
simples (SCD-1, alteração in-place) e não entra neste registry; as Regras 1 a 7
não se aplicam a ele (ADR-004 Regra 8).

Cada recurso define: model, chave de entidade, campos (cadastro/edição/export),
resolução de FKs, colunas de export e list_display. Usado pelos comandos genéricos
cadastrar_bitemporal, editar_bitemporal e exportar_bitemporal.

Para incluir um novo recurso bitemporal: adicione um entry em RESOURCES com
model_name, entity_key (lista de {arg, lookup}), fields (name, type, required,
default; type fk aceita fk_resource, fk_semantic_attr, fk_current), export_columns,
list_display, select_related e order_by. FK para base_legal_tecnica é tratada em
resolve_fk() (modelo SCD-1).
"""
from datetime import date
from typing import Any, Dict, List, Optional

# Import apenas quando necessário para evitar circular import no boot do Django
def _get_models():
    from apps.core.models import (
        SerieClassificacao,
        Classificacao,
        NivelHierarquico,
        VersaoClassificacao,
        VarianteClassificacao,
        ItemClassificacao,
        VALID_TIME_SENTINEL,
        TRANSACTION_TIME_SENTINEL,
    )
    return {
        "SerieClassificacao": SerieClassificacao,
        "Classificacao": Classificacao,
        "NivelHierarquico": NivelHierarquico,
        "VersaoClassificacao": VersaoClassificacao,
        "VarianteClassificacao": VarianteClassificacao,
        "ItemClassificacao": ItemClassificacao,
    }, VALID_TIME_SENTINEL, TRANSACTION_TIME_SENTINEL


# Nomes dos recursos (slug) -> configuração. model_name evita import no load do módulo.
RESOURCES: Dict[str, Dict[str, Any]] = {
    "serie_classificacao": {
        "model_name": "SerieClassificacao",
        "entity_key": [
            {"arg": "serie_id", "lookup": "serie_id"},
        ],
        "fields": [
            {"name": "serie_id", "type": "string", "required": True},
            {"name": "serie_ref", "type": "integer", "required": True},
            {"name": "serie_nome", "type": "string", "required": True},
            {"name": "descricao", "type": "string", "required": False, "default": ""},
            {"name": "orgao_responsavel", "type": "string", "required": False, "default": ""},
        ],
        "export_columns": [
            "serie_id", "serie_ref", "serie_nome", "descricao", "orgao_responsavel",
            "data_vigencia_inicio", "data_vigencia_fim", "data_registro_inicio", "data_registro_fim",
        ],
        "list_display": ["serie_id", "serie_nome", "data_vigencia_inicio", "data_vigencia_fim"],
        "select_related": [],
        "order_by": ["serie_id", "data_registro_inicio"],
    },
    "classificacao": {
        "model_name": "Classificacao",
        "entity_key": [
            {"arg": "classificacao_id", "lookup": "classificacao_id"},
        ],
        "fields": [
            {"name": "classificacao_id", "type": "string", "required": True},
            {"name": "classificacao_ref", "type": "integer", "required": True},
            {"name": "serie_id", "type": "fk", "required": True, "fk_resource": "serie_classificacao", "fk_semantic_attr": "serie_id", "fk_current": True},
            {"name": "classificacao_nome", "type": "string", "required": True},
            {"name": "descricao", "type": "string", "required": False, "default": ""},
            {"name": "tipo_classificacao", "type": "string", "required": True, "default": "hierárquica", "choices_attr": "TIPO_CHOICES"},
            {"name": "numero_niveis", "type": "integer", "required": True},
            {"name": "numero_digitos", "type": "integer", "required": False, "default": None},
            {"name": "base_legal_tecnica_id", "type": "fk", "required": False, "fk_resource": "base_legal_tecnica", "fk_semantic_attr": "base_legal_tecnica_id", "fk_current": False},
        ],
        "export_columns": [
            "classificacao_id", "classificacao_ref", "serie_id", "classificacao_nome", "descricao",
            "tipo_classificacao", "numero_niveis", "numero_digitos", "base_legal_tecnica_id",
            "data_vigencia_inicio", "data_vigencia_fim", "data_registro_inicio", "data_registro_fim",
        ],
        "list_display": ["classificacao_id", "classificacao_nome", "data_vigencia_inicio", "data_vigencia_fim"],
        "select_related": ["serie_id", "base_legal_tecnica_id"],
        "order_by": ["classificacao_id", "data_registro_inicio"],
    },
    "nivel_hierarquico": {
        "model_name": "NivelHierarquico",
        "entity_key": [
            {"arg": "nivel_id", "lookup": "nivel_id"},
            {"arg": "classificacao_id", "lookup": "classificacao_id__classificacao_id"},
        ],
        "fields": [
            {"name": "nivel_id", "type": "string", "required": True},
            {"name": "nivel_ref", "type": "integer", "required": True},
            {"name": "classificacao_id", "type": "fk", "required": True, "fk_resource": "classificacao", "fk_semantic_attr": "classificacao_id", "fk_current": True},
            {"name": "nivel_numero", "type": "integer", "required": True},
            {"name": "nivel_nome", "type": "string", "required": True},
            {"name": "descricao", "type": "string", "required": False, "default": ""},
            {"name": "estrutura_codigo", "type": "string", "required": False, "default": ""},
            {"name": "numero_digitos", "type": "integer", "required": True},
            {"name": "tipo_codigo", "type": "string", "required": True, "default": "numérico", "choices_attr": "TIPO_CODIGO_CHOICES"},
        ],
        "export_columns": [
            "nivel_id", "nivel_ref", "classificacao_id", "nivel_numero", "nivel_nome",
            "descricao", "estrutura_codigo", "numero_digitos", "tipo_codigo",
            "data_vigencia_inicio", "data_vigencia_fim", "data_registro_inicio", "data_registro_fim",
        ],
        "list_display": ["nivel_id", "classificacao_id", "data_registro_inicio", "data_vigencia_inicio", "data_vigencia_fim", "nivel_nome"],
        "select_related": ["classificacao_id"],
        "order_by": ["nivel_id", "classificacao_id__classificacao_id", "data_registro_inicio"],
    },
    "versao_classificacao": {
        "model_name": "VersaoClassificacao",
        "entity_key": [{"arg": "versao_id", "lookup": "versao_id"}],
        "fields": [
            {"name": "versao_id", "type": "string", "required": True},
            {"name": "versao_ref", "type": "integer", "required": False, "default": None},
            {"name": "classificacao", "type": "fk", "required": True, "fk_resource": "classificacao", "fk_semantic_attr": "classificacao_id", "fk_current": True},
            {"name": "versao_numero", "type": "string", "required": True},
            {"name": "versao_nome", "type": "string", "required": False, "default": ""},
            {"name": "descricao", "type": "string", "required": False, "default": ""},
            {"name": "data_lancamento", "type": "date", "required": False, "default": None},
        ],
        "export_columns": [
            "versao_id", "versao_ref", "classificacao", "versao_numero", "versao_nome", "descricao", "data_lancamento",
            "data_vigencia_inicio", "data_vigencia_fim", "data_registro_inicio", "data_registro_fim",
        ],
        "list_display": ["versao_id", "versao_numero", "data_vigencia_inicio", "data_vigencia_fim"],
        "select_related": ["classificacao"],
        "order_by": ["versao_id", "data_registro_inicio"],
    },
    "variante_classificacao": {
        "model_name": "VarianteClassificacao",
        "entity_key": [{"arg": "variante_id", "lookup": "variante_id"}],
        "fields": [
            {"name": "variante_id", "type": "string", "required": True},
            {"name": "classificacao", "type": "fk", "required": True, "fk_resource": "classificacao", "fk_semantic_attr": "classificacao_id", "fk_current": True},
            {"name": "versao", "type": "fk", "required": False, "fk_resource": "versao_classificacao", "fk_semantic_attr": "versao_id", "fk_current": True},
            {"name": "variante_nome", "type": "string", "required": True},
            {"name": "tipo_variante", "type": "string", "required": True, "choices_attr": "TIPO_CHOICES"},
            {"name": "descricao", "type": "string", "required": False, "default": ""},
            {"name": "proposito", "type": "string", "required": False, "default": ""},
        ],
        "export_columns": [
            "variante_id", "classificacao", "versao", "variante_nome", "tipo_variante", "descricao", "proposito",
            "data_vigencia_inicio", "data_vigencia_fim", "data_registro_inicio", "data_registro_fim",
        ],
        "list_display": ["variante_id", "variante_nome", "data_vigencia_inicio", "data_vigencia_fim"],
        "select_related": ["classificacao", "versao"],
        "order_by": ["variante_id", "data_registro_inicio"],
    },
    "item_classificacao": {
        "model_name": "ItemClassificacao",
        "entity_key": [
            {"arg": "item_id", "lookup": "item_id"},
            {"arg": "classificacao_id", "lookup": "classificacao_id__classificacao_id"},
        ],
        "fields": [
            {"name": "item_id", "type": "string", "required": True},
            {"name": "item_ref", "type": "integer", "required": False, "default": None},
            {"name": "classificacao_id", "type": "fk", "required": False, "fk_resource": "classificacao", "fk_semantic_attr": "classificacao_id", "fk_current": True},
            {"name": "receita_cod", "type": "string", "required": False, "default": None},
            {"name": "matriz", "type": "boolean", "required": False, "default": False},
            {"name": "receita_nome", "type": "string", "required": False, "default": ""},
            {"name": "receita_descricao", "type": "string", "required": False, "default": ""},
            {"name": "nivel_id", "type": "fk", "required": True, "fk_resource": "nivel_hierarquico", "fk_semantic_attr": "nivel_id", "fk_current": True},
            {"name": "parent_item_id", "type": "fk", "required": False, "fk_resource": "item_classificacao", "fk_semantic_attr": "item_id", "fk_current": True},
            {"name": "item_gerado", "type": "boolean", "required": False, "default": False},
        ],
        "export_columns": [
            "item_id", "item_ref", "classificacao_id", "receita_cod", "matriz", "receita_nome", "receita_descricao",
            "nivel_id", "parent_item_id", "item_gerado",
            "data_vigencia_inicio", "data_vigencia_fim", "data_registro_inicio", "data_registro_fim",
        ],
        "list_display": ["item_id", "receita_cod", "data_registro_inicio", "data_vigencia_inicio", "data_vigencia_fim"],
        "select_related": ["classificacao_id", "nivel_id", "parent_item_id"],
        "order_by": ["item_id", "classificacao_id__classificacao_id", "data_registro_inicio"],
    },
}


def get_resource(name: str) -> Dict[str, Any]:
    if name not in RESOURCES:
        raise KeyError(
            f"Recurso '{name}' não encontrado. Recursos: {', '.join(sorted(RESOURCES))}"
        )
    return RESOURCES[name].copy()


def get_model_for_resource(name: str):
    """Retorna a classe do model Django para o recurso."""
    res = get_resource(name)
    models_map, _, _ = _get_models()
    model_name = res["model_name"]
    if model_name not in models_map:
        raise KeyError(f"Model '{model_name}' não encontrado em core.models")
    return models_map[model_name]


def get_sentinela_date() -> date:
    _, _, sentinel = _get_models()
    return date.fromisoformat(sentinel)


def resolve_fk(resource_name: str, field_meta: Dict[str, Any], value: Any):
    """Resolve valor semântico para instância do model referenciado (FK)."""
    if value is None or value == "":
        return None
    fk_resource = field_meta.get("fk_resource")
    fk_semantic_attr = field_meta.get("fk_semantic_attr")
    fk_current = field_meta.get("fk_current", False)
    if not fk_resource or not fk_semantic_attr:
        return None
    # base_legal_tecnica não é bitemporal no registry; tem model em models_base_legal
    if fk_resource == "base_legal_tecnica":
        from core.models_base_legal import BaseLegalTecnica
        qs = BaseLegalTecnica.objects.filter(**{fk_semantic_attr: value})
    else:
        model = get_model_for_resource(fk_resource)
        filter_kw = {fk_semantic_attr: value}
        if fk_current and hasattr(model, "data_registro_fim"):
            filter_kw["data_registro_fim"] = get_sentinela_date()
        qs = model.objects.filter(**filter_kw)
    obj = qs.first()
    if not obj and value:
        raise ValueError(f"Referência não encontrada: {fk_resource}.{fk_semantic_attr}={value}")
    return obj


def build_entity_filter(resource_name: str, entity_data: Dict[str, Any]) -> Dict[str, Any]:
    """Monta o dicionário de filtro para identificar a entidade (e a linha ativa)."""
    res = get_resource(resource_name)
    filt = {}
    for ek in res["entity_key"]:
        arg = ek["arg"]
        lookup = ek["lookup"]
        if arg not in entity_data:
            raise ValueError(f"Chave de entidade ausente no --data: {arg}")
        filt[lookup] = entity_data[arg]
    return filt


def get_export_value(obj, field_name: str, field_meta: Optional[Dict] = None, resource_name: Optional[str] = None) -> Any:
    """Valor de um campo para exportação CSV (FK vira o identificador semântico)."""
    if hasattr(obj, field_name):
        val = getattr(obj, field_name)
    else:
        val = getattr(obj, field_name, None)
    if val is None:
        return "" if field_meta and field_meta.get("type") == "string" else None
    # FK: exportar o identificador semântico
    if field_meta and field_meta.get("type") == "fk":
        # val é a instância relacionada; queremos o atributo semântico
        semantic_attr = field_meta.get("fk_semantic_attr", "pk")
        return getattr(val, semantic_attr, str(val))
    if hasattr(val, "isoformat"):
        return val.isoformat()
    return val
