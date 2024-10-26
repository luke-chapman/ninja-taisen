from abc import ABC, abstractmethod
from logging import getLogger

from ninja_taisen.objects.types import CompletedMoves

log = getLogger(__name__)


class IStrategy(ABC):
    @abstractmethod
    def choose_moves(self, all_permitted_moves: list[CompletedMoves]) -> CompletedMoves:
        pass
