from argparse import ArgumentParser
from cProfile import Profile
from logging import basicConfig, getLogger
from pstats import SortKey  # type: ignore
from random import seed

from ninja_taisen.game.game_results import GameResults
from ninja_taisen.game.game_runner import GameRunner
from ninja_taisen.objects.card import Team
from ninja_taisen.strategy.strategy import IStrategy
from ninja_taisen.strategy.strategy_lookup import STRATEGIES, lookup_strategy

log = getLogger(__name__)


def run(games: int, monkey_strategy: IStrategy, wolf_strategy: IStrategy) -> None:
    all_results = GameResults()
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


def main() -> None:

    parser = ArgumentParser()
    parser.add_argument("--games", type=int, default=1, help="Number of games to simulate")
    parser.add_argument("--monkey-strategy", type=str, default="random", choices=STRATEGIES)
    parser.add_argument("--wolf-strategy", type=str, default="random", choices=STRATEGIES)
    parser.add_argument("--verbosity", action="count", default=0, help="Verbosity level for logging")
    parser.add_argument("--profile", action="store_true", help="Profile the code")
    options = parser.parse_args()

    monkey_strategy = lookup_strategy(options.monkey_strategy)
    wolf_strategy = lookup_strategy(options.wolf_strategy)

    basicConfig(level=options.verbosity)

    if not options.profile:
        run(options.games, monkey_strategy, wolf_strategy)
        return

    with Profile() as profile:
        run(options.games, monkey_strategy, wolf_strategy)
    profile.print_stats(SortKey.TIME)


if __name__ == "__main__":
    main()
