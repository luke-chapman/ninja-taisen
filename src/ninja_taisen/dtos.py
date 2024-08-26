from datetime import datetime
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class NinjaTaisenModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    def to_json_file(self, filename: Path) -> None:
        content = self.model_dump_json(indent=2, round_trip=True, by_alias=True)
        filename.write_text(content)


class InstructionDto(NinjaTaisenModel):
    id: int
    seed: int
    monkey_strategy: str
    wolf_strategy: str


class ResultDto(NinjaTaisenModel):
    id: int
    seed: int
    monkey_strategy: str
    wolf_strategy: str
    winner: str
    turn_count: int
    start_time: datetime
    end_time: datetime
    process_name: str


class CategoryDto(StrEnum):
    rock = "rock"
    paper = "paper"
    scissors = "scissors"
    joker = "joker"


class TeamDto(StrEnum):
    monkey = "monkey"
    wolf = "wolf"


class DiceRollDto(NinjaTaisenModel):
    rock: int
    paper: int
    scissors: int


class BoardDto(NinjaTaisenModel):
    monkey: dict[int, list[str]]
    wolf: dict[int, list[str]]


class Strategy(StrEnum):
    random = "random"
    random_spot_win = "random_spot_win"
    metric_count = "metric_count"
    metric_position = "metric_position"
    metric_strength = "metric_strength"


class MoveRequestBody(NinjaTaisenModel):
    board: BoardDto
    dice: DiceRollDto
    team: TeamDto


class MoveDto(NinjaTaisenModel):
    dice_category: CategoryDto
    card: str


class MoveResponseBody(NinjaTaisenModel):
    moves: list[MoveDto]
