use std::collections::BTreeMap;
use serde::{Deserialize, Serialize};

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
