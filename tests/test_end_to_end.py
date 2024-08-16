from pathlib import Path

import polars as pl
import pytest
from ninja_taisen import Instruction, Options, simulate
from ninja_taisen.__main__ import main
from ninja_taisen.strategy.strategy_names import StrategyNames


@pytest.mark.parametrize("monkey_strategy", StrategyNames.ALL)
@pytest.mark.parametrize("wolf_strategy", StrategyNames.ALL)
@pytest.mark.parametrize("invocation", ["command_line", "library_api"])
def test_game_play(monkey_strategy: str, wolf_strategy: str, invocation: str, tmp_path: Path) -> None:
    results_file = tmp_path / "results.csv"
    if invocation == "command_line":
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
    elif invocation == "library_api":
        simulate([Instruction(monkey_strategy, wolf_strategy, 0)], Options(results_file=results_file))
    else:
        raise ValueError(f"Unexpected invocation {invocation}")

    frame = pl.read_csv(results_file, schema_overrides={"start_time": pl.Datetime, "end_time": pl.Datetime})
    assert frame.columns == [
        "monkey_strategy",
        "wolf_strategy",
        "seed",
        "winner",
        "turn_count",
        "start_time",
        "end_time",
    ]
    assert frame["monkey_strategy"][0] == monkey_strategy
    assert frame["wolf_strategy"][0] == wolf_strategy
    assert frame["seed"][0] == 0
    assert frame["winner"][0] in ("MONKEY", "WOLF", "NONE")
    assert 0 < frame["turn_count"][0] < 100

    time_taken_s = (frame["end_time"][0] - frame["start_time"][0]).total_seconds()
    assert 0.0 < time_taken_s < 10.0
