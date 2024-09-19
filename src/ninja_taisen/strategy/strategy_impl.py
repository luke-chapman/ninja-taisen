import itertools
import math
from collections import defaultdict
from copy import copy
from logging import getLogger

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
        log.debug(f"Grouped {len(all_permitted_moves)} moves into {len(metric_to_moves)} groups by strength")

        # Filter our moves down to a subset that look promising - save effort on future analysis
        moves_for_analysis = self.__select_moves_for_analysis(metric_to_moves=metric_to_moves)

        # Over all possible dice rolls, what is the probability our opponent wins next turn?
        dice_rolls = [DiceRoll(*t) for t in itertools.product((1, 2, 3), (1, 2, 3), (1, 2, 3))]
        log.debug(
            f"Will factor in chance of losing next turn for {len(moves_for_analysis)} moves out of "
            f"{len(all_permitted_moves)}, using {len(dice_rolls)} dice rolls"
        )
        advanced_metric_to_moves: dict[float, list[CompletedMoves]] = defaultdict(list)
        max_simple_metric = moves_for_analysis[0][0]
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

            if metric == max_simple_metric and chance_lose_next_turn == 0.0:
                log.debug(
                    f"Selecting move with best metric={metric} and best chance_lost_next_turn={chance_lose_next_turn}"
                )
                return this_turn

            # If there's zero chance of losing next turn, double the attractiveness of this turn
            # Otherwise use a negative linear gradient to express dislike to chances of losing next turn
            weighting = 2.0 if chance_lose_next_turn == 0.0 else (1.0 - chance_lose_next_turn)
            advanced_metric = round(metric * weighting, 6)
            log.debug(f"chance_lose_next_turn={chance_lose_next_turn:.3f}, advanced_metric={advanced_metric:.3f}")
            advanced_metric_to_moves[advanced_metric].append(this_turn)

        max_metric = max(advanced_metric_to_moves.keys())
        max_metrics_boards = advanced_metric_to_moves[max_metric]
        log.debug(f"Selecting move from {len(max_metrics_boards)} moves with max_metric {max_metric:.3f}")
        return self.random.choice(max_metrics_boards)

    # Select best 20% of moves, at least 10 and no more than 20
    # Prefer those with higher naive strength metrics
    def __select_moves_for_analysis(
        self, metric_to_moves: dict[float, list[CompletedMoves]]
    ) -> list[tuple[float, CompletedMoves]]:
        total_moves = sum(len(m) for m in metric_to_moves.values())
        rough_proportion = 0.2
        min_moves = min(10, total_moves)
        max_moves = 20
        rough_moves = math.ceil(total_moves * rough_proportion)
        moves_to_select = max(min_moves, min(max_moves, rough_moves))
        log.debug(
            f"Selecting {moves_to_select} moves out of {total_moves}; proportion of "
            f"{int(rough_proportion * 100)}%, bounded between {min_moves} and {max_moves}"
        )

        moves_for_analysis: list[tuple[float, CompletedMoves]] = []
        for metric, moves in sorted(metric_to_moves.items(), key=lambda t: t[0], reverse=True):
            if len(moves_for_analysis) >= moves_to_select:
                break

            moves_copy = copy(moves)
            self.random.shuffle(moves_copy)
            to_use = min(len(moves_copy), moves_to_select - len(moves_for_analysis))
            log.debug(f"Selecting {to_use} of {len(moves_copy)} moves with metric {metric:.3f} for further analysis")
            for i in range(to_use):
                moves_for_analysis.append((metric, moves_copy[i]))

        return moves_for_analysis
