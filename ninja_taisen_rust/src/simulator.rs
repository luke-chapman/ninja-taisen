use rand::Rng;
use rand::seq::SliceRandom;

// We represent each card as a byte, i.e. in the range 0-255
// The encoding for each of the bits is as follows:
// 0:        0=null, 1=non-null
// 1:        0=monkey, 1=wolf
// 2,3:      [0,0]=rock, [0,1]=paper, [1,0]=scissors, [1,1]=joker
// 4,5,6,7:  [0,0,0,1]=1, [0,0,1,0]=2, [0,0,1,1]=3, [0,1,0,0]=4 (encodes strength)
//
// Of the 255 available values, the 29 we expect to use are detailed in the below enum
mod cards {
    pub const NULL: u8 = 0b0_0_00_0000;

    pub const MR1: u8 = 0b1_0_00_0001;
    pub const MR2: u8 = 0b1_0_00_0010;
    pub const MR3: u8 = 0b1_0_00_0011;

    pub const MP1: u8 = 0b1_0_01_0001;
    pub const MP2: u8 = 0b1_0_01_0010;
    pub const MP3: u8 = 0b1_0_01_0011;

    pub const MS1: u8 = 0b1_0_10_0001;
    pub const MS2: u8 = 0b1_0_10_0010;
    pub const MS3: u8 = 0b1_0_10_0011;

    pub const MJ0: u8 = 0b1_0_11_0000;
    pub const MJ1: u8 = 0b1_0_11_0001;
    pub const MJ2: u8 = 0b1_0_11_0010;
    pub const MJ3: u8 = 0b1_0_11_0011;
    pub const MJ4: u8 = 0b1_0_11_0100;

    pub const WR1: u8 = 0b1_1_00_0001;
    pub const WR2: u8 = 0b1_1_00_0010;
    pub const WR3: u8 = 0b1_1_00_0011;

    pub const WP1: u8 = 0b1_1_01_0001;
    pub const WP2: u8 = 0b1_1_01_0010;
    pub const WP3: u8 = 0b1_1_01_0011;

    pub const WS1: u8 = 0b1_1_10_0001;
    pub const WS2: u8 = 0b1_1_10_0010;
    pub const WS3: u8 = 0b1_1_10_0011;

    pub const WJ0: u8 = 0b1_1_11_0000;
    pub const WJ1: u8 = 0b1_1_11_0001;
    pub const WJ2: u8 = 0b1_1_11_0010;
    pub const WJ3: u8 = 0b1_1_11_0011;
    pub const WJ4: u8 = 0b1_1_11_0100;

    pub const CHECK_CATEGORY: u8 = 0b0_0_11_0000;
    pub const CHECK_STRENGTH: u8 = 0b0_0_00_1111;
    pub const CHECK_TEAM: u8 = 0b0_1_00_0000;

    pub const NON_NULL: u8 = 0b1_0_00_0000;

    pub const CATEGORY_ROCK: u8 = 0b0_0_00_0000;
    pub const CATEGORY_PAPER: u8 = 0b0_0_01_0000;
    pub const CATEGORY_SCISSORS: u8 = 0b0_0_10_0000;
    pub const CATEGORY_JOKER: u8 = 0b0_0_11_0000;

    pub const ZERO_STRENGTH: u8 = 0b1_1_11_0000;
}

pub struct BattleResult {
    pub winning_team: u8,
    pub card_a_residual: u8,
    pub card_b_residual: u8
}

fn battle_winner(card_a: u8, card_b: u8) -> BattleResult {
    let card_a_category = card_a & cards::CHECK_CATEGORY;
    let card_b_category = card_b & cards::CHECK_CATEGORY;

    let card_a_strength = card_a & cards::CHECK_STRENGTH;
    let card_b_strength = card_b & cards::CHECK_STRENGTH;

    let card_a_team = card_a & cards::CHECK_TEAM;
    let card_b_team = card_b & cards::CHECK_TEAM;

    if card_a_category == cards::CATEGORY_JOKER {
        // joker vs joker
        if card_b_category == cards::CATEGORY_JOKER {
            if card_a_strength > card_b_strength {
                return BattleResult {
                    winning_team: card_a_team,
                    card_a_residual: cards::NON_NULL | card_a_team | card_a_category | (card_a_strength - card_b_strength),
                    card_b_residual: cards::NULL
                }
            } else if card_a_strength < card_b_strength {
                return BattleResult {
                    winning_team: card_b_team,
                    card_a_residual: cards::NULL,
                    card_b_residual: cards::NON_NULL | card_b_team | card_b_category | (card_b_strength - card_a_strength)
                }
            } else {
                return BattleResult {
                    winning_team: cards::NULL,
                    card_a_residual: card_a & cards::ZERO_STRENGTH,
                    card_b_residual: card_b & cards::ZERO_STRENGTH
                }
            }
        }
        // joker vs joker non-joker
        else {
            if card_a_strength > card_b_strength {
                return BattleResult {
                    winning_team: card_a_team,
                    card_a_residual: cards::NON_NULL | card_a_team | card_a_category | (card_a_strength - card_b_strength),
                    card_b_residual: cards::NULL
                }
            } else if card_a_strength < card_b_strength {
                return BattleResult {
                    winning_team: card_b_team,
                    card_a_residual: cards::NULL,
                    card_b_residual: card_b
                }
            } else {
                return BattleResult {
                    winning_team: cards::NULL,
                    card_a_residual: card_a & cards::ZERO_STRENGTH,
                    card_b_residual: card_b
                }
            }
        }
    }
    else if card_b_category == cards::CATEGORY_JOKER {
        // non-joker vs joker
        if card_a_strength > card_b_strength {
            return BattleResult {
                winning_team: card_a_team,
                card_a_residual: card_a,
                card_b_residual: cards::NULL
            }
        } else if card_a_strength < card_b_strength {
            return BattleResult {
                winning_team: card_b_team,
                card_a_residual: cards::NULL,
                card_b_residual: cards::NON_NULL | card_b_team | card_b_category | (card_b_strength - card_a_strength)
            }
        } else {
            return BattleResult {
                winning_team: cards::NULL,
                card_a_residual: card_a,
                card_b_residual: card_b & cards::ZERO_STRENGTH
            }
        }
    }
    else if card_a_category != card_b_category {
        // rock-paper-scissors battle. rock=0, paper=1, scissors=2
        let card_a_wins = ((card_a_category - card_b_category) % 3) == 1;
        if card_a_wins {
            return BattleResult {
                winning_team: card_a_team,
                card_a_residual: card_a,
                card_b_residual: cards::NULL
            }
        } else {
            return BattleResult {
                winning_team: card_b_team,
                card_a_residual: cards::NULL,
                card_b_residual: card_b
            }
        }
    }
    else {
        // same category; strength battle
        if card_a_strength > card_b_strength {
            return BattleResult {
                winning_team: card_a_team,
                card_a_residual: card_a,
                card_b_residual: cards::NULL,
            }
        } else if card_a_strength < card_b_strength {
            return BattleResult {
                winning_team: card_b_team,
                card_a_residual: cards::NULL,
                card_b_residual: card_b,
            }
        } else {
            return BattleResult {
                winning_team: cards::NULL,
                card_a_residual: card_a,
                card_b_residual: card_b,
            }
        }
    }
}

