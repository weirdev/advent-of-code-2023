// To anyone reading this code: Please know I'm aware it's a monstrosity.
use regex::Regex;

use std::fs::File;
use std::io::{self, BufRead};
use std::path::Path;

struct ContextWindow<F1, F2, F3, F4> {
    part_sum: u32,
    lines: [Option<String>; 3],
    adj_match: F1,
    score_adj_match: F2,
    score_adj_match_horiz_seq_once: bool,
    agg_matches: F3,
    line_agg: F4,
}

impl<F1, F2, F3, F4> ContextWindow<F1, F2, F3, F4>
where
    F1: Fn(char) -> bool,
    F2: Fn((usize, u8), &[Option<String>; 3]) -> u32,
    F3: Fn(&mut dyn Iterator<Item = u32>) -> u32,
    F4: Fn(regex::Match<'_>, u32) -> u32,
{
    fn new(
        adj_match: F1,
        score_adj_match: F2,
        score_adj_match_horiz_seq_once: bool,
        agg_matches: F3,
        line_agg: F4,
    ) -> ContextWindow<F1, F2, F3, F4> {
        ContextWindow {
            part_sum: 0,
            lines: [None, None, None],
            adj_match,
            score_adj_match,
            score_adj_match_horiz_seq_once,
            agg_matches,
            line_agg,
        }
    }

    pub fn add_line(&mut self, line: String, re: &Regex) {
        self.add_line_or_none(Some(line), re)
    }

    pub fn finialize(&mut self, re: &Regex) {
        self.add_line_or_none(None, re)
    }

    fn add_line_or_none(&mut self, line: Option<String>, re: &Regex) {
        self.lines.rotate_left(1);
        self.lines[2] = line;
        self.part_sum += sum_mid_line(
            &self.lines,
            re,
            &self.adj_match,
            &self.score_adj_match,
            self.score_adj_match_horiz_seq_once,
            &self.agg_matches,
            &self.line_agg,
        );
    }
}

struct PeekingIterator<I>
where
    I: Iterator,
{
    iter: I,
    peeked: Option<I::Item>,
}

impl<I> PeekingIterator<I>
where
    I: Iterator,
{
    fn new(mut iter: I) -> PeekingIterator<I> {
        let nxt = iter.next();
        PeekingIterator {
            iter: iter,
            peeked: nxt,
        }
    }
}

impl<I> Iterator for PeekingIterator<I>
where
    I: Iterator,
    I::Item: Copy,
{
    type Item = (I::Item, Option<I::Item>);

    fn next(&mut self) -> Option<Self::Item> {
        if let Some(r) = self.peeked.take() {
            self.peeked = self.iter.next();
            Some((r, self.peeked))
        } else {
            None
        }
    }
}

fn read_lines<P>(filename: P) -> io::Result<io::Lines<io::BufReader<File>>>
where
    P: AsRef<Path>,
{
    let file = File::open(filename)?;
    Ok(io::BufReader::new(file).lines())
}

fn sum_lines<F1, F2, F3, F4>(
    filename: &str,
    re: &Regex,
    adj_match: F1,
    score_adj_match: F2,
    score_adj_match_horiz_seq_once: bool,
    agg_matches: F3,
    line_agg: F4,
) -> u32
where
    F1: Fn(char) -> bool,
    F2: Fn((usize, u8), &[Option<String>; 3]) -> u32,
    F3: Fn(&mut dyn Iterator<Item = u32>) -> u32,
    F4: Fn(regex::Match<'_>, u32) -> u32,
{
    let mut ctx = ContextWindow::new(
        adj_match,
        score_adj_match,
        score_adj_match_horiz_seq_once,
        agg_matches,
        line_agg,
    );
    read_lines(filename)
        .unwrap() // panic on possible file-reading errors
        .filter_map(Result::ok) // filter out possible errors
        .filter(|l| !l.trim().is_empty())
        .for_each(|l| ctx.add_line(l, &re));
    ctx.finialize(&re);

    ctx.part_sum
}

fn sum_mid_line<F1, F2, F3, F4>(
    lines: &[Option<String>; 3],
    re: &Regex,
    adj_match: &F1,
    score_adj_match: &F2,
    score_adj_match_horiz_seq_once: bool,
    agg_matches: &F3,
    line_agg: &F4,
) -> u32
where
    F1: Fn(char) -> bool,
    F2: Fn((usize, u8), &[Option<String>; 3]) -> u32,
    F3: Fn(&mut dyn Iterator<Item = u32>) -> u32,
    F4: Fn(regex::Match<'_>, u32) -> u32,
{
    if let Some(ln1) = &lines[1] {
        re.find_iter(ln1)
            .map(|m| {
                (
                    m,
                    agg_matches(
                        &mut PeekingIterator::new(search_range(m.start(), m.end(), ln1.len())).map(
                            |((x, y), next_coord)| {
                                lines[y as usize]
                                    .as_ref()
                                    .and_then(|ln| {
                                        let c = ln[x..x + 1].chars().next().unwrap();
                                        if adj_match(c) {
                                            if score_adj_match_horiz_seq_once {
                                                if let Some((nx, ny)) = next_coord {
                                                    if ny == y && nx == x + 1 {
                                                        let next_matches_too = lines[ny as usize]
                                                            .as_ref()
                                                            .map(|ln| {
                                                                let nc = ln[nx..nx + 1]
                                                                    .chars()
                                                                    .next()
                                                                    .unwrap();
                                                                adj_match(nc)
                                                            })
                                                            .unwrap_or(false);
                                                        if next_matches_too {
                                                            // Skip this, score only the rightmost
                                                            return None;
                                                        }
                                                    }
                                                }
                                            }

                                            Some((x, y))
                                        } else {
                                            None
                                        }
                                    })
                                    .map(|coord| score_adj_match(coord, lines))
                                    .unwrap_or(0)
                            },
                        ).filter(|s| *s > 0),
                    ),
                )
            })
            .filter(|(_, s)| *s > 0)
            .map(|(m, s)| line_agg(m, s))
            .sum::<u32>()
    } else {
        0
    }
}

// Requires that, within the same line (y axis),
// adjacent coordinates are returned left to right
// (in increasing order of x axis)
fn search_range(
    num_start_incl: usize,
    num_end_excl: usize,
    line_len: usize,
) -> impl Iterator<Item = (usize, u8)> {
    // Diagonals should be checked,
    // so need one position to left and one to right of text's x coordinate
    [0, 2]
        .into_iter()
        .flat_map(move |y| {
            (num_start_incl.saturating_sub(1)..(num_end_excl + 1).min(line_len))
                .map(move |x| (x, y))
        })
        // Characters on same line as number,
        // one to the left and one to the right
        .chain(
            std::iter::once(0u8)
                .filter(move |_| num_start_incl > 0)
                .map(move |_| (num_start_incl - 1, 1)),
        )
        .chain(
            std::iter::once(0)
                .filter(move |_| num_end_excl < line_len)
                .map(move |_| (num_end_excl, 1)),
        )
}

fn score_part3_match((x, y): (usize, u8), lines: &[Option<String>; 3]) -> u32 {
    let mut start_x = x;
    while start_x > 0
        && lines[y as usize].as_ref().unwrap()[start_x - 1..start_x]
            .chars()
            .next()
            .unwrap()
            .is_ascii_digit()
    {
        start_x -= 1;
    }
    let mut end_x = x;
    while end_x < lines[y as usize].as_ref().unwrap().len()
        && lines[y as usize].as_ref().unwrap()[end_x..end_x + 1]
            .chars()
            .next()
            .unwrap()
            .is_ascii_digit()
    {
        end_x += 1;
    }

    let num_found = lines[y as usize].as_ref().unwrap()[start_x..end_x]
        .parse::<u32>()
        .unwrap();
    println!("Found {} at ({}, {})", num_found, x, y);
    num_found
}

fn main() {
    println!(
        "Part 1: {}",
        sum_lines(
            "input",
            &Regex::new(r"\d+").unwrap(),
            // Is a "symbol"? (not a digit or a period)
            |c| c != '.' && !(c >= '0' && c <= '9'),
            // Each match scores as 1
            |_, _| 1,
            false,
            |iter| iter.sum(),
            |m, _| m.as_str().parse::<u32>().unwrap(),
        )
    );
    println!(
        "Part 2: {}",
        sum_lines(
            "input",
            &Regex::new(r"\*").unwrap(),
            // Match any digit
            |c| c.is_ascii_digit(),
            score_part3_match,
            true,
            // Product of exactly 2 matches, else 0
            |iter| {
                let mut iter = iter.fuse();
                let p1 = iter.next().unwrap_or(0);
                let p2 = iter.next().unwrap_or(0);
                if iter.any(|s| s != 0) {
                    0
                } else {
                    println!("Adj nums: {} {}", p1, p2);
                    p1 * p2
                }
            },
            |_, p| p,
        )
    );
}
