"""
Edição genérica de recursos bitemporais (ADR-004, Regras 2 a 7).

Tipos: sobrescrever (corrigir mesma vigência) ou nova_vigencia (encerrar vigência anterior + nova).
Identificação da linha: chave da entidade (em --data) + --data-registro-inicio.
data_registro_inicio e data_registro_fim das novas linhas são sempre definidos pelo comando (MUST).
Aplica-se apenas a recursos bitemporais (datapackage exceto base_legal_tecnica).
"""
import json
from datetime import date, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.core.bitemporal_registry import (
    RESOURCES,
    get_resource,
    get_model_for_resource,
    get_sentinela_date,
    build_entity_filter,
    resolve_fk,
)
from apps.core.models import VALID_TIME_SENTINEL


class Command(BaseCommand):
    help = (
        "Edita um registro ativo (data_registro_fim = sentinela) em um recurso bitemporal (ADR-004). "
        "Use --recurso, --data (JSON com chave da entidade e opcionalmente overrides) e "
        "--data-registro-inicio para identificar a linha. --tipo-edicao: sobrescrever | nova_vigencia. "
        "Para nova_vigencia, --nova-data-vigencia-inicio tem default 01/01/ano da operação (Regra 6)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--recurso",
            choices=sorted(RESOURCES.keys()),
            required=True,
            help="Recurso bitemporal.",
        )
        parser.add_argument(
            "--data",
            required=True,
            help='JSON com chave da entidade (ex.: {"nivel_id":"NIVEL-3","classificacao_id":"CLASS-X"}) e, opcionalmente, campos a alterar.',
        )
        parser.add_argument(
            "--data-registro-inicio",
            required=True,
            help="Data de início do registro da linha a editar (AAAA-MM-DD).",
        )
        parser.add_argument(
            "--tipo-edicao",
            choices=["sobrescrever", "nova_vigencia"],
            required=True,
            help="sobrescrever = corrigir mesma vigência; nova_vigencia = encerrar vigência anterior e registrar nova.",
        )
        parser.add_argument(
            "--nova-data-vigencia-inicio",
            default=None,
            help="Início da nova vigência para nova_vigencia (AAAA-MM-DD). Se omitido, usa 01/01/ano da operação (ADR-004 Regra 6).",
        )
        parser.add_argument(
            "--nova-data-vigencia-fim",
            default=VALID_TIME_SENTINEL.isoformat(),
            help=f"Fim da nova vigência para nova_vigencia (MUST: padrão sentinela {VALID_TIME_SENTINEL.isoformat()}; pode ser outra data para vigência encerrada).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Apenas exibe o que seria feito.",
        )
        parser.add_argument(
            "--listar",
            action="store_true",
            help="Lista linhas ativas do recurso e sai.",
        )

    def handle(self, *args, **options):
        resource_name = options["recurso"]
        res = get_resource(resource_name)
        model = get_model_for_resource(resource_name)
        sentinela = get_sentinela_date()

        if options.get("listar"):
            self._listar(resource_name, res, model, sentinela)
            return

        try:
            data = json.loads(options["data"])
        except json.JSONDecodeError as e:
            raise CommandError(f"--data JSON inválido: {e}") from e
        if not isinstance(data, dict):
            raise CommandError("--data deve ser um objeto JSON.")

        data_reg_ini_str = options["data_registro_inicio"]
        try:
            data_reg_ini = date.fromisoformat(data_reg_ini_str)
        except (ValueError, TypeError) as e:
            raise CommandError(f"data_registro_inicio inválido: {e}") from e

        filt = build_entity_filter(resource_name, data)
        filt["data_registro_inicio"] = data_reg_ini
        filt["data_registro_fim"] = sentinela

        qs = model.objects.filter(**filt)
        if res.get("select_related"):
            qs = qs.select_related(*res["select_related"])
        linha = qs.first()
        if not linha:
            raise CommandError(
                f"Linha ativa não encontrada para filtro {filt}. Use --listar para ver linhas ativas."
            )

        tipo = options["tipo_edicao"]
        data_op = date.today()
        if tipo == "nova_vigencia":
            # ADR-004 Regra 6: default para data_vigencia_inicio = 01/01/AAAA (ano da operação)
            nova_ini = options.get("nova_data_vigencia_inicio") or data.get("nova_data_vigencia_inicio")
            if not nova_ini:
                nova_ini = date(data_op.year, 1, 1)
            else:
                nova_ini = date.fromisoformat(nova_ini) if isinstance(nova_ini, str) else nova_ini
            nova_fim = options.get("nova_data_vigencia_fim") or data.get("nova_data_vigencia_fim", VALID_TIME_SENTINEL)
            nova_fim = date.fromisoformat(nova_fim) if isinstance(nova_fim, str) else nova_fim
            if nova_ini >= nova_fim:
                raise CommandError("nova_data_vigencia_inicio deve ser anterior a nova_data_vigencia_fim.")
            vig_fim_anterior = nova_ini - timedelta(days=1)
            if linha.data_vigencia_inicio > vig_fim_anterior:
                raise CommandError(
                    f"Vigência anterior resultaria em data_vigencia_fim ({vig_fim_anterior}) "
                    f"anterior a data_vigencia_inicio da linha ({linha.data_vigencia_inicio})."
                )
            self._editar_nova_vigencia(linha, resource_name, res, model, data_op, vig_fim_anterior, nova_ini, nova_fim, data, options)
        else:
            self._editar_sobrescrever(linha, resource_name, res, model, data_op, data, options)

    def _listar(self, resource_name, res, model, sentinela):
        qs = model.objects.filter(data_registro_fim=sentinela)
        if res.get("select_related"):
            qs = qs.select_related(*res["select_related"])
        order = res.get("order_by", [])
        if order:
            qs = qs.order_by(*order)
        rows = list(qs[:200])
        if not rows:
            self.stdout.write(f"Nenhuma linha ativa em {resource_name}.")
            return
        display = res.get("list_display", [])
        self.stdout.write(" | ".join(display))
        for r in rows:
            vals = []
            for attr in display:
                v = getattr(r, attr, None)
                if hasattr(v, "isoformat"):
                    v = v.isoformat()
                elif hasattr(v, "pk") and hasattr(v, "classificacao_id"):
                    v = getattr(v, "classificacao_id", str(v))
                elif hasattr(v, "pk") and hasattr(v, "serie_id"):
                    v = getattr(v, "serie_id", str(v))
                elif hasattr(v, "pk") and hasattr(v, "nivel_id"):
                    v = getattr(v, "nivel_id", str(v))
                vals.append(str(v) if v is not None else "")
            self.stdout.write(" | ".join(vals))
        if len(rows) >= 200:
            self.stdout.write("... (máx. 200)")

    def _attrs_from_row(self, linha, res):
        """Dicionário de atributos da linha para replicar (inclui vigência para create)."""
        out = {}
        for f in res["fields"]:
            name = f["name"]
            out[name] = getattr(linha, name, None)
        out["data_vigencia_inicio"] = linha.data_vigencia_inicio
        out["data_vigencia_fim"] = linha.data_vigencia_fim
        return out

    def _apply_overrides(self, attrs, res, resource_name, data, options):
        """Aplica overrides de --data nos attrs (valores para nova linha)."""
        for f in res["fields"]:
            name = f["name"]
            if name not in data:
                continue
            val = data[name]
            if f.get("type") == "fk" and val not in (None, ""):
                attrs[name] = resolve_fk(resource_name, f, val)
            elif f.get("type") == "integer" and val is not None:
                attrs[name] = int(val)
            elif f.get("type") == "boolean":
                attrs[name] = bool(val)
            elif f.get("type") == "date" and val is not None:
                attrs[name] = date.fromisoformat(val) if isinstance(val, str) else val
            else:
                attrs[name] = val

    def _editar_sobrescrever(self, linha, resource_name, res, model, data_op, data, options):
        attrs = self._attrs_from_row(linha, res)
        self._apply_overrides(attrs, res, resource_name, data, options)
        # Vigência pode ser sobrescrita
        if "data_vigencia_inicio" in data:
            attrs["data_vigencia_inicio"] = date.fromisoformat(data["data_vigencia_inicio"]) if isinstance(data["data_vigencia_inicio"], str) else data["data_vigencia_inicio"]
        if "data_vigencia_fim" in data:
            attrs["data_vigencia_fim"] = date.fromisoformat(data["data_vigencia_fim"]) if isinstance(data["data_vigencia_fim"], str) else data["data_vigencia_fim"]

        if options["dry_run"]:
            self.stdout.write(self.style.WARNING("Dry-run: fechar linha e inserir 1 nova (sobrescrever)."))
            self.stdout.write(f"  Nova linha: {attrs}")
            return

        with transaction.atomic():
            # Regra 4: única alteração in place é data_registro_fim
            linha.data_registro_fim = data_op
            linha.save(update_fields=["data_registro_fim"])
            # Nova linha: data_registro_* definidos pelo sistema (MUST)
            create_kw = {**attrs, "data_registro_inicio": data_op, "data_registro_fim": get_sentinela_date()}
            model.objects.create(**create_kw)
        self.stdout.write(self.style.SUCCESS("Edição (sobrescrever) aplicada."))

    def _editar_nova_vigencia(self, linha, resource_name, res, model, data_op, vig_fim_anterior, nova_ini, nova_fim, data, options):
        attrs_encerramento = self._attrs_from_row(linha, res)
        attrs_encerramento["data_vigencia_fim"] = vig_fim_anterior

        attrs_nova = self._attrs_from_row(linha, res)
        self._apply_overrides(attrs_nova, res, resource_name, data, options)
        attrs_nova["data_vigencia_inicio"] = nova_ini
        attrs_nova["data_vigencia_fim"] = nova_fim

        if options["dry_run"]:
            self.stdout.write(self.style.WARNING("Dry-run: fechar linha, inserir encerramento e nova vigência."))
            return

        with transaction.atomic():
            # Regra 4: fechar apenas data_registro_fim da linha editada
            linha.data_registro_fim = data_op
            linha.save(update_fields=["data_registro_fim"])
            # Novas linhas: data_registro_* definidos pelo sistema (MUST)
            sentinela = get_sentinela_date()
            create_enc = {**attrs_encerramento, "data_registro_inicio": data_op, "data_registro_fim": sentinela}
            model.objects.create(**create_enc)
            create_nova = {**attrs_nova, "data_registro_inicio": data_op, "data_registro_fim": sentinela}
            model.objects.create(**create_nova)
        self.stdout.write(self.style.SUCCESS("Edição (nova vigência) aplicada."))
