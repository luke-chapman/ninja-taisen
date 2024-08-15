from datetime import datetime
from pathlib import Path
from typing import NamedTuple


class GameInstruction(NamedTuple):
    monkey_strategy: str
    wolf_strategy: str
    seed: int


class GameOptions(NamedTuple):
    verbosity: int
    profile: bool
    results_file: Path


class GameResult(NamedTuple):
    monkey_strategy: str
    wolf_strategy: str
    seed: int
    winner: str
    turn_count: int
    start_time: datetime
    end_time: datetime
