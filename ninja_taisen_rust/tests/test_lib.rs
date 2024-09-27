use std::path::Path;
use tempfile::tempdir;
use ninja_taisen_rust::{InstructionDto, ResultDto, simulate};

#[test]
fn test_simulate() {
    let temp_dir = tempdir().expect("Failed to create temp dir");

    let instructions = vec![
        InstructionDto{
            id: 1,
            seed: 2,
            monkey_strategy: String::from("metric_strength"),
            wolf_strategy: String::from("wolf_strength")
        }
    ];

    let results = simulate(
        instructions: instructions,
        results_dir: temp_dir,
        max_processes: 1,
        per_process: 5,
    );

    assert_eq!(results.len(), 1);
}
