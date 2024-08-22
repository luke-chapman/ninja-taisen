from ninja_taisen.objects.types import Card, Category


def MR1() -> Card:
    return Card(Category.rock, strength=1)


def MR2() -> Card:
    return Card(Category.rock, strength=2)


def MR3() -> Card:
    return Card(Category.rock, strength=3)


def MP1() -> Card:
    return Card(Category.paper, strength=1)


def MP2() -> Card:
    return Card(Category.paper, strength=2)


def MP3() -> Card:
    return Card(Category.paper, strength=3)


def MS1() -> Card:
    return Card(Category.scissors, strength=1)


def MS2() -> Card:
    return Card(Category.scissors, strength=2)


def MS3() -> Card:
    return Card(Category.scissors, strength=3)


def MJ4() -> Card:
    return Card(Category.joker, strength=4)


def WR1() -> Card:
    return Card(Category.rock, strength=1)


def WR2() -> Card:
    return Card(Category.rock, strength=2)


def WR3() -> Card:
    return Card(Category.rock, strength=3)


def WP1() -> Card:
    return Card(Category.paper, strength=1)


def WP2() -> Card:
    return Card(Category.paper, strength=2)


def WP3() -> Card:
    return Card(Category.paper, strength=3)


def WS1() -> Card:
    return Card(Category.scissors, strength=1)


def WS2() -> Card:
    return Card(Category.scissors, strength=2)


def WS3() -> Card:
    return Card(Category.scissors, strength=3)


def WJ4() -> Card:
    return Card(Category.joker, strength=4)