static DICE_FACES: [u8; 6] = [1, 1, 1, 2, 2, 3];

fn roll_dice(mut rng: &rand::rngs::StdRng) -> u8 {
    let roll = DICE_FACES.choose(&mut rng);
    if roll.is_some() {
        *roll
    }
    else {
        panic!("Dice roll was null - this should not happen")
    }
}

struct Board {
    monkey_cards: [u8; 110],
    wolf_cards: [u8; 110],
    monkey_heights: [u8; 11],
    wolf_heights: [u8; 11]
}

impl Board {
    fn get_height(&self, is_monkey: bool, pile_index: u8) -> u8 {
        if is_monkey {
            self.monkey_heights[pile_index]
        }
        else {
            self.wolf_heights[pile_index]
        }
    }

    fn set_height(&mut self, is_monkey: bool, pile_index: u8, height: u8) {
        if is_monkey {
            self.monkey_heights[pile_index] = height
        }
        else {
            self.wolf_heights[pile_index] = height
        }
    }

    fn get_card(&self, is_monkey: bool, pile_index: u8, card_index: u8) -> u8 {
        let index = pile_index * 10 + card_index;
        if is_monkey {
            self.monkey_cards[index]
        }
        else {
            self.wolf_cards[index]
        }
    }

    fn set_card(&mut self, is_monkey: bool, pile_index: u8, card_index: u8, card: u8) {
        let index = pile_index * 10 + card_index;
        if is_monkey {
            self.monkey_cards[index] = card
        }
        else {
            self.wolf_cards[index] = card
        }
    }

    fn new(mut rng: &rand::rngs::StdRng) -> Self {
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
        monkey.shuffle(&mut rng);
        wolf.shuffle(&mut rng);

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

        Board {
            monkey_cards,
            monkey_heights: [4, 3, 2, 1, 0, 0, 0, 0, 0, 0, 0],
            wolf_cards,
            wolf_heights: [0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4]
        }
    }

    fn clone(&self) -> Self {
        Board {
            monkey_cards: self.monkey_cards.clone(),
            monkey_heights: self.monkey_heights.clone(),
            wolf_cards: self.wolf_cards.clone(),
            wolf_heights: self.wolf_heights.clone()
        }
    }
}

struct CardMover {
    board: Board,
    remaining_battles: Vec<u8>
}

impl CardMover {
    pub fn move_card_and_resolve_battles(&mut self, is_monkey: bool, dice_roll: u8, pile_index: u8, card_index: u8) {
        self.move_card(is_monkey, dice_roll, pile_index, card_index);

        while !self.remaining_battles.is_empty() {
            // Resolve battle!
        }

        // Restore jokers
    }

    fn move_card(&mut self, is_monkey: bool, dice_roll: u8, pile_index: u8, card_index: u8) {
        let new_pile_index = Self::new_pile_index(is_monkey, dice_roll, pile_index);
        let old_pile_height = self.board.get_height(is_monkey, pile_index);
        let new_pile_starting_height = self.board.get_height(is_monkey, new_pile_index);

        for old_index in card_index..old_pile_height {
            let card = self.board.get_card(is_monkey, pile_index, old_index);
            let new_card_index = new_pile_starting_height + old_index - card_index;

            self.board.set_card(is_monkey, new_pile_index, new_card_index, card);
            self.board.set_card(is_monkey, pile_index, old_index, cards::NULL);
        }

        self.board.set_height(is_monkey, pile_index, card_index);
        self.board.set_height(is_monkey, new_pile_index, new_pile_starting_height + old_pile_height - card_index);

        // Schedule this one battle to start with
        self.remaining_battles.push(new_pile_index)
    }

    fn new_pile_index(is_monkey: bool, dice_roll: u8, pile_index: u8) -> u8 {
        let new_pile_index = if is_monkey { pile_index + dice_roll } else { pile_index - dice_roll };
        std::cmp::min(10, std::cmp::max(0, new_pile_index))
    }
}
