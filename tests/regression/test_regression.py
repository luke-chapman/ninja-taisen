from pathlib import Path
from shutil import copyfile

from ninja_taisen import Instruction, Options, simulate
from ninja_taisen.api import read_results_csv
from ninja_taisen.strategy.strategy_names import StrategyNames
from polars.testing import assert_frame_equal


def test_regression(tmp_path: Path) -> None:
    expected = Path(__file__).resolve().parent / "expected_results.csv"

    instructions: list[Instruction] = []
    seed = 0
    for monkey_strategy in StrategyNames.ALL:
        for wolf_strategy in StrategyNames.ALL:
            instructions.append(Instruction(monkey_strategy, wolf_strategy, seed))
            seed += 1

    results_file = tmp_path / "results.csv"
    results = simulate(instructions, Options(results_file=results_file))
    assert len(results) == len(instructions)

    regen = True
    if regen:
        copyfile(results_file, expected)
    else:
        df_expected = read_results_csv(expected)
        df_actual = read_results_csv(results_file)
        assert_frame_equal(df_expected, df_actual)
