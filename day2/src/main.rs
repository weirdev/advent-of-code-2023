use regex::Regex;

use std::fs::File;
use std::io::{self, BufRead};
use std::path::Path;

#[derive(Clone, Copy)]
struct Draw {
    red_cubes: u32,
    green_cubes: u32,
    blue_cubes: u32,
}

impl Draw {
    fn from_vec(cubes: Vec<(u32, &str)>) -> Draw {
        let mut draw = Draw {
            red_cubes: 0,
            green_cubes: 0,
            blue_cubes: 0,
        };

        if cubes.len() > 3 {
            panic!("Too many cubes in draw: {:?}", cubes);
        }

        if cubes.len() == 0 {
            panic!("No cubes in draw");
        }

        for (num, color) in cubes {
            let to_update = match color {
                "red" => &mut draw.red_cubes,
                "green" => &mut draw.green_cubes,
                "blue" => &mut draw.blue_cubes,
                _ => panic!("Invalid color: {}", color),
            };
            if *to_update != 0 {
                panic!("Duplicate color: {}", color);
            }
            *to_update += num;
        }

        draw
    }

    fn max_by_color(&self, other: Draw) -> Draw {
        Draw {
            red_cubes: self.red_cubes.max(other.red_cubes),
            green_cubes: self.green_cubes.max(other.green_cubes),
            blue_cubes: self.blue_cubes.max(other.blue_cubes),
        }
    }
}

struct Game {
    game_num: u32,
    draws: Vec<Draw>,
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

fn create_game_regexes() -> (Regex, Regex, Regex) {
    // Game 1: 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green
    let cube_draw_re = Regex::new(r"(?<cube_count>\d+) (?<cube_color>[[:alpha:]]+)").unwrap();
    // Same as above, but with no capture groups
    let cube_draw = r"\d+ [[:alpha:]]+";

    let draw_re =
        Regex::new(format!(r"(?<cube_draws>{}(?:, {})*)", cube_draw, cube_draw).as_str()).unwrap();
    // Same as above, but with no capture groups
    let draw = format!(r"{}(?:, {})*", cube_draw, cube_draw);

    let game_re =
        Regex::new(format!(r"Game (?<game_num>\d+): (?<draws>{}(?:; {})*)", draw, draw).as_str())
            .unwrap();

    (cube_draw_re, draw_re, game_re)
}

fn parse_game(game: &str, cube_draw_re: &Regex, draw_re: &Regex, game_re: &Regex) -> Game {
    let game_caps = game_re.captures(game).unwrap();

    let game_num = game_caps["game_num"].parse::<u32>().unwrap();

    let draws = game_caps.name("draws").unwrap().as_str();
    let draws_parsed = draws
        .split("; ")
        .map(|d| draw_re.captures(d).unwrap())
        .map(|d| d.name("cube_draws").unwrap().as_str())
        .map(|cds| {
            cds.split(", ")
                .map(|cd| cube_draw_re.captures(cd).unwrap())
                .map(|cd| {
                    (
                        cd["cube_count"].parse::<u32>().unwrap(),
                        cd.name("cube_color").unwrap().as_str(),
                    )
                })
                .collect::<Vec<(u32, &str)>>()
        })
        .map(|cds| Draw::from_vec(cds))
        .collect::<Vec<Draw>>();

    Game {
        game_num,
        draws: draws_parsed,
    }
}

fn game_line_to_num_fn(draw_limits: Draw) -> impl Fn(&str) -> u32 {
    let (cube_draw_re, draw_re, game_re) = create_game_regexes();
    move |line: &str| -> u32 {
        let game = parse_game(line, &cube_draw_re, &draw_re, &game_re);

        // With replacement
        let valid_game = game.draws.into_iter().all(|d| {
            d.red_cubes <= draw_limits.red_cubes
                && d.green_cubes <= draw_limits.green_cubes
                && d.blue_cubes <= draw_limits.blue_cubes
        });

        if valid_game {
            game.game_num
        } else {
            0
        }
    }
}

fn game_line_to_num_fn_part2() -> impl Fn(&str) -> u32 {
    let (cube_draw_re, draw_re, game_re) = create_game_regexes();
    move |line: &str| -> u32 {
        let game = parse_game(line, &cube_draw_re, &draw_re, &game_re);

        // With replacement
        let min_boxes_possible = game
            .draws
            .into_iter()
            .reduce(|acc, d| acc.max_by_color(d))
            .unwrap();

        min_boxes_possible.red_cubes
            * min_boxes_possible.green_cubes
            * min_boxes_possible.blue_cubes
    }
}

fn main() {
    println!(
        "Part 1: {}",
        sum_lines(
            "input",
            game_line_to_num_fn(Draw {
                red_cubes: 12,
                green_cubes: 13,
                blue_cubes: 14
            })
        )
    );
    println!(
        "Part 2: {}",
        sum_lines("input", game_line_to_num_fn_part2())
    );
}
