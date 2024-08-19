from datetime import datetime

from pydantic import BaseModel


class Instruction(BaseModel):
    id: int
    seed: int
    monkey_strategy: str
    wolf_strategy: str


class Result(BaseModel):
    id: int
    seed: int
    monkey_strategy: str
    wolf_strategy: str
    winner: str
    turn_count: int
    start_time: datetime
    end_time: datetime
    process_name: str
