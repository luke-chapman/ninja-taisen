import requests

from ninja_taisen import ChooseRequest
from ninja_taisen.algos.board_builder import make_board
from ninja_taisen.dtos import ChooseResponse, DiceRollDto, TeamDto
from ninja_taisen.objects.safe_random import SafeRandom
from tests.conftest import validate_choose_response

URL = "http://localhost:5000"


def test_choose() -> None:
    random = SafeRandom(0)
    team = TeamDto.monkey

    choose_request = ChooseRequest(
        board=make_board(random=random, shuffle_cards=True).to_dto(),
        dice=DiceRollDto(rock=random.roll_dice(), paper=random.roll_dice(), scissors=random.roll_dice()),
        team=team,
    )
    request_json = choose_request.model_dump_json(by_alias=True, round_trip=True)
    headers = {"Content-Type": "application/json"}

    response = requests.post(url=URL + "/choose", data=request_json, headers=headers)
    assert response.status_code == 200, f"status_code={response.status_code}, text={response.text}"

    choose_response = ChooseResponse.model_validate(response.json())
    validate_choose_response(choose_response, team)
