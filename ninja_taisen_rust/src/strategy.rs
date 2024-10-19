use std::collections::HashMap;
use rand::prelude::StdRng;
use rand::Rng;
use crate::board::CompletedMoves;
use crate::card::cards;
use crate::metric::{CountMetric,PositionMetric,StrengthMetric,Metric};
use ordered_float::OrderedFloat;

#[derive(PartialEq)]
enum StrategyName {
    Random,
    RandomSpotWin,
    MetricCount,
    MetricPosition,
    MetricStrength,
}

pub struct Strategy {
    name: StrategyName,
}

impl Strategy {
    pub fn new(strategy_name: &String) -> Self {
        match strategy_name.as_str() {
            "random" => { Strategy{name: StrategyName::Random} },
            "random_spot_win" => { Strategy{name: StrategyName::RandomSpotWin} },
            "metric_count" => { Strategy{name: StrategyName::MetricCount} },
            "metric_position" => { Strategy{name: StrategyName::MetricPosition} },
            "metric_strength" => { Strategy{name: StrategyName::MetricStrength} },
            _ => panic!("{}", format!("Could not match strategy_name '{}'", strategy_name)),
        }
    }

    pub fn choose_move<'a, 'b>(&self, all_permitted_moves: &'a Vec<CompletedMoves>, rng: &'b mut StdRng) -> &'a CompletedMoves {
        if self.name != StrategyName::Random {
            for moves in all_permitted_moves {
                let victorious_team = moves.board.victorious_team();
                if victorious_team == cards::NULL {
                    continue
                }
                if moves.is_monkey {
                    if (victorious_team & cards::CHECK_TEAM) == cards::BIT_TEAM_MONKEY {
                        return moves;
                    }
                } else {
                    if (victorious_team & cards::CHECK_TEAM) == cards::BIT_TEAM_WOLF {
                        return moves;
                    }
                }
            }
        }

        match self.name {
            StrategyName::Random => { Self::random_move(all_permitted_moves, rng) }
            StrategyName::RandomSpotWin => { Self::random_move(all_permitted_moves, rng) }
            StrategyName::MetricCount => {
                let metric = CountMetric{};
                Self::random_best_metric(all_permitted_moves, &metric, rng)
            }
            StrategyName::MetricPosition => {
                let metric = PositionMetric{};
                Self::random_best_metric(all_permitted_moves, &metric, rng)
            }
            StrategyName::MetricStrength => {
                let metric = StrengthMetric{};
                Self::random_best_metric(all_permitted_moves, &metric, rng)
            }
        }
    }

    fn random_move<'a, 'b>(all_permitted_moves: &'a Vec<CompletedMoves>, rng: &'b mut StdRng) -> &'a CompletedMoves {
        &all_permitted_moves[rng.gen_range(0..all_permitted_moves.len())]
    }

    fn random_best_metric<'a, 'b, 'c>(all_permitted_moves: &'a Vec<CompletedMoves>, metric: &'b impl Metric, rng: &'c mut StdRng) -> &'a CompletedMoves {
        let mut metric_to_moves: HashMap<OrderedFloat<f32>, Vec<&CompletedMoves>> = HashMap::new();
        for completed_moves in all_permitted_moves {
            let metric_value = OrderedFloat(metric.calculate(completed_moves));
            let existing_moves = metric_to_moves.get_mut(&metric_value);
            if existing_moves.is_some() {
                existing_moves.unwrap().push(completed_moves);
            }
            else {
                metric_to_moves.insert(metric_value, vec![completed_moves]);
            }
        }

        let moves_with_max_metric = metric_to_moves
            .iter()
            .max_by_key(|&t| t.0)
            .unwrap().1;
        &moves_with_max_metric[rng.gen_range(0..moves_with_max_metric.len())]
    }
}
