from __future__ import annotations

from shikaku.parser3d import parse_puzzle_3d_text
from shikaku.solver3d import generate_candidates_3d, solve_puzzle_3d
from shikaku.verifier3d import validate_solution_3d


def test_generate_candidates_for_simple_3d() -> None:
    puzzle = parse_puzzle_3d_text(
        """
        2 2 2
        4 .
        . .
        ---
        4 .
        . .
        """
    )

    candidates = generate_candidates_3d(puzzle)
    clue_values = sorted((clue.value, len(regions)) for clue, regions in candidates.items())
    assert clue_values == [(4, 1), (4, 1)]


def test_solve_simple_3d() -> None:
    puzzle = parse_puzzle_3d_text(
        """
        2 2 2
        4 .
        . .
        ---
        4 .
        . .
        """
    )

    solution = solve_puzzle_3d(puzzle)
    assert solution is not None
    validate_solution_3d(solution)
    assert len(solution.regions) == 2


def test_unsolvable_3d_when_total_volume_mismatch() -> None:
    puzzle = parse_puzzle_3d_text(
        """
        2 2 2
        3 .
        . .
        ---
        4 .
        . .
        """
    )
    assert solve_puzzle_3d(puzzle) is None
