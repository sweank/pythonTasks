from __future__ import annotations

from pathlib import Path

from shikaku.cli import run


def test_cli_solves_file_and_writes_output(tmp_path: Path, capsys) -> None:
    puzzle_file = tmp_path / "puzzle.txt"
    puzzle_file.write_text("2 2\n2 2\n. .\n", encoding="utf-8")

    exit_code = run([str(puzzle_file)])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "STATUS: SOLVED" in captured.out
    assert f"FILE: {puzzle_file}" in captured.out


def test_cli_reports_invalid_input_without_traceback(tmp_path: Path, capsys) -> None:
    puzzle_file = tmp_path / "bad.txt"
    puzzle_file.write_text("2 2\n. .\n", encoding="utf-8")

    exit_code = run([str(puzzle_file)])
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "STATUS: ERROR" in captured.out
    assert "Traceback" not in captured.out


def test_cli_can_write_to_output_file(tmp_path: Path) -> None:
    puzzle_file = tmp_path / "puzzle.txt"
    output_file = tmp_path / "result.txt"
    puzzle_file.write_text("2 2\n2 2\n. .\n", encoding="utf-8")

    exit_code = run([str(puzzle_file), "-o", str(output_file)])

    assert exit_code == 0
    assert "STATUS: SOLVED" in output_file.read_text(encoding="utf-8")
