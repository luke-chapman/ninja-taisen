from abc import ABC, abstractmethod

from ninja_taisen.objects.board import Board
from ninja_taisen.objects.card import Card, Team


class IMetric(ABC):
    @abstractmethod
    def calculate(self, board: Board, team: Team) -> float:
        pass


class CountMetric(IMetric):
    def calculate(self, board: Board, team: Team) -> float:
        team_metric = self._calculate_team_metric(board.cards[team])
        other_team_metric = self._calculate_team_metric(board.cards[team.other()])
        return team_metric - other_team_metric

    @staticmethod
    def _calculate_team_metric(cards: list[list[Card]]) -> float:
        metric = 0.0
        for pile in cards:
            metric += len(pile)
        return metric


MONKEY_PILE_WEIGHTS = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 0.0]
WOLF_PILE_WEIGHTS = list(reversed(MONKEY_PILE_WEIGHTS))
PILE_WEIGHTS = {Team.MONKEY: MONKEY_PILE_WEIGHTS, Team.WOLF: WOLF_PILE_WEIGHTS}
PILE_WEIGHT_NORMALIZER = max(MONKEY_PILE_WEIGHTS)


class PositionMetric(IMetric):
    def calculate(self, board: Board, team: Team) -> float:
        team_metric = self._calculate_team_metric(board.cards[team], PILE_WEIGHTS[team])
        other_team_metric = self._calculate_team_metric(board.cards[team.other()], PILE_WEIGHTS[team.other()])
        return team_metric - other_team_metric

    @staticmethod
    def _calculate_team_metric(piles: list[list[Card]], pile_weights: list[float]) -> float:
        metric = 0.0
        for pile, pile_weight in zip(piles, pile_weights, strict=False):
            metric += len(pile) * pile_weight
        return metric


# Strength = how many other cards this card can beat
STRENGTHS_TO_WEIGHTS = {1: 3.0, 2: 4.0, 3: 5.0, 4: 9.0}
STRENGTH_WEIGHTING_NORMALIZER = max(STRENGTHS_TO_WEIGHTS.values())


class StrengthMetric(IMetric):
    def calculate(self, board: Board, team: Team) -> float:
        team_metric = self._calculate_team_metric(board.cards[team])
        other_team_metric = self._calculate_team_metric(board.cards[team.other()])
        return team_metric - other_team_metric

    @staticmethod
    def _calculate_team_metric(piles: list[list[Card]]) -> float:
        metric = 0.0
        for pile in piles:
            for card in pile:
                metric += STRENGTHS_TO_WEIGHTS[card.strength]
        return metric


class PositionStrengthMetric(IMetric):
    def calculate(self, board: Board, team: Team) -> float:
        team_metric = self._calculate_team_metric(board.cards[team], PILE_WEIGHTS[team])
        other_team_metric = self._calculate_team_metric(board.cards[team.other()], PILE_WEIGHTS[team.other()])
        return team_metric - other_team_metric

    @staticmethod
    def _calculate_team_metric(piles: list[list[Card]], pile_weights: list[float]) -> float:
        metric = 0.0
        for pile, pile_weight in zip(piles, pile_weights, strict=False):
            for card in pile:
                metric += (
                    STRENGTHS_TO_WEIGHTS[card.strength] / STRENGTH_WEIGHTING_NORMALIZER
                    + pile_weight / PILE_WEIGHT_NORMALIZER
                )
        return metric
