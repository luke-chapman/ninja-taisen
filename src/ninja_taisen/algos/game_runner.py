import datetime
import itertools
import logging
import math
import multiprocessing
from logging import getLogger
from pathlib import Path
from time import perf_counter

from pydantic import BaseModel

from ninja_taisen.algos import board_builder, board_inspector, move_gatherer
from ninja_taisen.dtos import DiceRollDto, InstructionDto, MoveRequestBody, MoveResponseBody, ResultDto
from ninja_taisen.logging_setup import setup_logging
from ninja_taisen.objects.safe_random import SafeRandom
from ninja_taisen.objects.types import DTO_BY_TEAM, Category, Move, Team
from ninja_taisen.strategy.strategy import IStrategy
from ninja_taisen.strategy.strategy_lookup import lookup_strategy

log = getLogger(__name__)


class GameRunner:
    def __init__(
        self,
        monkey_strategy: IStrategy,
        wolf_strategy: IStrategy,
        starting_team: Team,
        random: SafeRandom,
        serialisation_dir: Path | None,
    ) -> None:
        self.board = board_builder.make_board(random=random)
        self.strategies = {Team.monkey: monkey_strategy, Team.wolf: wolf_strategy}
        self.starting_team = starting_team
        self.random = random
        self.serialisation_dir = serialisation_dir

    def execute(self, instruction: InstructionDto) -> ResultDto:
        start_time = datetime.datetime.now(datetime.UTC)

        team = self.starting_team
        victorious_team: Team | None = None
        turn_count = 0
        while victorious_team is None and turn_count < 100:
            self.__execute_turn(turn_count, team)

            victorious_team = board_inspector.victorious_team(self.board)
            team = team.other()
            turn_count += 1

        if self.serialisation_dir:
            self.board.to_dto().to_json_file(self.serialisation_dir / "final_board.json")

        end_time = datetime.datetime.now(datetime.UTC)
        result = ResultDto(
            id=instruction.id,
            seed=instruction.seed,
            monkey_strategy=instruction.monkey_strategy,
            wolf_strategy=instruction.wolf_strategy,
            winner=DTO_BY_TEAM[victorious_team].value if victorious_team is not None else "none",
            turn_count=turn_count,
            start_time=start_time,
            end_time=end_time,
            process_name=multiprocessing.current_process().name,
        )

        if log.level <= logging.DEBUG:
            to_log = result.model_dump(exclude={"start_time", "end_time"})
            log.debug(to_log)

        return result

    def __execute_turn(self, turn_index: int, team: Team) -> None:
        dice_rolls = {
            Category.rock: self.random.roll_dice(),
            Category.paper: self.random.roll_dice(),
            Category.scissors: self.random.roll_dice(),
        }

        if self.serialisation_dir:
            self.__serialise_request(turn_index, team, dice_rolls)

        all_permitted_moves = move_gatherer.gather_all_permitted_moves(
            starting_board=self.board, team=team, dice_rolls=dice_rolls
        )
        if all_permitted_moves:
            chosen_moves = self.strategies[team].choose_moves(all_permitted_moves)
            self.board = chosen_moves.board
            if self.serialisation_dir:
                self.__serialise_response(turn_index, chosen_moves.moves)
        elif self.serialisation_dir:
            self.__serialise_response(turn_index, moves=[])

    def __serialise_request(self, turn_index: int, team: Team, dice_rolls: dict[Category, int]) -> None:
        assert self.serialisation_dir is not None

        request = MoveRequestBody(
            board=self.board.to_dto(),
            dice=DiceRollDto(
                rock=dice_rolls[Category.rock],
                paper=dice_rolls[Category.paper],
                scissors=dice_rolls[Category.scissors],
            ),
            team=DTO_BY_TEAM[team],
        )

        request.to_json_file(self.serialisation_dir / f"request_{turn_index}.json")

    def __serialise_response(self, turn_index: int, moves: list[Move]) -> None:
        assert self.serialisation_dir is not None

        move_response_body = MoveResponseBody(moves=[m.to_dto() for m in moves])
        move_response_body.to_json_file(self.serialisation_dir / f"response_{turn_index}.json")


def simulate_one(instruction: InstructionDto, serialisation_dir: Path | None) -> ResultDto:
    random = SafeRandom(instruction.seed)

    monkey_strategy = lookup_strategy(instruction.monkey_strategy, random)
    wolf_strategy = lookup_strategy(instruction.wolf_strategy, random)

    game_runner = GameRunner(
        monkey_strategy=monkey_strategy,
        wolf_strategy=wolf_strategy,
        starting_team=Team.monkey,
        random=random,
        serialisation_dir=serialisation_dir,
    )
    return game_runner.execute(instruction)


# We have to put all arguments for the multiprocessing subprocess into a class which can be pickled
class SubprocessArgs(BaseModel):
    instructions: list[InstructionDto]
    verbosity: int
    log_file: Path | None
    serialisation_dir: Path | None


def simulate_many_single_thread(args: SubprocessArgs) -> list[ResultDto]:
    setup_logging(verbosity=args.verbosity, log_file=args.log_file)

    suffix = (
        f"block with ids {args.instructions[0].id}-{args.instructions[-1].id} "
        f"in process {multiprocessing.current_process().name}"
    )
    log.info(f"Starting {suffix}")
    start = perf_counter()
    results = [simulate_one(i, args.serialisation_dir) for i in args.instructions]
    stop = perf_counter()
    log.info(f"Completed {suffix} in {stop - start:0.1f} seconds")
    return results


def simulate_many_multi_process(
    instructions: list[InstructionDto],
    max_processes: int,
    per_process: int,
    verbosity: int,
    log_file: Path | None,
    serialisation_dir: Path | None,
) -> list[ResultDto]:
    if max_processes == 1:
        log.info("Bypassing multiprocessing.Pool because max_processes=1 specified")
        return simulate_many_single_thread(
            SubprocessArgs(
                instructions=instructions, verbosity=log.level, log_file=log_file, serialisation_dir=serialisation_dir
            )
        )

    assert max_processes > 0
    assert per_process > 0
    log.info(
        f"Will assign {len(instructions)} instructions in blocks of {per_process} between {max_processes} processes"
    )

    blocks_count = int(math.ceil(len(instructions) / per_process))
    i_blocks = [instructions[i * per_process : (i + 1) * per_process] for i in range(blocks_count)]
    subprocess_args = [
        SubprocessArgs(
            instructions=i_block, verbosity=verbosity, log_file=log_file, serialisation_dir=serialisation_dir
        )
        for i_block in i_blocks
    ]

    with multiprocessing.Pool(processes=max_processes) as pool:
        r_blocks = pool.map(simulate_many_single_thread, subprocess_args)
        return list(itertools.chain(*r_blocks))
