from typing import List, Set, Tuple

def read_grid(filename: str) -> List[List[str]]:
    with open(filename) as f:
        return [l.strip() for l in f.readlines()]


def get_beam_grid(grid: List[str], incoming_pos: Tuple[int, int], incoming_dir: Tuple[int, int]) -> List[List[Set[Tuple[int, int]]]]:
    def enqueue(queue, pos: Tuple[int, int], dir: Tuple[int, int], grid, beam_grid):
        if pos[0] >= 0 and pos[0] < len(grid[0]) and pos[1] >= 0 and pos[1] < len(grid):
            # Already processed a beam going this direction through here?
            if dir not in beam_grid[pos[1]][pos[0]]:
                beam_grid[pos[1]][pos[0]].add(dir)
                queue.append((pos, dir))

    queue = [(incoming_pos, incoming_dir)]
    beam_grid = [[set() for _ in range(len(grid[0]))] for _ in range(len(grid))]
    beam_grid[incoming_pos[1]][incoming_pos[0]].add(incoming_dir)
    while len(queue) > 0:
        (x, y), (dir_x, dir_y) = queue.pop()
        if grid[y][x] == ".":
            enqueue(queue, (x + dir_x, y + dir_y), (dir_x, dir_y), grid, beam_grid)
        elif grid[y][x] == "|":
            if dir_y != 0:
                # Vertical beam, not affected
                enqueue(queue, (x + dir_x, y + dir_y), (dir_x, dir_y), grid, beam_grid)
            else:
                # Horizontal beam, split
                enqueue(queue, (x, y - 1), (0, -1), grid, beam_grid)
                enqueue(queue, (x, y + 1), (0, 1), grid, beam_grid)
        elif grid[y][x] == "-":
            if dir_x != 0:
                # Horizontal beam, not affected
                enqueue(queue, (x + dir_x, y + dir_y), (dir_x, dir_y), grid, beam_grid)
            else:
                # Vertical beam, split
                enqueue(queue, (x - 1, y), (-1, 0), grid, beam_grid)
                enqueue(queue, (x + 1, y), (1, 0), grid, beam_grid)
        elif grid[y][x] == "\\":
            new_dir_x = dir_y
            new_dir_y = dir_x
            enqueue(queue, (x + new_dir_x, y + new_dir_y), (new_dir_x, new_dir_y), grid, beam_grid)
        else:
            assert grid[y][x] == "/", "Unknown grid char"
            new_dir_x = -dir_y
            new_dir_y = -dir_x
            enqueue(queue, (x + new_dir_x, y + new_dir_y), (new_dir_x, new_dir_y), grid, beam_grid)

    return beam_grid


def total_energized_tiles(beam_grid: List[List[Set[Tuple[int, int]]]]) -> int:
    return sum(1 for row in beam_grid for beams in row if len(beams) > 0)


def beam_grid_str(beam_grid: List[List[Set[Tuple[int, int]]]]) -> str:
    def beams_str(beams: Set[Tuple[int, int]]) -> str:
        if len(beams) == 0:
            return "."
        elif len(beams) == 1:
            return "#"
        else:
            return str(len(beams))
    return "\n".join("".join(beams_str(b) for b in row) for row in beam_grid)


def part1(filename: str) -> int:
    grid = read_grid(filename)
    beam_grid = get_beam_grid(grid, (0, 0), (1, 0))
    return total_energized_tiles(beam_grid)


def part2(filename: str) -> int:
    grid = read_grid(filename)
    max_et = 0
    for dir_axis in 0, 1:
        for inv in -1, 1:
            dir = [0, 0]
            dir[dir_axis] = inv
            dir = tuple(dir)
            if dir_axis == 0:
                bound = len(grid)
            else:
                bound = len(grid[0])
            for i in range(bound):
                pos = [None, None]
                if inv < 0:
                    start = bound - 1
                else:
                    start = 0
                pos[dir_axis] = start
                pos[1 - dir_axis] = i
                beam_grid = get_beam_grid(grid, tuple(pos), dir)
                max_et = max(max_et, total_energized_tiles(beam_grid))

    return max_et


if __name__ == "__main__":
    p1 = part1("input")
    print(f"Part 1: {p1}")
    p2 = part2("input")
    print(f"Part 2: {p2}")
