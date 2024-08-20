from ninja_taisen.objects.safe_random import SafeRandom
from ninja_taisen.objects.types import StrategyName
from ninja_taisen.strategy.metric import CountMetric, PositionMetric, StrengthMetric
from ninja_taisen.strategy.strategy import IStrategy, MetricStrategy, RandomSpotWinStrategy, RandomStrategy


def lookup_strategy(strategy: str, random: SafeRandom) -> IStrategy:
    if strategy == StrategyName.random:
        return RandomStrategy(random)
    if strategy == StrategyName.random_spot_win:
        return RandomSpotWinStrategy(random)
    if strategy == StrategyName.metric_count:
        return MetricStrategy(CountMetric(), random)
    if strategy == StrategyName.metric_position:
        return MetricStrategy(PositionMetric(), random)
    if strategy == StrategyName.metric_strength:
        return MetricStrategy(StrengthMetric(), random)
    else:
        raise ValueError(f"Unexpected strategy '{strategy}'")
