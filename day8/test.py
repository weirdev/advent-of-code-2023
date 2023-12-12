def align(cycle_1_len, offset_1, cycle_2_len, offset_2):
    """Returns the alignment of two cycles"""
    z = (offset_2 - offset_1) % cycle_2_len
    a = 0
    while (cycle_1_len * a) % cycle_2_len != z:
        a += 1

    while (cycle_1_len * a) + offset_1 - offset_2 < 0:
        a += cycle_2_len

    return a, ((cycle_1_len * a) + offset_1 - offset_2) // cycle_2_len

def test_align(cycle_1_len, offset_1, cycle_2_len, offset_2):
    print(f"{cycle_1_len}a + {offset_1} = {cycle_2_len}b + {offset_2}")
    a, b = align(cycle_1_len, offset_1, cycle_2_len, offset_2)
    print(f"a: {a}, b: {b}")
    left = cycle_1_len*a + offset_1
    right = cycle_2_len*b + offset_2
    print(f"{left} == {right}")
    assert left == right


if __name__ == "__main__":
    test_align(5, 3, 7, 5)
    print()

    test_align(5, 3, 6, 4)
    print()

    test_align(53, 20, 67, 10)
    print()