import datetime
import itertools
import logging
import math
import multiprocessing
from logging import getLogger
from pathlib import Path
from time import perf_counter

from more_itertools import unique_everseen
from pydantic import BaseModel

from ninja_taisen.algos import board_builder, board_context_gatherer, board_inspector
from ninja_taisen.dtos import InstructionDto, ResultDto, TeamDto
from ninja_taisen.logging_setup import setup_logging
from ninja_taisen.objects.safe_random import SafeRandom
from ninja_taisen.strategy.strategy import IStrategy
from ninja_taisen.strategy.strategy_lookup import lookup_strategy

log = getLogger(__name__)


class GameRunner:
    def __init__(
        self, monkey_strategy: IStrategy, wolf_strategy: IStrategy, starting_team: TeamDto, random: SafeRandom
    ) -> None:
        self.board = board_builder.make_board(random=random)
        self.strategies = {TeamDto.monkey: monkey_strategy, TeamDto.wolf: wolf_strategy}
        self.starting_team = starting_team
        self.random = random

    def execute(self, instruction: InstructionDto) -> ResultDto:
        start_time = datetime.datetime.now(datetime.UTC)

        team = self.starting_team
        victorious_team: TeamDto | None = None
        turn_count = 0
        while victorious_team is None and turn_count < 100:
            self.__execute_turn(team)

            victorious_team = board_inspector.victorious_team(self.board)
            team = team.other()
            turn_count += 1

        end_time = datetime.datetime.now(datetime.UTC)
        result = ResultDto(
            id=instruction.id,
            seed=instruction.seed,
            monkey_strategy=instruction.monkey_strategy,
            wolf_strategy=instruction.wolf_strategy,
            winner=str(victorious_team),
            turn_count=turn_count,
            start_time=start_time,
            end_time=end_time,
            process_name=multiprocessing.current_process().name,
        )

        if log.level <= logging.DEBUG:
            to_log = result.model_dump(exclude={"start_time", "end_time"})
            log.debug(to_log)

        return result

    def __execute_turn(self, team: TeamDto) -> None:
        board_contexts = board_context_gatherer.gather_complete_move_contexts(self.board, team, random=self.random)
        unique_boards = list(unique_everseen(context.board for context in board_contexts))
        if unique_boards:
            self.board = self.strategies[team].choose_board(unique_boards, team)


def simulate_one(instruction: InstructionDto) -> ResultDto:
    random = SafeRandom(instruction.seed)

    monkey_strategy = lookup_strategy(instruction.monkey_strategy, random)
    wolf_strategy = lookup_strategy(instruction.wolf_strategy, random)

    game_runner = GameRunner(
        monkey_strategy=monkey_strategy,
        wolf_strategy=wolf_strategy,
        starting_team=TeamDto.monkey,
        random=random,
    )
    return game_runner.execute(instruction)


# We have to put all arguments for the multiprocessing subprocess into a class which can be pickled
class SubprocessArgs(BaseModel):
    instructions: list[InstructionDto]
    log_file: Path | None


def simulate_many_single_thread(args: SubprocessArgs) -> list[ResultDto]:
    setup_logging(verbosity=logging.INFO, log_file=args.log_file)

    suffix = (
        f"block with ids {args.instructions[0].id}-{args.instructions[-1].id} "
        f"in process {multiprocessing.current_process().name}"
    )
    log.info(f"Starting {suffix}")
    start = perf_counter()
    results = [simulate_one(i) for i in args.instructions]
    stop = perf_counter()
    log.info(f"Completed {suffix} in {stop - start:0.1f} seconds")
    return results


def simulate_many_multi_process(
    instructions: list[InstructionDto], max_processes: int, per_process: int, log_file: Path | None
) -> list[ResultDto]:
    if max_processes == 1:
        log.info("Bypassing multiprocessing.Pool because max_processes=1 specified")
        return simulate_many_single_thread(SubprocessArgs(instructions=instructions, log_file=log_file))

    assert max_processes > 0
    assert per_process > 0
    log.info(
        f"Will assign {len(instructions)} instructions in blocks of {per_process} between {max_processes} processes"
    )

    blocks_count = int(math.ceil(len(instructions) / per_process))
    i_blocks = [instructions[i * per_process : (i + 1) * per_process] for i in range(blocks_count)]
    subprocess_args = [SubprocessArgs(instructions=i_block, log_file=log_file) for i_block in i_blocks]

    with multiprocessing.Pool(processes=max_processes) as pool:
        r_blocks = pool.map(simulate_many_single_thread, subprocess_args)
        return list(itertools.chain(*r_blocks))
