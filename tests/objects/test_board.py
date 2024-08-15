from more_itertools import unique_everseen
from ninja_taisen.objects.board import Board
from ninja_taisen.objects.card import Card, CombatCategory, Team


def test_equality() -> None:
    board_a = mock_board()
    board_b = mock_board()
    assert board_a == board_a, f"{board_a} != {board_a}"
    assert board_a == board_b, f"{board_a} != {board_b}"


def test_non_equality() -> None:
    board_a = mock_board()
    board_b = board_a.clone()
    board_b.wolf_cards[5].append(Card(Team.WOLF, CombatCategory.SCISSORS, 2))

    assert board_a != board_b, f"{board_a} == {board_b}"


def test_clone() -> None:
    board_a = mock_board()
    board_b = board_a.clone()
    assert board_a == board_b, f"{board_a} != {board_b}"


def test_unique_everseen() -> None:
    boards = [mock_board(), mock_board()]
    boards[0].compute_hash()
    boards[1].compute_hash()
    unique_boards = list(unique_everseen(boards))
    assert len(unique_boards) == 1
    assert [boards[0]] == unique_boards


def test_str() -> None:
    board = mock_board()
    expected_string = (
        "MR3                                         \n"
        + "MR2 MP3                                     \n"
        + "MR1 MP2 MS2                                 \n"
        + "MJ4 MP1 MS1 MS3                             \n"
        + "--- --- --- --- --- --- --- --- --- --- --- \n"
        + "                            WS3 WS1 WP1 WJ4 \n"
        + "                                WS2 WP2 WR1 \n"
        + "                                    WP3 WR2 \n"
        + "                                        WR3 \n"
    )

    actual_string = board.__str__()
    assert expected_string == actual_string, f"\n{expected_string}\n != \n{actual_string}\n"


def mock_board() -> Board:

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
