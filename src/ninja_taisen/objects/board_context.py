from copy import deepcopy

from ninja_taisen.dtos import BoardDto, CategoryDto


class BoardContext:
    def __init__(
        self,
        board: BoardDto,
        used_joker: bool,
        dice_used: list[tuple[CategoryDto, int]],
    ) -> None:
        self.board = board
        self.used_joker = used_joker
        self.dice_used = dice_used

    def clone(self) -> "BoardContext":
        return BoardContext(self.board.model_copy(deep=True), self.used_joker, deepcopy(self.dice_used))
