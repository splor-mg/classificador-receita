"""
Carrega dados iniciais a partir do datapackage.yaml (ADR-004 Regra 8).

Recursos bitemporais (serie_classificacao, classificacao, nivel_hierarquico,
versao_classificacao, variante_classificacao, item_classificacao): os seeds devem
estar em conformidade com o modelo bitemporal (data_registro_*, data_vigencia_*);
o carregamento apenas insere as linhas dos CSVs.

base_legal_tecnica é modelo temporal simples (SCD-1, alteração in-place); as
Regras 1 a 7 da ADR-004 não se aplicam ao seu carregamento nem à sua governança.
"""
from datetime import datetime
from pathlib import Path
from typing import Iterable, Mapping, Any

from django.core.management.base import BaseCommand, CommandParser
from django.db import transaction
from django.utils import timezone

from frictionless import Package, Resource


def make_datetime_aware(value):
    """Converte datetime naive para aware no timezone local (settings.TIME_ZONE)."""
    if value is None:
        return None
    if isinstance(value, datetime):
        if timezone.is_naive(value):
            return timezone.make_aware(value)
        return value
    return value

from apps.core.models import (
    SerieClassificacao,
    BaseLegalTecnica,
    Classificacao,
    NivelHierarquico,
    ItemClassificacao,
    VersaoClassificacao,
    VarianteClassificacao,
)
from apps.core.bitemporal_registry import get_sentinela_datetime


