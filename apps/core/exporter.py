import tempfile
import os
import shutil
import sys
from pathlib import Path
from datetime import datetime
import threading

from django.db import connection
from django.conf import settings

from apps.core.bitemporal_registry import (
    get_resource,
    get_model_for_resource,
    get_sentinela_datetime,
    RESOURCES,
)
# process-local locks to serialize exports per resource
_resource_locks = {}


def export_resource(recurso: str, output: str | None = None, scope: str = "all", do_backup: bool = False, backup_dir: str | None = None, dry_run: bool = False) -> dict:
    """
    Exporta recurso definido no registry para CSV usando COPY.
    Retorna dict com info: {'rows': N (if available), 'output': path, 'backup': path_or_none}
    """
    res = get_resource(recurso)
    model = get_model_for_resource(recurso)
    columns = res["export_columns"]

    # Build joins and select parts similar to command implementation
    main_table = model._meta.db_table
    main_alias = "m"

    joins = []
    alias_map = {}
    alias_count = 0

    for fmeta in res["fields"]:
        if fmeta.get("type") != "fk":
            continue
        fname = fmeta["name"]
        fk_resource = fmeta.get("fk_resource")
        fk_semantic_attr = fmeta.get("fk_semantic_attr")
        if not fk_resource or not fk_semantic_attr:
            continue
        ref_model = get_model_for_resource(fk_resource)
        alias_count += 1
        alias = f"t{alias_count}"
        alias_map[fname] = (alias, ref_model, fk_semantic_attr)
        try:
            main_fk_col = model._meta.get_field(fname).column
        except Exception:
            main_fk_col = fname
        ref_pk_col = ref_model._meta.pk.column
        joins.append(f"LEFT JOIN {ref_model._meta.db_table} AS {alias} ON {main_alias}.{main_fk_col} = {alias}.{ref_pk_col}")

    select_parts = []
    app_tz = getattr(settings, "TIME_ZONE", "UTC")
    fields_by_name = {f["name"]: f for f in res["fields"]}
    for col in columns:
        fmeta = fields_by_name.get(col)
        if fmeta and fmeta.get("type") == "fk":
            alias, ref_model, fk_semantic_attr = alias_map.get(
                fmeta["name"], (None, None, None)
            )
            if alias is None:
                raise ValueError(f"FK field {fmeta['name']} has no join alias")
            try:
                sem_col = ref_model._meta.get_field(fk_semantic_attr).column
            except Exception:
                sem_col = fk_semantic_attr
            select_parts.append(f'{alias}.{sem_col} AS "{col}"')
        else:
            # Formatar campos datetime de registro no padrão
            # "YYYY-MM-DD HH:MM:SS" no timezone da aplicação, para
            # alinhar com o que é exibido no Admin (sem microsegundos
            # nem offset explícito).
            if col in ("data_registro_inicio", "data_registro_fim"):
                try:
                    col_db = model._meta.get_field(col).column
                except Exception:
                    col_db = col
                select_parts.append(
                    f"to_char({main_alias}.{col_db} AT TIME ZONE '{app_tz}', "
                    f"'YYYY-MM-DD HH24:MI:SS') AS \"{col}\""
                )
            else:
                try:
                    col_db = model._meta.get_field(col).column
                except Exception:
                    col_db = col
                select_parts.append(f'{main_alias}.{col_db} AS "{col}"')

    select_sql = f"SELECT {', '.join(select_parts)} FROM {main_table} AS {main_alias} "
    if joins:
        select_sql += " " + " ".join(joins)

    is_bitemporal = hasattr(model, "data_registro_inicio")
    where_clauses = []
    if is_bitemporal and scope == "current":
        sent = get_sentinela_datetime().isoformat()
        where_clauses.append(f"{main_alias}.data_registro_fim = TIMESTAMP '{sent}'")
    if where_clauses:
        select_sql += " WHERE " + " AND ".join(where_clauses)

    # Enforce deterministic ordering.
    order_sql_parts = []

    resource_order = res.get("order_by") or []
    if resource_order:
        # Respeitar explicitamente a ordem definida no registry.
        for ob in resource_order:
            direction = "ASC"
            field_expr = ob
            if ob.startswith("-"):
                direction = "DESC"
                field_expr = ob[1:]

            if "__" in field_expr:
                left, right = field_expr.split("__", 1)
                if left in alias_map:
                    alias, ref_model, fk_semantic_attr = alias_map[left]
                    try:
                        right_col = ref_model._meta.get_field(right).column
                    except Exception:
                        right_col = right
                    order_sql_parts.append(f"{alias}.{right_col} {direction}")
                else:
                    try:
                        col_db = model._meta.get_field(field_expr).column
                    except Exception:
                        col_db = field_expr.replace("__", ".")
                    order_sql_parts.append(f"{main_alias}.{col_db} {direction}")
            else:
                try:
                    col_db = model._meta.get_field(field_expr).column
                except Exception:
                    col_db = field_expr
                order_sql_parts.append(f"{main_alias}.{col_db} {direction}")
    else:
        # Fallback heurístico para recursos sem order_by explícito:
        # preferir campo *_ref, depois datas de vigência/registro.
        ref_field_name = None
        for f in res.get("fields", []):
            if f.get("name", "").endswith("_ref"):
                ref_field_name = f["name"]
                break

        if ref_field_name:
            try:
                ref_col = model._meta.get_field(ref_field_name).column
            except Exception:
                ref_col = ref_field_name
            order_sql_parts.append(f"{main_alias}.{ref_col} ASC")

        try:
            vig_col = model._meta.get_field("data_vigencia_inicio").column
            order_sql_parts.append(f"{main_alias}.{vig_col} DESC")
        except Exception:
            pass

        try:
            reg_col = model._meta.get_field("data_registro_inicio").column
            order_sql_parts.append(f"{main_alias}.{reg_col} DESC")
        except Exception:
            pass

    if order_sql_parts:
        select_sql += " ORDER BY " + ", ".join(order_sql_parts)

    copy_sql = f"COPY ({select_sql}) TO STDOUT WITH CSV HEADER"

    if dry_run:
        # Count approximate rows using the same WHERE if current
        count_sql = f"SELECT count(*) FROM {main_table} AS {main_alias}"
        if where_clauses:
            count_sql += " WHERE " + " AND ".join(where_clauses)
        with connection.cursor() as cur:
            cur.execute(count_sql)
            cnt = cur.fetchone()[0]
        return {"rows": cnt, "output": output, "backup": None}

    if output:
        out_path = Path(output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = None
        lock = _resource_locks.setdefault(recurso, threading.Lock())
        lock.acquire()
        try:
            try:
                with tempfile.NamedTemporaryFile(mode="wb", delete=False, dir=str(out_path.parent)) as tmpf:
                    tmp = tmpf.name
                    with connection.cursor() as cur:
                        cur.copy_expert(copy_sql, tmpf)
            except Exception:
                if tmp and os.path.exists(tmp):
                    os.remove(tmp)
                raise

            backup_path = None
            if do_backup and out_path.exists():
                bdir = Path(backup_dir) if backup_dir else out_path.parent
                bdir.mkdir(parents=True, exist_ok=True)
                ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
                backup_name = f"{out_path.name}.backup.{ts}"
                backup_path = bdir / backup_name
                shutil.move(str(out_path), str(backup_path))
            shutil.move(tmp, str(out_path))
            return {"rows": None, "output": str(out_path), "backup": str(backup_path) if backup_path else None}
        finally:
            lock.release()
            if tmp and os.path.exists(tmp):
                os.remove(tmp)
    else:
        with connection.cursor() as cur:
            # write to stdout.buffer (binary) to accept bytes from copy_expert
            cur.copy_expert(copy_sql, sys.stdout.buffer)
        return {"rows": None, "output": None, "backup": None}

