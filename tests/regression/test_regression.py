import itertools
import os
from pathlib import Path

import polars as pl
import pytest
from polars.testing import assert_frame_equal

from ninja_taisen import Instruction, simulate
from ninja_taisen.api import make_data_frame
from ninja_taisen.strategy.strategy_names import StrategyNames


def __run_regression_test(regen: bool, max_threads: int) -> None:
    expected = Path(__file__).resolve().parent / "expected_results.csv"

    instructions: list[Instruction] = []
    for index, (monkey_strategy, wolf_strategy) in enumerate(itertools.product(StrategyNames.ALL, StrategyNames.ALL)):
        instructions.append(Instruction(index, index, monkey_strategy, wolf_strategy))

    results = simulate(instructions=instructions, max_threads=max_threads, per_thread=5)
    assert len(results) == len(instructions)
    recovered_instructions = [Instruction(r.id, r.seed, r.monkey_strategy, r.wolf_strategy) for r in results]
    assert instructions == recovered_instructions

    df_actual = make_data_frame(results).drop(["start_time", "end_time", "thread_name"])
    if regen:
        df_actual.write_csv(expected)
    else:
        df_expected = pl.read_csv(expected)
        assert_frame_equal(df_expected, df_actual)


def test_regression(regen: bool) -> None:
    __run_regression_test(regen=regen, max_threads=1)


@pytest.mark.parametrize("max_threads", range(2, os.cpu_count() or 2))
def test_regression_multi_threaded(max_threads: int) -> None:
    __run_regression_test(regen=False, max_threads=max_threads)
