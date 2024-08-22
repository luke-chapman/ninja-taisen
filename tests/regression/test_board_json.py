from pathlib import Path

from ninja_taisen.dtos import BoardDto
from ninja_taisen.objects.types import Board


def sample_board_dto() -> BoardDto:
    return BoardDto(
        monkey={
            0: ["J4", "R3", "P2", "S1"],
            1: ["P3", "S2", "R1"],
            2: ["S3", "R2"],
            3: ["P1"],
        },
        wolf={
            7: ["P3"],
            8: ["S1", "R2"],
            9: ["P1", "S2", "R3"],
            10: ["J4", "R1", "P2", "S3"],
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
