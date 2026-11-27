"""Forma um CSV de item no schema, com identificador, nível e pai.

A máscara sai das linhas abertas de ``seed_nivel_hierarquico.csv``: registro
com fim no sentinela ``9999-12-31``. ``classificacao_id`` escolhe a largura, e
todo nível aberto dessa largura entra na máscara. ``item_ref`` fica vazio
quando o arquivo não o traz. As colunas de registro não são gravadas.
"""

from __future__ import annotations

import csv
import io
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

OUTPUT_COLUMNS = (
    "item_id",
    "item_ref",
    "classificacao_id",
    "receita_cod",
    "matriz",
    "receita_nome",
    "receita_descricao",
    "base_legal_tecnica_id",
    "base_legal_tecnica_referencia",
    "destinacao_legal",
    "informacoes_gerenciais",
    "nivel_id",
    "parent_item_id",
    "item_gerado",
    "data_vigencia_inicio",
    "data_vigencia_fim",
)
RECORD_COLUMNS = ("data_registro_inicio", "data_registro_fim")
DERIVED_COLUMNS = ("item_id", "nivel_id", "parent_item_id")
REQUIRED_COLUMNS = ("receita_cod",)
PARENT_MISSING = "-"
RECORD_SENTINEL = "9999-12-31"


class ItemTransformError(Exception):
    """O pedido parou. O CSV de destino não foi gravado."""


@dataclass(frozen=True)
class LevelSegment:
    nivel_id: str
    nivel_numero: int
    numero_digitos: int


@dataclass(frozen=True)
class Mask:
    width: int
    segments: tuple[LevelSegment, ...]


def default_level_seed_path() -> Path:
    return Path(__file__).resolve().parents[2] / "docs" / "assets" / "seed_nivel_hierarquico.csv"


def assign_classification(
    header: list[str], rows: list[list[str]], classification: str
) -> tuple[list[str], list[list[str]]]:
    """Garante ``classificacao_id`` e preenche cada linha de dados com o mesmo valor."""
    classification = classification.strip()
    if classification == "":
        raise ItemTransformError("Informe o valor de classificacao_id.")
    matches = [index for index, name in enumerate(header) if name == "classificacao_id"]
    if len(matches) > 1:
        raise ItemTransformError(
            "A coluna 'classificacao_id' aparece mais de uma vez no cabeçalho. "
            "O arquivo não foi alterado."
        )
    if matches:
        index = matches[0]
        filled: list[list[str]] = []
        for row in rows:
            cells = list(row)
            while len(cells) <= index:
                cells.append("")
            cells[index] = classification
            filled.append(cells)
        return list(header), filled

    insert_at = len(header)
    target = OUTPUT_COLUMNS.index("classificacao_id")
    rank = {name: index for index, name in enumerate(OUTPUT_COLUMNS)}
    for index, name in enumerate(header):
        if name in rank and rank[name] > target:
            insert_at = index
            break
    new_header = header[:insert_at] + ["classificacao_id"] + header[insert_at:]
    filled = []
    for row in rows:
        cells = list(row)
        cells.insert(insert_at, classification)
        filled.append(cells)
    return new_header, filled


