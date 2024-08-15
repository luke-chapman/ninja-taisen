from ninja_taisen.objects import dice


class TestDice:
    def test_rolls(self) -> None:
        rolls = {1: 0, 2: 0, 3: 0}
        rolls_count = 1000

        for _ in range(rolls_count):
            roll = dice.roll()
            rolls[roll] += 1

        assert rolls[1] > rolls[2]
        assert rolls[2] > rolls[3]
