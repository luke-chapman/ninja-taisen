import sys
from argparse import ArgumentParser
from logging import getLogger
from pathlib import Path
from subprocess import list2cmdline
from time import perf_counter, time

import polars as pl

# TODO 2024-11-13 - work out why the import of ninja_taisen fails. Maturin docs are confusing!
try:
    import ninja_taisen  # noqa
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ninja_taisen import InstructionDto, simulate
from ninja_taisen.dtos import Strategy
from ninja_taisen.objects.constants import DEFAULT_LOGGING
from ninja_taisen.utils.logging_setup import setup_logging
from ninja_taisen.utils.run_directory import choose_run_directory, timestamp

log = getLogger(__name__)


def run() -> None:
    parser = ArgumentParser()
    parser.add_argument(
        "--monkey",
        choices=list(Strategy),
        default=Strategy.metric_strength,
        help="Strategy for the monkey team. Monkey plays first",
    )
    parser.add_argument(
        "--wolf",
        choices=list(Strategy),
        default=Strategy.random,
        help="Strategy for the wolf team. Wolf plays first",
    )
    parser.add_argument(
        "--seed-offset", type=int, default=int(time()), help="Optional seed offset for deterministic results"
    )
    parser.add_argument("--multiplier", default=1, type=int, help="How many times to play the game")
    parser.add_argument(
        "--run-dir", default=choose_run_directory(), type=Path, help="Directory with results, logs and analysis"
    )

    args = parser.parse_args()
    run_dir = args.run_dir.resolve()
    run_dir.mkdir(parents=True, exist_ok=True)
    log_file = run_dir / f"log_{timestamp()}.txt"

    setup_logging(DEFAULT_LOGGING, log_file)
    log.info("Command line\n" + list2cmdline(sys.orig_argv))
    log.info(f"Using run_dir={run_dir}")

    instructions = [
        InstructionDto(id=i, seed=args.seed_offset + i, monkey_strategy=args.monkey, wolf_strategy=args.wolf)
        for i in range(args.multiplier)
    ]
    start = perf_counter()
    simulate(
        instructions=instructions,
        results_dir=run_dir,
        results_format="csv",
        log_file=log_file,
        max_processes=1,
    )
    stop = perf_counter()
    log.info(f"Game simulation took {stop - start:.2f}s")

    results_csv = run_dir / "results.csv"
    results = pl.read_csv(results_csv, schema_overrides={"start_time": pl.Datetime, "end_time": pl.Datetime})
    assert results.shape[0] == args.multiplier

    columns = (
        "id",
        "seed",
        "monkey_strategy",
        "wolf_strategy",
        "winner",
        "turn_count",
        "monkey_cards_left",
        "wolf_cards_left",
    )
    max_length = max(len(c) for c in columns)
    for r in range(results.shape[0]):
        log.info("")
        log.info(f"Result {r} of {results.shape[0]}:")
        for column in columns:
            value = results[column][r]
            log.info(f"{column.ljust(max_length)} - {value}")

    log.info("game complete")


if __name__ == "__main__":
    run()
