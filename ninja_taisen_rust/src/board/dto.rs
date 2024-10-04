use std::collections::BTreeMap;
use serde::Serialize;

#[derive(Serialize)]
pub struct BoardDto {
    pub monkey: BTreeMap<u8, Vec<String>>,
    pub wolf: BTreeMap<u8, Vec<String>>
}

#[derive(Serialize)]
pub struct DiceRollDto {
    pub rock: i8,
    pub paper: i8,
    pub scissors: i8
}

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
pub struct MoveDto {
    pub dice_category: String,
    pub card: String
}

#[derive(Serialize)]
pub struct ExecuteRequest {
    pub board: BoardDto,
    pub dice: DiceRollDto,
    pub team: String,
    pub moves: Vec<MoveDto>
}

#[derive(Serialize)]
pub struct ExecuteResponse {
    pub board: BoardDto
}
