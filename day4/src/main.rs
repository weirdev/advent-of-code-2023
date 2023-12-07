use std::collections::VecDeque;
use std::fs::File;
use std::io::{self, BufRead};
use std::path::Path;

fn read_lines<P>(filename: P) -> io::Result<io::Lines<io::BufReader<File>>>
where
    P: AsRef<Path>,
{
    let file = File::open(filename)?;
    Ok(io::BufReader::new(file).lines())
}

fn sum_lines<F>(filename: &str, mut line_to_num: F) -> u32
where
    F: FnMut(&[u8]) -> u32,
{
    read_lines(filename)
        .unwrap()
        .filter_map(Result::ok) // filter out possible errors
        .filter(|l| !l.trim().is_empty())
        .map(|l| line_to_num(l.as_bytes())) // convert each line to a number
        .sum()
}

fn line_to_num_p1(l: &[u8]) -> u32 {
    let mut nums = l.split_at(l.iter().position(|&c| c == b':').unwrap()).1;
    nums = &nums[1..];
    let (winners, mut yours) = nums.split_at(nums.iter().position(|&c| c == b'|').unwrap());
    yours = &yours[1..];

    let winning_nums = space_separated_nums_to_iter(winners);
    let your_nums = space_separated_nums_to_iter(yours);

    let mut winning_arr: [u32; 10] = [0; 10];
    for (i, num) in winning_nums.enumerate().take(10) {
        winning_arr[i] = num;
    }

    winning_arr.sort();

    let count = your_nums
        .filter(|&num| winning_arr.binary_search(&num).is_ok())
        .count();

    if count > 0 {
        2u32.pow(count as u32 - 1)
    } else {
        0
    }
}

fn line_to_num_p2(l: &[u8], ctx: &mut VecDeque<u32>) -> u32 {
    // Always one of each card, even if we havent earned an extra copy
    let count_of_this_card = ctx.pop_front().unwrap_or(1);

    let (_card, mut nums) = l.split_at(l.iter().position(|&c| c == b':').unwrap());
    nums = &nums[1..];
    let (winners, mut yours) = nums.split_at(nums.iter().position(|&c| c == b'|').unwrap());
    yours = &yours[1..];

    // let card_num = card_and_num_to_num(card);
    let winning_nums = space_separated_nums_to_iter(winners);
    let your_nums = space_separated_nums_to_iter(yours);

    let mut winning_arr: [u32; 10] = [0; 10];
    for (i, num) in winning_nums.enumerate().take(10) {
        winning_arr[i] = num;
    }

    winning_arr.sort();

    let count = your_nums
        .filter(|&num| winning_arr.binary_search(&num).is_ok())
        .count();

    for i in 0..count {
        if i < ctx.len() {
            ctx[i] += count_of_this_card;
        } else {
            // One original copy of this card + copies earned from each copy of this card
            ctx.push_back(1 + count_of_this_card);
        }
    }

    count_of_this_card
}

fn space_separated_nums_to_iter<'a>(l: &'a [u8]) -> impl Iterator<Item = u32> + 'a {
    l.split(|&c| c == b' ')
        .filter(|&w| !w.is_empty())
        .map(|w| unsafe { std::str::from_utf8_unchecked(w).parse().unwrap()})
}

fn card_and_num_to_num(l: &[u8]) -> u32 {
    let num_data = l.split(|&c| c == b' ')
        .last().unwrap();
    let num = unsafe { std::str::from_utf8_unchecked(num_data) };
    num.parse().unwrap()
}

fn main() {
    println!("Part 1: {}", sum_lines("input", line_to_num_p1));

    let mut ctx = VecDeque::new();
    println!("Part 2: {}", sum_lines("input", |l| line_to_num_p2(l, &mut ctx)));
    assert!(ctx.is_empty())
}
