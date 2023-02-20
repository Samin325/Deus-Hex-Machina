# twobridge.py

from coord import Coord
from constants import Color, Status


class TwoBridge:
    def __init__(
            self,
            origin: Coord,
            dest: Coord,
            depends: tuple,
            status: Status
            ) -> None:
        """ Create a TwoBridge object

        Parameters:
            origin: (Coord) coordinate of originating cell
            dest: (Coord) coordinate of this cell (the two-bridge)
            depends: (tuple[Coord, Coord]) coordinates of dependency cells
            status: (Status) status of this cell's two-bridgedness
        """
        self.origin = origin
        self.dest = dest
        self.depends = depends
        self.status = status

    def update_status(self, board: object) -> Status:
        """ Update the status of this two-bridge based on the board state

        Parameters:
            board: (Board) the board in current gamestate

        Returns: (Status)
            new status, after updating internally
        """
        EMPTY = Color.EMPTY
        FRIENDLY = board.cells[self.origin].color
        HOSTILE = Color.BLACK if FRIENDLY == Color.WHITE else Color.WHITE

        ORIG_COLOR = FRIENDLY
        DEP_COLORS = [board.cells[self.depends[i]].color for i in range(2)]
        DEST_COLOR = board.cells[self.dest].color

        if ORIG_COLOR == EMPTY:
            self.status = Status.READY

        elif DEST_COLOR != HOSTILE and any([DEP_COLORS[i] == FRIENDLY for i in range(2)]):
            self.status = Status.HALFWAY

        elif DEST_COLOR == EMPTY and all([DEP_COLORS[i] == EMPTY for i in range(2)]):
            self.status = Status.TO_BE

        elif DEST_COLOR == FRIENDLY and all([DEP_COLORS[i] == EMPTY for i in range(2)]):
            self.status = Status.SUCCESS

        elif DEST_COLOR == HOSTILE or all([DEP_COLORS[i] == HOSTILE for i in range(2)]) or \
                (DEST_COLOR == EMPTY and any([DEP_COLORS[i] == HOSTILE for i in range(2)])):
            self.status = Status.FAIL

        elif DEST_COLOR == FRIENDLY and any([DEP_COLORS[i] == HOSTILE for i in range(2)]):
            self.status = Status.JEOPARDY

        return self.status
