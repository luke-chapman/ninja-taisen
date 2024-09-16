import itertools
import logging
import sys
from argparse import ArgumentParser
from collections import defaultdict
from logging import getLogger
from pathlib import Path
from subprocess import list2cmdline
from time import perf_counter

import matplotlib.pyplot as plt
import polars as pl

from ninja_taisen import InstructionDto, simulate
from ninja_taisen.objects.types import ALL_STRATEGY_NAMES
from ninja_taisen.utils.logging_setup import setup_logging
from ninja_taisen.utils.run_directory import choose_run_directory, timestamp

log = getLogger(__name__)


def run_simulation(strategies: list[str], multiplier: int, run_dir: Path, max_processes: int, log_file: Path) -> None:
    start = perf_counter()

    instructions: list[InstructionDto] = []
    enumeration = enumerate(itertools.product(strategies, strategies, range(multiplier)))
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
        data = defaultdict(list)
        for strategy_b in strategies:
            monkey_row = df_counts.filter(
                pl.col("monkey_strategy") == strategy_a,
                pl.col("wolf_strategy") == strategy_b,
                pl.col("winner") == "monkey",
            )
            assert monkey_row.height == 1
            monkey_proportion = monkey_row["proportion"][0]

            wolf_row = df_counts.filter(
                pl.col("wolf_strategy") == strategy_a,
                pl.col("monkey_strategy") == strategy_b,
                pl.col("winner") == "wolf",
            )
            assert wolf_row.height == 1
            wolf_proportion = wolf_row["proportion"][0]

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
        help="Number of processes to use. Negative values are deducted from available cores on this machine",
    )
    parser.add_argument(
        "--strategies",
        nargs="*",
        choices=ALL_STRATEGY_NAMES,
        default=ALL_STRATEGY_NAMES,
        help="Names of strategies to play against each other",
    )
    parser.add_argument("--multiplier", default=10, help="How many times to play each strategy pair against each other")
    parser.add_argument(
        "--run-dir", default=choose_run_directory(), type=Path, help="Directory with results, logs and analysis"
    )

    args = parser.parse_args()
    run_dir = args.run_dir.resolve()
    run_dir.mkdir(parents=True, exist_ok=True)
    log_file = run_dir / f"log_{timestamp()}.txt"

    setup_logging(logging.INFO, log_file)
    log.info("Command line\n" + list2cmdline(sys.orig_argv))
    log.info(f"Using run_dir={run_dir}")

    results_parquet = run_dir / "results.parquet"
    if results_parquet.exists():
        log.info(f"Skipping simulation because '{results_parquet}' already exists")
    else:
        run_simulation(
            strategies=args.strategies,
            multiplier=args.multiplier,
            run_dir=run_dir,
            max_processes=args.max_processes,
            log_file=log_file,
        )

    run_analysis(strategies=args.strategies, results_parquet=results_parquet)


if __name__ == "__main__":
    run()
