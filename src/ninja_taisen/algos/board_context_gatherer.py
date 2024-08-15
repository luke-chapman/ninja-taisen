from logging import getLogger

from ninja_taisen.algos import board_inspector, card_mover
from ninja_taisen.objects import dice
from ninja_taisen.objects.board import Board
from ninja_taisen.objects.board_context import BoardContext
from ninja_taisen.objects.card import CombatCategory, Team

log = getLogger(__name__)


def gather_complete_move_contexts(starting_board: Board, team: Team) -> list[BoardContext]:
    board_contexts = []
    dice_rolls = [
        (CombatCategory.ROCK, dice.roll()),
        (CombatCategory.PAPER, dice.roll()),
        (CombatCategory.SCISSORS, dice.roll()),
    ]
    starting_context = BoardContext(board=starting_board, used_joker=False, dice_used=[])

    for dice_type_a, roll_a in dice_rolls:

        new_contexts_a = gather_single_move_contexts([starting_context], dice_type_a, roll_a, team)
        board_contexts += new_contexts_a

        for dice_type_b, roll_b in dice_rolls:
            if dice_type_a == dice_type_b:
                continue

            new_contexts_b = gather_single_move_contexts(new_contexts_a, dice_type_b, roll_b, team)
            board_contexts += new_contexts_b

            for dice_type_c, roll_c in dice_rolls:
                if dice_type_a == dice_type_c or dice_type_b == dice_type_c:
                    continue

                new_contexts_c = gather_single_move_contexts(new_contexts_b, dice_type_c, roll_c, team)
                board_contexts += new_contexts_c

    return board_contexts


def gather_single_move_contexts(
    starting_contexts: list[BoardContext],
    combat_category: CombatCategory,
    dice_roll: int,
    team: Team,
) -> list[BoardContext]:

    final_contexts = []

    for starting_context in starting_contexts:
        board = starting_context.board
        if board_inspector.victorious_team(board) is not None:
            continue

        cards = board.monkey_cards if team == Team.MONKEY else board.wolf_cards
        movable_locations = board_inspector.movable_card_locations(cards, combat_category, starting_context.used_joker)

        for movable_location in movable_locations:
            cloned_context = starting_context.clone()
            using_joker = cards[movable_location[0]][movable_location[1]].combat_category == CombatCategory.JOKER

            try:
                card_mover.move_card(cloned_context.board, movable_location, dice_roll, team)
            except Exception:
                log.info("Error moving card!")
                log.info(f"Starting board\n{starting_context.board}")
                log.info(f"combat_category {combat_category}, dice_roll {dice_roll}, team {team}")
                log.info(f"Movable location {movable_location}")
                raise

            cloned_context.used_joker |= using_joker
            cloned_context.dice_used.append((combat_category, dice_roll))
            cloned_context.board.compute_hash()

            final_contexts.append(cloned_context)

    return final_contexts
