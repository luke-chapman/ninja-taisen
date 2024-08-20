import itertools
import os
from pathlib import Path

import polars as pl
import pytest
from polars.testing import assert_frame_equal

from ninja_taisen import InstructionDto, simulate
from ninja_taisen.api import make_data_frame
from ninja_taisen.strategy.strategy_names import StrategyNames


def __run_simulation_regression_test(regen: bool, max_processes: int) -> None:
    expected = Path(__file__).resolve().parent / "expected_results.csv"

    instructions: list[InstructionDto] = []
    for index, (monkey_strategy, wolf_strategy) in enumerate(itertools.product(StrategyNames.ALL, StrategyNames.ALL)):
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
    if regen:
        df_actual.write_csv(expected)
    else:
        df_expected = pl.read_csv(expected)
        assert_frame_equal(df_expected, df_actual)


def test_single_process(regen: bool) -> None:
    __run_simulation_regression_test(regen=regen, max_processes=1)


@pytest.mark.parametrize("max_processes", range(2, os.cpu_count() or 2))
def test_multi_process(max_processes: int) -> None:
    __run_simulation_regression_test(regen=False, max_processes=max_processes)
