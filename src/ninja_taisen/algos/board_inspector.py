from ninja_taisen.objects.types import Board, CardPiles, Category, CompletedMoves, Team


def victorious_team(board: Board) -> Team | None:
    if board.monkey_cards[-1]:
        assert not board.wolf_cards[0]
        return Team.monkey
    if board.wolf_cards[0]:
        return Team.wolf
    return None


def find_first_winning_move(all_completed_moves: list[CompletedMoves], team: Team) -> CompletedMoves | None:
    for completed_moves in all_completed_moves:
        if victorious_team(completed_moves.board) == team:
            return completed_moves
    return None


def movable_card_indices(cards: CardPiles, category: Category, used_joker: bool) -> list[tuple[int, int]]:
    indices = []
    for pile_index, pile_cards in enumerate(cards):
        height_of_pile = len(pile_cards)
        accessible_start = max(0, height_of_pile - 3)

        for card_index in range(accessible_start, height_of_pile):
            card_category = pile_cards[card_index].category
            if card_category == category or (not used_joker and card_category == Category.joker):
                indices.append((pile_index, card_index))

    return indices
