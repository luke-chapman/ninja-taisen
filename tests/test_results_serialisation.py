import datetime
from pathlib import Path

import pytest
from polars.testing import assert_frame_equal

from ninja_taisen import Result
from ninja_taisen.api import (
    read_csv_results,
    read_parquet_results,
    write_csv_results,
    write_parquet_results,
)
from ninja_taisen.objects.card import Team
from ninja_taisen.strategy.strategy_names import StrategyNames


@pytest.mark.parametrize("file_format", ["csv", "parquet"])
def test_csv_round_trip(file_format: str, tmp_path: Path) -> None:
    now = datetime.datetime.now(datetime.UTC)

    results = [
        Result(
            id=0,
            seed=5,
            monkey_strategy=StrategyNames.random,
            wolf_strategy=StrategyNames.metric_count,
            winner=str(Team.MONKEY),
            turn_count=18,
            start_time=now,
            end_time=now + datetime.timedelta(milliseconds=100),
            process_name="process-1",
        ),
        Result(
            id=1,
            seed=55,
            monkey_strategy=StrategyNames.random_spot_win,
            wolf_strategy=StrategyNames.metric_position,
            winner=str(Team.WOLF),
            turn_count=22,
            start_time=datetime.datetime.now(datetime.UTC) + datetime.timedelta(milliseconds=110),
            end_time=datetime.datetime.now(datetime.UTC) + datetime.timedelta(milliseconds=211),
            process_name="process-2",
        ),
    ]

    if file_format == "csv":
        csv_filename = tmp_path / "results.csv"
        write_csv_results(results, csv_filename)
        assert csv_filename.is_file()
        recovered_frame = read_csv_results(csv_filename)
    elif file_format == "parquet":
        parquet_filename = tmp_path / "results.parquet"
        write_parquet_results(results, parquet_filename)
        assert parquet_filename.is_file()
        recovered_frame = read_parquet_results(parquet_filename)
    else:
        raise ValueError(f"Unsupported file format: {file_format}")

    assert_frame_equal(recovered_frame, recovered_frame)
