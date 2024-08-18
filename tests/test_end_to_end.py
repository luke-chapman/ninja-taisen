from pathlib import Path

import pytest

from ninja_taisen import Instruction, simulate
from ninja_taisen.__main__ import main
from ninja_taisen.api import make_data_frame, read_results_csv
from ninja_taisen.strategy.strategy_names import StrategyNames


def __launch_and_assert_game(monkey_strategy: str, wolf_strategy: str, invocation: str, tmp_path: Path) -> None:
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
        frame = read_results_csv(results_file)
    elif invocation == "library_api":
        results = simulate([Instruction(monkey_strategy, wolf_strategy, 0)], results_file=results_file)
        frame = make_data_frame(results)
    else:
        raise ValueError(f"Unexpected invocation {invocation}")

    assert frame.columns == [
        "monkey_strategy",
        "wolf_strategy",
        "seed",
        "winner",
        "turn_count",
        "start_time",
        "end_time",
        "thread_name",
    ]
    assert frame["monkey_strategy"][0] == monkey_strategy
    assert frame["wolf_strategy"][0] == wolf_strategy
    assert frame["seed"][0] == 0
    assert frame["winner"][0] in ("MONKEY", "WOLF", "NONE")
    assert 0 < frame["turn_count"][0] < 100

    time_taken_s = (frame["end_time"][0] - frame["start_time"][0]).total_seconds()
    assert 0.0 < time_taken_s < 10.0
    assert frame["thread_name"][0]


@pytest.mark.parametrize("monkey_strategy", StrategyNames.ALL)
@pytest.mark.parametrize("wolf_strategy", StrategyNames.ALL)
def test_strategy_combination(monkey_strategy: str, wolf_strategy: str, tmp_path: Path) -> None:
    __launch_and_assert_game(
        monkey_strategy=monkey_strategy, wolf_strategy=wolf_strategy, invocation="library_api", tmp_path=tmp_path
    )


# We only test one strategy-pair from the command line because launching a subprocess is slow
def test_from_command_line(tmp_path: Path) -> None:
    __launch_and_assert_game(
        monkey_strategy=StrategyNames.random_spot_win,
        wolf_strategy=StrategyNames.metric_position_strength,
        invocation="command_line",
        tmp_path=tmp_path,
    )
