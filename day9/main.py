from typing import List

def all_zeros(seq: List[int]) -> bool:
    return all(x==0 for x in seq)

def first_order_derivatives(seq: List[int]) -> List[int]:
    assert len(seq) > 1
    return [seq[i+1] - seq[i] for i in range(len(seq)-1)]

def derivatives_all_orders(seq: List[int]) -> List[List[int]]:
    derivatives = [seq]
    while not all_zeros(derivatives[-1]):
        derivatives.append(first_order_derivatives(derivatives[-1]))
    return derivatives

def predict_next(derivatives: List[List[int]]) -> int:
    assert len(derivatives) > 1
    assert derivatives[-1][-1] == 0

    return sum(d_seq[-1] for d_seq in derivatives)


def predict_prev(derivatives: List[List[int]]) -> int:
    assert len(derivatives) > 1
    assert derivatives[-1][-1] == 0

    # 0 - 1 + 2 - 3 + ...
    return sum(d_seq[0] * (((i % 2) * 2) - 1) * -1 for i, d_seq in enumerate(derivatives))


def read_lines(filename: str) -> List[str]:
    with open(filename) as f:
        return f.readlines()

def parse_line(line: str) -> List[int]:
    return list(map(int, line.strip().split(" ")))


def part1(filename: str) -> int:
    lines = read_lines(filename)
    parsed_lines = map(parse_line, lines)

    return sum(predict_next(derivatives_all_orders(parsed_line)) for parsed_line in parsed_lines)


def part2(filename: str) -> int:
    lines = read_lines(filename)
    parsed_lines = map(parse_line, lines)

    return sum(predict_prev(derivatives_all_orders(parsed_line)) for parsed_line in parsed_lines)


if __name__ == "__main__":
    p1 = part1("input")
    print(f"Part 1: {p1}")
    p2 = part2("input")
    print(f"Part 2: {p2}")
