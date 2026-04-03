"""Backtracking solver for the minimal 3D Shikaku extension."""

from __future__ import annotations

from collections import defaultdict
from typing import Optional

from .models3d import Clue3D, CuboidRegion, Position3D, Puzzle3D, Solution3D


def _factor_triples(volume: int) -> list[tuple[int, int, int]]:
    triples: set[tuple[int, int, int]] = set()
    for depth in range(1, volume + 1):
        if volume % depth != 0:
            continue
        area = volume // depth
        for height in range(1, area + 1):
            if area % height != 0:
                continue
            width = area // height
            triples.add((depth, height, width))
    return sorted(triples)


def generate_candidates_3d(puzzle: Puzzle3D) -> dict[Clue3D, tuple[CuboidRegion, ...]]:
    clue_positions = {clue.position for clue in puzzle.clues}
    result: dict[Clue3D, tuple[CuboidRegion, ...]] = {}

    for clue in puzzle.clues:
        candidates: list[CuboidRegion] = []
        for depth_size, height, width in _factor_triples(clue.value):
            for front in range(clue.position.layer - depth_size + 1, clue.position.layer + 1):
                back = front + depth_size - 1
                if front < 0 or back >= puzzle.depth:
                    continue
                for top in range(clue.position.row - height + 1, clue.position.row + 1):
                    bottom = top + height - 1
                    if top < 0 or bottom >= puzzle.rows:
                        continue
                    for left in range(clue.position.col - width + 1, clue.position.col + 1):
                        right = left + width - 1
                        if left < 0 or right >= puzzle.cols:
                            continue
                        region = CuboidRegion(front, top, left, back, bottom, right, clue)
                        other_clue_inside = any(
                            pos != clue.position and region.contains(pos) for pos in clue_positions
                        )
                        if other_clue_inside:
                            continue
                        candidates.append(region)
        result[clue] = tuple(dict.fromkeys(candidates))
    return result


class Solver3D:
    """Solve 3D Shikaku using DFS with pruning."""

    def __init__(self, puzzle: Puzzle3D) -> None:
        self.puzzle = puzzle
        self.candidates = generate_candidates_3d(puzzle)
        self.unassigned_clues = tuple(
            sorted(puzzle.clues, key=lambda clue: (clue.position.layer, clue.position.row, clue.position.col))
        )
        self._cell_to_regions = self._build_cell_index()

    def _build_cell_index(self) -> dict[Position3D, tuple[CuboidRegion, ...]]:
        index: dict[Position3D, list[CuboidRegion]] = defaultdict(list)
        for regions in self.candidates.values():
            for region in regions:
                for cell in region.cells():
                    index[cell].append(region)
        return {cell: tuple(regions) for cell, regions in index.items()}

    def solve(self) -> Optional[Solution3D]:
        if self.puzzle.total_clue_volume != self.puzzle.board_volume:
            return None
        if any(not regions for regions in self.candidates.values()):
            return None

        chosen = self._search(assigned={}, occupied=set())
        if chosen is None:
            return None

        ordered_regions = tuple(
            chosen[clue]
            for clue in sorted(chosen, key=lambda current: (current.position.layer, current.position.row, current.position.col))
        )
        return Solution3D(self.puzzle, ordered_regions)

    def _search(
        self,
        assigned: dict[Clue3D, CuboidRegion],
        occupied: set[Position3D],
    ) -> Optional[dict[Clue3D, CuboidRegion]]:
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
        assigned: dict[Clue3D, CuboidRegion],
        occupied: set[Position3D],
    ) -> Optional[Clue3D]:
        best_clue: Optional[Clue3D] = None
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

    def _is_state_feasible(
        self,
        assigned: dict[Clue3D, CuboidRegion],
        occupied: set[Position3D],
    ) -> bool:
        for clue in self.unassigned_clues:
            if clue in assigned:
                continue
            if not any(all(cell not in occupied for cell in region.cells()) for region in self.candidates[clue]):
                return False

        for layer in range(self.puzzle.depth):
            for row in range(self.puzzle.rows):
                for col in range(self.puzzle.cols):
                    cell = Position3D(layer, row, col)
                    if cell in occupied:
                        continue
                    if not any(
                        candidate.clue not in assigned
                        and all(region_cell not in occupied for region_cell in candidate.cells())
                        for candidate in self._cell_to_regions.get(cell, ())
                    ):
                        return False
        return True


def solve_puzzle_3d(puzzle: Puzzle3D) -> Optional[Solution3D]:
    return Solver3D(puzzle).solve()