def transform_csv(
    path: Path,
    level_seed_path: Path | None = None,
    *,
    classification: str | None = None,
) -> None:
    """Reescreve ``path`` ou não grava nada."""
    forced = None if classification is None else classification.strip()
    if forced == "":
        raise ItemTransformError("Informe o valor de classificacao_id.")
    path = Path(path)
    seed_path = default_level_seed_path() if level_seed_path is None else Path(level_seed_path)
    if path.suffix.lower() != ".csv":
        raise ItemTransformError(f"O arquivo '{path}' não é CSV.")
    if not path.is_file():
        raise ItemTransformError(f"O arquivo '{path}' não foi encontrado.")

    raw, rows, delimiter = _read_csv(path)
    if not rows:
        raise ItemTransformError(f"O arquivo '{path}' não tem cabeçalho.")
    header = [name.strip() for name in rows[0]]
    _refuse_header(header)
    masks = load_masks(seed_path)
    rewritten = [list(OUTPUT_COLUMNS)]
    codes: dict[str, int] = {}
    pending: list[tuple[int, str, Mask, int]] = []
    for line, row in enumerate(rows[1:], start=2):
        if not any(cell.strip() for cell in row):
            continue
        values = _row_map(header, row)
        code = values.get("receita_cod", "").strip()
        classification = (
            forced if forced is not None else values.get("classificacao_id", "").strip()
        )
        if code in codes:
            raise ItemTransformError(
                f"O código '{code}' aparece mais de uma vez. O arquivo não foi alterado."
            )
        codes[code] = line
        item = {name: values.get(name, "").strip() for name in OUTPUT_COLUMNS}
        item["item_id"] = f"IT-{code}"
        item["receita_cod"] = code
        item["classificacao_id"] = classification
        if classification:
            mask = _mask_for(masks, classification, line)
            if len(code) != mask.width or not code.isdigit():
                raise ItemTransformError(
                    f"A linha {line}, código '{code}', tem {len(code)} dígitos e a máscara tem {mask.width}. "
                    "O arquivo não foi alterado."
                )
            level = _level_index(code, mask)
            if level is None:
                raise ItemTransformError(
                    f"A linha {line}, código '{code}', não tem nível. O arquivo não foi alterado."
                )
            item["nivel_id"] = mask.segments[level].nivel_id
            pending.append((line, code, mask, level))
        rewritten.append(item)

    by_code = {item["receita_cod"]: item["item_id"] for item in rewritten[1:]}
    for line, code, mask, level in pending:
        item = next(row for row in rewritten[1:] if row["receita_cod"] == code)
        if level == 0:
            item["parent_item_id"] = PARENT_MISSING
            continue
        keep = sum(segment.numero_digitos for segment in mask.segments[:level])
        parent_code = code[:keep] + ("0" * (mask.width - keep))
        parent_id = by_code.get(parent_code)
        if parent_id is None:
            raise ItemTransformError(
                f"A linha {line}, código '{code}', não encontra o pai '{parent_code}'. "
                "O arquivo não foi alterado."
            )
        item["parent_item_id"] = parent_id

    body = [list(OUTPUT_COLUMNS)]
    body.extend([[item[name] for name in OUTPUT_COLUMNS] for item in rewritten[1:]])
    lineterminator = "\r\n" if b"\r\n" in raw else "\n"
    _write_csv(path, body, lineterminator, delimiter)


def load_masks(path: Path) -> dict[str, Mask]:
    """Uma máscara por ``classificacao_id`` presente nas linhas abertas."""
    path = Path(path)
    if not path.is_file():
        raise ItemTransformError(f"A semente de nível '{path}' não foi encontrada.")
    _raw, rows, _delimiter = _read_csv(path)
    if not rows:
        raise ItemTransformError(f"A semente de nível '{path}' não tem cabeçalho.")
    header = [name.strip() for name in rows[0]]
    missing = [
        name
        for name in (
            "classificacao_id",
            "nivel_id",
            "nivel_numero",
            "estrutura_codigo",
            "numero_digitos",
            "data_registro_fim",
        )
        if name not in header
    ]
    if missing:
        raise ItemTransformError(f"A semente de nível '{path}' não tem a coluna '{missing[0]}'.")

    open_rows: list[tuple[str, str, int, int, int]] = []
    for line, row in enumerate(rows[1:], start=2):
        if not any(cell.strip() for cell in row):
            continue
        values = _row_map(header, row)
        record_end = values.get("data_registro_fim", "").strip()
        if not record_end.startswith(RECORD_SENTINEL):
            continue
        classification = values.get("classificacao_id", "").strip()
        nivel_id = values.get("nivel_id", "").strip()
        try:
            numero = int(values.get("nivel_numero", "").strip())
            digits = int(values.get("numero_digitos", "").strip())
        except ValueError as exc:
            raise ItemTransformError(
                f"A linha {line} da semente de nível não tem número de nível legível."
            ) from exc
        width = _estrutura_width(values.get("estrutura_codigo", ""))
        open_rows.append((classification, nivel_id, numero, digits, width))

    by_width: dict[int, list[tuple[str, int, int]]] = {}
    widths_of: dict[str, set[int]] = {}
    for classification, nivel_id, numero, digits, width in open_rows:
        widths_of.setdefault(classification, set()).add(width)
        by_width.setdefault(width, []).append((nivel_id, numero, digits))

    masks: dict[str, Mask] = {}
    for classification, widths in widths_of.items():
        if len(widths) > 1:
            raise ItemTransformError(
                f"A classificação '{classification}' tem mais de uma máscara aberta. "
                "O arquivo não foi alterado."
            )
    masks_by_width = {width: _mask_from_levels(width, levels) for width, levels in by_width.items()}
    for classification, widths in widths_of.items():
        masks[classification] = masks_by_width[next(iter(widths))]
    return masks


