from ninja_taisen.algos import card_battle
from ninja_taisen.objects.types import BOARD_LENGTH, BattleStatus, Board, CardPiles, Category, Team


def move_card(board: Board, position: tuple[int, int], dice_roll: int, team: Team) -> None:
    __move_card_recursive(board, position, dice_roll, team)
    __restore_jokers(board.monkey_cards)
    __restore_jokers(board.wolf_cards)


def __move_card_recursive(board: Board, position: tuple[int, int], dice_roll: int, team: Team) -> None:
    team_cards = board.cards(team)
    old_pile_index = position[0]
    new_pile_index = old_pile_index + dice_roll if team == Team.monkey else old_pile_index - dice_roll
    new_pile_index = max(0, min(new_pile_index, BOARD_LENGTH - 1))

    cards_moved = 0
    for card_index in range(position[1], len(team_cards[old_pile_index])):
        card_to_move = team_cards[old_pile_index][card_index]
        team_cards[new_pile_index].append(card_to_move)
        cards_moved += 1

    for _ in range(cards_moved):
        team_cards[old_pile_index].pop()

    __resolve_battles(board, new_pile_index, team)


def __resolve_battles(board: Board, pile_index: int, team: Team) -> None:
    monkey_pile = board.monkey_cards[pile_index]
    wolf_pile = board.wolf_cards[pile_index]

    while monkey_pile and wolf_pile:
        battle_result = card_battle.battle_winner(monkey_pile[-1], wolf_pile[-1])
        if battle_result.status == BattleStatus.card_a_wins:
            wolf_pile.pop()
        elif battle_result.status == BattleStatus.card_b_wins:
            monkey_pile.pop()
        elif battle_result.status == BattleStatus.draw:
            #  If the result is a draw, both cards move one space back (unless the battle takes place on a home)
            #  Any future battles are resolved starting with those closest to the team's home
            if team == Team.monkey:
                if pile_index == BOARD_LENGTH - 1:
                    wolf_pile.pop()
                else:
                    __move_card_recursive(board, (pile_index, len(monkey_pile) - 1), -1, Team.monkey)
                    __move_card_recursive(board, (pile_index, len(wolf_pile) - 1), -1, Team.wolf)
            else:
                if pile_index == 0:
                    monkey_pile.pop()
                else:
                    __move_card_recursive(board, (pile_index, len(wolf_pile) - 1), -1, Team.wolf)
                    __move_card_recursive(board, (pile_index, len(monkey_pile) - 1), -1, Team.monkey)
        else:
            raise ValueError(f"Unexpected battle_result.winner: {battle_result.status}")


def __restore_jokers(cards: CardPiles) -> None:
    for pile in cards:
        for card in pile:
            if card.category == Category.joker:
                card.strength = 4
