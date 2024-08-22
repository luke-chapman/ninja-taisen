from pathlib import Path

from ninja_taisen.dtos import BoardDto, CategoryDto, DiceRollDto, MoveDto, MoveRequestBody, MoveResponseBody, TeamDto
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

    move_request_body_1 = MoveRequestBody(
        board=board_dto_1, dice=DiceRollDto(rock=1, paper=3, scissors=2), team=TeamDto.wolf
    )
    move_response_body_1 = MoveResponseBody(
        moves=[MoveDto(dice_category=CategoryDto.paper, card="P2"), MoveDto(dice_category=CategoryDto.rock, card="R3")]
    )

    json_dir = Path(__file__).resolve().parent
    board_json = json_dir / "board.json"
    move_request_body_json = json_dir / "move_request_body.json"
    move_response_body_json = json_dir / "move_response_body.json"

    if regen:
        board_json.write_text(board_dto_1.model_dump_json(indent=2, round_trip=True))
        move_request_body_json.write_text(move_request_body_1.model_dump_json(indent=2, round_trip=True))
        move_response_body_json.write_text(move_response_body_1.model_dump_json(indent=2, round_trip=True))
    else:
        board_content = board_json.read_text()
        board_dto_3 = BoardDto.model_validate_json(board_content)
        assert board_dto_1 == board_dto_3

        move_request_body_content = move_request_body_json.read_text()
        move_request_body_2 = MoveRequestBody.model_validate_json(move_request_body_content)
        assert move_request_body_2 == move_request_body_1

        move_response_body_content = move_response_body_json.read_text()
        move_response_body_2 = MoveResponseBody.model_validate_json(move_response_body_content)
        assert move_response_body_2 == move_response_body_1
