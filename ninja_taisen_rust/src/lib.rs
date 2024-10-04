mod board;

use std::fs::File;
use std::io::Write;
use chrono::Utc;
use rand::{Rng, SeedableRng};
use rand::rngs::StdRng;
use std::path::Path;
use serde::Serialize;
use crate::board::{roll_dice_three_times, Board, ExecuteRequest, ExecuteResponse};

pub struct InstructionDto {
    pub id: u64,
    pub seed: u64,
    pub monkey_strategy: String,
    pub wolf_strategy: String,
}

#[derive(Serialize)]
pub struct ResultDto {
    pub id: u64,
    pub seed: u64,
    pub monkey_strategy: String,
    pub wolf_strategy: String,
    pub winner: String,
    pub turn_count: u8,
    pub monkey_cards_left: u8,
    pub wolf_cards_left: u8,
    pub start_time: String,
    pub end_time: String,
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
        start_time: start_time.to_rfc3339(),
        end_time: Utc::now().to_rfc3339(),
        process_name: String::from("main_process"),
    }
}

pub fn simulate(
    instructions: &Vec<InstructionDto>,
    results_dir: &Path,
) -> Vec<ResultDto> {
    let mut results = Vec::new();

    for instruction in instructions.iter() {
        let mut rng = StdRng::seed_from_u64(instruction.seed);
        results.push(simulate_one(instruction, &mut rng))
    }

    let json = serde_json::to_string_pretty(&results).unwrap();
    let filename = results_dir.join("results.json");
    let mut file = File::create(filename).expect("Unable to create results.json");
    file.write(json.as_bytes()).expect("Unable to write data");

    results
}

pub fn execute_move(request: ExecuteRequest) -> ExecuteResponse {
    let is_monkey =
        if request.team == "monkey" { true }
        else if request.team == "wolf" { false }
        else { panic!("Unexpected team {}", request.team) };

    let mut board = Board::from_dto(&request.board);
    for a_move in request.moves {
        let card = board::cards::from_string(&a_move.card);
        let card_location = board.locate_card(is_monkey, card);
        board.move_card_and_resolve_battles(
            is_monkey,
            0,
            card_location.pile_index,
            card_location.card_index
        );
    }
    ExecuteResponse { board: board.to_dto() }
}
