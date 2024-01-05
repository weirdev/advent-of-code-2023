from collections import deque
from typing import Deque, Dict, List, Optional, Set, Tuple
import itertools


# def dj(graph: List[str], start: (int, int)):
#     def enqueue(node: (int, int), prev: (int, int), dist: int, queue):
#         # heapq.heappush(queue, (heat_loss, node))
#         queue.append((dist, node, prev))

#     queue = deque()
#     enqueue(start, queue)
#     visited: Set[Tuple[int, Tuple[int, int]]] = set()
#     while len(queue) > 0:
#         # heat_loss, dn = heapq.heappop(queue)
#         dist, node, prev = queue.popleft()

#         if node in visited:
#             continue
#         visited[node] = prev

#         for axis in 0, 1:
#             for inv in -1, 1:
#                 dx = inv if axis == 0 else 0
#                 dy = inv if axis != 0 else 0
#                 x = node[0] + dx
#                 y = node[1] + dy
#                 if x < 0 or x >= len(graph[0]) or y < 0 or y >= len(graph):
#                     continue
#                 if graph[y][x] == "#":
#                     continue

#                 enqueue((x, y), node, dist + 1, queue)

#     raise Exception("Goal not reached")


def step_iter(graph: List[str], pos: (int, int)):
    for axis in 0, 1:
        for inv in -1, 1:
            dx = inv if axis == 0 else 0
            dy = inv if axis != 0 else 0
            x = pos[0] + dx
            y = pos[1] + dy
            if x < 0 or x >= len(graph[0]) or y < 0 or y >= len(graph):
                continue
            if graph[y][x] == "#":
                continue
            yield (x, y)


def explore(graph: List[str], start: (int, int), steps: int) -> {Tuple[int, int]}:
    frontier = {start}
    for _ in range(steps):
        frontier = {next_step for step in frontier for next_step in step_iter(graph, step)}
    return frontier


def read_grid(filename: str) -> List[str]:
    with open(filename, "r") as f:
        grid = [line.strip() for line in f.readlines()]

    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            if cell == "S":
                start = (x, y)

    return grid, start


def part1(filename: str) -> int:
    graph, start = read_grid(filename)
    locations = explore(graph, start, 64)
    return len(locations)


if __name__ == "__main__":
    p1 = part1("input")
    print(f"Part 1: {p1}")
