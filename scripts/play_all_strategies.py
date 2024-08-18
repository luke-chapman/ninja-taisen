import datetime
import itertools
import logging
from logging import getLogger
from pathlib import Path
from time import perf_counter

from ninja_taisen import Instruction, simulate
from ninja_taisen.strategy.strategy_names import StrategyNames

log = getLogger(__name__)


def run() -> None:
    start = perf_counter()

    timestamp = datetime.datetime.now(datetime.UTC).strftime("%Y%m%d_%H%M%S")
    results_file = Path(__file__).resolve().parent / f"play_all_strategies_{timestamp}.csv"

    instructions: list[Instruction] = []
    enumeration = enumerate(itertools.product(StrategyNames.ALL, StrategyNames.ALL, range(10)))
    for index, (monkey_strategy, wolf_strategy, seed) in enumeration:
        instruction = Instruction(id=index, seed=seed, monkey_strategy=monkey_strategy, wolf_strategy=wolf_strategy)
        instructions.append(instruction)

    log.info(f"Will simulate {len(instructions)} games")
    simulate(instructions=instructions, max_threads=-2, results_file=results_file, verbosity=logging.INFO)

    stop = perf_counter()
    log.info(f"Took {stop - start:.2f} seconds")


if __name__ == "__main__":
    run()
