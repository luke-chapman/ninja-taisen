from datetime import datetime
from typing import NamedTuple


class Instruction(NamedTuple):
    id: int
    seed: int
    monkey_strategy: str
    wolf_strategy: str


class Result(NamedTuple):
    id: int
    seed: int
    monkey_strategy: str
    wolf_strategy: str
    winner: str
    turn_count: int
    start_time: datetime
    end_time: datetime
    process_name: str
