mod simulator;

use chrono::{DateTime, Utc};
use rand::{Rng, SeedableRng};
use rand::rngs::StdRng;
use std::path::Path;

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

fn simulate_one(instruction: &InstructionDto, mut rng: &rand::rngs::StdRng) -> ResultDto {
    ResultDto {
        id: instruction.id,
        seed: instruction.seed,
        monkey_strategy: instruction.monkey_strategy.clone(),
        wolf_strategy: instruction.wolf_strategy.clone(),
        winner: String::from("monkey"),
        turn_count: 8,
        monkey_cards_left: 4,
        wolf_cards_left: 2,
        start_time: Utc::now(),
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
