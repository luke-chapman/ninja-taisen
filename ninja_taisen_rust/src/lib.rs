mod board;

use std::collections::HashMap;
use std::fs::File;
use std::io::Write;
use chrono::Utc;
use rand::{Rng, SeedableRng};
use rand::rngs::StdRng;
use std::path::Path;
use serde::Serialize;
use crate::board::{roll_dice_three_times, Board, ExecuteRequest, ExecuteResponse};
use crate::board::cards::{BIT_TEAM_MONKEY, BIT_TEAM_WOLF, CHECK_TEAM};

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

fn simulate_one(instruction: &InstructionDto, rng: &mut StdRng) -> ResultDto {
    let mut board = Board::new(rng);
    let mut is_monkey = true;
    let mut turn_count: u8 = 0;
    let mut winner: Option<String> = None;
    let start_time = Utc::now();

    while turn_count < 100 {
        let victorious_team = board.victorious_team();
        if victorious_team != board::cards::NULL {
            if (victorious_team & CHECK_TEAM) == BIT_TEAM_MONKEY {
                winner = Some(String::from("monkey"));
            }
            else {
                assert_eq!(victorious_team & CHECK_TEAM, BIT_TEAM_WOLF);
                winner = Some(String::from("wolf"))
            }
            break;
        }

        let dice_rolls = roll_dice_three_times(rng);
        let permitted_moves = board.gather_all_moves(is_monkey, &dice_rolls);

        turn_count += 1;
        is_monkey = !is_monkey;

        if !permitted_moves.is_empty() {
            let move_index = rng.gen_range(0..permitted_moves.len());
            board = permitted_moves[move_index].board.clone();
        }
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

pub fn execute_move(request: &ExecuteRequest) -> ExecuteResponse {
    let is_monkey =
        if request.team == "monkey" { true }
        else if request.team == "wolf" { false }
        else { panic!("Unexpected team {}", request.team) };

    let mut dice_lookup = HashMap::new();
    dice_lookup.insert(String::from("rock"), request.dice.rock);
    dice_lookup.insert(String::from("paper"), request.dice.paper);
    dice_lookup.insert(String::from("scissors"), request.dice.scissors);

    let mut board = Board::from_dto(&request.board);
    for a_move in &request.moves {
        let card = board::cards::from_string(&a_move.card);
        let dice_roll = dice_lookup.get(&a_move.dice_category);
        let card_location = board.locate_card(is_monkey, card);
        board.move_card_and_resolve_battles(
            is_monkey,
            *dice_roll.unwrap(),
            card_location.pile_index,
            card_location.card_index
        );
    }
    ExecuteResponse { board: board.to_dto() }
}

#[cfg(test)]
mod tests {
    use std::fs::{read_dir, File};
    use std::io::Read;
    use std::path::Path;
    use tempfile::tempdir;
    use crate::{execute_move, simulate, ExecuteRequest, InstructionDto};
    use crate::board::*;

    #[test]
    fn test_simulate_one() {
        let temp_dir = tempdir().expect("Failed to create temp dir");
        let instructions = vec![
            InstructionDto{
                id: 0,
                seed: 0,
                monkey_strategy: String::from("metric_strength"),
                wolf_strategy: String::from("wolf_strength")
            }
        ];
        let results = simulate(&instructions, temp_dir.path());

        assert_eq!(results.len(), 1);
        assert_eq!(results[0].id, instructions[0].id);
        assert_eq!(results[0].seed, instructions[0].seed);
        assert_eq!(results[0].monkey_strategy, instructions[0].monkey_strategy);
        assert_eq!(results[0].wolf_strategy, instructions[0].wolf_strategy);
    }

    #[test]
    fn test_simulate_many() {
        let temp_dir = tempdir().expect("Failed to create temp dir");
        let mut instructions = Vec::new();
        for i in 0..100 {
            instructions.push(InstructionDto{
                id: i,
                seed: i,
                monkey_strategy: String::from("metric_strength"),
                wolf_strategy: String::from("wolf_strength")
            });
        }

        let results = simulate(&instructions, temp_dir.path());
        assert_eq!(results.len(), instructions.len());
    }

    #[test]
    fn test_execute_move_agrees_with_python() {
        let this_file = Path::new(file!()).canonicalize().unwrap();
        let json_root = this_file
            .parent().unwrap()
            .parent().unwrap()
            .parent().unwrap()
            .join(Path::new("tests/regression/turn_by_turn"));

        let mut pass_count = 0;
        let mut fail_count = 0;

        for json_dir_wrap in read_dir(&json_root).unwrap() {
            let json_dir = json_dir_wrap.unwrap();
            if !json_dir.file_type().unwrap().is_dir() {
                continue
            }

            for item_wrap in read_dir(&json_dir.path()).unwrap() {
                let filename = item_wrap.unwrap().file_name();
                let filename_str = filename.to_str().unwrap();
                if filename_str.starts_with("request_") && filename_str.ends_with(".json") {
                    let index_str = filename_str.replace("request_", "").replace(".json", "");
                    let index: u8 = index_str.parse().unwrap();
                    let pass = assert_execute_response(&json_dir.path(), index);
                    if pass {
                        pass_count += 1;
                    } else {
                        fail_count += 1;
                    }
                }
            }
        }

        assert_eq!(fail_count, 0);
        assert_ne!(pass_count, 0);
    }

    fn assert_execute_response(json_dir: &Path, turn_index: u8) -> bool {
        let mut request_string = String::new();
        File::open(json_dir.join(format!("request_{}.json", turn_index)))
            .unwrap()
            .read_to_string(&mut request_string)
            .unwrap();
        let request: ChooseRequest = serde_json::from_str(&request_string).unwrap();

        let mut response_string = String::new();
        File::open(json_dir.join(format!("response_{}.json", turn_index)))
            .unwrap()
            .read_to_string(&mut response_string)
            .unwrap();
        let response: ChooseResponse = serde_json::from_str(&response_string).unwrap();

        let execute_request = ExecuteRequest{
            board: request.board,
            dice: request.dice,
            team: request.team,
            moves: response.moves
        };
        let execute_response = execute_move(&execute_request);

        let next_request_filename = json_dir.join(format!("request_{}.json", turn_index + 1));
        if next_request_filename.exists() {
            let mut next_request_string = String::new();
            File::open(next_request_filename)
                .unwrap()
                .read_to_string(&mut next_request_string)
                .unwrap();
            let next_request: ChooseRequest = serde_json::from_str(&next_request_string).unwrap();
            next_request.board == execute_response.board
        }
        else {
            let mut board_string = String::new();
            File::open(json_dir.join("final_board.json"))
                .unwrap()
                .read_to_string(&mut board_string)
                .unwrap();
            let expected_board: BoardDto = serde_json::from_str(&board_string).unwrap();
            expected_board == execute_response.board
        }
    }
}
