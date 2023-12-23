import itertools
from typing import List, Dict, Optional


def identity_dict_rows(grid: List[str]) -> Dict[int, List[int]]:
    content_to_row_nums = {}
    for y, row in enumerate(grid):
        if row not in content_to_row_nums:
            content_to_row_nums[row] = [y]
        else:
            content_to_row_nums[row].append(y)

    idd = {}
    for row_nums in content_to_row_nums.values():
        for row_num in row_nums:
            idd[row_num] = row_nums
    return idd


def identity_dict_cols(grid: List[str]) -> Dict[int, List[int]]:
    inv_grid = ["".join(sl) for sl in zip(*grid)]
    return identity_dict_rows(inv_grid)


def find_flip(idd: Dict[int, List[int]], axis_len: int) -> Optional[int]:
    possible_flips = set(range(axis_len - 1))
    for pos, ident_idxs in idd.items():
        impossible_flips = set()
        for pf in possible_flips:
            delta = (pf + 1) - pos
            required_ident = pf + delta
            if required_ident >= 0 and required_ident < axis_len:
                if required_ident not in ident_idxs:
                    impossible_flips.add(pf)
        possible_flips -= impossible_flips

        if len(possible_flips) == 0:
            break

    if len(possible_flips) == 0:
        return None
    elif len(possible_flips) == 1:
        return next(iter(possible_flips))
    else:
        raise Exception("More than one flip")


def find_row_or_col_flip(grid: List[str]) -> int:
    row_idd = identity_dict_rows(grid)
    row_flip_opt = find_flip(row_idd, len(grid))
    if row_flip_opt is not None:
        return (row_flip_opt + 1) * 100

    col_idd = identity_dict_cols(grid)
    col_flip = find_flip(col_idd, len(grid[0]))
    assert col_flip is not None, "No flip found"
    return col_flip + 1


def read_grids(filename: str) -> List[List[str]]:
    with open(filename) as f:
        lines = [l.strip() for l in f.readlines()]

    return [list(v) for is_d, v in itertools.groupby(lines, lambda l: l == "") if not is_d]


def part1(filename: str) -> int:
    grids = read_grids(filename)
    return sum(find_row_or_col_flip(g) for g in grids)


if __name__ == '__main__':
    p1 = part1('input')
    print(f'Part 1: {p1}')
