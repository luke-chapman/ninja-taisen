from ninja_taisen.objects.types import Card, Category, Team


def MR1() -> Card:
    return Card(Team.monkey, Category.rock, 1)


def MR2() -> Card:
    return Card(Team.monkey, Category.rock, 2)


def MR3() -> Card:
    return Card(Team.monkey, Category.rock, 3)


def MP1() -> Card:
    return Card(Team.monkey, Category.paper, 1)


def MP2() -> Card:
    return Card(Team.monkey, Category.paper, 2)


def MP3() -> Card:
    return Card(Team.monkey, Category.paper, 3)


def MS1() -> Card:
    return Card(Team.monkey, Category.scissors, 1)


def MS2() -> Card:
    return Card(Team.monkey, Category.scissors, 2)


def MS3() -> Card:
    return Card(Team.monkey, Category.scissors, 3)


def MJ4() -> Card:
    return Card(Team.monkey, Category.joker, 4)


def WR1() -> Card:
    return Card(Team.wolf, Category.rock, 1)


def WR2() -> Card:
    return Card(Team.wolf, Category.rock, 2)


def WR3() -> Card:
    return Card(Team.wolf, Category.rock, 3)


def WP1() -> Card:
    return Card(Team.wolf, Category.paper, 1)


def WP2() -> Card:
    return Card(Team.wolf, Category.paper, 2)


def WP3() -> Card:
    return Card(Team.wolf, Category.paper, 3)


def WS1() -> Card:
    return Card(Team.wolf, Category.scissors, 1)


def WS2() -> Card:
    return Card(Team.wolf, Category.scissors, 2)


def WS3() -> Card:
    return Card(Team.wolf, Category.scissors, 3)


def WJ4() -> Card:
    return Card(Team.wolf, Category.joker, 4)
