from cProfile import Profile
from logging import basicConfig
import random
from pstats import SortKey

from ninja_taisen import GameInstruction, GameOptions, GameResult
from ninja_taisen.strategy.strategy_lookup import lookup_strategy


def simulate(instructions: list[GameInstruction], options: GameOptions) -> list[GameResult]:
    basicConfig(level=options.verbosity)
    options.results_file.parent.mkdir(parents=True, exist_ok=True)

    results: list[GameResult] = []
    for instruction in instructions:
        random.seed(instruction.seed)
        monkey_strategy = lookup_strategy(instruction.monkey_strategy)
        wolf_strategy = lookup_strategy(instruction.wolf_strategy)

        if options.profile:
            with Profile() as profile:
                simulate_one(monkey_strategy, wolf_strategy)
            profile.print_stats(SortKey.TIME)
        else:
            simulate_one(monkey_strategy, wolf_strategy)

    return results
