import itertools
from collections import defaultdict
from logging import getLogger

import numpy as np

from ninja_taisen.algos import board_inspector, move_gatherer
from ninja_taisen.objects.safe_random import SafeRandom
from ninja_taisen.objects.types import Category, CompletedMoves, DiceRoll
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


class NextTurnPrototypeStrategy(IStrategy):
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

        percentile_80 = np.percentile(list(metric_to_moves.keys()), 80)
        log.info(f"Will perform advanced analysis on those moves with metrics>={percentile_80}")
        dice_rolls = [DiceRoll(*t) for t in itertools.product(range(3), range(3), range(3))]

        advanced_metric_to_moves: dict[float, list[CompletedMoves]] = defaultdict(list)
        for metric, this_turn_moves in metric_to_moves.items():
            if metric < percentile_80:
                log.info(f"Ignoring metric {metric} which is < {percentile_80}")
                continue

            log.info(f"Metric {metric} is > {percentile_80} - will compute next turn")
            for this_turn in this_turn_moves:
                chance_lose_next_turn = 0.0
                for roll in dice_rolls:
                    log.info(roll)
                    next_turn_moves = move_gatherer.gather_all_permitted_moves(
                        starting_board=this_turn.board,
                        team=this_turn.team.other(),
                        dice_rolls={
                            Category.rock: roll.rock,
                            Category.paper: roll.paper,
                            Category.scissors: roll.scissors,
                        },
                    )
                    other_team_wins = board_inspector.find_first_winning_move(next_turn_moves)
                    if other_team_wins:
                        chance_lose_next_turn += roll.probability()

                advanced_metric = metric * (1.0 - chance_lose_next_turn)
                advanced_metric_to_moves[advanced_metric].append(this_turn)

        max_metric = max(advanced_metric_to_moves.keys())
        max_metrics_boards = advanced_metric_to_moves[max_metric]
        return self.random.choice(max_metrics_boards)
