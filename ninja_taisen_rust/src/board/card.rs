// We represent each card as a byte, i.e. in the range 0-255
// The encoding for each of the bits is as follows:
// 0:        0=null, 1=non-null
// 1:        0=monkey, 1=wolf
// 2,3:      [0,0]=rock, [0,1]=paper, [1,0]=scissors, [1,1]=joker
// 4,5,6,7:  [0,0,0,1]=1, [0,0,1,0]=2, [0,0,1,1]=3, [0,1,0,0]=4 (encodes strength)
//
// Of the 255 available values, the 29 we expect to use are detailed in the below enum
pub mod cards {
    // NULL, used to indicate an empty space on the board
    pub const NULL: u8 = 0b0_0_00_0000;

    // BITs used to construct cards: NON_NULL, TEAM, CATEGORY, STRENGTH
    pub const BIT_NON_NULL: u8 = 0b1_0_00_0000;
    pub const BIT_TEAM_MONKEY: u8 = 0b0_0_00_0000;
    pub const BIT_TEAM_WOLF: u8 = 0b0_1_00_0000;

    pub const BITS_CATEGORY_ROCK: u8 = 0b0_0_00_0000;
    pub const BITS_CATEGORY_PAPER: u8 = 0b0_0_01_0000;
    pub const BITS_CATEGORY_SCISSORS: u8 = 0b0_0_10_0000;
    pub const BITS_CATEGORY_JOKER: u8 = 0b0_0_11_0000;

    pub const BITS_STRENGTH_0: u8 = 0b0_0_00_0000;
    pub const BITS_STRENGTH_1: u8 = 0b0_0_00_0001;
    pub const BITS_STRENGTH_2: u8 = 0b0_0_00_0010;
    pub const BITS_STRENGTH_3: u8 = 0b0_0_00_0011;
    pub const BITS_STRENGTH_4: u8 = 0b0_0_00_0100;

    // Monkey cards
    pub const MR1: u8 = BIT_NON_NULL | BIT_TEAM_MONKEY | BITS_CATEGORY_ROCK | BITS_STRENGTH_1;
    pub const MR2: u8 = BIT_NON_NULL | BIT_TEAM_MONKEY | BITS_CATEGORY_ROCK | BITS_STRENGTH_2;
    pub const MR3: u8 = BIT_NON_NULL | BIT_TEAM_MONKEY | BITS_CATEGORY_ROCK | BITS_STRENGTH_3;
    pub const MP1: u8 = BIT_NON_NULL | BIT_TEAM_MONKEY | BITS_CATEGORY_PAPER | BITS_STRENGTH_1;
    pub const MP2: u8 = BIT_NON_NULL | BIT_TEAM_MONKEY | BITS_CATEGORY_PAPER | BITS_STRENGTH_2;
    pub const MP3: u8 = BIT_NON_NULL | BIT_TEAM_MONKEY | BITS_CATEGORY_PAPER | BITS_STRENGTH_3;
    pub const MS1: u8 = BIT_NON_NULL | BIT_TEAM_MONKEY | BITS_CATEGORY_SCISSORS | BITS_STRENGTH_1;
    pub const MS2: u8 = BIT_NON_NULL | BIT_TEAM_MONKEY | BITS_CATEGORY_SCISSORS | BITS_STRENGTH_2;
    pub const MS3: u8 = BIT_NON_NULL | BIT_TEAM_MONKEY | BITS_CATEGORY_SCISSORS | BITS_STRENGTH_3;
    pub const MJ4: u8 = BIT_NON_NULL | BIT_TEAM_MONKEY | BITS_CATEGORY_JOKER | BITS_STRENGTH_4;

    // Wolf cards
    pub const WR1: u8 = BIT_NON_NULL | BIT_TEAM_WOLF | BITS_CATEGORY_ROCK | BITS_STRENGTH_1;
    pub const WR2: u8 = BIT_NON_NULL | BIT_TEAM_WOLF | BITS_CATEGORY_ROCK | BITS_STRENGTH_2;
    pub const WR3: u8 = BIT_NON_NULL | BIT_TEAM_WOLF | BITS_CATEGORY_ROCK | BITS_STRENGTH_3;
    pub const WP1: u8 = BIT_NON_NULL | BIT_TEAM_WOLF | BITS_CATEGORY_PAPER | BITS_STRENGTH_1;
    pub const WP2: u8 = BIT_NON_NULL | BIT_TEAM_WOLF | BITS_CATEGORY_PAPER | BITS_STRENGTH_2;
    pub const WP3: u8 = BIT_NON_NULL | BIT_TEAM_WOLF | BITS_CATEGORY_PAPER | BITS_STRENGTH_3;
    pub const WS1: u8 = BIT_NON_NULL | BIT_TEAM_WOLF | BITS_CATEGORY_SCISSORS | BITS_STRENGTH_1;
    pub const WS2: u8 = BIT_NON_NULL | BIT_TEAM_WOLF | BITS_CATEGORY_SCISSORS | BITS_STRENGTH_2;
    pub const WS3: u8 = BIT_NON_NULL | BIT_TEAM_WOLF | BITS_CATEGORY_SCISSORS | BITS_STRENGTH_3;
    pub const WJ4: u8 = BIT_NON_NULL | BIT_TEAM_WOLF | BITS_CATEGORY_JOKER | BITS_STRENGTH_4;

