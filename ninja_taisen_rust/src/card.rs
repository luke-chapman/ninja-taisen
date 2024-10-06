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

pub fn from_string(card_string: &String) -> u8 {
    if card_string.len() != 3 {
        panic!("{}", format!("Invalid card_string {}, expected it to be length 3", card_string));
    }

    let mut card = cards::BIT_NON_NULL;
    let card_chars = Vec::from_iter(card_string.chars());
    match card_chars[0] {
        'M' => {
            card |= cards::BIT_TEAM_MONKEY;
        },
        'W' => {
            card |= cards::BIT_TEAM_WOLF;
        }
        _ => {
            panic!("{}", format!("Invalid card_string {}, expected index 0 to be M or W", card_string));
        }
    }

    match card_chars[1] {
        'R' => {
            card |= cards::BITS_CATEGORY_ROCK;
        }
        'P' => {
            card |= cards::BITS_CATEGORY_PAPER;
        }
        'S' => {
            card |= cards::BITS_CATEGORY_SCISSORS;
        }
        'J' => {
            card |= cards::BITS_CATEGORY_JOKER;
        }
        _ => {
            panic!("{}", format!("Invalid card string {}, expected index 1 to be R, P S or J", card_string))
        }
    }

    match card_chars[2] {
        '0' => {
            card |= cards::BITS_STRENGTH_0;
        }
        '1' => {
            card |= cards::BITS_STRENGTH_1;
        }
        '2' => {
            card |= cards::BITS_STRENGTH_2;
        }
        '3' => {
            card |= cards::BITS_STRENGTH_3;
        }
        '4' => {
            card |= cards::BITS_STRENGTH_4;
        }
        _ => {
            panic!("{}", format!("Invalid card string {}, expected index 2 to be in [0,1,2,3,4]", card_string))
        }
    }

    card
}

pub fn to_string(card_u8: u8) -> String {
    let mut components: Vec<char> = Vec::new();

    match card_u8 & cards::CHECK_TEAM {
        cards::BIT_TEAM_MONKEY => {
            components.push('M');
        }
        cards::BIT_TEAM_WOLF => {
            components.push('W');
        }
        _ => {
            panic!("{}", format!("Unexpected card {}, cannot determine team", card_u8));
        }
    }

    match card_u8 & cards::CHECK_CATEGORY {
        cards::BITS_CATEGORY_ROCK => {
            components.push('R');
        }
        cards::BITS_CATEGORY_PAPER => {
            components.push('P');
        }
        cards::BITS_CATEGORY_SCISSORS => {
            components.push('S');
        }
        cards::BITS_CATEGORY_JOKER => {
            components.push('J');
        }
        _ => {
            panic!("{}", format!("Unexpected card {}, cannot determine category", card_u8));
        }
    }

    match card_u8 & cards::CHECK_STRENGTH {
        cards::BITS_STRENGTH_0 => {
            components.push('0');
        }
        cards::BITS_STRENGTH_1 => {
            components.push('1');
        }
        cards::BITS_STRENGTH_2 => {
            components.push('2');
        }
        cards::BITS_STRENGTH_3 => {
            components.push('3');
        }
        cards::BITS_STRENGTH_4 => {
            components.push('4');
        }
        _ => {
            panic!("{}", format!("Unexpected card {}, cannot determine strength", card_u8))
        }
    }

    String::from_iter(components)
}
