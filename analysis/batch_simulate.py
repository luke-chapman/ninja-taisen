import itertools
import sys
from argparse import ArgumentParser
from collections import defaultdict
from logging import getLogger
from pathlib import Path
from subprocess import list2cmdline
from time import perf_counter
from typing import Any

import matplotlib.pyplot as plt
import polars as pl

from ninja_taisen import InstructionDto, simulate
from ninja_taisen.objects.constants import DEFAULT_LOGGING
from ninja_taisen.objects.types import ALL_STRATEGY_NAMES
from ninja_taisen.utils.logging_setup import setup_logging
from ninja_taisen.utils.run_directory import choose_run_directory, timestamp

log = getLogger(__name__)


def run_simulation(
    monkey_strategies: list[str],
    wolf_strategies: list[str],
    multiplier: int,
    run_dir: Path,
    max_processes: int,
    log_file: Path,
) -> None:
    start = perf_counter()

    instructions: list[InstructionDto] = []
    enumeration = enumerate(itertools.product(monkey_strategies, wolf_strategies, range(multiplier)))
    for index, (monkey_strategy, wolf_strategy, seed) in enumeration:
        instruction = InstructionDto(id=index, seed=seed, monkey_strategy=monkey_strategy, wolf_strategy=wolf_strategy)
        instructions.append(instruction)

    simulate(
        instructions=instructions,
        results_dir=run_dir,
        results_format="parquet",
        max_processes=max_processes,
        log_file=log_file,
    )

    stop = perf_counter()
    log.info(f"Simulation took {stop - start:.2f} seconds")


def write_png_csv(strategy: str, df: pl.DataFrame, run_dir: Path) -> None:
    df.write_csv(run_dir / f"{strategy}.csv")

    heights = (df["wins_as_monkey"] - df["wins_as_wolf"]).abs()
    bottom = df.select(pl.min_horizontal("wins_as_monkey", "wins_as_wolf")).to_series(0)

    plt.figure(figsize=(8, 6))
    plt.bar(
        x=df["vs"],
        height=heights,
        bottom=bottom,
    )

    plt.ylabel("proportion of games won")
    plt.title(strategy)
    plt.yticks([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    plt.ylim(0, 1)
    plt.grid(axis="y")
    plt.savefig(run_dir / f"{strategy}.png")
    log.info(f"Wrote csv and png for {strategy}")


def get_proportion(df_counts: pl.DataFrame, monkey_strategy: str, wolf_strategy: str, winner: str) -> float:
    rows = df_counts.filter(
        pl.col("monkey_strategy") == monkey_strategy,
        pl.col("wolf_strategy") == wolf_strategy,
        pl.col("winner") == winner,
    )

    if rows.height == 0:
        return 0.0
    elif rows.height == 1:
        return rows["proportion"][0]
    else:
        raise ValueError(
            f"Found {rows.height} rows matching monkey_strategy={monkey_strategy}, "
            f"wolf_strategy={wolf_strategy}, winner={winner}; expected either 0 or 1"
        )


def run_analysis(strategies: list[str], results_parquet: Path) -> None:
    log.info("Beginning analysis...")
    df_counts = (
        pl.scan_parquet(results_parquet)
        .group_by("monkey_strategy", "wolf_strategy")
        .agg(pl.col("winner").value_counts(normalize=True))
        .explode("winner")
        .unnest("winner")
        .with_columns([pl.col("proportion").round(6)])
        .collect()
    )

    for strategy_a in strategies:
        data: defaultdict[str, list[Any]] = defaultdict(list)
        for strategy_b in strategies:
            monkey_proportion = get_proportion(
                df_counts=df_counts, monkey_strategy=strategy_a, wolf_strategy=strategy_b, winner="monkey"
            )
            wolf_proportion = get_proportion(
                df_counts=df_counts, monkey_strategy=strategy_b, wolf_strategy=strategy_a, winner="wolf"
            )

            data["vs"].append(strategy_b)
            data["wins_as_monkey"].append(monkey_proportion)
            data["wins_as_wolf"].append(wolf_proportion)

        df = pl.DataFrame(data=data)
        write_png_csv(strategy=strategy_a, df=df, run_dir=results_parquet.parent)

    log.info("All post analysis complete")


def run() -> None:
    parser = ArgumentParser()
    parser.add_argument(
        "--max-processes",
        default=-1,
        type=int,
        help="Number of processes to use. Negative values are deducted from available cores on this machine",
    )
    parser.add_argument(
        "--monkey-strategies",
        nargs="*",
        choices=ALL_STRATEGY_NAMES,
        default=ALL_STRATEGY_NAMES,
        help="Names of monkey strategies to use (monkey plays first)",
    )
    parser.add_argument(
        "--wolf-strategies",
        nargs="*",
        choices=ALL_STRATEGY_NAMES,
        default=ALL_STRATEGY_NAMES,
        help="Names of wolf strategies to use (wolf plays second)",
    )
    parser.add_argument(
        "--multiplier", default=10, type=int, help="How many times to play each strategy pair against each other"
    )
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

    results_parquet = run_dir / "results.parquet"
    if results_parquet.exists():
        log.info(f"Skipping simulation because '{results_parquet}' already exists")
    else:
        run_simulation(
            monkey_strategies=args.monkey_strategies,
            wolf_strategies=args.wolf_strategies,
            multiplier=args.multiplier,
            run_dir=run_dir,
            max_processes=args.max_processes,
            log_file=log_file,
        )

    run_analysis(strategies=args.strategies, results_parquet=results_parquet)


if __name__ == "__main__":
    run()
