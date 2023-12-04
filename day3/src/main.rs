use regex::Regex;

use std::fs::File;
use std::io::{self, BufRead};
use std::path::Path;

struct ContextWindow {
    part_sum: u32,
    lines: [Option<String>; 3],
}

impl ContextWindow {
    fn new() -> ContextWindow {
        ContextWindow {
            part_sum: 0,
            lines: [None, None, None],
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
        self.part_sum += sum_mid_line(&self.lines, re);
    }
}

fn read_lines<P>(filename: P) -> io::Result<io::Lines<io::BufReader<File>>>
where
    P: AsRef<Path>,
{
    let file = File::open(filename)?;
    Ok(io::BufReader::new(file).lines())
}

fn sum_lines(filename: &str, re: &Regex) -> u32 {
    let mut ctx = ContextWindow::new();
    read_lines(filename)
        .unwrap() // panic on possible file-reading errors
        .filter_map(Result::ok) // filter out possible errors
        .filter(|l| !l.trim().is_empty())
        .for_each(|l| ctx.add_line(l, &re));
    ctx.finialize(&re);

    ctx.part_sum
}

fn sum_mid_line(lines: &[Option<String>; 3], re: &Regex) -> u32 {
    if let Some(ln1) = &lines[1] {
        re.find_iter(ln1)
            .filter(|m| {
                search_range(m.start(), m.end(), ln1.len()).any(|(x, y)| {
                    lines[y as usize]
                        .as_ref()
                        .map(|ln| {
                            let c = ln[x..x + 1].chars().next().unwrap();
                            // Is a "symbol"? (not a digit or a period)
                            return c != '.' && !(c >= '0' && c <= '9');
                        })
                        .unwrap_or(false)
                })
            })
            .map(|m| m.as_str().parse::<u32>().unwrap())
            .sum::<u32>()
    } else {
        0
    }
}

fn search_range(
    num_start_incl: usize,
    num_end_excl: usize,
    line_len: usize,
) -> impl Iterator<Item = (usize, u8)> {
    // Diagonals should be checked,
    // so need one position to left and one to right of the text
    (num_start_incl.saturating_sub(1)..(num_end_excl + 1).min(line_len))
        .flat_map(|x| [0, 2].into_iter().map(move |y: u8| (x, y)))
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

fn main() {
    println!(
        "Part 1: {}",
        sum_lines("input", &Regex::new(r"\d+").unwrap())
    );
}
