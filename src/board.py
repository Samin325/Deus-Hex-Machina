# board.py

from constants import *
from coord import Coord
from cell import Cell
from twobridge import TwoBridge


class Board:
    def __init__(self, size: int) -> None:
        self.__boardsize = size
        self.cells = dict()
        self.blacks = dict()
        self.whites = dict()
        self.empties = dict()
        self.create_all_cells()

    def getsize(self) -> int:
        return self.__boardsize

    def create_all_cells(self) -> None:
        # create all the standard cells
        for i in range(1, self.__boardsize+1):
            for j in range(1, self.__boardsize+1):
                coord = Coord(i, j)
                cell = Cell(coord, Color.EMPTY, self.__boardsize)
                self.cells[coord] = cell
                self.empties[coord] = cell

        # create the edge cells
        top = Cell(Edges.TOP, Color.WHITE, self.__boardsize)
        for x in range(1, self.__boardsize+1):
            top.neighbours.append(Coord(x, self.__boardsize))
        for x in range(2, self.__boardsize+1):
            dest = Coord(x, self.__boardsize-1)
            top.twobridges[dest] = TwoBridge(
                Edges.TOP,
                dest,
                (Coord(x-1, self.__boardsize), Coord(x, self.__boardsize)),
                Status.TO_BE
            )
        bottom = Cell(Edges.BOTTOM, Color.WHITE, self.__boardsize)
        for x in range (1, self.__boardsize+1):
            bottom.neighbours.append(Coord(i, 1))
        for x in range (1, self.__boardsize):
            dest = Coord(x, 2)
            bottom.twobridges[dest] = TwoBridge(
                Edges.BOTTOM,
                dest,
                (Coord(x, 1), Coord(x+1, 1)),
                Status.TO_BE
            )
        left = Cell(Edges.LEFT, Color.BLACK, self.__boardsize)
        for y in range(1, self.__boardsize+1):
            left.neighbours.append(Coord(1, y))
        for y in range(1, self.__boardsize):
            dest = Coord(2, y)
            left.twobridges[dest] = TwoBridge(
                Edges.LEFT,
                dest,
                (Coord(1, y), Coord(1, y+1)),
                Status.TO_BE
            )
        right = Cell(Edges.RIGHT, Color.BLACK, self.__boardsize)
        for y in range (1, self.__boardsize+1):
            right.neighbours.append(Coord(self.__boardsize, y))
        for y in range (2, self.__boardsize+1):
            dest = Coord(self.__boardsize-1, y)
            right.twobridges[dest] = TwoBridge(
                Edges.RIGHT,
                dest,
                (Coord(self.__boardsize, y-1), Coord(self.__boardsize, y)),
                Status.TO_BE
            )

        # populate the cells dicts
        self.whites[Edges.TOP] = top
        self.whites[Edges.BOTTOM] = bottom
        self.blacks[Edges.LEFT] = left
        self.blacks[Edges.RIGHT] = right


    def check_win() -> Color:
        pass

    def display(self) -> None:
        """Prints the board to stdout. This is primarily used for
        testing purposes & when playing against a human opponent
        """
        tile_chars = {
            Color.EMPTY: ".",
            Color.BLACK: "B",
            Color.WHITE: "W",
        }

        chars = []
        for y in range(self.__boardsize, 0, -1):
            for _ in range(y-1):
                chars.append(' ')
            for x in range(1, self.__boardsize+1):
                chars.append( tile_chars[self.cells[Coord(x, y)].color] )
                chars.append(' ')
            if y != 1:
                chars.append('\n')

        print("".join(chars))
        return

    def set(color, coord) -> None:
        pass

    def swap():
        pass

    def unset():
        pass
