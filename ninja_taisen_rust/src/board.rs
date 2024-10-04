mod card;

use rand::prelude::SliceRandom;
use rand::Rng;

use crate::board::card::cards;

pub struct Board {
    monkey_cards: [u8; 110],
    wolf_cards: [u8; 110],
    pub monkey_heights: [u8; 11],
    pub wolf_heights: [u8; 11]
}

pub struct CardLocation {
    pile_index: u8,
    card_index: u8
}

pub struct DiceRoll {
    category: u8,
    roll: i8
}

static DICE_FACES: [i8; 6] = [1, 1, 1, 2, 2, 3];

fn roll_dice(rng: &mut rand::rngs::StdRng) -> i8 {
    DICE_FACES[rng.gen_range(0..6)]
}

pub fn roll_dice_three_times(rng: &mut rand::rngs::StdRng) -> [DiceRoll; 3] {
    [
        DiceRoll{category: cards::BITS_CATEGORY_ROCK, roll: roll_dice(rng)},
        DiceRoll{category: cards::BITS_CATEGORY_PAPER, roll: roll_dice(rng)},
        DiceRoll{category: cards::BITS_CATEGORY_SCISSORS, roll: roll_dice(rng)},
    ]
}

#[derive(Clone)]
pub struct Move {
    dice_category: u8,
    dice_roll: i8,
    card: u8
}

pub struct CompletedMoves {
    moves: Vec<Move>,
    pub board: Board
}

impl CompletedMoves {
    pub fn used_joker(&self) -> bool {
        self.moves.iter().any(|m| (m.card & cards::CHECK_CATEGORY) == cards::BITS_CATEGORY_JOKER)
    }
}

impl Board {
    pub fn new(rng: &mut rand::rngs::StdRng) -> Self {
        let mut monkey = vec![
            cards::MR1, cards::MR2, cards::MR3,
            cards::MP1, cards::MP2, cards::MP3,
            cards::MS1, cards::MS2, cards::MS3
        ];
        let mut wolf = vec![
            cards::WR1, cards::WR2, cards::WR3,
            cards::WP1, cards::WP2, cards::WP3,
            cards::WS1, cards::WS2, cards::WS3
        ];
        monkey.shuffle(rng);
        wolf.shuffle(rng);

        let mut monkey_cards = [cards::NULL; 110];
        monkey_cards[0] = cards::MJ4;
        monkey_cards[1] = monkey[0];
        monkey_cards[2] = monkey[1];
        monkey_cards[3] = monkey[2];
        monkey_cards[10] = monkey[3];
        monkey_cards[11] = monkey[4];
        monkey_cards[12] = monkey[5];
        monkey_cards[20] = monkey[6];
        monkey_cards[21] = monkey[7];
        monkey_cards[30] = monkey[8];

        let mut wolf_cards = [cards::NULL; 110];
        wolf_cards[70] = wolf[0];
        wolf_cards[80] = wolf[1];
        wolf_cards[81] = wolf[2];
        wolf_cards[90] = wolf[3];
        wolf_cards[91] = wolf[4];
        wolf_cards[92] = wolf[5];
        wolf_cards[100] = cards::WJ4;
        wolf_cards[101] = wolf[6];
        wolf_cards[102] = wolf[7];
        wolf_cards[103] = wolf[8];

        Self {
            monkey_cards,
            monkey_heights: [4, 3, 2, 1, 0, 0, 0, 0, 0, 0, 0],
            wolf_cards,
            wolf_heights: [0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4]
        }
    }

    pub fn clone(&self) -> Self {
        Self {
            monkey_cards: self.monkey_cards.clone(),
            monkey_heights: self.monkey_heights.clone(),
            wolf_cards: self.wolf_cards.clone(),
            wolf_heights: self.wolf_heights.clone()
        }
    }

    pub fn move_card_and_resolve_battles(&mut self, is_monkey: bool, dice_roll: i8, pile_index: u8, card_index: u8) {
        let mut remaining_battles = Vec::new();
        self.move_card(is_monkey, dice_roll, pile_index, card_index, &mut remaining_battles);

        loop {
            let maybe_next_battle = remaining_battles.last();
            if maybe_next_battle.is_none() {
                break;
            }

            let next_battle = *maybe_next_battle.unwrap();
            self.resolve_battle(is_monkey, next_battle, &mut remaining_battles);
            remaining_battles.retain(|&x| x != next_battle);
        }

        // Restore jokers
        self.restore_joker_strengths();
    }

