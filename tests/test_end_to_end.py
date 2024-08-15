import pytest
from ninja_taisen.__main__ import main
from ninja_taisen.strategy.strategy_names import StrategyNames


def __all_strategy_pairs() -> list[tuple[str, str]]:
    pairs = []
    for monkey_strategy in StrategyNames.ALL:
        for wolf_strategy in StrategyNames.ALL:
            pairs.append((monkey_strategy, wolf_strategy))
    return pairs


@pytest.mark.parametrize("monkey_strategy, wolf_strategy", __all_strategy_pairs())
def test_game_play(monkey_strategy: str, wolf_strategy: str) -> None:
    command_line = ["--games", "1", "--monkey-strategy", monkey_strategy, "--wolf-strategy", wolf_strategy]
    main(command_line)
