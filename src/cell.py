# coord.py

from twobridge import TwoBridge
from constants import *
from coord import Coord

class Cell:
    def __init__(
            self,
            coord: Coord,
            color: Color,
            boardsize: int
            ) -> None:
        """ Create a Cell object 

        Parameters: 
            coord: (Coord) coordinates of this cell
            color: (Color) colour/whether this cell is empty
            boardsize: (int) size of the square board
        """
        self.coord = coord
        self.color = color
        self.neighbours = set()
        self.twobridges = dict()
        self.__boardsize = boardsize
        self.g = 0
        self.black_parent = self.coord
        self.white_parent = self.coord
        self.__populate_neighbours()
        self.__populate_twobridges()

    def __populate_neighbours(self) -> None:
        """ Calculates the direct neighbours of this cell

        Not be used anywhere except during initialization
        """
        # if there is a -1 in either of the coords, then its a special edge piece, so skip
        if (self.coord.getx() == -1 or self.coord.gety() == -1):
            return

        # neighbour to top left exists only if cell is not on top row and not first column
        if (self.coord.gety()<self.__boardsize and self.coord.getx()>1):
            self.neighbours.add(Coord(self.coord.getx()-1,self.coord.gety()+1))

        # neighbour to top right exists only if cell is not on top row
        if (self.coord.gety()<self.__boardsize):
            self.neighbours.add(Coord(self.coord.getx(),self.coord.gety()+1))

        # neighbour to left exists only if cell is not on first column
        if (self.coord.getx()>1):
            self.neighbours.add(Coord(self.coord.getx()-1,self.coord.gety()))

        # neighbour to right exists only if cell is not on last column
        if (self.coord.getx()<self.__boardsize):
            self.neighbours.add(Coord(self.coord.getx()+1,self.coord.gety()))

        # neighbour to bottom left exists only if cell is not on bottom row
        if (self.coord.gety()>1):
            self.neighbours.add(Coord(self.coord.getx(),self.coord.gety()-1))

        # neighbour to bottom right exists only if cell is not on bottom row and not on last column
        if (self.coord.gety()>1 and self.coord.getx()<self.__boardsize):
            self.neighbours.add(Coord(self.coord.getx()+1,self.coord.gety()-1))

        # check to see if the cell is on any edge; if so, make a neighbour of it a special edge cell
        if (self.coord.getx()==1):
            self.neighbours.add(Edges.LEFT)

        if (self.coord.getx()==self.__boardsize):
            self.neighbours.add(Edges.RIGHT)

        if (self.coord.gety()==self.__boardsize):
            self.neighbours.add(Edges.TOP)

        if (self.coord.gety()==1):
            self.neighbours.add(Edges.BOTTOM)


    def __populate_twobridges(self) -> None:
        """ Calculates which positions this cell could be strong connected to

        Not to be used anywhere except during initialization
        """
        # if there is a -1 in either of the coords, then its a special edge piece, so skip
        if (self.coord.getx() == -1 or self.coord.gety() == -1):
            return

        # twobridges is indexed by coords of the destination, represented as dest
        # the two cells in the middle of the twobridge is represented as deps

        # two bridge top only exists if origin isn't in top two rows and not in first column
        if (self.coord.gety()<self.__boardsize-1 and self.coord.getx()>1):
            dest = Coord(self.coord.getx()-1,self.coord.gety()+2)
            deps = (Coord(self.coord.getx()-1,self.coord.gety()+1), Coord(self.coord.getx(),self.coord.gety()+1))
            self.twobridges[dest] = TwoBridge(self.coord, dest, deps, Status.READY)
        elif (self.coord.gety()==self.__boardsize-1 and self.coord.getx()>1):
            dest = Edges.TOP
            deps = (Coord(self.coord.getx()-1,self.coord.gety()+1), Coord(self.coord.getx(),self.coord.gety()+1))
            self.twobridges[dest] = TwoBridge(self.coord, dest, deps, Status.READY)

        # two bridge bottom only exists if origin isn't in bottom two rows and not in last column
        if (self.coord.gety()>2 and self.coord.getx()<self.__boardsize):
            dest = Coord(self.coord.getx()+1,self.coord.gety()-2)
            deps = (Coord(self.coord.getx(),self.coord.gety()-1), Coord(self.coord.getx()+1,self.coord.gety()-1))
            self.twobridges[dest] = TwoBridge(self.coord, dest, deps, Status.READY)
        elif (self.coord.gety()==2 and self.coord.getx()<self.__boardsize):
            dest = Edges.BOTTOM
            deps = (Coord(self.coord.getx(),self.coord.gety()-1), Coord(self.coord.getx()+1,self.coord.gety()-1))
            self.twobridges[dest] = TwoBridge(self.coord, dest, deps, Status.READY)

        # two bridge upper left only exists if not in first two columns and not in top row
        if (self.coord.gety()<self.__boardsize and self.coord.getx()>2):
            dest = Coord(self.coord.getx()-2,self.coord.gety()+1)
            deps = (Coord(self.coord.getx()-1,self.coord.gety()), Coord(self.coord.getx()-1,self.coord.gety()+1))
            self.twobridges[dest] = TwoBridge(self.coord, dest, deps, Status.READY)
        elif (self.coord.gety()<self.__boardsize and self.coord.getx()==2):
            dest = Edges.LEFT
            deps = (Coord(self.coord.getx()-1,self.coord.gety()), Coord(self.coord.getx()-1,self.coord.gety()+1))
            self.twobridges[dest] = TwoBridge(self.coord, dest, deps, Status.READY)

        # two bridge lower right only exists if not in last two columns and not in bottom row
        if (self.coord.gety()>1  and self.coord.getx()<self.__boardsize-1):
            dest = Coord(self.coord.getx()+2,self.coord.gety()-1)
            deps = (Coord(self.coord.getx()+1,self.coord.gety()), Coord(self.coord.getx()+1,self.coord.gety()-1))
            self.twobridges[dest] = TwoBridge(self.coord, dest, deps, Status.READY)
        elif (self.coord.gety()>1  and self.coord.getx()==self.__boardsize-1):
            dest = Edges.RIGHT
            deps = (Coord(self.coord.getx()+1,self.coord.gety()), Coord(self.coord.getx()+1,self.coord.gety()-1))
            self.twobridges[dest] = TwoBridge(self.coord, dest, deps, Status.READY)

        # two bridge lower left only exists if not in first column and not in bottom row
        if (self.coord.gety()>1 and self.coord.getx()>1):
            dest = Coord(self.coord.getx()-1,self.coord.gety()-1)
            deps = (Coord(self.coord.getx()-1,self.coord.gety()), Coord(self.coord.getx(),self.coord.gety()-1))
            self.twobridges[dest] = TwoBridge(self.coord, dest, deps, Status.READY)

        # two bridge upper right only exists if not in last column and not in top row
        if (self.coord.gety()<self.__boardsize and self.coord.getx()<self.__boardsize):
            dest = Coord(self.coord.getx()+1,self.coord.gety()+1)
            deps = (Coord(self.coord.getx()+1,self.coord.gety()), Coord(self.coord.getx(),self.coord.gety()+1))
            self.twobridges[dest] = TwoBridge(self.coord, dest, deps, Status.READY)

    def __lt__(self, other: object) -> bool:
        return self.g < other.g

    def __hash__(self) -> int:
        return hash(self.coord)