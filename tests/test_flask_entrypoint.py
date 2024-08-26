import subprocess
import sys
from pathlib import Path
from typing import Any

import requests

from ninja_taisen import ChooseRequest, execute_move
from ninja_taisen.algos.board_builder import make_board
from ninja_taisen.dtos import (
    CategoryDto,
    ChooseResponse,
    DiceRollDto,
    ExecuteRequest,
    ExecuteResponse,
    MoveDto,
    TeamDto,
)
from ninja_taisen.objects.safe_random import SafeRandom
from tests.conftest import validate_choose_response


def test_choose(tmp_path: Path) -> None:
    random = SafeRandom(0)
    team = TeamDto.monkey

    choose_request = ChooseRequest(
        board=make_board(random=random, shuffle_cards=True).to_dto(),
        dice=DiceRollDto(rock=random.roll_dice(), paper=random.roll_dice(), scissors=random.roll_dice()),
        team=team,
    )

    response = __submit_request(
        url="http://localhost:5000/choose",
        json=choose_request.model_dump(by_alias=True, round_trip=True),
        tmp_path=tmp_path,
    )
    assert response.status_code == 200, f"status_code={response.status_code}, text={response.text}"

    choose_response = ChooseResponse.model_validate(response.json())
    validate_choose_response(choose_response, team)


def test_execute(tmp_path: Path) -> None:
    random = SafeRandom(0)
    team = TeamDto.wolf

    execute_request = ExecuteRequest(
        board=make_board(random=random, shuffle_cards=True).to_dto(),
        dice=DiceRollDto(rock=random.roll_dice(), paper=random.roll_dice(), scissors=random.roll_dice()),
        team=team,
        moves=[MoveDto(dice_category=CategoryDto.rock, card="WR2")],
    )

    response = __submit_request(
        url="http://localhost:5000/execute",
        json=execute_request.model_dump(by_alias=True, round_trip=True),
        tmp_path=tmp_path,
    )
    assert response.status_code == 200, f"status_code={response.status_code}, text={response.text}"

    actual_response = ExecuteResponse.model_validate(response.json())
    expected_response = execute_move(execute_request)
    assert actual_response == expected_response


def __submit_request(url: str, json: dict[str, Any], tmp_path: Path) -> requests.Response:
    process: subprocess.Popen[bytes] | None = None
    flask_entrypoint = Path(__file__).resolve().parent.parent / "src" / "ninja_taisen" / "flask_entrypoint.py"
    assert flask_entrypoint.is_file()

    try:
        command_line = [
            sys.executable,
            "-m",
            "flask",
            "--app",
            str(flask_entrypoint),
            "run",
        ]
        process = subprocess.Popen(command_line, cwd=tmp_path)
        return requests.post(url=url, json=json)
    finally:
        if process is not None:
            process.terminate()
            process.wait()
