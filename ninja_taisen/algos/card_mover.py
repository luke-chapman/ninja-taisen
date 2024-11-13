import logging
from collections import defaultdict

from ninja_taisen.algos import card_battle
from ninja_taisen.objects.types import (
    BOARD_LENGTH,
    DTO_BY_TEAM,
    BattleStatus,
    Board,
    Card,
    Team,
)

log = logging.getLogger(__name__)


class CardMover:
    def __init__(self, board: Board) -> None:
        """
        Class for moving a card and resolving battles. Can be used for multiple card moves
        :param board: Reference to the board; this board's state will be edited when cards are moved
        """
        self.board = board
        self.remaining_battles: list[int] = []
        self.joker_strengths = {Team.monkey: 4, Team.wolf: 4}

    def move_card_and_resolve_battles(self, team: Team, dice_roll: int, pile_index: int, card_index: int) -> None:
        log.debug("Starting board\n%s", self.board)
        self.__move_card(team=team, dice_roll=dice_roll, pile_index=pile_index, card_index=card_index)

        while self.remaining_battles:
            log.debug("remaining_battles=%s", self.remaining_battles)
            self.__resolve_battle(pile_index=self.remaining_battles[-1], team=team)

        self.__remove_empty_piles(self.board.monkey_cards)
        self.__remove_empty_piles(self.board.wolf_cards)
        self.joker_strengths[Team.monkey] = 4
        self.joker_strengths[Team.wolf] = 4

        log.debug("Final board\n%s", self.board)

    def __move_card(self, team: Team, dice_roll: int, pile_index: int, card_index: int) -> None:
        """
        Move the card in question and all cards on top of it to the new space.
        Register the card's destination as requiring battle resolution, but do not resolve the battle

        :param team: Which team's card to move
        :param dice_roll: How many spaces to move the card
        :param pile_index: Index of the pile containing the card (from 0-10)
        :param card_index: Index of the card within the pile
        :return:
        """
        log.debug(
            "Moving team=%s, dice_roll=%s, pile_index=%s, card_index=%s",
            DTO_BY_TEAM[team].value,
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
        """
        Resolve an individual battle. Drawn battles may involve moving cards and scheduling new battles
        :param pile_index: Index of the pile where the battle takes place (from 0-10)
        :param team: The team whose turn it is. This affects how a draw is resolved
        :return:
        """
        monkey_pile = self.board.monkey_cards[pile_index]
        wolf_pile = self.board.wolf_cards[pile_index]

        while monkey_pile and wolf_pile:
            log.debug("Battle between M%s and W%s in pile %s", monkey_pile[-1], wolf_pile[-1], pile_index)
            battle_result = card_battle.battle_winner(monkey_pile[-1], wolf_pile[-1], self.joker_strengths)

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

        log.debug("All battles at pile_index %s resolved - board\n%s", pile_index, self.board)
        self.remaining_battles = [i for i in self.remaining_battles if i != pile_index]

    @staticmethod
    def __remove_empty_piles(card_piles: defaultdict[int, list[Card]]) -> None:
        """
        Save memory by removing empty card piles from the final board
        :param card_piles: Remaining cards for a team
        :return:
        """
        empty_pile_indices = [i for i in card_piles if len(card_piles[i]) == 0]
        for index in empty_pile_indices:
            card_piles.pop(index)
