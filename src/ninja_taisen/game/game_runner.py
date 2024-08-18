import datetime
from concurrent.futures import ThreadPoolExecutor
from logging import getLogger

from more_itertools import unique_everseen

from ninja_taisen.algos import board_builder, board_context_gatherer, board_inspector
from ninja_taisen.objects.card import Team
from ninja_taisen.objects.safe_random import SafeRandom
from ninja_taisen.public_types import Instruction, Result
from ninja_taisen.strategy.strategy import IStrategy
from ninja_taisen.strategy.strategy_lookup import lookup_strategy

log = getLogger(__name__)


class GameRunner:
    def __init__(
        self, monkey_strategy: IStrategy, wolf_strategy: IStrategy, starting_team: Team, random: SafeRandom
    ) -> None:
        self.board = board_builder.make_board(random=SafeRandom(0))
        self.strategies = {Team.MONKEY: monkey_strategy, Team.WOLF: wolf_strategy}
        self.starting_team = starting_team
        self.random = random

    def simulate(self, instruction: Instruction) -> Result:
        start_time = datetime.datetime.now(datetime.UTC)

        team = self.starting_team
        victorious_team: Team | None = None
        turn_count = 0
        while victorious_team is None and turn_count < 100:
            self._execute_turn(team)

            victorious_team = board_inspector.victorious_team(self.board)
            team = team.other()
            turn_count += 1

        end_time = datetime.datetime.now(datetime.UTC)
        time_taken_s = end_time - start_time
        log.info(f"Winner={victorious_team}, turn_count={turn_count}, time_taken={time_taken_s}s")
        return Result(
            monkey_strategy=instruction.monkey_strategy,
            wolf_strategy=instruction.wolf_strategy,
            seed=instruction.seed,
            winner=str(victorious_team),
            turn_count=turn_count,
            start_time=start_time,
            end_time=end_time,
        )

    def _execute_turn(self, team: Team) -> None:
        board_contexts = board_context_gatherer.gather_complete_move_contexts(self.board, team, random=SafeRandom(0))
        unique_boards = list(unique_everseen(context.board for context in board_contexts))
        if unique_boards:
            self.board = self.strategies[team].choose_board(unique_boards, team)


def simulate_one(instruction: Instruction) -> Result:
    random = SafeRandom(instruction.seed)

    monkey_strategy = lookup_strategy(instruction.monkey_strategy, random)
    wolf_strategy = lookup_strategy(instruction.wolf_strategy, random)

    game_runner = GameRunner(
        monkey_strategy=monkey_strategy,
        wolf_strategy=wolf_strategy,
        starting_team=Team.MONKEY,
        random=random,
    )
    return game_runner.simulate(instruction)


def simulate_all(instructions: list[Instruction], max_threads: int) -> list[Result]:
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        return list(executor.map(simulate_one, instructions))
