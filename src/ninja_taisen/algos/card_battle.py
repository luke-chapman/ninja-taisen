from ninja_taisen.objects.types import Card, Category


def battle_winner(card_a: Card, card_b: Card) -> Card | None:
    # Case where both cards are jokers
    if card_a.category == Category.joker:
        if card_b.category == Category.joker:
            return _joker_versus_joker(card_a, card_b)
        else:
            return _joker_versus_non_joker(card_a, card_b)

    if card_b.category == Category.joker:
        return _joker_versus_non_joker(card_b, card_a)

    if card_a.category == card_b.category:
        return _strength_winner(card_a, card_b)

    return _rock_paper_scissors_winner(card_a, card_b)


def _joker_versus_joker(joker_a: Card, joker_b: Card) -> Card | None:
    assert joker_a.category == Category.joker, f"Expected {joker_a} to be a joker"
    assert joker_b.category == Category.joker, f"Expected {joker_b} to be a joker"

    result = _strength_winner(joker_a, joker_b)
    if not result:
        joker_a = Card(category=joker_a.category, strength=0)
        joker_b = Card(category=joker_b.category, strength=0)
    else:
        result = Card(category=result.category, strength=result.strength - min(joker_a.strength, joker_b.strength))

    return result


def _joker_versus_non_joker(joker: Card, non_joker: Card) -> Card | None:
    assert joker.category == Category.joker, f"Expected {joker} to be a joker"

    result = _strength_winner(joker, non_joker)

    if not result:
        joker = Card(category=joker.category, strength=0)
    elif result.category == Category.joker:
        result = Card(category=result.category, strength=result.strength - non_joker.strength)

    return result


def _strength_winner(card_a: Card, card_b: Card) -> Card | None:
    if card_a.strength > card_b.strength:
        return card_a
    if card_a.strength < card_b.strength:
        return card_b

    return None


# Assumes the cards have different combat categories and neither is a joker
def _rock_paper_scissors_winner(card_a: Card, card_b: Card) -> Card:
    assert card_a.category != Category.joker, f"Expected {card_a} to not be a joker"
    assert card_b.category != Category.joker, f"Expected {card_b} to not be a joker"
    assert card_a.category != card_b.category, f"Expected {card_a},{card_b} to have different combat categories"

    if card_a.category == Category.rock:
        return card_a if card_b.category == Category.scissors else card_b
    if card_a.category == Category.paper:
        return card_a if card_b.category == Category.rock else card_b
    if card_a.category == Category.scissors:
        return card_a if card_b.category == Category.paper else card_b

    raise ValueError(f"Unexpected card battle between {card_a} and {card_b}")
