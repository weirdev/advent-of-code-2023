from typing import List, Tuple, Dict


def hole_filling_combinations(terrain: List[str], contig_seqs: List[int], memo: Dict[Tuple[int, int], int]) -> int:
    """
    Given a list of must-fill and can-fill holes, returns the number of ways to fill them.
    The holes are assumed to be in ascending order.
    """
    def memo_set_get(terrain: List[str], contig_seqs: List[int]) -> int:
        key = (len(terrain), len(contig_seqs))
        if key not in memo:
            memo[key] = hole_filling_combinations(terrain, contig_seqs, memo)
        return memo[key]

    if len(contig_seqs) == 0:
        for c in terrain:
            if c == "#":
                return 0
        return 1

    i = 0
    while i < len(terrain) and terrain[i] == ".":
        i += 1

    if i >= len(terrain):
        # Reached the end and stil have sequences left
        return 0

    if terrain[i] == "#":
        # Must eat next seq
        next_seq_len = contig_seqs[0]
        seq_end = i + next_seq_len
        if seq_end > len(terrain):
            return 0

        while i < seq_end:
            if terrain[i] != "#" and terrain[i] != "?":
                return 0
            i += 1
        if i < len(terrain) and terrain[i] == "#":
            # Partially eaten sequence
            return 0

        # i+1, because must be . or ? treated as . so seq ends
        return memo_set_get(terrain[i+1:], contig_seqs[1:])
    elif terrain[i] == "?":
        # Can eat next seq
        maybe_loc = i
        next_seq_len = contig_seqs[0]
        seq_end = i + next_seq_len
        if seq_end > len(terrain):
            return 0

        eat_failed = False
        while i < seq_end:
            if terrain[i] != "#" and terrain[i] != "?":
                eat_failed = True
                break
            i += 1
        if i < len(terrain) and terrain[i] == "#":
            # Partially eaten sequence
            eat_failed = True

        no_eat_maybe = memo_set_get(terrain[maybe_loc+1:], contig_seqs)
        if eat_failed:
            return no_eat_maybe
        else:
            # i+1, because must be . or ? treated as . so seq ends
            return no_eat_maybe + memo_set_get(terrain[i+1:], contig_seqs[1:])
    else:
        raise Exception(f"Unexpected terrain char {terrain[i]}")


def line_to_terrain_and_contig_steps(line: str) -> Tuple[List[str], List[int]]:
    terrain, seq_str = line.split(" ")
    return (terrain, [int(x) for x in seq_str.split(",")])


def part1(filename: str) -> int:
    with open(filename) as f:
        lines = [line.strip() for line in f.readlines()]

    inputs = [line_to_terrain_and_contig_steps(line) for line in lines]

    return sum(hole_filling_combinations(terrain, contig_seqs, {}) for terrain, contig_seqs in inputs)


def unfold_terrain(terrain: str) -> List[str]:
    return "?".join([terrain]*5)


def unfold_seqs(seqs: List[int]) -> List[int]:
    return seqs*5


def part2(filename: str) -> int:
    with open(filename) as f:
        lines = [line.strip() for line in f.readlines()]

    inputs = [line_to_terrain_and_contig_steps(line) for line in lines]
    inputs = [(unfold_terrain(terrain), unfold_seqs(contig_seqs)) for terrain, contig_seqs in inputs]

    return sum(hole_filling_combinations(terrain, contig_seqs, {}) for terrain, contig_seqs in inputs)


if __name__ == '__main__':
    p1 = part1('input')
    print(f'Part 1: {p1}')
    p2 = part2('input')
    print(f'Part 2: {p2}')
