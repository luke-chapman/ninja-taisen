from ninja_taisen.dtos import BoardDto, CardDto, CardPilesDto, CategoryDto, TeamDto
from ninja_taisen.objects.safe_random import SafeRandom


def make_board(random: SafeRandom, shuffle_cards: bool = True) -> BoardDto:
    return BoardDto(monkey_cards=_monkey_cards(random, shuffle_cards), wolf_cards=_wolf_cards(random, shuffle_cards))


def _monkey_cards(random: SafeRandom, shuffle_cards: bool) -> CardPilesDto:
    cards: CardPilesDto = ([], [], [], [], [], [], [], [], [], [], [])
    cards[0].append(CardDto(team=TeamDto.monkey, category=CategoryDto.joker, strength=4))

    remaining_cards = _non_jokers(TeamDto.monkey, random, shuffle_cards)
    _add_remaining_cards(cards, remaining_cards, {0: 3, 1: 3, 2: 2, 3: 1})

    return cards


def _wolf_cards(random: SafeRandom, shuffle_cards: bool) -> CardPilesDto:
    cards: CardPilesDto = ([], [], [], [], [], [], [], [], [], [], [])
    cards[-1].append(CardDto(team=TeamDto.wolf, category=CategoryDto.joker, strength=4))

    remaining_cards = _non_jokers(TeamDto.wolf, random, shuffle_cards)
    _add_remaining_cards(cards, remaining_cards, {-1: 3, -2: 3, -3: 2, -4: 1})

    return cards


def _non_jokers(team: TeamDto, random: SafeRandom, shuffle_cards: bool) -> list[CardDto]:
    non_jokers = [
        CardDto(team=team, category=CategoryDto.rock, strength=1),
        CardDto(team=team, category=CategoryDto.rock, strength=2),
        CardDto(team=team, category=CategoryDto.rock, strength=3),
        CardDto(team=team, category=CategoryDto.paper, strength=1),
        CardDto(team=team, category=CategoryDto.paper, strength=2),
        CardDto(team=team, category=CategoryDto.paper, strength=3),
        CardDto(team=team, category=CategoryDto.scissors, strength=1),
        CardDto(team=team, category=CategoryDto.scissors, strength=2),
        CardDto(team=team, category=CategoryDto.scissors, strength=3),
    ]

    if shuffle_cards:
        random.shuffle(non_jokers)

    return non_jokers


def _add_remaining_cards(
    cards: CardPilesDto,
    shuffled_cards: list[CardDto],
    initial_positions: dict[int, int],
) -> None:
    index = 0
    for position_index, count in initial_positions.items():
        for _ in range(count):
            cards[position_index].append(shuffled_cards[index])
            index += 1

    assert index == 9
