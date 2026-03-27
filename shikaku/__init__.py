"""Shikaku puzzle solver package."""

from .models import Puzzle, RectangleRegion, Solution
from .parser import parse_puzzle_file, parse_puzzle_text
from .solver import generate_candidates, solve_puzzle
from .verifier import validate_solution

__all__ = [
    "Puzzle",
    "RectangleRegion",
    "Solution",
    "parse_puzzle_file",
    "parse_puzzle_text",
    "generate_candidates",
    "solve_puzzle",
    "validate_solution",
]