def _mask_from_levels(width: int, levels: list[tuple[str, int, int]]) -> Mask:
    chosen: dict[int, tuple[str, int]] = {}
    for nivel_id, numero, digits in levels:
        previous = chosen.get(numero)
        if previous is None:
            chosen[numero] = (nivel_id, digits)
            continue
        if previous != (nivel_id, digits):
            raise ItemTransformError(
                f"A máscara de {width} dígitos define o nível {numero} mais de uma vez. "
                "O arquivo não foi alterado."
            )
    segments = tuple(
        LevelSegment(nivel_id, numero, digits)
        for numero, (nivel_id, digits) in sorted(chosen.items())
    )
    if sum(segment.numero_digitos for segment in segments) != width:
        raise ItemTransformError(
            f"A máscara de {width} dígitos não fecha a soma dos níveis. "
            "O arquivo não foi alterado."
        )
    return Mask(width, segments)


def _mask_for(masks: dict[str, Mask], classification: str, line: int) -> Mask:
    mask = masks.get(classification)
    if mask is None:
        raise ItemTransformError(
            f"A linha {line}, classificação '{classification}', não tem máscara aberta. "
            "O arquivo não foi alterado."
        )
    return mask


def _level_index(code: str, mask: Mask) -> int | None:
    start = 0
    found: int | None = None
    for index, segment in enumerate(mask.segments):
        piece = code[start : start + segment.numero_digitos]
        if piece != ("0" * segment.numero_digitos):
            found = index
        start += segment.numero_digitos
    return found


def _estrutura_width(estrutura: str) -> int:
    return sum(1 for char in estrutura if char.isdigit() or char in "Xx")


def _refuse_header(header: list[str]) -> None:
    allowed = set(OUTPUT_COLUMNS) | set(RECORD_COLUMNS)
    for name in header:
        if name not in allowed:
            raise ItemTransformError(
                f"A coluna '{name}' não pertence ao schema. O arquivo não foi alterado."
            )
    for name in REQUIRED_COLUMNS:
        if name not in header:
            raise ItemTransformError(
                f"A coluna '{name}' não está no arquivo. O arquivo não foi alterado."
            )
    seen: set[str] = set()
    for name in header:
        if name in seen:
            raise ItemTransformError(
                f"A coluna '{name}' aparece mais de uma vez no cabeçalho. "
                "O arquivo não foi alterado."
            )
        seen.add(name)


def _row_map(header: list[str], row: list[str]) -> dict[str, str]:
    values = {name: "" for name in header}
    for name, cell in zip(header, row):
        values[name] = cell
    return values


def _read_csv(path: Path) -> tuple[bytes, list[list[str]], str]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise ItemTransformError(f"O arquivo '{path}' não pôde ser lido.") from exc
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ItemTransformError(f"O arquivo '{path}' não é texto UTF-8.") from exc
    first = text.splitlines()[0] if text else ""
    delimiter = _header_delimiter(first)
    rows = list(csv.reader(io.StringIO(text, newline=""), delimiter=delimiter))
    width = len(rows[0]) if rows else 0
    if rows and all(len(row) >= width for row in rows):
        return raw, rows, delimiter
    return raw, _read_physical_lines(text, delimiter), delimiter


def _read_physical_lines(text: str, delimiter: str) -> list[list[str]]:
    """Uma linha física é um registro. O último campo pode conter o separador.

    Algumas linhas vêm embrulhadas por aspas, com as aspas internas dobradas.
    """
    lines = text.splitlines()
    if not lines:
        return []
    header = lines[0].split(delimiter)
    width = len(header)
    rows = [header]
    for line in lines[1:]:
        if not line.strip():
            continue
        inner = _unwrap_whole_line(line, delimiter, width)
        parts = inner.split(delimiter, width - 1) if width else [inner]
        rows.append([_unwrap_field(part) for part in parts])
    return rows


def _unwrap_field(field: str) -> str:
    """Tira um par de aspas que embrulhava o campo inteiro, não as aspas do texto."""
    if len(field) >= 2 and field[0] == '"' and field[-1] == '"':
        return field[1:-1]
    return field


def _unwrap_whole_line(line: str, delimiter: str, width: int) -> str:
    if len(line) >= 2 and line[0] == '"' and line[-1] == '"':
        inner = line[1:-1].replace('""', '"')
        if inner.count(delimiter) >= max(width - 1, 1):
            return inner
    return line


def _header_delimiter(header_line: str) -> str:
    counts = {",": 0, ";": 0}
    quoted = False
    for char in header_line:
        if char == '"':
            quoted = not quoted
            continue
        if not quoted and char in counts:
            counts[char] += 1
    if counts[";"] > counts[","]:
        return ";"
    return ","


def _write_csv(path: Path, rows: list[list[str]], lineterminator: str, delimiter: str) -> None:
    handle_fd, tmp_name = tempfile.mkstemp(prefix=".transform-", suffix=".csv", dir=path.parent)
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(handle_fd, "w", encoding="utf-8", newline="") as handle:
            csv.writer(handle, delimiter=delimiter, lineterminator=lineterminator).writerows(rows)
        os.replace(tmp_path, path)
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise
