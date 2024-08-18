import datetime
import itertools
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
    instructions = [Instruction(*t) for t in itertools.product(StrategyNames.ALL, StrategyNames.ALL, range(5))]
    log.info(f"Will simulate {len(instructions)} games")
    simulate(instructions=instructions, max_threads=2, results_file=results_file)

    stop = perf_counter()
    log.info(f"Took {stop - start:.2f} seconds")


if __name__ == "__main__":
    run()
