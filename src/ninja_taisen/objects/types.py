from copy import deepcopy
from enum import IntEnum
from typing import NamedTuple

from ninja_taisen.dtos import BoardDto, CardDto, CategoryDto, StrategyName, TeamDto


# We represent Category as an IntEnum internally for speed
# We check for rock/paper/scissors winners using arithmetic modulo 3
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


class Card:
    def __init__(self, category: Category, strength: int) -> None:
        self.category = category
        self.strength = strength

    def __eq__(self, other):
        if not isinstance(other, Card):
            raise TypeError(f"Unexpected type {type(other)}")
        return (self.category, self.strength) == (other.strength, other.category)

    def __hash__(self) -> int:
        return hash((self.category, self.strength))

    def __lt__(self, other):
        if not isinstance(other, Card):
            raise TypeError(f"Unexpected type {type(other)}")
        return (self.category, self.strength) < (other.strength, other.category)

    def __str__(self) -> str:
        return f"{CATEGORY_TYPE_TO_DTO[self.category].value[0]}{self.strength}".upper()

    def display(self, team: Team) -> str:
        return TEAM_TYPE_TO_DTO[team].value[0].upper() + str(self)

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
        def __monkey_cards(index: int) -> list[Card]:
            return [Card.from_dto(d) for d in dto.monkey_cards.get(index, [])]

        def __wolf_cards(index: int) -> list[Card]:
            return [Card.from_dto(d) for d in dto.wolf_cards.get(index, [])]

        return Board(
            monkey_cards=(
                __monkey_cards(0),
                __monkey_cards(1),
                __monkey_cards(2),
                __monkey_cards(3),
                __monkey_cards(4),
                __monkey_cards(5),
                __monkey_cards(6),
                __monkey_cards(7),
                __monkey_cards(8),
                __monkey_cards(9),
                __monkey_cards(10),
            ),
            wolf_cards=(
                __wolf_cards(0),
                __wolf_cards(1),
                __wolf_cards(2),
                __wolf_cards(3),
                __wolf_cards(4),
                __wolf_cards(5),
                __wolf_cards(6),
                __wolf_cards(7),
                __wolf_cards(8),
                __wolf_cards(9),
                __wolf_cards(10),
            ),
        )

    def to_dto(self) -> BoardDto:
        return BoardDto(
            monkey_cards={
                i: [c.to_dto(TeamDto.monkey) for c in cs] for i, cs in enumerate(self.monkey_cards) if len(cs) > 0
            },
            wolf_cards={i: [c.to_dto(TeamDto.wolf) for c in cs] for i, cs in enumerate(self.wolf_cards) if len(cs) > 0},
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
            self_str += self.__row_str(self.monkey_cards, row_index, Team.monkey) + "\n"

        self_str += "--- " * 11 + "\n"

        max_wolf_height = max([len(pile_cards) for pile_cards in self.wolf_cards])
        for row_index in range(max_wolf_height):
            self_str += self.__row_str(self.wolf_cards, row_index, Team.wolf) + "\n"

        return self_str

    @staticmethod
    def __row_str(cards: CardPiles, row_index: int, team: Team) -> str:
        row_str = ""

        for pile_index in range(11):
            if len(cards[pile_index]) <= row_index:
                row_str += "    "
            else:
                row_str += cards[pile_index][row_index].display(team) + " "

        return row_str


class BoardStateMidTurn(NamedTuple):
    board: Board
    used_joker: bool
    dice_used: list[tuple[Category, int]]


class BattleStatus(IntEnum):
    card_a_wins = -1
    draw = 0
    card_b_wins = 1

    def other(self) -> "BattleStatus":
        return BattleStatus(-self.value)


class BattleResult(NamedTuple):
    status: BattleStatus
    winner: Card | None


ALL_STRATEGY_NAMES = list(StrategyName)
