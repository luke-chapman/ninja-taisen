from abc import ABC, abstractmethod
from collections import defaultdict
from logging import getLogger

from ninja_taisen.algos.board_inspector import find_first_winning_move
from ninja_taisen.objects.safe_random import SafeRandom
from ninja_taisen.objects.types import CompletedMoves, Team
from ninja_taisen.strategy.metric import IMetric

log = getLogger(__name__)


class IStrategy(ABC):
    @abstractmethod
    def choose_moves(self, all_permitted_moves: list[CompletedMoves], team: Team) -> CompletedMoves:
        pass


class RandomStrategy(IStrategy):
    def __init__(self, random: SafeRandom) -> None:
        self.random = random

    def choose_moves(self, all_permitted_moves: list[CompletedMoves], team: Team) -> CompletedMoves:
        return self.random.choice(all_permitted_moves)


class RandomSpotWinStrategy(IStrategy):
    def __init__(self, random: SafeRandom) -> None:
        self.random = random

    def choose_moves(self, all_permitted_moves: list[CompletedMoves], team: Team) -> CompletedMoves:
        winning_board = find_first_winning_move(all_permitted_moves, team)
        if winning_board:
            return winning_board

        return self.random.choice(all_permitted_moves)


class MetricStrategy(IStrategy):
    def __init__(self, metric: IMetric, random: SafeRandom) -> None:
        self.metric = metric
        self.random = random

    def choose_moves(self, all_permitted_moves: list[CompletedMoves], team: Team) -> CompletedMoves:
        winning_board = find_first_winning_move(all_permitted_moves, team)
        if winning_board:
            return winning_board

        metric_to_moves: dict[float, list[CompletedMoves]] = defaultdict(list)
        for completed_moves in all_permitted_moves:
            metric = self.metric.calculate(completed_moves.board, team)
            metric_to_moves[metric].append(completed_moves)

        max_metric = max(metric_to_moves.keys())
        max_metrics_boards = metric_to_moves[max_metric]
        return self.random.choice(max_metrics_boards)
