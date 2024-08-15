from typing import Dict

from ninja_taisen.strategy.metric import CountMetric, IMetric, PositionMetric, PositionStrengthMetric, StrengthMetric
from ninja_taisen.strategy.strategy import IStrategy, MetricStrategy, RandomSpotWinStrategy, RandomStrategy


def lookup_strategy(strategy: str) -> IStrategy:
    if strategy == "random":
        return RandomStrategy()
    if strategy == "random-spot-win":
        return RandomSpotWinStrategy()
    if strategy.startswith("metric:"):
        _, metric = strategy.split(":")
        metrics: Dict[str, IMetric] = {
            "count": CountMetric(),
            "position": PositionMetric(),
            "position-strength": PositionStrengthMetric(),
            "strength": StrengthMetric(),
        }
        return MetricStrategy(metrics[metric])

    raise RuntimeError(f"Unexpected strategy {strategy}")