    // Bits to use to extra certain fields
    pub const CHECK_TEAM: u8 = 0b0_1_00_0000;
    pub const CHECK_CATEGORY: u8 = 0b0_0_11_0000;
    pub const CHECK_STRENGTH: u8 = 0b0_0_00_1111;
}

pub struct BattleResult {
    // The winner of the battle. Either NULL, or one of the original two cards
    pub winner: u8,

    // The residual value of card_a. Either
    // - NULL (dead)
    // - card_a (won and card_a not a joker)
    // - card_a with a lower strength (won but lost joker strength)
    pub card_a_residual: u8,

    // The residual value of card_b. Either
    // - NULL (dead)
    // - card_b (won and card_a not a joker)
    // - card_b with a lower strength (won but lost joker strength)
    pub card_b_residual: u8
}

pub fn battle_winner(card_a: u8, card_b: u8) -> BattleResult {
    let card_a_team = card_a & cards::CHECK_TEAM;
    let card_b_team = card_b & cards::CHECK_TEAM;

    let card_a_category = card_a & cards::CHECK_CATEGORY;
    let card_b_category = card_b & cards::CHECK_CATEGORY;

    let card_a_strength = card_a & cards::CHECK_STRENGTH;
    let card_b_strength = card_b & cards::CHECK_STRENGTH;

    if card_a_category == cards::BITS_CATEGORY_JOKER {
        // joker vs joker
        if card_b_category == cards::BITS_CATEGORY_JOKER {
            if card_a_strength > card_b_strength {
                return BattleResult {
                    winner: card_a,
                    card_a_residual: cards::BIT_NON_NULL | card_a_team | card_a_category | (card_a_strength - card_b_strength),
                    card_b_residual: cards::NULL
                }
            } else if card_a_strength < card_b_strength {
                return BattleResult {
                    winner: card_b,
                    card_a_residual: cards::NULL,
                    card_b_residual: cards::BIT_NON_NULL | card_b_team | card_b_category | (card_b_strength - card_a_strength)
                }
            } else {
                return BattleResult {
                    winner: cards::NULL,
                    card_a_residual: cards::BIT_NON_NULL | card_a_team | card_a_category | cards::BITS_STRENGTH_0,
                    card_b_residual: cards::BIT_NON_NULL | card_b_team | card_b_category | cards::BITS_STRENGTH_0
                }
            }
        }
        // joker vs non-joker
        else {
            if card_a_strength > card_b_strength {
                return BattleResult {
                    winner: card_a,
                    card_a_residual: cards::BIT_NON_NULL | card_a_team | card_a_category | (card_a_strength - card_b_strength),
                    card_b_residual: cards::NULL
                }
            } else if card_a_strength < card_b_strength {
                return BattleResult {
                    winner: card_b,
                    card_a_residual: cards::NULL,
                    card_b_residual: card_b
                }
            } else {
                return BattleResult {
                    winner: cards::NULL,
                    card_a_residual: cards::BIT_NON_NULL | card_a_team | card_a_category | cards::BITS_STRENGTH_0,
                    card_b_residual: card_b
                }
            }
        }
    }
    else if card_b_category == cards::BITS_CATEGORY_JOKER {
        // non-joker vs joker
        if card_a_strength > card_b_strength {
            return BattleResult {
                winner: card_a,
                card_a_residual: card_a,
                card_b_residual: cards::NULL
            }
        } else if card_a_strength < card_b_strength {
            return BattleResult {
                winner: card_b,
                card_a_residual: cards::NULL,
                card_b_residual: cards::BIT_NON_NULL | card_b_team | card_b_category | (card_b_strength - card_a_strength)
            }
        } else {
            return BattleResult {
                winner: cards::NULL,
                card_a_residual: card_a,
                card_b_residual: cards::BIT_NON_NULL | card_b_team | card_b_category | cards::BITS_STRENGTH_0
            }
        }
    }
    else if card_a_category != card_b_category {
        // rock-paper-scissors battle. Shift bits to the right, then we have rock=0, paper=1, scissors=2
        let category_difference = ((card_a_category >> 4) as i8) - ((card_b_category >> 4) as i8);
        let card_a_wins = (category_difference % 3) == 1;
        if card_a_wins {
            return BattleResult {
                winner: card_a,
                card_a_residual: card_a,
                card_b_residual: cards::NULL
            }
        } else {
            return BattleResult {
                winner: card_b,
                card_a_residual: cards::NULL,
                card_b_residual: card_b
            }
        }
    }
    else {
        // same category => strength battle
        if card_a_strength > card_b_strength {
            return BattleResult {
                winner: card_a,
                card_a_residual: card_a,
                card_b_residual: cards::NULL,
            }
        } else if card_a_strength < card_b_strength {
            return BattleResult {
                winner: card_b,
                card_a_residual: cards::NULL,
                card_b_residual: card_b,
            }
        } else {
            return BattleResult {
                winner: cards::NULL,
                card_a_residual: card_a,
                card_b_residual: card_b,
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use crate::board::card::{battle_winner, cards};

    #[test]
    fn test_rock_paper_scissors_1() {
        let card_a = cards::MP1;
        let card_b = cards::WS2;
        let result = battle_winner(card_a, card_b);

        assert_eq!(cards::WS2, result.winner);
        assert_eq!(cards::NULL, result.card_a_residual);
        assert_eq!(cards::WS2, result.card_b_residual);
    }

    #[test]
    fn test_rock_paper_scissors_2() {
        let card_a = cards::MR2;
        let card_b = cards::WP3;
        let result = battle_winner(card_a, card_b);

        assert_eq!(card_b, result.winner);
        assert_eq!(cards::NULL, result.card_a_residual);
        assert_eq!(card_b, result.card_b_residual);
    }

    #[test]
    fn test_rock_paper_scissors_3() {
        let card_a = cards::MS1;
        let card_b = cards::WR1;
        let result = battle_winner(card_a, card_b);

        assert_eq!(card_b, result.winner);
        assert_eq!(cards::NULL, result.card_a_residual);
        assert_eq!(card_b, result.card_b_residual);
    }

    #[test]
    fn test_strength_draw() {
        let card_a = cards::MR2;
        let card_b = cards::WR2;
        let result = battle_winner(card_a, card_b);

        assert_eq!(cards::NULL, result.winner);
        assert_eq!(card_a, result.card_a_residual);
        assert_eq!(card_b, result.card_b_residual);
    }

    #[test]
    fn test_strength_win() {
        let card_a = cards::MP3;
        let card_b = cards::WP1;
        let result = battle_winner(card_a, card_b);

        assert_eq!(card_a, result.winner);
        assert_eq!(card_a, result.card_a_residual);
        assert_eq!(cards::NULL, result.card_b_residual);
    }

    #[test]
    fn test_joker_battles_1() {
        let card_a = cards::MJ4;
        let result_1 = battle_winner(card_a, cards::WS3);

        assert_eq!(card_a, result_1.winner);
        assert_eq!(
            cards::BIT_NON_NULL | cards::BIT_TEAM_MONKEY | cards::BITS_CATEGORY_JOKER | cards::BITS_STRENGTH_1,
            result_1.card_a_residual
        );
        assert_eq!(cards::NULL, result_1.card_b_residual);

        let result_2 = battle_winner(result_1.card_a_residual, cards::WP1);
        assert_eq!(cards::NULL, result_2.winner);
        assert_eq!(
            cards::BIT_NON_NULL | cards::BIT_TEAM_MONKEY | cards::BITS_CATEGORY_JOKER | cards::BITS_STRENGTH_0,
            result_2.card_a_residual
        );
        assert_eq!(cards::WP1, result_2.card_b_residual);

        let result_3 = battle_winner(result_2.card_a_residual, cards::WJ4);
        assert_eq!(cards::WJ4, result_3.winner);
        assert_eq!(cards::NULL, result_3.card_a_residual);
        assert_eq!(cards::WJ4, result_3.card_b_residual);
    }

    #[test]
    fn test_joker_battles_2() {
        let result_a = battle_winner(cards::MJ4, cards::WJ4);
        assert_eq!(cards::NULL, result_a.winner);
        assert_eq!(
            cards::BIT_NON_NULL | cards::BIT_TEAM_MONKEY | cards::BITS_CATEGORY_JOKER | cards::BITS_STRENGTH_0,
            result_a.card_a_residual
        );
        assert_eq!(
            cards::BIT_NON_NULL | cards::BIT_TEAM_WOLF | cards::BITS_CATEGORY_JOKER | cards::BITS_STRENGTH_0,
            result_a.card_b_residual
        );

        let result_b = battle_winner(cards::MP1, result_a.card_b_residual);
        assert_eq!(cards::MP1, result_b.winner);
        assert_eq!(cards::MP1, result_b.card_a_residual);
        assert_eq!(cards::NULL, result_b.card_b_residual);
    }
}
