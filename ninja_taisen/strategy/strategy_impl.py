from collections import defaultdict
from logging import getLogger

from ninja_taisen.algos import board_inspector
from ninja_taisen.objects.safe_random import SafeRandom
from ninja_taisen.objects.types import CompletedMoves
from ninja_taisen.strategy.metric import IMetric
from ninja_taisen.strategy.strategy import IStrategy

log = getLogger(__name__)


class RandomStrategy(IStrategy):
    def __init__(self, random: SafeRandom) -> None:
        self.random = random

    def choose_moves(self, all_permitted_moves: list[CompletedMoves]) -> CompletedMoves:
        return self.random.choice(all_permitted_moves)


class RandomSpotWinStrategy(IStrategy):
    def __init__(self, random: SafeRandom) -> None:
        self.random = random

    def choose_moves(self, all_permitted_moves: list[CompletedMoves]) -> CompletedMoves:
        winning_move = board_inspector.find_first_winning_move(all_permitted_moves)
        if winning_move:
            return winning_move

        return self.random.choice(all_permitted_moves)


class MetricStrategy(IStrategy):
    def __init__(self, metric: IMetric, random: SafeRandom) -> None:
        self.metric = metric
        self.random = random

    def choose_moves(self, all_permitted_moves: list[CompletedMoves]) -> CompletedMoves:
        winning_move = board_inspector.find_first_winning_move(all_permitted_moves)
        if winning_move:
            return winning_move

        metric_to_moves: dict[float, list[CompletedMoves]] = defaultdict(list)
        for completed_moves in all_permitted_moves:
            metric = self.metric.calculate(completed_moves.board, completed_moves.team)
            metric_to_moves[metric].append(completed_moves)

        max_metric = max(metric_to_moves.keys())
        max_metrics_boards = metric_to_moves[max_metric]
        return self.random.choice(max_metrics_boards)
