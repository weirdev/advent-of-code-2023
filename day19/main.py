from typing import List, Tuple, Dict, Optional
import itertools
from collections import deque
from math import prod


class Condition:
    def __init__(self, key: str, op: str, val: int):
        self.key = key
        self.op = op
        self.val = val

    def __call__(self, part: Dict[str, int]) -> bool:
        if self.op == '>':
            return part[self.key] > self.val
        else:
            assert self.op == '<'
            return part[self.key] < self.val

    def apply_to_bounds(self, bounds: {str: Tuple[int, int]}) -> Optional[Dict[str, Tuple[int, int]]]:
        low_incl, high_incl = bounds[self.key]

        bounds = bounds.copy()
        if self.op == '>':
            if high_incl <= self.val: # highest value <= the exclusive lowest value allowed by this condition
                return None
            bounds[self.key] = (max(low_incl, self.val + 1), high_incl)
        else:
            assert self.op == '<'
            if low_incl >= self.val: # lowest value >= the exclusive highest value allowed by this condition
                return None
            bounds[self.key] = (low_incl, min(high_incl, self.val - 1))

        return bounds

    def __neg__(self) -> 'Condition':
        if self.op == '>':
            return Condition(self.key, '<', self.val + 1)
        else:
            assert self.op == '<'
            return Condition(self.key, '>', self.val - 1)


def read_file(filename: str) -> (Dict[str, List[Tuple[Optional[Condition], str]]], List[Dict[str, int]]):
    with open(filename) as f:
        lines = [l.strip() for l in f.readlines()]

    workflows_iter, parts_iter = (list(v) for is_d, v in itertools.groupby(lines, lambda l: l == "") if not is_d)

    workflow_dict: {str: List[Tuple[Optional[Condition], str]]} = {}
    for w in workflows_iter:
        name, steps_str = w.split('{')
        steps_iter = steps_str[:-1].split(',')
        steps: [Tuple[Optional[Condition], str]] = []
        for s in steps_iter[:-1]:
            cond, target = s.split(':')
            steps.append((Condition(cond[0], cond[1], int(cond[2:])), target))
        steps.append((None, steps_iter[-1])) # Last step has no condition

        workflow_dict[name] = steps

    parts: [Dict[str, int]] = []
    for ratings in parts_iter:
        ratings = ratings[1:-1].split(",")
        ratings_dict: Dict[str, int] = {}
        for r in ratings:
            k, v = r.split('=')
            ratings_dict[k] = int(v)

        parts.append(ratings_dict)

    return workflow_dict, parts


def process_part(part: {str: int}, workflow_dict: {str: List[Tuple[Optional[Condition], str]]}) -> int:
    workflow = workflow_dict['in']
    while True:
        target = run_workflow(part, workflow)
        if target == 'A':
            return sum(part.values())
        elif target == 'R':
            return 0
        else:
            workflow = workflow_dict[target]


def run_workflow(part: {str: int}, workflow: List[Tuple[Optional[Condition], str]]) -> str:
    for cond, target in workflow:
        if cond:
            if cond(part):
                return target
        else:
            return target # fallback

    raise Exception("No matching condition (including fallback) found")


def part1(filename: str) -> int:
    workflow_dict, parts = read_file(filename)
    return sum(process_part(part, workflow_dict) for part in parts)


def wf_combinations(workflow_dict: {str: List[Tuple[Optional[Condition], str]]}) -> int:
    explore_queue = deque([({k: (1, 4000) for k in "xmas"}, 'in')]) # [(bounds: {k: (low_incl, high_incl)}, wf)]
    visited = {'in'}
    passes = []

    while len(explore_queue) > 0:
        bounds, workflow = explore_queue.popleft()

        for cond, target in workflow_dict[workflow]:
            new_bounds = bounds
            if cond is not None:
                new_bounds = cond.apply_to_bounds(new_bounds)
                # We only go into the next step if we did not satisify the current condition.
                inv_cond = -cond
                bounds = inv_cond.apply_to_bounds(bounds)

            if new_bounds is not None: # Cannot match?
                if target == 'R':
                    pass
                elif target == 'A':
                    passes.append(new_bounds)
                else:
                    if target not in visited:
                        visited.add(target)
                        explore_queue.append((new_bounds, target))

            if bounds is None:
                # No values can satisify the next step(s) so skip
                break

    return passes


def part2(filename: str) -> int:
    workflow_dict, _ = read_file(filename)
    passing_bounds = wf_combinations(workflow_dict)
    return combinations(passing_bounds)


def compose_conjunction(bound_a: Tuple[int, int], bound_b: Tuple[int, int]) -> Tuple[int, int]:
    low_a, high_a = bound_a
    low_b, high_b = bound_b

    new_bound = (max(low_a, low_b), min(high_a, high_b))
    if new_bound[0] <= new_bound[1]:
        return new_bound
    else:
        return None


def combinations(bounds_list: [{str: Tuple[int, int]}]) -> int:
    """Calculate the number of possible combinations of values that satisfy the given sets of bounds.
    This was created to handle cases where there are overlapping bounds, but given the structure of
    the problem that wasn't necessary, so we only run the outer loop for i=1. The remainder is probably
    buggy."""
    total = 0
    for i in range(1, len(bounds_list)+1):
        inv = ((i%2)*2) - 1
        idxs = list(range(i))
        j = i - 1
        all_none = True
        while True:
            bounds = bounds_list[idxs[0]].copy()
            for idx in idxs[1:]:
                for k in "xmas":
                    bounds[k] = compose_conjunction(bounds[k], bounds_list[idx][k])
                    if bounds[k] is None:
                        bounds = None
                        break
                if bounds is None:
                    break
            if bounds is not None:
                all_none = False
                comb = prod(high_incl - low_incl + 1 for low_incl, high_incl in bounds.values())
                total += comb * inv

            while j >= 0 and idxs[j] >= len(bounds_list)-1:
                j -= 1
            if j < 0:
                break

            idxs[j] += 1
            if j < i:
                idxs[j+1:] = [0] * (len(idxs)-j-1)
                j = i - 1

        # if all_none:
        #     break
        break

    return total


if __name__ == '__main__':
    p1 = part1('input')
    print(f'Part 1: {p1}')
    p2 = part2('input')
    print(f'Part 2: {p2}')
