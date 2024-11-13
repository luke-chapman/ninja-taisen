from logging import getLogger

from flask import Flask, Response, jsonify, request

from ninja_taisen import choose_move, execute_move
from ninja_taisen.dtos import ChooseRequest, ExecuteRequest
from ninja_taisen.utils.logging_setup import setup_logging
from ninja_taisen.utils.run_directory import setup_run_directory

# Setup run directory, logging, and our random number generator
run_directory = setup_run_directory()
setup_logging(log_file=run_directory / "log.txt")
log = getLogger(__name__)


# Methods to handle different types of requests
def handle_choose() -> tuple[Response, int]:
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    try:
        data = request.get_json()
        request_body = ChooseRequest.model_validate(data)
        response_body = choose_move(request=request_body)
        response = jsonify(response_body.model_dump(round_trip=True, by_alias=True))
        return response, 200
    except Exception as e:
        return jsonify({"error": repr(e)}), 500


def handle_execute() -> tuple[Response, int]:
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    try:
        data = request.get_json()
        request_body = ExecuteRequest.model_validate(data)
        response_body = execute_move(request=request_body)
        response = jsonify(response_body.model_dump(round_trip=True, by_alias=True))
        return response, 200
    except Exception as e:
        return jsonify({"error": repr(e)}), 500


# Instantiate the magic Flask object and add the /choose and /execute rules
app = Flask(__name__)
log.info(f"Setting up Flask server '{__name__}'")

app.add_url_rule(rule="/choose", methods=["POST"], view_func=handle_choose)
log.info("Added /choose POST url rule")

app.add_url_rule(rule="/execute", methods=["POST"], view_func=handle_execute)
log.info("Added /execute POST url rule")
