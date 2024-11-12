from pathlib import Path

import polars as pl

from ninja_taisen import InstructionDto, simulate
from ninja_taisen.dtos import ResultDto, Strategy


def test_simulate_rust(tmp_path: Path) -> None:
    i = 0
    instructions = []
    strategies = [Strategy.random, Strategy.random_spot_win, Strategy.metric_count, Strategy.metric_strength]
    for monkey_strategy in strategies:
        for wolf_strategy in strategies:
            for _ in range(4):
                instruction = InstructionDto(id=i, seed=i, monkey_strategy=monkey_strategy, wolf_strategy=wolf_strategy)
                instructions.append(instruction)
                i += 1

    simulate(instructions=instructions, results_dir=tmp_path, max_processes=-1, per_process=3, rust=True)

    results_df = pl.read_parquet(tmp_path / "results.parquet")
    assert results_df.shape == (64, 11)
    for i in range(64):
        result = ResultDto(**dict(zip(results_df.columns, results_df.row(i), strict=False)))

        assert result.id == i
        assert result.seed == i
        assert result.monkey_strategy in strategies
        assert result.wolf_strategy in strategies
        assert result.winner in ("monkey", "wolf", "none")
        assert 0 < result.turn_count < 100
        assert 0 <= result.monkey_cards_left <= 10
        assert 0 <= result.wolf_cards_left <= 10
        time_taken_s = (result.end_time - result.start_time).total_seconds()
        assert 0.0 < time_taken_s < 100.0
        assert result.process_name
