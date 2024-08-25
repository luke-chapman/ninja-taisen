import pytest

from ninja_taisen.algos import card_battle
from ninja_taisen.objects.cards import MJ4, MP2, MR1, MR2, MR3, WJ4, WP1, WP2, WP3, WR1, WS1, WS2, WS3
from ninja_taisen.objects.types import BattleStatus, Card, Category, Team


@pytest.mark.parametrize("category", (Category.rock, Category.paper, Category.scissors))
@pytest.mark.parametrize("strength", (1, 2, 3))
def test_non_joker_draws(category: Category, strength: int) -> None:
    monkey = Card(team=Team.monkey, category=category, strength=strength)
    wolf = Card(team=Team.wolf, category=category, strength=strength)
    battle_result = card_battle.battle_winner(monkey, wolf, {Team.wolf: 4, Team.monkey: 4})
    assert battle_result.status == BattleStatus.draw
    assert battle_result.winner is None


@pytest.mark.parametrize("strength", (0, 1, 2, 3, 4))
def test_joker_joker_draws(strength: int) -> None:
    joker_strengths = {Team.wolf: strength, Team.monkey: strength}
    battle_result = card_battle.battle_winner(MJ4, WJ4, joker_strengths)
    assert battle_result.status == BattleStatus.draw
    assert battle_result.winner is None
    assert joker_strengths[Team.monkey] == 0
    assert joker_strengths[Team.wolf] == 0


def test_rock_paper_scissors_wins() -> None:
    for monkey_rock in (MR1, MR2, MR3):
        for wolf_paper in (WP1, WP2, WP3):
            assert_battle_winner(wolf_paper, monkey_rock)

        for wolf_scissors in (WS1, WS2, WS3):
            assert_battle_winner(monkey_rock, wolf_scissors)


@pytest.mark.parametrize("category", (Category.rock, Category.paper, Category.scissors))
def test_strength_wins(category: Category) -> None:
    M1 = Card(team=Team.monkey, category=category, strength=1)
    M2 = Card(team=Team.monkey, category=category, strength=2)
    M3 = Card(team=Team.monkey, category=category, strength=3)

    W1 = Card(team=Team.wolf, category=category, strength=1)
    W2 = Card(team=Team.wolf, category=category, strength=2)
    W3 = Card(team=Team.wolf, category=category, strength=3)

    assert_battle_winner(M2, W1)
    assert_battle_winner(M3, W1)
    assert_battle_winner(M3, W2)

    assert_battle_winner(W2, M1)
    assert_battle_winner(W3, M1)
    assert_battle_winner(W3, M2)


def test_joker_non_joker_wins_MJ4_WR1() -> None:
    joker_strengths = {Team.monkey: 4, Team.wolf: 4}
    battle_result = card_battle.battle_winner(MJ4, WR1, joker_strengths)
    assert battle_result.status == BattleStatus.card_a_wins
    assert battle_result.winner == MJ4
    assert joker_strengths[Team.monkey] == 3
    assert joker_strengths[Team.wolf] == 4


def test_joker_non_joker_wins_MJ3_WR1() -> None:
    joker_strengths = {Team.monkey: 3, Team.wolf: 4}
    battle_result = card_battle.battle_winner(MJ4, WR1, joker_strengths)
    assert battle_result.status == BattleStatus.card_a_wins
    assert battle_result.winner == MJ4
    assert joker_strengths[Team.monkey] == 2
    assert joker_strengths[Team.wolf] == 4


def test_joker_non_joker_wins_MJ2_WR1() -> None:
    joker_strengths = {Team.monkey: 2, Team.wolf: 4}
    battle_result = card_battle.battle_winner(MJ4, WR1, joker_strengths)
    assert battle_result.status == BattleStatus.card_a_wins
    assert battle_result.winner == MJ4
    assert joker_strengths[Team.monkey] == 1
    assert joker_strengths[Team.wolf] == 4


def test_joker_non_joker_wins_MP2_WJ4() -> None:
    joker_strengths = {Team.monkey: 4, Team.wolf: 4}
    battle_result = card_battle.battle_winner(MP2, WJ4, joker_strengths)
    assert battle_result.status == BattleStatus.card_b_wins
    assert battle_result.winner == WJ4
    assert joker_strengths[Team.monkey] == 4
    assert joker_strengths[Team.wolf] == 2


def test_joker_non_joker_wins_MJ4_WS3() -> None:
    joker_strengths = {Team.monkey: 4, Team.wolf: 4}
    battle_result = card_battle.battle_winner(MJ4, WS3, joker_strengths)
    assert battle_result.status == BattleStatus.card_a_wins
    assert battle_result.winner == MJ4
    assert joker_strengths[Team.monkey] == 1
    assert joker_strengths[Team.wolf] == 4


@pytest.mark.parametrize(
    "monkey_strength, wolf_strength", ((3, 4), (2, 4), (1, 4), (0, 4), (2, 3), (1, 3), (0, 3), (1, 2), (0, 2), (0, 1))
)
def test_joker_joker_wins(monkey_strength: int, wolf_strength: int) -> None:
    joker_strengths = {Team.monkey: monkey_strength, Team.wolf: wolf_strength}
    battle_result = card_battle.battle_winner(MJ4, WJ4, joker_strengths)
    assert battle_result.status == BattleStatus.card_b_wins
    assert battle_result.winner == WJ4

    assert joker_strengths[Team.monkey] == monkey_strength
    assert joker_strengths[Team.wolf] == wolf_strength - monkey_strength


def assert_battle_winner(winner: Card, loser: Card) -> None:
    assert winner.category != Category.joker
    assert loser.category != Category.joker

    battle_result_1 = card_battle.battle_winner(winner, loser, {Team.wolf: 4, Team.monkey: 4})
    assert battle_result_1.status == BattleStatus.card_a_wins
    assert battle_result_1.winner == winner

    battle_result_2 = card_battle.battle_winner(loser, winner, {Team.wolf: 4, Team.monkey: 4})
    assert battle_result_2.status == BattleStatus.card_b_wins
    assert battle_result_2.winner == winner
