"""Validation helpers for 3D Shikaku solutions."""

from __future__ import annotations

from .errors import SolutionValidationError
from .models3d import Position3D, Solution3D


def validate_solution_3d(solution: Solution3D) -> None:
    puzzle = solution.puzzle
    covered_by: dict[Position3D, int] = {}

    if len(solution.regions) != len(puzzle.clues):
        raise SolutionValidationError("Количество 3D-областей не совпадает с количеством чисел.")

    for index, region in enumerate(solution.regions):
        cells = list(region.cells())
        if region.volume != region.clue.value:
            raise SolutionValidationError(
                f"3D-область для числа {region.clue.value} имеет объём {region.volume}, ожидалось {region.clue.value}."
            )

        clues_inside = 0
        for clue in puzzle.clues:
            if region.contains(clue.position):
                clues_inside += 1
        if clues_inside != 1:
            raise SolutionValidationError("Каждая 3D-область должна содержать ровно одно число.")

        for cell in cells:
            if cell in covered_by:
                raise SolutionValidationError(
                    f"Ячейка {cell.to_human()} покрыта более одной областью."
                )
            covered_by[cell] = index

    expected_cells = {
        Position3D(layer, row, col)
        for layer in range(puzzle.depth)
        for row in range(puzzle.rows)
        for col in range(puzzle.cols)
    }
    if set(covered_by) != expected_cells:
        missing = sorted(expected_cells - set(covered_by))
        raise SolutionValidationError(
            f"Решение покрывает не все 3D-ячейки. Пример непокрытой ячейки: {missing[0].to_human()}."
        )
