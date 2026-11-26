"""Normalização de colunas de um CSV.

A normalização de título sobrescreve a coluna. Com comparação, a origem permanece
e a leitura entra em ``<coluna>_normalized``, imediatamente à direita. Conectivos
saem de ``LEXICO_CONNECTIVOS_FIXOS``. A caixa de uma abreviação sai da primeira
ocorrência de ``abreviacao`` em ``docs/assets/seed_lista_abreviacoes.csv``. Aspas
duplas da leitura, retas ou curvas, viram aspas simples.

A normalização de texto troca essas mesmas aspas por aspas simples e sobrescreve
a coluna. Não cria coluna irmã e não aplica caixa de título. O trecho da coluna
começa depois do separador indicado pelo cabeçalho. Se a coluna é a última, o
trecho vai até o fim da linha, e um ponto e vírgula nesse trecho permanece.
Um arquivo lido com ponto e vírgula é gravado com vírgula. O campo que contém
vírgula sai entre aspas.
"""

from __future__ import annotations

import csv
import functools
import io
import os
import re
import tempfile
from pathlib import Path
from typing import Sequence

from apps.core.code_name_connectives import LEXICO_CONNECTIVOS_FIXOS

# Aspa reta e aspas duplas curvas (as de “Causa Mortis”).
_DOUBLE_QUOTES = str.maketrans(
    {
        '"': "'",
        "\u201c": "'",
        "\u201d": "'",
        "\u201e": "'",
        "\u201f": "'",
    }
)


class ColumnNormalizeError(Exception):
    """O pedido parou. O CSV de destino não foi gravado."""


def default_abbreviation_list_path() -> Path:
    return Path(__file__).resolve().parents[2] / "docs" / "assets" / "seed_lista_abreviacoes.csv"


def load_abbreviations(path: Path) -> list[str]:
    """Casing de ``abreviacao``, na ordem do arquivo. A primeira grafia de cada texto fica.

    Abreviação cujo texto inteiro é um conectivo fica de fora, para ``da`` não virar ``DA``.
    """
    path = Path(path)
    if not path.is_file():
        raise ColumnNormalizeError(f"A lista de abreviações '{path}' não foi encontrada.")
    try:
        text = path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ColumnNormalizeError(f"A lista de abreviações '{path}' não é texto UTF-8.") from exc

    rows = list(csv.reader(io.StringIO(text, newline="")))
    if not rows or "abreviacao" not in rows[0]:
        raise ColumnNormalizeError("A lista de abreviações não tem a coluna 'abreviacao'.")

    index = rows[0].index("abreviacao")
    found: list[str] = []
    seen: set[str] = set()
    for line, row in enumerate(rows[1:], start=2):
        if index >= len(row) or "\x00" in row[index]:
            raise ColumnNormalizeError(f"A linha {line}, coluna 'abreviacao', não é texto.")
        value = row[index]
        if value == "" or _abbreviation_is_connective(value):
            continue
        key = value.casefold()
        if key in seen:
            continue
        seen.add(key)
        found.append(value)
    return found


def title_case_reading(text: str, abbreviations: Sequence[str]) -> str:
    """Caixa de título fora dos trechos de abreviação; dentro, a caixa da lista."""
    spans = _abbreviation_spans(text, abbreviations)
    parts: list[str] = []
    cursor = 0
    for start, end, canonical in spans:
        parts.append(_title_case_gap(text[cursor:start]))
        parts.append(canonical)
        cursor = end
    parts.append(_title_case_gap(text[cursor:]))
    return "".join(parts).translate(_DOUBLE_QUOTES)


def plain_text_reading(text: str) -> str:
    """Troca aspas duplas, retas ou curvas, por aspas simples."""
    return text.translate(_DOUBLE_QUOTES)


def normalize_csv(
    path: Path,
    column: str,
    abbreviations: Sequence[str],
    *,
    compare: bool = False,
) -> str | None:
    """Normaliza ``column`` em caixa de título. Com ``compare``, devolve a coluna irmã."""
    return normalize_file(path, abbreviations, title_column=column, compare=compare)


