from ninja_taisen.public_types import Board, Card, Category, Team


def victorious_team(board: Board) -> Team | None:
    if board.monkey_cards[-1]:
        assert not board.wolf_cards[0]
        return Team.monkey
    if board.wolf_cards[0]:
        return Team.wolf
    return None


def find_winning_board(boards: list[Board], team: Team) -> Board | None:
    for board in boards:
        if victorious_team(board) == team:
            return board

    return None


def movable_card_locations(
    cards: list[list[Card]], combat_category: Category, used_joker: bool
) -> list[tuple[int, int]]:
    locations = []
    for pile_index, pile_cards in enumerate(cards):
        height_of_pile = len(pile_cards)
        accessible_start = max(0, height_of_pile - 3)

        for card_index in range(accessible_start, height_of_pile):
            card_combat_category = pile_cards[card_index].combat_category
            if card_combat_category == combat_category or (not used_joker and card_combat_category == Category.joker):
                locations.append((pile_index, card_index))

    return locations
