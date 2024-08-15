from ninja_taisen.strategy.metric import CountMetric, PositionMetric, PositionStrengthMetric, StrengthMetric
from ninja_taisen.strategy.strategy import IStrategy, MetricStrategy, RandomSpotWinStrategy, RandomStrategy
from ninja_taisen.strategy.strategy_names import StrategyNames


def lookup_strategy(strategy: str) -> IStrategy:
    if strategy == StrategyNames.random:
        return RandomStrategy()
    if strategy == StrategyNames.random_spot_win:
        return RandomSpotWinStrategy()
    if strategy == StrategyNames.metric_count:
        return MetricStrategy(CountMetric())
    if strategy == StrategyNames.metric_position:
        return MetricStrategy(PositionMetric())
    if strategy == StrategyNames.metric_position_strength:
        return MetricStrategy(PositionStrengthMetric())
    if strategy == StrategyNames.metric_count:
        return MetricStrategy(StrengthMetric())
    else:
        raise ValueError(f"Unexpected strategy '{strategy}'")
