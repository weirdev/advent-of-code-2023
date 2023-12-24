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


def approx_dict_rows(grid: List[str]) -> Dict[int, List[int]]:
    aidd = {}
    for i, rowi in enumerate(grid):
        for j, rowj in enumerate(grid[i+1:]):
            mismatches = [False for ci, cj in zip(rowi, rowj) if ci != cj]
            if len(mismatches) == 1:
                if i in aidd:
                    aidd[i].append(i + j + 1)
                else:
                    aidd[i] = [i + j + 1]

                if i + j + 1 in aidd:
                    aidd[i + j + 1].append(i)
                else:
                    aidd[i + j + 1] = [i]
    return aidd


def approx_dict_cols(grid: List[str]) -> Dict[int, List[int]]:
    inv_grid = ["".join(sl) for sl in zip(*grid)]
    return approx_dict_rows(inv_grid)


def find_exact_flip(idd: Dict[int, List[int]], axis_len: int) -> Optional[int]:
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


def dict_set_wo_overwrite(d, k, v):
    """Returns true iff k already in d"""
    if k not in d:
        d[k] = v
    return d[k]


def delta_abs(delta: int):
    """For our deltas calculated in find_*_flip(), -1 == 2 and 0 == 1"""
    if delta > 0:
        return delta
    return abs(delta) + 1


def find_approx_flip(idd: Dict[int, List[int]], aidd: Dict[int, List[int]], axis_len: int) -> Optional[int]:
    pos_perfect_flips = set(range(axis_len - 1))
    pos_approx_flips: Dict[int, int] = {}  # flip_pos -> delta_abs(delta)
    for pos in itertools.chain(idd.keys(), aidd.keys()):
        try:
            ident_idxs = idd[pos]
        except KeyError:
            ident_idxs = []
        try:
            approx_idxs = aidd[pos]
        except KeyError:
            approx_idxs = []

        for pf in list(itertools.chain(iter(pos_perfect_flips), pos_approx_flips.keys())):
            delta = (pf + 1) - pos
            required_ident = pf + delta
            if required_ident >= 0 and required_ident < axis_len:
                if required_ident not in ident_idxs:
                    # Remove perfect flip if present
                    removed_perfect = True
                    try:
                        pos_perfect_flips.remove(pf)
                    except KeyError:
                        removed_perfect = False
                    # Can we downgrade the perfect flip to an approximate one?
                    if required_ident in approx_idxs:
                        if removed_perfect:
                            # Only add approx match that we just removed from perfect matches
                            if dict_set_wo_overwrite(pos_approx_flips, pf, delta_abs(delta)) != delta_abs(delta):
                                del pos_approx_flips[pf] # Already using a different approximation for this flip, no longer an approx match
                        else:
                            if pf in pos_approx_flips:
                                if pos_approx_flips[pf] != delta_abs(delta):
                                    del pos_approx_flips[pf] # Already using a different approximation for this flip, no longer an approx match
                            else:
                                pos_approx_flips[pf] = delta_abs(delta)
                    else:
                        # No approx match either, remove if exists
                        pos_approx_flips.pop(pf, None)


        if len(pos_perfect_flips) + len(pos_approx_flips) == 0:
            break

    # Only interested in the approximate flip, not the exact one
    if len(pos_approx_flips) == 0:
        return None
    elif len(pos_approx_flips) == 1:
        return next(iter(pos_approx_flips))
    else:
        raise Exception("More than one approximate flip")


def find_row_or_col_flip_exact(grid: List[str]) -> int:
    row_idd = identity_dict_rows(grid)
    row_flip_opt = find_exact_flip(row_idd, len(grid))
    if row_flip_opt is not None:
        return (row_flip_opt + 1) * 100

    col_idd = identity_dict_cols(grid)
    col_flip = find_exact_flip(col_idd, len(grid[0]))
    assert col_flip is not None, "No flip found"
    return col_flip + 1


def find_row_or_col_flip_approx(grid: List[str]) -> int:
    row_idd = identity_dict_rows(grid)
    row_aidd = approx_dict_rows(grid)
    row_flip_opt = find_approx_flip(row_idd, row_aidd, len(grid))
    if row_flip_opt is not None:
        return (row_flip_opt + 1) * 100

    col_idd = identity_dict_cols(grid)
    col_aidd = approx_dict_cols(grid)
    col_flip = find_approx_flip(col_idd, col_aidd, len(grid[0]))
    assert col_flip is not None, "No approx flip found"
    return col_flip + 1


def read_grids(filename: str) -> List[List[str]]:
    with open(filename) as f:
        lines = [l.strip() for l in f.readlines()]

    return [list(v) for is_d, v in itertools.groupby(lines, lambda l: l == "") if not is_d]


def part1(filename: str) -> int:
    grids = read_grids(filename)
    return sum(find_row_or_col_flip_exact(g) for g in grids)


def part2(filename: str) -> int:
    grids = read_grids(filename)
    return sum(find_row_or_col_flip_approx(g) for g in grids)


if __name__ == '__main__':
    p1 = part1('input')
    print(f'Part 1: {p1}')
    p2 = part2('input')
    print(f'Part 2: {p2}')
