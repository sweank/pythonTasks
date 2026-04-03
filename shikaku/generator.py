"""Very small puzzle generators for 2D and 3D Shikaku.

The generator deliberately keeps things simple:
- create a valid random partition by splitting the board/cuboid,
- place one clue in each region,
- return a puzzle that is guaranteed to have at least one solution.
"""

from __future__ import annotations

import random

from .formatter3d import format_puzzle_3d
from .limits import validate_2d_dimensions, validate_3d_dimensions
from .models import Puzzle
from .models3d import Puzzle3D


Rect = tuple[int, int, int, int]
Box = tuple[int, int, int, int, int, int]


def _rect_area(rect: Rect) -> int:
    top, left, bottom, right = rect
    return (bottom - top + 1) * (right - left + 1)


def _box_volume(box: Box) -> int:
    front, top, left, back, bottom, right = box
    return (back - front + 1) * (bottom - top + 1) * (right - left + 1)


def _rect_splits(rect: Rect) -> list[tuple[Rect, Rect]]:
    top, left, bottom, right = rect
    splits: list[tuple[Rect, Rect]] = []
    if bottom > top:
        for cut in range(top, bottom):
            splits.append(((top, left, cut, right), (cut + 1, left, bottom, right)))
    if right > left:
        for cut in range(left, right):
            splits.append(((top, left, bottom, cut), (top, cut + 1, bottom, right)))
    return splits


def _box_splits(box: Box) -> list[tuple[Box, Box]]:
    front, top, left, back, bottom, right = box
    splits: list[tuple[Box, Box]] = []
    if back > front:
        for cut in range(front, back):
            splits.append(((front, top, left, cut, bottom, right), (cut + 1, top, left, back, bottom, right)))
    if bottom > top:
        for cut in range(top, bottom):
            splits.append(((front, top, left, back, cut, right), (front, cut + 1, left, back, bottom, right)))
    if right > left:
        for cut in range(left, right):
            splits.append(((front, top, left, back, bottom, cut), (front, top, cut + 1, back, bottom, right)))
    return splits


def generate_puzzle(rows: int, cols: int, seed: int | None = None, max_regions: int | None = None) -> Puzzle:
    validate_2d_dimensions(rows, cols)

    rng = random.Random(seed)
    target = max_regions if max_regions is not None else max(1, min(rows * cols, max(2, (rows * cols) // 2)))
    regions: list[Rect] = [(0, 0, rows - 1, cols - 1)]

    while len(regions) < target:
        splittable = [index for index, rect in enumerate(regions) if _rect_splits(rect)]
        if not splittable:
            break
        index = rng.choice(splittable)
        rect = regions.pop(index)
        first, second = rng.choice(_rect_splits(rect))
        regions.extend([first, second])

    grid = [[None for _ in range(cols)] for _ in range(rows)]
    for rect in regions:
        top, left, bottom, right = rect
        clue_row = rng.randint(top, bottom)
        clue_col = rng.randint(left, right)
        grid[clue_row][clue_col] = _rect_area(rect)

    return Puzzle(rows=rows, cols=cols, grid=tuple(tuple(row) for row in grid))


def generate_puzzle_3d(
    depth: int,
    rows: int,
    cols: int,
    seed: int | None = None,
    max_regions: int | None = None,
) -> Puzzle3D:
    validate_3d_dimensions(depth, rows, cols)

    rng = random.Random(seed)
    volume = depth * rows * cols
    target = max_regions if max_regions is not None else max(1, min(volume, max(2, volume // 2)))
    regions: list[Box] = [(0, 0, 0, depth - 1, rows - 1, cols - 1)]

    while len(regions) < target:
        splittable = [index for index, box in enumerate(regions) if _box_splits(box)]
        if not splittable:
            break
        index = rng.choice(splittable)
        box = regions.pop(index)
        first, second = rng.choice(_box_splits(box))
        regions.extend([first, second])

    grid = [[[None for _ in range(cols)] for _ in range(rows)] for _ in range(depth)]
    for box in regions:
        front, top, left, back, bottom, right = box
        clue_layer = rng.randint(front, back)
        clue_row = rng.randint(top, bottom)
        clue_col = rng.randint(left, right)
        grid[clue_layer][clue_row][clue_col] = _box_volume(box)

    return Puzzle3D(
        depth=depth,
        rows=rows,
        cols=cols,
        grid=tuple(tuple(tuple(row) for row in layer) for layer in grid),
    )


def format_puzzle(puzzle: Puzzle) -> str:
    lines = [f"{puzzle.rows} {puzzle.cols}"]
    for row in puzzle.grid:
        lines.append(" ".join("." if value is None else str(value) for value in row))
    return "\n".join(lines)


__all__ = [
    "generate_puzzle",
    "generate_puzzle_3d",
    "format_puzzle",
    "format_puzzle_3d",
]
