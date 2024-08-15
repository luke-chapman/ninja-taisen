from logging import getLogger

from ninja_taisen.objects.card import Team

logger = getLogger(__name__)


class GameResult:
    def __init__(self, winning_team: Team | None, turn_count: int, time_taken: float) -> None:
        self.winning_team = winning_team
        self.turn_count = turn_count
        self.time_taken = time_taken


class GameResults:
    def __init__(self) -> None:
        self.results: dict[Team | None, list[GameResult]] = {Team.MONKEY: [], Team.WOLF: [], None: []}

    def register_result(self, game_result: GameResult) -> None:
        self.results[game_result.winning_team].append(game_result)

    def print_stats(self) -> None:
        for team, results in self.results.items():
            logger.info(f"Team {team} won {len(results)} games")
