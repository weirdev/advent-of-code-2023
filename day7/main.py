from collections import Counter
from functools import cmp_to_key

CARD_RANKS_P1 = {c: i for i, c in enumerate("23456789TJQKA")}
CARD_RANKS_P2 = {c: i for i, c in enumerate("J23456789TQKA")}

def read_lines(filename):
    with open(filename) as f:
        return f.readlines()
    
def parse_line(line):
    """Returns a hand and a bid from a line of text."""
    hand, bid = line.strip().split(" ")
    return hand, int(bid)

def hand_category_p1(hand: str):
    counts = Counter(hand)
    if len(counts) == 1:
        return 10 # Five of a kind
    if len(counts) == 2:
        if 4 in counts.values():
            return 9 # Four of a kind
        return 8 # Full house
    if len(counts) == 3:
        if 3 in counts.values():
            return 7 # Three of a kind
        return 6 # Two pair
    if len(counts) == 4:
        return 5 # One pair
    return 4 # High card

def hand_category_p2(hand: str):
    counts = Counter(hand)
    js = counts.get("J", 0)
    if js == 5:
        return 10
    
    del counts["J"]
    oak = max(counts.values()) + js

    if oak == 5:
        return 10 # Five of a kind
    if oak == 4:
        return 9 # Four of a kind
    if len(counts) == 2:
        # We have a full house, possibly supplemented by jokers
        return 8 # Full house
    if oak == 3:
        return 7 # Three of a kind
    if oak == 2:
        if len(counts) == 3:
            return 6 # Two pair
        return 5 # One pair
    return 4 # High card

def compare_hands_p1(hand1, hand2):
    if hand1 == hand2:
        return 0
    
    cat1 = hand_category_p1(hand1)
    cat2 = hand_category_p1(hand2)
    if cat1 > cat2:
        return 1
    if cat1 < cat2:
        return -1
    for c1, c2 in zip(hand1, hand2):
        rank1 = CARD_RANKS_P1[c1]
        rank2 = CARD_RANKS_P1[c2]
        if rank1 > rank2:
            return 1
        if rank1 < rank2:
            return -1
    raise ValueError("Hands compare equal, but strings did not match")

def compare_hands_p2(hand1, hand2):
    if hand1 == hand2:
        return 0
    
    cat1 = hand_category_p2(hand1)
    cat2 = hand_category_p2(hand2)
    if cat1 > cat2:
        return 1
    if cat1 < cat2:
        return -1
    for c1, c2 in zip(hand1, hand2):
        rank1 = CARD_RANKS_P2[c1]
        rank2 = CARD_RANKS_P2[c2]
        if rank1 > rank2:
            return 1
        if rank1 < rank2:
            return -1
    raise ValueError("Hands compare equal, but strings did not match")
    
def part1(filename):
    hands = [parse_line(l) for l in read_lines(filename)]
    hands.sort(key=lambda h_b: cmp_to_key(compare_hands_p1)(h_b[0]))

    return sum(bid * (rank + 1) for (rank, (_, bid)) in enumerate(hands))

def part2(filename):
    hands = [parse_line(l) for l in read_lines(filename)]
    hands.sort(key=lambda h_b: cmp_to_key(compare_hands_p2)(h_b[0]))

    return sum(bid * (rank + 1) for (rank, (_, bid)) in enumerate(hands))
    
if __name__ == "__main__":
    print(f"Part 1: {part1("input")}")
    print(f"Part 2: {part2("input")}")
