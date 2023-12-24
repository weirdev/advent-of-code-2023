from typing import List, Optional, Tuple


def read_steps(filename: str) -> List[str]:
    with open(filename) as f:
        line = f.readline().strip()

    return line.split(",")


def HASH(s: str, cv: int = 0):
    if len(s) == 0:
        return cv

    cv += ord(s[0])
    cv *= 17
    cv %= 256
    return HASH(s[1:], cv)


def part1(filename: str) -> int:
    return sum(HASH(step) for step in read_steps(filename))


def parse_step(step: str) -> (str, str, Optional[int]):
    """(label, operator, focal_len)"""
    if "=" in step:
        label, fl_str = step.split("=")
        return (label, "=", int(fl_str))
    else:
        return (step[:-1], "-", None)


def focusing_power(box_num: int, lenses: List[Tuple[str, int]]) -> int:
    return sum((1+box_num)*(slot+1)*focal_len for slot, (_, focal_len) in enumerate(lenses))


def part2(filename: str) -> int:
    steps = [parse_step(step) for step in read_steps(filename)]

    boxes = [[] for _ in range(256)]
    for label, op, fl in steps:
        box = HASH(label)
        if op == "=":
            cur_pos = next((i for i, (l, f) in enumerate(boxes[box]) if l == label), None)
            if cur_pos is not None:
                boxes[box][cur_pos] = (label, fl)
            else:
                boxes[box].append((label, fl))
        else:
            assert op == "-"
            boxes[box] = [b for b in boxes[box] if b[0] != label]

    return sum(focusing_power(box, lenses) for box, lenses in enumerate(boxes))


if __name__ == '__main__':
    p1 = part1('input')
    print(f'Part 1: {p1}')
    p2 = part2('input')
    print(f'Part 2: {p2}')
