import datetime
import sys
from argparse import ArgumentParser
from logging import basicConfig, getLogger
from pathlib import Path

from ninja_taisen import Instruction, Options, simulate
from ninja_taisen.strategy.strategy_names import StrategyNames

log = getLogger(__name__)


def main(override_args: list[str] | None = None) -> int:

    parser = ArgumentParser()
    parser.add_argument("--games", type=int, default=1, help="Number of games to simulate")
    parser.add_argument("--monkey-strategy", type=str, default="random", choices=StrategyNames.ALL)
    parser.add_argument("--wolf-strategy", type=str, default="random", choices=StrategyNames.ALL)
    parser.add_argument("--verbosity", action="count", default=0, help="Verbosity level for logging")
    parser.add_argument("--profile", action="store_true", help="Profile the code")
    parser.add_argument("--results-file", type=Path, help="Filename to store results in csv format")
    args = parser.parse_args(override_args or sys.argv[1:])

    results_file = args.results_file
    if not results_file:
        timestamp = datetime.datetime.now(datetime.UTC).strftime("%Y%m%d_%H%M%S")
        results_file = Path.cwd() / ".ninja-taisen" / f"results_{timestamp}.csv"

    instructions = [
        Instruction(monkey_strategy=args.monkey_strategy, wolf_strategy=args.wolf_strategy, seed=seed)
        for seed in range(args.games)
    ]
    options = Options(verbosity=args.verbosity, profile=args.profile, results_file=results_file)

    basicConfig(level=args.verbosity)
    log.info(options)

    results = simulate(instructions, options)
    assert len(results) == len(instructions)
    print(f"Successfully simulated {len(results)} games")
    return 0


if __name__ == "__main__":
    sys.exit(main())
