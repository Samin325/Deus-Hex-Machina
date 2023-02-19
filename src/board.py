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
        """
        Run Bi-BFS algorithm to find path between two sides of the board

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
    

    def check_win(self, movecount: int, your_color: Color) -> int:
        """Check whether or not the game has come to a close

        Parameters:
            movecount (int) - number of moves that have been played
            your_color (Color) - the color that we are playing as

        Returns:
            int: 1 if this bot has won, -1 if the opponent has won, and 0 otherwise.
        """
        #  game cannot have been won if less than 19 moves have been made
        if (movecount<19):
            return 0
        
        winner = 0
        # check if white has won
        if self.bi_bfs(Edges.TOP, Edges.BOTTOM):
            winner = 1
        # check if black has won
        elif self.bi_bfs(Edges.LEFT, Edges.RIGHT):
            winner = -1
        # return the state of the game
        return winner*your_color


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

    def swap(self) -> bool:
        """ Perform the 'swap' move

        Returns: (bool)
            True if successful, False if swap move impermissible
        """
        ## MAY NEED TO REMOVE ENTIRELY. BOT SWAPS PLAYERS INSTEAD OF TILES
        if len(self.blacks) != 3 and len(self.whites) != 3:
            return False
        if len(self.blacks) == 3:
            for coord in self.blacks:
                if coord not in [Edges.LEFT, Edges.RIGHT]:
                    self.unset(coord)
                    self.set(coord, Color.WHITE)
                    break
        else:
            for coord in self.whites:
                if coord not in [Edges.TOP, Edges.BOTTOM]:
                    self.unset(coord)
                    self.set(coord, Color.BLACK)
                    break

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
