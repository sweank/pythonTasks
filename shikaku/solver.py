"""Backtracking Shikaku solver."""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, List, Optional

from .models import Clue, Position, Puzzle, RectangleRegion, Solution


def _factor_pairs(area: int) -> list[tuple[int, int]]:
    pairs: list[tuple[int, int]] = []
    for height in range(1, int(area**0.5) + 1):
        if area % height == 0:
            width = area // height
            pairs.append((height, width))
            if height != width:
                pairs.append((width, height))
    return pairs


def generate_candidates(puzzle: Puzzle) -> dict[Clue, tuple[RectangleRegion, ...]]:
    """Generate every rectangle allowed for each clue."""
    clue_positions = {clue.position for clue in puzzle.clues}
    result: dict[Clue, tuple[RectangleRegion, ...]] = {}

    for clue in puzzle.clues:
        candidates: list[RectangleRegion] = []
        for height, width in _factor_pairs(clue.value):
            for top in range(clue.position.row - height + 1, clue.position.row + 1):
                bottom = top + height - 1
                if top < 0 or bottom >= puzzle.rows:
                    continue
                for left in range(clue.position.col - width + 1, clue.position.col + 1):
                    right = left + width - 1
                    if left < 0 or right >= puzzle.cols:
                        continue
                    region = RectangleRegion(top, left, bottom, right, clue)
                    other_clue_inside = any(
                        pos != clue.position and region.contains(pos) for pos in clue_positions
                    )
                    if other_clue_inside:
                        continue
                    candidates.append(region)
        unique_candidates = tuple(dict.fromkeys(candidates))
        result[clue] = unique_candidates
    return result


class Solver:
    """Solve a Shikaku puzzle using candidate generation and DFS with pruning."""

    def __init__(self, puzzle: Puzzle) -> None:
        self.puzzle = puzzle
        self.candidates = generate_candidates(puzzle)
        self.unassigned_clues = tuple(sorted(puzzle.clues, key=lambda clue: (clue.position.row, clue.position.col)))
        self._cell_to_regions = self._build_cell_index()

    def _build_cell_index(self) -> dict[Position, tuple[RectangleRegion, ...]]:
        index: dict[Position, list[RectangleRegion]] = defaultdict(list)
        for regions in self.candidates.values():
            for region in regions:
                for cell in region.cells():
                    index[cell].append(region)
        return {cell: tuple(regions) for cell, regions in index.items()}

    def solve(self) -> Optional[Solution]:
        if self.puzzle.total_clue_area != self.puzzle.board_area:
            return None
        if any(not regions for regions in self.candidates.values()):
            return None

        chosen = self._search(assigned={}, occupied=set())
        if chosen is None:
            return None

        ordered_regions = tuple(
            chosen[clue]
            for clue in sorted(chosen, key=lambda current: (current.position.row, current.position.col))
        )
        return Solution(self.puzzle, ordered_regions)

    def _search(
        self,
        assigned: dict[Clue, RectangleRegion],
        occupied: set[Position],
    ) -> Optional[dict[Clue, RectangleRegion]]:
        if len(assigned) == len(self.unassigned_clues):
            return dict(assigned)

        clue = self._select_next_clue(assigned, occupied)
        if clue is None:
            return None

        for region in self.candidates[clue]:
            region_cells = tuple(region.cells())
            if any(cell in occupied for cell in region_cells):
                continue

            assigned[clue] = region
            occupied.update(region_cells)

            if self._is_state_feasible(assigned, occupied):
                solution = self._search(assigned, occupied)
                if solution is not None:
                    return solution

            for cell in region_cells:
                occupied.remove(cell)
            assigned.pop(clue)

        return None

    def _select_next_clue(
        self,
        assigned: dict[Clue, RectangleRegion],
        occupied: set[Position],
    ) -> Optional[Clue]:
        best_clue: Optional[Clue] = None
        best_count: Optional[int] = None

        for clue in self.unassigned_clues:
            if clue in assigned:
                continue
            count = 0
            for region in self.candidates[clue]:
                if all(cell not in occupied for cell in region.cells()):
                    count += 1
            if count == 0:
                return clue
            if best_count is None or count < best_count:
                best_count = count
                best_clue = clue
        return best_clue

    def _is_state_feasible(self, assigned: dict[Clue, RectangleRegion], occupied: set[Position]) -> bool:
        for clue in self.unassigned_clues:
            if clue in assigned:
                continue
            if not any(all(cell not in occupied for cell in region.cells()) for region in self.candidates[clue]):
                return False

        for row in range(self.puzzle.rows):
            for col in range(self.puzzle.cols):
                cell = Position(row, col)
                if cell in occupied:
                    continue
                if not any(
                    candidate.clue not in assigned
                    and all(region_cell not in occupied for region_cell in candidate.cells())
                    for candidate in self._cell_to_regions.get(cell, ())
                ):
                    return False
        return True


def solve_puzzle(puzzle: Puzzle) -> Optional[Solution]:
    """Solve a puzzle and return a Solution if one exists."""
    return Solver(puzzle).solve()
