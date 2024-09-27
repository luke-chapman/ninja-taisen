use tempfile::tempdir;
use ninja_taisen_rust::{InstructionDto, simulate};

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
    let results = simulate(&instructions, temp_dir.path(), 1, 5);
    
    assert_eq!(results.len(), 1);
    assert_eq!(results[0].id, instructions[0].id);
    assert_eq!(results[0].seed, instructions[0].seed);
    assert_eq!(results[0].monkey_strategy, instructions[0].monkey_strategy);
    assert_eq!(results[0].wolf_strategy, instructions[0].wolf_strategy);
}
