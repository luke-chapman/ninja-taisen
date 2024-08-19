import datetime
import itertools
import logging
from logging import getLogger
from pathlib import Path
from time import perf_counter

from ninja_taisen import Instruction, simulate
from ninja_taisen.api import read_csv_results
from ninja_taisen.strategy.strategy_names import StrategyNames

log = getLogger(__name__)


def run() -> None:
    start = perf_counter()

    timestamp = datetime.datetime.now(datetime.UTC).strftime("%Y%m%d_%H%M%S")
    results_file = Path(__file__).resolve().parent / f"play_all_strategies_{timestamp}.parquet"

    instructions: list[Instruction] = []
    enumeration = enumerate(itertools.product(StrategyNames.ALL, StrategyNames.ALL, range(1000)))
    for index, (monkey_strategy, wolf_strategy, seed) in enumeration:
        instruction = Instruction(id=index, seed=seed, monkey_strategy=monkey_strategy, wolf_strategy=wolf_strategy)
        instructions.append(instruction)

    log.info(f"Will simulate {len(instructions)} games")
    simulate(
        instructions=instructions,
        max_processes=-1,
        parquet_results=results_file,
        verbosity=logging.INFO,
        log_file=Path(__file__).resolve().parent / f"log_{timestamp}.txt",
    )

    stop = perf_counter()
    log.info(f"Took {stop - start:.2f} seconds")


def post_process() -> None:
    directory = Path(__file__).resolve().parent
    csv_file = list(directory.glob("*.csv"))[0]
    results = read_csv_results(csv_file)
    results.write_parquet(csv_file.with_suffix(".parquet"))


if __name__ == "__main__":
    post_process()
