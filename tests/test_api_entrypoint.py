from fastapi.testclient import TestClient

from ninja_taisen import ChooseRequest, execute_move
from ninja_taisen.algos.board_builder import make_board
from ninja_taisen.api_entrypoint import app
from ninja_taisen.dtos import (
    CategoryDto,
    ChooseResponse,
    DiceRollDto,
    ExecuteRequest,
    ExecuteResponse,
    MoveDto,
    Strategy,
    TeamDto,
)
from ninja_taisen.objects.safe_random import SafeRandom
from tests.conftest import validate_choose_response

client = TestClient(app)


def test_choose() -> None:
    random = SafeRandom(0)
    team = TeamDto.monkey

    choose_request = ChooseRequest(
        board=make_board(random=random, shuffle_cards=True).to_dto(),
        dice=DiceRollDto(rock=random.roll_dice(), paper=random.roll_dice(), scissors=random.roll_dice()),
        team=team,
        strategy=Strategy.metric_strength,
    )

    response = client.post("/choose", json=choose_request.model_dump(by_alias=True, round_trip=True))
    assert response.status_code == 200, f"status_code={response.status_code}, text={response.text}"

    choose_response = ChooseResponse.model_validate(response.json())
    validate_choose_response(choose_response, team)


def test_execute() -> None:
    random = SafeRandom(0)
    team = TeamDto.wolf

    execute_request = ExecuteRequest(
        board=make_board(random=random, shuffle_cards=True).to_dto(),
        dice=DiceRollDto(rock=random.roll_dice(), paper=random.roll_dice(), scissors=random.roll_dice()),
        team=team,
        moves=[MoveDto(dice_category=CategoryDto.rock, card="WR2")],
    )

    response = client.post("/execute", json=execute_request.model_dump(by_alias=True, round_trip=True))
    assert response.status_code == 200, f"status_code={response.status_code}, text={response.text}"

    actual_response = ExecuteResponse.model_validate(response.json())
    expected_response = execute_move(execute_request)
    assert actual_response == expected_response
