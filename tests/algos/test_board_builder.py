from itertools import chain

from more_itertools import unique_everseen

from ninja_taisen.algos.board_builder import make_board
from ninja_taisen.objects.board import BOARD_LENGTH, Board
from ninja_taisen.objects.card import Card, CombatCategory, Team
from ninja_taisen.objects.safe_random import SafeRandom


def test_make_board_not_shuffled() -> None:
    actual_board = make_board(shuffle_cards=False, random=SafeRandom(0))
    expected_board = make_non_shuffled_board()

    assert expected_board == actual_board


def test_make_board_shuffled() -> None:
    shuffled_board = make_board(shuffle_cards=True, random=SafeRandom(0))

    non_shuffled_board = make_non_shuffled_board()
    assert non_shuffled_board != shuffled_board

    assert len(shuffled_board.wolf_cards) == BOARD_LENGTH
    assert len(shuffled_board.monkey_cards) == BOARD_LENGTH

    monkey_lengths = [len(pile) for pile in non_shuffled_board.monkey_cards]
    wolf_lengths = [len(pile) for pile in non_shuffled_board.wolf_cards]

    assert monkey_lengths == [4, 3, 2, 1, 0, 0, 0, 0, 0, 0, 0]
    assert wolf_lengths == [0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4]

    unique_monkey_cards = sorted(unique_everseen(chain.from_iterable(shuffled_board.monkey_cards)))
    unique_wolf_cards = sorted(unique_everseen(chain.from_iterable(shuffled_board.wolf_cards)))

    assert unique_monkey_cards == make_ordered_cards(Team.MONKEY)
    assert unique_wolf_cards == make_ordered_cards(Team.WOLF)


def make_non_shuffled_board() -> Board:
    monkey_cards: list[list[Card]] = [
        [
            Card(Team.MONKEY, CombatCategory.JOKER, 4),
            Card(Team.MONKEY, CombatCategory.ROCK, 1),
            Card(Team.MONKEY, CombatCategory.ROCK, 2),
            Card(Team.MONKEY, CombatCategory.ROCK, 3),
        ],
        [
            Card(Team.MONKEY, CombatCategory.PAPER, 1),
            Card(Team.MONKEY, CombatCategory.PAPER, 2),
            Card(Team.MONKEY, CombatCategory.PAPER, 3),
        ],
        [
            Card(Team.MONKEY, CombatCategory.SCISSORS, 1),
            Card(Team.MONKEY, CombatCategory.SCISSORS, 2),
        ],
        [
            Card(Team.MONKEY, CombatCategory.SCISSORS, 3),
        ],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
    ]

    wolf_cards: list[list[Card]] = [
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [
            Card(Team.WOLF, CombatCategory.SCISSORS, 3),
        ],
        [
            Card(Team.WOLF, CombatCategory.SCISSORS, 1),
            Card(Team.WOLF, CombatCategory.SCISSORS, 2),
        ],
        [
            Card(Team.WOLF, CombatCategory.PAPER, 1),
            Card(Team.WOLF, CombatCategory.PAPER, 2),
            Card(Team.WOLF, CombatCategory.PAPER, 3),
        ],
        [
            Card(Team.WOLF, CombatCategory.JOKER, 4),
            Card(Team.WOLF, CombatCategory.ROCK, 1),
            Card(Team.WOLF, CombatCategory.ROCK, 2),
            Card(Team.WOLF, CombatCategory.ROCK, 3),
        ],
    ]

    return Board(monkey_cards, wolf_cards)


def make_ordered_cards(team: Team) -> list[Card]:
    return [
        Card(team, CombatCategory.ROCK, 1),
        Card(team, CombatCategory.ROCK, 2),
        Card(team, CombatCategory.ROCK, 3),
        Card(team, CombatCategory.PAPER, 1),
        Card(team, CombatCategory.PAPER, 2),
        Card(team, CombatCategory.PAPER, 3),
        Card(team, CombatCategory.SCISSORS, 1),
        Card(team, CombatCategory.SCISSORS, 2),
        Card(team, CombatCategory.SCISSORS, 3),
        Card(team, CombatCategory.JOKER, 4),
    ]
