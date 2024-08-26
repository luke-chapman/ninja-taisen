from pathlib import Path

import pytest

from ninja_taisen import ExecuteResponse
from ninja_taisen.api import choose_move, execute_move
from ninja_taisen.dtos import BoardDto, ChooseRequest, ChooseResponse, ExecuteRequest
from ninja_taisen.objects.types import ALL_STRATEGY_NAMES
from tests.conftest import validate_choose_response

TURN_BY_TURN_DIR = Path(__file__).resolve().parent / "regression" / "turn_by_turn"


def __games_and_indices() -> list[tuple[str, int]]:
    games_and_indices: list[tuple[str, int]] = []
    game_dirs = sorted(d for d in TURN_BY_TURN_DIR.iterdir() if d.is_dir())
    for game_dir in game_dirs:
        requests_json = sorted(r for r in game_dir.iterdir() if r.name.startswith("request_"))
        for request_json in requests_json:
            turn_index = int(request_json.name[len("request_") : -len(".json")])
            games_and_indices.append((game_dir.name, turn_index))
    return games_and_indices


@pytest.mark.parametrize("game,turn_index", __games_and_indices())
def test_execute(game: str, turn_index: int) -> None:
    request_json = TURN_BY_TURN_DIR / game / f"request_{turn_index}.json"
    response_json = TURN_BY_TURN_DIR / game / f"response_{turn_index}.json"

    request = ChooseRequest.model_validate_json(request_json.read_text())
    response = ChooseResponse.model_validate_json(response_json.read_text())
    execute_request = ExecuteRequest(board=request.board, dice=request.dice, team=request.team, moves=response.moves)

    next_request_json = TURN_BY_TURN_DIR / game / f"request_{turn_index + 1}.json"
    if next_request_json.exists():
        expected_board = ChooseRequest.model_validate_json(next_request_json.read_text()).board
    else:
        final_board_json = TURN_BY_TURN_DIR / game / "final_board.json"
        expected_board = BoardDto.model_validate_json(final_board_json.read_text())
    expected_response = ExecuteResponse(board=expected_board)

    execute_response = execute_move(request=execute_request)
    assert execute_response == expected_response


@pytest.mark.parametrize("strategy_name", ALL_STRATEGY_NAMES)
@pytest.mark.parametrize("game,turn_index", __games_and_indices())
def test_choose(game: str, turn_index: int, strategy_name: str) -> None:
    request_json = TURN_BY_TURN_DIR / game / f"request_{turn_index}.json"
    request = ChooseRequest.model_validate_json(request_json.read_text())

    response = choose_move(request=request, strategy_name=strategy_name, random=None)
    validate_choose_response(response, request.team)
