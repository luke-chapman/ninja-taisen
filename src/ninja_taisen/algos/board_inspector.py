from collections import defaultdict

from ninja_taisen.objects.types import Board, Card, Category, CompletedMoves, Team


def victorious_team(board: Board) -> Team | None:
    if board.monkey_cards[10]:
        assert not board.wolf_cards[0]
        return Team.monkey
    if board.wolf_cards[0]:
        return Team.wolf

    monkeys_remain = any(len(p) > 0 for p in board.monkey_cards.values())
    wolves_remain = any(len(p) > 0 for p in board.wolf_cards.values())
    if monkeys_remain:
        if wolves_remain:
            return None
        else:
            return Team.monkey
    else:
        if wolves_remain:
            return Team.wolf
        else:
            return None


def find_first_winning_move(all_completed_moves: list[CompletedMoves]) -> CompletedMoves | None:
    for completed_moves in all_completed_moves:
        if victorious_team(completed_moves.board) == completed_moves.team:
            return completed_moves
    return None


def movable_card_indices(
    cards: defaultdict[int, list[Card]], category: Category, used_joker: bool
) -> list[tuple[int, int]]:
    indices = []
    for pile_index, pile_cards in cards.items():
        height_of_pile = len(pile_cards)
        accessible_start = max(0, height_of_pile - 3)

        for card_index in range(accessible_start, height_of_pile):
            card_category = pile_cards[card_index].category
            if card_category == category or (not used_joker and card_category == Category.joker):
                indices.append((pile_index, card_index))

    return sorted(indices)
