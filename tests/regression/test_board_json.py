from pathlib import Path

from ninja_taisen.dtos import BoardDto, CardDto, CategoryDto, TeamDto


def test_for_board_json_changes(regen: bool) -> None:
    board = BoardDto(
        monkey_cards=(
            [
                CardDto(team=TeamDto.monkey, category=CategoryDto.joker, strength=4),
                CardDto(team=TeamDto.monkey, category=CategoryDto.rock, strength=3),
                CardDto(team=TeamDto.monkey, category=CategoryDto.paper, strength=2),
                CardDto(team=TeamDto.monkey, category=CategoryDto.scissors, strength=1),
            ],
            [
                CardDto(team=TeamDto.monkey, category=CategoryDto.paper, strength=3),
                CardDto(team=TeamDto.monkey, category=CategoryDto.scissors, strength=2),
                CardDto(team=TeamDto.monkey, category=CategoryDto.rock, strength=1),
            ],
            [
                CardDto(team=TeamDto.monkey, category=CategoryDto.scissors, strength=3),
                CardDto(team=TeamDto.monkey, category=CategoryDto.rock, strength=2),
            ],
            [
                CardDto(team=TeamDto.monkey, category=CategoryDto.paper, strength=1),
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
                CardDto(team=TeamDto.wolf, category=CategoryDto.paper, strength=1),
            ],
            [
                CardDto(team=TeamDto.wolf, category=CategoryDto.scissors, strength=3),
                CardDto(team=TeamDto.wolf, category=CategoryDto.rock, strength=2),
            ],
            [
                CardDto(team=TeamDto.wolf, category=CategoryDto.paper, strength=1),
                CardDto(team=TeamDto.wolf, category=CategoryDto.scissors, strength=2),
                CardDto(team=TeamDto.wolf, category=CategoryDto.rock, strength=3),
            ],
            [
                CardDto(team=TeamDto.wolf, category=CategoryDto.joker, strength=4),
                CardDto(team=TeamDto.wolf, category=CategoryDto.rock, strength=1),
                CardDto(team=TeamDto.wolf, category=CategoryDto.paper, strength=2),
                CardDto(team=TeamDto.wolf, category=CategoryDto.scissors, strength=3),
            ],
        ),
    )

    board_json = Path(__file__).resolve().parent / "expected_board.json"
    if regen:
        content = board.model_dump_json(indent=2, round_trip=True)
        board_json.write_text(content)
    else:
        content = board_json.read_text()
        recovered_board = BoardDto.model_validate_json(content)
        assert board == recovered_board
