mod board;

use chrono::{DateTime, Utc};
use rand::{Rng, SeedableRng};
use rand::rngs::StdRng;
use std::path::Path;
use crate::board::{roll_dice_three_times, Board};

pub struct InstructionDto {
    pub id: u32,
    pub seed: u32,
    pub monkey_strategy: String,
    pub wolf_strategy: String,
}

pub struct ResultDto {
    pub id: u32,
    pub seed: u32,
    pub monkey_strategy: String,
    pub wolf_strategy: String,
    pub winner: String,
    pub turn_count: u8,
    pub monkey_cards_left: u8,
    pub wolf_cards_left: u8,
    pub start_time: DateTime<Utc>,
    pub end_time: DateTime<Utc>,
    pub process_name: String,
}

fn simulate_one(instruction: &InstructionDto, rng: &mut rand::rngs::StdRng) -> ResultDto {
    let mut board = Board::new(rng);
    let mut is_monkey = true;
    let mut turn_count: u8 = 0;
    let mut winner: Option<String> = None;
    let start_time = Utc::now();

    while turn_count < 100 {
        let victorious_team = board.victorious_team();
        if victorious_team != 0 {
            if victorious_team == 0b1_0_00_0000 {
                winner = Some(String::from("monkey"));
            }
            else {
                winner = Some(String::from("wolf"))
            }
            break;
        }

        let dice_rolls = roll_dice_three_times(rng);
        let permitted_moves = board.gather_all_moves(is_monkey, &dice_rolls);
        if permitted_moves.is_empty() {
            continue
        }

        let move_index = rng.gen_range(0..permitted_moves.len());
        board = permitted_moves[move_index].board.clone();
        is_monkey = !is_monkey;
        turn_count += 1;
    }

    ResultDto {
        id: instruction.id,
        seed: instruction.seed,
        monkey_strategy: instruction.monkey_strategy.clone(),
        wolf_strategy: instruction.wolf_strategy.clone(),
        winner: winner.unwrap_or(String::from("none")),
        turn_count,
        monkey_cards_left: board.monkey_heights.iter().sum(),
        wolf_cards_left: board.wolf_heights.iter().sum(),
        start_time,
        end_time: Utc::now(),
        process_name: String::from("main_process"),
    }
}

pub fn simulate(
    instructions: &Vec<InstructionDto>,
    results_dir: &Path,
    max_processes: u8,
    per_process: u8,
) -> Vec<ResultDto> {
    let mut results = Vec::new();

    for instruction in instructions.iter() {
        let mut rng = StdRng::seed_from_u64(42);
        results.push(simulate_one(instruction, &mut rng))
    }

    results
}
