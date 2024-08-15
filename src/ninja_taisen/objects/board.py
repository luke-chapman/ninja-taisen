from ninja_taisen.objects.card import Card, Team

BOARD_LENGTH = 11


class Board:
    def __init__(self, monkey_cards: list[list[Card]], wolf_cards: list[list[Card]]) -> None:
        self.cards = {Team.MONKEY: monkey_cards, Team.WOLF: wolf_cards}
        self.__hash = 0

        assert len(monkey_cards) == BOARD_LENGTH, f"Expected board length {BOARD_LENGTH}, was {len(monkey_cards)}"
        assert len(wolf_cards) == BOARD_LENGTH, f"Expected board length {BOARD_LENGTH}, was {len(wolf_cards)}"

        assert all(
            map(
                lambda pile: all(map(lambda card: card.team == Team.MONKEY, pile)),
                monkey_cards,
            )
        ), f"Some monkey cards were not monkeys, {monkey_cards}"
        assert all(
            map(
                lambda pile: all(map(lambda card: card.team == Team.WOLF, pile)),
                wolf_cards,
            )
        ), f"Some wolf cards were not wolves, {wolf_cards}"

    @property
    def monkey_cards(self) -> list[list[Card]]:
        return self.cards[Team.MONKEY]

    @property
    def wolf_cards(self) -> list[list[Card]]:
        return self.cards[Team.WOLF]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Board):
            return NotImplemented

        return self.monkey_cards == other.monkey_cards and self.wolf_cards == other.wolf_cards

    def compute_hash(self) -> None:
        self.__hash = hash(self._cards_str(self.monkey_cards) + self._cards_str(self.wolf_cards))

    @staticmethod
    def _cards_str(cards: list[list[Card]]) -> str:
        str_cards = ""
        for pile in cards:
            str_cards += "["
            for card in pile:
                str_cards += str(card) + ","
            str_cards += "],"
        return str_cards

    def __hash__(self) -> int:
        assert self.__hash
        return self.__hash

    def clone(self) -> "Board":
        cloned_monkey_cards = self._clone_cards(self.monkey_cards)
        cloned_wolf_cards = self._clone_cards(self.wolf_cards)
        return Board(cloned_monkey_cards, cloned_wolf_cards)

    @staticmethod
    def _clone_cards(cards: list[list[Card]]) -> list[list[Card]]:
        cloned_cards = []
        for position_cards in cards:
            cloned_position_cards = []
            for card in position_cards:
                cloned_position_cards.append(card.clone())
            cloned_cards.append(cloned_position_cards)

        return cloned_cards

    def __str__(self) -> str:

        self_str = ""

        max_monkey_height = max([len(pile_cards) for pile_cards in self.monkey_cards])
        for row_index in range(max_monkey_height - 1, -1, -1):
            self_str += self._row_str(self.monkey_cards, row_index) + "\n"

        self_str += "--- " * BOARD_LENGTH + "\n"

        max_wolf_height = max([len(pile_cards) for pile_cards in self.wolf_cards])
        for row_index in range(max_wolf_height):
            self_str += self._row_str(self.wolf_cards, row_index) + "\n"

        return self_str

    @staticmethod
    def _row_str(cards: list[list[Card]], row_index: int) -> str:
        row_str = ""

        for pile_index in range(BOARD_LENGTH):
            if len(cards[pile_index]) <= row_index:
                row_str += "    "
            else:
                row_str += cards[pile_index][row_index].__str__() + " "

        return row_str
