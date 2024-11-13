from abc import ABC, abstractmethod
from collections import defaultdict

from ninja_taisen.objects.types import Board, Card, Team


class IMetric(ABC):
    @abstractmethod
    def calculate(self, board: Board, team: Team) -> float:
        pass

    @staticmethod
    def _normalise(team_metric: float, other_team_metric: float) -> float:
        assert team_metric >= 0.0
        assert other_team_metric >= 0.0
        return team_metric / other_team_metric if other_team_metric != 0.0 else team_metric


class CountMetric(IMetric):
    def calculate(self, board: Board, team: Team) -> float:
        team_metric = self.__count_cards(board.cards(team))
        other_team_metric = self.__count_cards(board.cards(team.other()))
        return self._normalise(team_metric, other_team_metric)

    @staticmethod
    def __count_cards(cards: defaultdict[int, list[Card]]) -> float:
        return float(sum(len(pile) for pile in cards.values()))


MONKEY_PILE_WEIGHTS = [4, 4, 4, 4, 5, 6, 7, 8, 9, 10, 100]
WOLF_PILE_WEIGHTS = list(reversed(MONKEY_PILE_WEIGHTS))
PILE_WEIGHTS = {Team.monkey: MONKEY_PILE_WEIGHTS, Team.wolf: WOLF_PILE_WEIGHTS}


class PositionMetric(IMetric):
    def calculate(self, board: Board, team: Team) -> float:
        team_metric = self.__calculate_team_metric(board.cards(team), PILE_WEIGHTS[team])
        other_team_metric = self.__calculate_team_metric(board.cards(team.other()), PILE_WEIGHTS[team.other()])
        return self._normalise(team_metric, other_team_metric)

    @staticmethod
    def __calculate_team_metric(piles: defaultdict[int, list[Card]], pile_weights: list[int]) -> float:
        metric = 0.0
        for index, pile in piles.items():
            metric += len(pile) * pile_weights[index]
        return metric


# Strength = how many other cards this card can beat
STRENGTHS_TO_WEIGHTS = {1: 3.0, 2: 4.0, 3: 5.0, 4: 9.0}


class StrengthMetric(IMetric):
    def calculate(self, board: Board, team: Team) -> float:
        team_metric = self.__calculate_team_metric(board.cards(team))
        other_metric = self.__calculate_team_metric(board.cards(team.other()))
        return self._normalise(team_metric, other_metric)

    @staticmethod
    def __calculate_team_metric(piles: defaultdict[int, list[Card]]) -> float:
        metric = 0.0
        for pile in piles.values():
            for card in pile:
                metric += STRENGTHS_TO_WEIGHTS[card.strength]
        return metric
