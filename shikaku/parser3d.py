"""Parsing and validation for a simple 3D Shikaku text format.

Format:
    <depth> <rows> <cols>
    <layer 1 row 1>
    ...
    <layer 1 row N>
    ---
    <layer 2 row 1>
    ...

Blank lines and comments starting with '#' are ignored.
The separator line '---' between layers is optional.
Empty cells may be written as '.', '0' or '_'.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from .errors import InputFormatError
from .limits import validate_3d_dimensions
from .parser import EMPTY_TOKENS, _parse_token
from .models3d import Puzzle3D


SEPARATOR = "---"


def _significant_lines_3d(text: str) -> list[str]:
    lines: list[str] = []
    for raw_line in text.replace("\ufeff", "").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line == SEPARATOR:
            continue
        lines.append(line)
    return lines


def _parse_dimensions(line: str) -> tuple[int, int, int]:
    parts = line.split()
    if len(parts) != 3:
        raise InputFormatError(
            "Первая значимая строка 3D-формата должна содержать три целых числа: <depth> <rows> <cols>."
        )
    try:
        depth, rows, cols = (int(parts[0]), int(parts[1]), int(parts[2]))
    except ValueError as exc:
        raise InputFormatError("Размеры 3D-поля должны быть целыми числами.") from exc
    validate_3d_dimensions(depth, rows, cols, InputFormatError)
    return depth, rows, cols


def parse_puzzle_3d_text(text: str) -> Puzzle3D:
    lines = _significant_lines_3d(text)
    if not lines:
        raise InputFormatError("Входные данные 3D-задачи пусты.")

    depth, rows, cols = _parse_dimensions(lines[0])
    data_lines = lines[1:]
    expected = depth * rows
    if len(data_lines) != expected:
        raise InputFormatError(
            f"Ожидалось {expected} строк данных для 3D-поля, получено {len(data_lines)}."
        )

    layers: list[tuple[tuple[Optional[int], ...], ...]] = []
    index = 0
    for layer_index in range(depth):
        current_rows: list[tuple[Optional[int], ...]] = []
        for row_index in range(rows):
            line = data_lines[index]
            index += 1
            tokens = line.split()
            if len(tokens) != cols:
                raise InputFormatError(
                    f"Строка слоя {layer_index + 1}, строка {row_index + 1} должна содержать {cols} значений, получено {len(tokens)}."
                )
            current_rows.append(
                tuple(_parse_token(token, row_index, col_index) for col_index, token in enumerate(tokens))
            )
        layers.append(tuple(current_rows))

    if not any(value is not None for layer in layers for row in layer for value in row):
        raise InputFormatError("3D-поле должно содержать хотя бы одно число-подсказку.")

    return Puzzle3D(depth=depth, rows=rows, cols=cols, grid=tuple(layers))


def parse_puzzle_3d_file(path: str | Path) -> Puzzle3D:
    file_path = Path(path)
    try:
        content = file_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise InputFormatError(f"Файл не найден: {file_path}") from exc
    except OSError as exc:
        raise InputFormatError(f"Не удалось прочитать файл: {file_path}") from exc
    return parse_puzzle_3d_text(content)
