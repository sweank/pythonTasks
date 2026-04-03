from __future__ import annotations

import pytest

from shikaku.errors import InputFormatError
from shikaku.parser3d import parse_puzzle_3d_text


def test_parse_valid_3d_puzzle() -> None:
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

    assert puzzle.depth == 2
    assert puzzle.rows == 2
    assert puzzle.cols == 2
    assert puzzle.grid[0][0][0] == 4
    assert puzzle.grid[1][0][0] == 4


@pytest.mark.parametrize(
    "text, message_part",
    [
        ("", "пусты"),
        ("2 2\n1 .\n. .", "три целых числа"),
        ("0 2 2\n1 .\n. .", "положительными"),
        ("2 2 2\n4 .\n. .", "Ожидалось 4 строк"),
        ("2 2 2\n4 . .\n. .\n4 .\n. .", "должна содержать 2 значений"),
        ("2 1 1\n.\n.", "хотя бы одно число"),
    ],
)
def test_parse_invalid_3d_input(text: str, message_part: str) -> None:
    with pytest.raises(InputFormatError, match=message_part):
        parse_puzzle_3d_text(text)
