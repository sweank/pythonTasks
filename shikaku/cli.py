"""Command-line interface for the Shikaku solver and its minimal extensions."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .errors import InputFormatError, ShikakuError, SolutionValidationError
from .formatter import format_no_solution, format_solution
from .formatter3d import format_puzzle_3d, format_solution_3d
from .generator import format_puzzle, generate_puzzle, generate_puzzle_3d
from .gui import main as gui_main
from .parser import parse_puzzle_file, parse_puzzle_text
from .parser3d import parse_puzzle_3d_file, parse_puzzle_3d_text
from .solver import solve_puzzle
from .solver3d import solve_puzzle_3d
from .verifier import validate_solution
from .verifier3d import validate_solution_3d


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="shikaku",
        description=(
            "Решение, генерация и запуск минимального UI для 2D/3D головоломки Shikaku. "
            "2D формат: <rows> <cols> и далее rows строк. "
            "3D формат: <depth> <rows> <cols> и далее depth*rows строк, разделитель слоёв --- необязателен."
        ),
        epilog=(
            "Примеры:\n"
            "  python -m shikaku puzzle.txt\n"
            "  python -m shikaku --mode 3d puzzle3d.txt\n"
            "  python -m shikaku --generate --rows 4 --cols 5\n"
            "  python -m shikaku --generate --mode 3d --depth 2 --rows 3 --cols 3\n"
            "  python -m shikaku --gui\n"
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("inputs", nargs="*", help="Пути к входным файлам. Используйте '-' для чтения из stdin.")
    parser.add_argument("-o", "--output", help="Путь к файлу для записи результата.")
    parser.add_argument("--debug", action="store_true", help="Показывать traceback при внутренних ошибках.")
    parser.add_argument("--mode", choices=["2d", "3d"], default="2d", help="Режим решения или генерации.")
    parser.add_argument("--generate", action="store_true", help="Сгенерировать новую головоломку вместо решения файла.")
    parser.add_argument("--rows", type=int, help="Число строк для генератора.")
    parser.add_argument("--cols", type=int, help="Число столбцов для генератора.")
    parser.add_argument("--depth", type=int, help="Глубина для 3D-генератора.")
    parser.add_argument("--seed", type=int, help="Seed для воспроизводимой генерации.")
    parser.add_argument("--gui", action="store_true", help="Запустить минимальный графический интерфейс.")
    return parser


def _solve_one_2d(input_name: str) -> tuple[str, int]:
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


def _solve_one_3d(input_name: str) -> tuple[str, int]:
    if input_name == "-":
        puzzle = parse_puzzle_3d_text(sys.stdin.read())
        title = "stdin"
    else:
        puzzle = parse_puzzle_3d_file(input_name)
        title = input_name

    solution = solve_puzzle_3d(puzzle)
    if solution is None:
        return f"FILE: {title}\nSTATUS: NO_SOLUTION_3D", 1

    validate_solution_3d(solution)
    return f"FILE: {title}\n{format_solution_3d(solution)}", 0


def _render_generated(args: argparse.Namespace) -> str:
    if args.rows is None or args.cols is None:
        raise InputFormatError("Для генерации укажите --rows и --cols.")
    if args.mode == "3d":
        if args.depth is None:
            raise InputFormatError("Для 3D-генерации укажите --depth.")
        puzzle = generate_puzzle_3d(args.depth, args.rows, args.cols, seed=args.seed)
        return format_puzzle_3d(puzzle)
    puzzle = generate_puzzle(args.rows, args.cols, seed=args.seed)
    return format_puzzle(puzzle)


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.gui:
        gui_main()
        return 0

    if args.generate:
        try:
            rendered = _render_generated(args)
        except (InputFormatError, ShikakuError, ValueError) as exc:
            rendered = f"STATUS: ERROR\nMESSAGE: {exc}"
            if args.output:
                Path(args.output).write_text(rendered + "\n", encoding="utf-8")
            else:
                print(rendered)
            return 2
        if args.output:
            Path(args.output).write_text(rendered + "\n", encoding="utf-8")
        else:
            print(rendered)
        return 0

    if not args.inputs:
        parser.error("нужно указать входной файл, --generate или --gui")

    parts: list[str] = []
    exit_code = 0
    solver = _solve_one_3d if args.mode == "3d" else _solve_one_2d

    for input_name in args.inputs:
        try:
            text, status = solver(input_name)
            parts.append(text)
            exit_code = max(exit_code, status)
        except (InputFormatError, SolutionValidationError) as exc:
            parts.append(f"FILE: {input_name}\nSTATUS: ERROR\nMESSAGE: {exc}")
            exit_code = 2
        except ShikakuError as exc:
            parts.append(f"FILE: {input_name}\nSTATUS: ERROR\nMESSAGE: {exc}")
            exit_code = 2
        except Exception:
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

    rendered = ("\n\n" + ("-" * 60) + "\n\n").join(parts)

    if args.output:
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)

    return exit_code


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":
    main()
