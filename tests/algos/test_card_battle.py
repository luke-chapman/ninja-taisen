from ninja_taisen.algos import card_battle
from ninja_taisen.objects.types import BattleStatus, Card, Category


def test_battle_draws() -> None:
    assert_battle_draw(Category.rock, 1)
    assert_battle_draw(Category.paper, 2)
    assert_battle_draw(Category.scissors, 3)
    assert_battle_draw(Category.joker, 0)
    assert_battle_draw(Category.joker, 1)
    assert_battle_draw(Category.joker, 2)
    assert_battle_draw(Category.joker, 3)
    assert_battle_draw(Category.joker, 4)


def test_rock_paper_scissors_wins() -> None:
    monkey_rocks = [
        Card(category=Category.rock, strength=1),
        Card(category=Category.rock, strength=2),
        Card(category=Category.rock, strength=3),
    ]

    wolf_papers = [
        Card(category=Category.paper, strength=1),
        Card(category=Category.paper, strength=2),
        Card(category=Category.paper, strength=3),
    ]

    wolf_scissorses = [
        Card(category=Category.scissors, strength=1),
        Card(category=Category.scissors, strength=2),
        Card(category=Category.scissors, strength=3),
    ]

    for monkey_rock in monkey_rocks:
        for wolf_paper in wolf_papers:
            assert_battle_winner(wolf_paper, monkey_rock)

        for wolf_scissors in wolf_scissorses:
            assert_battle_winner(monkey_rock, wolf_scissors)


def test_strength_wins() -> None:
    for category in [
        Category.rock,
        Category.paper,
        Category.scissors,
    ]:
        M1 = Card(category=category, strength=1)
        M2 = Card(category=category, strength=2)
        M3 = Card(category=category, strength=3)

        W1 = Card(category=category, strength=1)
        W2 = Card(category=category, strength=2)
        W3 = Card(category=category, strength=3)

        assert_battle_winner(M2, W1)
        assert_battle_winner(M3, W1)
        assert_battle_winner(M3, W2)

        assert_battle_winner(W2, M1)
        assert_battle_winner(W3, M1)
        assert_battle_winner(W3, M2)


def test_joker_non_joker_battles() -> None:
    MJ4 = Card(category=Category.joker, strength=4)
    WP3 = Card(category=Category.paper, strength=3)
    assert_battle_winner(MJ4, WP3)
    assert MJ4.strength == 1

    WS1 = Card(category=Category.scissors, strength=1)
    assert card_battle.battle_winner(MJ4, WS1).status == BattleStatus.draw
    assert MJ4.strength == 0

    WR2 = Card(category=Category.rock, strength=2)
    assert_battle_winner(WR2, MJ4)


def test_joker_joker_draws() -> None:
    for joker_strength in range(0, 4):
        MJ = Card(category=Category.joker, strength=joker_strength)
        WJ = Card(category=Category.joker, strength=joker_strength)
        assert card_battle.battle_winner(MJ, WJ).status == BattleStatus.draw
        assert MJ.strength == 0
        assert WJ.strength == 0


def test_joker_joker_wins() -> None:
    MJ = Card(category=Category.joker, strength=4)
    WJ2 = Card(category=Category.joker, strength=1)
    result_a = card_battle.battle_winner(MJ, WJ2)
    assert result_a.status == BattleStatus.card_a_wins
    assert result_a.winner == MJ
    assert MJ.strength == 3

    WJ1 = Card(category=Category.joker, strength=2)
    result_b = card_battle.battle_winner(WJ1, MJ)
    assert result_b.status == BattleStatus.card_b_wins
    assert result_b.winner == MJ
    assert MJ.strength == 1

    WJ4 = Card(category=Category.joker, strength=4)
    result_c = card_battle.battle_winner(MJ, WJ4)
    assert result_c.status == BattleStatus.card_b_wins
    assert result_c.winner == WJ4
    assert WJ4.strength == 3


def assert_battle_draw(category: Category, strength: int) -> None:
    monkey = Card(category=category, strength=strength)
    wolf = Card(category=category, strength=strength)
    battle_result = card_battle.battle_winner(monkey, wolf)
    assert battle_result.status == BattleStatus.draw
    assert battle_result.winner is None


def assert_battle_winner(winner: Card, loser: Card) -> None:
    winner_copy = Card(winner.category, winner.strength)
    loser_copy = Card(loser.category, loser.strength)

    battle_result_1 = card_battle.battle_winner(winner, loser)
    assert battle_result_1.status == BattleStatus.card_a_wins
    assert battle_result_1.winner == winner

    battle_result_2 = card_battle.battle_winner(loser_copy, winner_copy)
    assert battle_result_2.status == BattleStatus.card_b_wins
    assert battle_result_2.winner == winner_copy

    assert winner_copy.strength == winner.strength
    assert loser_copy.strength == loser.strength
