import logging
import os
from cProfile import Profile
from logging import basicConfig, getLogger
from pathlib import Path
from pstats import SortKey

import polars as pl

from ninja_taisen.game.game_runner import simulate_many_multi_threads
from ninja_taisen.public_types import Instruction, Result

log = getLogger(__name__)


def simulate(
    instructions: list[Instruction],
    max_threads: int = 1,
    per_thread: int = 100,
    results_file: Path | None = None,
    verbosity: int = logging.INFO,
    profile: bool = False,
) -> list[Result]:
    basicConfig(level=verbosity)
    if max_threads <= 0:
        cpu_count = os.cpu_count()
        if cpu_count is None:
            raise OSError("Unable to deduce CPU count from os.cpu_count(). Please manually specify max_threads >= 1")
        log.info(f"User provided max_threads={max_threads}; os.cpu_count()={cpu_count}")
        max_threads = max(cpu_count + max_threads, 1)
        log.info(f"Set max_threads=max(cpu_count + max_threads), 1)={max_threads}")

    if profile:
        with Profile() as profiler:
            results = simulate_many_multi_threads(
                instructions=instructions, max_threads=max_threads, per_thread=per_thread
            )
        profiler.print_stats(SortKey.TIME)
    else:
        results = simulate_many_multi_threads(instructions=instructions, max_threads=max_threads, per_thread=per_thread)

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
