import random
from cProfile import Profile
from logging import basicConfig
from pstats import SortKey

import polars as pl

from ninja_taisen.game.game_runner import simulate_one
from ninja_taisen.public_types import Instruction, Options, Result
from ninja_taisen.strategy.strategy_lookup import lookup_strategy


def simulate(instructions: list[Instruction], options: Options) -> list[Result]:
    basicConfig(level=options.verbosity)
    options.results_file.parent.mkdir(parents=True, exist_ok=True)

    results: list[Result] = []
    for instruction in instructions:
        random.seed(instruction.seed)
        monkey_strategy = lookup_strategy(instruction.monkey_strategy)
        wolf_strategy = lookup_strategy(instruction.wolf_strategy)

        if options.profile:
            with Profile() as profile:
                result = simulate_one(monkey_strategy, wolf_strategy, instruction)
            profile.print_stats(SortKey.TIME)
        else:
            result = simulate_one(monkey_strategy, wolf_strategy, instruction)
        results.append(result)

    df = pl.DataFrame(data=results, schema=Result._fields, orient="row")
    df.write_csv(options.results_file)

    return results
