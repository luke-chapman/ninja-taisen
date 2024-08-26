from pathlib import Path
from shutil import copytree, rmtree

import pytest

from ninja_taisen import InstructionDto, simulate
from ninja_taisen.api import make_data_frame
from ninja_taisen.objects.types import ALL_STRATEGY_NAMES


@pytest.mark.parametrize("monkey_strategy", ALL_STRATEGY_NAMES)
@pytest.mark.parametrize("wolf_strategy", ALL_STRATEGY_NAMES)
def test_strategy_combination(monkey_strategy: str, wolf_strategy: str, tmp_path: Path, regen: bool) -> None:
    results = simulate(
        [InstructionDto(id=0, seed=0, monkey_strategy=monkey_strategy, wolf_strategy=wolf_strategy)],
        serialisation_dir=tmp_path,
    )

    assert len(results) == 1
    result = results[0]
    assert result.id == 0
    assert result.seed == 0
    assert result.monkey_strategy == monkey_strategy
    assert result.wolf_strategy == wolf_strategy
    assert result.winner in ("monkey", "wolf", "none")
    assert 0 < result.turn_count < 100
    time_taken_s = (result.end_time - result.start_time).total_seconds()
    assert 0.0 < time_taken_s < 10.0
    assert result.process_name

    frame = make_data_frame(results).drop(["start_time", "end_time", "process_name"])
    frame.write_csv(tmp_path / "results.csv")

    results_dir = Path(__file__).resolve().parent / f"{monkey_strategy}_vs_{wolf_strategy}"
    results_dir.mkdir(exist_ok=True)
    if regen:
        rmtree(results_dir)
        copytree(tmp_path, results_dir)
        return

    actual_filenames = sorted(f.name for f in tmp_path.iterdir())
    expected_filenames = sorted(f.name for f in results_dir.iterdir())
    assert actual_filenames == expected_filenames

    different_files: list[str] = []
    for filename in actual_filenames:
        actual_contents = (tmp_path / filename).read_text()
        expected_contents = (results_dir / filename).read_text()
        if actual_contents != expected_contents:
            different_files.append(filename)

    assert not different_files, f"{len(different_files)} were different: {different_files}"
