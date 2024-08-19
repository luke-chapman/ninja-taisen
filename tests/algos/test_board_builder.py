from itertools import chain

from more_itertools import unique_everseen

from ninja_taisen.algos.board_builder import make_board
from ninja_taisen.objects.safe_random import SafeRandom
from ninja_taisen.public_types import BOARD_LENGTH, Board, Card, CardPiles, Category, Team


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
    monkey_cards: CardPiles = (
        [
            Card(team=Team.monkey, category=Category.joker, strength=4),
            Card(team=Team.monkey, category=Category.rock, strength=1),
            Card(team=Team.monkey, category=Category.rock, strength=2),
            Card(team=Team.monkey, category=Category.rock, strength=3),
        ],
        [
            Card(team=Team.monkey, category=Category.paper, strength=1),
            Card(team=Team.monkey, category=Category.paper, strength=2),
            Card(team=Team.monkey, category=Category.paper, strength=3),
        ],
        [
            Card(team=Team.monkey, category=Category.scissors, strength=1),
            Card(team=Team.monkey, category=Category.scissors, strength=2),
        ],
        [
            Card(team=Team.monkey, category=Category.scissors, strength=3),
        ],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
    )

    wolf_cards: CardPiles = (
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [
            Card(team=Team.wolf, category=Category.scissors, strength=3),
        ],
        [
            Card(team=Team.wolf, category=Category.scissors, strength=1),
            Card(team=Team.wolf, category=Category.scissors, strength=2),
        ],
        [
            Card(team=Team.wolf, category=Category.paper, strength=1),
            Card(team=Team.wolf, category=Category.paper, strength=2),
            Card(team=Team.wolf, category=Category.paper, strength=3),
        ],
        [
            Card(team=Team.wolf, category=Category.joker, strength=4),
            Card(team=Team.wolf, category=Category.rock, strength=1),
            Card(team=Team.wolf, category=Category.rock, strength=2),
            Card(team=Team.wolf, category=Category.rock, strength=3),
        ],
    )

    return Board(monkey_cards=monkey_cards, wolf_cards=wolf_cards)


def make_ordered_cards(team: Team) -> list[Card]:
    return [
        Card(team=team, category=Category.joker, strength=4),
        Card(team=team, category=Category.paper, strength=1),
        Card(team=team, category=Category.paper, strength=2),
        Card(team=team, category=Category.paper, strength=3),
        Card(team=team, category=Category.rock, strength=1),
        Card(team=team, category=Category.rock, strength=2),
        Card(team=team, category=Category.rock, strength=3),
        Card(team=team, category=Category.scissors, strength=1),
        Card(team=team, category=Category.scissors, strength=2),
        Card(team=team, category=Category.scissors, strength=3),
    ]
