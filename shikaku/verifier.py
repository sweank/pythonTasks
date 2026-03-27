"""Verification helpers for Shikaku solutions."""

from __future__ import annotations

from .errors import SolutionValidationError
from .models import Position, Solution


def validate_solution(solution: Solution) -> None:
    """Raise SolutionValidationError if the solution is invalid."""
    puzzle = solution.puzzle
    covered_by: dict[Position, int] = {}

    if len(solution.regions) != len(puzzle.clues):
        raise SolutionValidationError("Количество областей не совпадает с количеством чисел.")

    for index, region in enumerate(solution.regions):
        cells = list(region.cells())
        if region.area != region.clue.value:
            raise SolutionValidationError(
                f"Область для числа {region.clue.value} имеет площадь {region.area}, ожидалось {region.clue.value}."
            )

        clues_inside = 0
        for clue in puzzle.clues:
            if region.contains(clue.position):
                clues_inside += 1
        if clues_inside != 1:
            raise SolutionValidationError("Каждая область должна содержать ровно одно число.")

        for cell in cells:
            if cell in covered_by:
                raise SolutionValidationError(
                    f"Клетка {cell.to_human()} покрыта более одной областью."
                )
            covered_by[cell] = index

    expected_cells = {Position(row, col) for row in range(puzzle.rows) for col in range(puzzle.cols)}
    if set(covered_by) != expected_cells:
        missing = sorted(expected_cells - set(covered_by))
        raise SolutionValidationError(
            f"Решение покрывает не все клетки. Пример непокрытой клетки: {missing[0].to_human()}."
        )
