from typing import List


def shift_dir(grid: List[List[str]], dir: (int, int)):
    for y in range(len(grid)):
        if dir[1] > 0:
            y = len(grid) - 1 - y

        for x in range(len(grid[y])):
            if dir[0] > 0:
                x = len(grid[y]) - 1 - x

            if grid[y][x] == "O":
                step = dir[0] + dir[1]
                if dir[1] != 0:
                    start = y
                    if dir[1] > 0:
                        end = len(grid)
                    else:
                        end = -1
                else:
                    start = x
                    if dir[0] > 0:
                        end = len(grid[y])
                    else:
                        end = -1
                for move_pos in range(start+step, end, step):
                    if dir[0] != 0:
                        new_y = y
                        prev_y = y
                        new_x = move_pos
                        prev_x = move_pos - step
                    else:
                        new_y = move_pos
                        prev_y = move_pos - step
                        new_x = x
                        prev_x = x

                    if grid[new_y][new_x] == ".":
                        grid[new_y][new_x] = "O"
                        grid[prev_y][prev_x] = "."
                    else:
                        break


def calculate_load(grid: List[List[str]]) -> int:
    return sum(len(grid) - y for y in range(len(grid)) for x in range(len(grid[y])) if grid[y][x] == "O")


def read_grid(filename: str) -> List[List[str]]:
    with open(filename) as f:
        return [list(line.strip()) for line in f.readlines()]


def part1(filename: str) -> int:
    grid = read_grid(filename)
    shift_dir(grid, (0, -1))
    return calculate_load(grid)


def part2(filename: str) -> int:
    grid = read_grid(filename)
    # N W S E
    cycle = [(0, -1), (-1, 0), (0, 1), (1, 0)]

    prev_grids = {} # grid_str -> cycle#
    c = 0
    limit = 1000000000
    while c < limit:
        for dir in cycle:
            shift_dir(grid, dir)
        grid_str = "\n".join("".join(row) for row in grid)
        if grid_str in prev_grids:
            equal_cycle = prev_grids[grid_str]
            delta = c - equal_cycle
            remaining_cycles = 1000000000 - 1 - c
            limit = c + (remaining_cycles % delta) + 1
        else:
            prev_grids[grid_str] = c
        c += 1

    return calculate_load(grid)


if __name__ == "__main__":
    p1 = part1("input")
    print(f"Part 1: {p1}")
    p2 = part2("input")
    print(f"Part 2: {p2}")
