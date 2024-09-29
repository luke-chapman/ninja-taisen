use crate::simulator::cards::ZERO_STRENGTH;

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

    if card_a_category == cards::CATEGORY_JOKER && card_b_category == cards::CATEGORY_JOKER {
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
    } else if card_a_category == cards::CATEGORY_JOKER {
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
                card_a_residual: card_a & ZERO_STRENGTH,
                card_b_residual: card_b
            }
        }
    }
    if card_b_category == cards::CATEGORY_JOKER {
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
        if card_a_strength > card_b_strength {
            return BattleResult {
                winning_team: card_a_team,
                card_a_residual: card_a,
                card_b_residual: cards::NULL,
            }
        } else if card_a_strength < card_b_strength
        {
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

struct Board {
    cards: [Card; 220]
}
