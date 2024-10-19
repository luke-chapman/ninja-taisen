mod board;
mod dto;
mod battle;
mod card;
mod dice;
mod move_gatherer;
mod strategy;
mod metric;

use std::collections::HashMap;
use std::fs::File;
use chrono::Utc;
use rand::SeedableRng;
use rand::rngs::StdRng;
use std::path::{Path, PathBuf};
use std::time::{SystemTime, UNIX_EPOCH};
use polars::prelude::*;
use crate::board::*;
use crate::card::cards;
use crate::dice::{roll_dice_three_times, DiceRoll};
use crate::dto::*;
use crate::move_gatherer::gather_all_moves;
use crate::strategy::Strategy;

fn simulate_one(instruction: &InstructionDto, rng: &mut StdRng) -> ResultDto {
    let monkey_strategy = Strategy::new(&instruction.monkey_strategy);
    let wolf_strategy = Strategy::new(&instruction.wolf_strategy);

    let mut board = Board::new(rng);
    let mut is_monkey = true;
    let mut turn_count: u8 = 0;
    let mut winner: Option<String> = None;
    let start_time = Utc::now();

    while turn_count < 100 {
        let victorious_team = board.victorious_team();
        if victorious_team != cards::NULL {
            if (victorious_team & cards::CHECK_TEAM) == cards::BIT_TEAM_MONKEY {
                winner = Some(String::from("monkey"));
            }
            else {
                assert_eq!(victorious_team & cards::CHECK_TEAM, cards::BIT_TEAM_WOLF);
                winner = Some(String::from("wolf"))
            }
            break;
        }

        let dice_rolls = roll_dice_three_times(rng);
        let permitted_moves = gather_all_moves(&board, is_monkey, &dice_rolls);

        if !permitted_moves.is_empty() {
            if is_monkey {
                board = monkey_strategy.choose_move(&permitted_moves, rng).board.clone();
            }
            else {
                board = wolf_strategy.choose_move(&permitted_moves, rng).board.clone();
            }
        }

        turn_count += 1;
        is_monkey = !is_monkey;
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

pub fn simulate_many_single_thread(
    instructions: &[InstructionDto],
    results_dir: &Path,
) -> PathBuf {
    let mut vec_id = Vec::new();
    let mut vec_seed = Vec::new();
    let mut vec_monkey_strategy = Vec::new();
    let mut vec_wolf_strategy = Vec::new();
    let mut vec_winner = Vec::new();
    let mut vec_turn_count = Vec::new();
    let mut vec_monkey_cards_left = Vec::new();
    let mut vec_wolf_cards_left = Vec::new();
    let mut vec_start_time = Vec::new();
    let mut vec_end_time = Vec::new();
    let mut vec_process_name = Vec::new();

    for instruction in instructions.iter() {
        let mut rng = StdRng::seed_from_u64(instruction.seed);
        let result = simulate_one(instruction, &mut rng);

        vec_id.push(result.id);
        vec_seed.push(result.seed);
        vec_monkey_strategy.push(result.monkey_strategy);
        vec_wolf_strategy.push(result.wolf_strategy);
        vec_winner.push(result.winner);
        vec_turn_count.push(result.turn_count);
        vec_monkey_cards_left.push(result.monkey_cards_left);
        vec_wolf_cards_left.push(result.wolf_cards_left);
        vec_start_time.push(result.start_time);
        vec_end_time.push(result.end_time);
        vec_process_name.push(result.process_name);
    }

    let mut df = DataFrame::new(vec![
        Series::new("id".into(), &vec_id),
        Series::new("seed".into(), &vec_seed),
        Series::new("monkey_strategy".into(), &vec_monkey_strategy),
        Series::new("wolf_strategy".into(), &vec_wolf_strategy),
        Series::new("winner".into(), &vec_winner),
        Series::new("turn_count".into(), &vec_turn_count),
        Series::new("monkey_cards_left".into(), &vec_monkey_cards_left),
        Series::new("wolf_cards_left".into(), &vec_wolf_cards_left),
        Series::new("start_time".into(), &vec_start_time),
        Series::new("end_time".into(), &vec_end_time),
        Series::new("process_name".into(), &vec_process_name),
    ]).unwrap();

    // Path to write the Parquet file
    let filename = format!("results_{}-{}.parquet", instructions[0].id, instructions[instructions.len() - 1].id);
    let full_filename = results_dir.join(filename);

    // Write the DataFrame to a Parquet file
    let file = File::create(&full_filename).unwrap();
    ParquetWriter::new(file).finish(&mut df).unwrap();

    println!("Wrote parquet results to {}", full_filename.as_os_str().to_str().unwrap());
    full_filename
}

pub fn choose_move(request: &ChooseRequest) -> ChooseResponse {
    let board = Board::from_dto(&request.board);
    let is_monkey =
        if request.team == *"monkey" { true }
        else if request.team == *"wolf" { false }
        else { panic!("Unexpected team {}", request.team) };
    let dice_roll = [
        DiceRoll{category: cards::BITS_CATEGORY_ROCK, roll: request.dice.rock},
        DiceRoll{category: cards::BITS_CATEGORY_PAPER, roll: request.dice.paper},
        DiceRoll{category: cards::BITS_CATEGORY_SCISSORS, roll: request.dice.scissors},
    ];

    let all_permitted_moves = gather_all_moves(&board, is_monkey, &dice_roll);
    if all_permitted_moves.is_empty() {
        return ChooseResponse{moves: Vec::new()};
    }
    let strategy = Strategy::new(&request.strategy);

    let start = SystemTime::now();
    let since_epoch = start.duration_since(UNIX_EPOCH).expect("Time went backwards");
    let seed = since_epoch.as_secs(); // Use seconds as the seed
    let mut rng = StdRng::seed_from_u64(seed);

    let chosen_move = strategy.choose_move(&all_permitted_moves, &mut rng);

    let mut move_dtos = Vec::new();
    for a_move in &chosen_move.moves {
        move_dtos.push(a_move.to_dto())
    }
    ChooseResponse{moves: move_dtos}
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
        let card = card::from_string(&a_move.card);
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
    use std::collections::HashSet;
    use std::fs::{read_dir, File};
    use std::io::Read;
    use std::path::Path;
    use polars::prelude::{ParquetReader, SerReader};
    use tempfile::tempdir;
    use crate::{card, choose_move, execute_move, simulate_many_single_thread, ExecuteRequest, InstructionDto};
    use crate::card::cards;
    use crate::dto::{BoardDto, ChooseRequest, ChooseResponse};

    #[test]
    fn test_simulate_one() {
        let temp_dir = tempdir().expect("Failed to create temp dir");
        let instructions = vec![
            InstructionDto{
                id: 0,
                seed: 0,
                monkey_strategy: String::from("metric_strength"),
                wolf_strategy: String::from("random")
            }
        ];
        let results_filename = simulate_many_single_thread(&instructions, temp_dir.path());
        let mut results_file = File::open(&results_filename).unwrap();
        let results_df = ParquetReader::new(&mut results_file).finish().unwrap();

        assert_eq!(results_df.shape().0, 1);
        assert_eq!(results_df.shape().1, 11);
    }

    #[test]
    fn test_simulate_many() {
        let temp_dir = tempdir().expect("Failed to create temp dir");
        let mut instructions = Vec::new();
        for i in 0..100 {
            instructions.push(InstructionDto{
                id: i,
                seed: i,
                monkey_strategy: String::from("random_spot_win"),
                wolf_strategy: String::from("metric_count")
            });
        }

        let results_filename = simulate_many_single_thread(&instructions, temp_dir.path());
        let mut results_file = File::open(&results_filename).unwrap();
        let results_df = ParquetReader::new(&mut results_file).finish().unwrap();

        assert_eq!(results_df.shape().0, instructions.len());
        assert_eq!(results_df.shape().1, 11);
    }

    #[test]
    fn test_choose_move_returns_valid_move() {
        test_each_request_response(true)
    }

    #[test]
    fn test_execute_move_agrees_with_python() {
        test_each_request_response(false)
    }

    fn test_each_request_response(is_choose: bool) {
        let json_root = Path::new(file!())
            .canonicalize().unwrap()
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

                    let pass =
                        if is_choose {
                            assert_choose_response(&json_dir.path(), index)
                        } else {
                            assert_execute_response(&json_dir.path(), index)
                        };

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

    fn assert_choose_response(json_dir: &Path, turn_index: u8) -> bool {
        let mut request_string = String::new();
        File::open(json_dir.join(format!("request_{}.json", turn_index)))
            .unwrap()
            .read_to_string(&mut request_string)
            .unwrap();
        let request: ChooseRequest = serde_json::from_str(&request_string).unwrap();

        let response = choose_move(&request);

        let mut result = response.moves.len() <= 3;
        let mut seen_dice_categories: HashSet<String> = HashSet::new();
        let mut seen_cards: HashSet<String> = HashSet::new();

        for a_move in &response.moves {
            let dice_category = &a_move.dice_category;
            let card = &a_move.card;

            let card_u8 = card::from_string(card);
            let card_category_u8 = card_u8 & cards::CHECK_CATEGORY;
            let dice_category_u8 =
                if dice_category == "rock" { cards::BITS_CATEGORY_ROCK }
                else if dice_category == "paper" { cards::BITS_CATEGORY_PAPER }
                else if dice_category == "scissors" { cards::BITS_CATEGORY_SCISSORS }
                else { panic!("Unexpected dice_category {}", dice_category) };
            let team_u8 =
                if request.team == "monkey" { cards::BIT_TEAM_MONKEY }
                else if request.team == "wolf" { cards::BIT_TEAM_WOLF }
                else { panic!("Unexpected team {}", request.team) };

            result &= (card_u8 & cards::CHECK_TEAM) == team_u8;
            if card_category_u8 != cards::BITS_CATEGORY_JOKER {
                result &= card_category_u8 == dice_category_u8;
            }

            result &= !seen_dice_categories.contains(dice_category);
            result &= !seen_cards.contains(card);

            seen_dice_categories.insert(dice_category.clone());
            seen_cards.insert(card.clone());
        }

        result
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
