"""
Inferência da lista de abreviações a partir de ``ItemClassificacao`` (BD), com fallback ao CSV de seed.

Delega a orquestração a ``apps.core.alias_lexico_run``; aplica flags ``(F)`` e export.
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Max
from django.utils import timezone

from apps.core.admin_mixins import transaction_time_sentinel_for_query
from apps.core.alias_lexico_infer import _interactive_pick_conflict_abbrev
from apps.core.alias_lexico_protocol import insert_alias_lexico_if_new
from apps.core.alias_lexico_run import (
    export_alias_lexico_seed,
    maybe_export_seed_after_management_batch,
    renumber_alias_lexico_refs_alphabetical,
    run_alias_lexico_infer_persist,
)
from apps.core.alias_lexico_termo_policy import termo_nome_rejeitado_encurtamento_iv
from apps.core.models_alias_lexico import AliasLexico, lista_abreviacoes_registro_inicio_novo

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        "Atualiza lista_abreviacoes no BD por inferência a partir de ItemClassificacao (vigência em T); "
        "apenas INSERTs novos na fase automática (nunca apaga linhas existentes). "
        "fallback opcional aos CSVs de seed. Export do seed (iii) só após mutações na lista, salvo "
        "--export-seed. Flags --print-conflicts / --print-conflicts-resolve conforme spec."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--as-of",
            default=None,
            help="Instante ISO8601 para T (vigência orçamentária); default: agora (timezone.now()).",
        )
        parser.add_argument(
            "--no-items-csv-fallback",
            action="store_true",
            help="Não ler seed_item_classificacao.csv quando não houver linhas de item válidas em T na BD.",
        )
        parser.add_argument(
            "--no-alias-seed-fallback",
            action="store_true",
            help="Não ler seed_lista_abreviacoes.csv quando a tabela lista_abreviacoes estiver vazia.",
        )
        parser.add_argument(
            "--print-conflicts",
            action="store_true",
            help="Lista conflitos silenciosos ao fim (não altera o BD).",
        )
        parser.add_argument(
            "--print-conflicts-resolve",
            action="store_true",
            help=(
                "Modo interativo após gravação automática: INSERT para termo novo ou UPDATE da "
                "abreviação se o termo já existir (spec F), com confirmação [y/N] antes de substituir "
                "linha existente."
            ),
        )
        parser.add_argument(
            "--no-export",
            action="store_true",
            help="Não exportar seed_lista_abreviacoes.csv após mutações.",
        )
        parser.add_argument(
            "--export-seed",
            action="store_true",
            help=(
                "Exportar sempre docs/assets/seed_lista_abreviacoes.csv a partir da BD "
                "(útil quando não houve INSERT/UPDATE nesta execução mas a tabela já foi alterada). "
                "Por omissão cria cópia .backup.* do CSV anterior antes de substituir o ficheiro."
            ),
        )
        parser.add_argument(
            "--export-seed-no-backup",
            action="store_true",
            help="Com ``--export-seed``, não criar ficheiro ``.backup.*`` antes de substituir o CSV.",
        )
        parser.add_argument(
            "--new-ref",
            action="store_true",
            help=(
                "Após inferência (e resolução interactiva, se aplicável), renumera alias_lexico_ref "
                "na BD para 1..N na ordem alfabética de termo (LOWER(termo), data_registro_inicio), "
                "como no export do seed; em seguida exporta o CSV se não usar --no-export."
            ),
        )

    def handle(self, *args, **options):
        logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
        print_conflicts: bool = options["print_conflicts"]
        print_resolve: bool = options["print_conflicts_resolve"]
        no_export: bool = options["no_export"]
        export_seed: bool = options["export_seed"]
        export_seed_no_backup: bool = options["export_seed_no_backup"]
        new_ref: bool = options["new_ref"]

        n_lista_existing = AliasLexico.objects.count()

        if options["as_of"]:
            raw = options["as_of"].strip()
            try:
                t_instant = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            except ValueError:
                self.stderr.write(self.style.ERROR(f"--as-of inválido: {raw!r}"))
                return
            if timezone.is_naive(t_instant):
                t_instant = timezone.make_aware(t_instant, timezone.get_current_timezone())
        else:
            t_instant = timezone.now()

        logger.info(
            "atualizar_lista_abreviacoes: início T=%s print_conflicts=%s print_resolve=%s "
            "lista_abreviacoes_existentes=%s new_ref=%s",
            t_instant.isoformat(),
            print_conflicts,
            print_resolve,
            n_lista_existing,
            new_ref,
        )

        res = run_alias_lexico_infer_persist(
            t_instant=t_instant,
            items_csv_fallback=not options["no_items_csv_fallback"],
            alias_seed_fallback=not options["no_alias_seed_fallback"],
        )
        conflicts = res.conflicts

        logger.info(
            "atualizar_lista_abreviacoes: inferência — inferidos=%s omitidas_comp_inf=%s omitidas_junction_m=%s "
            "derivadas=%s omitidas_termo_viii=%s",
            res.n_inferred_only,
            res.n_skip_comp_inf,
            res.n_skip_junction_m,
            res.n_derived,
            res.n_skip_termo_viii,
        )
        logger.info(
            "atualizar_lista_abreviacoes: inserts — inseridos=%s duplicados=%s itens_em_T=%s",
            res.n_inserted,
            res.n_skipped_duplicate,
            res.n_item_rows_at_t,
        )

        sent_orm = transaction_time_sentinel_for_query()
        n_resolve_insert = 0
        n_resolve_update = 0
        if print_resolve and conflicts:
            if not sys.stdin.isatty():
                logger.warning(
                    "atualizar_lista_abreviacoes: --print-conflicts-resolve ignorado (stdin não é TTY)"
                )
                self.stderr.write(
                    self.style.WARNING(
                        "Resolução interativa ignorada: stdin não é um terminal "
                        "(use um terminal interativo para --print-conflicts-resolve)."
                    )
                )
            else:
                logger.info(
                    "atualizar_lista_abreviacoes: resolução interativa para %s conflito(s)",
                    len(conflicts),
                )
                with transaction.atomic():
                    for termo_c, abrevs in sorted(conflicts, key=lambda x: x[0].lower()):
                        opts = sorted(abrevs)
                        picked = _interactive_pick_conflict_abbrev(termo_c, opts)
                        if picked is None:
                            continue
                        existing = AliasLexico.objects.filter(termo__iexact=termo_c).first()
                        if existing:
                            cur = (existing.abreviacao or "").strip()
                            if cur == picked:
                                logger.info(
                                    "atualizar_lista_abreviacoes: resolve sem alteração termo=%r",
                                    termo_c,
                                )
                                continue
                            self.stdout.write(
                                self.style.WARNING(
                                    f"\nO termo {termo_c!r} já existe na lista de abreviações "
                                    f"(abreviação actual: {cur!r}).\n"
                                    f"Substituir por {picked!r}? [y/N]"
                                )
                            )
                            resp = input("> ").strip().lower()
                            if resp not in {"y", "yes", "s", "sim"}:
                                logger.info(
                                    "atualizar_lista_abreviacoes: resolve UPDATE recusado termo=%r",
                                    termo_c,
                                )
                                self.stdout.write(
                                    self.style.NOTICE(
                                        f"Mantido registo existente para {termo_c!r} (abrev.: {cur!r})."
                                    )
                                )
                                continue
                            existing.abreviacao = picked
                            existing.data_registro_fim = sent_orm
                            existing.save(update_fields=["abreviacao", "data_registro_fim"])
                            n_resolve_update += 1
                            logger.info(
                                "atualizar_lista_abreviacoes: resolve UPDATE termo=%r abreviacao=%r",
                                termo_c,
                                picked,
                            )
                        else:
                            if termo_nome_rejeitado_encurtamento_iv(termo_c):
                                logger.warning(
                                    "atualizar_lista_abreviacoes: resolve INSERT omitido (termo viii): %r",
                                    termo_c,
                                )
                                self.stderr.write(
                                    self.style.WARNING(
                                        f"Resolução: INSERT omitido — termo inválido por (viii): {termo_c!r}"
                                    )
                                )
                                continue
                            mx = AliasLexico.objects.aggregate(m=Max("alias_lexico_ref"))["m"] or 0
                            inserted, _ = insert_alias_lexico_if_new(
                                termo=termo_c,
                                abreviacao=picked,
                                alias_lexico_ref=mx + 1,
                                data_registro_inicio=lista_abreviacoes_registro_inicio_novo(),
                                data_registro_fim=sent_orm,
                            )
                            if inserted:
                                n_resolve_insert += 1
                                logger.info(
                                    "atualizar_lista_abreviacoes: resolve INSERT termo=%r abreviacao=%r",
                                    termo_c,
                                    picked,
                                )

        if print_conflicts and conflicts:
            logger.info(
                "atualizar_lista_abreviacoes: conflitos silenciosos (lista parcial até 80): total=%s",
                len(conflicts),
            )
            for t, ab in conflicts[:80]:
                self.stdout.write(f"  {t!r}: {sorted(ab)}")
            if len(conflicts) > 80:
                self.stdout.write(self.style.WARNING(f"  ... e mais {len(conflicts) - 80}"))

        n_renumbered = 0
        if new_ref:
            n_renumbered = renumber_alias_lexico_refs_alphabetical()
            if n_renumbered:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Renumeração --new-ref: {n_renumbered} linhas, alias_lexico_ref 1..{n_renumbered} "
                        f"(ordem alfabética de termo)."
                    )
                )

        if not no_export:
            try:
                if export_seed:
                    result = export_alias_lexico_seed(
                        do_backup=not export_seed_no_backup,
                    )
                    logger.info(
                        "atualizar_lista_abreviacoes: export forçado (--export-seed) output=%s",
                        result.get("output"),
                    )
                    self.stdout.write(self.style.SUCCESS(f"Export seed: {result.get('output')}"))
                else:
                    result = maybe_export_seed_after_management_batch(
                        n_auto_insert=res.n_inserted,
                        n_resolve_insert=n_resolve_insert,
                        n_resolve_update=n_resolve_update,
                        n_renumbered=n_renumbered,
                    )
                    if result is not None:
                        logger.info(
                            "atualizar_lista_abreviacoes: export (iii) lista_abreviacoes output=%s",
                            result.get("output"),
                        )
                        self.stdout.write(self.style.SUCCESS(f"Export seed: {result.get('output')}"))
                    else:
                        self.stdout.write(
                            self.style.NOTICE(
                                "Export do seed omitido (nenhuma mutação nesta execução). "
                                "Para gravar a BD actual no CSV: "
                                "``python manage.py atualizar_lista_abreviacoes --export-seed``."
                            )
                        )
            except Exception as exc:
                logger.exception("atualizar_lista_abreviacoes: export falhou")
                self.stderr.write(self.style.ERROR(f"Export falhou: {exc}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"Concluído: inseridos={res.n_inserted} omitidos_termo_viii={res.n_skip_termo_viii} "
                f"resolve_insert={n_resolve_insert} resolve_update={n_resolve_update} "
                f"renumerados={n_renumbered} conflitos_pendentes={len(conflicts)}"
            )
        )
