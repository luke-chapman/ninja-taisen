from logging import getLogger

from fastapi import FastAPI

from ninja_taisen import choose_move, execute_move
from ninja_taisen.dtos import ChooseRequest, ExecuteRequest
from ninja_taisen.utils.logging_setup import setup_logging
from ninja_taisen.utils.run_directory import setup_run_directory

# Setup run directory, logging, and our random number generator
run_directory = setup_run_directory()
setup_logging(log_file=run_directory / "log.txt")
log = getLogger(__name__)


app = FastAPI()
log.info(f"Setting up FastAPI server '{__name__}'")


@app.post("/choose")
async def handle_choose(request_body: ChooseRequest) -> dict:
    log.info("Added /choose POST endpoint")
    response_body = choose_move(request=request_body)
    return response_body.model_dump(round_trip=True, by_alias=True)


@app.post("/execute")
async def handle_execute(request_body: ExecuteRequest) -> dict:
    log.info("Added /execute POST endpoint")
    response_body = execute_move(request=request_body)
    return response_body.model_dump(round_trip=True, by_alias=True)
