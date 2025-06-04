import enum
from collections import namedtuple

class Player(enum.Enum):
    black = 1
    white = 2

    @property
    def color(self):
        return 'b' if self == Player.black else 'w'

    @property
    def other(self):
        return Player.black if self == Player.white else Player.white

    def set_human_or_ai(self, is_human: bool):
        self.is_human = is_human

    def is_human(self):
        return getattr(self, 'is_human', True)

class Point(namedtuple('Point', 'row col')):
    def neighbors(self):
        return [
            Point(self.row - 1, self.col),
            Point(self.row + 1, self.col),
            Point(self.row, self.col - 1),
            Point(self.row, self.col + 1),
        ]