class Command(BaseCommand):
    help = (
        "Carrega dados iniciais do classificador de receita a partir do datapackage.yaml "
        "e dos arquivos seed_* declarados nos recursos. Recursos bitemporais seguem ADR-004; "
        "base_legal_tecnica é SCD-1 (temporal simples)."
    )

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--datapackage",
            default="datapackage.yaml",
            help="Caminho para o datapackage.yaml (padrão: %(default)s).",
        )
        parser.add_argument(
            "--resource",
            help=(
                "Nome de um recurso específico do Data Package a ser carregado "
                "(ex.: serie_classificacao, classificacao, nivel_hierarquico...). "
                "Se omitido, carrega todos os recursos na ordem recomendada."
            ),
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Executa apenas leitura/contagem das linhas dos recursos, sem escrever no banco.",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help=(
                "Antes de carregar, limpa as tabelas correspondentes (ordem inversa das dependências). "
                "Use com cuidado em ambientes com dados."
            ),
        )

    def handle(self, *args, **options) -> None:
        datapackage_path = Path(options["datapackage"])
        resource_filter = options.get("resource")
        dry_run: bool = options["dry_run"]
        clear: bool = options["clear"]

        if not datapackage_path.exists():
            self.stderr.write(self.style.ERROR(f"datapackage.yaml não encontrado em {datapackage_path}"))
            return

        package = Package(str(datapackage_path))

        # Ordem de carregamento previamente alinhada
        load_order = [
            "serie_classificacao",
            "base_legal_tecnica",
            "classificacao",
            "nivel_hierarquico",
            "versao_classificacao",
            "variante_classificacao",
            "item_classificacao",
        ]

        if resource_filter:
            if resource_filter not in load_order:
                self.stderr.write(
                    self.style.ERROR(
                        f"Recurso '{resource_filter}' não é conhecido. "
                        f"Recursos válidos: {', '.join(load_order)}"
                    )
                )
                return
            resources_to_load = [resource_filter]
        else:
            resources_to_load = load_order

        # Mapeamento recurso -> model Django
        resource_model_map = {
            "serie_classificacao": SerieClassificacao,
            "base_legal_tecnica": BaseLegalTecnica,
            "classificacao": Classificacao,
            "nivel_hierarquico": NivelHierarquico,
            "item_classificacao": ItemClassificacao,
            "versao_classificacao": VersaoClassificacao,
            "variante_classificacao": VarianteClassificacao,
        }

        if clear and not dry_run:
            # Limpa tabelas na ordem inversa das dependências, apenas para os recursos selecionados
            self.stdout.write(self.style.WARNING("Limpando tabelas antes do carregamento (--clear)..."))
            for name in reversed(load_order):
                if name in resources_to_load:
                    model = resource_model_map[name]
                    deleted, _ = model.objects.all().delete()
                    self.stdout.write(f"  - {name}: {deleted} registros apagados.")

        if dry_run:
            self.stdout.write(self.style.NOTICE("Executando em modo dry-run (sem gravação no banco)."))

        # Envolve o carregamento em transação quando não for dry-run
        ctx = transaction.atomic() if not dry_run else _nullcontext()

        with ctx:
            for name in resources_to_load:
                resource = package.get_resource(name)
                self._load_resource(name, resource, dry_run)

        self.stdout.write(self.style.SUCCESS("Carregamento concluído."))

    # ---- helpers de carregamento por recurso ---------------------------------

    def _load_resource(self, name: str, resource: Resource, dry_run: bool) -> None:
        if dry_run:
            # Para dry-run, usamos inferência/estatísticas para obter número de linhas
            try:
                resource.infer()
                total = resource.stats.get("rows")  # type: ignore[assignment]
            except Exception:
                total = None

            if total is not None:
                self.stdout.write(f"[dry-run] {name}: {total} linhas encontradas em {resource.path}.")
            else:
                self.stdout.write(f"[dry-run] {name}: não foi possível inferir número de linhas em {resource.path}.")
            return

        try:
            rows: Iterable[Mapping[str, Any]] = list(resource.read_rows())
        except Exception as e:
            # Log diagnostic info to help debug resource opening issues (encoding / path / format)
            import traceback as _traceback
            import sys as _sys

            self.stderr.write(self.style.ERROR(f"Falha ao abrir recurso '{name}' - path={getattr(resource, 'path', None)}"))
            # Print full traceback to stderr for deeper diagnosis
            _traceback.print_exc(file=_sys.stderr)
            # Try to show resource descriptor/metadata if available (best-effort)
            try:
                desc = None
                try:
                    desc = getattr(resource, "descriptor", None)
                except Exception:
                    # older/newer versions may expose different attributes
                    try:
                        desc = resource.metadata.to_descriptor()
                    except Exception:
                        desc = None
                self.stderr.write(self.style.ERROR(f"Resource descriptor/metadata: {desc}"))
            except Exception:
                pass
            # Fallback: tentar ler o CSV diretamente com csv.DictReader (mais tolerante)
            csv_path = getattr(resource, "path", None)
            if csv_path:
                import csv as _csv

                try:
                    with open(csv_path, newline="", encoding="utf-8") as _f:
                        dict_reader = _csv.DictReader(_f)
                        rows = list(dict_reader)
                        self.stdout.write(self.style.NOTICE(f"[fallback] lidas {len(rows)} linhas em {csv_path} via csv.DictReader"))
                except Exception as e2:
                    self.stderr.write(self.style.ERROR(f"[fallback] falha ao ler {csv_path} diretamente: {e2}"))
                    raise
            else:
                raise
        # Dispatch to resource-specific loaders (outside of exception handling).
        if name == "serie_classificacao":
            self._load_serie_classificacao(rows)
        elif name == "base_legal_tecnica":
            self._load_base_legal_tecnica(rows)
        elif name == "classificacao":
            self._load_classificacao(rows)
        elif name == "nivel_hierarquico":
            self._load_nivel_hierarquico(rows)
        elif name == "versao_classificacao":
            self._load_versao_classificacao(rows)
        elif name == "variante_classificacao":
            self._load_variante_classificacao(rows)
        elif name == "item_classificacao":
            self._load_item_classificacao(rows)
        else:
            self.stdout.write(self.style.WARNING(f"Recurso '{name}' não possui loader específico. Ignorando."))

    def _prepare_registro_dates(self, row: Mapping[str, Any]) -> dict:
        """Converte datas de registro naive para aware e retorna dict com as datas."""
        result = dict(row)
        if "data_registro_inicio" in result:
            result["data_registro_inicio"] = make_datetime_aware(result["data_registro_inicio"])
        if "data_registro_fim" in result:
            result["data_registro_fim"] = make_datetime_aware(result["data_registro_fim"])
        return result

    def _get_bitemporal_instance(self, model, semantic_field: str, row: Mapping[str, Any]):
        """
        Retorna a instância bitemporal correta do model dado o identificador semântico
        presente em row. Se row contém `data_registro_inicio` tenta corresponder por
        essa data; caso contrário, busca a instância atual (data_registro_fim = sentinela).
        """
        semantic_val = row.get(semantic_field)
        if semantic_val is None or semantic_val == "":
            return None
        # Preferir correspondência por data_registro_inicio quando disponível
        dr_ini = row.get("data_registro_inicio")
        try:
            if dr_ini:
                dr_ini_aware = make_datetime_aware(dr_ini)
                return model.objects.get(**{semantic_field: semantic_val, "data_registro_inicio": dr_ini_aware})
            return model.objects.get(**{semantic_field: semantic_val, "data_registro_fim": get_sentinela_datetime()})
        except model.DoesNotExist:
            # fallback: try to return any matching semantic (may raise MultipleObjectsReturned)
            return model.objects.filter(**{semantic_field: semantic_val}).first()

    def _load_serie_classificacao(self, rows: Iterable[Mapping[str, Any]]) -> None:
        if SerieClassificacao.objects.exists():
            self.stdout.write(
                self.style.WARNING(
                    "Tabela 'serie_classificacao' já possui registros. Pule este recurso ou use --clear."
                )
            )
            return

        created = 0
        for row in rows:
            prepared = self._prepare_registro_dates(row)
            SerieClassificacao.objects.create(**prepared)
            created += 1
        self.stdout.write(self.style.SUCCESS(f"serie_classificacao: {created} linhas carregadas."))

    def _load_base_legal_tecnica(self, rows: Iterable[Mapping[str, Any]]) -> None:
        if BaseLegalTecnica.objects.exists():
            self.stdout.write(
                self.style.WARNING(
                    "Tabela 'base_legal_tecnica' já possui registros. Pule este recurso ou use --clear."
                )
            )
            return

        created = 0
        for row in rows:
            BaseLegalTecnica.objects.create(**row)
            created += 1
        self.stdout.write(self.style.SUCCESS(f"base_legal_tecnica: {created} linhas carregadas."))

    def _load_classificacao(self, rows: Iterable[Mapping[str, Any]]) -> None:
        if Classificacao.objects.exists():
            self.stdout.write(
                self.style.WARNING(
                    "Tabela 'classificacao' já possui registros. Pule este recurso ou use --clear."
                )
            )
            return

        created = 0
        for row in rows:
            serie = self._get_bitemporal_instance(SerieClassificacao, "serie_id", row)

            base_legal = None
            base_id = row.get("base_legal_tecnica_id") or None
            if base_id:
                base_legal = BaseLegalTecnica.objects.get(base_legal_tecnica_id=base_id)

            prepared = self._prepare_registro_dates(row)
            Classificacao.objects.create(
                classificacao_id=prepared["classificacao_id"],
                classificacao_ref=prepared["classificacao_ref"],
                serie_id=serie,
                classificacao_nome=prepared["classificacao_nome"],
                classificacao_descricao=prepared.get("classificacao_descricao") or "",
                tipo_classificacao=prepared["tipo_classificacao"],
                numero_niveis=prepared["numero_niveis"],
                numero_digitos=prepared.get("numero_digitos"),
                base_legal_tecnica_id=base_legal,
                data_vigencia_inicio=prepared["data_vigencia_inicio"],
                data_vigencia_fim=prepared["data_vigencia_fim"],
                data_registro_inicio=prepared["data_registro_inicio"],
                data_registro_fim=prepared["data_registro_fim"],
            )
            created += 1

        self.stdout.write(self.style.SUCCESS(f"classificacao: {created} linhas carregadas."))

    def _load_nivel_hierarquico(self, rows: Iterable[Mapping[str, Any]]) -> None:
        if NivelHierarquico.objects.exists():
            self.stdout.write(
                self.style.WARNING(
                    "Tabela 'nivel_hierarquico' já possui registros. Pule este recurso ou use --clear."
                )
            )
            return

        created = 0
        for row in rows:
            prepared = self._prepare_registro_dates(row)
            classificacao = self._get_bitemporal_instance(Classificacao, "classificacao_id", prepared)
            NivelHierarquico.objects.create(
                nivel_id=prepared["nivel_id"],
                nivel_ref=prepared["nivel_ref"],
                classificacao_id=classificacao,
                nivel_numero=prepared["nivel_numero"],
                nivel_nome=prepared["nivel_nome"],
                nivel_descricao=prepared.get("nivel_descricao") or "",
                estrutura_codigo=prepared.get("estrutura_codigo") or "",
                numero_digitos=prepared.get("numero_digitos"),
                tipo_codigo=prepared["tipo_codigo"],
                data_vigencia_inicio=prepared["data_vigencia_inicio"],
                data_vigencia_fim=prepared["data_vigencia_fim"],
                data_registro_inicio=prepared["data_registro_inicio"],
                data_registro_fim=prepared["data_registro_fim"],
            )
            created += 1

        self.stdout.write(self.style.SUCCESS(f"nivel_hierarquico: {created} linhas carregadas."))

    def _load_versao_classificacao(self, rows: Iterable[Mapping[str, Any]]) -> None:
        if VersaoClassificacao.objects.exists():
            self.stdout.write(
                self.style.WARNING(
                    "Tabela 'versao_classificacao' já possui registros. Pule este recurso ou use --clear."
                )
            )
            return

        created = 0
        for row in rows:
            prepared = self._prepare_registro_dates(row)
            classificacao = self._get_bitemporal_instance(Classificacao, "classificacao_id", prepared)
            VersaoClassificacao.objects.create(
                versao_id=prepared["versao_id"],
                versao_ref=prepared["versao_ref"],
                classificacao=classificacao,
                versao_numero=prepared["versao_numero"],
                versao_nome=prepared.get("versao_nome") or "",
                versao_descricao=prepared.get("versao_descricao") or "",
                data_lancamento=prepared.get("data_lancamento"),
                data_vigencia_inicio=prepared["data_vigencia_inicio"],
                data_vigencia_fim=prepared["data_vigencia_fim"],
                data_registro_inicio=prepared["data_registro_inicio"],
                data_registro_fim=prepared["data_registro_fim"],
            )
            created += 1

        self.stdout.write(self.style.SUCCESS(f"versao_classificacao: {created} linhas carregadas."))

    def _load_variante_classificacao(self, rows: Iterable[Mapping[str, Any]]) -> None:
        if VarianteClassificacao.objects.exists():
            self.stdout.write(
                self.style.WARNING(
                    "Tabela 'variante_classificacao' já possui registros. Pule este recurso ou use --clear."
                )
            )
            return

        created = 0
        for row in rows:
            prepared = self._prepare_registro_dates(row)
            classificacao = self._get_bitemporal_instance(Classificacao, "classificacao_id", prepared)
            # No seed atual, versao_id pode vir vazio/-; mantemos FK opcional.
            versao = None
            versao_id = prepared.get("versao_id") or None
            if versao_id and versao_id != "-":
                # tentar encontrar versão correspondente por versao_id e data_registro, se fornecida
                dr_ini = prepared.get("data_registro_inicio")
                try:
                    if dr_ini:
                        versao = VersaoClassificacao.objects.get(versao_id=versao_id, data_registro_inicio=dr_ini)
                    else:
                        versao = VersaoClassificacao.objects.get(versao_id=versao_id, data_registro_fim=get_sentinela_datetime())
                except VersaoClassificacao.DoesNotExist:
                    versao = VersaoClassificacao.objects.filter(versao_id=versao_id).first()

            VarianteClassificacao.objects.create(
                variante_id=prepared["variante_id"],
                classificacao=classificacao,
                versao=versao,
                variante_nome=prepared["variante_nome"],
                tipo_variante=prepared["tipo_variante"],
                variante_descricao=prepared.get("variante_descricao") or "",
                proposito=prepared.get("proposito") or "",
                data_vigencia_inicio=prepared["data_vigencia_inicio"],
                data_vigencia_fim=prepared["data_vigencia_fim"],
                data_registro_inicio=prepared["data_registro_inicio"],
                data_registro_fim=prepared["data_registro_fim"],
            )
            created += 1

        self.stdout.write(self.style.SUCCESS(f"variante_classificacao: {created} linhas carregadas."))

    def _load_item_classificacao(self, rows: Iterable[Mapping[str, Any]]) -> None:
        if ItemClassificacao.objects.exists():
            self.stdout.write(
                self.style.WARNING(
                    "Tabela 'item_classificacao' já possui registros. Pule este recurso ou use --clear."
                )
            )
            return

        created = 0
        # Opcional: confiar na ordem do CSV (pais antes dos filhos).
        for row in rows:
            prepared = self._prepare_registro_dates(row)
            classificacao = self._get_bitemporal_instance(Classificacao, "classificacao_id", prepared)
            nivel = self._get_bitemporal_instance(NivelHierarquico, "nivel_id", prepared)

            base_legal = None
            base_id = prepared.get("base_legal_tecnica_id") or None
            if base_id and base_id != "-":
                base_legal = BaseLegalTecnica.objects.get(base_legal_tecnica_id=base_id)

            parent = None
            parent_code = prepared.get("parent_item_id") or None
            if parent_code and parent_code != "-":
                parent = ItemClassificacao.objects.filter(item_id=parent_code, data_registro_fim=get_sentinela_datetime()).first()

            # Normalize boolean and empty values coming from CSV (csv.DictReader returns strings)
            def _to_bool(v):
                if isinstance(v, bool):
                    return v
                if v is None:
                    return False
                s = str(v).strip().lower()
                return s in ("1", "true", "t", "yes", "y")

            def _none_if_empty(v):
                if v is None:
                    return None
                s = str(v).strip()
                return None if s in ("", "-", "NA", "null", "None") else s

            matriz_val = _to_bool(prepared.get("matriz"))
            item_gerado_val = _to_bool(prepared.get("item_gerado"))

            item = ItemClassificacao(
                item_id=_none_if_empty(prepared.get("item_id")),
                item_ref=_none_if_empty(prepared.get("item_ref")),
                classificacao_id=classificacao,
                receita_cod=_none_if_empty(prepared.get("receita_cod")),
                matriz=matriz_val,
                receita_nome=_none_if_empty(prepared.get("receita_nome")),
                receita_descricao=_none_if_empty(prepared.get("receita_descricao")),
                base_legal_tecnica_id=base_legal,
                base_legal_tecnica_referencia=_none_if_empty(prepared.get("base_legal_tecnica_referencia")),
                destinacao_legal=_none_if_empty(prepared.get("destinacao_legal")),
                informacoes_gerenciais=_none_if_empty(prepared.get("informacoes_gerenciais")),
                nivel_id=nivel,
                parent_item_id=parent,
                item_gerado=item_gerado_val,
                data_vigencia_inicio=prepared["data_vigencia_inicio"],
                data_vigencia_fim=prepared["data_vigencia_fim"],
                data_registro_inicio=prepared["data_registro_inicio"],
                data_registro_fim=prepared["data_registro_fim"],
            )
            # Skip model validation during bulk load; DB and later processes enforce business rules.
            item.save(_skip_validation=True)
            created += 1

        self.stdout.write(self.style.SUCCESS(f"item_classificacao: {created} linhas carregadas."))


class _nullcontext:
    """Context manager que não faz nada (usado para dry-run)."""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False