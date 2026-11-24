"""Leitura em caixa de título de uma coluna de um CSV.

A coluna de origem permanece. A leitura entra na coluna ``<coluna>_normalized``,
imediatamente à direita. Conectivos saem de ``LEXICO_CONNECTIVOS_FIXOS``. A caixa
de uma abreviação sai da primeira ocorrência de ``abreviacao`` em
``docs/assets/seed_lista_abreviacoes.csv``. Aspas duplas da leitura, retas ou curvas,
viram aspas simples.
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
    return (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "assets"
        / "seed_lista_abreviacoes.csv"
    )


def load_abbreviations(path: Path) -> list[str]:
    """Casing de ``abreviacao``, na ordem do arquivo. A primeira grafia de cada texto fica."""
    path = Path(path)
    if not path.is_file():
        raise ColumnNormalizeError(f"A lista de abreviações '{path}' não foi encontrada.")
    try:
        text = path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ColumnNormalizeError(
            f"A lista de abreviações '{path}' não é texto UTF-8."
        ) from exc

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
        if value == "":
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


def normalize_csv(path: Path, column: str, abbreviations: Sequence[str]) -> str:
    """Insere ``<column>_normalized`` à direita de ``column``. Devolve o nome da coluna nova."""
    path = Path(path)
    sibling = f"{column}_normalized"
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
    rows = list(csv.reader(io.StringIO(text, newline=""), delimiter=delimiter))
    if not rows:
        raise ColumnNormalizeError(f"A coluna '{column}' não está no arquivo.")

    header = rows[0]
    matches = [i for i, name in enumerate(header) if name == column]
    if not matches:
        raise ColumnNormalizeError(f"A coluna '{column}' não está no arquivo.")
    if len(matches) > 1:
        raise ColumnNormalizeError(
            f"A coluna '{column}' aparece mais de uma vez no cabeçalho."
        )
    if sibling in header:
        raise ColumnNormalizeError(
            f"A coluna '{sibling}' já existe. O arquivo não foi alterado."
        )

    index = matches[0]
    rewritten = [header[: index + 1] + [sibling] + header[index + 1 :]]
    for line, row in enumerate(rows[1:], start=2):
        if index >= len(row) or "\x00" in row[index]:
            raise ColumnNormalizeError(f"A linha {line}, coluna '{column}', não é texto.")
        reading = title_case_reading(row[index], abbreviations)
        rewritten.append(row[: index + 1] + [reading] + row[index + 1 :])

    lineterminator = "\r\n" if b"\r\n" in raw else "\n"
    _write_csv(path, rewritten, lineterminator, delimiter)
    return sibling


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
        if not isinstance(raw, str) or raw == "":
            continue
        key = raw.casefold()
        if key in seen:
            continue
        seen.add(key)
        pattern = re.compile(rf"(?<!\w){re.escape(raw)}(?!\w)", re.IGNORECASE)
        compiled.append((pattern, raw))
    return tuple(compiled)


def _abbreviation_spans(
    text: str, abbreviations: Sequence[str]
) -> list[tuple[int, int, str]]:
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


def _write_csv(path: Path, rows: list[list[str]], lineterminator: str, delimiter: str) -> None:
    handle_fd, tmp_name = tempfile.mkstemp(prefix=".normalize-", suffix=".csv", dir=path.parent)
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(handle_fd, "w", encoding="utf-8", newline="") as handle:
            csv.writer(handle, delimiter=delimiter, lineterminator=lineterminator).writerows(rows)
        os.replace(tmp_path, path)
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise
