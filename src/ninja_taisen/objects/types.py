from copy import deepcopy
from enum import IntEnum
from typing import NamedTuple

from ninja_taisen.dtos import BoardDto, CategoryDto, MoveDto, StrategyName, TeamDto


# We represent Category as an IntEnum internally for speed
# We check for rock/paper/scissors winners using arithmetic modulo 3
class Category(IntEnum):
    rock = 0
    paper = 1
    scissors = 2
    joker = 3


CATEGORY_BY_DTO = {
    CategoryDto.rock: Category.rock,
    CategoryDto.paper: Category.paper,
    CategoryDto.scissors: Category.scissors,
    CategoryDto.joker: Category.joker,
}
DTO_BY_CATEGORY = {v: k for k, v in CATEGORY_BY_DTO.items()}
CATEGORY_BY_SHORTHAND = {
    "R": Category.rock,
    "P": Category.paper,
    "S": Category.scissors,
    "J": Category.joker,
}
SHORTHAND_BY_CATEGORY = {v: k for k, v in CATEGORY_BY_SHORTHAND.items()}


class Team(IntEnum):
    monkey = 0
    wolf = 1

    def other(self) -> "Team":
        if self == Team.monkey:
            return Team.wolf
        if self == Team.wolf:
            return Team.monkey
        raise ValueError(f"Unknown team {self}")


TEAM_BY_DTO = {TeamDto.monkey: Team.monkey, TeamDto.wolf: Team.wolf}
DTO_BY_TEAM = {v: k for k, v in TEAM_BY_DTO.items()}
TEAM_BY_SHORTHAND = {"M": Team.monkey, "W": Team.wolf}
SHORTHAND_BY_TEAM = {v: k for k, v in TEAM_BY_SHORTHAND.items()}


class Card:
    def __init__(self, category: Category, strength: int) -> None:
        self.category = category
        self.strength = strength

    def __eq__(self, other):
        if not isinstance(other, Card):
            raise TypeError(f"Unexpected type {type(other)}")
        return (self.category, self.strength) == (other.category, other.strength)

    def __hash__(self) -> int:
        return hash((self.category, self.strength))

    def __lt__(self, other):
        if not isinstance(other, Card):
            raise TypeError(f"Unexpected type {type(other)}")
        return (self.category, self.strength) < (other.category, other.strength)

    def __str__(self) -> str:
        return SHORTHAND_BY_CATEGORY[self.category] + str(self.strength)

    def display(self, team: Team) -> str:
        return self.to_dto(team)

    @classmethod
    def from_dto(cls, dto: str) -> "Card":
        assert len(dto) == 3
        return Card(category=CATEGORY_BY_SHORTHAND[dto[1]], strength=int(dto[2]))

    def to_dto(self, team: Team) -> str:
        return SHORTHAND_BY_TEAM[team] + str(self)


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
            return [Card.from_dto(d) for d in dto.monkey.get(index, [])]

        def __wolf_cards(index: int) -> list[Card]:
            return [Card.from_dto(d) for d in dto.wolf.get(index, [])]

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
            monkey={i: [c.to_dto(Team.monkey) for c in cs] for i, cs in enumerate(self.monkey_cards) if len(cs) > 0},
            wolf={i: [c.to_dto(Team.wolf) for c in cs] for i, cs in enumerate(self.wolf_cards) if len(cs) > 0},
        )

    def cards(self, team: Team) -> CardPiles:
        if team == Team.monkey:
            return self.monkey_cards
        if team == Team.wolf:
            return self.wolf_cards
        raise ValueError(f"Unsupported team {team}")

    def locate_card(self, card: Card, team: Team) -> tuple[int, int]:
        team_cards = self.cards(team)
        for pile_index in range(BOARD_LENGTH):
            for card_index in range(len(team_cards[pile_index])):
                if team_cards[pile_index][card_index] == card:
                    return pile_index, card_index
        raise ValueError(f"Unable to find card {card.display(team)} in board")

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

    def __eq__(self, other):
        if not isinstance(other, Board):
            raise TypeError(f"Unexpected type {type(other)}")
        for i in range(BOARD_LENGTH):
            if len(self.monkey_cards[i]) != len(other.monkey_cards[i]):
                return False
            if len(self.wolf_cards[i]) != len(other.wolf_cards[i]):
                return False
            for self_monkey, other_monkey in zip(self.monkey_cards[i], other.monkey_cards[i], strict=False):
                if self_monkey != other_monkey:
                    return False
            for self_wolf, other_wolf in zip(self.wolf_cards[i], other.wolf_cards[i], strict=False):
                if self_wolf != other_wolf:
                    return False
        return True


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


class Move(NamedTuple):
    dice_category: Category
    dice_roll: int
    card: Card

    def to_dto(self, team: Team) -> MoveDto:
        return MoveDto(dice_category=DTO_BY_CATEGORY[self.dice_category], card=self.card.to_dto(team))


class CompletedMoves(NamedTuple):
    moves: list[Move]
    team: Team
    board: Board

    def used_joker(self) -> bool:
        return any(m.card.category == Category.joker for m in self.moves)
