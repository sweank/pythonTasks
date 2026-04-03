# Shikaku Solver

Console and minimal GUI implementation of the Shikaku puzzle.

## Features

- 2D Shikaku solver
- 3D Shikaku solver (minimal cuboid-based extension)
- random puzzle generator for 2D and 3D
- basic Tkinter UI for manual solving, checking and generation
- unit tests and GitHub Actions CI

## 2D input format

```text
<rows> <cols>
<row 1>
...
<row N>
```

Empty cells: `.`, `0`, `_`

Example:

```text
3 3
3 . .
. 3 .
. . 3
```

## 3D input format

```text
<depth> <rows> <cols>
<layer 1 row 1>
...
<layer 1 row N>
---
<layer 2 row 1>
...
```

Separator `---` is optional.

Example:

```text
2 2 2
4 .
. .
---
4 .
. .
```

## CLI usage

Solve 2D puzzle:

```bash
python -m shikaku puzzle.txt
```

Solve 3D puzzle:

```bash
python -m shikaku --mode 3d puzzle3d.txt
```

Generate 2D puzzle:

```bash
python -m shikaku --generate --rows 4 --cols 4 --seed 1
```

Generate 3D puzzle:

```bash
python -m shikaku --generate --mode 3d --depth 2 --rows 3 --cols 3 --seed 1
```

Run GUI for manual solving:

```bash
python -m shikaku --gui
```

## Architecture

- `shikaku/models.py` - 2D models
- `shikaku/models3d.py` - 3D models
- `shikaku/parser.py` / `parser3d.py` - input parsing
- `shikaku/solver.py` / `solver3d.py` - backtracking solvers
- `shikaku/verifier.py` / `verifier3d.py` - result validation
- `shikaku/generator.py` - minimal puzzle generation
- `shikaku/gui.py` - minimal Tkinter interface for manual solving
- `tests/` - unit tests

## Notes

- The 3D version is intentionally minimal: the puzzle is split into cuboids instead of rectangles.
- The generator aims for simplicity, not for guaranteed uniqueness of the solution.
- In the GUI, the user solves puzzles manually: 2D by selecting rectangle corners, 3D by entering cuboid coordinates and checking the result.
- Replace the author placeholder in project metadata before final submission.
