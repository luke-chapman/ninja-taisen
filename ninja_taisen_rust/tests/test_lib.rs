use std::fs::{File,read_dir};
use std::io::Read;
use std::path::Path;
use tempfile::tempdir;
use ninja_taisen_rust::{InstructionDto, simulate, BoardDto, ChooseRequest, ChooseResponse, ExecuteRequest, execute_move};

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
    for i in 0..10 {
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
fn test_execute_move() {
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
        return next_request.board == execute_response.board
    }
    else {
        let mut board_string = String::new();
        File::open(json_dir.join("final_board.json"))
            .unwrap()
            .read_to_string(&mut board_string)
            .unwrap();
        let expected_board: BoardDto = serde_json::from_str(&board_string).unwrap();
        return expected_board == execute_response.board
    }
}
