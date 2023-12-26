import heapq
from typing import List, Set, Tuple, Optional

class DerivedNode:
    """A 'node' in Dijkstra's algorithm that includes """
    def __init__(self, pos: (int, int), prev: Optional[Tuple[int, int]], straight_steps: int, path: List[Tuple[int, int]]):
        self.pos = pos
        self.prev = prev
        self.straight_steps = straight_steps
        # Ignore in derived methods
        self.path = path


    def _members(self):
        return (self.pos, self.prev, self.straight_steps)

    def __eq__(self, other):
        if type(other) is type(self):
            return self._members() == other._members()
        else:
            return False

    def __hash__(self):
        return hash(self._members())

    def __lt__(self, other):
        # Arbitrary but consistent ordering
        return hash(self) < hash(other)


def dj(graph: List[str], start: (int, int), goal: (int, int), min_straight_steps: int, max_straight_steps: int):
    def enqueue(heat_loss: int, node: DerivedNode, queue):
        heapq.heappush(queue, (heat_loss, node))

    queue = []
    enqueue(0, DerivedNode(start, None, 0, []), queue)
    visited: Set[DerivedNode] = set()
    while len(queue) > 0:
        heat_loss, dn = heapq.heappop(queue)
        if dn.pos == goal and dn.straight_steps >= min_straight_steps - 1:\
            return heat_loss, dn.path

        if dn in visited:
            continue
        visited.add(dn)

        if dn.prev is None:
            backwards = None
            forbidden_dirs = set()
            straight = None
        else:
            backwards = (dn.prev[0] - dn.pos[0], dn.prev[1] - dn.pos[1])
            forbidden_dirs = {backwards}
            straight = (-backwards[0], -backwards[1])
        # By the time we "realize" we are in a straight step seq,
        # we are already on the first step of it, plotting the second.
        # So the first step has straight_steps=0, the second one is 1, etc.
        # So to check >=n steps, check straight_steps >=n-1

        if dn.straight_steps < min_straight_steps - 1:
            if straight is not None:
                # Must go straight
                axis = 0 if straight[0] == 0 else 1
                if axis == 0:
                    forbidden_dirs.add((1, 0))
                    forbidden_dirs.add((-1, 0))
                else:
                    forbidden_dirs.add((0, 1))
                    forbidden_dirs.add((0, -1))
        elif dn.straight_steps >= max_straight_steps - 1:
            # Must not go straight
            forbidden_dirs.add(straight)

        for axis in 0, 1:
            for inv in -1, 1:
                dx = inv if axis == 0 else 0
                dy = inv if axis != 0 else 0
                if (dx, dy) in forbidden_dirs:
                    continue

                x = dn.pos[0] + dx
                y = dn.pos[1] + dy
                if x < 0 or x >= len(graph[0]) or y < 0 or y >= len(graph):
                    continue

                new_heat_loss = heat_loss + int(graph[y][x])
                straight_steps = dn.straight_steps + 1 if (dx, dy) == straight else 0
                enqueue(new_heat_loss, DerivedNode((x, y), dn.pos, straight_steps, dn.path + [(x, y)]), queue)

    raise Exception("Goal not reached")


def read_grid(filename: str) -> List[List[str]]:
    with open(filename) as f:
        return [l.strip() for l in f.readlines()]


def part1(filename: str):
    graph = read_grid(filename)
    start = (0, 0)
    end = (len(graph[0])-1, len(graph)-1)
    hl, path = dj(graph, start, end, 0, 3)
    # print(path_str(graph, path))
    return hl


def part2(filename: str):
    graph = read_grid(filename)
    start = (0, 0)
    end = (len(graph[0])-1, len(graph)-1)
    hl, path = dj(graph, start, end, 4, 10)
    # print(path_str(graph, path))
    return hl


def path_str(grid: List[str], path: List[Tuple[int, int]]):
    path = set(path)
    return "\n".join("".join("*" if (x, y) in path else hl for x, hl in enumerate(row)) for y, row in enumerate(grid))


if __name__ == '__main__':
    p1 = part1('input')
    print(f'Part 1: {p1}')
    p2 = part2('input')
    print(f'Part 2: {p2}')
