# coord.py

# from twobridge import TwoBridge
from constants import Edges, Color
from coord import Coord

class Cell:
    def __init__(
            self,
            coord: Coord,
            color: Color,
            boardsize: int
            ) -> None:
        """ Create a cell object 

        Parameters: 
            coord (Coord)    - coordinates of this cell
            color (Color)    - colour/whether this cell is empty
            boardsize (int)  - size of the square board
        """
        self.coord = coord
        self.color = color
        self.neighbours = []
        self.twobridges = dict()
        self.__boardsize = boardsize
        self.populate_neighbours()
        self.populate_twobridges()

    def populate_neighbours(self) -> None:
        """ Calculates neighbours and populates list of neighbours of this cell """
        # neighbour to top left exists only if cell is not on top row and not first column
        if (self.coord.gety()<self.__boardsize and self.coord.getx()>1):
            self.neighbours.append(Coord(self.coord.getx()-1,self.coord.gety()+1))

        # neighbour to top right exists only if cell is not on top row
        if (self.coord.gety()<self.__boardsize):
            self.neighbours.append(Coord(self.coord.getx(),self.coord.gety()+1))

        # neighbour to left exists only if cell is not on first column
        if (self.coord.getx()>1):
            self.neighbours.append(Coord(self.coord.getx()-1,self.coord.gety()))

        # neighbour to right exists only if cell is not on last column
        if (self.coord.getx()<self.__boardsize):
            self.neighbours.append(Coord(self.coord.getx()+1,self.coord.gety()))

        # neighbour to bottom left exists only if cell is not on bottom row
        if (self.coord.gety()>1):
            self.neighbours.append(Coord(self.coord.getx(),self.coord.gety()-1))

        # neighbour to bottom right exists only if cell is not on bottom row and not on last column
        if (self.coord.gety()>1 and self.coord.getx()<self.__boardsize):
            self.neighbours.append(Coord(self.coord.getx()+1,self.coord.gety()-1))

        # check to see if the cell is on any edge; if so, make a neighbour of it a special edge cell
        if (self.coord.getx()==1):
            self.neighbours.append(Edges.LEFT)

        if (self.coord.getx()==self.__boardsize):
            self.neighbours.append(Edges.RIGHT)

        if (self.coord.gety()==self.__boardsize):
            self.neighbours.append(Edges.TOP)

        if (self.coord.gety()==1):
            self.neighbours.append(Edges.BOTTOM)


    def populate_twobridges(self) -> None:
        """ Calculates which positions this cell could be strong connected to """
        # if there is a 0.5 in either of the coords, then its an edge piece, so skip
        if (self.coord.getx() == 0.5 or self.coord.gety() == 0.5):
            return

        # index by coord of dest

        # TODO: import twobridge and update the following so it updates dict of twobridges
        # (the logic is in each statement but commented out)

        # two bridge top only exists if origin isn't in top two rows and not in first column
        if (self.coord.gety()<self.__boardsize-1 and self.coord.getx()>1):
            # dest: Coord(self.coord.getx()-1,self.coord.gety()+2))
            # deps: Coord(self.coord.getx()-1,self.coord.gety()+1))     Coord(self.coord.getx(),self.coord.gety()+1))
            pass
        elif (self.coord.gety()==self.__boardsize-1 and self.coord.getx()>1):
            # dest: Coord(TOP)
            # deps: Coord(self.coord.getx()-1,self.coord.gety()+1))     Coord(self.coord.getx(),self.coord.gety()+1))
            pass

        # two bridge bottom only exists if origin isn't in bottom two rows and not in last column
        if (self.coord.gety()>2 and self.coord.getx()<self.__boardsize):
            # dest: Coord(self.coord.getx()+1,self.coord.gety()-2))
            # deps: Coord(self.coord.getx(),self.coord.gety()-1))       Coord(self.coord.getx()+1,self.coord.gety()-1))
            pass
        elif (self.coord.gety()==2 and self.coord.getx()<self.__boardsize):
            # dest: Coord(BOTTOM)
            # deps: Coord(self.coord.getx(),self.coord.gety()-1))       Coord(self.coord.getx()+1,self.coord.gety()-1))
            pass

        # two bridge upper left only exists if not in first two columns and not in top row
        if (self.coord.gety()<self.__boardsize and self.coord.getx()>2):
            # dest: Coord(self.coord.getx()-2,self.coord.gety()+1))
            # deps: Coord(self.coord.getx()-1,self.coord.gety())        Coord(self.coord.getx()-1,self.coord.gety()+1)
            pass
        elif (self.coord.gety()<self.__boardsize and self.coord.getx()==2):
            # dest: Coord(LEFT)
            # deps: Coord(self.coord.getx()-1,self.coord.gety())        Coord(self.coord.getx()-1,self.coord.gety()+1)
            pass

        # two bridge lower right only exists if not in last two columns and not in bottom row
        if (self.coord.gety()>1  and self.coord.getx()<self.__boardsize-1):
            # dest: Coord(self.coord.getx()+2,self.coord.gety()-1))
            # deps: Coord(self.coord.getx()+1,self.coord.gety()))       Coord(self.coord.getx()+1,self.coord.gety()-1))
            pass
        elif (self.coord.gety()>1  and self.coord.getx()==self.__boardsize-1):
            # dest: Coord(RIGHT)
            # deps: Coord(self.coord.getx()+1,self.coord.gety()))       Coord(self.coord.getx()+1,self.coord.gety()-1))
            pass

        # two bridge lower left only exists if not in first column and not in bottom row
        if (self.coord.gety()>1 and self.coord.getx()>1):
            # dest: Coord(self.coord.getx()-1,self.coord.gety()-1))
            # deps: Coord(self.coord.getx()-1,self.coord.gety()))       Coord(self.coord.getx(),self.coord.gety()-1))
            pass

        # two bridge upper right only exists if not in last column and not in top row
        if (self.coord.gety()<self.__boardsize and self.coord.getx()<self.__boardsize):
            # dest: Coord(self.coord.getx()+1,self.coord.gety()+1))
            # deps: Coord(self.coord.getx()+1,self.coord.gety()))       Coord(self.coord.getx(),self.coord.gety()+1))
            pass
