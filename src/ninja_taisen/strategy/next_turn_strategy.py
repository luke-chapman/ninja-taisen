import itertools
from abc import abstractmethod

from ninja_taisen.algos import move_gatherer
from ninja_taisen.objects.types import Category, CompletedMoves, DiceRoll, NextTurnForecast
from ninja_taisen.strategy.strategy import IStrategy


class INextTurnStrategy(IStrategy):
    def choose_moves(self, all_permitted_moves: list[CompletedMoves]) -> CompletedMoves:
        dice_rolls = [DiceRoll(*t) for t in itertools.product(range(3), range(3), range(3))]
        forecasts: list[NextTurnForecast] = []

        for this_turn in all_permitted_moves:
            next_turn = {}
            for roll in dice_rolls:
                next_turn[roll] = move_gatherer.gather_all_permitted_moves(
                    starting_board=this_turn.board,
                    team=this_turn.team.other(),
                    dice_rolls={Category.rock: roll.rock, Category.paper: roll.paper, Category.scissors: roll.scissors},
                )
            forecast = NextTurnForecast(this_turn=this_turn, next_turn=next_turn)
            forecasts.append(forecast)

        return self.choose_moves_next_turn(forecasts)

    @abstractmethod
    def choose_moves_next_turn(self, forecasts: list[NextTurnForecast]) -> CompletedMoves:
        pass
