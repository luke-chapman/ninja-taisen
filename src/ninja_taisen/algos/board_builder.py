from random import shuffle
from typing import Dict, List

from ninja_taisen.objects.board import BOARD_LENGTH, Board
from ninja_taisen.objects.card import Card, CombatCategory, Team


def make_board(shuffle_cards: bool = True) -> Board:
    return Board(_monkey_cards(shuffle_cards), _wolf_cards(shuffle_cards))


def _monkey_cards(shuffle_cards: bool) -> List[List[Card]]:
    cards: List[List[Card]] = [[] for _ in range(BOARD_LENGTH)]
    cards[0].append(Card(Team.MONKEY, CombatCategory.JOKER, 4))

    remaining_cards = _non_jokers(Team.MONKEY, shuffle_cards)
    _add_remaining_cards(cards, remaining_cards, {0: 3, 1: 3, 2: 2, 3: 1})

    return cards


def _wolf_cards(shuffle_cards: bool) -> List[List[Card]]:
    cards: List[List[Card]] = [[] for _ in range(BOARD_LENGTH)]
    cards[-1].append(Card(Team.WOLF, CombatCategory.JOKER, 4))

    remaining_cards = _non_jokers(Team.WOLF, shuffle_cards)
    _add_remaining_cards(cards, remaining_cards, {-1: 3, -2: 3, -3: 2, -4: 1})

    return cards


def _non_jokers(team: Team, shuffle_cards: bool) -> List[Card]:

    non_jokers = [
        Card(team, CombatCategory.ROCK, 1),
        Card(team, CombatCategory.ROCK, 2),
        Card(team, CombatCategory.ROCK, 3),
        Card(team, CombatCategory.PAPER, 1),
        Card(team, CombatCategory.PAPER, 2),
        Card(team, CombatCategory.PAPER, 3),
        Card(team, CombatCategory.SCISSORS, 1),
        Card(team, CombatCategory.SCISSORS, 2),
        Card(team, CombatCategory.SCISSORS, 3),
    ]

    if shuffle_cards:
        shuffle(non_jokers)

    return non_jokers


def _add_remaining_cards(
    cards: List[List[Card]],
    shuffled_cards: List[Card],
    initial_positions: Dict[int, int],
) -> None:
    index = 0
    for position_index, count in initial_positions.items():
        for _ in range(count):
            cards[position_index].append(shuffled_cards[index])
            index += 1

    assert index == 9
