from collections import defaultdict

from ninja_taisen.algos.card_mover import CardMover
from ninja_taisen.objects.cards import MJ4, MP2, MR2, MS1, MS2, MS3, WJ4, WP1, WP3, WR3, WS1
from ninja_taisen.objects.types import Board, Team


# This test covers a complex move which caught a few bugs in the original card_mover logic
# See the debug log output below to help you understand what happens internally
#
# DEBUG - card_mover - Starting board
#                     MS3
#                 MJ4 MS1
#     MS2         MP2 MR2
# --- --- --- --- --- --- --- --- --- --- ---
#                         WS1 WJ4 WR3 WP3
#                         WP1
#
# DEBUG - card_mover - Moving team=monkey, dice_roll=2, pile_index=5, card_index=0
# DEBUG - card_mover - Board after card move, pre-battles
#                             MS3
#                 MJ4         MS1
#     MS2         MP2         MR2
# --- --- --- --- --- --- --- --- --- --- ---
#                         WS1 WJ4 WR3 WP3
#                         WP1
#
# DEBUG - card_mover - remaining_battles=[7]
# DEBUG - card_mover - Battle between MS3 and WJ4 in pile 7
# DEBUG - card_mover - Removing MS3 on top of pile 7
# DEBUG - card_mover - Battle between MS1 and WJ1 in pile 7
# DEBUG - card_mover - Draw - both cards retreat, schedule adjacent battles
#                 MJ4         MS1
#     MS2         MP2         MR2
# --- --- --- --- --- --- --- --- --- --- ---
#                         WS1 WJ0 WR3 WP3
#                         WP1
#
# DEBUG - card_mover - Moving team=wolf, dice_roll=-1, pile_index=7, card_index=0
# DEBUG - card_mover - Board after card move, pre-battles
#                 MJ4         MS1
#     MS2         MP2         MR2
# --- --- --- --- --- --- --- --- --- --- ---
#                         WS1     WR3 WP3
#                         WP1     WJ0
#
# DEBUG - card_mover - Moving team=monkey, dice_roll=-1, pile_index=7, card_index=1
# DEBUG - card_mover - Board after card move, pre-battles
#                 MJ4
#     MS2         MP2     MS1 MR2
# --- --- --- --- --- --- --- --- --- --- ---
#                         WS1     WR3 WP3
#                         WP1     WJ0
#
# DEBUG - card_mover - Battle at pile_index 7 resolved - board
#                 MJ4
#     MS2         MP2     MS1 MR2
# --- --- --- --- --- --- --- --- --- --- ---
#                         WS1     WR3 WP3
#                         WP1     WJ0
#
# DEBUG - card_mover - remaining_battles=[8, 6]
# DEBUG - card_mover - Battle between MS1 and WP1 in pile 6
# DEBUG - card_mover - Removing WP1 on top of pile 6
# DEBUG - card_mover - Battle between MS1 and WS1 in pile 6
# DEBUG - card_mover - Draw - both cards retreat, schedule adjacent battles
#                 MJ4
#     MS2         MP2     MS1 MR2
# --- --- --- --- --- --- --- --- --- --- ---
#                         WS1     WR3 WP3
#                                 WJ0
#
# DEBUG - card_mover - Moving team=wolf, dice_roll=-1, pile_index=6, card_index=0
# DEBUG - card_mover - Board after card move, pre-battles
#                 MJ4
#     MS2         MP2     MS1 MR2
# --- --- --- --- --- --- --- --- --- --- ---
#                             WS1 WR3 WP3
#                                 WJ0
#
# DEBUG - card_mover - Moving team=monkey, dice_roll=-1, pile_index=6, card_index=0
# DEBUG - card_mover - Board after card move, pre-battles
#                 MJ4
#     MS2         MP2 MS1     MR2
# --- --- --- --- --- --- --- --- --- --- ---
#                             WS1 WR3 WP3
#                                 WJ0
#
# DEBUG - card_mover - Battle at pile_index 6 resolved - board
#                 MJ4
#     MS2         MP2 MS1     MR2
# --- --- --- --- --- --- --- --- --- --- ---
#                             WS1 WR3 WP3
#                                 WJ0
#
# DEBUG - card_mover - remaining_battles=[8, 7, 5]
# DEBUG - card_mover - Battle at pile_index 5 resolved - board
#                 MJ4
#     MS2         MP2 MS1     MR2
# --- --- --- --- --- --- --- --- --- --- ---
#                             WS1 WR3 WP3
#                                 WJ0
#
# DEBUG - card_mover - remaining_battles=[8, 7]
# DEBUG - card_mover - Battle between MR2 and WS1 in pile 7
# DEBUG - card_mover - Removing WS1 on top of pile 7
# DEBUG - card_mover - Battle at pile_index 7 resolved - board
#                 MJ4
#     MS2         MP2 MS1     MR2
# --- --- --- --- --- --- --- --- --- --- ---
#                                 WR3 WP3
#                                 WJ0
#
# DEBUG - card_mover - remaining_battles=[8]
# DEBUG - card_mover - Battle at pile_index 8 resolved - board
#                 MJ4
#     MS2         MP2 MS1     MR2
# --- --- --- --- --- --- --- --- --- --- ---
#                                 WR3 WP3
#                                 WJ0
#
# DEBUG - card_mover - Final board
#                 MJ4
#     MS2         MP2 MS1     MR2
# --- --- --- --- --- --- --- --- --- --- ---
#                                 WR3 WP3
#                                 WJ4
#
def test_complex_battle() -> None:
    board = Board(
        monkey_cards=defaultdict(list, {1: [MS2], 4: [MP2, MJ4], 5: [MR2, MS1, MS3]}),
        wolf_cards=defaultdict(list, {6: [WS1, WP1], 7: [WJ4], 8: [WR3], 9: [WP3]}),
    )
    card_mover = CardMover(board=board)
    card_mover.move_card_and_resolve_battles(team=Team.monkey, dice_roll=2, pile_index=5, card_index=0)

    final_board = Board(
        monkey_cards=defaultdict(list, {1: [MS2], 4: [MP2, MJ4], 5: [MS1], 7: [MR2]}),
        wolf_cards=defaultdict(list, {8: [WR3, WJ4], 9: [WP3]}),
    )

    assert board == final_board
