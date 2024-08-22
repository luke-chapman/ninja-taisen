import logging

from ninja_taisen.algos import card_battle
from ninja_taisen.objects.types import (
    BOARD_LENGTH,
    TEAM_TYPE_TO_DTO,
    BattleStatus,
    Board,
    CardPiles,
    Category,
    Team,
)

log = logging.getLogger(__name__)


class CardMover:
    def __init__(self, board: Board) -> None:
        self.board = board
        self.remaining_battles: list[int] = []

    def move_card_and_resolve_battles(self, team: Team, dice_roll: int, pile_index: int, card_index: int) -> None:
        log.debug("Starting board\n%s", self.board)
        self.__move_card(team=team, dice_roll=dice_roll, pile_index=pile_index, card_index=card_index)

        while self.remaining_battles:
            log.debug("remaining_battles=%s", self.remaining_battles)
            self.__resolve_battle(pile_index=self.remaining_battles[-1], team=team)

        self.__restore_jokers(self.board.monkey_cards)
        self.__restore_jokers(self.board.wolf_cards)

        log.debug("Final board\n%s", self.board)

    def __move_card(self, team: Team, dice_roll: int, pile_index: int, card_index: int) -> None:
        log.debug(
            "Moving team=%s, dice_roll=%s, pile_index=%s, card_index=%s",
            TEAM_TYPE_TO_DTO[team].value,
            dice_roll,
            pile_index,
            card_index,
        )

        team_cards = self.board.cards(team)
        new_pile_index = pile_index + dice_roll if team == Team.monkey else pile_index - dice_roll
        new_pile_index = max(0, min(new_pile_index, BOARD_LENGTH - 1))

        cards_moved = 0
        for index_in_pile in range(card_index, len(team_cards[pile_index])):
            card_to_move = team_cards[pile_index][index_in_pile]
            team_cards[new_pile_index].append(card_to_move)
            cards_moved += 1

        for _ in range(cards_moved):
            team_cards[pile_index].pop()

        self.remaining_battles.append(new_pile_index)
        log.debug(f"Board after card move, pre-battles\n{self.board}")

    def __resolve_battle(self, pile_index: int, team: Team) -> None:
        self.remaining_battles = [i for i in self.remaining_battles if i != pile_index]

        monkey_pile = self.board.monkey_cards[pile_index]
        wolf_pile = self.board.wolf_cards[pile_index]

        while monkey_pile and wolf_pile:
            log.debug("Battle between M%s and W%s in pile %s", monkey_pile[-1], wolf_pile[-1], pile_index)
            battle_result = card_battle.battle_winner(monkey_pile[-1], wolf_pile[-1])

            if battle_result.status == BattleStatus.card_a_wins:
                log.debug("Removing W%s on top of pile %s", wolf_pile[-1], pile_index)
                wolf_pile.pop()

            elif battle_result.status == BattleStatus.card_b_wins:
                log.debug("Removing M%s on top of pile %s", monkey_pile[-1], pile_index)
                monkey_pile.pop()

            elif battle_result.status == BattleStatus.draw:
                #  If the result is a draw, both cards move one space back (unless the battle takes place on a home)
                #  Any future battles are resolved starting with those closest to the team's home
                if team == Team.monkey:
                    if pile_index == BOARD_LENGTH - 1:
                        log.debug("Draw in wolf home - removing W%s", wolf_pile[-1])
                        wolf_pile.pop()
                    else:
                        log.debug(
                            "Draw - both cards retreat, schedule adjacent battles\n%s",
                            self.board,
                        )
                        self.__move_card(
                            team=Team.wolf, pile_index=pile_index, card_index=len(wolf_pile) - 1, dice_roll=-1
                        )
                        self.__move_card(
                            team=Team.monkey, pile_index=pile_index, card_index=len(monkey_pile) - 1, dice_roll=-1
                        )
                elif team == Team.wolf:
                    if pile_index == 0:
                        log.debug("Draw in monkey home - removing M%s", monkey_pile[-1])
                        monkey_pile.pop()
                    else:
                        log.debug(
                            "Draw - both cards retreat, schedule adjacent battles\n%s",
                            self.board,
                        )
                        self.__move_card(
                            team=Team.monkey, pile_index=pile_index, card_index=len(monkey_pile) - 1, dice_roll=-1
                        )
                        self.__move_card(
                            team=Team.wolf, pile_index=pile_index, card_index=len(wolf_pile) - 1, dice_roll=-1
                        )
                else:
                    raise ValueError(f"Unexpected team: {team}")
            else:
                raise ValueError(f"Unexpected battle_result.status: {battle_result.status}")

        log.debug("Battle at pile_index %s resolved - board\n%s", pile_index, self.board)

    @staticmethod
    def __restore_jokers(card_piles: CardPiles) -> None:
        for pile in card_piles:
            for card in pile:
                if card.category == Category.joker:
                    card.strength = 4