    fn move_card(&mut self, is_monkey: bool, dice_roll: i8, pile_index: u8, card_index: u8, remaining_battles: &mut Vec<u8>) {
        let new_pile_index = Self::new_pile_index(is_monkey, dice_roll, pile_index);
        let old_pile_height = self.get_height(is_monkey, pile_index);
        let new_pile_starting_height = self.get_height(is_monkey, new_pile_index);

        for old_index in card_index..old_pile_height {
            let card = self.get_card(is_monkey, pile_index, old_index);
            let new_card_index = new_pile_starting_height + old_index - card_index;

            self.set_card(is_monkey, new_pile_index, new_card_index, card);
            self.set_card(is_monkey, pile_index, old_index, cards::NULL);
        }

        self.set_height(is_monkey, pile_index, card_index);
        self.set_height(is_monkey, new_pile_index, new_pile_starting_height + old_pile_height - card_index);

        // Add the new_pile_index to the list of battles to be resolved
        remaining_battles.push(new_pile_index)
    }

    pub fn victorious_team(&self) -> u8 {
        if self.monkey_heights[10] > 0 {
            assert_eq!(self.wolf_heights[0], 0);
            return cards::BIT_NON_NULL | cards::BIT_TEAM_MONKEY
        }
        if self.wolf_heights[0] > 0 {
            return cards::BIT_NON_NULL | cards::BIT_TEAM_WOLF
        }

        let monkey_alive = self.monkey_heights.iter().any(|&x| x > 0);
        let wolf_alive = self.monkey_heights.iter().any(|&x| x > 0);

        if monkey_alive {
            if wolf_alive {
                cards::NULL
            }
            else {
                cards::BIT_NON_NULL | cards::BIT_TEAM_MONKEY
            }
        }
        else {
            if wolf_alive {
                cards::BIT_NON_NULL | cards::BIT_TEAM_WOLF
            }
            else {
                cards::NULL
            }
        }
    }

