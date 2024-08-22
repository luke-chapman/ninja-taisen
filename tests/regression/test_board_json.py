from pathlib import Path

from ninja_taisen.dtos import BoardDto, CardDto, CategoryDto
from ninja_taisen.objects.types import Board


def sample_board_dto() -> BoardDto:
    return BoardDto(
        monkey_cards={
            0: [
                CardDto(category=CategoryDto.joker, strength=4),
                CardDto(category=CategoryDto.rock, strength=3),
                CardDto(category=CategoryDto.paper, strength=2),
                CardDto(category=CategoryDto.scissors, strength=1),
            ],
            1: [
                CardDto(category=CategoryDto.paper, strength=3),
                CardDto(category=CategoryDto.scissors, strength=2),
                CardDto(category=CategoryDto.rock, strength=1),
            ],
            2: [
                CardDto(category=CategoryDto.scissors, strength=3),
                CardDto(category=CategoryDto.rock, strength=2),
            ],
            3: [
                CardDto(category=CategoryDto.paper, strength=1),
            ],
        },
        wolf_cards={
            7: [
                CardDto(category=CategoryDto.paper, strength=1),
            ],
            8: [
                CardDto(category=CategoryDto.scissors, strength=3),
                CardDto(category=CategoryDto.rock, strength=2),
            ],
            9: [
                CardDto(category=CategoryDto.paper, strength=1),
                CardDto(category=CategoryDto.scissors, strength=2),
                CardDto(category=CategoryDto.rock, strength=3),
            ],
            10: [
                CardDto(category=CategoryDto.joker, strength=4),
                CardDto(category=CategoryDto.rock, strength=1),
                CardDto(category=CategoryDto.paper, strength=2),
                CardDto(category=CategoryDto.scissors, strength=3),
            ],
        },
    )


def test_for_board_json_changes(regen: bool) -> None:
    board_dto_1 = sample_board_dto()

    board = Board.from_dto(board_dto_1)
    board_dto_2 = board.to_dto()
    assert board_dto_1 == board_dto_2

    board_json = Path(__file__).resolve().parent / "expected_board.json"
    if regen:
        content = board_dto_1.model_dump_json(indent=2, round_trip=True)
        board_json.write_text(content)
    else:
        content = board_json.read_text()
        board_dto_3 = BoardDto.model_validate_json(content)
        assert board_dto_1 == board_dto_3
