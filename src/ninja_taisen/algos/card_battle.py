from ninja_taisen.objects.types import BattleResult, BattleStatus, Card, Category


def battle_winner(card_a: Card, card_b: Card) -> BattleResult:
    if card_a.category == Category.joker:
        if card_b.category == Category.joker:
            return _joker_versus_joker(card_a, card_b)
        else:
            return _joker_versus_non_joker(card_a, card_b)
    elif card_b.category == Category.joker:
        result = _joker_versus_non_joker(card_b, card_a)
        return BattleResult(status=result.status.other(), winner=result.winner)
    elif card_a.category == card_b.category:
        return _strength_winner(card_a, card_b)
    else:
        return _rock_paper_scissors_winner(card_a, card_b)


def _joker_versus_joker(joker_a: Card, joker_b: Card) -> BattleResult:
    assert joker_a.category == Category.joker, f"Expected {joker_a} to be a joker"
    assert joker_b.category == Category.joker, f"Expected {joker_b} to be a joker"

    result = _strength_winner(joker_a, joker_b)
    if result.winner is None:
        joker_a.strength = 0
        joker_b.strength = 0
    else:
        result.winner.strength -= min(joker_a.strength, joker_b.strength)

    return result


def _joker_versus_non_joker(joker: Card, non_joker: Card) -> BattleResult:
    assert joker.category == Category.joker, f"Expected {joker} to be a joker"

    result = _strength_winner(joker, non_joker)

    if result.winner is None:
        joker.strength = 0
    elif result.winner.category == Category.joker:
        joker.strength -= non_joker.strength

    return result


def _strength_winner(card_a: Card, card_b: Card) -> BattleResult:
    if card_a.strength > card_b.strength:
        return BattleResult(status=BattleStatus.card_a_wins, winner=card_a)
    if card_a.strength < card_b.strength:
        return BattleResult(status=BattleStatus.card_b_wins, winner=card_b)
    else:
        return BattleResult(status=BattleStatus.draw, winner=None)


# Assumes the cards have different combat categories and neither is a joker
def _rock_paper_scissors_winner(card_a: Card, card_b: Card) -> BattleResult:
    assert card_a.category != Category.joker, f"Expected {card_a} to not be a joker"
    assert card_b.category != Category.joker, f"Expected {card_b} to not be a joker"
    assert card_a.category != card_b.category, f"Expected {card_a},{card_b} to have different categories"

    card_a_wins = (card_a.category.value - card_b.category.value) % 3 == 1
    if card_a_wins:
        return BattleResult(status=BattleStatus.card_a_wins, winner=card_a)
    else:
        return BattleResult(status=BattleStatus.card_b_wins, winner=card_b)