def normalize_file(
    path: Path,
    abbreviations: Sequence[str],
    *,
    title_column: str | None = None,
    text_column: str | None = None,
    compare: bool = False,
) -> str | None:
    """Aplica título, texto, ou os dois, numa só gravação.

    Devolve o nome da coluna irmã quando o título é comparado. Sem comparação, devolve None.
    """
    if title_column is None and text_column is None:
        raise ColumnNormalizeError("Informe a coluna de título ou a coluna de texto.")

    path = Path(path)
    if path.suffix.lower() != ".csv":
        raise ColumnNormalizeError(f"O arquivo '{path}' não é CSV.")
    if not path.is_file():
        raise ColumnNormalizeError(f"O arquivo '{path}' não foi encontrado.")

    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise ColumnNormalizeError(f"O arquivo '{path}' não pôde ser lido.") from exc
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ColumnNormalizeError(f"O arquivo '{path}' não é texto UTF-8.") from exc

    delimiter = _header_delimiter(text.splitlines()[0] if text else "")
    rows = _read_rows(text, delimiter)
    named = title_column if title_column is not None else text_column
    if not rows:
        raise ColumnNormalizeError(f"A coluna '{named}' não está no arquivo.")

    header = rows[0]
    title_index = None if title_column is None else _column_index(header, title_column)
    text_index = None if text_column is None else _column_index(header, text_column)
    sibling = None
    if title_column is not None and compare:
        sibling = f"{title_column}_normalized"
        if sibling in header:
            raise ColumnNormalizeError(
                f"A coluna '{sibling}' já existe. O arquivo não foi alterado."
            )

    checked: list[tuple[int, str]] = []
    if title_index is not None and title_column is not None:
        checked.append((title_index, title_column))
    if text_index is not None and text_column is not None and text_index != title_index:
        checked.append((text_index, text_column))
    for line, row in enumerate(rows[1:], start=2):
        for index, column in checked:
            _require_text_cell(row, index, line, column)

    header_out = list(header)
    if title_index is not None and sibling is not None:
        header_out.insert(title_index + 1, sibling)
    keep_title_source = compare and title_index is not None and text_index == title_index
    rewritten = [header_out]
    for row in rows[1:]:
        cells = list(row)
        if text_index is not None and not keep_title_source:
            if title_index == text_index:
                cells[text_index] = title_case_reading(row[text_index], abbreviations)
            else:
                cells[text_index] = plain_text_reading(cells[text_index])
        if title_index is not None and title_index != text_index:
            reading = title_case_reading(row[title_index], abbreviations)
            if compare:
                cells.insert(title_index + 1, reading)
            else:
                cells[title_index] = reading
        elif title_index is not None and compare:
            reading = title_case_reading(row[title_index], abbreviations)
            cells.insert(title_index + 1, reading)
        rewritten.append(cells)

    lineterminator = "\r\n" if b"\r\n" in raw else "\n"
    quote_text = text_index is not None and not keep_title_source
    quote_index = _output_text_index(title_index, text_index, compare) if quote_text else None
    _write_csv(
        path,
        rewritten,
        lineterminator,
        _output_delimiter(delimiter),
        quote_index=quote_index,
    )
    return sibling


def _column_index(header: list[str], column: str) -> int:
    matches = [i for i, name in enumerate(header) if name == column]
    if not matches:
        raise ColumnNormalizeError(f"A coluna '{column}' não está no arquivo.")
    if len(matches) > 1:
        raise ColumnNormalizeError(f"A coluna '{column}' aparece mais de uma vez no cabeçalho.")
    return matches[0]


def _require_text_cell(row: list[str], index: int, line: int, column: str) -> None:
    if index >= len(row) or "\x00" in row[index]:
        raise ColumnNormalizeError(f"A linha {line}, coluna '{column}', não é texto.")


def _read_rows(text: str, delimiter: str) -> list[list[str]]:
    """Lê o CSV. Se uma linha perde coluna, cada linha física vira um registro.

    O último campo fica com os separadores que sobrarem. Uma linha embrulhada
    por aspas, com aspas internas dobradas, perde esse embrulho antes do corte.
    """
    rows = list(csv.reader(io.StringIO(text, newline=""), delimiter=delimiter))
    width = len(rows[0]) if rows else 0
    if rows and all(len(row) >= width for row in rows):
        return rows
    return _read_physical_lines(text, delimiter)


