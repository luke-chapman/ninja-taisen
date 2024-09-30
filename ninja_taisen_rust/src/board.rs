mod card;
mod dice;

use rand::prelude::SliceRandom;
use rand::Rng;

use crate::board::card::cards;

pub struct Board {
    monkey_cards: [u8; 110],
    wolf_cards: [u8; 110],
    monkey_heights: [u8; 11],
    wolf_heights: [u8; 11]
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
        let mut remaining_battles: Vec<u8> = Vec::new();
        self.move_card(is_monkey, dice_roll, pile_index, card_index, &mut remaining_battles);

        loop {
            let remaining_battle = remaining_battles.pop();
            if remaining_battle.is_none() {
                break;
            }

            self.resolve_battle(is_monkey, remaining_battle.unwrap(), &mut remaining_battles)
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

    fn new_pile_index(is_monkey: bool, dice_roll: i8, pile_index: u8) -> u8 {
        let mut unsnapped_index: Option<u8> = None;
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

            let monkey_pile = monkey_height - 1;
            let wolf_pile = wolf_height - 1;

            let monkey_card = self.get_card(true, battle_index, monkey_pile);
            let wolf_card = self.get_card(false, battle_index, wolf_pile);

            let battle_result = card::battle_winner(monkey_card, wolf_card);
            self.set_card(true, battle_index, monkey_pile, monkey_card);
            self.set_card(false, battle_index, wolf_pile, wolf_card);

            match battle_result.winning_team {
                cards::NULL => {
                    self.resolve_draw(is_monkey, battle_index, monkey_pile, wolf_pile, remaining_battles)
                }
                cards::TEAM_MONKEY => {
                    self.set_height(false, battle_index, wolf_height - 1);
                }
                cards::TEAM_WOLF => {
                    self.set_height(true, battle_index, monkey_height - 1);
                }
                _ => panic!("Unexpected winning_team")
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
            if self.monkey_cards[i] & cards::CHECK_CATEGORY == cards::CATEGORY_JOKER
            {
                self.monkey_cards[i] = cards::MJ4
            }
        }
        for i in 0..self.wolf_cards.len() {
            if self.wolf_cards[i] & cards::CHECK_CATEGORY == cards::CATEGORY_JOKER
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
