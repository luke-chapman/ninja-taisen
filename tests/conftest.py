import pytest
from _pytest.config import Parser
from _pytest.fixtures import FixtureRequest


def pytest_addoption(parser: Parser) -> None:
    parser.addoption("--regen", action="store_true", help="Regenerate expected results in regression tests")


@pytest.fixture
def regen(request: FixtureRequest) -> None:
    return request.config.getoption("--regen")
