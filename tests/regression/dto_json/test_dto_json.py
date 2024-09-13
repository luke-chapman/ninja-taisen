from pathlib import Path

from ninja_taisen import execute_move
from ninja_taisen.dtos import (
    BoardDto,
    CategoryDto,
    ChooseRequest,
    ChooseResponse,
    DiceRollDto,
    MoveDto,
    Strategy,
    TeamDto, ExecuteRequest, ExecuteResponse
)
from ninja_taisen.objects.cards import WP2, WR3
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


def test_for_dto_json_changes(regen: bool) -> None:
    board_dto_1 = sample_board_dto()

    board = Board.from_dto(board_dto_1)
    board_dto_2 = board.to_dto()
    assert board_dto_1 == board_dto_2

    dice = DiceRollDto(rock=1, paper=3, scissors=2)

    choose_request_1 = ChooseRequest(
        board=board_dto_1,
        dice=dice,
        team=TeamDto.wolf,
        strategy=Strategy.metric_strength,
    )
    choose_response_1 = ChooseResponse(
        moves=[
            MoveDto(dice_category=CategoryDto.paper, card=WP2.to_dto()),
            MoveDto(dice_category=CategoryDto.rock, card=WR3.to_dto()),
        ]
    )

    execute_request_1 = ExecuteRequest(board=board_dto_1, dice=dice, team=TeamDto.wolf, moves=choose_request_1.moves)
    execute_response_1 = execute_move(execute_request_1)

    json_dir = Path(__file__).resolve().parent
    board_json = json_dir / "board.json"
    choose_request_json = json_dir / "choose_request.json"
    choose_response_json = json_dir / "choose_response.json"
    execute_request_json = json_dir / "execute_request.json"
    execute_response_json = json_dir / "execute_response.json"

    if regen:
        board_dto_1.to_json_file(board_json, indent=None)
        choose_request_1.to_json_file(choose_request_json, indent=None)
        choose_response_1.to_json_file(choose_response_json, indent=None)
        execute_request_1.to_json_file(execute_request_json, indent=None)
        execute_response_1.to_json_file(execute_response_json, indent=None)
    else:
        board_content = board_json.read_text()
        board_dto_3 = BoardDto.model_validate_json(board_content)
        assert board_dto_1 == board_dto_3

        choose_request_content = choose_request_json.read_text()
        choose_request_2 = ChooseRequest.model_validate_json(choose_request_content)
        assert choose_request_2 == choose_request_1

        choose_response_content = choose_response_json.read_text()
        choose_response_2 = ChooseResponse.model_validate_json(choose_response_content)
        assert choose_response_2 == choose_response_1

        execute_request_content = execute_request_json.read_text()
        execute_request_2 = ExecuteRequest.model_validate_json(execute_request_content)
        assert execute_request_2 == execute_request_1

        execute_response_content = execute_response_json.read_text()
        execute_response_2 = ExecuteResponse.model_validate_json(execute_response_content)
        assert execute_response_2 == execute_response_1
