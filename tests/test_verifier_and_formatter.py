from __future__ import annotations

import pytest

from shikaku.errors import SolutionValidationError
from shikaku.formatter import format_no_solution, format_solution
from shikaku.models import Clue, Position, Puzzle, RectangleRegion, Solution
from shikaku.parser import parse_puzzle_text
from shikaku.solver import solve_puzzle
from shikaku.verifier import validate_solution


def test_formatter_contains_sections() -> None:
    puzzle = parse_puzzle_text(
        """
        2 2
        2 2
        . .
        """
    )
    solution = solve_puzzle(puzzle)
    assert solution is not None

    rendered = format_solution(solution)
    assert "STATUS: SOLVED" in rendered
    assert "BOARD:" in rendered
    assert "REGIONS:" in rendered
    assert format_no_solution() == "STATUS: NO_SOLUTION"


def test_verifier_rejects_overlapping_regions() -> None:
    puzzle = Puzzle(
        rows=3,
        cols=2,
        grid=((2, None), (None, None), (2, None)),
    )
    clue_a, clue_b = puzzle.clues
    overlapping_solution = Solution(
        puzzle,
        (
            RectangleRegion(0, 0, 1, 0, clue_a),
            RectangleRegion(1, 0, 2, 0, clue_b),
        ),
    )

    with pytest.raises(SolutionValidationError, match="более одной областью"):
        validate_solution(overlapping_solution)


def test_verifier_rejects_wrong_area() -> None:
    puzzle = Puzzle(
        rows=1,
        cols=2,
        grid=((2, None),),
    )
    clue = puzzle.clues[0]
    invalid_solution = Solution(puzzle, (RectangleRegion(0, 0, 0, 0, clue),))

    with pytest.raises(SolutionValidationError, match="имеет площадь"):
        validate_solution(invalid_solution)
