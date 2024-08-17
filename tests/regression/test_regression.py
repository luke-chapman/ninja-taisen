from pathlib import Path

import polars as pl
from ninja_taisen import Instruction, Options, simulate
from ninja_taisen.api import make_data_frame
from ninja_taisen.strategy.strategy_names import StrategyNames
from polars.testing import assert_frame_equal


def test_regression(regen: bool) -> None:
    expected = Path(__file__).resolve().parent / "expected_results.csv"

    instructions: list[Instruction] = []
    seed = 0
    for monkey_strategy in StrategyNames.ALL:
        for wolf_strategy in StrategyNames.ALL:
            instructions.append(Instruction(monkey_strategy, wolf_strategy, seed))
            seed += 1

    results = simulate(instructions, Options())
    assert len(results) == len(instructions)

    df_actual = make_data_frame(results).drop(["start_time", "end_time"])
    if regen:
        df_actual.write_csv(expected)
    else:
        df_expected = pl.read_csv(expected)
        assert_frame_equal(df_expected, df_actual)
