from pathlib import Path

import polars as pl
from polars.testing import assert_frame_equal

from ninja_taisen import InstructionDto, simulate
from ninja_taisen.dtos import Strategy


def test_next_turn_prototype_vs_random(regen: bool, tmp_path: Path) -> None:
    instructions = [
        InstructionDto(id=0, seed=0, monkey_strategy=Strategy.next_turn_prototype, wolf_strategy=Strategy.random)
    ]
    simulate(
        instructions=instructions,
        results_dir=tmp_path,
        max_processes=1,
        per_process=5,
    )

    df_lazy = pl.scan_parquet(tmp_path / "results.parquet")
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
