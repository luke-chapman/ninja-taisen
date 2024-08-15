from collections import defaultdict
from logging import getLogger
from random import choice
from typing import Dict, List

from ninja_taisen.algos.board_inspector import find_winning_board
from ninja_taisen.objects.board import Board
from ninja_taisen.objects.card import Team
from ninja_taisen.strategy.metric import IMetric

log = getLogger(__name__)


class IStrategy:
    def choose_board(self, boards: List[Board], team: Team) -> Board:
        pass


class RandomStrategy(IStrategy):
    def choose_board(self, boards: List[Board], team: Team) -> Board:
        return choice(boards)


class RandomSpotWinStrategy(IStrategy):
    def choose_board(self, boards: List[Board], team: Team) -> Board:
        winning_board = find_winning_board(boards, team)
        if winning_board:
            return winning_board

        return choice(boards)


class MetricStrategy(IStrategy):
    def __init__(self, metric: IMetric) -> None:
        self.metric = metric

    def choose_board(self, boards: List[Board], team: Team) -> Board:
        winning_board = find_winning_board(boards, team)
        if winning_board:
            return winning_board

        metric_to_boards: Dict[float, List[Board]] = defaultdict(list)
        for board in boards:
            metric = self.metric.calculate(board, team)
            metric_to_boards[metric].append(board)

        max_metric = max(metric_to_boards.keys())
        max_metrics_boards = metric_to_boards[max_metric]
        return choice(max_metrics_boards)
