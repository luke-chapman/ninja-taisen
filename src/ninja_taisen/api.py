from cProfile import Profile
from logging import basicConfig, getLogger
from pathlib import Path
from pstats import SortKey

import polars as pl

from ninja_taisen.game.game_runner import simulate_all
from ninja_taisen.public_types import Instruction, Result

log = getLogger(__name__)


def simulate(
    instructions: list[Instruction], results_file: Path | None = None, verbosity: int = 0, profile: bool = False
) -> list[Result]:
    basicConfig(level=verbosity)

    if profile:
        with Profile() as profiler:
            results = simulate_all(instructions)
        profiler.print_stats(SortKey.TIME)
    else:
        results = simulate_all(instructions)

    if results_file:
        results_file.parent.mkdir(parents=True, exist_ok=True)
        write_results_csv(results, results_file)
        log.info(f"Results written to {results_file}")

    return results


def make_data_frame(results: list[Result]) -> pl.DataFrame:
    return pl.DataFrame(data=results, schema=Result._fields, orient="row")


def write_results_csv(results: list[Result], filename: Path) -> None:
    df = make_data_frame(results)
    df.write_csv(filename)


def read_results_csv(filename: Path) -> pl.DataFrame:
    return pl.read_csv(filename, schema_overrides={"start_time": pl.Datetime, "end_time": pl.Datetime})
