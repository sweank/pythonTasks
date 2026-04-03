"""Formatting helpers for 3D Shikaku solutions and puzzles."""

from __future__ import annotations

from .formatter import _labels
from .models3d import Puzzle3D, Solution3D


def format_solution_3d(solution: Solution3D) -> str:
    labels = _labels(len(solution.regions))
    boards = [
        [["." for _ in range(solution.puzzle.cols)] for _ in range(solution.puzzle.rows)]
        for _ in range(solution.puzzle.depth)
    ]

    region_lines: list[str] = []
    for label, region in zip(labels, solution.regions):
        for cell in region.cells():
            boards[cell.layer][cell.row][cell.col] = label
        region_lines.append(region.label_description(label))

    cell_width = max(max(len(cell) for board in boards for row in board for cell in row), 1)
    lines = ["STATUS: SOLVED_3D", "BOARD:"]
    for layer_index, board in enumerate(boards):
        lines.append(f"Layer {layer_index + 1}:")
        lines.extend(" ".join(cell.rjust(cell_width) for cell in row) for row in board)
    lines.extend(["REGIONS:", *region_lines])
    return "\n".join(lines)


def format_puzzle_3d(puzzle: Puzzle3D) -> str:
    lines = [f"{puzzle.depth} {puzzle.rows} {puzzle.cols}"]
    for layer_index, layer in enumerate(puzzle.grid):
        for row in layer:
            lines.append(" ".join("." if value is None else str(value) for value in row))
        if layer_index != puzzle.depth - 1:
            lines.append("---")
    return "\n".join(lines)
