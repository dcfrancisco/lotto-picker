use crate::cli::{CliArgs, Strategy};
use crate::db::get_draws;
use crate::models::Draw;
use rand::seq::SliceRandom;
use rand::thread_rng;
use rusqlite::Connection;
use std::collections::HashMap;

pub fn run_cli(conn: &Connection, args: &CliArgs) -> anyhow::Result<()> {
    let draws = get_draws(conn, &args.game)?;
    if draws.is_empty() {
        println!("No draws found for game: {}", args.game);
        return Ok(());
    }
    let freq = count_number_frequency(&draws);
    if args.show_freq {
        println!("Number Frequency (1-55):");
        for n in 1..=55 {
            println!("{:2}: {}", n, freq.get(&n).unwrap_or(&0));
        }
        println!("");
    }
    if args.play {
        let picks = balanced_random_lines(10, 6, 1, 55);
        println!("\n-- PLAY MODE: 10 Balanced Random Lines --");
        for (idx, pick) in picks.iter().enumerate() {
            println!("Line {:2}: {:?}", idx + 1, pick);
        }
        println!("---------------------------------------\n");
        // Analysis
        let results = check_picks_against_history(&picks, &draws);
        println!("-- PLAY MODE ANALYSIS --");
        let mut win_stats = HashMap::from([(6,0),(5,0),(4,0),(3,0)]);
        for (idx, res) in results.iter().enumerate() {
            println!("Line {:2}: Best match: {} | Exact match: {}", idx+1, res.best_match, res.exact_match);
            if win_stats.contains_key(&res.best_match) {
                *win_stats.get_mut(&res.best_match).unwrap() += 1;
            }
        }
        println!("Win Stats (across all lines): {:?}", win_stats);
        println!("---------------------------\n");
        return Ok(());
    }
    // ...other logic for strategies, simulation, etc.
    Ok(())
}

pub fn count_number_frequency(draws: &[Draw]) -> HashMap<u8, usize> {
    let mut freq = HashMap::new();
    for draw in draws {
        for &num in &draw.numbers {
            *freq.entry(num).or_insert(0) += 1;
        }
    }
    freq
}

pub struct MatchResult {
    pub pick: Vec<u8>,
    pub best_match: usize,
    pub exact_match: bool,
}

pub fn check_picks_against_history(picks: &[Vec<u8>], draws: &[Draw]) -> Vec<MatchResult> {
    let mut results = Vec::new();
    for pick in picks {
        let mut best_match = 0;
        let mut exact_match = false;
        for draw in draws {
            let match_count = pick.iter().filter(|n| draw.numbers.contains(n)).count();
            if match_count > best_match {
                best_match = match_count;
            }
            if pick.len() == draw.numbers.len() && pick.iter().all(|n| draw.numbers.contains(n)) {
                exact_match = true;
            }
        }
        results.push(MatchResult {
            pick: pick.clone(),
            best_match,
            exact_match,
        });
    }
    results
}

pub fn balanced_random_lines(n_lines: usize, n_per_line: usize, min: u8, max: u8) -> Vec<Vec<u8>> {
    let mut pool: Vec<u8> = (min..=max).collect();
    let mut picks = Vec::new();
    let mut rng = thread_rng();
    for _ in 0..n_lines {
        if pool.len() < n_per_line {
            pool.extend(min..=max);
        }
        pool.shuffle(&mut rng);
        let pick: Vec<u8> = pool.drain(0..n_per_line).collect();
        picks.push(pick);
    }
    picks
}
