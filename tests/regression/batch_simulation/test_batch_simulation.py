import itertools
from pathlib import Path
from typing import get_args

import polars as pl
import pytest
from polars.testing import assert_frame_equal

from ninja_taisen import InstructionDto, simulate
from ninja_taisen.dtos import ResultsFormat, Strategy


@pytest.mark.parametrize("max_processes", (1, 2, -2))
@pytest.mark.parametrize("results_format", get_args(ResultsFormat))
def test_all_strategies(max_processes: int, results_format: ResultsFormat, regen: bool, tmp_path: Path) -> None:
    if regen and (max_processes != -2 or results_format != "parquet"):
        # We only regenerate the output for one variant of this test
        return

    instructions: list[InstructionDto] = []
    strategies = (Strategy.random, Strategy.random_spot_win, Strategy.metric_count, Strategy.metric_strength)
    for index, (monkey_strategy, wolf_strategy) in enumerate(itertools.product(strategies, strategies)):
        instructions.append(
            InstructionDto(id=index, seed=index, monkey_strategy=monkey_strategy, wolf_strategy=wolf_strategy)
        )

    simulate(
        instructions=instructions,
        results_dir=tmp_path,
        results_format=results_format,
        max_processes=max_processes,
        per_process=5,
        rust=False,
    )

    df_lazy = (
        pl.scan_parquet(tmp_path / "results.parquet")
        if results_format == "parquet"
        else pl.scan_csv(tmp_path / "results.csv")
    )
    df_actual = df_lazy.drop(["start_time", "end_time", "process_name"]).collect()

    df_instructions_expected = pl.DataFrame(data=instructions, orient="row")
    df_instructions_actual = df_actual.select("id", "seed", "monkey_strategy", "wolf_strategy")
    assert_frame_equal(df_instructions_expected, df_instructions_actual)

    results_csv = Path(__file__).resolve().parent / "results.csv"
    if regen:
        df_actual.write_csv(results_csv)
    else:
        df_expected = pl.read_csv(results_csv)
        assert_frame_equal(df_expected, df_actual)
