from collections import defaultdict

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
from ninja_taisen.objects.types import Board, Card


def make_board(random: SafeRandom, shuffle_cards: bool = True) -> Board:
    return Board(monkey_cards=_monkey_cards(random, shuffle_cards), wolf_cards=_wolf_cards(random, shuffle_cards))


def _monkey_cards(random: SafeRandom, shuffle_cards: bool) -> defaultdict[int, list[Card]]:
    cards: defaultdict[int, list[Card]] = defaultdict(list)
    cards[0].append(MJ4)

    remaining_cards = [MR1, MR2, MR3, MP1, MP2, MP3, MS1, MS2, MS3]
    if shuffle_cards:
        random.shuffle(remaining_cards)
    _add_remaining_cards(cards, remaining_cards, {0: 3, 1: 3, 2: 2, 3: 1})

    return cards


def _wolf_cards(random: SafeRandom, shuffle_cards: bool) -> defaultdict[int, list[Card]]:
    cards: defaultdict[int, list[Card]] = defaultdict(list)
    cards[10].append(WJ4)

    remaining_cards = [WR1, WR2, WR3, WP1, WP2, WP3, WS1, WS2, WS3]
    if shuffle_cards:
        random.shuffle(remaining_cards)
    _add_remaining_cards(cards, remaining_cards, {10: 3, 9: 3, 8: 2, 7: 1})

    return cards


def _add_remaining_cards(
    cards: defaultdict[int, list[Card]],
    shuffled_cards: list[Card],
    initial_positions: dict[int, int],
) -> None:
    index = 0
    for position_index, count in initial_positions.items():
        for _ in range(count):
            cards[position_index].append(shuffled_cards[index])
            index += 1

    assert index == 9
