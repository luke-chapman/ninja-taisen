from collections import defaultdict
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


class Card(NamedTuple):
    team: Team
    category: Category
    strength: int

    def __str__(self) -> str:
        return SHORTHAND_BY_TEAM[self.team] + SHORTHAND_BY_CATEGORY[self.category] + str(self.strength)

    @classmethod
    def from_dto(cls, dto: str) -> "Card":
        assert len(dto) == 3
        return Card(team=TEAM_BY_SHORTHAND[dto[0]], category=CATEGORY_BY_SHORTHAND[dto[1]], strength=int(dto[2]))

    def to_dto(self) -> str:
        return str(self)


BOARD_LENGTH = 11


class Board(NamedTuple):
    monkey_cards: defaultdict[int, list[Card]]
    wolf_cards: defaultdict[int, list[Card]]

    @classmethod
    def from_dto(cls, dto: BoardDto) -> "Board":
        return Board(
            monkey_cards=defaultdict(list, {i: [Card.from_dto(c) for c in cs] for i, cs in dto.monkey.items()}),
            wolf_cards=defaultdict(list, {i: [Card.from_dto(c) for c in cs] for i, cs in dto.wolf.items()}),
        )

    def to_dto(self) -> BoardDto:
        return BoardDto(
            monkey={i: [c.to_dto() for c in cs] for i, cs in self.monkey_cards.items() if len(cs) > 0},
            wolf={i: [c.to_dto() for c in cs] for i, cs in self.wolf_cards.items() if len(cs) > 0},
        )

    def cards(self, team: Team) -> defaultdict[int, list[Card]]:
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
        raise ValueError(f"Unable to find card {card} in board")

    def __str__(self) -> str:
        self_str = ""

        max_monkey_height = (
            max([len(pile_cards) for pile_cards in self.monkey_cards.values()]) if self.monkey_cards else 0
        )
        for row_index in range(max_monkey_height - 1, -1, -1):
            self_str += self.__row_str(self.monkey_cards, row_index, Team.monkey) + "\n"

        self_str += "--- " * 11 + "\n"

        max_wolf_height = max([len(pile_cards) for pile_cards in self.wolf_cards.values()]) if self.wolf_cards else 0
        for row_index in range(max_wolf_height):
            self_str += self.__row_str(self.wolf_cards, row_index, Team.wolf) + "\n"

        return self_str

    @staticmethod
    def __row_str(cards: defaultdict[int, list[Card]], row_index: int, team: Team) -> str:
        row_str = ""

        for pile_index in range(11):
            if len(cards[pile_index]) <= row_index:
                row_str += "    "
            else:
                row_str += str(cards[pile_index][row_index]) + " "

        return row_str

    def __eq__(self, other):
        if not isinstance(other, Board):
            raise TypeError(f"Unexpected type {type(other)}")
        for i in range(BOARD_LENGTH):
            if len(self.monkey_cards[i]) != len(other.monkey_cards[i]):
                return False
            if len(self.wolf_cards[i]) != len(other.wolf_cards[i]):
                return False
            for self_monkey, other_monkey in zip(self.monkey_cards[i], other.monkey_cards[i], strict=True):
                if self_monkey != other_monkey:
                    return False
            for self_wolf, other_wolf in zip(self.wolf_cards[i], other.wolf_cards[i], strict=True):
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
        return MoveDto(dice_category=DTO_BY_CATEGORY[self.dice_category], card=self.card.to_dto())


class CompletedMoves(NamedTuple):
    moves: list[Move]
    team: Team
    board: Board

    def used_joker(self) -> bool:
        return any(m.card.category == Category.joker for m in self.moves)
