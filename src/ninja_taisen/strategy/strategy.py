from abc import ABC, abstractmethod
from collections import defaultdict
from logging import getLogger

from ninja_taisen.algos.board_inspector import find_winning_board
from ninja_taisen.dtos import BoardDto, TeamDto
from ninja_taisen.objects.safe_random import SafeRandom
from ninja_taisen.strategy.metric import IMetric

log = getLogger(__name__)


class IStrategy(ABC):
    @abstractmethod
    def choose_board(self, boards: list[BoardDto], team: TeamDto) -> BoardDto:
        pass


class RandomStrategy(IStrategy):
    def __init__(self, random: SafeRandom) -> None:
        self.random = random

    def choose_board(self, boards: list[BoardDto], team: TeamDto) -> BoardDto:
        return self.random.choice(boards)


class RandomSpotWinStrategy(IStrategy):
    def __init__(self, random: SafeRandom) -> None:
        self.random = random

    def choose_board(self, boards: list[BoardDto], team: TeamDto) -> BoardDto:
        winning_board = find_winning_board(boards, team)
        if winning_board:
            return winning_board

        return self.random.choice(boards)


class MetricStrategy(IStrategy):
    def __init__(self, metric: IMetric, random: SafeRandom) -> None:
        self.metric = metric
        self.random = random

    def choose_board(self, boards: list[BoardDto], team: TeamDto) -> BoardDto:
        winning_board = find_winning_board(boards, team)
        if winning_board:
            return winning_board

        metric_to_boards: dict[float, list[BoardDto]] = defaultdict(list)
        for board in boards:
            metric = self.metric.calculate(board, team)
            metric_to_boards[metric].append(board)

        max_metric = max(metric_to_boards.keys())
        max_metrics_boards = metric_to_boards[max_metric]
        return self.random.choice(max_metrics_boards)
