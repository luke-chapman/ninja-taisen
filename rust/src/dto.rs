use std::collections::BTreeMap;
use serde::{Deserialize, Serialize};

#[derive(Clone, Deserialize, Debug)]
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

#[derive(Serialize, Deserialize, PartialEq, Debug)]
pub struct BoardDto {
    pub monkey: BTreeMap<u8, Vec<String>>,
    pub wolf: BTreeMap<u8, Vec<String>>
}

#[derive(Serialize, Deserialize)]
pub struct DiceRollDto {
    pub rock: i8,
    pub paper: i8,
    pub scissors: i8
}

#[derive(Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct MoveDto {
    pub dice_category: String,
    pub card: String
}

#[derive(Serialize, Deserialize)]
pub struct ChooseRequest {
    pub board: BoardDto,
    pub dice: DiceRollDto,
    pub team: String,
    pub strategy: String,
}

#[derive(Serialize, Deserialize)]
pub struct ChooseResponse {
    pub moves: Vec<MoveDto>
}

#[derive(Serialize, Deserialize)]
pub struct ExecuteRequest {
    pub board: BoardDto,
    pub dice: DiceRollDto,
    pub team: String,
    pub moves: Vec<MoveDto>
}

#[derive(Serialize, Deserialize)]
pub struct ExecuteResponse {
    pub board: BoardDto
}