def _read_physical_lines(text: str, delimiter: str) -> list[list[str]]:
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
    """Tira um par de aspas que embrulhava o campo inteiro."""
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
    """Vírgula ou ponto e vírgula, pelo que separa o cabeçalho fora de aspas."""
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


def _abbreviation_is_connective(value: str) -> bool:
    """True quando a abreviação inteira é um conectivo, como ``DA`` para ``da``."""
    return value.casefold() in LEXICO_CONNECTIVOS_FIXOS


def _title_case_gap(gap: str) -> str:
    """Uma palavra é uma sequência de letras. Conectivo fica inteiro em minúscula."""
    parts: list[str] = []
    index = 0
    size = len(gap)
    while index < size:
        if not gap[index].isalpha():
            parts.append(gap[index])
            index += 1
            continue
        end = index + 1
        while end < size and gap[end].isalpha():
            end += 1
        word = gap[index:end].casefold()
        if word in LEXICO_CONNECTIVOS_FIXOS:
            parts.append(word)
        else:
            parts.append(word[:1].upper() + word[1:])
        index = end
    return "".join(parts)


@functools.lru_cache(maxsize=32)
def _compiled(abbreviations: tuple[str, ...]) -> tuple[tuple[re.Pattern[str], str], ...]:
    seen: set[str] = set()
    compiled: list[tuple[re.Pattern[str], str]] = []
    for raw in abbreviations:
        if not isinstance(raw, str) or raw == "" or _abbreviation_is_connective(raw):
            continue
        key = raw.casefold()
        if key in seen:
            continue
        seen.add(key)
        pattern = re.compile(rf"(?<!\w){re.escape(raw)}(?!\w)", re.IGNORECASE)
        compiled.append((pattern, raw))
    return tuple(compiled)


def _abbreviation_spans(text: str, abbreviations: Sequence[str]) -> list[tuple[int, int, str]]:
    """Trechos inteiros, sem sobreposição. O mais longo prevalece; empate fica com o da esquerda."""
    candidates: list[tuple[int, int, str]] = []
    for pattern, canonical in _compiled(tuple(abbreviations)):
        for match in pattern.finditer(text):
            candidates.append((match.start(), match.end(), canonical))
    candidates.sort(key=lambda item: (-(item[1] - item[0]), item[0]))

    chosen: list[tuple[int, int, str]] = []
    for start, end, canonical in candidates:
        if any(start < other_end and end > other_start for other_start, other_end, _ in chosen):
            continue
        chosen.append((start, end, canonical))
    chosen.sort(key=lambda item: item[0])
    return chosen


def _output_delimiter(delimiter: str) -> str:
    """A grade parte na vírgula. O ponto e vírgula de entrada vira vírgula na gravação."""
    if delimiter == ";":
        return ","
    return delimiter


def _output_text_index(
    title_index: int | None, text_index: int | None, compare: bool
) -> int | None:
    """Índice da coluna de texto depois que a irmã de título entra à direita."""
    if text_index is None:
        return None
    if compare and title_index is not None and title_index < text_index:
        return text_index + 1
    return text_index


def _quote_field(value: str, delimiter: str, *, force: bool) -> str:
    """Aspas estruturais em volta do campo. O texto interno não ganha nem perde espaço."""
    if (
        not force
        and delimiter not in value
        and '"' not in value
        and "\n" not in value
        and "\r" not in value
    ):
        return value
    return '"' + value.replace('"', '""') + '"'


def _write_csv(
    path: Path,
    rows: list[list[str]],
    lineterminator: str,
    delimiter: str,
    *,
    quote_index: int | None = None,
) -> None:
    handle_fd, tmp_name = tempfile.mkstemp(prefix=".normalize-", suffix=".csv", dir=path.parent)
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(handle_fd, "w", encoding="utf-8", newline="") as handle:
            for line, row in enumerate(rows):
                fields = [
                    _quote_field(
                        cell,
                        delimiter,
                        force=quote_index is not None and line > 0 and index == quote_index,
                    )
                    for index, cell in enumerate(row)
                ]
                handle.write(delimiter.join(fields) + lineterminator)
        os.replace(tmp_path, path)
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise
