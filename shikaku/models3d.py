"""3D data models used by the extended Shikaku solver."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional


@dataclass(frozen=True, order=True)
class Position3D:
    """A zero-based position in a 3D Shikaku grid."""

    layer: int
    row: int
    col: int

    def to_human(self) -> str:
        return f"(layer {self.layer + 1}, row {self.row + 1}, col {self.col + 1})"


@dataclass(frozen=True)
class Clue3D:
    """A numeric clue placed inside a 3D puzzle."""

    position: Position3D
    value: int


@dataclass(frozen=True)
class CuboidRegion:
    """A rectangular cuboid used in a 3D Shikaku partition."""

    front: int
    top: int
    left: int
    back: int
    bottom: int
    right: int
    clue: Clue3D

    @property
    def depth(self) -> int:
        return self.back - self.front + 1

    @property
    def height(self) -> int:
        return self.bottom - self.top + 1

    @property
    def width(self) -> int:
        return self.right - self.left + 1

    @property
    def volume(self) -> int:
        return self.depth * self.height * self.width

    def cells(self) -> Iterable[Position3D]:
        for layer in range(self.front, self.back + 1):
            for row in range(self.top, self.bottom + 1):
                for col in range(self.left, self.right + 1):
                    yield Position3D(layer, row, col)

    def contains(self, pos: Position3D) -> bool:
        return (
            self.front <= pos.layer <= self.back
            and self.top <= pos.row <= self.bottom
            and self.left <= pos.col <= self.right
        )

    def overlaps(self, other: "CuboidRegion") -> bool:
        return not (
            self.right < other.left
            or other.right < self.left
            or self.bottom < other.top
            or other.bottom < self.top
            or self.back < other.front
            or other.back < self.front
        )

    def label_description(self, label: str) -> str:
        return (
            f"{label}: layers {self.front + 1}-{self.back + 1}, rows {self.top + 1}-{self.bottom + 1}, "
            f"cols {self.left + 1}-{self.right + 1}, volume {self.volume}, "
            f"clue {self.clue.value} at {self.clue.position.to_human()}"
        )


@dataclass(frozen=True)
class Puzzle3D:
    """An immutable 3D Shikaku puzzle."""

    depth: int
    rows: int
    cols: int
    grid: tuple[tuple[tuple[Optional[int], ...], ...], ...]

    def __post_init__(self) -> None:
        if self.depth <= 0 or self.rows <= 0 or self.cols <= 0:
            raise ValueError("Puzzle dimensions must be positive")
        if len(self.grid) != self.depth:
            raise ValueError("Grid layer count does not match puzzle depth")
        for layer in self.grid:
            if len(layer) != self.rows:
                raise ValueError("Grid row count does not match puzzle height")
            for row in layer:
                if len(row) != self.cols:
                    raise ValueError("Grid column count does not match puzzle width")

    @property
    def clues(self) -> tuple[Clue3D, ...]:
        result: list[Clue3D] = []
        for layer_index, layer in enumerate(self.grid):
            for row_index, row in enumerate(layer):
                for col_index, value in enumerate(row):
                    if value is not None:
                        result.append(Clue3D(Position3D(layer_index, row_index, col_index), value))
        return tuple(result)

    @property
    def total_clue_volume(self) -> int:
        return sum(clue.value for clue in self.clues)

    @property
    def board_volume(self) -> int:
        return self.depth * self.rows * self.cols


@dataclass(frozen=True)
class Solution3D:
    """A complete solution for a 3D Shikaku puzzle."""

    puzzle: Puzzle3D
    regions: tuple[CuboidRegion, ...]
