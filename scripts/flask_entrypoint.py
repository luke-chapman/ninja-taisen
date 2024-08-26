from logging import getLogger

from flask import Flask, Response, jsonify, request

from ninja_taisen import execute_move
from ninja_taisen.api import move
from ninja_taisen.dtos import ChooseRequest, ExecuteRequest, Strategy
from ninja_taisen.objects.safe_random import SafeRandom
from ninja_taisen.utils.logging_setup import setup_logging
from ninja_taisen.utils.run_directory import setup_run_directory

# Options for how we run the web server
STRATEGY = Strategy.random
SEED = 0

# Setup run directory, logging, and our random number generator
run_directory = setup_run_directory()
setup_logging(log_file=run_directory / "log.txt")
log = getLogger(__name__)
random = SafeRandom(SEED)


# Methods to handle different types of requests
def handle_choose() -> tuple[Response, int]:
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    try:
        data = request.get_json()
        request_body = ChooseRequest.model_validate_json(data)
        response_body = move(request=request_body, strategy_name=STRATEGY, random=random)
        response = jsonify(response_body.model_dump(round_trip=True, by_alias=True))
        return response, 200
    except Exception as e:
        return jsonify({"error": repr(e)}), 500


def handle_execute() -> tuple[Response, int]:
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    try:
        data = request.get_json()
        request_body = ExecuteRequest.model_validate_json(data)
        response_body = execute_move(request=request_body)
        response = jsonify(response_body.model_dump(round_trip=True, by_alias=True))
        return response, 200
    except Exception as e:
        return jsonify({"error": repr(e)}), 500


# Instantiate the magic Flask object and add the /choose and /execute rules
app = Flask(__name__)
app.add_url_rule(rule="/choose", view_func=handle_choose)
app.add_url_rule(rule="/execute", view_func=handle_execute)
