import itertools
from pathlib import Path

import polars as pl
import pytest
from polars.testing import assert_frame_equal

from ninja_taisen import InstructionDto, simulate
from ninja_taisen.objects.types import ALL_STRATEGY_NAMES


@pytest.mark.parametrize("max_processes", (-1, 2))
def test_all_strategies(max_processes: int, regen: bool, tmp_path: Path) -> None:
    if regen and max_processes != -1:
        # We only regenerate the output on the all-but-one-thread variant of this test
        return

    instructions: list[InstructionDto] = []
    for index, (monkey_strategy, wolf_strategy) in enumerate(itertools.product(ALL_STRATEGY_NAMES, ALL_STRATEGY_NAMES)):
        instructions.append(
            InstructionDto(id=index, seed=index, monkey_strategy=monkey_strategy, wolf_strategy=wolf_strategy)
        )

    simulate(
        instructions=instructions,
        results_dir=tmp_path,
        results_format="parquet",
        max_processes=max_processes,
        per_process=5,
    )
    df_actual = pl.scan_parquet(tmp_path / "results.parquet").drop(["start_time", "end_time", "process_name"]).collect()

    df_instructions_expected = pl.DataFrame(data=instructions, orient="row")
    df_instructions_actual = df_actual.select("id", "seed", "monkey_strategy", "wolf_strategy")
    assert_frame_equal(df_instructions_expected, df_instructions_actual)

    results_csv = Path(__file__).resolve().parent / "results.csv"
    if regen:
        df_actual.write_csv(results_csv)
    else:
        df_expected = pl.read_csv(results_csv)
        assert_frame_equal(df_expected, df_actual)
