from pathlib import Path

from ninja_taisen.public_types import Board, Card, Category, Team


def test_board(regen: bool) -> None:
    board = Board(
        monkey_cards=(
            [
                Card(team=Team.monkey, category=Category.joker, strength=4),
                Card(team=Team.monkey, category=Category.rock, strength=3),
                Card(team=Team.monkey, category=Category.paper, strength=2),
                Card(team=Team.monkey, category=Category.scissors, strength=1),
            ],
            [
                Card(team=Team.monkey, category=Category.paper, strength=3),
                Card(team=Team.monkey, category=Category.scissors, strength=2),
                Card(team=Team.monkey, category=Category.rock, strength=1),
            ],
            [
                Card(team=Team.monkey, category=Category.scissors, strength=3),
                Card(team=Team.monkey, category=Category.rock, strength=2),
            ],
            [
                Card(team=Team.monkey, category=Category.paper, strength=1),
            ],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
        ),
        wolf_cards=(
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [
                Card(team=Team.wolf, category=Category.paper, strength=1),
            ],
            [
                Card(team=Team.wolf, category=Category.scissors, strength=3),
                Card(team=Team.wolf, category=Category.rock, strength=2),
            ],
            [
                Card(team=Team.wolf, category=Category.paper, strength=1),
                Card(team=Team.wolf, category=Category.scissors, strength=2),
                Card(team=Team.wolf, category=Category.rock, strength=3),
            ],
            [
                Card(team=Team.wolf, category=Category.joker, strength=4),
                Card(team=Team.wolf, category=Category.rock, strength=1),
                Card(team=Team.wolf, category=Category.paper, strength=2),
                Card(team=Team.wolf, category=Category.scissors, strength=3),
            ],
        ),
    )

    board_json = Path(__file__).resolve().parent / "board.json"
    if regen:
        content = board.model_dump_json(indent=2, round_trip=True)
        board_json.write_text(content)
    else:
        content = board_json.read_text()
        recovered_board = Board.model_validate_json(content)
        assert board == recovered_board
