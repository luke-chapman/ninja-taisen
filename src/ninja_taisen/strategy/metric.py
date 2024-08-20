from abc import ABC, abstractmethod

from ninja_taisen.dtos import BoardDto, CardPilesDto, TeamDto


class IMetric(ABC):
    @abstractmethod
    def calculate(self, board: BoardDto, team: TeamDto) -> float:
        pass


class CountMetric(IMetric):
    def calculate(self, board: BoardDto, team: TeamDto) -> float:
        team_metric = self.__count_cards(board.cards(team))
        other_team_metric = self.__count_cards(board.cards(team.other()))
        return team_metric - other_team_metric

    @staticmethod
    def __count_cards(cards: CardPilesDto) -> float:
        return float(sum(len(pile) for pile in cards))


MONKEY_PILE_WEIGHTS = [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]
WOLF_PILE_WEIGHTS = [5, 4, 3, 2, 1, 0, -1, -2, -3, -4, -5]
PILE_WEIGHTS = {TeamDto.monkey: MONKEY_PILE_WEIGHTS, TeamDto.wolf: WOLF_PILE_WEIGHTS}


class PositionMetric(IMetric):
    def calculate(self, board: BoardDto, team: TeamDto) -> float:
        team_metric = self.__calculate_team_metric(board.cards(team), PILE_WEIGHTS[team])
        other_team_metric = self.__calculate_team_metric(board.cards(team.other()), PILE_WEIGHTS[team.other()])
        return team_metric - other_team_metric

    @staticmethod
    def __calculate_team_metric(piles: CardPilesDto, pile_weights: list[int]) -> float:
        metric = 0.0
        for pile, pile_weight in zip(piles, pile_weights, strict=True):
            metric += len(pile) * pile_weight
        return metric


# Strength = how many other cards this card can beat
STRENGTHS_TO_WEIGHTS = {1: 3.0, 2: 4.0, 3: 5.0, 4: 9.0}


class StrengthMetric(IMetric):
    def calculate(self, board: BoardDto, team: TeamDto) -> float:
        team_metric = self.__calculate_team_metric(board.cards(team))
        other_team_metric = self.__calculate_team_metric(board.cards(team.other()))
        return team_metric - other_team_metric

    @staticmethod
    def __calculate_team_metric(piles: CardPilesDto) -> float:
        metric = 0.0
        for pile in piles:
            for card in pile:
                metric += STRENGTHS_TO_WEIGHTS[card.strength]
        return metric
