from copy import deepcopy

from ninja_taisen.public_types import Board, Category


class BoardContext:
    def __init__(
        self,
        board: Board,
        used_joker: bool,
        dice_used: list[tuple[Category, int]],
    ) -> None:
        self.board = board
        self.used_joker = used_joker
        self.dice_used = dice_used

    def clone(self) -> "BoardContext":
        return BoardContext(self.board.model_copy(deep=True), self.used_joker, deepcopy(self.dice_used))
