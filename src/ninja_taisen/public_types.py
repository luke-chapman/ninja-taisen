from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class Instruction(BaseModel):
    id: int
    seed: int
    monkey_strategy: str
    wolf_strategy: str


class Result(BaseModel):
    id: int
    seed: int
    monkey_strategy: str
    wolf_strategy: str
    winner: str
    turn_count: int
    start_time: datetime
    end_time: datetime
    process_name: str


class Category(StrEnum):
    rock = "rock"
    paper = "paper"
    scissors = "scissors"
    joker = "joker"


class Team(StrEnum):
    monkey = "monkey"
    wolf = "wolf"


class Card(BaseModel):
    team: Team
    category: Category
    strength: int

    def __str__(self) -> str:
        return f"{self.team[0]}{self.combat_category[0]}{self.strength}".upper()


CardPiles = tuple[
    list[Card],
    list[Card],
    list[Card],
    list[Card],
    list[Card],
    list[Card],
    list[Card],
    list[Card],
    list[Card],
    list[Card],
    list[Card],
]
BOARD_LENGTH = len(CardPiles.__args__)


class DiceRoll(BaseModel):
    rock: int
    paper: int
    scissors: int


class Board(BaseModel):
    monkey_cards: CardPiles
    wolf_cards: CardPiles

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
    def __row_str(cards: list[list[Card]], row_index: int) -> str:
        row_str = ""

        for pile_index in range(11):
            if len(cards[pile_index]) <= row_index:
                row_str += "    "
            else:
                row_str += cards[pile_index][row_index].__str__() + " "

        return row_str
