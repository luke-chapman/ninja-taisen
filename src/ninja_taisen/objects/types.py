from copy import deepcopy
from dataclasses import dataclass
from enum import IntEnum
from typing import NamedTuple

from ninja_taisen.dtos import BoardDto, CardDto, CategoryDto, StrategyName, TeamDto


# We represent Category as an IntEnum internally for speed
# We check for rock/paper/scissors winners using arithemtic modulo 3
class Category(IntEnum):
    rock = 0
    paper = 1
    scissors = 2
    joker = 3


CATEGORY_DTO_TO_TYPE = {
    CategoryDto.rock: Category.rock,
    CategoryDto.paper: Category.paper,
    CategoryDto.scissors: Category.scissors,
    CategoryDto.joker: Category.joker,
}
CATEGORY_TYPE_TO_DTO = {v: k for k, v in CATEGORY_DTO_TO_TYPE.items()}


class Team(IntEnum):
    monkey = 0
    wolf = 1

    def other(self) -> "Team":
        if self == Team.monkey:
            return Team.wolf
        if self == Team.wolf:
            return Team.monkey
        raise ValueError(f"Unknown team {self.value}")


TEAM_DTO_TO_TYPE = {TeamDto.monkey: Team.monkey, TeamDto.wolf: Team.wolf}
TEAM_TYPE_TO_DTO = {v: k for k, v in TEAM_DTO_TO_TYPE.items()}


@dataclass(order=True)
class Card:
    category: Category
    strength: int  # mutable - the strength of a joker decreases after each fight, but resets after a move is complete

    def __str__(self) -> str:
        return f"{CATEGORY_TYPE_TO_DTO[self.category].value[0]}{self.strength}".upper()

    @classmethod
    def from_dto(cls, dto: CardDto) -> "Card":
        return Card(category=CATEGORY_DTO_TO_TYPE[dto.category], strength=dto.strength)

    def to_dto(self, team: TeamDto) -> CardDto:
        return CardDto(team=team, category=CATEGORY_TYPE_TO_DTO[self.category], strength=self.strength)


BOARD_LENGTH = 11
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


