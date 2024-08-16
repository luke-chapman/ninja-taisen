from datetime import datetime
from pathlib import Path
from typing import NamedTuple


class Instruction(NamedTuple):
    monkey_strategy: str
    wolf_strategy: str
    seed: int


class Options(NamedTuple):
    verbosity: int
    profile: bool
    results_file: Path


class Result(NamedTuple):
    monkey_strategy: str
    wolf_strategy: str
    seed: int
    winner: str
    turn_count: int
    start_time: datetime
    end_time: datetime
