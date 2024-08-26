import sys
from argparse import ArgumentParser
from logging import getLogger

from flask import Flask, request

from ninja_taisen.api import choose_move
from ninja_taisen.dtos import MoveRequestBody, StrategyName
from ninja_taisen.objects.safe_random import SafeRandom
from ninja_taisen.objects.types import ALL_STRATEGY_NAMES

log = getLogger(__name__)


def main(override_args: list[str] | None = None) -> int:
    parser = ArgumentParser()
    parser.add_argument("--strategy", default=StrategyName.metric_strength, choices=ALL_STRATEGY_NAMES)
    parser.add_argument("--seed", default=0)
    args = parser.parse_args(override_args or sys.argv[1:])
    strategy = args.strategy
    random = SafeRandom(args.seed)

    def handle_choose():
        if not request.is_json:
            return {"error": "Request must be JSON"}, 400
        try:
            data = request.get_json()
            request_body = MoveRequestBody.model_validate_json(data)
            response_body = choose_move(request=request_body, strategy_name=strategy, random=random)
            return response_body.model_dump(round_trip=True, by_alias=True), 200
        except Exception as e:
            return {"error": str(e)}, 400

    app = Flask(__name__)
    app.route("/choose", methods=["POST"])(handle_choose)
    app.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
