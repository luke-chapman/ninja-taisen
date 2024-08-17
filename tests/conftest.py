import pytest


def pytest_addoption(parser) -> None:
    parser.addoption("--regen", action="store_true", help="Regenerate expected results in regression tests")


@pytest.fixture
def regen(request):
    return request.config.getoption("--regen")
