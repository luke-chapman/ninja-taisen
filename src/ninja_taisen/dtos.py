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

    def other(self) -> "TeamDto":
        if self == TeamDto.monkey:
            return TeamDto.wolf
        if self == TeamDto.wolf:
            return TeamDto.monkey
        raise ValueError(f"Unknown team {self.value}")


class CardDto(BaseModel):
    team: TeamDto
    category: CategoryDto
    strength: int

    def __str__(self) -> str:
        return f"{self.team[0]}{self.category[0]}{self.strength}".upper()

    def __lt__(self, other):
        if not isinstance(other, CardDto):
            return NotImplemented
        return (self.team, self.category, self.strength) < (other.team, other.category, other.strength)


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

    def cards(self, team: TeamDto) -> CardPilesDto:
        if team == TeamDto.monkey:
            return self.monkey_cards
        if team == TeamDto.wolf:
            return self.wolf_cards
        raise ValueError(f"Unsupported team {team}")

    def __str__(self) -> str:
        self_str = ""

        max_monkey_height = max([len(pile_cards) for pile_cards in self.monkey_cards])
        for row_index in range(max_monkey_height - 1, -1, -1):
            self_str += self.__row_str(self.monkey_cards, row_index) + "\n"

        self_str += "--- " * 11 + "\n"

        max_wolf_height = max([len(pile_cards) for pile_cards in self.wolf_cards])
        for row_index in range(max_wolf_height):
            self_str += self.__row_str(self.wolf_cards, row_index) + "\n"

        return self_str

    @staticmethod
    def __row_str(cards: CardPilesDto, row_index: int) -> str:
        row_str = ""

        for pile_index in range(11):
            if len(cards[pile_index]) <= row_index:
                row_str += "    "
            else:
                row_str += cards[pile_index][row_index].__str__() + " "

        return row_str
