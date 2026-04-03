from __future__ import annotations

from shikaku.generator import generate_puzzle, generate_puzzle_3d
from shikaku.solver import solve_puzzle
from shikaku.solver3d import solve_puzzle_3d
from shikaku.verifier import validate_solution
from shikaku.verifier3d import validate_solution_3d


def test_generate_2d_puzzle_is_solvable() -> None:
    puzzle = generate_puzzle(3, 4, seed=123)
    solution = solve_puzzle(puzzle)
    assert solution is not None
    validate_solution(solution)


def test_generate_3d_puzzle_is_solvable() -> None:
    puzzle = generate_puzzle_3d(2, 2, 3, seed=123)
    solution = solve_puzzle_3d(puzzle)
    assert solution is not None
    validate_solution_3d(solution)
