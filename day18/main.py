from typing import Tuple, List
from itertools import chain


def parse_dig_line(line) -> (Tuple[int, int], int, str):
    dir, count, color = line.split(' ')
    count = int(count)
    color = color[2:-1] # (#xxxxxx)
    return (dir_to_delta_coord(dir), count, color)


def parse_dig_line_color(line) -> (Tuple[int, int], int):
    _, _, color = line.split(' ')
    count = color[2:-2] # (#xxxxx<|>x)
    count = int(count, 16)
    dir = color[-2] # (#xxxxx<|>x)
    return (color_dir_to_delta_coord(dir), count)


def color_dir_to_delta_coord(color) -> (int, int):
    if color == '0': # R
        return (1, 0)
    elif color == '1': # D
        return (0, 1)
    elif color == '2': # L
        return (-1, 0)
    else:
        assert color == '3' # U
        return (0, -1)


def dir_to_delta_coord(dir) -> (int, int):
    if dir == 'U':
        return (0, -1)
    elif dir == 'D':
        return (0, 1)
    elif dir == 'L':
        return (-1, 0)
    else:
        assert dir == 'R'
        return (1, 0)


def read_dig_seq(filename: str) -> List[Tuple[Tuple[int, int], int, str]]:
    with open(filename) as f:
        return [parse_dig_line(line.strip()) for line in f.readlines()]


def read_dig_seq_color(filename: str) -> List[Tuple[Tuple[int, int], int]]:
    with open(filename) as f:
        return [parse_dig_line_color(line.strip()) for line in f.readlines()]


def create_terrain(dig_seq: List[Tuple[Tuple[int, int], int, str]]) -> List[List[bool]]:
    max_x = sum(abs(dx)*c for (dx, _), c, _ in dig_seq) + 1
    max_y = sum(abs(dy)*c for (_, dy), c, _ in dig_seq) + 1
    return [[False for _ in range(max_x)] for _ in range(max_y)]


def dig(terrain: List[List[bool]], dig_seq: List[Tuple[Tuple[int, int], int, str]]) -> None:
    x = len(terrain[0]) // 2
    y = len(terrain) // 2
    terrain[y][x] = True
    for (dx, dy), count, color in dig_seq:
        for _ in range(count):
            x += dx
            y += dy
            terrain[y][x] = True


def find_outside(terrain: List[List[bool]]) -> {Tuple[int, int]}:
    edges = ([[(0, y), (len(terrain[0]) - 1, y)] for y in range(len(terrain))]
                    + [[(x, 0), (x, len(terrain) - 1)] for x in range(len(terrain[0]))])
    outside = {(x,y) for x, y in chain.from_iterable(edges) if not terrain[y][x]}
    outside_to_check = list(outside)
    checked_coords = set(outside)

    while len(outside_to_check) > 0:
        x, y = outside_to_check.pop()

        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx == 0 and dy == 0:
                    continue
                nx = x + dx
                ny = y + dy
                if nx < 0 or nx >= len(terrain[0]) or ny < 0 or ny >= len(terrain):
                    continue

                if (nx, ny) in checked_coords:
                    continue
                checked_coords.add((nx, ny))

                if not terrain[ny][nx]:
                    outside.add((nx, ny))
                    outside_to_check.append((nx, ny))

    return outside


def part1(filename: str) -> int:
    dig_seq = read_dig_seq(filename)
    terrain = create_terrain(dig_seq)
    dig(terrain, dig_seq)

    return (len(terrain[0]) * len(terrain)) - len(find_outside(terrain))


def bin_search(target: int, seq: List[int]) -> int:
    lo = 0
    hi = len(seq) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if seq[mid] == target:
            return mid
        elif seq[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    raise ValueError("target not found in seq")


def dig_cont(dig_seq: List[Tuple[Tuple[int, int], int]], x_axis_positions: List[int],
             y_axis_positions: List[int], min_x: int, min_y: int) -> List[List[bool]]:
    x = min_x
    y = min_y
    terrain = [[False for _ in range(len(x_axis_positions))] for _ in range(len(y_axis_positions))]
    x_pos = bin_search(x, x_axis_positions)
    y_pos = bin_search(y, y_axis_positions)
    for (dx, dy), count in dig_seq:
        target_x = x + dx*count
        target_y = y + dy*count
        while x != target_x or y != target_y:
            if dx != 0:
                x_pos += dx # -1 or +1
            else:
                assert dy != 0
                y_pos += dy # -1 or +1
            x = x_axis_positions[x_pos]
            y = y_axis_positions[y_pos]

            terrain[y_pos][x_pos] = True

    return terrain


def plan_dig(dig_seq: List[Tuple[Tuple[int, int], int]]) -> (List[int], List[int], int, int):
    x_axis_positions = set()
    y_axis_positions = set()
    x = 0
    y = 0
    min_x = 0
    min_y = 0
    for (dx, dy), count in dig_seq:
        dx *= count
        dy *= count
        x += dx
        y += dy
        x_axis_positions.add(x)
        # We are only digging a 1m square at a time,
        # so the positions dug must only be 1m (on at least one axis)
        x_axis_positions.add(x-1)
        x_axis_positions.add(x+1)

        y_axis_positions.add(y)
        # We are only digging a 1m square at a time,
        # so the positions dug must only be 1m (on at least one axis)
        y_axis_positions.add(y-1)
        y_axis_positions.add(y+1)

        min_x = min(min_x, x)
        min_y = min(min_y, y)

    assert x == 0
    assert y == 0

    dx = abs(min_x)
    x_axis_positions = [x + dx for x in x_axis_positions]
    x_axis_positions.sort()
    dy = abs(min_y)
    y_axis_positions = [y + dy for y in y_axis_positions]
    y_axis_positions.sort()

    return (x_axis_positions, y_axis_positions, dx, dy)


def rect_area(rect_pos: (int, int), x_axis_positions: List[int], y_axis_positions: List[int]) -> int:
    end_x = x_axis_positions[rect_pos[0]]
    if rect_pos[0] > 0:
        start_x = x_axis_positions[rect_pos[0] - 1]
    else:
        start_x = 0

    end_y = y_axis_positions[rect_pos[1]]
    if rect_pos[1] > 0:
        start_y = y_axis_positions[rect_pos[1] - 1]
    else:
        start_y = 0

    return (end_x - start_x) * (end_y - start_y)

def part2(filename: str) -> int:
    dig_seq = read_dig_seq_color(filename)
    x_axis_positions, y_axis_positions, min_x, min_y = plan_dig(dig_seq)
    terrain = dig_cont(dig_seq, x_axis_positions, y_axis_positions, min_x, min_y)
    outside = find_outside(terrain)
    return sum(rect_area((x, y), x_axis_positions, y_axis_positions) for y, row in enumerate(terrain)
                for x, rect in enumerate(row) if not (x, y) in outside)


if __name__ == "__main__":
    p1 = part1("input")
    print(f"Part 1: {p1}")
    p2 = part2("input")
    print(f"Part 2: {p2}")
