import datetime
from collections import defaultdict
from logging import getLogger
from pathlib import Path
from typing import Any

import polars as pl

from ninja_taisen.objects.card import Team

logger = getLogger(__name__)


class GameResult:
    def __init__(self, winning_team: Team | None, turn_count: int, time_taken_s: float) -> None:
        self.winning_team = winning_team
        self.turn_count = turn_count
        self.time_taken_s = time_taken_s


class GameResults:
    def __init__(self, results_dir: Path) -> None:
        assert results_dir.is_dir()
        self.results_dir = results_dir
        self.results: list[GameResult] = []

    def register_result(self, game_result: GameResult) -> None:
        self.results.append(game_result)

    def print_stats(self) -> None:
        for team in (Team.MONKEY, Team.WOLF, None):
            games_won = sum(1 if r.winning_team == team else 0 for r in self.results)
            logger.info(f"Team {team} won {games_won} games")

        frame_dict: dict[str, list[Any]] = defaultdict(list)
        for i, result in enumerate(self.results):
            frame_dict["game_index"].append(i)
            frame_dict["winning_team"].append(str(result.winning_team) or "NONE")
            frame_dict["turn_count"].append(result.turn_count)
            frame_dict["time_taken_s"].append(result.time_taken_s)

        df = pl.DataFrame(frame_dict)
        timestamp = datetime.datetime.now(datetime.UTC).strftime("%Y%m%d_%H%M%S")
        df.write_csv(self.results_dir / f"results_{timestamp}.csv")