class Board(NamedTuple):
    monkey_cards: CardPiles
    wolf_cards: CardPiles

    #  Because CardPiles is a tuple of lists, a deepcopy would normally stop at the immutable tuple
    #  Therefore we implement our own .clone() operation which invokes the deepcopy inside the tuples
    def clone(self) -> "Board":
        return Board(
            monkey_cards=(
                deepcopy(self.monkey_cards[0]),
                deepcopy(self.monkey_cards[1]),
                deepcopy(self.monkey_cards[2]),
                deepcopy(self.monkey_cards[3]),
                deepcopy(self.monkey_cards[4]),
                deepcopy(self.monkey_cards[5]),
                deepcopy(self.monkey_cards[6]),
                deepcopy(self.monkey_cards[7]),
                deepcopy(self.monkey_cards[8]),
                deepcopy(self.monkey_cards[9]),
                deepcopy(self.monkey_cards[10]),
            ),
            wolf_cards=(
                deepcopy(self.wolf_cards[0]),
                deepcopy(self.wolf_cards[1]),
                deepcopy(self.wolf_cards[2]),
                deepcopy(self.wolf_cards[3]),
                deepcopy(self.wolf_cards[4]),
                deepcopy(self.wolf_cards[5]),
                deepcopy(self.wolf_cards[6]),
                deepcopy(self.wolf_cards[7]),
                deepcopy(self.wolf_cards[8]),
                deepcopy(self.wolf_cards[9]),
                deepcopy(self.wolf_cards[10]),
            ),
        )

    @classmethod
    def from_dto(cls, dto: BoardDto) -> "Board":
        return Board(
            monkey_cards=(
                [Card.from_dto(d) for d in dto.monkey_cards[0]],
                [Card.from_dto(d) for d in dto.monkey_cards[1]],
                [Card.from_dto(d) for d in dto.monkey_cards[2]],
                [Card.from_dto(d) for d in dto.monkey_cards[3]],
                [Card.from_dto(d) for d in dto.monkey_cards[4]],
                [Card.from_dto(d) for d in dto.monkey_cards[5]],
                [Card.from_dto(d) for d in dto.monkey_cards[6]],
                [Card.from_dto(d) for d in dto.monkey_cards[7]],
                [Card.from_dto(d) for d in dto.monkey_cards[8]],
                [Card.from_dto(d) for d in dto.monkey_cards[9]],
                [Card.from_dto(d) for d in dto.monkey_cards[10]],
            ),
            wolf_cards=(
                [Card.from_dto(d) for d in dto.wolf_cards[0]],
                [Card.from_dto(d) for d in dto.wolf_cards[1]],
                [Card.from_dto(d) for d in dto.wolf_cards[2]],
                [Card.from_dto(d) for d in dto.wolf_cards[3]],
                [Card.from_dto(d) for d in dto.wolf_cards[4]],
                [Card.from_dto(d) for d in dto.wolf_cards[5]],
                [Card.from_dto(d) for d in dto.wolf_cards[6]],
                [Card.from_dto(d) for d in dto.wolf_cards[7]],
                [Card.from_dto(d) for d in dto.wolf_cards[8]],
                [Card.from_dto(d) for d in dto.wolf_cards[9]],
                [Card.from_dto(d) for d in dto.wolf_cards[10]],
            ),
        )

    def to_dto(self) -> BoardDto:
        return BoardDto(
            monkey_cards=(
                [c.to_dto(TeamDto.monkey) for c in self.monkey_cards[0]],
                [c.to_dto(TeamDto.monkey) for c in self.monkey_cards[1]],
                [c.to_dto(TeamDto.monkey) for c in self.monkey_cards[2]],
                [c.to_dto(TeamDto.monkey) for c in self.monkey_cards[3]],
                [c.to_dto(TeamDto.monkey) for c in self.monkey_cards[4]],
                [c.to_dto(TeamDto.monkey) for c in self.monkey_cards[5]],
                [c.to_dto(TeamDto.monkey) for c in self.monkey_cards[6]],
                [c.to_dto(TeamDto.monkey) for c in self.monkey_cards[7]],
                [c.to_dto(TeamDto.monkey) for c in self.monkey_cards[8]],
                [c.to_dto(TeamDto.monkey) for c in self.monkey_cards[9]],
                [c.to_dto(TeamDto.monkey) for c in self.monkey_cards[10]],
            ),
            wolf_cards=(
                [c.to_dto(TeamDto.wolf) for c in self.wolf_cards[0]],
                [c.to_dto(TeamDto.wolf) for c in self.wolf_cards[1]],
                [c.to_dto(TeamDto.wolf) for c in self.wolf_cards[2]],
                [c.to_dto(TeamDto.wolf) for c in self.wolf_cards[3]],
                [c.to_dto(TeamDto.wolf) for c in self.wolf_cards[4]],
                [c.to_dto(TeamDto.wolf) for c in self.wolf_cards[5]],
                [c.to_dto(TeamDto.wolf) for c in self.wolf_cards[6]],
                [c.to_dto(TeamDto.wolf) for c in self.wolf_cards[7]],
                [c.to_dto(TeamDto.wolf) for c in self.wolf_cards[8]],
                [c.to_dto(TeamDto.wolf) for c in self.wolf_cards[9]],
                [c.to_dto(TeamDto.wolf) for c in self.wolf_cards[10]],
            ),
        )

    def cards(self, team: Team) -> CardPiles:
        if team == Team.monkey:
            return self.monkey_cards
        if team == Team.wolf:
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
    def __row_str(cards: CardPiles, row_index: int) -> str:
        row_str = ""

        for pile_index in range(11):
            if len(cards[pile_index]) <= row_index:
                row_str += "    "
            else:
                row_str += cards[pile_index][row_index].__str__() + " "

        return row_str


class BoardStateMidTurn(NamedTuple):
    board: Board
    used_joker: bool
    dice_used: list[tuple[Category, int]]


ALL_STRATEGY_NAMES = list(s.value for s in StrategyName)
