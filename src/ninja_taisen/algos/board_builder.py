from ninja_taisen.objects.safe_random import SafeRandom
from ninja_taisen.public_types import BOARD_LENGTH, Board, Card, Category, Team


def make_board(random: SafeRandom, shuffle_cards: bool = True) -> Board:
    return Board(_monkey_cards(random, shuffle_cards), _wolf_cards(random, shuffle_cards))


def _monkey_cards(random: SafeRandom, shuffle_cards: bool) -> list[list[Card]]:
    cards: list[list[Card]] = [[] for _ in range(BOARD_LENGTH)]
    cards[0].append(Card(Team.monkey, Category.joker, 4))

    remaining_cards = _non_jokers(Team.monkey, random, shuffle_cards)
    _add_remaining_cards(cards, remaining_cards, {0: 3, 1: 3, 2: 2, 3: 1})

    return cards


def _wolf_cards(random: SafeRandom, shuffle_cards: bool) -> list[list[Card]]:
    cards: list[list[Card]] = [[] for _ in range(BOARD_LENGTH)]
    cards[-1].append(Card(Team.wolf, Category.joker, 4))

    remaining_cards = _non_jokers(Team.wolf, random, shuffle_cards)
    _add_remaining_cards(cards, remaining_cards, {-1: 3, -2: 3, -3: 2, -4: 1})

    return cards


def _non_jokers(team: Team, random: SafeRandom, shuffle_cards: bool) -> list[Card]:
    non_jokers = [
        Card(team, Category.rock, 1),
        Card(team, Category.rock, 2),
        Card(team, Category.rock, 3),
        Card(team, Category.paper, 1),
        Card(team, Category.paper, 2),
        Card(team, Category.paper, 3),
        Card(team, Category.scissors, 1),
        Card(team, Category.scissors, 2),
        Card(team, Category.scissors, 3),
    ]

    if shuffle_cards:
        random.shuffle(non_jokers)

    return non_jokers


def _add_remaining_cards(
    cards: list[list[Card]],
    shuffled_cards: list[Card],
    initial_positions: dict[int, int],
) -> None:
    index = 0
    for position_index, count in initial_positions.items():
        for _ in range(count):
            cards[position_index].append(shuffled_cards[index])
            index += 1

    assert index == 9
