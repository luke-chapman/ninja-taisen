from ninja_taisen.strategy.metric import CountMetric, IMetric, PositionMetric, PositionStrengthMetric, StrengthMetric
from ninja_taisen.strategy.strategy import IStrategy, MetricStrategy, RandomSpotWinStrategy, RandomStrategy

STRATEGIES = [
    "random",
    "random_spot_win",
    "metric_count",
    "metric_position",
    "metric_position_strength",
    "metric_strength",
]


def lookup_strategy(strategy: str) -> IStrategy:
    if strategy == "random":
        return RandomStrategy()
    if strategy == "random_spot_win":
        return RandomSpotWinStrategy()
    if strategy.startswith("metric_"):
        _, metric = strategy.split("_")
        metrics: dict[str, IMetric] = {
            "count": CountMetric(),
            "position": PositionMetric(),
            "position_strength": PositionStrengthMetric(),
            "strength": StrengthMetric(),
        }
        return MetricStrategy(metrics[metric])

    raise RuntimeError(f"Unexpected strategy {strategy}")
