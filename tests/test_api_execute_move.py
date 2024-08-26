from pathlib import Path

import pytest

from ninja_taisen.api import execute_move
from ninja_taisen.dtos import BoardDto, MoveRequestBody, MoveResponseBody

MOVE_BY_MOVE_DIR = Path(__file__).resolve().parent / "regression" / "move_by_move"


def __games_and_indices() -> list[tuple[str, int]]:
    games_and_indices: list[tuple[str, int]] = []
    game_dirs = sorted(d for d in MOVE_BY_MOVE_DIR.iterdir() if d.is_dir())
    for game_dir in game_dirs:
        requests_json = sorted(r for r in game_dir.iterdir() if r.name.startswith("request_"))
        for request_json in requests_json:
            turn_index = int(request_json.name[len("request_") : -len(".json")])
            games_and_indices.append((game_dir.name, turn_index))
    return games_and_indices


@pytest.mark.parametrize("game,turn_index", __games_and_indices())
def test_move_by_move(game: str, turn_index: int) -> None:
    request_json = MOVE_BY_MOVE_DIR / game / f"request_{turn_index}.json"
    response_json = MOVE_BY_MOVE_DIR / game / f"response_{turn_index}.json"

    request = MoveRequestBody.model_validate_json(request_json.read_text())
    response = MoveResponseBody.model_validate_json(response_json.read_text())

    next_request_json = MOVE_BY_MOVE_DIR / game / f"request_{turn_index+1}.json"
    if next_request_json.exists():
        expected_board = MoveRequestBody.model_validate_json(next_request_json.read_text()).board
    else:
        final_board_json = MOVE_BY_MOVE_DIR / game / "final_board.json"
        expected_board = BoardDto.model_validate_json(final_board_json.read_text())

    board = execute_move(request, response)
    assert board == expected_board
