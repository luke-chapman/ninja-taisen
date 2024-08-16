from ninja_taisen.objects.card import Card, CombatCategory


def battle_winner(card_a: Card, card_b: Card) -> Card | None:
    assert card_a.team != card_b.team, f"battle_cards {card_a},{card_b} have the same team"

    # Case where both cards are jokers
    if card_a.combat_category == CombatCategory.JOKER:
        if card_b.combat_category == CombatCategory.JOKER:
            return _joker_versus_joker(card_a, card_b)
        else:
            return _joker_versus_non_joker(card_a, card_b)

    if card_b.combat_category == CombatCategory.JOKER:
        return _joker_versus_non_joker(card_b, card_a)

    if card_a.combat_category == card_b.combat_category:
        return _strength_winner(card_a, card_b)

    return _rock_paper_scissors_winner(card_a, card_b)


def _joker_versus_joker(joker_a: Card, joker_b: Card) -> Card | None:
    assert joker_a.combat_category == CombatCategory.JOKER, f"Expected {joker_a} to be a joker"
    assert joker_b.combat_category == CombatCategory.JOKER, f"Expected {joker_b} to be a joker"

    result = _strength_winner(joker_a, joker_b)
    if not result:
        joker_a.strength = 0
        joker_b.strength = 0
    else:
        result.strength -= min(joker_a.strength, joker_b.strength)

    return result


def _joker_versus_non_joker(joker: Card, non_joker: Card) -> Card | None:
    assert joker.combat_category == CombatCategory.JOKER, f"Expected {joker} to be a joker"

    result = _strength_winner(joker, non_joker)

    if not result:
        joker.strength = 0
    elif result.combat_category == CombatCategory.JOKER:
        result.strength -= non_joker.strength

    return result


def _strength_winner(card_a: Card, card_b: Card) -> Card | None:
    if card_a.strength > card_b.strength:
        return card_a
    if card_a.strength < card_b.strength:
        return card_b

    return None


# Assumes the cards have different combat categories and neither is a joker
def _rock_paper_scissors_winner(card_a: Card, card_b: Card) -> Card:
    assert card_a.combat_category != CombatCategory.JOKER, f"Expected {card_a} to not be a joker"
    assert card_b.combat_category != CombatCategory.JOKER, f"Expected {card_b} to not be a joker"
    assert (
        card_a.combat_category != card_b.combat_category
    ), f"Expected {card_a},{card_b} to have different combat categories"

    card_a_wins = (card_a.combat_category - card_b.combat_category) % 3 == 1
    return card_a if card_a_wins else card_b
