import logging
import multiprocessing
from cProfile import Profile
from logging import getLogger
from pathlib import Path
from pstats import SortKey

import polars as pl

from ninja_taisen.game.game_runner import simulate_many_multi_process
from ninja_taisen.logging_setup import setup_logging
from ninja_taisen.public_types import Instruction, Result

log = getLogger(__name__)


def simulate(
    instructions: list[Instruction],
    max_processes: int = 1,
    per_process: int = 100,
    results_file: Path | None = None,
    verbosity: int = logging.INFO,
    log_file: Path | None = None,
    profile: bool = False,
) -> list[Result]:
    setup_logging(verbosity, log_file)

    if max_processes <= 0:
        cpu_count = multiprocessing.cpu_count()
        if cpu_count is None:
            raise OSError("Unable to deduce CPU count from os.cpu_count(). Please manually specify max_processes >= 1")
        log.info(f"User provided max_processes={max_processes}; found cpu_count={cpu_count}")
        max_processes = max(cpu_count + max_processes, 1)
        log.info(f"Will use max_processes={max_processes}")

    if profile:
        with Profile() as profiler:
            results = simulate_many_multi_process(
                instructions=instructions,
                max_processes=max_processes,
                per_process=per_process,
                log_file=log_file,
            )
        profiler.print_stats(SortKey.TIME)
    else:
        results = simulate_many_multi_process(
            instructions=instructions,
            max_processes=max_processes,
            per_process=per_process,
            log_file=log_file,
        )

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
