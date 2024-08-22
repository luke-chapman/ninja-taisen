import datetime
import logging
import sys
from argparse import ArgumentParser
from logging import getLogger
from pathlib import Path

from ninja_taisen.api import simulate
from ninja_taisen.dtos import InstructionDto
from ninja_taisen.objects.types import ALL_STRATEGY_NAMES

log = getLogger(__name__)


def main(override_args: list[str] | None = None) -> int:

    parser = ArgumentParser()
    parser.add_argument("--games", type=int, default=1, help="Number of games to simulate")
    parser.add_argument("--monkey-strategy", type=str, default="random", choices=ALL_STRATEGY_NAMES)
    parser.add_argument("--wolf-strategy", type=str, default="random", choices=ALL_STRATEGY_NAMES)
    parser.add_argument("--verbosity", action="count", default=logging.INFO, help="Verbosity level for logging")
    parser.add_argument("--profile", action="store_true", help="Profile the code")
    parser.add_argument("--results-file", type=Path, help="Filename to store results in csv format")
    args = parser.parse_args(override_args or sys.argv[1:])

    results_file = args.results_file
    if not results_file:
        timestamp = datetime.datetime.now(datetime.UTC).strftime("%Y%m%d_%H%M%S")
        results_file = Path.cwd() / ".ninja-taisen" / f"results_{timestamp}.csv"

    instructions = [
        InstructionDto(id=index, seed=index, monkey_strategy=args.monkey_strategy, wolf_strategy=args.wolf_strategy)
        for index in range(args.games)
    ]

    results = simulate(
        instructions=instructions, csv_results=results_file, verbosity=args.verbosity, profile=args.profile
    )
    assert len(results) == len(instructions)
    log.info(f"Successfully simulated {len(results)} games")

    return 0


if __name__ == "__main__":
    sys.exit(main())
