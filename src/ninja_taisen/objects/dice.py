from random import choice

FACES = [1, 1, 1, 2, 2, 3]


def roll() -> int:
    return choice(FACES)
