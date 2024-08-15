from enum import IntEnum


class CombatCategory(IntEnum):
    ROCK = 0
    PAPER = 1
    SCISSORS = 2
    JOKER = 3


class Team(IntEnum):
    MONKEY = 0
    WOLF = 1

    def other(self) -> "Team":
        return 1 - self

    def __str__(self) -> str:
        if self == Team.MONKEY:
            return "MONKEY"
        if self == Team.WOLF:
            return "WOLF"
        raise RuntimeError("Bad team value")


TEAM_STRS = {Team.MONKEY: "M", Team.WOLF: "W"}
COMBAT_CATEGORY_STRS = {
    CombatCategory.ROCK: "R",
    CombatCategory.PAPER: "P",
    CombatCategory.SCISSORS: "S",
    CombatCategory.JOKER: "J",
}


class Card:
    def __init__(self, team: Team, combat_category: CombatCategory, strength: int) -> None:
        self.team = team
        self.combat_category = combat_category
        self.strength = strength
        self.__hash = hash((self.team, self.combat_category, self.strength))
        self.__str = f"{TEAM_STRS[self.team]}{COMBAT_CATEGORY_STRS[self.combat_category]}{self.strength}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Card):
            return NotImplemented

        return (
            self.team == other.team
            and self.combat_category == other.combat_category
            and self.strength == other.strength
        )

    def __hash__(self) -> int:
        return self.__hash

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Card):
            return NotImplemented

        return (self.team, self.combat_category, self.strength) < (other.team, other.combat_category, other.strength)

    def clone(self) -> "Card":
        return Card(self.team, self.combat_category, self.strength)

    def __str__(self) -> str:
        return self.__str
