from ninja_taisen.objects.types import BattleResult, BattleStatus, Card, Category, Team


def battle_winner(card_a: Card, card_b: Card, joker_strengths: dict[Team, int]) -> BattleResult:
    if card_a.category == Category.joker:
        if card_b.category == Category.joker:
            return _joker_versus_joker(card_a, card_b, joker_strengths)
        else:
            return _joker_versus_non_joker(card_a, card_b, joker_strengths)
    elif card_b.category == Category.joker:
        result = _joker_versus_non_joker(card_b, card_a, joker_strengths)
        return BattleResult(status=result.status.other(), winner=result.winner)
    elif card_a.category == card_b.category:
        return _strength_winner(card_a, card_b, joker_strengths)
    else:
        return _rock_paper_scissors_winner(card_a, card_b)


def _joker_versus_joker(joker_a: Card, joker_b: Card, joker_strengths: dict[Team, int]) -> BattleResult:
    assert joker_a.category == Category.joker, f"Expected {joker_a} to be a joker"
    assert joker_b.category == Category.joker, f"Expected {joker_b} to be a joker"

    result = _strength_winner(joker_a, joker_b, joker_strengths)
    if result.winner is None:
        joker_strengths[Team.monkey] = 0
        joker_strengths[Team.wolf] = 0
    else:
        joker_strengths[result.winner.team] -= min(joker_strengths.values())

    return result


def _joker_versus_non_joker(joker: Card, non_joker: Card, joker_strengths: dict[Team, int]) -> BattleResult:
    assert joker.category == Category.joker, f"Expected {joker} to be a joker"

    result = _strength_winner(joker, non_joker, joker_strengths)

    if result.winner is None:
        joker_strengths[joker.team] = 0
    elif result.winner.category == Category.joker:
        joker_strengths[joker.team] -= non_joker.strength

    return result


def _strength_winner(card_a: Card, card_b: Card, joker_strengths: dict[Team, int]) -> BattleResult:
    card_a_strength = card_a.strength if card_a.category != Category.joker else joker_strengths[card_a.team]
    card_b_strength = card_b.strength if card_b.category != Category.joker else joker_strengths[card_b.team]

    if card_a_strength > card_b_strength:
        return BattleResult(status=BattleStatus.card_a_wins, winner=card_a)
    if card_a_strength < card_b_strength:
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
