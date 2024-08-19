from ninja_taisen.objects.safe_random import SafeRandom
from ninja_taisen.strategy.metric import CountMetric, PositionMetric, StrengthMetric
from ninja_taisen.strategy.strategy import IStrategy, MetricStrategy, RandomSpotWinStrategy, RandomStrategy
from ninja_taisen.strategy.strategy_names import StrategyNames


def lookup_strategy(strategy: str, random: SafeRandom) -> IStrategy:
    if strategy == StrategyNames.random:
        return RandomStrategy(random)
    if strategy == StrategyNames.random_spot_win:
        return RandomSpotWinStrategy(random)
    if strategy == StrategyNames.metric_count:
        return MetricStrategy(CountMetric(), random)
    if strategy == StrategyNames.metric_position:
        return MetricStrategy(PositionMetric(), random)
    if strategy == StrategyNames.metric_strength:
        return MetricStrategy(StrengthMetric(), random)
    else:
        raise ValueError(f"Unexpected strategy '{strategy}'")
