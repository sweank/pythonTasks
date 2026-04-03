from __future__ import annotations

import pytest

from shikaku.errors import InputFormatError
from shikaku.parser import parse_puzzle_text


def test_parse_valid_puzzle() -> None:
    puzzle = parse_puzzle_text(
        """
        # comments are allowed
        3 3
        3 . .
        . 3 .
        . . 3
        """
    )

    assert puzzle.rows == 3
    assert puzzle.cols == 3
    assert puzzle.grid[0][0] == 3
    assert puzzle.grid[1][1] == 3
    assert puzzle.grid[0][1] is None


@pytest.mark.parametrize(
    "text, message_part",
    [
        ("", "пусты"),
        ("3 x\n1 . .\n. . .\n. . .", "целыми"),
        ("0 3\n1 . .", "положительными"),
        ("2 2\n1 .", "Ожидалось 2 строк"),
        ("2 2\n1 . .\n. .", "должна содержать 2 значений"),
        ("2 2\n1 a\n. .", "Недопустимый токен"),
        ("2 2\n. .\n. .", "хотя бы одно число"),
    ],
)
def test_parse_invalid_input(text: str, message_part: str) -> None:
    with pytest.raises(InputFormatError, match=message_part):
        parse_puzzle_text(text)
