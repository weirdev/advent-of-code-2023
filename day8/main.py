def read_lines(filename):
    with open(filename) as f:
        return f.readlines()

def parse_map_line(line):
    """Returns a hand and a bid from a line of text."""
    key, value = line.split("=")
    left, right = value.replace("(", "").replace(")", "").split(",")

    return (key.strip(), (left.strip(), right.strip()))

def part1(filename):
    lines = read_lines(filename)

    lr = lines[0].strip()
    lines = lines[2:]

    adj_map = {key: value for (key, value) in map(parse_map_line, lines)}

    steps = 0
    zzz_found = False
    key = "AAA"
    while not zzz_found:
        for dir in lr:
            left, right = adj_map[key]
            if dir == 'L':
                key = left
            else:
                key = right

            steps += 1

            if key == "ZZZ":
                zzz_found = True
                break

    return steps

def part2(filename):
    lines = read_lines(filename)

    lr = lines[0].strip()
    lines = lines[2:]

    adj_map = {key: value for (key, value) in map(parse_map_line, lines)}

    steps = 0
    zs_found = False
    keys = [k for k in adj_map.keys() if k[2] == "A"]
    print(keys)
    while not zs_found:
        for dir in lr:
            all_keys_end_z = True
            for i, key in enumerate(keys):
                left, right = adj_map[key]
                if dir == 'L':
                    key = left
                else:
                    key = right
                keys[i] = key

                if key[2] != "Z":
                    all_keys_end_z = False
            # print(keys)
            steps += 1

            if all_keys_end_z:
                zs_found = True
                break

    return steps

def part2_fast(filename):
    lines = read_lines(filename)

    lr = lines[0].strip()
    lines = lines[2:]

    adj_map = {key: value for (key, value) in map(parse_map_line, lines)}

    steps = 0
    seq_done = False
    keys = [k for k in adj_map.keys() if k[2] == "A"]
    # (k, lr_index): (steps, rep_start)
    seqs = [{} for k in keys] #[{(k, 0): (0, False)} for k in keys]
    print(seqs)
    while not seq_done:
        for lr_index, dir in enumerate(lr):
            steps += 1
            all_keys_done = True
            for i, key in enumerate(keys):
                if key is None:
                    continue
                left, right = adj_map[key]
                if dir == 'L':
                    key = left
                else:
                    key = right
                keys[i] = key

                seq = seqs[i]
                if key not in seq:
                    seq[(key, lr_index+1)] = (steps, False)
                    all_keys_done = False
                else:
                    seq[(key, lr_index+1)] = (seq[(key, lr_index+1)][0], True)
                    keys[i] = None
            print(keys)

            if all_keys_done:
                seq_done = True
                break

    print(seqs)

    start_points = [next(filter(lambda v: v[1], s.values()))[0] for s in seqs]
    print(start_points)
    cycle_lens = [len(seq) - sp for sp, seq in zip(start_points, seqs)]
    print(cycle_lens)
    z_locs = [[v[1] for k, v in seq.items() if k[0][2] == 'Z'] for seq in seqs]
    print(z_locs)

    return steps


def lcm(nums):
    def gcd(a, b):
        while b > 0:
            a, b = b, a % b
        return a

    a = nums[0]
    for bi in range(1, len(nums)):
        a = a // gcd(a, nums[bi]) * nums[bi]
    return a


def part2_3(filename):
    """
    They repeat, but not with the same LR iteration point (at least not for many iterations)
    """
    lines = read_lines(filename)

    lr = lines[0].strip()
    lines = lines[2:]

    adj_map = {key: value for (key, value) in map(parse_map_line, lines)}

    keys = [[k] for k in adj_map.keys() if k[2] == "A"]
    step_counts = []
    for i, key_seq in enumerate(keys):
        zs_found = False
        steps = 0
        while not zs_found:
            for dir in lr:
                key = key_seq[-1]
                left, right = adj_map[key]
                if dir == 'L':
                    key = left
                else:
                    key = right
                key_seq.append(key)

                steps += 1

                if key[2] == "Z":
                    step_counts.append(steps)
                    zs_found = True
                    break

    return lcm(step_counts)


if __name__ == "__main__":
    p1 = part1("input")
    print(f"Part 1: {p1}")
    p2 = part2_3('input')
    print(f"Part 2: {p2}")
