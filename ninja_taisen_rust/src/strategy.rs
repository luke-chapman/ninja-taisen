use rand::prelude::StdRng;
use rand::Rng;
use crate::board::CompletedMoves;
use crate::card::cards;

trait Strategy {
    fn find_winning_move(&self, all_permitted_moves: &Vec<CompletedMoves>) -> Option<&CompletedMoves> {
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

    fn choose_move(&self, all_permitted_moves: &Vec<CompletedMoves>, rng: &mut StdRng) -> &CompletedMoves;
}

pub struct RandomStrategy {
}

impl Strategy for RandomStrategy {
    fn choose_move(&self, all_permitted_moves: &Vec<CompletedMoves>, rng: &mut StdRng) -> &CompletedMoves {
        &all_permitted_moves[rng.gen_range(0..all_permitted_moves.len())]
    }
}

pub struct RandomSpotWinStrategy {
}

impl Strategy for RandomSpotWinStrategy {
    fn choose_move(&self, all_permitted_moves: &Vec<CompletedMoves>, rng: &mut StdRng) -> &CompletedMoves {
        let winning_move = self.find_winning_move(all_permitted_moves);
        if winning_move.is_some() {
            return winning_move.unwrap()
        }

        &all_permitted_moves[rng.gen_range(0..all_permitted_moves.len())]
    }
}
