from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class InstructionDto(BaseModel):
    id: int
    seed: int
    monkey_strategy: str
    wolf_strategy: str


class ResultDto(BaseModel):
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


class CardDto(BaseModel):
    team: TeamDto
    category: CategoryDto
    strength: int


CardPilesDto = tuple[
    list[CardDto],
    list[CardDto],
    list[CardDto],
    list[CardDto],
    list[CardDto],
    list[CardDto],
    list[CardDto],
    list[CardDto],
    list[CardDto],
    list[CardDto],
    list[CardDto],
]
BOARD_LENGTH = 11


class DiceRollDto(BaseModel):
    rock: int
    paper: int
    scissors: int


class BoardDto(BaseModel):
    monkey_cards: CardPilesDto
    wolf_cards: CardPilesDto


class StrategyName(StrEnum):
    random = "random"
    random_spot_win = "random_spot_win"
    metric_count = "metric_count"
    metric_position = "metric_position"
    metric_strength = "metric_strength"
