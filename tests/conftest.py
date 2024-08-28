import logging

import pytest
from _pytest.config.argparsing import Parser
from _pytest.fixtures import FixtureRequest
from _pytest.logging import LogCaptureFixture

from ninja_taisen import ChooseResponse
from ninja_taisen.dtos import TeamDto
from ninja_taisen.objects.types import CATEGORY_BY_DTO, TEAM_BY_DTO, Card, Category


@pytest.fixture(autouse=True)
def set_log_level(caplog: LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO)


def pytest_addoption(parser: Parser) -> None:
    parser.addoption("--regen", action="store_true", help="Regenerate expected results in regression tests")


@pytest.fixture
def regen(request: FixtureRequest) -> None:
    return request.config.getoption("--regen")


def validate_choose_response(response: ChooseResponse, team: TeamDto) -> None:
    assert 0 <= len(response.moves) <= 3

    seen_dice_categories: set[Category] = set()
    seen_cards: set[Card] = set()

    for move in response.moves:
        dice_category = CATEGORY_BY_DTO[move.dice_category]
        card = Card.from_dto(move.card)

        # The card should be of the desired team
        assert card.team == TEAM_BY_DTO[team]

        # The card's category should match the dice category, unless it's a joker
        if card.category != Category.joker:
            assert card.category == dice_category

        # We can only move a card once, and we can only use a dice_category once
        assert dice_category not in seen_dice_categories
        assert card not in seen_cards
        seen_dice_categories.add(dice_category)
        seen_cards.add(card)
