mod trie;

use std::fs::File;
use std::io::{self, BufRead};
use std::path::Path;

use trie::{TrieNode, TrieSearchResult};

fn trie_insert_str(trie: &mut TrieNode<char, u32>, key: &str, value: u32) {
    trie.insert(&key.chars().collect::<Vec<char>>()[..], value);
}

fn build_num_trie() -> TrieNode<char, u32> {
    let mut trie = TrieNode::empty();
    trie_insert_str(&mut trie, "zero", 0);
    trie_insert_str(&mut trie, "one", 1);
    trie_insert_str(&mut trie, "two", 2);
    trie_insert_str(&mut trie, "three", 3);
    trie_insert_str(&mut trie, "four", 4);
    trie_insert_str(&mut trie, "five", 5);
    trie_insert_str(&mut trie, "six", 6);
    trie_insert_str(&mut trie, "seven", 7);
    trie_insert_str(&mut trie, "eight", 8);
    trie_insert_str(&mut trie, "nine", 9);

    trie
}

fn read_lines<P>(filename: P) -> io::Result<io::Lines<io::BufReader<File>>>
where
    P: AsRef<Path>,
{
    let file = File::open(filename)?;
    Ok(io::BufReader::new(file).lines())
}

fn sum_lines<F>(filename: &str, line_to_num: F) -> u32
where
    F: Fn(&str) -> u32,
{
    read_lines(filename)
        .unwrap() // panic on possible file-reading errors
        .filter_map(Result::ok) // filter out possible errors
        .filter(|l| !l.trim().is_empty())
        .map(|l| line_to_num(&l)) // convert each line to a number
        .sum()
}

fn digits_iter_to_num<I>(mut digits: I) -> u32
where
    I: Iterator<Item = u32>,
{
    let mut output = digits.next().unwrap();
    // Last digit may be same as first digit
    // (and first digit has already been consumed).
    if let Some(d) = digits.last() {
        output = output * 10 + d;
    } else {
        output = output * 10 + output;
    }

    output
}

fn line_to_num_only_digits(line: &str) -> u32 {
    // Convert the line to an array of characters.
    let digits = line
        .chars()
        // Filter out all non-digit characters.
        .filter_map(|c| c.to_digit(10));

    digits_iter_to_num(digits)
}

fn line_to_num_incl_words(
    line: &str,
    // trie: &Trie<&str, u32>
) -> u32 {
    // Convert the line to an array of characters.
    let trie = build_num_trie();
    let mut searches: Vec<TrieSearchResult<char, u32>> = vec![];

    let digits = line.chars().filter_map(|c| {
        if let Some(cd) = c.to_digit(10) {
            // Digit, so clear searches
            searches = vec![];
            return Some(cd);
        } else {
            // Not a digit, so search for a word.
            searches = searches
                .iter()
                .map(|r| r.search(&[c]))
                // Add new search starting with this character.
                .chain(std::iter::once(trie.search(&[c])))
                .filter_map(|r| r)
                .collect();

            if let Some(wd) = searches.iter().filter_map(|r| r.get_match()).next() {
                return Some(*wd);
            }
        }

        None
    });

    digits_iter_to_num(digits)
}

fn main() {
    // Part 1
    println!("Part 1: {}", sum_lines("input", line_to_num_only_digits));
    // Part 2
    println!("Part 2: {}", sum_lines("input", line_to_num_incl_words));
}
