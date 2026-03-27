"""Formatting helpers for human-readable CLI output."""

from __future__ import annotations

from .models import Solution


def _labels(count: int) -> list[str]:
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    labels: list[str] = []
    current = 0
    while len(labels) < count:
        number = current
        chunk = ""
        while True:
            number, remainder = divmod(number, len(alphabet))
            chunk = alphabet[remainder] + chunk
            if number == 0:
                break
            number -= 1
        labels.append(chunk)
        current += 1
    return labels


def format_solution(solution: Solution) -> str:
    """Return a multi-line solved puzzle representation."""
    labels = _labels(len(solution.regions))
    board = [["." for _ in range(solution.puzzle.cols)] for _ in range(solution.puzzle.rows)]

    region_lines: list[str] = []
    for label, region in zip(labels, solution.regions):
        for cell in region.cells():
            board[cell.row][cell.col] = label
        region_lines.append(region.label_description(label))

    cell_width = max(max(len(cell) for row in board for cell in row), 1)
    board_lines = [" ".join(cell.rjust(cell_width) for cell in row) for row in board]

    return "\n".join(
        [
            "STATUS: SOLVED",
            "BOARD:",
            *board_lines,
            "REGIONS:",
            *region_lines,
        ]
    )


def format_no_solution() -> str:
    """Return text for an unsolved puzzle."""
    return "STATUS: NO_SOLUTION"
