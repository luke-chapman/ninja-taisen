from ninja_taisen.__main__ import main
from ninja_taisen.strategy.strategy_names import StrategyNames


def run() -> None:
    for monkey_strategy in StrategyNames.ALL:
        for wolf_strategy in StrategyNames.ALL:
            command_line = [
                "--games",
                "2",
                "--monkey-strategy",
                monkey_strategy,
                "--wolf-strategy",
                wolf_strategy,
                "--results-prefix",
                f"{monkey_strategy}_vs_{wolf_strategy}_",
            ]
            main(command_line)


if __name__ == "__main__":
    run()
