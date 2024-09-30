use rand::Rng;

static DICE_FACES: [i8; 6] = [1, 1, 1, 2, 2, 3];

fn roll_dice(rng: &mut rand::rngs::StdRng) -> i8 {
    DICE_FACES[rng.gen_range(0..6)]
}
