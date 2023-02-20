from multiprocessing.sharedctypes import Value
from constants import Color
from random import choice, seed
from board import *

seed(42)  # Get same results temporarily

# Note: WHITE goes left->right, BLACK goes top->bottom
# seems like the obtuse corner is bottom-left
# numbers run across the top, letters run downwards

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

        Returns:
            bool: True if the command exists and ran successfully, False otherwise
        """
        tile_chars = {
            Color.EMPTY: ".",
            Color.BLACK: "B",
            Color.WHITE: "W",
        }

        chars = list(map(lambda x: tile_chars[x], self.board))

        for i in reversed(range(1, self.board_size+1)):  # Reverse to avoid shifting indicies
            chars.insert(i * self.board_size, "|")

        print("".join(chars))
        return

    def make_move(self):
        """Generates the move. For this bot, the move is randomly selected from all empty positions."""
        if self.move_count == 1:
            print("swap")
            self.move_count += 1
            return

        empties = []
        for i, cell in enumerate(self.board):
            if cell == Color.EMPTY:
                empties.append(i)

        move = self.coord_to_move(choice(empties))
        self.sety(move)
        print(move)
        return

    def swap(self):
        """
        Performs the 'swap' move
        """
        self.opp, self.color = self.color, self.opp
        self.move_count += 1

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
        coord = self.move_to_coord(move)
        if self.board[coord] != Color.EMPTY:
            #print("Trying to play on a non-empty square!")
            return
        self.board[coord] = self.color
        self.move_count += 1
        return

    def unset(self, move):
        """Tells the bot to set a tile as unused

        Args:
            move (str): A human-readable position on the board
        Returns:
            bool: True if the move has been unmade, False otherwise
        """

        coord = self.move_to_coord(move)
        self.board[coord] = Color.EMPTY
        return True

    def check_win(self):
        """Checks whether or not the game has come to a close.

        Returns:
            int: 1 if this bot has won, -1 if the opponent has won, and 0 otherwise.
        """
        # 
        winning_color = self.board.check_win(self.move_count)
        if winning_color == Color.EMPTY:
            return 0
        elif winning_color == self.color:
            return 1
        else:
            return -1 
         

    def coord_to_move(self, coord):
        """Converts an integer coordinate to a human-readable move

        Args:
            coord (int): A coordinate within self.board

        Returns:
            str: A human-readable version of coord
        Example:
            >>> assert coord_to_move(0) == "a1"
            >>> assert coord_to_move(self.board_size + 2) == "b3"
            >>> assert coord_to_move(22 * self.board_size + 11) == "w12"
        """
        letter = chr(coord // self.board_size + ord("a"))
        number = coord % self.board_size + 1

        return f'{letter}{number}'

    def move_to_coord(self, move):
        """Converts a human-readable move to a coordinate within self.board

        Args:
            move (str): A human-readable position on the board

        Returns:
            int: The integer coordinate of 'move', used to interact with the board

        Example:
            >>> assert move_to_coord("a1") == 0
            >>> assert move_to_coord("b3") == self.board_size + 2
            >>> assert move_to_coord("w12") == 22 * self.board_size + 11
        """
        # TODO: Handle swap move
        if move == "swap":
            self.swap_move()
            return

        assert len(move) >= 2, "Move must be a character-digit pair. Ex: a12"
        assert move[0].isalpha(), "First character must be a letter. Ex: a12"
        assert move[1:].isdigit(), "Digits must follow the first character. Ex: a12"
        assert (
            ord(move[0]) - ord("a") < self.board_size
        ), "The letter in 'move' must have value less than board size!"
        assert (
            0 < int(move[1:]) <= self.board_size
        ), "Integer part of move must be within range (0, board_size]!"

        column = int(move[1:]) - 1
        row = ord(move[0]) - ord("a")
        return row * self.board_size + column
