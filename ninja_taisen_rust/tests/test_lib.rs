use std::fs::File;
use std::io::Read;
use std::path::Path;
use tempfile::tempdir;
use ninja_taisen_rust::{InstructionDto, simulate, ChooseRequest, ChooseResponse, ExecuteRequest, ExecuteResponse, execute_move};

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
    let json_dir = this_file
        .parent().unwrap()
        .parent().unwrap()
        .parent().unwrap()
        .join(Path::new("tests/regression/turn_by_turn/random_vs_random"));

    let mut request_0_string = String::new();
    File::open(json_dir.join("request_0.json"))
        .unwrap()
        .read_to_string(&mut request_0_string)
        .unwrap();
    let request_0: ChooseRequest = serde_json::from_str(&request_0_string).unwrap();

    let mut response_0_string = String::new();
    File::open(json_dir.join("response_0.json"))
        .unwrap()
        .read_to_string(&mut response_0_string)
        .unwrap();
    let response_0: ChooseResponse = serde_json::from_str(&response_0_string).unwrap();

    let execute_request = ExecuteRequest{
        board: request_0.board,
        dice: request_0.dice,
        team: request_0.team,
        moves: response_0.moves
    };

    let execute_response = execute_move(&execute_request);

    let mut request_1_string = String::new();
    File::open(json_dir.join("request_1.json"))
        .unwrap()
        .read_to_string(&mut request_1_string)
        .unwrap();
    let request_1: ChooseRequest = serde_json::from_str(&request_1_string).unwrap();

    assert_eq!(request_1.board.monkey[&0][0], execute_response.board.monkey[&0][0]);
}
