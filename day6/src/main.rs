use std::fs::File;
use std::io::{self, BufRead};
use std::path::Path;

#[derive(Clone, Copy)]
struct Race {
    time: u64,
    record_distance: u64,
}

fn read_lines<P>(filename: P) -> io::Result<io::Lines<io::BufReader<File>>>
where
    P: AsRef<Path>,
{
    let file = File::open(filename)?;
    Ok(io::BufReader::new(file).lines())
}

fn process_races(filename: &str) -> u64 {
    let mut lines = read_lines(filename)
        .unwrap()
        .filter_map(Result::ok) // filter out possible errors
        .filter(|l| !l.trim().is_empty());

    let mut time_line = lines.next().unwrap();
    let time_nums = &time_line
        .split_at(time_line.chars().position(|c| c == ':').unwrap())
        .1[1..];
    let times = space_separated_nums_to_iter(time_nums);

    let mut distance_line = lines.next().unwrap();
    let distance_nums = &distance_line
        .split_at(distance_line.chars().position(|c| c == ':').unwrap())
        .1[1..];
    let distances = space_separated_nums_to_iter(distance_nums);

    let races = times.zip(distances).map(|(t, d)| Race {
        time: t,
        record_distance: d,
    });

    races.map(|r| ways_to_win(r)).product()
}

fn process_race_part2(filename: &str) -> u64 {
    let mut lines = read_lines(filename)
        .unwrap()
        .filter_map(Result::ok) // filter out possible errors
        .filter(|l| !l.trim().is_empty());

    let mut time_line = lines.next().unwrap();
    let time_nums = &time_line
        .split_at(time_line.chars().position(|c| c == ':').unwrap())
        .1[1..];
    let time = time_nums.replace(' ', "").parse::<u64>().unwrap();

    let mut distance_line = lines.next().unwrap();
    let distance_nums = &distance_line
        .split_at(distance_line.chars().position(|c| c == ':').unwrap())
        .1[1..];
    let distance = distance_nums.replace(' ', "").parse::<u64>().unwrap();

    let race = Race {
        time,
        record_distance: distance,
    };

    ways_to_win(race)
}

fn space_separated_nums_to_iter<'a>(l: &'a str) -> impl Iterator<Item = u64> + 'a {
    l.split(|c| c == ' ')
        .filter(|&w| !w.is_empty())
        .map(|w| w.parse().unwrap())
}

fn ways_to_win(race: Race) -> u64 {
    let max_t = race.time / 2;
    let rem = race.time % 2;

    let mut ways = 0;
    for charge_time in 1..=max_t {
        let drive_time = race.time - charge_time;

        if charge_time * drive_time > race.record_distance {
            ways += 1;
        }
    }

    if rem == 0 {
        // ie. times were 1+4, 2+3, 3+2, 4+1
        ((ways - 1) * 2) + 1
    } else {
        // ie. times were 1+3, 2+2, 3+1
        ways * 2
    }
}

fn main() {
    println!("Part 1: {}", process_races("input"));
    println!("Part 2: {}", process_race_part2("input"));
}
