import random

DICE_FACES = [1, 1, 1, 2, 2, 3]


class SafeRandom(random.Random):
    def roll_dice(self):
        return self.choice(DICE_FACES)
