from pathlib import Path

from ninja_taisen import choose_move, execute_move
from ninja_taisen.dtos import (
    BoardDto,
    ChooseRequest,
    ChooseResponse,
    DiceRollDto,
    ExecuteRequest,
    ExecuteResponse,
    Strategy,
    TeamDto,
)
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


def test_board_round_trips_to_internal_type() -> None:
    board_dto = sample_board_dto()

    board = Board.from_dto(board_dto)
    board_dto_2 = board.to_dto()
    assert board_dto == board_dto_2


def test_for_dto_json_changes(regen: bool) -> None:
    choose_request = ChooseRequest(
        board=sample_board_dto(),
        dice=DiceRollDto(rock=1, paper=3, scissors=2),
        team=TeamDto.monkey,
        strategy=Strategy.random,
        seed=42,
    )
    choose_response = choose_move(choose_request)

    execute_request = ExecuteRequest(
        board=choose_request.board, dice=choose_request.dice, team=choose_request.team, moves=choose_response.moves
    )
    execute_response = execute_move(execute_request)

    json_dir = Path(__file__).resolve().parent
    choose_request_json = json_dir / "choose_request.json"
    choose_response_json = json_dir / "choose_response.json"
    execute_request_json = json_dir / "execute_request.json"
    execute_response_json = json_dir / "execute_response.json"

    if regen:
        choose_request.to_json_file(choose_request_json, indent=None)
        choose_response.to_json_file(choose_response_json, indent=None)
        execute_request.to_json_file(execute_request_json, indent=None)
        execute_response.to_json_file(execute_response_json, indent=None)
    else:
        choose_request_content = choose_request_json.read_text()
        choose_request_2 = ChooseRequest.model_validate_json(choose_request_content)
        assert choose_request_2 == choose_request

        choose_response_content = choose_response_json.read_text()
        choose_response_2 = ChooseResponse.model_validate_json(choose_response_content)
        assert choose_response_2 == choose_response

        execute_request_content = execute_request_json.read_text()
        execute_request_2 = ExecuteRequest.model_validate_json(execute_request_content)
        assert execute_request_2 == execute_request

        execute_response_content = execute_response_json.read_text()
        execute_response_2 = ExecuteResponse.model_validate_json(execute_response_content)
        assert execute_response_2 == execute_response
