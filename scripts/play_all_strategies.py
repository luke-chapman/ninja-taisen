import datetime
import itertools
from pathlib import Path

from ninja_taisen import Instruction, Options, simulate
from ninja_taisen.strategy.strategy_names import StrategyNames


def run() -> None:
    timestamp = datetime.datetime.now(datetime.UTC).strftime("%Y%m%d_%H%M%S")
    results_file = Path(__file__).resolve().parent / f"play_all_strategies_{timestamp}.csv"
    options = Options(results_file)
    instructions = [Instruction(*t) for t in itertools.product(StrategyNames.ALL, StrategyNames.ALL, range(5))]
    print(f"Will simulate {len(instructions)} games")
    simulate(instructions=instructions, options=options)


if __name__ == "__main__":
    run()
