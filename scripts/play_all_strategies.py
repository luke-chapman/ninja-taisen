import datetime
from pathlib import Path

from ninja_taisen.__main__ import main
from ninja_taisen.strategy.strategy_names import StrategyNames


def run() -> None:
    timestamp = datetime.datetime.now(datetime.UTC).strftime("%Y%m%d_%H%M%S")

    for monkey_strategy in StrategyNames.ALL:
        for wolf_strategy in StrategyNames.ALL:
            command_line = [
                "--games",
                "1",
                "--monkey-strategy",
                monkey_strategy,
                "--wolf-strategy",
                wolf_strategy,
                "--results-file",
                str(Path.cwd() / ".ninja-taisen" / timestamp / f"{monkey_strategy}_vs_{wolf_strategy}.csv"),
            ]
            main(command_line)


if __name__ == "__main__":
    run()
