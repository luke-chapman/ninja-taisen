import sys
from argparse import ArgumentParser
from cProfile import Profile
from logging import basicConfig, getLogger
from pathlib import Path
from pstats import SortKey
from random import seed

from ninja_taisen.game.game_results import GameResults
from ninja_taisen.game.game_runner import GameRunner
from ninja_taisen.objects.card import Team
from ninja_taisen.strategy.strategy import IStrategy
from ninja_taisen.strategy.strategy_lookup import lookup_strategy
from ninja_taisen.strategy.strategy_names import StrategyNames

log = getLogger(__name__)


def run(games: int, monkey_strategy: IStrategy, wolf_strategy: IStrategy, results_dir: Path, prefix: str) -> None:
    all_results = GameResults(results_dir, prefix)
    starting_team = Team.MONKEY

    for i in range(games):
        log.info(f"Beginning game with seed {i}")
        seed(i)

        game_runner = GameRunner(
            monkey_strategy=monkey_strategy,
            wolf_strategy=wolf_strategy,
            starting_team=starting_team,
        )

        game_result = game_runner.play()
        all_results.register_result(game_result)
        starting_team = starting_team.other()

    all_results.print_stats()


def main(override_args: list[str] | None = None) -> int:

    parser = ArgumentParser()
    parser.add_argument("--games", type=int, default=1, help="Number of games to simulate")
    parser.add_argument("--monkey-strategy", type=str, default="random", choices=StrategyNames.ALL)
    parser.add_argument("--wolf-strategy", type=str, default="random", choices=StrategyNames.ALL)
    parser.add_argument("--verbosity", action="count", default=0, help="Verbosity level for logging")
    parser.add_argument("--profile", action="store_true", help="Profile the code")
    parser.add_argument("--results-dir", type=Path, help="Directory in which to store results")
    parser.add_argument("--results-prefix", help="Prefix to prepend to results files")
    args = parser.parse_args(override_args or sys.argv[1:])

    basicConfig(level=args.verbosity)
    results_dir = args.results_dir or Path.cwd() / ".ninja-taisen"
    results_dir.mkdir(parents=True, exist_ok=True)
    monkey_strategy = lookup_strategy(args.monkey_strategy)
    wolf_strategy = lookup_strategy(args.wolf_strategy)

    if args.profile:
        with Profile() as profile:
            run(args.games, monkey_strategy, wolf_strategy, results_dir, args.results_prefix or "")
        profile.print_stats(SortKey.TIME)
    else:
        run(args.games, monkey_strategy, wolf_strategy, results_dir, args.results_prefix or "")

    return 0


if __name__ == "__main__":
    sys.exit(main())
