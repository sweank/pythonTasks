"""Command-line interface for the Shikaku solver."""

from __future__ import annotations

import argparse
import sys
import traceback
from pathlib import Path
from typing import Iterable

from .errors import InputFormatError, ShikakuError, SolutionValidationError
from .formatter import format_no_solution, format_solution
from .parser import parse_puzzle_file, parse_puzzle_text
from .solver import solve_puzzle
from .verifier import validate_solution


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="shikaku",
        description=(
            "Решение головоломки Shikaku из файла или набора файлов. "
            "Формат входа: первая строка '<rows> <cols>', далее rows строк по cols токенов; "
            "пустая клетка обозначается '.', '0' или '_'"
        ),
        epilog=(
            "Примеры:\n"
            "  python -m shikaku puzzle.txt\n"
            "  python -m shikaku examples/solvable_3x3.txt examples/unsolvable_2x2.txt\n"
            "  python -m shikaku puzzle.txt -o result.txt\n"
            "  cat puzzle.txt | python -m shikaku -"
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "inputs",
        nargs="+",
        help="Путь к входному файлу. Используйте '-' для чтения из stdin. Можно указать несколько файлов.",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Путь к файлу для записи результата. Если входов несколько, результаты будут объединены.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Показывать traceback при внутренних ошибках.",
    )
    return parser


def _solve_one(input_name: str) -> tuple[str, int]:
    if input_name == "-":
        puzzle = parse_puzzle_text(sys.stdin.read())
        title = "stdin"
    else:
        puzzle = parse_puzzle_file(input_name)
        title = input_name

    solution = solve_puzzle(puzzle)
    if solution is None:
        return f"FILE: {title}\n{format_no_solution()}", 1

    validate_solution(solution)
    return f"FILE: {title}\n{format_solution(solution)}", 0


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    parts: list[str] = []
    exit_code = 0

    for input_name in args.inputs:
        try:
            text, status = _solve_one(input_name)
            parts.append(text)
            exit_code = max(exit_code, status)
        except (InputFormatError, SolutionValidationError) as exc:
            parts.append(f"FILE: {input_name}\nSTATUS: ERROR\nMESSAGE: {exc}")
            exit_code = 2
        except ShikakuError as exc:
            parts.append(f"FILE: {input_name}\nSTATUS: ERROR\nMESSAGE: {exc}")
            exit_code = 2
        except Exception as exc:  # pragma: no cover - protected by CLI tests in normal mode
            if args.debug:
                raise
            parts.append(
                "\n".join(
                    [
                        f"FILE: {input_name}",
                        "STATUS: ERROR",
                        "MESSAGE: Внутренняя ошибка приложения. Запустите с --debug для подробностей.",
                    ]
                )
            )
            exit_code = 2

    output_text = "\n\n" + ("-" * 60) + "\n\n"
    rendered = output_text.join(parts)

    if args.output:
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)

    return exit_code


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":
    main()
