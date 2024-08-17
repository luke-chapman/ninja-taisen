from datetime import datetime
from pathlib import Path
from typing import NamedTuple


class Instruction(NamedTuple):
    monkey_strategy: str
    wolf_strategy: str
    seed: int


class Options(NamedTuple):
    results_file: Path | None = None
    verbosity: int = 0
    profile: bool = False


class Result(NamedTuple):
    monkey_strategy: str
    wolf_strategy: str
    seed: int
    winner: str
    turn_count: int
    start_time: datetime
    end_time: datetime
