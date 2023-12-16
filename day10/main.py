from typing import List, Iterator, Tuple

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

def connected_omni_dir(grid: List[List[str]], x: int, y: int) -> [(int, int)]:
    connections = []
    for i, j in adj_points_iter(grid, x, y):
        if i == x and j == y:
            continue
        char = grid[j][i]
        if char == 'S': # (x,y) is probably the only S, but explicitly handle connecting to one just in case
            # connections.append((i, j))
            raise Exception("Omni direction connection (S) to (another) S")
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

def traverse(grid: List[List[str]], start: (int, int), start_prev: (int, int), end: (int, int)) -> int:
    path = [start_prev, start]
    while path[-1] != end:
        path.append(get_next_point(grid, path[-1], path[-2]))

    return len(path)

def traverse_from_start(grid: List[List[str]]) -> int:
    start_prev, start, end = get_start_first_and_last_points(grid)
    return traverse(grid, start, start_prev, end)


def part1(filename: str) -> int:
    with open(filename, "r") as f:
        lines = list(map(lambda line: list(line.strip()), f.readlines()))

    path_len = traverse_from_start(lines)

    return path_len // 2


if __name__ == "__main__":
    p1 = part1("input")
    print(f"Part 1: {p1}")
