from collections import defaultdict
from itertools import chain

from more_itertools import unique_everseen

from ninja_taisen.algos.board_builder import make_board
from ninja_taisen.objects.cards import (
    MJ4,
    MP1,
    MP2,
    MP3,
    MR1,
    MR2,
    MR3,
    MS1,
    MS2,
    MS3,
    WJ4,
    WP1,
    WP2,
    WP3,
    WR1,
    WR2,
    WR3,
    WS1,
    WS2,
    WS3,
)
from ninja_taisen.objects.safe_random import SafeRandom
from ninja_taisen.objects.types import BOARD_LENGTH, Board, Card, Category, Team


def test_make_board_not_shuffled() -> None:
    actual_board = make_board(shuffle_cards=False, random=SafeRandom(0))
    expected_board = make_non_shuffled_board()

    assert expected_board == actual_board


def test_make_board_shuffled() -> None:
    shuffled_board = make_board(shuffle_cards=True, random=SafeRandom(0))

    non_shuffled_board = make_non_shuffled_board()
    assert non_shuffled_board != shuffled_board

    monkey_lengths = [len(non_shuffled_board.monkey_cards[i]) for i in range(BOARD_LENGTH)]
    wolf_lengths = [len(non_shuffled_board.wolf_cards[i]) for i in range(BOARD_LENGTH)]

    assert monkey_lengths == [4, 3, 2, 1, 0, 0, 0, 0, 0, 0, 0]
    assert wolf_lengths == [0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4]

    unique_monkey_cards = sorted(unique_everseen(chain.from_iterable(shuffled_board.monkey_cards.values())))
    unique_wolf_cards = sorted(unique_everseen(chain.from_iterable(shuffled_board.wolf_cards.values())))

    assert unique_monkey_cards == make_ordered_cards(team=Team.monkey)
    assert unique_wolf_cards == make_ordered_cards(team=Team.wolf)


def make_non_shuffled_board() -> Board:
    board = Board(monkey_cards=defaultdict(list), wolf_cards=defaultdict(list))
    board.monkey_cards[0] = [MJ4, MR1, MR2, MR3]
    board.monkey_cards[1] = [MP1, MP2, MP3]
    board.monkey_cards[2] = [MS1, MS2]
    board.monkey_cards[3] = [MS3]

    board.wolf_cards[7] = [WS3]
    board.wolf_cards[8] = [WS1, WS2]
    board.wolf_cards[9] = [WP1, WP2, WP3]
    board.wolf_cards[10] = [WJ4, WR1, WR2, WR3]
    return board


def make_ordered_cards(team: Team) -> list[Card]:
    return [
        Card(team=team, category=Category.rock, strength=1),
        Card(team=team, category=Category.rock, strength=2),
        Card(team=team, category=Category.rock, strength=3),
        Card(team=team, category=Category.paper, strength=1),
        Card(team=team, category=Category.paper, strength=2),
        Card(team=team, category=Category.paper, strength=3),
        Card(team=team, category=Category.scissors, strength=1),
        Card(team=team, category=Category.scissors, strength=2),
        Card(team=team, category=Category.scissors, strength=3),
        Card(team=team, category=Category.joker, strength=4),
    ]
