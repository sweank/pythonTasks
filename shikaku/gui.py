"""A minimal Tkinter interface for manually solving 2D and 3D Shikaku puzzles.

The GUI is intentionally simple:
- the left panel stores the puzzle text in the same format as the CLI;
- the right panel shows the current puzzle and the user's regions;
- in 2D mode, the user solves by clicking two opposite corners of a rectangle;
- in 3D mode, the user solves by entering cuboid coordinates and adding them;
- the program only checks the user's work, it does not auto-solve from the GUI.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from .errors import InputFormatError, ShikakuError, SolutionValidationError
from .formatter import _labels
from .formatter3d import format_puzzle_3d
from .generator import format_puzzle, generate_puzzle, generate_puzzle_3d
from .models import Puzzle, RectangleRegion, Solution
from .models3d import CuboidRegion, Puzzle3D, Solution3D
from .parser import parse_puzzle_text
from .parser3d import parse_puzzle_3d_text
from .verifier import validate_solution
from .verifier3d import validate_solution_3d


REGION_COLORS = [
    "#d6eaf8",
    "#d5f5e3",
    "#fdebd0",
    "#f5eef8",
    "#fadbd8",
    "#fcf3cf",
    "#d4efdf",
    "#ebdef0",
    "#e8f8f5",
    "#f9e79f",
]


class ShikakuApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Shikaku Manual UI")
        self.mode = tk.StringVar(value="2d")
        self.rows_var = tk.StringVar(value="4")
        self.cols_var = tk.StringVar(value="4")
        self.depth_var = tk.StringVar(value="2")
        self.seed_var = tk.StringVar(value="")
        self.status_var = tk.StringVar(value="Load or generate a puzzle, then solve it manually.")

        self.current_puzzle_2d: Puzzle | None = None
        self.current_puzzle_3d: Puzzle3D | None = None
        self.regions_2d: list[RectangleRegion] = []
        self.regions_3d: list[CuboidRegion] = []
        self.first_corner: tuple[int, int] | None = None

        self.layer_from_var = tk.StringVar(value="1")
        self.row_from_var = tk.StringVar(value="1")
        self.col_from_var = tk.StringVar(value="1")
        self.layer_to_var = tk.StringVar(value="1")
        self.row_to_var = tk.StringVar(value="1")
        self.col_to_var = tk.StringVar(value="1")

        self.board_frame: ttk.Frame | None = None
        self.region_listbox: tk.Listbox | None = None
        self._build()

    def _build(self) -> None:
        top = ttk.Frame(self.root, padding=10)
        top.pack(fill="x")

        ttk.Label(top, text="Mode:").grid(row=0, column=0, sticky="w")
        ttk.Combobox(top, textvariable=self.mode, values=["2d", "3d"], width=6, state="readonly").grid(row=0, column=1)
        ttk.Label(top, text="Depth:").grid(row=0, column=2, sticky="w", padx=(10, 0))
        ttk.Entry(top, textvariable=self.depth_var, width=6).grid(row=0, column=3)
        ttk.Label(top, text="Rows:").grid(row=0, column=4, sticky="w", padx=(10, 0))
        ttk.Entry(top, textvariable=self.rows_var, width=6).grid(row=0, column=5)
        ttk.Label(top, text="Cols:").grid(row=0, column=6, sticky="w", padx=(10, 0))
        ttk.Entry(top, textvariable=self.cols_var, width=6).grid(row=0, column=7)
        ttk.Label(top, text="Seed:").grid(row=0, column=8, sticky="w", padx=(10, 0))
        ttk.Entry(top, textvariable=self.seed_var, width=8).grid(row=0, column=9)

        actions = ttk.Frame(self.root, padding=(10, 0, 10, 8))
        actions.pack(fill="x")
        ttk.Button(actions, text="Generate", command=self.generate).pack(side="left")
        ttk.Button(actions, text="Load from text", command=self.load_from_text).pack(side="left", padx=6)
        ttk.Button(actions, text="Undo", command=self.undo).pack(side="left")
        ttk.Button(actions, text="Clear regions", command=self.clear_regions).pack(side="left", padx=6)
        ttk.Button(actions, text="Check", command=self.check_solution).pack(side="left")

        ttk.Label(self.root, textvariable=self.status_var, padding=(10, 0, 10, 8)).pack(fill="x")

        body = ttk.Panedwindow(self.root, orient="horizontal")
        body.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        input_frame = ttk.Labelframe(body, text="Puzzle text")
        work_frame = ttk.Labelframe(body, text="Manual solving")
        body.add(input_frame, weight=1)
        body.add(work_frame, weight=2)

        self.input_text = tk.Text(input_frame, wrap="none", width=36, height=30)
        self.input_text.pack(fill="both", expand=True)

        self.board_frame = ttk.Frame(work_frame, padding=8)
        self.board_frame.pack(fill="both", expand=True)

        sidebar = ttk.Frame(work_frame, padding=(8, 0, 8, 8))
        sidebar.pack(fill="x")

        ttk.Label(sidebar, text="Added regions").pack(anchor="w")
        self.region_listbox = tk.Listbox(sidebar, height=6)
        self.region_listbox.pack(fill="x", pady=(4, 8))

        coords = ttk.Labelframe(sidebar, text="3D cuboid coordinates (1-based)")
        coords.pack(fill="x")
        labels = [
            ("Layer from", self.layer_from_var),
            ("Row from", self.row_from_var),
            ("Col from", self.col_from_var),
            ("Layer to", self.layer_to_var),
            ("Row to", self.row_to_var),
            ("Col to", self.col_to_var),
        ]
        for index, (caption, variable) in enumerate(labels):
            ttk.Label(coords, text=caption).grid(row=index // 3, column=(index % 3) * 2, sticky="w", padx=(0, 4), pady=2)
            ttk.Entry(coords, textvariable=variable, width=5).grid(row=index // 3, column=(index % 3) * 2 + 1, sticky="w", padx=(0, 8), pady=2)
        ttk.Button(coords, text="Add 3D region", command=self.add_region_3d_from_entries).grid(
            row=2, column=0, columnspan=6, sticky="w", pady=(6, 0)
        )

        self.input_text.insert("1.0", "2 2\n2 2\n. .\n")

    def _seed(self) -> int | None:
        value = self.seed_var.get().strip()
        return int(value) if value else None

    def _clear_board_frame(self) -> None:
        if self.board_frame is None:
            return
        for child in self.board_frame.winfo_children():
            child.destroy()

    def _set_status(self, text: str) -> None:
        self.status_var.set(text)

    def _region_label(self, index: int) -> str:
        return _labels(index + 1)[-1]

    def _region_color(self, index: int) -> str:
        return REGION_COLORS[index % len(REGION_COLORS)]

    def _refresh_region_list(self) -> None:
        if self.region_listbox is None:
            return
        self.region_listbox.delete(0, tk.END)
        if self.mode.get() == "3d":
            for index, region in enumerate(self.regions_3d):
                label = self._region_label(index)
                self.region_listbox.insert(tk.END, region.label_description(label))
        else:
            for index, region in enumerate(self.regions_2d):
                label = self._region_label(index)
                self.region_listbox.insert(tk.END, region.label_description(label))

    def clear_regions(self) -> None:
        self.regions_2d.clear()
        self.regions_3d.clear()
        self.first_corner = None
        self._refresh_region_list()
        self.render_current_puzzle()
        self._set_status("All added regions were cleared.")

    def undo(self) -> None:
        if self.mode.get() == "3d":
            if self.regions_3d:
                self.regions_3d.pop()
                self._refresh_region_list()
                self.render_current_puzzle()
                self._set_status("Last 3D region removed.")
        else:
            if self.regions_2d:
                self.regions_2d.pop()
                self._refresh_region_list()
                self.render_current_puzzle()
                self._set_status("Last 2D region removed.")

    def generate(self) -> None:
        try:
            rows = int(self.rows_var.get())
            cols = int(self.cols_var.get())
            seed = self._seed()
            if self.mode.get() == "3d":
                depth = int(self.depth_var.get())
                puzzle = generate_puzzle_3d(depth, rows, cols, seed=seed)
                text = format_puzzle_3d(puzzle)
            else:
                puzzle = generate_puzzle(rows, cols, seed=seed)
                text = format_puzzle(puzzle)
            self.input_text.delete("1.0", tk.END)
            self.input_text.insert("1.0", text + "\n")
            self.load_from_text()
            self._set_status("Puzzle generated. Solve it manually and press Check.")
        except Exception as exc:
            messagebox.showerror("Generation error", str(exc))

    def load_from_text(self) -> None:
        text = self.input_text.get("1.0", tk.END)
        try:
            self.regions_2d.clear()
            self.regions_3d.clear()
            self.first_corner = None
            if self.mode.get() == "3d":
                self.current_puzzle_3d = parse_puzzle_3d_text(text)
                self.current_puzzle_2d = None
                self.layer_from_var.set("1")
                self.row_from_var.set("1")
                self.col_from_var.set("1")
                self.layer_to_var.set("1")
                self.row_to_var.set("1")
                self.col_to_var.set("1")
                self._set_status("3D puzzle loaded. Add cuboids with 1-based coordinates, then press Check.")
            else:
                self.current_puzzle_2d = parse_puzzle_text(text)
                self.current_puzzle_3d = None
                self._set_status("2D puzzle loaded. Click two opposite corners to add a rectangle.")
            self._refresh_region_list()
            self.render_current_puzzle()
        except (ShikakuError, ValueError) as exc:
            messagebox.showerror("Load error", str(exc))

    def render_current_puzzle(self) -> None:
        self._clear_board_frame()
        if self.mode.get() == "3d":
            self._render_3d()
        else:
            self._render_2d()

    def _find_region_for_cell_2d(self, row: int, col: int) -> int | None:
        for index, region in enumerate(self.regions_2d):
            if region.top <= row <= region.bottom and region.left <= col <= region.right:
                return index
        return None

    def _render_2d(self) -> None:
        puzzle = self.current_puzzle_2d
        if puzzle is None or self.board_frame is None:
            ttk.Label(self.board_frame, text="No 2D puzzle loaded.").pack(anchor="w")
            return

        ttk.Label(
            self.board_frame,
            text="2D mode: click one corner, then the opposite corner of the rectangle.",
        ).grid(row=0, column=0, columnspan=puzzle.cols, sticky="w", pady=(0, 8))

        for row in range(puzzle.rows):
            for col in range(puzzle.cols):
                clue_value = puzzle.grid[row][col]
                region_index = self._find_region_for_cell_2d(row, col)
                label = self._region_label(region_index) if region_index is not None else ""
                if clue_value is not None and label:
                    text = f"{clue_value}\n{label}"
                elif clue_value is not None:
                    text = str(clue_value)
                else:
                    text = label or " "

                options: dict[str, object] = {
                    "text": text,
                    "width": 6,
                    "height": 3,
                    "command": lambda r=row, c=col: self.on_cell_click_2d(r, c),
                    "relief": "raised",
                }
                if region_index is not None:
                    options["bg"] = self._region_color(region_index)
                if self.first_corner == (row, col):
                    options["relief"] = "sunken"

                button = tk.Button(self.board_frame, **options)
                button.grid(row=row + 1, column=col, padx=1, pady=1, sticky="nsew")

    def on_cell_click_2d(self, row: int, col: int) -> None:
        puzzle = self.current_puzzle_2d
        if puzzle is None:
            return

        if self.first_corner is None:
            self.first_corner = (row, col)
            self.render_current_puzzle()
            self._set_status(
                f"First corner selected at row {row + 1}, col {col + 1}. Click the opposite corner."
            )
            return

        start_row, start_col = self.first_corner
        self.first_corner = None
        top, bottom = sorted((start_row, row))
        left, right = sorted((start_col, col))
        self._try_add_region_2d(top, left, bottom, right)

    def _try_add_region_2d(self, top: int, left: int, bottom: int, right: int) -> None:
        puzzle = self.current_puzzle_2d
        if puzzle is None:
            return

        clues_inside = [clue for clue in puzzle.clues if top <= clue.position.row <= bottom and left <= clue.position.col <= right]
        if len(clues_inside) != 1:
            messagebox.showerror(
                "Invalid rectangle",
                "A 2D rectangle must contain exactly one clue.",
            )
            self.render_current_puzzle()
            return

        clue = clues_inside[0]
        region = RectangleRegion(top=top, left=left, bottom=bottom, right=right, clue=clue)
        if region.area != clue.value:
            messagebox.showerror(
                "Invalid rectangle",
                f"Rectangle area is {region.area}, but the clue requires {clue.value}.",
            )
            self.render_current_puzzle()
            return

        if any(existing.clue.position == clue.position for existing in self.regions_2d):
            messagebox.showerror("Invalid rectangle", "This clue already has a region.")
            self.render_current_puzzle()
            return

        if any(region.overlaps(existing) for existing in self.regions_2d):
            messagebox.showerror("Invalid rectangle", "The rectangle overlaps an existing region.")
            self.render_current_puzzle()
            return

        self.regions_2d.append(region)
        self._refresh_region_list()
        self.render_current_puzzle()
        self._set_status(
            f"Added 2D region for clue {clue.value} at {clue.position.to_human()}. Press Check when finished."
        )

    def _find_region_for_cell_3d(self, layer: int, row: int, col: int) -> int | None:
        for index, region in enumerate(self.regions_3d):
            if (
                region.front <= layer <= region.back
                and region.top <= row <= region.bottom
                and region.left <= col <= region.right
            ):
                return index
        return None

    def _render_3d(self) -> None:
        puzzle = self.current_puzzle_3d
        if puzzle is None or self.board_frame is None:
            ttk.Label(self.board_frame, text="No 3D puzzle loaded.").pack(anchor="w")
            return

        ttk.Label(
            self.board_frame,
            text="3D mode: enter two opposite cuboid corners below the board, then press Add 3D region.",
        ).pack(anchor="w", pady=(0, 8))

        layers_row = ttk.Frame(self.board_frame)
        layers_row.pack(anchor="w")

        for layer_index in range(puzzle.depth):
            layer_frame = ttk.Labelframe(layers_row, text=f"Layer {layer_index + 1}", padding=6)
            layer_frame.pack(side="left", padx=(0, 10), anchor="n")
            for row in range(puzzle.rows):
                for col in range(puzzle.cols):
                    clue_value = puzzle.grid[layer_index][row][col]
                    region_index = self._find_region_for_cell_3d(layer_index, row, col)
                    label = self._region_label(region_index) if region_index is not None else ""
                    if clue_value is not None and label:
                        text = f"{clue_value}\n{label}"
                    elif clue_value is not None:
                        text = str(clue_value)
                    else:
                        text = label or " "
                    widget = tk.Label(layer_frame, text=text, width=6, height=3, relief="ridge", borderwidth=1)
                    if region_index is not None:
                        widget.configure(bg=self._region_color(region_index))
                    widget.grid(row=row, column=col, padx=1, pady=1)

    def add_region_3d_from_entries(self) -> None:
        puzzle = self.current_puzzle_3d
        if puzzle is None:
            messagebox.showerror("3D region", "Load a 3D puzzle first.")
            return

        try:
            front = int(self.layer_from_var.get()) - 1
            top = int(self.row_from_var.get()) - 1
            left = int(self.col_from_var.get()) - 1
            back = int(self.layer_to_var.get()) - 1
            bottom = int(self.row_to_var.get()) - 1
            right = int(self.col_to_var.get()) - 1
        except ValueError:
            messagebox.showerror("3D region", "All cuboid coordinates must be integers.")
            return

        front, back = sorted((front, back))
        top, bottom = sorted((top, bottom))
        left, right = sorted((left, right))

        if not (0 <= front <= back < puzzle.depth and 0 <= top <= bottom < puzzle.rows and 0 <= left <= right < puzzle.cols):
            messagebox.showerror("3D region", "Cuboid coordinates are outside the puzzle bounds.")
            return

        clues_inside = [
            clue
            for clue in puzzle.clues
            if front <= clue.position.layer <= back
            and top <= clue.position.row <= bottom
            and left <= clue.position.col <= right
        ]
        if len(clues_inside) != 1:
            messagebox.showerror("3D region", "A 3D cuboid must contain exactly one clue.")
            return

        clue = clues_inside[0]
        region = CuboidRegion(front=front, top=top, left=left, back=back, bottom=bottom, right=right, clue=clue)
        if region.volume != clue.value:
            messagebox.showerror(
                "3D region",
                f"Cuboid volume is {region.volume}, but the clue requires {clue.value}.",
            )
            return

        if any(existing.clue.position == clue.position for existing in self.regions_3d):
            messagebox.showerror("3D region", "This clue already has a cuboid.")
            return

        if any(region.overlaps(existing) for existing in self.regions_3d):
            messagebox.showerror("3D region", "The cuboid overlaps an existing region.")
            return

        self.regions_3d.append(region)
        self._refresh_region_list()
        self.render_current_puzzle()
        self._set_status(
            f"Added 3D region for clue {clue.value} at {clue.position.to_human()}. Press Check when finished."
        )

    def check_solution(self) -> None:
        try:
            if self.mode.get() == "3d":
                if self.current_puzzle_3d is None:
                    raise InputFormatError("Load a 3D puzzle before checking it.")
                solution = Solution3D(self.current_puzzle_3d, tuple(self.regions_3d))
                validate_solution_3d(solution)
                self._set_status("Correct 3D solution. The puzzle is solved.")
                messagebox.showinfo("Success", "The 3D solution is correct.")
            else:
                if self.current_puzzle_2d is None:
                    raise InputFormatError("Load a 2D puzzle before checking it.")
                solution = Solution(self.current_puzzle_2d, tuple(self.regions_2d))
                validate_solution(solution)
                self._set_status("Correct 2D solution. The puzzle is solved.")
                messagebox.showinfo("Success", "The 2D solution is correct.")
        except (ShikakuError, SolutionValidationError, ValueError) as exc:
            messagebox.showerror("Check failed", str(exc))



def main() -> None:
    root = tk.Tk()
    root.geometry("1200x760")
    ShikakuApp(root)
    root.mainloop()
