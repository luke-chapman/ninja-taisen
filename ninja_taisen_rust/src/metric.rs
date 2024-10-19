use crate::board::CompletedMoves;
use crate::card::cards;

pub trait Metric {
    fn normalise(team_metric: f32, other_team_metric: f32) -> f32 {
        assert!(team_metric >= 0.0);
        assert!(other_team_metric >= 0.0);
        if other_team_metric != 0.0 { team_metric / other_team_metric } else { team_metric }
    }

    fn calculate(&self, completed_moves: &CompletedMoves) -> f32;
}

pub struct CountMetric {
}

impl Metric for CountMetric {
    fn calculate(&self, completed_moves: &CompletedMoves) -> f32 {
        let monkey_count = completed_moves.board.monkey_heights.iter().sum();
        let wolf_count = completed_moves.board.wolf_heights.iter().sum();
        if completed_moves.is_monkey {
            Metric::normalise(monkey_count, wolf_count)
        }
        else {
            Metric::normalise(wolf_count, monkey_count)
        }
    }
}

pub struct StrengthMetric {
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

pub struct PositionMetric {
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
