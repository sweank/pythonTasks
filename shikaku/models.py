"""Core data models used by the Shikaku solver."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional


@dataclass(frozen=True, order=True)
class Position:
    """A zero-based grid position."""

    row: int
    col: int

    def to_human(self) -> str:
        """Return a one-based human-readable coordinate."""
        return f"({self.row + 1}, {self.col + 1})"


@dataclass(frozen=True)
class Clue:
    """A numeric clue placed on the puzzle grid."""

    position: Position
    value: int


@dataclass(frozen=True)
class RectangleRegion:
    """A rectangular region in the final Shikaku partition."""

    top: int
    left: int
    bottom: int
    right: int
    clue: Clue

    @property
    def width(self) -> int:
        return self.right - self.left + 1

    @property
    def height(self) -> int:
        return self.bottom - self.top + 1

    @property
    def area(self) -> int:
        return self.width * self.height

    def cells(self) -> Iterable[Position]:
        for row in range(self.top, self.bottom + 1):
            for col in range(self.left, self.right + 1):
                yield Position(row, col)

    def contains(self, pos: Position) -> bool:
        return self.top <= pos.row <= self.bottom and self.left <= pos.col <= self.right

    def overlaps(self, other: "RectangleRegion") -> bool:
        return not (
            self.right < other.left
            or other.right < self.left
            or self.bottom < other.top
            or other.bottom < self.top
        )

    def label_description(self, label: str) -> str:
        return (
            f"{label}: rows {self.top + 1}-{self.bottom + 1}, cols {self.left + 1}-{self.right + 1}, "
            f"area {self.area}, clue {self.clue.value} at {self.clue.position.to_human()}"
        )


@dataclass(frozen=True)
class Puzzle:
    """A Shikaku puzzle with immutable grid data."""

    rows: int
    cols: int
    grid: tuple[tuple[Optional[int], ...], ...]

    def __post_init__(self) -> None:
        if self.rows <= 0 or self.cols <= 0:
            raise ValueError("Puzzle dimensions must be positive")
        if len(self.grid) != self.rows:
            raise ValueError("Grid row count does not match puzzle height")
        for row in self.grid:
            if len(row) != self.cols:
                raise ValueError("Grid column count does not match puzzle width")

    @property
    def clues(self) -> tuple[Clue, ...]:
        result: list[Clue] = []
        for r, row in enumerate(self.grid):
            for c, value in enumerate(row):
                if value is not None:
                    result.append(Clue(Position(r, c), value))
        return tuple(result)

    @property
    def total_clue_area(self) -> int:
        return sum(clue.value for clue in self.clues)

    @property
    def board_area(self) -> int:
        return self.rows * self.cols


@dataclass(frozen=True)
class Solution:
    """A complete Shikaku solution."""

    puzzle: Puzzle
    regions: tuple[RectangleRegion, ...]
