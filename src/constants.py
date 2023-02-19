# constants.py

from enum import Enum
from coord import Coord


class Color(Enum):
    EMPTY = 0
    WHITE = 1
    BLACK = -1


class Status(Enum):
    READY = 0       # origin empty
    HALFWAY = 0.5   # origin+depend friendly, dest not hostile
    TO_BE = 1       # origin friendly,  depends+dest empty
    SUCCESS = 2     # origin+dest friendly, depends empty
    FAIL = -1       # dest hostile / depends both hostile / dest empty+depend hostile
    JEOPARDY = 4    # origin+dest friendly, 1depend hostile


class Edges:
    LEFT = Coord(0, 0.5)
    RIGHT = Coord(999, 0.5)
    BOTTOM = Coord(0.5, 0)
    TOP = Coord(0.5, 999)
