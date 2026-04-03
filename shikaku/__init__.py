"""Shikaku puzzle solver package."""

from .models import Puzzle, RectangleRegion, Solution
from .models3d import Puzzle3D, CuboidRegion, Solution3D
from .parser import parse_puzzle_file, parse_puzzle_text
from .parser3d import parse_puzzle_3d_file, parse_puzzle_3d_text
from .solver import generate_candidates, solve_puzzle
from .solver3d import generate_candidates_3d, solve_puzzle_3d
from .verifier import validate_solution
from .verifier3d import validate_solution_3d

__all__ = [
    "Puzzle",
    "RectangleRegion",
    "Solution",
    "Puzzle3D",
    "CuboidRegion",
    "Solution3D",
    "parse_puzzle_file",
    "parse_puzzle_text",
    "parse_puzzle_3d_file",
    "parse_puzzle_3d_text",
    "generate_candidates",
    "generate_candidates_3d",
    "solve_puzzle",
    "solve_puzzle_3d",
    "validate_solution",
    "validate_solution_3d",
]
