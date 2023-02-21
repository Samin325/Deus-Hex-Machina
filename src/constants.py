# constants.py

from enum import Enum
from coord import Coord


class Color(Enum):
    EMPTY = 0
    WHITE = 1
    BLACK = -1


class Status(Enum):
    FAIL = -1       # dest/orig hostile / deps both hostile / orig/dest empty, dep hostile
    HALFWAY = 0.5   # dest+orig not hostile, any deps friendly
    READY = 0       # everything empty
    TO_BE = 1       # orig friendly, deps+dest empty (forwards) / dest friendly, deps+orig empty (backwards)
    SUCCESS = 2     # orig+dest friendly, deps empty
    JEOPARDY = 4    # orig+dest friendly, 1dep hostile


class Edges:
    LEFT = Coord(0, -1)
    RIGHT = Coord(999, -1)
    BOTTOM = Coord(-1, 0)
    TOP = Coord(-1, 999)
