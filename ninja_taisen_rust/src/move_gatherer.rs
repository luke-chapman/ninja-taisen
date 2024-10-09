use crate::board::{Board, CardLocation, CompletedMoves, Move};
use crate::card::cards;
use crate::dice::DiceRoll;

pub fn gather_all_moves(board: &Board, is_monkey: bool, dice_rolls: &[DiceRoll; 3]) -> Vec<CompletedMoves> {
    let mut completed_moves = Vec::new();
    let initial_states = vec![CompletedMoves {
        moves: Vec::new(),
        board: board.clone(),
        is_monkey,
    }];

    for a in 0..dice_rolls.len() {
        let mut new_moves_a = gather_moves_for_dice_roll(
            &initial_states,
            is_monkey,
            dice_rolls[a].category,
            dice_rolls[a].roll
        );

        for b in 0..dice_rolls.len() {
            if a == b {
                continue
            }

            let mut new_moves_b = gather_moves_for_dice_roll(
                &new_moves_a,
                is_monkey,
                dice_rolls[b].category,
                dice_rolls[b].roll
            );

            for c in 0..dice_rolls.len() {
                if a == c || b == c {
                    continue
                }

                let mut new_moves_c = gather_moves_for_dice_roll(
                    &new_moves_b,
                    is_monkey,
                    dice_rolls[c].category,
                    dice_rolls[c].roll
                );
                completed_moves.append(&mut new_moves_c);
            }
            completed_moves.append(&mut new_moves_b);
        }
        completed_moves.append(&mut new_moves_a);
    }

    completed_moves
}

fn gather_moves_for_dice_roll(
    initial_states: &Vec<CompletedMoves>,
    is_monkey: bool,
    dice_category: u8,
    dice_roll: i8
) -> Vec<CompletedMoves> {
    let mut end_states = Vec::new();

    for initial_state in initial_states {
        if initial_state.board.victorious_team() != cards::NULL {
            continue
        }

        let movable_card_locations = moveable_card_indices(
            &initial_state.board, is_monkey, dice_category, initial_state.used_joker()
        );
        for card_location in movable_card_locations {
            let mut board = initial_state.board.clone();
            let card = board.get_card(is_monkey, card_location.pile_index, card_location.card_index);
            board.move_card_and_resolve_battles(
                is_monkey,
                dice_roll,
                card_location.pile_index,
                card_location.card_index
            );

            let mut moves = initial_state.moves.clone();
            moves.push(Move{dice_category, dice_roll, card });

            let end_state = CompletedMoves { moves, board, is_monkey };
            end_states.push(end_state);
        }
    }

    end_states
}

fn moveable_card_indices(board: &Board, is_monkey: bool, category: u8, used_joker: bool) -> Vec<CardLocation> {
    let mut card_locations = Vec::new();
    let heights = if is_monkey { board.monkey_heights } else { board.wolf_heights };
    let cards = if is_monkey { board.monkey_cards } else { board.wolf_cards };

    for pile_index in 0..heights.len() {
        let pile_height = heights[pile_index] as i8;
        let accessible_start = std::cmp::max(0, pile_height - 3);

        for card_index_i8 in accessible_start..pile_height {
            let card_index = card_index_i8 as usize;
            let card = cards[pile_index * 10 + card_index];
            let card_category = card & cards::CHECK_CATEGORY;
            if card_category == category || ((card_category == cards::BITS_CATEGORY_JOKER) && !used_joker) {
                card_locations.push(CardLocation{
                    pile_index: pile_index as u8,
                    card_index: card_index as u8
                })
            }
        }
    }

    card_locations
}
