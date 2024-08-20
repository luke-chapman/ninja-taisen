import datetime
import itertools
import logging
from logging import getLogger
from pathlib import Path
from time import perf_counter

from ninja_taisen import InstructionDto, simulate
from ninja_taisen.strategy.strategy_names import StrategyNames

log = getLogger(__name__)


def run() -> None:
    start = perf_counter()

    timestamp = datetime.datetime.now(datetime.UTC).strftime("%Y%m%d_%H%M%S")
    results_dir = Path(__file__).resolve().parent / f".ninja-taisen-{timestamp}"
    results_dir.mkdir()
    results_file = results_dir / "results.parquet"

    instructions: list[InstructionDto] = []
    enumeration = enumerate(itertools.product([StrategyNames.metric_count], [StrategyNames.random_spot_win], range(1)))
    for index, (monkey_strategy, wolf_strategy, seed) in enumeration:
        instruction = InstructionDto(id=index, seed=seed, monkey_strategy=monkey_strategy, wolf_strategy=wolf_strategy)
        instructions.append(instruction)

    log.info(f"Will simulate {len(instructions)} games")
    simulate(
        instructions=instructions,
        max_processes=1,
        parquet_results=results_file,
        verbosity=logging.INFO,
        log_file=results_dir / "log.txt",
        profile=True,
    )

    stop = perf_counter()
    log.info(f"Took {stop - start:.2f} seconds")


if __name__ == "__main__":
    run()
