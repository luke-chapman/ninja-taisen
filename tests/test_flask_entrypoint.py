import requests

from ninja_taisen import ChooseRequest, execute_move
from ninja_taisen.algos.board_builder import make_board
from ninja_taisen.dtos import ChooseResponse, DiceRollDto, TeamDto, ExecuteRequest, MoveDto, CategoryDto, \
    ExecuteResponse
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

    response = requests.post(
        url=URL + "/choose",
        json=choose_request.model_dump(by_alias=True, round_trip=True),
    )
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
        moves=[
            MoveDto(dice_category=CategoryDto.rock, card="WR2")
        ]
    )

    response = requests.post(
        url=URL + "/execute",
        json=execute_request.model_dump(by_alias=True, round_trip=True),
    )
    assert response.status_code == 200, f"status_code={response.status_code}, text={response.text}"

    actual_response = ExecuteResponse.model_validate(response.json())
    expected_response = execute_move(execute_request)
    assert actual_response == expected_response
