from multiprocessing.sharedctypes import Value
from constants import Color
from random import choice, seed
from board import *

seed(42)  # Get same results temporarily

# Note: BLACK goes left->right, WHITE goes top->bottom in our orientation
# the acute corner is bottom-left
# numbers run across the upwards, letters run rightwards (like a chessboard)

class RandomHexBot:
    def __init__(self, color, board_size=10):
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

    def is_cmd(self, cmd):
        """Checks to see whether the command in 'cmd' conforms to the expected format

        Args:
            cmd (List[str]): A space-separated list of the commands given on the command line

        Returns:
            bool: True if the command exists and has the correct # of arguments, False otherwise
        """
        assert len(cmd)
        if cmd[0] not in self.pub:
            return False
        if len(cmd) - 1 != self.argnums[cmd[0]]:
            return False

        return True

    def run_command(self, cmd):
        """Executes the command contained within 'cmd' if it is applicable

        Args:
            cmd (List[str]): A space-separated list of the commands given on the command line
        """
        if len(cmd) > 1:
            self.pub[cmd[0]](cmd[1])
        else:
            self.pub[cmd[0]]()

    def init_board(self, board_size):
        """Tells the bot to reset the game to an empty board with a specified side length

        Args:
            board_size (int): The width & height of the hex game board to create
        """
        self.board_size = int(board_size)
        self.board = Board(self.board_size)
        self.move_count = 0

    def show_board(self):
        """Prints the board to stdout. This is primarily used for
        testing purposes & when playing against a human opponent
        """
        if self.color == Color.BLACK:
            print("Playing as black")
        else:
            print("Playing as white")
        self.board.display()

    def make_move(self):
        """Generates the move. For this bot, the move is randomly selected from all empty positions."""
        if self.move_count == 1:
            self.swap()
            print("swap")
            return
        move = choice(list(self.board.empties.keys()))
        self.sety(str(move))
        print(move)
        return

    def swap(self):
        """ Performs the 'swap' move """
        self.opp, self.color = self.color, self.opp
        self.move_count += 1
        return

    def seto(self, move):
        """Tells the bot about a move for the other bot

        Args:
            move (str): A human-readable position on which the opponent has just played
        """
        coord = Coord(*Coord.str2cart(move))
        if not self.board.set(coord, self.opp):
            # if set fails, return false
            return False
        self.move_count += 1
        return True

    def sety(self, move):
        """Set Your [tile]. Tells the bot to play a move for itself

        Args:
            move (str): A human-readable position on the board
        """
        coord = Coord(*Coord.str2cart(move))
        if not self.board.set(coord, self.color):
            return False
        self.move_count += 1
        return True

    def unset(self, move):
        """Tells the bot to set a tile as unused

        Args:
            move (str): A human-readable position on the board
        Returns:
            bool: True if the move has been unmade, False otherwise
        """
        coord = Coord(*Coord.str2cart(move))
        return self.board.unset(coord)

    def check_win(self):
        """Checks whether or not the game has come to a close.

        Returns:
            int: 1 if this bot has won, -1 if the opponent has won, and 0 otherwise.
        """
        # if our color is the same as winning color, we win
        winning_color = self.board.check_win(self.move_count)
        if winning_color == Color.EMPTY:
            return 0
        elif winning_color == self.color:
            return 1
        else:
            return -1 
