from ninja_taisen.objects.safe_random import SafeRandom
from ninja_taisen.public_types import Board, Card, CardPiles, Category, Team


def make_board(random: SafeRandom, shuffle_cards: bool = True) -> Board:
    return Board(monkey_cards=_monkey_cards(random, shuffle_cards), wolf_cards=_wolf_cards(random, shuffle_cards))


def _monkey_cards(random: SafeRandom, shuffle_cards: bool) -> CardPiles:
    cards: CardPiles = ([], [], [], [], [], [], [], [], [], [], [])
    cards[0].append(Card(team=Team.monkey, category=Category.joker, strength=4))

    remaining_cards = _non_jokers(Team.monkey, random, shuffle_cards)
    _add_remaining_cards(cards, remaining_cards, {0: 3, 1: 3, 2: 2, 3: 1})

    return cards


def _wolf_cards(random: SafeRandom, shuffle_cards: bool) -> CardPiles:
    cards: CardPiles = ([], [], [], [], [], [], [], [], [], [], [])
    cards[-1].append(Card(team=Team.wolf, category=Category.joker, strength=4))

    remaining_cards = _non_jokers(Team.wolf, random, shuffle_cards)
    _add_remaining_cards(cards, remaining_cards, {-1: 3, -2: 3, -3: 2, -4: 1})

    return cards


def _non_jokers(team: Team, random: SafeRandom, shuffle_cards: bool) -> list[Card]:
    non_jokers = [
        Card(team=team, category=Category.rock, strength=1),
        Card(team=team, category=Category.rock, strength=2),
        Card(team=team, category=Category.rock, strength=3),
        Card(team=team, category=Category.paper, strength=1),
        Card(team=team, category=Category.paper, strength=2),
        Card(team=team, category=Category.paper, strength=3),
        Card(team=team, category=Category.scissors, strength=1),
        Card(team=team, category=Category.scissors, strength=2),
        Card(team=team, category=Category.scissors, strength=3),
    ]

    if shuffle_cards:
        random.shuffle(non_jokers)

    return non_jokers


def _add_remaining_cards(
    cards: CardPiles,
    shuffled_cards: list[Card],
    initial_positions: dict[int, int],
) -> None:
    index = 0
    for position_index, count in initial_positions.items():
        for _ in range(count):
            cards[position_index].append(shuffled_cards[index])
            index += 1

    assert index == 9
