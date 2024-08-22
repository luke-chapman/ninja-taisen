from ninja_taisen.algos.card_mover import move_card
from ninja_taisen.objects.types import Board, Team
from tests.cards import MJ4, MP2, MR2, MS1, MS2, MS3, WJ4, WP1, WP3, WR3, WS1


#
#                      MS3
#                  MJ4 MS1
#      MS2         MP2 MR2
#  --- --- --- --- --- --- --- --- --- --- ---
#                          WS1 WJ4 WR3 WP3
#                          WP1
#
def test_big_battle() -> None:
    board = Board(
        monkey_cards=([], [MS2()], [], [], [MP2(), MJ4()], [MR2(), MS1(), MS3()], [], [], [], [], []),
        wolf_cards=([], [], [], [], [], [], [WS1(), WP1()], [WJ4()], [WR3()], [WP3()], []),
    )
    move_card(board, position=(5, 0), dice_roll=2, team=Team.monkey)
