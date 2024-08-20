from ninja_taisen.algos import card_battle
from ninja_taisen.dtos import CardDto, CategoryDto, TeamDto


def test_battle_draws() -> None:
    assert_battle_draw(CategoryDto.rock, 1)
    assert_battle_draw(CategoryDto.paper, 2)
    assert_battle_draw(CategoryDto.scissors, 3)
    assert_battle_draw(CategoryDto.joker, 4)


def test_rock_paper_scissors_wins() -> None:
    monkey_rocks = [
        CardDto(team=TeamDto.monkey, category=CategoryDto.rock, strength=1),
        CardDto(team=TeamDto.monkey, category=CategoryDto.rock, strength=2),
        CardDto(team=TeamDto.monkey, category=CategoryDto.rock, strength=3),
    ]

    wolf_papers = [
        CardDto(team=TeamDto.wolf, category=CategoryDto.paper, strength=1),
        CardDto(team=TeamDto.wolf, category=CategoryDto.paper, strength=2),
        CardDto(team=TeamDto.wolf, category=CategoryDto.paper, strength=3),
    ]

    wolf_scissorss = [
        CardDto(team=TeamDto.wolf, category=CategoryDto.scissors, strength=1),
        CardDto(team=TeamDto.wolf, category=CategoryDto.scissors, strength=2),
        CardDto(team=TeamDto.wolf, category=CategoryDto.scissors, strength=3),
    ]

    for monkey_rock in monkey_rocks:
        for wolf_paper in wolf_papers:
            assert_battle_winner(wolf_paper, monkey_rock)

        for wolf_scissors in wolf_scissorss:
            assert_battle_winner(monkey_rock, wolf_scissors)


def test_strength_wins() -> None:
    for category in [
        CategoryDto.rock,
        CategoryDto.paper,
        CategoryDto.scissors,
    ]:
        M1 = CardDto(team=TeamDto.monkey, category=category, strength=1)
        M2 = CardDto(team=TeamDto.monkey, category=category, strength=2)
        M3 = CardDto(team=TeamDto.monkey, category=category, strength=3)

        W1 = CardDto(team=TeamDto.wolf, category=category, strength=1)
        W2 = CardDto(team=TeamDto.wolf, category=category, strength=2)
        W3 = CardDto(team=TeamDto.wolf, category=category, strength=3)

        assert_battle_winner(M2, W1)
        assert_battle_winner(M3, W1)
        assert_battle_winner(M3, W2)

        assert_battle_winner(W2, M1)
        assert_battle_winner(W3, M1)
        assert_battle_winner(W3, M2)


def test_joker_nonjoker_battles() -> None:
    MJ4 = CardDto(team=TeamDto.monkey, category=CategoryDto.joker, strength=4)
    WP3 = CardDto(team=TeamDto.wolf, category=CategoryDto.paper, strength=3)
    assert_battle_winner(MJ4, WP3)
    assert MJ4.strength == 1

    WS1 = CardDto(team=TeamDto.wolf, category=CategoryDto.scissors, strength=1)
    assert not card_battle.battle_winner(MJ4, WS1)
    assert MJ4.strength == 0

    WR2 = CardDto(team=TeamDto.wolf, category=CategoryDto.rock, strength=2)
    assert_battle_winner(WR2, MJ4)


def test_joker_joker_draws() -> None:
    for joker_strength in range(0, 4):
        MJ = CardDto(team=TeamDto.monkey, category=CategoryDto.joker, strength=joker_strength)
        WJ = CardDto(team=TeamDto.wolf, category=CategoryDto.joker, strength=joker_strength)
        assert not card_battle.battle_winner(MJ, WJ)
        assert MJ.strength == 0
        assert WJ.strength == 0


def test_joker_joker_wins() -> None:
    MJ = CardDto(team=TeamDto.monkey, category=CategoryDto.joker, strength=4)
    WJ2 = CardDto(team=TeamDto.wolf, category=CategoryDto.joker, strength=1)
    winner_a = card_battle.battle_winner(MJ, WJ2)
    assert winner_a is not None
    assert winner_a.team == TeamDto.monkey
    assert MJ.strength == 3

    WJ1 = CardDto(team=TeamDto.wolf, category=CategoryDto.joker, strength=2)
    winner_b = card_battle.battle_winner(MJ, WJ1)
    assert winner_b is not None
    assert winner_b.team == TeamDto.monkey
    assert MJ.strength == 1


def assert_battle_draw(category: CategoryDto, strength: int) -> None:
    monkey = CardDto(team=TeamDto.monkey, category=category, strength=strength)
    wolf = CardDto(team=TeamDto.wolf, category=category, strength=strength)
    assert not card_battle.battle_winner(monkey, wolf)


def assert_battle_winner(expected_winner: CardDto, expected_loser: CardDto) -> None:
    actual_winner = card_battle.battle_winner(expected_winner, expected_loser)
    assert expected_winner == actual_winner
