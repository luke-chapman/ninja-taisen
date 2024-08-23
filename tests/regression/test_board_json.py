from pathlib import Path

from ninja_taisen.dtos import BoardDto, CategoryDto, DiceRollDto, MoveDto, MoveRequestBody, MoveResponseBody, TeamDto
from ninja_taisen.objects.types import Board


def sample_board_dto() -> BoardDto:
    return BoardDto(
        monkey={
            0: ["MJ4", "MR3", "MP2", "MS1"],
            1: ["MP3", "MS2", "MR1"],
            2: ["MS3", "MR2"],
            3: ["MP1"],
        },
        wolf={
            7: ["WP3"],
            8: ["WS1", "WR2"],
            9: ["WP1", "WS2", "WR3"],
            10: ["WJ4", "WR1", "WP2", "WS3"],
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
        board_json.write_text(board_dto_1.model_dump_json(indent=2, round_trip=True, by_alias=True))
        move_request_body_json.write_text(move_request_body_1.model_dump_json(indent=2, round_trip=True, by_alias=True))
        move_response_body_json.write_text(
            move_response_body_1.model_dump_json(indent=2, round_trip=True, by_alias=True)
        )
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
