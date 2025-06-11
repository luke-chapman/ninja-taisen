from logging import getLogger

from ninja_taisen.dtos import Strategy
from ninja_taisen.objects.safe_random import SafeRandom
from ninja_taisen.strategy.metric import CountMetric, PositionMetric, StrengthMetric
from ninja_taisen.strategy.strategy import IStrategy
from ninja_taisen.strategy.strategy_impl import (
    MetricStrategy,
    RandomSpotWinStrategy,
    RandomStrategy,
)

log = getLogger(__name__)


def lookup_strategy(strategy: str, random: SafeRandom) -> IStrategy:
    if strategy == "default":
        strategy = Strategy.metric_strength
        log.info(f"Using default strategy '{strategy}'")

    if strategy == Strategy.random:
        return RandomStrategy(random)
    if strategy == Strategy.random_spot_win:
        return RandomSpotWinStrategy(random)
    if strategy == Strategy.metric_count:
        return MetricStrategy(CountMetric(), random)
    if strategy == Strategy.metric_position:
        return MetricStrategy(PositionMetric(), random)
    if strategy == Strategy.metric_strength:
        return MetricStrategy(StrengthMetric(), random)
    else:
        raise ValueError(f"Unexpected strategy '{strategy}'")
