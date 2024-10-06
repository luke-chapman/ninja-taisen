use crate::card::cards;

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
        match card_a_category {
            cards::BITS_CATEGORY_ROCK => {
                match card_b_category {
                    cards::BITS_CATEGORY_PAPER => {
                        return BattleResult {
                            winner: card_b,
                            card_a_residual: cards::NULL,
                            card_b_residual: card_b
                        }
                    }
                    cards::BITS_CATEGORY_SCISSORS => {
                        return BattleResult {
                            winner: card_a,
                            card_a_residual: card_a,
                            card_b_residual: cards::NULL
                        }
                    }
                    _ => panic!("Unexpected category")
                }
            }
            cards::BITS_CATEGORY_PAPER => {
                match card_b_category {
                    cards::BITS_CATEGORY_SCISSORS => {
                        return BattleResult {
                            winner: card_b,
                            card_a_residual: cards::NULL,
                            card_b_residual: card_b
                        }
                    }
                    cards::BITS_CATEGORY_ROCK => {
                        return BattleResult {
                            winner: card_a,
                            card_a_residual: card_a,
                            card_b_residual: cards::NULL
                        }
                    }
                    _ => panic!("Unexpected category")
                }
            }
            cards::BITS_CATEGORY_SCISSORS => {
                match card_b_category {
                    cards::BITS_CATEGORY_ROCK => {
                        return BattleResult {
                            winner: card_b,
                            card_a_residual: cards::NULL,
                            card_b_residual: card_b
                        }
                    }
                    cards::BITS_CATEGORY_PAPER => {
                        return BattleResult {
                            winner: card_a,
                            card_a_residual: card_a,
                            card_b_residual: cards::NULL
                        }
                    }
                    _ => panic!("Unexpected category")
                }
            }
            _ => panic!("Unexpected category")
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
    use crate::battle::battle_winner;
    use crate::card::cards;

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
    fn test_rock_paper_scissors_4() {
        let card_a = cards::MR2;
        let card_b = cards::WS1;
        let result = battle_winner(card_a, card_b);

        assert_eq!(card_a, result.winner);
        assert_eq!(card_a, result.card_a_residual);
        assert_eq!(cards::NULL, result.card_b_residual);
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
    fn test_strength_win_1() {
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
