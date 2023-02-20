# bot.py

from random import choice, seed
from constants import Color
from coord import Coord
from board import Board

seed(42)  # Get same results temporarily

# Note: BLACK goes left->right, WHITE goes top->bottom in our orientation
# the acute corner is bottom-left
# numbers run across the upwards, letters run rightwards (like a chessboard)

class HexBot:
    def __init__(self, color: Color, board_size: int = 10) -> None:
        """ Create a HexBot object

        Parameters:
            color: (Color) what colour tiles this bot is playing
            board_size: (int) gameboard dimensions (default 10)
        """
        self.color = color
        self.opp = Color.BLACK if color == Color.WHITE else Color.WHITE
        self.move_count = 0
        self.init_board(board_size)

        self.pub = {
            "init_board": self.init_board,
            "show_board": self.show_board,
            "make_move": self.make_move,
            "swap": self.swap,
            "seto": self.seto,
            "sety": self.sety,
            "unset": self.unset,
            "check_win": self.check_win,
        }

        self.argnums = {
            "init_board": 1,
            "show_board": 0,
            "make_move": 0,
            "swap": 0,
            "seto": 1,
            "sety": 1,
            "unset": 1,
            "check_win": 0,
        }

    def is_cmd(self, cmd: list) -> bool:
        """ Checks to see whether the command in 'cmd' conforms to the expected format

        Parameters:
            cmd: (list[str]) A space-separated list of the commands given on the command line

        Returns: (bool)
            True if the command exists and has the correct # of arguments, False otherwise
        """
        assert len(cmd)
        if cmd[0] not in self.pub:
            return False
        if len(cmd) - 1 != self.argnums[cmd[0]]:
            return False
        return True

    def run_command(self, cmd: list) -> None:
        """ Executes the command contained within 'cmd' if it is applicable

        Parameters:
            cmd (list[str]): A space-separated list of the commands given on the command line
        """
        if len(cmd) > 1:
            self.pub[cmd[0]](cmd[1])
        else:
            self.pub[cmd[0]]()

    def init_board(self, board_size: int) -> None:
        """ Tells the bot to reset the game to an empty board with a specified side length

        Parameters:
            board_size: (int) The width & height of the hex game board to create
        """
        self.board_size = int(board_size)
        self.board = Board(self.board_size)
        self.move_count = 0

    def show_board(self) -> None:
        """ Prints the board to stdout

        Primarily used for testing & when playing against a human opponent
        """
        print("Playing as:", "black" if self.color == Color.BLACK else "white")
        print("Move count:", self.move_count)
        self.board.display()

    def make_move(self) -> None:
        """ Generates a move, plays it for itself, and prints it to stdout

        For now, the move is randomly selected from all empty positions
        """
        if self.move_count == 1:
            self.swap()
            print("swap")
            return
        move = choice(list(self.board.empties.keys()))
        self.sety(str(move))
        print(move)
        return

    def swap(self) -> bool:
        """ Performs the 'swap' move

        Returns: (bool)
            True if successful, False if swap move is illegal (not first move)
        """
        if self.move_count != 1:
            return False
        self.opp, self.color = self.color, self.opp
        self.move_count += 1
        return True

    def seto(self, move: str) -> bool:
        """ Tells the bot about a move for the other bot

        Parameters:
            move: (str) A human-readable position on which the opponent has just played

        Returns: (bool)
            True if successful, False if the tile was not empty
        """
        # note: move must be of type str to conform with the driver code
        coord = Coord(*Coord.str2cart(move))
        if not self.board.set(coord, self.opp):
            return False
        self.move_count += 1
        return True

    def sety(self, move: str) -> bool:
        """ Set Your [tile]. Tells the bot to play a move for itself

        Parameters:
            move: (str) A human-readable position on the board

        Returns: (bool)
            True if successful, False if the tile was not empty
        """
        coord = Coord(*Coord.str2cart(move))
        if not self.board.set(coord, self.color):
            return False
        self.move_count += 1
        return True

    def unset(self, move: str) -> bool:
        """ Tells the bot to set a tile as unused

        Parameters:
            move: (str) A human-readable position on the board

        Returns: (bool)
            True if the move has been unmade, False if the tile was alr empty
        """
        coord = Coord(*Coord.str2cart(move))
        return self.board.unset(coord)

    def check_win(self) -> None:
        """ Checks whether or not the game has come to a close.

        Prints 1 if we have won, -1 if opponent has, 0 otherwise
        """
        # if our color is the same as winning color, we win
        winning_color = self.board.check_win(self.move_count)
        if winning_color == Color.EMPTY:
            print(0)
        elif winning_color == self.color:
            print(1)
        else:
            print(-1)
