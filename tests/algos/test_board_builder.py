from itertools import chain

from more_itertools import unique_everseen

from ninja_taisen.algos.board_builder import make_board
from ninja_taisen.dtos import BOARD_LENGTH, BoardDto, CardDto, CardPilesDto, CategoryDto, TeamDto
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

    assert unique_monkey_cards == make_ordered_cards(TeamDto.monkey)
    assert unique_wolf_cards == make_ordered_cards(TeamDto.wolf)


def make_non_shuffled_board() -> BoardDto:
    monkey_cards: CardPilesDto = (
        [
            CardDto(team=TeamDto.monkey, category=CategoryDto.joker, strength=4),
            CardDto(team=TeamDto.monkey, category=CategoryDto.rock, strength=1),
            CardDto(team=TeamDto.monkey, category=CategoryDto.rock, strength=2),
            CardDto(team=TeamDto.monkey, category=CategoryDto.rock, strength=3),
        ],
        [
            CardDto(team=TeamDto.monkey, category=CategoryDto.paper, strength=1),
            CardDto(team=TeamDto.monkey, category=CategoryDto.paper, strength=2),
            CardDto(team=TeamDto.monkey, category=CategoryDto.paper, strength=3),
        ],
        [
            CardDto(team=TeamDto.monkey, category=CategoryDto.scissors, strength=1),
            CardDto(team=TeamDto.monkey, category=CategoryDto.scissors, strength=2),
        ],
        [
            CardDto(team=TeamDto.monkey, category=CategoryDto.scissors, strength=3),
        ],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
    )

    wolf_cards: CardPilesDto = (
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [
            CardDto(team=TeamDto.wolf, category=CategoryDto.scissors, strength=3),
        ],
        [
            CardDto(team=TeamDto.wolf, category=CategoryDto.scissors, strength=1),
            CardDto(team=TeamDto.wolf, category=CategoryDto.scissors, strength=2),
        ],
        [
            CardDto(team=TeamDto.wolf, category=CategoryDto.paper, strength=1),
            CardDto(team=TeamDto.wolf, category=CategoryDto.paper, strength=2),
            CardDto(team=TeamDto.wolf, category=CategoryDto.paper, strength=3),
        ],
        [
            CardDto(team=TeamDto.wolf, category=CategoryDto.joker, strength=4),
            CardDto(team=TeamDto.wolf, category=CategoryDto.rock, strength=1),
            CardDto(team=TeamDto.wolf, category=CategoryDto.rock, strength=2),
            CardDto(team=TeamDto.wolf, category=CategoryDto.rock, strength=3),
        ],
    )

    return BoardDto(monkey_cards=monkey_cards, wolf_cards=wolf_cards)


def make_ordered_cards(team: TeamDto) -> list[CardDto]:
    return [
        CardDto(team=team, category=CategoryDto.joker, strength=4),
        CardDto(team=team, category=CategoryDto.paper, strength=1),
        CardDto(team=team, category=CategoryDto.paper, strength=2),
        CardDto(team=team, category=CategoryDto.paper, strength=3),
        CardDto(team=team, category=CategoryDto.rock, strength=1),
        CardDto(team=team, category=CategoryDto.rock, strength=2),
        CardDto(team=team, category=CategoryDto.rock, strength=3),
        CardDto(team=team, category=CategoryDto.scissors, strength=1),
        CardDto(team=team, category=CategoryDto.scissors, strength=2),
        CardDto(team=team, category=CategoryDto.scissors, strength=3),
    ]
