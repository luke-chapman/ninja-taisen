from itertools import product
from pathlib import Path

import polars as pl
from polars.testing import assert_frame_equal

from ninja_taisen import InstructionDto, simulate
from ninja_taisen.dtos import ResultsFormat
from ninja_taisen.objects.types import ALL_STRATEGY_NAMES


def __run_test_all_strategies(max_processes: int, results_format: ResultsFormat, regen: bool, tmp_path: Path) -> None:
    instructions: list[InstructionDto] = []
    for index, (monkey_strategy, wolf_strategy) in enumerate(product(ALL_STRATEGY_NAMES, ALL_STRATEGY_NAMES)):
        instructions.append(
            InstructionDto(id=index, seed=index, monkey_strategy=monkey_strategy, wolf_strategy=wolf_strategy)
        )

    simulate(
        instructions=instructions,
        results_dir=tmp_path,
        results_format=results_format,
        max_processes=max_processes,
        per_process=5,
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


def test_all_strategies_2_parquet(regen: bool, tmp_path: Path) -> None:
    __run_test_all_strategies(max_processes=2, results_format="parquet", regen=regen, tmp_path=tmp_path)


def test_all_strategies_minus2_parquet(regen: bool, tmp_path: Path) -> None:
    if not regen:
        __run_test_all_strategies(max_processes=-2, results_format="parquet", regen=regen, tmp_path=tmp_path)


def test_all_strategies_2_csv(regen: bool, tmp_path: Path) -> None:
    if not regen:
        __run_test_all_strategies(max_processes=2, results_format="csv", regen=regen, tmp_path=tmp_path)


def test_all_strategies_minus2_csv(regen: bool, tmp_path: Path) -> None:
    if not regen:
        __run_test_all_strategies(max_processes=-2, results_format="csv", regen=regen, tmp_path=tmp_path)
