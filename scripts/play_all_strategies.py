import itertools
from logging import getLogger
from time import perf_counter

from ninja_taisen import InstructionDto, simulate
from ninja_taisen.objects.types import ALL_STRATEGY_NAMES
from ninja_taisen.utils.run_directory import setup_run_directory

log = getLogger(__name__)


def run() -> None:
    start = perf_counter()
    run_dir = setup_run_directory()

    instructions: list[InstructionDto] = []
    enumeration = enumerate(itertools.product(ALL_STRATEGY_NAMES, ALL_STRATEGY_NAMES, range(1000)))
    for index, (monkey_strategy, wolf_strategy, seed) in enumeration:
        instruction = InstructionDto(id=index, seed=seed, monkey_strategy=monkey_strategy, wolf_strategy=wolf_strategy)
        instructions.append(instruction)

    simulate(
        instructions=instructions,
        results_dir=run_dir,
        results_format="parquet",
        max_processes=-1,
        log_file=run_dir / "log.txt",
    )

    stop = perf_counter()
    log.info(f"Took {stop - start:.2f} seconds")


if __name__ == "__main__":
    run()
