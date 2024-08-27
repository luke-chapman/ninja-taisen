import logging
import multiprocessing
from cProfile import Profile
from logging import getLogger
from pathlib import Path
from pstats import SortKey

from ninja_taisen.algos.card_mover import CardMover
from ninja_taisen.algos.game_runner import simulate_many_multi_process
from ninja_taisen.algos.move_gatherer import gather_all_permitted_moves
from ninja_taisen.dtos import (
    ChooseRequest,
    ChooseResponse,
    ExecuteRequest,
    ExecuteResponse,
    InstructionDto,
    ResultsFormat,
)
from ninja_taisen.objects.safe_random import SafeRandom
from ninja_taisen.objects.types import CATEGORY_BY_DTO, TEAM_BY_DTO, Board, Card, Category
from ninja_taisen.strategy.strategy_lookup import lookup_strategy
from ninja_taisen.utils.logging_setup import setup_logging

log = getLogger(__name__)


def simulate(
    instructions: list[InstructionDto],
    results_dir: Path,
    results_format: ResultsFormat = "parquet",
    max_processes: int = 1,
    per_process: int = 100,
    verbosity: int = logging.INFO,
    log_file: Path | None = None,
    profile: bool = False,
    serialisation_dir: Path | None = None,
) -> None:
    setup_logging(verbosity, log_file)

    results_dir.mkdir(parents=True, exist_ok=True)
    if serialisation_dir:
        serialisation_dir.mkdir(parents=True, exist_ok=True)

    if max_processes <= 0:
        cpu_count = multiprocessing.cpu_count()
        if cpu_count is None:
            raise OSError("Unable to deduce CPU count from os.cpu_count(). Please manually specify max_processes >= 1")
        log.info(f"User provided max_processes={max_processes}; found cpu_count={cpu_count}")
        max_processes = max(cpu_count + max_processes, 1)
        log.info(f"Will use max_processes={max_processes}")

    if profile:
        with Profile() as profiler:
            simulate_many_multi_process(
                instructions=instructions,
                results_dir=results_dir,
                results_format=results_format,
                max_processes=max_processes,
                per_process=per_process,
                verbosity=verbosity,
                log_file=log_file,
                serialisation_dir=serialisation_dir,
            )
        profiler.print_stats(SortKey.TIME)
    else:
        simulate_many_multi_process(
            instructions=instructions,
            results_dir=results_dir,
            results_format=results_format,
            max_processes=max_processes,
            per_process=per_process,
            verbosity=verbosity,
            log_file=log_file,
            serialisation_dir=serialisation_dir,
        )


def choose_move(request: ChooseRequest, strategy_name: str, random: SafeRandom | None) -> ChooseResponse:
    all_permitted_moves = gather_all_permitted_moves(
        starting_board=Board.from_dto(request.board),
        team=TEAM_BY_DTO[request.team],
        dice_rolls={
            Category.rock: request.dice.rock,
            Category.paper: request.dice.paper,
            Category.scissors: request.dice.scissors,
        },
    )
    if len(all_permitted_moves) == 0:
        return ChooseResponse(moves=[])

    random = random or SafeRandom()  # Seeded with current time by default
    strategy = lookup_strategy(strategy_name, random)
    chosen_moves = strategy.choose_moves(all_permitted_moves)
    return ChooseResponse(moves=[m.to_dto() for m in chosen_moves.moves])


def execute_move(request: ExecuteRequest) -> ExecuteResponse:
    board = Board.from_dto(request.board)
    dice_by_category = {
        Category.rock: request.dice.rock,
        Category.paper: request.dice.paper,
        Category.scissors: request.dice.scissors,
    }
    team = TEAM_BY_DTO[request.team]

    for i, move in enumerate(request.moves):
        log.info(f"Executing move {i+1} of {len(request.moves)}")
        dice_category = CATEGORY_BY_DTO[move.dice_category]
        dice_roll = dice_by_category[dice_category]
        card = Card.from_dto(move.card)
        pile_index, card_index = board.locate_card(card, team)
        card_mover = CardMover(board=board)
        card_mover.move_card_and_resolve_battles(
            team=team, dice_roll=dice_roll, pile_index=pile_index, card_index=card_index
        )

    return ExecuteResponse(board=board.to_dto())
