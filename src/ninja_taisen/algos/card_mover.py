from ninja_taisen.algos import card_battle
from ninja_taisen.dtos import BOARD_LENGTH, BoardDto, CardPilesDto, CategoryDto, TeamDto


def move_card(board: BoardDto, position: tuple[int, int], dice_roll: int, team: TeamDto) -> None:
    _move_card_recursive(board, position, dice_roll, team)
    _restore_jokers(board.monkey_cards)
    _restore_jokers(board.wolf_cards)


def _move_card_recursive(board: BoardDto, position: tuple[int, int], dice_roll: int, team: TeamDto) -> None:
    team_cards = board.monkey_cards if team == TeamDto.monkey else board.wolf_cards
    old_pile_index = position[0]
    new_pile_index = old_pile_index + dice_roll if team == TeamDto.monkey else old_pile_index - dice_roll
    new_pile_index = max(0, min(new_pile_index, BOARD_LENGTH - 1))

    cards_moved = 0
    for card_index in range(position[1], len(team_cards[old_pile_index])):
        card_to_move = team_cards[old_pile_index][card_index]
        team_cards[new_pile_index].append(card_to_move)
        cards_moved += 1

    for _ in range(cards_moved):
        team_cards[old_pile_index].pop()

    _resolve_battles(board, new_pile_index, team)


def _resolve_battles(board: BoardDto, pile_index: int, team: TeamDto) -> None:
    monkey_pile = board.monkey_cards[pile_index]
    wolf_pile = board.wolf_cards[pile_index]

    while monkey_pile and wolf_pile:
        winning_card = card_battle.battle_winner(monkey_pile[-1], wolf_pile[-1])
        if winning_card:
            if winning_card.team == TeamDto.monkey:
                wolf_pile.pop()
            else:
                monkey_pile.pop()
        else:
            if team == TeamDto.monkey:
                if pile_index == BOARD_LENGTH - 1:
                    wolf_pile.pop()
                else:
                    move_card(board, (pile_index, len(monkey_pile) - 1), -1, TeamDto.monkey)
                    move_card(board, (pile_index, len(wolf_pile) - 1), -1, TeamDto.wolf)
            else:
                if pile_index == 0:
                    monkey_pile.pop()
                else:
                    move_card(board, (pile_index, len(wolf_pile) - 1), -1, TeamDto.wolf)
                    move_card(board, (pile_index, len(monkey_pile) - 1), -1, TeamDto.monkey)


def _restore_jokers(cards: CardPilesDto) -> None:
    for position_cards in cards:
        for card in position_cards:
            if card.category == CategoryDto.joker:
                card.strength = 4
