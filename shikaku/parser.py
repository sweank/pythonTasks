"""Parsing and validation for the custom Shikaku text format.

Format:
    <rows> <cols>
    <row 1 tokens>
    <row 2 tokens>
    ...
    <row N tokens>

Tokens:
    .  or 0  -> empty cell
    positive integer -> clue value

Blank lines and lines starting with '#' are ignored.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional

from .errors import InputFormatError
from .limits import validate_2d_dimensions
from .models import Puzzle


EMPTY_TOKENS = {".", "0", "_"}


def _significant_lines(text: str) -> list[str]:
    lines: list[str] = []
    for raw_line in text.replace("\ufeff", "").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        lines.append(line)
    return lines


def _parse_dimensions(line: str) -> tuple[int, int]:
    parts = line.split()
    if len(parts) != 2:
        raise InputFormatError(
            "Первая значимая строка должна содержать два целых числа: <rows> <cols>."
        )
    try:
        rows, cols = (int(parts[0]), int(parts[1]))
    except ValueError as exc:
        raise InputFormatError("Размеры поля должны быть целыми числами.") from exc
    validate_2d_dimensions(rows, cols, InputFormatError)
    return rows, cols


def _parse_token(token: str, row_index: int, col_index: int) -> Optional[int]:
    if token in EMPTY_TOKENS:
        return None
    try:
        value = int(token)
    except ValueError as exc:
        raise InputFormatError(
            f"Недопустимый токен '{token}' в строке {row_index + 2}, столбце {col_index + 1}."
        ) from exc
    if value <= 0:
        raise InputFormatError(
            f"Число в строке {row_index + 2}, столбце {col_index + 1} должно быть положительным."
        )
    return value


def parse_puzzle_text(text: str) -> Puzzle:
    """Parse a puzzle from text and validate its basic structure."""
    lines = _significant_lines(text)
    if not lines:
        raise InputFormatError("Входные данные пусты.")

    rows, cols = _parse_dimensions(lines[0])
    data_lines = lines[1:]

    if len(data_lines) != rows:
        raise InputFormatError(
            f"Ожидалось {rows} строк(и) поля после строки размеров, получено {len(data_lines)}."
        )

    grid: list[tuple[Optional[int], ...]] = []
    for row_index, line in enumerate(data_lines):
        tokens = line.split()
        if len(tokens) != cols:
            raise InputFormatError(
                f"Строка {row_index + 2} должна содержать {cols} значений, получено {len(tokens)}."
            )
        parsed_row = tuple(_parse_token(token, row_index, col_index) for col_index, token in enumerate(tokens))
        grid.append(parsed_row)

    if not any(value is not None for row in grid for value in row):
        raise InputFormatError("Поле должно содержать хотя бы одно число-подсказку.")

    return Puzzle(rows=rows, cols=cols, grid=tuple(grid))


def parse_puzzle_file(path: str | Path) -> Puzzle:
    """Read a puzzle from a file and parse it."""
    file_path = Path(path)
    try:
        content = file_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise InputFormatError(f"Файл не найден: {file_path}") from exc
    except OSError as exc:
        raise InputFormatError(f"Не удалось прочитать файл: {file_path}") from exc
    return parse_puzzle_text(content)
