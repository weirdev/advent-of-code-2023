from typing import Tuple, List
from itertools import chain


def parse_dig_line(line) -> (Tuple[int, int], int, str):
    dir, count, color = line.split(' ')
    count = int(count)
    color = color[2:-1] # (#xxxxxx)
    return dir_to_delta_coord(dir), count, color


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


def count_outside(terrain: List[List[bool]]) -> int:
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

    return len(outside)


def part1(filename: str) -> int:
    dig_seq = read_dig_seq(filename)
    terrain = create_terrain(dig_seq)
    dig(terrain, dig_seq)

    return (len(terrain[0]) * len(terrain)) - count_outside(terrain)


if __name__ == "__main__":
    p1 = part1("input")
    print(f"Part 1: {p1}")
