MAX_2D_ROWS = 10
MAX_2D_COLS = 25
MAX_3D_ROWS = 10
MAX_3D_COLS_BY_DEPTH = {
    1: 25,
    2: 15,
    3: 10,
    4: 7,
    5: 6,
    6: 5,
    7: 4,
    8: 3,
    9: 3,
}
MAX_3D_DEPTH = max(MAX_3D_COLS_BY_DEPTH)


def validate_2d_dimensions(rows: int, cols: int, error_type: type[Exception] = ValueError) -> None:
    if rows <= 0 or cols <= 0:
        raise error_type("Размеры поля должны быть положительными.")
    if rows > MAX_2D_ROWS or cols > MAX_2D_COLS:
        raise error_type(f"Для 2D максимум {MAX_2D_ROWS} строк и {MAX_2D_COLS} столбцов.")


def validate_3d_dimensions(
    depth: int,
    rows: int,
    cols: int,
    error_type: type[Exception] = ValueError,
) -> None:
    if depth <= 0 or rows <= 0 or cols <= 0:
        raise error_type("Размеры 3D-поля должны быть положительными.")
    if depth > MAX_3D_DEPTH:
        raise error_type(f"Для 3D глубина должна быть от 1 до {MAX_3D_DEPTH}.")

    max_cols = MAX_3D_COLS_BY_DEPTH[depth]
    if rows > MAX_3D_ROWS or cols > max_cols:
        raise error_type(f"Для 3D при глубине {depth} максимум {MAX_3D_ROWS} строк и {max_cols} столбцов.")
