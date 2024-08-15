from pathlib import Path

import polars as pl
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
def test_game_play(monkey_strategy: str, wolf_strategy: str, tmp_path: Path) -> None:
    results_file = tmp_path / "results.csv"
    command_line = [
        "--games",
        "1",
        "--monkey-strategy",
        monkey_strategy,
        "--wolf-strategy",
        wolf_strategy,
        "--results-file",
        str(results_file),
    ]
    main(command_line)

    frame = pl.read_csv(results_file)
    assert frame.columns == ["game_index", "winning_team", "turn_count", "time_taken_s"]
    assert frame["game_index"][0] == 0
    assert frame["winning_team"][0] in ("MONKEY", "WOLF", "NONE")
    assert 0 < frame["turn_count"][0] < 100
    assert 0.0 < frame["time_taken_s"][0] < 10.0
