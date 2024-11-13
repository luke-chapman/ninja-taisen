from copy import deepcopy
from logging import getLogger

from ninja_taisen.algos import board_inspector
from ninja_taisen.algos.card_mover import CardMover
from ninja_taisen.objects.types import DTO_BY_CATEGORY, DTO_BY_TEAM, Board, Category, CompletedMoves, Move, Team

log = getLogger(__name__)


def gather_all_permitted_moves(
    starting_board: Board, team: Team, dice_rolls: dict[Category, int]
) -> list[CompletedMoves]:
    moves: list[CompletedMoves] = []
    initial_state = CompletedMoves(moves=[], team=team, board=starting_board)

    for dice_type_a, roll_a in dice_rolls.items():
        new_moves_a = __gather_moves_for_dice_roll([initial_state], dice_type_a, roll_a, team)
        moves.extend(new_moves_a)

        for dice_type_b, roll_b in dice_rolls.items():
            if dice_type_a == dice_type_b:
                continue

            new_moves_b = __gather_moves_for_dice_roll(new_moves_a, dice_type_b, roll_b, team)
            moves.extend(new_moves_b)

            for dice_type_c, roll_c in dice_rolls.items():
                if dice_type_a == dice_type_c or dice_type_b == dice_type_c:
                    continue

                new_moves_c = __gather_moves_for_dice_roll(new_moves_b, dice_type_c, roll_c, team)
                moves.extend(new_moves_c)

    return moves


def __gather_moves_for_dice_roll(
    initial_states: list[CompletedMoves],
    category: Category,
    dice_roll: int,
    team: Team,
) -> list[CompletedMoves]:
    final_states = []

    for initial_state in initial_states:
        if board_inspector.victorious_team(initial_state.board) is not None:
            continue

        cards = initial_state.board.cards(team)
        movable_card_indices = board_inspector.movable_card_indices(cards, category, initial_state.used_joker())

        for pile_index, card_index in movable_card_indices:
            copied_state = deepcopy(initial_state)
            card = cards[pile_index][card_index]

            try:
                card_mover = CardMover(board=copied_state.board)
                card_mover.move_card_and_resolve_battles(
                    team=team, dice_roll=dice_roll, pile_index=pile_index, card_index=card_index
                )
            except Exception as e:
                log.error(e)
                log.error("Error moving card!")
                log.error(f"Starting board\n{initial_state.board}")
                log.error(
                    f"team={DTO_BY_TEAM[team].value}, "
                    f"category={DTO_BY_CATEGORY[category].value}, "
                    f"dice_roll={dice_roll}"
                )
                log.error(f"pile_index={pile_index}, card_index={card_index}")
                raise

            copied_state.moves.append(Move(dice_category=category, dice_roll=dice_roll, card=card))
            final_states.append(copied_state)

    return final_states
