import logging
import multiprocessing
from cProfile import Profile
from logging import getLogger
from pathlib import Path
from pstats import SortKey

import polars as pl

from ninja_taisen.algos.card_mover import CardMover
from ninja_taisen.algos.game_runner import simulate_many_multi_process
from ninja_taisen.algos.move_gatherer import gather_all_permitted_moves
from ninja_taisen.dtos import BoardDto, InstructionDto, MoveRequestBody, MoveResponseBody, ResultDto, StrategyName
from ninja_taisen.logging_setup import setup_logging
from ninja_taisen.objects.safe_random import SafeRandom
from ninja_taisen.objects.types import CATEGORY_BY_DTO, TEAM_BY_DTO, Board, Card, Category
from ninja_taisen.strategy.strategy_lookup import lookup_strategy

log = getLogger(__name__)


def simulate(
    instructions: list[InstructionDto],
    max_processes: int = 1,
    per_process: int = 100,
    csv_results: Path | None = None,
    parquet_results: Path | None = None,
    verbosity: int = logging.INFO,
    log_file: Path | None = None,
    profile: bool = False,
) -> list[ResultDto]:
    setup_logging(verbosity, log_file)

    if max_processes <= 0:
        cpu_count = multiprocessing.cpu_count()
        if cpu_count is None:
            raise OSError("Unable to deduce CPU count from os.cpu_count(). Please manually specify max_processes >= 1")
        log.info(f"User provided max_processes={max_processes}; found cpu_count={cpu_count}")
        max_processes = max(cpu_count + max_processes, 1)
        log.info(f"Will use max_processes={max_processes}")

    if profile:
        with Profile() as profiler:
            results = simulate_many_multi_process(
                instructions=instructions,
                max_processes=max_processes,
                per_process=per_process,
                verbosity=verbosity,
                log_file=log_file,
            )
        profiler.print_stats(SortKey.TIME)
    else:
        results = simulate_many_multi_process(
            instructions=instructions,
            max_processes=max_processes,
            per_process=per_process,
            verbosity=verbosity,
            log_file=log_file,
        )

    if csv_results:
        csv_results.parent.mkdir(parents=True, exist_ok=True)
        write_csv_results(results, csv_results)
        log.info(f"csv results written to {csv_results}")

    if parquet_results:
        parquet_results.parent.mkdir(parents=True, exist_ok=True)
        write_parquet_results(results, parquet_results)
        log.info(f"parquet results written to {parquet_results}")

    return results


def make_data_frame(results: list[ResultDto]) -> pl.DataFrame:
    return pl.DataFrame(data=results, orient="row")


def write_csv_results(results: list[ResultDto], filename: Path) -> None:
    df = make_data_frame(results)
    df.write_csv(filename)


def write_parquet_results(results: list[ResultDto], filename: Path) -> None:
    df = make_data_frame(results)
    df.write_parquet(filename)


def read_csv_results(filename: Path) -> pl.DataFrame:
    return pl.read_csv(filename, schema_overrides={"start_time": pl.Datetime, "end_time": pl.Datetime})


def read_parquet_results(filename: Path) -> pl.DataFrame:
    return pl.read_parquet(filename)


def choose_move(request: MoveRequestBody, strategy_name: StrategyName, random: SafeRandom | None) -> MoveResponseBody:
    setup_logging()

    random = random or SafeRandom(seed=None)
    dice_rolls = {
        Category.rock: random.roll_dice(),
        Category.paper: random.roll_dice(),
        Category.scissors: random.roll_dice(),
    }
    team = TEAM_BY_DTO[request.team]
    strategy = lookup_strategy(strategy_name, random)

    all_permitted_moves = gather_all_permitted_moves(
        starting_board=Board.from_dto(request.board),
        team=team,
        dice_rolls=dice_rolls,
    )
    chosen_moves = strategy.choose_moves(all_permitted_moves)

    return MoveResponseBody(moves=[m.to_dto(team) for m in chosen_moves.moves])


def execute_move(request: MoveRequestBody, response: MoveResponseBody) -> BoardDto:
    setup_logging()

    board = Board.from_dto(request.board)
    dice_by_category = {
        Category.rock: request.dice.rock,
        Category.paper: request.dice.paper,
        Category.scissors: request.dice.scissors,
    }
    team = TEAM_BY_DTO[request.team]

    for i, move in enumerate(response.moves):
        log.info(f"Executing move {i+1} of {len(response.moves)}")
        dice_category = CATEGORY_BY_DTO[move.dice_category]
        dice_roll = dice_by_category[dice_category]
        card = Card.from_dto(move.card)
        pile_index, card_index = board.locate_card(card, team)
        card_mover = CardMover(board=board)
        card_mover.move_card_and_resolve_battles(
            team=team, dice_roll=dice_roll, pile_index=pile_index, card_index=card_index
        )

    return board.to_dto()
