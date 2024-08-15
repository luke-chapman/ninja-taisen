from argparse import ArgumentParser
from cProfile import Profile
from logging import basicConfig, getLogger
from pstats import SortKey  # type: ignore
from random import seed
from time import perf_counter

from ninja_taisen.game.game_results import GameResults
from ninja_taisen.game.game_runner import GameRunner
from ninja_taisen.objects.card import Team
from ninja_taisen.strategy.strategy import IStrategy
from ninja_taisen.strategy.strategy_lookup import lookup_strategy

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
    parser.add_argument("-g", "--games", type=int, default=1, dest="games")
    parser.add_argument("-ms", "--monkey-strategy", type=str, default="random", dest="monkey_strategy")
    parser.add_argument("-ws", "--wolf-strategy", type=str, default="random", dest="wolf_strategy")
    parser.add_argument("-v", "--verbose", action="count", default=0, dest="verbosity")
    parser.add_argument("-p", "--profile", action="store_true", default=False, dest="profile")
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
