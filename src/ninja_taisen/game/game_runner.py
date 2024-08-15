from logging import getLogger
from time import perf_counter

from more_itertools import unique_everseen

from ninja_taisen.algos import board_builder, board_context_gatherer, board_inspector
from ninja_taisen.game.game_results import GameResult
from ninja_taisen.objects.card import Team
from ninja_taisen.strategy.strategy import IStrategy

log = getLogger(__name__)


class GameRunner:
    def __init__(self, monkey_strategy: IStrategy, wolf_strategy: IStrategy, starting_team: Team) -> None:
        self.board = board_builder.make_board()
        self.strategies = {Team.MONKEY: monkey_strategy, Team.WOLF: wolf_strategy}
        self.starting_team = starting_team

    def play(self) -> GameResult:

        start_time = perf_counter()

        team = self.starting_team
        victorious_team: Team | None = None
        turn_count = 0
        while victorious_team is None and turn_count < 50:
            self._execute_turn(team)

            victorious_team = board_inspector.victorious_team(self.board)
            team = team.other()
            turn_count += 1

        time_taken = perf_counter() - start_time
        log.info(f"Winner={victorious_team}, turn_count={turn_count}, time_taken={time_taken}s")
        return GameResult(victorious_team, turn_count, time_taken)

    def _execute_turn(self, team: Team) -> None:

        board_contexts = board_context_gatherer.gather_complete_move_contexts(self.board, team)
        unique_boards = list(unique_everseen(context.board for context in board_contexts))
        if unique_boards:
            self.board = self.strategies[team].choose_board(unique_boards, team)
