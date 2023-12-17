from typing import List, Iterator, Tuple, Optional, Dict


class Pipe:
    def __init__(self, char: str, start: (int, int), end: (int, int)):
        """
        :param char: The character that represents this pipe
        :param start: The starting position of the pipe on the 3x3 grid around this pipe
        :param end: The ending position of the pipe on the 3x3 grid around this pipe
        """
        self.char = char
        self.start = start
        self.end = end


# y=0 is the top row
WE = Pipe('-', (-1, 0), (1, 0))
NS = Pipe('|', (0, -1), (0, 1))
SE = Pipe('F', (0, 1), (1, 0))
WS = Pipe('7', (-1, 0), (0, 1))
NW = Pipe('J', (0, -1), (-1, 0))
EN = Pipe('L', (1, 0), (0, -1))

PIPES = [WE, NS, SE, WS, NW, EN]
PIPES_BY_CHAR = {pipe.char: pipe for pipe in PIPES}


def adj_points_iter(grid: List[List[str]], x: int, y: int) -> Iterator[Tuple[int, int]]:
    if x > 0:
        yield (x-1, y)
    if x < len(grid[0]) - 1:
        yield (x+1, y)
    if y > 0:
        yield (x, y-1)
    if y < len(grid) - 1:
        yield (x, y+1)


def connected_omni_dir(grid: List[List[str]], x: int, y: int, allow_omni_to_omni: bool = False) -> [(int, int)]:
    connections = []
    for i, j in adj_points_iter(grid, x, y):
        if i == x and j == y:
            continue
        char = grid[j][i]
        if char == 'S':
            if not allow_omni_to_omni:
                # (x,y) is probably the only S, but explicitly handle connecting to one just in case
                raise Exception("Omni direction connection (S) to (another) S")
            connections.append((i, j))
        elif char != '.': # (x,y) is probably the only S, but exclude it just in case
            pipe = PIPES_BY_CHAR[char]
            for con in pipe.start, pipe.end:
                # Check if pipe connects back to (x,y)
                if i + con[0] == x and j + con[1] == y:
                    connections.append((i, j))

    return connections


def get_start_first_and_last_points(grid: List[List[str]]) -> ((int, int), (int, int), (int, int)):
    for i in range(len(grid[0])):
        for j in range(len(grid)):
            char = grid[j][i]
            if char == 'S':
                connections = connected_omni_dir(grid, i, j)
                assert len(connections) == 2
                start, end = connections
                return ((i, j), start, end)

    raise Exception("No start point (S) found")


def get_next_point(grid: List[List[str]], curr: (int, int), prev: (int, int)) -> (int, int):
    x, y = curr
    char = grid[y][x]
    if char == 'S' or char == '.':
        raise Exception(f"Invalid current point ('{char}' at {curr}) for get_next_point()")
    pipe = PIPES_BY_CHAR[char]
    for con in pipe.start, pipe.end:
        pos_next_x = x + con[0]
        pos_next_y = y + con[1]
        if not (pos_next_x == prev[0] and pos_next_y == prev[1]):
            return (pos_next_x, pos_next_y)
    raise Exception(f"Couldn't find next point for {curr}")


def traverse(grid: List[List[str]], start: (int, int), start_prev: (int, int), end: (int, int)) -> List[Tuple[int, int]]:
    path = [start_prev, start]
    while path[-1] != end:
        path.append(get_next_point(grid, path[-1], path[-2]))

    return path


def traverse_from_start(grid: List[List[str]]) -> List[Tuple[int, int]]:
    start_prev, start, end = get_start_first_and_last_points(grid)
    return traverse(grid, start, start_prev, end)


def part1(filename: str) -> int:
    with open(filename, "r") as f:
        lines = list(map(lambda line: list(line.strip()), f.readlines()))

    path_len = len(traverse_from_start(lines))

    return path_len // 2


def adj_half_to_full_pos_iter(grid: List[List[str]], full: (int, int)) -> Iterator[Tuple[int, int]]:
    x = full[0] * 2 + 1
    y = full[1] * 2 + 1

    if x > 0:
        yield (x-1, y)
    if x < len(grid[0]) * 2:
        yield (x+1, y)

    if y > 0:
        yield (x, y-1)
    if y < len(grid) * 2:
        yield (x, y+1)


