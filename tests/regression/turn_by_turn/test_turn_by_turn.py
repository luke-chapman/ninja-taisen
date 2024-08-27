from itertools import product
from pathlib import Path
from shutil import copytree, rmtree

import polars as pl
import pytest

from ninja_taisen import InstructionDto, ResultDto, simulate
from ninja_taisen.objects.types import ALL_STRATEGY_NAMES


@pytest.mark.parametrize("monkey_strategy,wolf_strategy", tuple(product(ALL_STRATEGY_NAMES, ALL_STRATEGY_NAMES)))
def test_strategy_combination(monkey_strategy: str, wolf_strategy: str, tmp_path: Path, regen: bool) -> None:
    results_dir = tmp_path / "results"
    serialisation_dir = tmp_path / "serialisation"

    simulate(
        instructions=[InstructionDto(id=0, seed=0, monkey_strategy=monkey_strategy, wolf_strategy=wolf_strategy)],
        results_dir=results_dir,
        results_format="csv",
        serialisation_dir=serialisation_dir,
    )

    results_df = pl.read_csv(
        results_dir / "results.csv", schema_overrides={"start_time": pl.Datetime, "end_time": pl.Datetime}
    )
    assert results_df.shape == (1, 9)
    result = ResultDto(**dict(zip(results_df.columns, results_df.row(0), strict=False)))

    assert result.id == 0
    assert result.seed == 0
    assert result.monkey_strategy == monkey_strategy
    assert result.wolf_strategy == wolf_strategy
    assert result.winner in ("monkey", "wolf", "none")
    assert 0 < result.turn_count < 100
    time_taken_s = (result.end_time - result.start_time).total_seconds()
    assert 0.0 < time_taken_s < 10.0
    assert result.process_name

    results_df.drop(["start_time", "end_time", "process_name"]).write_csv(serialisation_dir / "results.csv")

    expected_dir = Path(__file__).resolve().parent / f"{monkey_strategy}_vs_{wolf_strategy}"
    expected_dir.mkdir(exist_ok=True)
    if regen:
        rmtree(expected_dir)
        copytree(serialisation_dir, expected_dir)
        return

    actual_filenames = sorted(f.name for f in serialisation_dir.iterdir())
    expected_filenames = sorted(f.name for f in expected_dir.iterdir())
    assert actual_filenames == expected_filenames

    different_files: list[str] = []
    for filename in actual_filenames:
        actual_contents = (serialisation_dir / filename).read_text()
        expected_contents = (expected_dir / filename).read_text()
        if actual_contents != expected_contents:
            different_files.append(filename)

    assert not different_files, f"{len(different_files)} were different: {different_files}"
