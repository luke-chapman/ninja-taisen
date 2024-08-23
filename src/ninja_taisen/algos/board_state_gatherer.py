from logging import getLogger

from ninja_taisen.algos import board_inspector
from ninja_taisen.algos.card_mover import CardMover
from ninja_taisen.objects.safe_random import SafeRandom
from ninja_taisen.objects.types import DTO_BY_CATEGORY, DTO_BY_TEAM, Board, BoardStateMidTurn, Category, Team

log = getLogger(__name__)


def gather_all_board_states_post_move(starting_board: Board, team: Team, random: SafeRandom) -> list[BoardStateMidTurn]:
    board_contexts = []
    dice_rolls = {
        Category.rock: random.roll_dice(),
        Category.paper: random.roll_dice(),
        Category.scissors: random.roll_dice(),
    }
    initial_state = BoardStateMidTurn(board=starting_board, used_joker=False, dice_used=[])

    for dice_type_a, roll_a in dice_rolls.items():
        new_contexts_a = gather_board_state_post_move([initial_state], dice_type_a, roll_a, team)
        board_contexts.extend(new_contexts_a)

        for dice_type_b, roll_b in dice_rolls.items():
            if dice_type_a == dice_type_b:
                continue

            new_contexts_b = gather_board_state_post_move(new_contexts_a, dice_type_b, roll_b, team)
            board_contexts.extend(new_contexts_b)

            for dice_type_c, roll_c in dice_rolls.items():
                if dice_type_a == dice_type_c or dice_type_b == dice_type_c:
                    continue

                new_contexts_c = gather_board_state_post_move(new_contexts_b, dice_type_c, roll_c, team)
                board_contexts.extend(new_contexts_c)

    return board_contexts


def gather_board_state_post_move(
    initial_states: list[BoardStateMidTurn],
    category: Category,
    dice_roll: int,
    team: Team,
) -> list[BoardStateMidTurn]:
    final_states = []

    for initial_state in initial_states:
        board = initial_state.board
        if board_inspector.victorious_team(board) is not None:
            continue

        cards = board.cards(team)
        movable_card_indices = board_inspector.movable_card_indices(cards, category, initial_state.used_joker)

        for pile_index, card_index in movable_card_indices:
            cloned_board = board.clone()
            dice_used = list(initial_state.dice_used)  # Take a copy
            used_joker = initial_state.used_joker
            using_joker = cards[pile_index][card_index].category == Category.joker

            try:
                card_mover = CardMover(board=cloned_board)
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

            used_joker |= using_joker
            dice_used.append((category, dice_roll))

            final_states.append(BoardStateMidTurn(board=cloned_board, used_joker=used_joker, dice_used=dice_used))

    return final_states
