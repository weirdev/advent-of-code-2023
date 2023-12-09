use std::fmt;
use std::fs::File;
use std::io::{self, BufRead};
use std::path::Path;

use itertools::Itertools;

#[derive(Clone, Copy)]
struct Mapping {
    src_start: u64,
    dst_start: u64,
    count: NumOrInf,
}

#[derive(Clone, Copy)]
enum NumOrInf {
    Finite(u64),
    Infinite,
}

impl PartialEq for NumOrInf {
    fn eq(&self, other: &Self) -> bool {
        match self {
            NumOrInf::Finite(s) => match other {
                NumOrInf::Finite(o) => s == o,
                NumOrInf::Infinite => false,
            },
            NumOrInf::Infinite => false,
        }
    }
}

impl PartialOrd for NumOrInf {
    fn partial_cmp(&self, other: &Self) -> Option<std::cmp::Ordering> {
        match self {
            NumOrInf::Finite(s) => match other {
                NumOrInf::Finite(o) => s.partial_cmp(o),
                NumOrInf::Infinite => Some(std::cmp::Ordering::Less),
            },
            NumOrInf::Infinite => match other {
                NumOrInf::Finite(_) => Some(std::cmp::Ordering::Greater),
                NumOrInf::Infinite => None,
            },
        }
    }
}

impl fmt::Display for NumOrInf {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            Self::Finite(c) => write!(f, "{}", c),
            Self::Infinite => write!(f, "inf"),
        }
    }
}

impl NumOrInf {
    fn unwrap(self) -> u64 {
        match self {
            NumOrInf::Finite(c) => c,
            NumOrInf::Infinite => panic!("Cannot unwrap infinite value!"),
        }
    }
}

impl fmt::Display for Mapping {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(
            f,
            "src_start: {} dst_start: {} count: {}",
            self.src_start, self.dst_start, self.count
        )
    }
}