    pub fn gather_all_moves(&self, is_monkey: bool, dice_rolls: &[DiceRoll; 3]) -> Vec<CompletedMoves> {
        let mut completed_moves = Vec::new();
        let initial_states = vec![CompletedMoves { moves: Vec::new(), board: self.clone() }];

        for a in 0..dice_rolls.len() {
            let mut new_moves_a = Self::gather_moves_for_dice_roll(
                &initial_states,
                is_monkey,
                dice_rolls[a].category,
                dice_rolls[a].roll
            );

            for b in 0..dice_rolls.len() {
                if a == b {
                    continue
                }

                let mut new_moves_b = Self::gather_moves_for_dice_roll(
                    &new_moves_a,
                    is_monkey,
                    dice_rolls[b].category,
                    dice_rolls[b].roll
                );

                for c in 0..dice_rolls.len() {
                    if a == c || b == c {
                        continue
                    }

                    let mut new_moves_c = Self::gather_moves_for_dice_roll(
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
        let mut options = Vec::new();

        for initial_state in initial_states {
            if initial_state.board.victorious_team() != cards::NULL {
                continue
            }

            let movable_card_locations = initial_state.board.moveable_card_indices(
                is_monkey, dice_category, initial_state.used_joker()
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

                let new_state = CompletedMoves { moves, board };
                options.push(new_state);
            }
        }

        options
    }

    fn moveable_card_indices(&self, is_monkey: bool, category: u8, used_joker: bool) -> Vec<CardLocation> {
        let mut card_locations = Vec::new();
        let heights = if is_monkey { self.monkey_heights } else { self.wolf_heights };
        let cards = if is_monkey { self.monkey_cards } else { self.wolf_cards };

        for pile_index in 0..heights.len() {
            let pile_height = heights[pile_index] as i8;
            let accessible_start = std::cmp::max(0, pile_height - 3);

            for card_index_i32 in accessible_start..pile_height {
                let card_index = card_index_i32 as usize;
                let card = cards[pile_index * 10 + card_index];
                let card_category = card & cards::CHECK_CATEGORY;
                if card_category == category || (card_category == cards::BITS_CATEGORY_JOKER && !used_joker) {
                    card_locations.push(CardLocation{
                        pile_index: pile_index as u8,
                        card_index: card_index as u8
                    })
                }
            }
        }

        card_locations
    }

    fn new_pile_index(is_monkey: bool, dice_roll: i8, pile_index: u8) -> u8 {
        let unsnapped_index: Option<u8>;
        if is_monkey {
            if dice_roll >= 0 {
                unsnapped_index = Some(pile_index + (dice_roll as u8));
            }
            else {
                unsnapped_index = Some(pile_index - ((-dice_roll) as u8));
            }
        }
        else {
            if dice_roll >= 0 {
                unsnapped_index = Some(pile_index - (dice_roll as u8));
            }
            else {
                unsnapped_index = Some(pile_index + (-dice_roll as u8));
            }
        }

        std::cmp::min(10, std::cmp::max(0, unsnapped_index.unwrap()))
    }

    fn resolve_battle(&mut self, is_monkey: bool, battle_index: u8, remaining_battles: &mut Vec<u8>) {
        loop {
            let monkey_height = self.get_height(true, battle_index);
            let wolf_height = self.get_height(false, battle_index);

            if monkey_height == 0 || wolf_height == 0 {
                break
            }

            let monkey_card_index = monkey_height - 1;
            let wolf_card_index = wolf_height - 1;

            let monkey_card = self.get_card(true, battle_index, monkey_card_index);
            let wolf_card = self.get_card(false, battle_index, wolf_card_index);

            let battle_result = card::battle_winner(monkey_card, wolf_card);
            self.set_card(true, battle_index, monkey_card_index, battle_result.card_a_residual);
            self.set_card(false, battle_index, wolf_card_index, battle_result.card_b_residual);

            if battle_result.winner == cards::NULL {
                self.resolve_draw(is_monkey, battle_index, monkey_card_index, wolf_card_index, remaining_battles)
            }
            else if battle_result.winner == monkey_card {
                self.set_height(false, battle_index, wolf_card_index)
            }
            else if battle_result.winner == wolf_card {
                self.set_height(true, battle_index, monkey_card_index)
            }
            else {
                panic!("Unexpected battle_result winner")
            }
        }
    }

    fn resolve_draw(
        &mut self,
        is_monkey: bool,
        battle_index: u8,
        monkey_card_index: u8,
        wolf_card_index: u8,
        remaining_battles: &mut Vec<u8>
    ) {
        if is_monkey {
            if battle_index == 10 {
                self.set_card(false, battle_index, wolf_card_index, cards::NULL);
                self.set_height(false, battle_index, wolf_card_index);
            }
            else {
                self.move_card(false, -1, battle_index, wolf_card_index, remaining_battles);
                self.move_card(true, -1, battle_index, monkey_card_index, remaining_battles);
            }
        }
        else {
            if battle_index == 0 {
                self.set_card(true, battle_index, monkey_card_index, cards::NULL);
                self.set_height(true, battle_index, monkey_card_index);
            }
            else {
                self.move_card(true, -1, battle_index, monkey_card_index, remaining_battles);
                self.move_card(false, -1, battle_index, wolf_card_index, remaining_battles);
            }
        }
    }

    fn restore_joker_strengths(&mut self) {
        for i in 0..self.monkey_cards.len() {
            if (self.monkey_cards[i] & cards::CHECK_CATEGORY) == cards::BITS_CATEGORY_JOKER
            {
                self.monkey_cards[i] = cards::MJ4
            }
        }
        for i in 0..self.wolf_cards.len() {
            if (self.wolf_cards[i] & cards::CHECK_CATEGORY) == cards::BITS_CATEGORY_JOKER
            {
                self.wolf_cards[i] = cards::WJ4
            }
        }
    }

    fn get_height(&self, is_monkey: bool, pile_index: u8) -> u8 {
        if is_monkey {
            self.monkey_heights[pile_index as usize]
        }
        else {
            self.wolf_heights[pile_index as usize]
        }
    }

    fn set_height(&mut self, is_monkey: bool, pile_index: u8, height: u8) {
        if is_monkey {
            self.monkey_heights[pile_index as usize] = height
        }
        else {
            self.wolf_heights[pile_index as usize] = height
        }
    }

    fn get_card(&self, is_monkey: bool, pile_index: u8, card_index: u8) -> u8 {
        let index = pile_index * 10 + card_index;
        if is_monkey {
            self.monkey_cards[index as usize]
        }
        else {
            self.wolf_cards[index as usize]
        }
    }

    fn set_card(&mut self, is_monkey: bool, pile_index: u8, card_index: u8, card: u8) {
        let index = pile_index * 10 + card_index;
        if is_monkey {
            self.monkey_cards[index as usize] = card
        }
        else {
            self.wolf_cards[index as usize] = card
        }
    }
}

#[cfg(test)]
mod tests {
    use std::collections::HashSet;
    use rand::prelude::StdRng;
    use rand::SeedableRng;
    use crate::board::Board;
    use crate::board::card::cards;

    #[test]
    fn test_new_board() {
        for seed in 42..45 {
            let mut rnd = StdRng::seed_from_u64(seed);
            let original = Board::new(&mut rnd);
            let cloned = original.clone();

            for board in [original, cloned] {
                assert_eq!(board.monkey_heights, [4, 3, 2, 1, 0, 0, 0, 0, 0, 0, 0]);
                assert_eq!(board.wolf_heights, [0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4]);
                assert_eq!(board.monkey_cards[0], cards::MJ4);
                assert_eq!(board.wolf_cards[100], cards::WJ4);
                assert_eq!(board.monkey_cards.len(), 110);
                assert_eq!(board.wolf_cards.len(), 110);

                {
                    let monkey_indices: [usize; 10] = [0, 1, 2, 3, 10, 11, 12, 20, 21, 30];
                    let monkey_cards = [
                        cards::MJ4,
                        cards::MR1, cards::MR2, cards::MR3,
                        cards::MP1, cards::MP2, cards::MP3,
                        cards::MS1, cards::MS2, cards::MS3
                    ];
                    let mut seen_monkey_cards = HashSet::new();
                    for i in 0..board.monkey_cards.len() {
                        let card = board.monkey_cards[i];
                        if monkey_indices.contains(&i) {
                            assert_ne!(cards::NULL, card);
                            assert!(monkey_cards.contains(&card));
                            assert!(!seen_monkey_cards.contains(&card));
                            seen_monkey_cards.insert(card);
                        }
                        else {
                            assert_eq!(cards::NULL, board.monkey_cards[i]);
                        }
                    }
                }

                {
                    let wolf_indices: [usize; 10] = [100, 101, 102, 103, 90, 91, 92, 80, 81, 70];
                    let wolf_cards = [
                        cards::WJ4,
                        cards::WR1, cards::WR2, cards::WR3,
                        cards::WP1, cards::WP2, cards::WP3,
                        cards::WS1, cards::WS2, cards::WS3
                    ];
                    let mut seen_wolf_cards = HashSet::new();
                    for i in 0..board.wolf_cards.len() {
                        let card = board.wolf_cards[i];
                        if wolf_indices.contains(&i) {
                            assert_ne!(cards::NULL, card);
                            assert!(wolf_cards.contains(&card));
                            assert!(!seen_wolf_cards.contains(&card));
                            seen_wolf_cards.insert(card);
                        }
                        else {
                            assert_eq!(cards::NULL, board.wolf_cards[i]);
                        }
                    }
                }
            }
        }
    }

    #[test]
    fn test_complex_battle() {
        let mut board = Board{
            monkey_cards: [cards::NULL; 110],
            wolf_cards: [cards::NULL; 110],
            monkey_heights: [0, 1, 0, 0, 2, 3, 0, 0, 0, 0, 0],
            wolf_heights: [0, 0, 0, 0, 0, 0, 2, 1, 1, 1, 0],
        };

        board.set_card(true, 1, 0, cards::MS2);
        board.set_card(true, 4, 0, cards::MP2);
        board.set_card(true, 4, 1, cards::MJ4);
        board.set_card(true, 5, 0, cards::MR2);
        board.set_card(true, 5, 1, cards::MS1);
        board.set_card(true, 5, 2, cards::MS3);

        board.set_card(false, 6, 0, cards::WS1);
        board.set_card(false, 6, 1, cards::WP1);
        board.set_card(false, 7, 0, cards::WJ4);
        board.set_card(false, 8, 0, cards::WR3);
        board.set_card(false, 9, 0, cards::WP3);

        board.move_card_and_resolve_battles(true, 2, 5, 0);

        assert_eq!(board.monkey_heights, [0, 1, 0, 0, 2, 1, 0, 1, 0, 0, 0]);
        assert_eq!(board.wolf_heights,   [0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 0]);

        assert_eq!(cards::MS2, board.get_card(true, 1, 0));
        assert_eq!(cards::MP2, board.get_card(true, 4, 0));
        assert_eq!(cards::MJ4, board.get_card(true, 4, 1));
        assert_eq!(cards::MS1, board.get_card(true, 5, 0));
        assert_eq!(cards::MR2, board.get_card(true, 7, 0));

        assert_eq!(cards::WR3, board.get_card(false, 8, 0));
        assert_eq!(cards::WJ4, board.get_card(false, 8, 1));
        assert_eq!(cards::WP3, board.get_card(false, 9, 0));
    }
}
