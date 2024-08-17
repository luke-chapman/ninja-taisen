from ninja_taisen import Instruction, Options, simulate
from ninja_taisen.strategy.strategy_names import StrategyNames


def test_regression() -> None:
    instructions: list[Instruction] = []
    seed = 0
    for monkey_strategy in StrategyNames.ALL:
        for wolf_strategy in StrategyNames.ALL:
            instructions.append(Instruction(monkey_strategy, wolf_strategy, seed))
            seed += 1

    results = simulate(instructions, Options())
    assert len(results) == len(instructions)