impl Mapping {
    fn merge(self, b: Self) -> Option<Self> {
        let a_end_incl = match self.count {
            NumOrInf::Finite(c) => NumOrInf::Finite(self.dst_start + c - 1),
            NumOrInf::Infinite => NumOrInf::Infinite,
        };
        let b_end_incl = match b.count {
            NumOrInf::Finite(c) => NumOrInf::Finite(b.src_start + c - 1),
            NumOrInf::Infinite => NumOrInf::Infinite,
        };

        if b_end_incl < NumOrInf::Finite(self.dst_start)
            || a_end_incl < NumOrInf::Finite(b.src_start)
        {
            None
        } else {
            let start = std::cmp::max(self.dst_start, b.src_start);
            let end = match a_end_incl {
                NumOrInf::Finite(ae) => match b_end_incl {
                    NumOrInf::Finite(be) => NumOrInf::Finite(std::cmp::min(ae, be)),
                    NumOrInf::Infinite => a_end_incl,
                },
                NumOrInf::Infinite => b_end_incl,
            };
            let count = match end {
                NumOrInf::Finite(e) => NumOrInf::Finite(e - start + 1),
                NumOrInf::Infinite => NumOrInf::Infinite,
            };

            let m = Mapping {
                src_start: self.src_start + (start - self.dst_start), // a.src + How much did left bound shift?
                dst_start: b.dst_start + (start - b.src_start), // b.dst + How much did left bound shift?
                count,
            };

            Some(m)
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

// Two working processing strategies to solve the problem
enum MapProcessing {
    // Do lookups in each map in turn
    Waterfall,
    // Merge all maps into one and then do lookups
    MapMerge,
}

fn process_maps(filename: &str, mp: MapProcessing) -> u64 {
    let mut blocks = read_lines(filename)
        .unwrap()
        .filter_map(Result::ok) // filter out possible errors
        .group_by(|l| l.trim().is_empty());
    let mut blocks_iter = blocks
        .into_iter()
        .filter_map(|(e, b)| if e { None } else { Some(b) });

    let mut seeds_block = preprocess_block(blocks_iter.next().unwrap());

    let mut seeds_line = seeds_block.next().unwrap();
    let seeds_line = preprocess_line(&seeds_line);
    let seed_nums = seeds_line
        .split_at(seeds_line.iter().position(|&c| c == b':').unwrap())
        .1;
    let seed_nums = &seed_nums[1..];
    let seeds = seed_nums
        .split(|&c| c == b' ')
        .filter(|s| !s.is_empty())
        .map(|seed| {
            let s = unsafe { std::str::from_utf8_unchecked(seed) }.parse::<u64>();
            if let Err(_) = s {
                println!("{}", unsafe { std::str::from_utf8_unchecked(seed) });
                panic!("Invalid seed number");
            } else {
                s.unwrap()
            }
        })
        .collect::<Vec<u64>>();

    match mp {
        MapProcessing::Waterfall => {
            let mut results = seeds.clone();
            for map_block in blocks_iter {
                let mut map_block = preprocess_block(map_block);
                let mut _map_name_line = map_block.next().unwrap();

                let mut new_mappings = Vec::new();
                for map_line in map_block {
                    let map_line = preprocess_line(&map_line);
                    // Mind the order swap
                    let (dst_start, src_start, count): (u64, u64, u64) = map_line
                        .split(|&c| c == b' ')
                        .filter(|s| !s.is_empty())
                        .map(|n| {
                            unsafe { std::str::from_utf8_unchecked(n) }
                                .parse::<u64>()
                                .unwrap()
                        })
                        .collect_tuple()
                        .unwrap();

                    new_mappings.push(Mapping {
                        src_start,
                        dst_start,
                        count: NumOrInf::Finite(count),
                    });
                }
                new_mappings = with_implicit_mappings(new_mappings);

                for mut key in &mut results {
                    for &mapping in &new_mappings {
                        let src_end_excl = match mapping.count {
                            NumOrInf::Finite(c) => NumOrInf::Finite(mapping.src_start + c),
                            NumOrInf::Infinite => NumOrInf::Infinite,
                        };
                        if mapping.src_start <= *key && NumOrInf::Finite(*key) < src_end_excl {
                            *key = mapping.dst_start + (*key - mapping.src_start);
                            break;
                        }
                    }
                }
            }

            let mut least = None;
            for i in 0..results.len() {
                if let Some(l) = least {
                    if results[i] < l {
                        least = Some(results[i]);
                    }
                } else {
                    least = Some(results[i]);
                }
            }

            least.unwrap()
        }
        MapProcessing::MapMerge => {
            let mut mappings_red: Option<Vec<Mapping>> = None;
            for map_block in blocks_iter {
                let mut map_block = preprocess_block(map_block);
                let mut _map_name_line = map_block.next().unwrap();

                let mut new_mappings = Vec::new();
                for map_line in map_block {
                    let map_line = preprocess_line(&map_line);
                    let (dst_start, src_start, count): (u64, u64, u64) = map_line
                        .split(|&c| c == b' ')
                        .filter(|s| !s.is_empty())
                        .map(|n| {
                            unsafe { std::str::from_utf8_unchecked(n) }
                                .parse::<u64>()
                                .unwrap()
                        })
                        .collect_tuple()
                        .unwrap();

                    new_mappings.push(Mapping {
                        src_start,
                        dst_start,
                        count: NumOrInf::Finite(count),
                    });
                }
                new_mappings = with_implicit_mappings(new_mappings);

                if let Some(existing_mappings) = mappings_red {
                    // mappings.sort
                    let merged = merge_mappings(&existing_mappings, &new_mappings);
                    mappings_red = Some(with_implicit_mappings(merged));
                } else {
                    // mappings.sort
                    mappings_red = Some(new_mappings);
                }
            }

            let mut mappings = mappings_red.unwrap();
            mappings = with_implicit_mappings(mappings);

            let mut least_dst = None;
            for seed in seeds {
                for &mapping in &mappings {
                    let src_end = match mapping.count {
                        NumOrInf::Finite(c) => NumOrInf::Finite(mapping.src_start + c),
                        NumOrInf::Infinite => NumOrInf::Infinite,
                    };
                    if mapping.src_start <= seed && NumOrInf::Finite(seed) < src_end {
                        let offset = seed - mapping.src_start;
                        let dst = mapping.dst_start + offset;
                        if let Some(least) = least_dst {
                            if dst < least {
                                least_dst = Some(dst);
                            }
                        } else {
                            least_dst = Some(dst);
                        }
                    }
                }
            }

            least_dst.unwrap()
        }
    }
}

fn with_implicit_mappings(mut mappings: Vec<Mapping>) -> Vec<Mapping> {
    mappings.sort_by(|&a, &b| a.src_start.cmp(&b.src_start));

    let mut last_end_excl = NumOrInf::Finite(0);
    let mut i = 0;
    while i < mappings.len() {
        let mut mapping = mappings[i];
        match last_end_excl {
            NumOrInf::Infinite => panic!("Can't have additional mappings after infinite"),
            NumOrInf::Finite(last_end_excl) => {
                if mapping.src_start != 0
                    && mapping.src_start == last_end_excl
                    && mapping.dst_start
                        == mappings[i - 1].dst_start + mappings[i - 1].count.unwrap()
                {
                    // Merge the two mappings into one
                    mappings[i - 1].count = match mapping.count {
                        NumOrInf::Finite(c) => NumOrInf::Finite(c + mappings[i - 1].count.unwrap()),
                        NumOrInf::Infinite => NumOrInf::Infinite,
                    };
                    mapping = mappings[i - 1];
                    mappings.remove(i);
                    i -= 1;
                } else if mapping.src_start > last_end_excl {
                    mappings.insert(
                        i,
                        Mapping {
                            src_start: last_end_excl,
                            dst_start: last_end_excl, // 1:1 implict mapping
                            count: NumOrInf::Finite(mapping.src_start - last_end_excl),
                        },
                    );
                    i += 1;
                }
            }
        };
        last_end_excl = match mapping.count {
            NumOrInf::Finite(c) => NumOrInf::Finite(mapping.src_start + c),
            NumOrInf::Infinite => NumOrInf::Infinite,
        };
        i += 1;
    }

    if let NumOrInf::Finite(last_end_excl) = last_end_excl {
        mappings.push(Mapping {
            src_start: last_end_excl,
            dst_start: last_end_excl, // 1:1 implict mapping
            count: NumOrInf::Infinite,
        });
    }

    mappings
}

fn merge_mappings(src: &[Mapping], dst: &[Mapping]) -> Vec<Mapping> {
    let mut merged_mappings = Vec::new();
    for s in src {
        for &d in dst {
            if let Some(m) = s.merge(d) {
                merged_mappings.push(m);
            }
        }
    }

    merged_mappings
}

fn preprocess_block(block: impl Iterator<Item = String>) -> impl Iterator<Item = String> {
    block.filter(|l| !l.trim().is_empty())
}

fn preprocess_line(line: &String) -> &[u8] {
    line.trim().as_bytes()
}

fn main() {
    println!("Part 1: {}", process_maps("input", MapProcessing::MapMerge));
}
