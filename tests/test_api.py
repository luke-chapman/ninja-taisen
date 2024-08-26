from pathlib import Path

import pytest

from ninja_taisen.api import choose_move, execute_move
from ninja_taisen.dtos import BoardDto, MoveRequestBody, MoveResponseBody
from ninja_taisen.objects.types import ALL_STRATEGY_NAMES, CATEGORY_BY_DTO, TEAM_BY_DTO, Card, Category

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
def test_move_is_executed_as_expected(game: str, turn_index: int) -> None:
    request_json = TURN_BY_TURN_DIR / game / f"request_{turn_index}.json"
    response_json = TURN_BY_TURN_DIR / game / f"response_{turn_index}.json"

    request = MoveRequestBody.model_validate_json(request_json.read_text())
    response = MoveResponseBody.model_validate_json(response_json.read_text())

    next_request_json = TURN_BY_TURN_DIR / game / f"request_{turn_index + 1}.json"
    if next_request_json.exists():
        expected_board = MoveRequestBody.model_validate_json(next_request_json.read_text()).board
    else:
        final_board_json = TURN_BY_TURN_DIR / game / "final_board.json"
        expected_board = BoardDto.model_validate_json(final_board_json.read_text())

    board = execute_move(request=request, response=response)
    assert board == expected_board


@pytest.mark.parametrize("strategy_name", ALL_STRATEGY_NAMES)
@pytest.mark.parametrize("game,turn_index", __games_and_indices())
def test_choose_move_gives_sane_output(game: str, turn_index: int, strategy_name: str) -> None:
    request_json = TURN_BY_TURN_DIR / game / f"request_{turn_index}.json"
    request = MoveRequestBody.model_validate_json(request_json.read_text())

    response = choose_move(request=request, strategy_name=strategy_name, random=None)
    assert 0 <= len(response.moves) <= 3

    seen_dice_categories: set[Category] = set()
    seen_cards: set[Card] = set()

    for move in response.moves:
        dice_category = CATEGORY_BY_DTO[move.dice_category]
        card = Card.from_dto(move.card)

        # The card should be of the desired team
        assert card.team == TEAM_BY_DTO[request.team]

        # The card's category should match the dice category, unless it's a joker
        if card.category != Category.joker:
            assert card.category == dice_category

        # We can only move a card once, and we can only use a dice_category once
        assert dice_category not in seen_dice_categories
        assert card not in seen_cards
        seen_dice_categories.add(dice_category)
        seen_cards.add(card)
