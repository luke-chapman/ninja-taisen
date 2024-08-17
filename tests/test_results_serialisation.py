import datetime
from pathlib import Path

from polars.testing import assert_frame_equal

from ninja_taisen import Result
from ninja_taisen.api import make_data_frame, read_results_csv, write_results_csv
from ninja_taisen.objects.card import Team
from ninja_taisen.strategy.strategy_names import StrategyNames


def test_csv_round_trip(tmp_path: Path) -> None:
    now = datetime.datetime.now(datetime.UTC)

    results = [
        Result(
            monkey_strategy=StrategyNames.random,
            wolf_strategy=StrategyNames.metric_count,
            seed=5,
            winner=str(Team.MONKEY),
            turn_count=18,
            start_time=now,
            end_time=now + datetime.timedelta(milliseconds=100),
        ),
        Result(
            monkey_strategy=StrategyNames.random_spot_win,
            wolf_strategy=StrategyNames.metric_position,
            seed=55,
            winner=str(Team.WOLF),
            turn_count=22,
            start_time=datetime.datetime.now(datetime.UTC) + datetime.timedelta(milliseconds=110),
            end_time=datetime.datetime.now(datetime.UTC) + datetime.timedelta(milliseconds=211),
        ),
    ]

    filename = tmp_path / "results.csv"
    write_results_csv(results, filename)
    assert filename.is_file()

    original_frame = make_data_frame(results)
    recovered_frame = read_results_csv(filename)

    assert_frame_equal(original_frame, recovered_frame)
