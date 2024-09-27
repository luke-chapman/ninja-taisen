use chrono::{DateTime, Utc};
use std::path::Path;

pub struct InstructionDto {
    id: u32,
    seed: u32,
    monkey_strategy: String,
    wolf_strategy: String,
}

pub struct ResultDto {
    id: u32,
    seed: u32,
    monkey_strategy: String,
    wolf_strategy: String,
    winner: String,
    turn_count: u8,
    monkey_cards_left: u8,
    wolf_cards_left: u8,
    start_time: DateTime<Utc>,
    end_time: DateTime<Utc>,
    process_name: String,
}

pub fn simulate(
    instructions: &Vec<InstructionDto>,
    results_dir: &Path,
    max_processes: u8,
    per_process: u8,
) -> Vec<ResultDto> {
    let mut results = Vec::new();

    for instruction in instructions.iter() {
        results.push(ResultDto{
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
        })
    }

    results
}
