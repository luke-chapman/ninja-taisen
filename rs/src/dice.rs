use rand::Rng;
use crate::card::cards;

pub struct DiceRoll {
    pub category: u8,
    pub roll: i8
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
