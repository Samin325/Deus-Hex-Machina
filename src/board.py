# board.py

from constants import *
from coord import Coord
from cell import Cell
from twobridge import TwoBridge


class Board:
    def __init__(self, size: int) -> None:
        """ Create a Board object

        Parameters:
            size: (int) size of the game board
        """
        self.__boardsize = size
        self.cells = dict()
        self.blacks = dict()
        self.whites = dict()
        self.empties = dict()
        self.create_all_cells()

    def getsize(self) -> int:
        return self.__boardsize

    def create_all_cells(self) -> None:
        """ Creates a Cell object for every coord on the board"""
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
            top.neighbours.add(Coord(x, self.__boardsize))
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
            bottom.neighbours.add(Coord(x, 1))
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
            left.neighbours.add(Coord(1, y))
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
            right.neighbours.add(Coord(self.__boardsize, y))
        for y in range (2, self.__boardsize+1):
            dest = Coord(self.__boardsize-1, y)
            right.twobridges[dest] = TwoBridge(
                Edges.RIGHT,
                dest,
                (Coord(self.__boardsize, y-1), Coord(self.__boardsize, y)),
                Status.TO_BE
            )

        # populate the relevant dicts with the edge cells
        self.cells[Edges.TOP] = top
        self.whites[Edges.TOP] = top
        self.cells[Edges.BOTTOM] = bottom
        self.whites[Edges.BOTTOM] = bottom
        self.cells[Edges.LEFT] = left
        self.blacks[Edges.LEFT] = left
        self.cells[Edges.RIGHT] = right
        self.blacks[Edges.RIGHT] = right


    def bi_bfs(self, si: Coord, sg: Coord) -> bool:
        """ Run Bi-BFS algorithm to find path between start and goal state

        Arguments:
        si (Coord): initial state
        sg (Coord): goal state
        self: map in which the states exist

        Returns:
        (bool) true if game has been won by this side, false if not
        """
        # initialize the forward open and closed (set) lists twith starting state
        color = self.cells[si].color
        openf = []
        openf.append(si)
        counterf = 0
        closedf = set()
        closedf.add(si)

        # initialize the backward lists with goal state
        openb = []
        openb.append(sg)
        counterb = 0
        closedb = set()
        closedb.add(sg)

        search_forwards = True

        # run Bi-BS
        while counterf < len(openf) and counterb < len(openb):
            if search_forwards:
                coord = openf[counterf]
                counterf+=1

                # get a list of children of the node that are the same color
                children = []
                for node in self.cells[coord].neighbours:
                    if self.cells[node].color == color:
                        children.append(node)

                for child in children:
                    # if the child exists in the closed backwards list, a path has been found and the game won
                    if child in closedb:
                        return True

                    # if the child does not exist in the closed forward list, add to open and closed forward lists
                    if child not in closedf:
                        openf.append(child)
                        closedf.add(child)

            # else, expand from backwards (same as done above but with switched backwards/forwards lists)
            else:
                coord = openb[counterb]
                counterb += 1

                children = []
                for node in self.cells[coord].neighbours:
                    if self.cells[node].color == color:
                        children.append(node)

                for child in children:
                    if child in closedf:
                        return True

                    if child not in closedb:
                        openb.append(child)
                        closedb.add(child)

            search_forwards = not search_forwards

        # if the loop has exited and no solution found, there is no solution, so return accordingly
        return False


    def check_win(self, movecount: int) -> Color:
        """Check whether or not the game has come to a close

        Parameters:
            movecount (int) - number of moves that have been played

        Returns:
            Color: color of the winning player, or empty for no winner
        """
        #  game cannot have been won if less than '19' moves have been made
        if (movecount < self.__boardsize*2-1):
            return Color.EMPTY
        # check if white has won
        if self.bi_bfs(Edges.TOP, Edges.BOTTOM):
            return Color.WHITE
        # check if black has won
        elif self.bi_bfs(Edges.LEFT, Edges.RIGHT):
            return Color.BLACK
        # return no one has won
        return Color.EMPTY


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

    def set(self, coord: Coord, color: Color) -> bool:
        """ Set a piece on an empty cell of the board

        Parameters:
            coord: (Coord) coordinate to place the piece on
            color: (Color) what colour piece to place

        Returns: (bool)
            True if successful, False if the cell was not empty
        """
        if self.cells[coord].color != Color.EMPTY:
            return False
        self.cells[coord].color = color
        if color == Color.BLACK:
            self.blacks[coord] = self.empties.pop(coord)
        elif color == Color.WHITE:
            self.whites[coord] = self.empties.pop(coord)
        else:
            return False  # attempted to set a cell to empty. use unset()
        return True

    def unset(self, coord: Coord) -> bool:
        """ Remove a piece from the board

        Parameters:
            coord: (Coord) coordinate to remove the piece from

        Returns: (bool)
            True if successful, False if there was no piece there
        """
        if self.cells[coord].color == Color.EMPTY:
            return False
        old_color = self.cells[coord].color
        self.cells[coord].color = Color.EMPTY
        if old_color == Color.BLACK:
            self.empties[coord] = self.blacks.pop(coord)
        else:
            self.empties[coord] = self.whites.pop(coord)
        return True
