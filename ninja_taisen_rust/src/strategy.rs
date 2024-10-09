use std::collections::HashMap;
use rand::prelude::StdRng;
use rand::Rng;
use crate::board::CompletedMoves;
use crate::card::cards;

trait Strategy {
    fn find_winning_move(all_permitted_moves: &Vec<CompletedMoves>) -> Option<&CompletedMoves> {
        for moves in all_permitted_moves {
            let victorious_team = moves.board.victorious_team();
            if victorious_team == cards::NULL {
                continue
            }
            if moves.is_monkey {
                if (victorious_team & cards::CHECK_CATEGORY) == cards::BIT_TEAM_MONKEY {
                    return Some(&moves);
                }
            }
            else {
                if (victorious_team & cards::CHECK_CATEGORY) == cards::BIT_TEAM_WOLF {
                    return Some(&moves);
                }
            }
        }

        return None
    }

    pub fn choose_move(&self, all_permitted_moves: &Vec<CompletedMoves>, rng: &mut StdRng) -> &CompletedMoves;
}

struct RandomStrategy {
}

impl Strategy for RandomStrategy {
    fn choose_move(&self, all_permitted_moves: &Vec<CompletedMoves>, rng: &mut StdRng) -> &CompletedMoves {
        &all_permitted_moves[rng.gen_range(0..all_permitted_moves.len())]
    }
}

struct RandomSpotWinStrategy {
}

impl Strategy for RandomSpotWinStrategy {
    fn choose_move(&self, all_permitted_moves: &Vec<CompletedMoves>, rng: &mut StdRng) -> &CompletedMoves {
        let winning_move = Strategy::find_winning_move(all_permitted_moves);
        if winning_move.is_some() {
            return winning_move.unwrap()
        }

        &all_permitted_moves[rng.gen_range(0..all_permitted_moves.len())]
    }
}

struct MetricStrategy {
    metric: dyn Metric
}

impl Strategy for MetricStrategy {
    fn choose_move(&self, all_permitted_moves: &Vec<CompletedMoves>, rng: &mut StdRng) -> &CompletedMoves {
        let winning_move = Strategy::find_winning_move(all_permitted_moves);
        if winning_move.is_some() {
            return winning_move.unwrap()
        }

        let mut metric_to_moves = HashMap::new();
        for completed_moves in all_permitted_moves {
            let metric = self.metric.calculate(completed_moves);
            let mut existing_moves = metric_to_moves.get_mut(&metric);
            if existing_moves.is_some() {
                existing_moves.unwrap().push(completed_moves);
            }
            else {
                metric_to_moves.insert(metric, vec![completed_moves]);
            }
        }

        let moves_with_max_metric = metric_to_moves
            .iter()
            .max_by_key(|&t| t.0)
            .unwrap().1;
        &moves_with_max_metric[rng.gen_range(0..moves_with_max_metric.len())]
    }
}

trait Metric {
    fn normalise(team_metric: f32, other_team_metric: f32) -> f32 {
        assert!(team_metric >= 0.0);
        assert!(other_team_metric >= 0.0);
        if other_team_metric != 0.0 { team_metric / other_team_metric } else { team_metric }
    }

    fn calculate(&self, completed_moves: &CompletedMoves) -> f32;
}

struct CountMetric {
}

impl Metric for CountMetric {
    fn calculate(&self, completed_moves: &CompletedMoves) -> f32 {
        let monkey_count = completed_moves.board.monkey_heights.iter().sum() as f32;
        let wolf_count = completed_moves.board.wolf_heights.iter().sum() as f32;
        if completed_moves.is_monkey {
            Metric::normalise(monkey_count, wolf_count)
        }
        else {
            Metric::normalise(wolf_count, monkey_count)
        }
    }
}

struct StrengthMetric {
}

impl StrengthMetric {
    fn card_metric(card: u8) -> f32 {
        let strength = card & cards::CHECK_STRENGTH;
        match strength {
            cards::BITS_STRENGTH_1 => { 3.0 }
            cards::BITS_STRENGTH_2 => { 4.0 }
            cards::BITS_STRENGTH_3 => { 5.0 }
            cards::BITS_STRENGTH_4 => { 9.0 }
            _ => { panic!("{}" format("Unexpected strength {}", strength)) }
        }
    }

    fn team_metric(heights: &[u8; 11], cards: &[u8; 110]) -> f32 {
        let mut metric = 0.0;
        for pile_index in 0..heights.len() {
            for card_index in 0..heights[pile_index] {
                metric += StrengthMetric::card_metric(cards[pile_index * 10 + card_index as usize])
            }
        }
        metric
    }
}

impl Metric for StrengthMetric {
    fn calculate(&self, completed_moves: &CompletedMoves) -> f32 {
        let monkey_metric = StrengthMetric::team_metric(&completed_moves.board.monkey_heights, &completed_moves.board.monkey_cards);
        let wolf_metric = StrengthMetric::team_metric(&completed_moves.board.wolf_heights, &completed_moves.board.wolf_cards);
        if completed_moves.is_monkey {
            Metric::normalise(monkey_metric, wolf_metric)
        }
        else {
            Metric::normalise(wolf_metric, monkey_metric)
        }
    }
}

struct PositionMetric {
}

impl PositionMetric {
    fn team_metric(&self, heights: &[u8; 11], is_monkey: bool) -> f32 {
        let monkey_weights: [f32; 11] = [4.0, 4.0, 4.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 100.0];
        let mut metric = 0.0;
        for pile_index in 0..heights.len() {
            if is_monkey {
                metric += (heights[pile_index] as f32) * monkey_weights[pile_index]
            }
            else {
                metric += (heights[pile_index] as f32) * monkey_weights[10 - pile_index]
            }
        }
        metric
    }
}

impl Metric for PositionMetric {
    fn calculate(&self, completed_moves: &CompletedMoves) -> f32 {
        let monkey_metric = self.team_metric(&completed_moves.board.monkey_heights, completed_moves.is_monkey);
        let wolf_metric = self.team_metric(&completed_moves.board.wolf_heights, completed_moves.is_monkey);
        if completed_moves.is_monkey {
            Metric::normalise(monkey_metric, wolf_metric)
        }
        else {
            Metric::normalise(wolf_metric, monkey_metric)
        }
    }
}

pub fn lookup_strategy(strategy_name: &String) -> Box<dyn Strategy> {
    match strategy_name {
        String::from("random") => { Box::new(RandomStrategy{}) }
        String::from("random_spot_win") => { Box::new(RandomSpotWinStrategy{}) }
        String::from("metric_count") => { Box::new(MetricStrategy{metric: CountMetric{}}) }
        String::from("metric_position") => { Box::new(MetricStrategy{metric: PositionMetric{}}) }
        String::from("metric_strength") => { Box::new(MetricStrategy{metric: StrengthMetric{}}) }
    }
}
