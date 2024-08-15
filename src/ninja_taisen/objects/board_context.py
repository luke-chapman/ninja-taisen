from copy import deepcopy

from ninja_taisen.objects.board import Board
from ninja_taisen.objects.card import CombatCategory


class BoardContext:
    def __init__(
        self,
        board: Board,
        used_joker: bool,
        dice_used: list[tuple[CombatCategory, int]],
    ) -> None:
        self.board = board
        self.used_joker = used_joker
        self.dice_used = dice_used

    def clone(self) -> "BoardContext":
        return BoardContext(self.board.clone(), self.used_joker, deepcopy(self.dice_used))
