import logging

import pytest
from _pytest.config import Parser
from _pytest.fixtures import FixtureRequest
from _pytest.logging import LogCaptureFixture


@pytest.fixture(autouse=True)
def set_log_level(caplog: LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO)


def pytest_addoption(parser: Parser) -> None:
    parser.addoption("--regen", action="store_true", help="Regenerate expected results in regression tests")


@pytest.fixture
def regen(request: FixtureRequest) -> None:
    return request.config.getoption("--regen")
