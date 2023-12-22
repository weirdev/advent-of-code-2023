from typing import List, Tuple

def dist1(a: Tuple[int, int], b: Tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def positions_to_dist_sum(positions: List[Tuple[int, int]]) -> int:
    s = 0
    for i, pos1 in enumerate(positions):
        for j, pos2 in enumerate(positions[i+1:]):
            s += dist1(pos1, pos2)
    return s


def add_expansion_to_grid(grid: List[List[str]]) -> None:
    # Rows
    y = 0
    while y < len(grid):
        row = grid[y]
        if all(c == "." for c in row):
            grid.insert(y, ["."] * len(row))
            y += 1
        y += 1

    # Columns
    x = 0
    while x < len(grid[0]):
        if all(grid[y][x] == "." for y in range(len(grid))):
            for row in grid:
                row.insert(x, ".")
            x += 1
        x += 1


def find_expansion_rows_cols(grid: List[List[str]]) -> Tuple[List[int], List[int]]:
    rows = []
    cols = []
    for y, row in enumerate(grid):
        if all(c == "." for c in row):
            rows.append(y)
    for x, col in enumerate(zip(*grid)):
        if all(c == "." for c in col):
            cols.append(x)
    return rows, cols


def positions_from_grid(grid: List[List[str]]) -> List[Tuple[int, int]]:
    return [(x, y) for y, row in enumerate(grid) for x, c in enumerate(row) if c == "#"]


def add_expansion_to_positions(positions: List[Tuple[int, int]], exp_rows: List[int], exp_cols: List[int], factor: int) -> None:
    # Rows
    row_exp = 0
    new_positions = []
    for pos in sorted(positions, key=lambda p: p[1]):
        while row_exp < len(exp_rows) and pos[1] > exp_rows[row_exp]:
            row_exp += 1
        new_positions.append((pos[0], pos[1] + ((factor - 1) * row_exp)))

    positions[:] = new_positions

    # Columns
    col_exp = 0
    new_positions = []
    for pos in sorted(positions, key=lambda p: p[0]):
        while col_exp < len(exp_cols) and pos[0] > exp_cols[col_exp]:
            col_exp += 1
        new_positions.append((pos[0] + ((factor - 1) * col_exp), pos[1]))

    positions[:] = new_positions # Forgot the slice assignment operator in CS1 Midterm 2...


def read_positions_p1(filename: str) -> List[Tuple[int, int]]:
    with open(filename) as f:
        lines = [list(line.strip()) for line in f.readlines()]

    add_expansion_to_grid(lines)

    return positions_from_grid(lines)


def read_positions_p2(filename: str, factor: int) -> List[Tuple[int, int]]:
    with open(filename) as f:
        lines = [list(line.strip()) for line in f.readlines()]

    positions = positions_from_grid(lines)

    exp_rows, exp_cols = find_expansion_rows_cols(lines)

    add_expansion_to_positions(positions, exp_rows, exp_cols, factor)

    return positions


def part1(filename: str) -> int:
    positions = read_positions_p1(filename)
    return positions_to_dist_sum(positions)


def part2(filename: str) -> int:
    positions = read_positions_p2(filename, 1000000)
    return positions_to_dist_sum(positions)


if __name__ == "__main__":
    p1 = part1("input")
    print(f"Part 1: {p1}")
    p2 = part2("input")
    print(f"Part 2: {p2}")
