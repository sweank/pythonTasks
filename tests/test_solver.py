from __future__ import annotations

from shikaku.parser import parse_puzzle_text
from shikaku.solver import generate_candidates, solve_puzzle
from shikaku.verifier import validate_solution


def test_generate_candidates_for_simple_2x2() -> None:
    puzzle = parse_puzzle_text(
        """
        2 2
        2 2
        . .
        """
    )

    candidates = generate_candidates(puzzle)
    clue_values = sorted((clue.value, len(regions)) for clue, regions in candidates.items())
    assert clue_values == [(2, 1), (2, 1)]


def test_solve_simple_2x2() -> None:
    puzzle = parse_puzzle_text(
        """
        2 2
        2 2
        . .
        """
    )

    solution = solve_puzzle(puzzle)
    assert solution is not None
    validate_solution(solution)
    assert len(solution.regions) == 2


def test_solve_rows_3x3() -> None:
    puzzle = parse_puzzle_text(
        """
        3 3
        3 . .
        . 3 .
        . . 3
        """
    )

    solution = solve_puzzle(puzzle)
    assert solution is not None
    validate_solution(solution)
    assert [region.area for region in solution.regions] == [3, 3, 3]


def test_unsolvable_when_total_area_does_not_match_board() -> None:
    puzzle = parse_puzzle_text(
        """
        2 2
        2 .
        . .
        """
    )
    assert solve_puzzle(puzzle) is None


def test_unsolvable_when_candidate_set_is_empty() -> None:
    puzzle = parse_puzzle_text(
        """
        2 2
        3 .
        . 1
        """
    )
    assert solve_puzzle(puzzle) is None
