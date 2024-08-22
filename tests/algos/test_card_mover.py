from ninja_taisen.algos.card_mover import CardMover
from ninja_taisen.objects.cards import MJ4, MP2, MR2, MS1, MS2, MS3, WJ4, WP1, WP3, WR3, WS1
from ninja_taisen.objects.types import Board, Team


#  Move MR2 two spaces to the right
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
    card_mover = CardMover(board=board)
    card_mover.move_card_and_resolve_battles(team=Team.monkey, dice_roll=2, pile_index=5, card_index=0)
