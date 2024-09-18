import itertools
import math
from collections import defaultdict
from copy import copy
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
        # First, if there's a winning move, choose it
        winning_move = board_inspector.find_first_winning_move(all_permitted_moves)
        if winning_move:
            return winning_move

        # Secondly, calculate the simple strength metric for all moves
        # Doing further analysis is costly, so we'll only do it for the 10% most promising moves
        metric_to_moves: dict[float, list[CompletedMoves]] = defaultdict(list)
        for completed_moves in all_permitted_moves:
            metric = self.metric.calculate(completed_moves.board, completed_moves.team)
            metric_to_moves[round(metric, 6)].append(completed_moves)
        log.info(f"Grouped {len(all_permitted_moves)} moves into {len(metric_to_moves)} groups by strength")

        # Filter our moves down to the 10% most promising
        # Filter the list down if it's longer than 10% of the original list, preferring larger metrics, then randomly
        # This does happen, e.g. if every metric is equal after the first move
        threshold_percentile = 90
        metric_threshold = np.percentile(list(metric_to_moves.keys()), threshold_percentile)
        max_length = math.ceil(len(all_permitted_moves) * (1 - threshold_percentile / 100))
        log.info(f"Found 90th percentile {metric_threshold:.3f}")
        moves_for_analysis: list[tuple[float, CompletedMoves]] = []
        for metric, moves in sorted(metric_to_moves.items(), key=lambda t: t[0], reverse=True):
            if metric < metric_threshold:
                log.info(f"Ignoring {len(moves)} moves with metric {metric:.3f} which is below threshold")
                continue

            new_length = len(moves_for_analysis) + len(moves)
            if new_length < max_length:
                log.info(f"Using all {len(moves)} moves with metric {metric:.3f}")
                for move in moves:
                    moves_for_analysis.append((metric, move))
            else:
                moves_copy = copy(moves)
                self.random.shuffle(moves_copy)
                to_use = max_length - len(moves_for_analysis)
                log.info(f"Randomly selecting {to_use} of {len(moves_copy)} moves with metric {metric:.3f}")
                for move in moves_copy[:to_use]:
                    moves_for_analysis.append((metric, move))
                break

        # Over all possible dice rolls, what is the probability our opponent wins next turn?
        dice_rolls = [DiceRoll(*t) for t in itertools.product((1, 2, 3), (1, 2, 3), (1, 2, 3))]
        log.info(
            f"Will factor in chance of losing next turn for {len(moves_for_analysis)} moves out of "
            f"{len(all_permitted_moves)}, using all {len(dice_rolls)} dice rolls"
        )
        advanced_metric_to_moves: dict[float, list[CompletedMoves]] = defaultdict(list)
        for metric, this_turn in moves_for_analysis:
            chance_lose_next_turn = 0.0
            for roll in dice_rolls:
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

            # If there's zero chance of losing next turn, double the attractiveness of this turn
            # Otherwise use a negative linear gradient to express dislike to chances of losing next turn
            weighting = 2.0 if chance_lose_next_turn == 0.0 else (1.0 - chance_lose_next_turn)
            advanced_metric = round(metric * weighting, 6)
            log.info(f"chance_lose_next_turn={chance_lose_next_turn:.3f}, advanced_metric={advanced_metric:.3f}")
            advanced_metric_to_moves[advanced_metric].append(this_turn)

        max_metric = max(advanced_metric_to_moves.keys())
        max_metrics_boards = advanced_metric_to_moves[max_metric]
        log.info(f"Selecting move from {len(max_metrics_boards)} moves with max_metric {max_metric:.3f}")
        return self.random.choice(max_metrics_boards)
