import itertools
from pathlib import Path

import polars as pl
import pytest
from polars.testing import assert_frame_equal

from ninja_taisen import InstructionDto, simulate
from ninja_taisen.api import make_data_frame
from ninja_taisen.objects.types import ALL_STRATEGY_NAMES


@pytest.mark.parametrize("max_processes", (-1, 2))
def test_all_strategies(max_processes: int, regen: bool) -> None:
    if regen and max_processes != -1:
        # We only regenerate the output on the all-but-one-thread variant of this test
        return

    instructions: list[InstructionDto] = []
    for index, (monkey_strategy, wolf_strategy) in enumerate(itertools.product(ALL_STRATEGY_NAMES, ALL_STRATEGY_NAMES)):
        instructions.append(
            InstructionDto(id=index, seed=index, monkey_strategy=monkey_strategy, wolf_strategy=wolf_strategy)
        )

    results = simulate(instructions=instructions, max_processes=max_processes, per_process=5)
    assert len(results) == len(instructions)
    recovered_instructions = [
        InstructionDto(id=r.id, seed=r.seed, monkey_strategy=r.monkey_strategy, wolf_strategy=r.wolf_strategy)
        for r in results
    ]
    assert instructions == recovered_instructions

    df_actual = make_data_frame(results).drop(["start_time", "end_time", "process_name"])
    results_csv = Path(__file__).resolve().parent / "results.csv"
    if regen:
        df_actual.write_csv(results_csv)
    else:
        df_expected = pl.read_csv(results_csv)
        assert_frame_equal(df_expected, df_actual)