def adj_half_to_half_iter(grid: List[List[str]], half: (int, int)):
    x, y = half
    if x % 2 == 0:
        # Vertical
        assert y % 2 == 1, "Half identifies line, not point"

        if y > 0:
            if y > 2:
                # Up vertical
                yield (x, y-2)
            if x > 0:
                # Up half left 90 deg
                yield (x-1, y-1)
            if x < len(grid[0]) * 2:
                # Up half right 90 deg
                yield (x+1, y-1)
        if y < len(grid) * 2:
            if y < (len(grid) * 2) - 2:
                # Down vertical
                yield (x, y+2)
            if x > 0:
                # Down half left 90 deg
                yield (x-1, y+1)
            if x < len(grid[0]) * 2:
                # Down half right 90 deg
                yield (x+1, y+1)
    elif y % 2 == 0:
        # Horizontal
        assert x % 2 == 1, "Half identifies line, not point"

        if x > 0:
            if x > 2:
                # Left horizontal
                yield (x-2, y)
            if y > 0:
                # Left half up 90 deg
                yield (x-1, y-1)
            if y < len(grid) * 2:
                # Left half down 90
                yield (x-1, y+1)
        if x < len(grid[0]) * 2:
            if x < (len(grid[0]) * 2) - 2:
                # Right horizontal
                yield (x+2, y)
            if y > 0:
                # Right half up 90 deg
                yield (x+1, y-1)
            if y < len(grid) * 2:
                # Right half down 90
                yield (x+1, y+1)
    else:
        raise Exception("Half identifies grid cell, not line")


def adj_breaks_conn(grid: List[List[str]], half: (int, int)) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
    x = half[0] // 2
    y = half[1] // 2
    if half[0] % 2 == 0:
        # Vertical
        assert half[1] % 2 == 1, "Half identifies line, not point"

        if x > 0 and x < len(grid[0]):
            return ((x-1, y), (x, y))
        return None
    elif half[1] % 2 == 0:
        # Horizontal
        assert half[0] % 2 == 1, "Half identifies line, not point"

        if y > 0 and y < len(grid):
            return ((x, y-1), (x, y))
        return None
    else:
        raise Exception("Half identifies grid cell, not line")


def path_to_dict(path: List[Tuple[int, int]]) -> Dict[Tuple[int, int], Tuple[int, int]]:
    d = {}
    for i in range(len(path)-1):
        d[path[i]] = path[i+1]
    d[path[-1]] = path[0]
    return d


def color_outside_path(grid: List[List[str]], path: List[Tuple[int, int]]) -> int:
    path_dict = path_to_dict(path)

    ## Find all the outside half positions
    outside_by_halfs = [] # Results
    outside_halfs_to_visit = [(0,1)] # Queue
    checked_halfs = set(outside_by_halfs) # Prevent checking the same half multiple times
    while len(outside_halfs_to_visit) > 0:
        outside_half = outside_halfs_to_visit.pop()

        for adj in adj_half_to_half_iter(grid, outside_half):
            if adj in checked_halfs:
                continue
            checked_halfs.add(adj)

            broken_conn_opt = adj_breaks_conn(grid, adj)
            if broken_conn_opt is not None:
                start, end = broken_conn_opt
                if (start in path_dict and path_dict[start] == end) or (end in path_dict and path_dict[end] == start):
                    continue # Cannot color through pipe path

            outside_by_halfs.append(adj)
            outside_halfs_to_visit.append(adj)

    ## Color each full position that
    ## 1. Is not a pipe
    ## 2. Is adjacent to an outside half
    outside_by_halfs = set(outside_by_halfs)
    # marked_grid = [list(row) for row in grid]
    marks = 0
    for x in range(len(grid[0])):
        for y in range(len(grid)):
            if (x, y) in path_dict:
                continue
            for adj in adj_half_to_full_pos_iter(grid, (x, y)):
                if adj in outside_by_halfs:
                    # marked_grid[y][x] = "#"
                    marks += 1
                    break

    return marks


def part2(filename: str) -> int:
    with open(filename, "r") as f:
        grid = list(map(lambda line: list(line.strip()), f.readlines()))

    path = traverse_from_start(grid)
    marks = color_outside_path(grid, path)

    return (len(grid) * len(grid[0])) - marks - len(path)


if __name__ == "__main__":
    p1 = part1("input")
    print(f"Part 1: {p1}")
    p2 = part2("input")
    print(f"Part 2: {p2}")
