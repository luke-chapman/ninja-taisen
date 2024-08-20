from ninja_taisen.dtos import BoardDto, CardPilesDto, CategoryDto, TeamDto


def victorious_team(board: BoardDto) -> TeamDto | None:
    if board.monkey_cards[-1]:
        assert not board.wolf_cards[0]
        return TeamDto.monkey
    if board.wolf_cards[0]:
        return TeamDto.wolf
    return None


def find_winning_board(boards: list[BoardDto], team: TeamDto) -> BoardDto | None:
    for board in boards:
        if victorious_team(board) == team:
            return board

    return None


def movable_card_locations(cards: CardPilesDto, category: CategoryDto, used_joker: bool) -> list[tuple[int, int]]:
    locations = []
    for pile_index, pile_cards in enumerate(cards):
        height_of_pile = len(pile_cards)
        accessible_start = max(0, height_of_pile - 3)

        for card_index in range(accessible_start, height_of_pile):
            card_category = pile_cards[card_index].category
            if card_category == category or (not used_joker and card_category == CategoryDto.joker):
                locations.append((pile_index, card_index))

    return locations
