from itertools import chain

from more_itertools import unique_everseen

from ninja_taisen.algos.board_builder import make_board
from ninja_taisen.objects.safe_random import SafeRandom
from ninja_taisen.public_types import BOARD_LENGTH, Board, Card, Category, Team


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

    assert unique_monkey_cards == make_ordered_cards(Team.monkey)
    assert unique_wolf_cards == make_ordered_cards(Team.wolf)


def make_non_shuffled_board() -> Board:
    monkey_cards: list[list[Card]] = [
        [
            Card(Team.monkey, Category.joker, 4),
            Card(Team.monkey, Category.rock, 1),
            Card(Team.monkey, Category.rock, 2),
            Card(Team.monkey, Category.rock, 3),
        ],
        [
            Card(Team.monkey, Category.paper, 1),
            Card(Team.monkey, Category.paper, 2),
            Card(Team.monkey, Category.paper, 3),
        ],
        [
            Card(Team.monkey, Category.scissors, 1),
            Card(Team.monkey, Category.scissors, 2),
        ],
        [
            Card(Team.monkey, Category.scissors, 3),
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
            Card(Team.wolf, Category.scissors, 3),
        ],
        [
            Card(Team.wolf, Category.scissors, 1),
            Card(Team.wolf, Category.scissors, 2),
        ],
        [
            Card(Team.wolf, Category.paper, 1),
            Card(Team.wolf, Category.paper, 2),
            Card(Team.wolf, Category.paper, 3),
        ],
        [
            Card(Team.wolf, Category.joker, 4),
            Card(Team.wolf, Category.rock, 1),
            Card(Team.wolf, Category.rock, 2),
            Card(Team.wolf, Category.rock, 3),
        ],
    ]

    return Board(monkey_cards, wolf_cards)


def make_ordered_cards(team: Team) -> list[Card]:
    return [
        Card(team, Category.rock, 1),
        Card(team, Category.rock, 2),
        Card(team, Category.rock, 3),
        Card(team, Category.paper, 1),
        Card(team, Category.paper, 2),
        Card(team, Category.paper, 3),
        Card(team, Category.scissors, 1),
        Card(team, Category.scissors, 2),
        Card(team, Category.scissors, 3),
        Card(team, Category.joker, 4),
    ]
