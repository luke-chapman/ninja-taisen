from ninja_taisen.objects.card import Card, CombatCategory, Team


def test_team_other() -> None:
    monkey_other = Team.MONKEY.other()
    assert monkey_other == Team.WOLF

    wolf_other = Team.WOLF.other()
    assert wolf_other == Team.MONKEY


def test_equality() -> None:
    card_a = Card(Team.WOLF, CombatCategory.ROCK, 2)
    card_b = Card(Team.WOLF, CombatCategory.ROCK, 2)
    assert card_a == card_b, f"{card_a} != {card_b}"


def test_non_equality() -> None:
    card_a = Card(Team.WOLF, CombatCategory.ROCK, 2)

    card_b = Card(Team.MONKEY, card_a.combat_category, card_a.strength)
    card_c = Card(card_a.team, CombatCategory.SCISSORS, card_a.strength)
    card_d = Card(card_a.team, card_a.combat_category, 1)

    assert card_a != card_b, f"{card_a} == {card_b}"
    assert card_a != card_c, f"{card_a} == {card_c}"
    assert card_a != card_d, f"{card_a} == {card_d}"


def test_clone() -> None:

    card_a = Card(Team.WOLF, CombatCategory.JOKER, 4)
    card_b = card_a.clone()

    assert card_a == card_b, f"{card_a} != {card_b}"


def test_str() -> None:
    cards_and_expected_strings = [
        (Card(Team.WOLF, CombatCategory.ROCK, 1), "WR1"),
        (Card(Team.MONKEY, CombatCategory.PAPER, 2), "MP2"),
        (Card(Team.WOLF, CombatCategory.SCISSORS, 3), "WS3"),
        (Card(Team.MONKEY, CombatCategory.JOKER, 4), "MJ4"),
    ]

    for card, expected_string in cards_and_expected_strings:
        actual_string = card.__str__()
        assert expected_string == actual_string
