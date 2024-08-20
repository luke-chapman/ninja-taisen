from ninja_taisen.dtos import CardDto, CategoryDto


def battle_winner(card_a: CardDto, card_b: CardDto) -> CardDto | None:
    assert card_a.team != card_b.team, f"battle_cards {card_a},{card_b} have the same team"

    # Case where both cards are jokers
    if card_a.category == CategoryDto.joker:
        if card_b.category == CategoryDto.joker:
            return _joker_versus_joker(card_a, card_b)
        else:
            return _joker_versus_non_joker(card_a, card_b)

    if card_b.category == CategoryDto.joker:
        return _joker_versus_non_joker(card_b, card_a)

    if card_a.category == card_b.category:
        return _strength_winner(card_a, card_b)

    return _rock_paper_scissors_winner(card_a, card_b)


def _joker_versus_joker(joker_a: CardDto, joker_b: CardDto) -> CardDto | None:
    assert joker_a.category == CategoryDto.joker, f"Expected {joker_a} to be a joker"
    assert joker_b.category == CategoryDto.joker, f"Expected {joker_b} to be a joker"

    result = _strength_winner(joker_a, joker_b)
    if not result:
        joker_a.strength = 0
        joker_b.strength = 0
    else:
        result.strength -= min(joker_a.strength, joker_b.strength)

    return result


def _joker_versus_non_joker(joker: CardDto, non_joker: CardDto) -> CardDto | None:
    assert joker.category == CategoryDto.joker, f"Expected {joker} to be a joker"

    result = _strength_winner(joker, non_joker)

    if not result:
        joker.strength = 0
    elif result.category == CategoryDto.joker:
        result.strength -= non_joker.strength

    return result


def _strength_winner(card_a: CardDto, card_b: CardDto) -> CardDto | None:
    if card_a.strength > card_b.strength:
        return card_a
    if card_a.strength < card_b.strength:
        return card_b

    return None


# Assumes the cards have different combat categories and neither is a joker
def _rock_paper_scissors_winner(card_a: CardDto, card_b: CardDto) -> CardDto:
    assert card_a.category != CategoryDto.joker, f"Expected {card_a} to not be a joker"
    assert card_b.category != CategoryDto.joker, f"Expected {card_b} to not be a joker"
    assert card_a.category != card_b.category, f"Expected {card_a},{card_b} to have different combat categories"

    if card_a.category == CategoryDto.rock:
        return card_a if card_b.category == CategoryDto.scissors else card_b
    if card_a.category == CategoryDto.paper:
        return card_a if card_b.category == CategoryDto.rock else card_b
    if card_a.category == CategoryDto.scissors:
        return card_a if card_b.category == CategoryDto.paper else card_b

    raise ValueError(f"Unexpected card battle between {card_a} and {card_b}")
