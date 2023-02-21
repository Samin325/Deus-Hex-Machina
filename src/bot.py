# bot.py

from random import choice, seed
from constants import *
from coord import Coord
from board import Board
from cell import Cell
import heapq

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
        self.jeopardized = 0
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
        # if self.move_count < 4:
            # move = self.early_move()
        move = choice(list(self.board.empties.keys()))
        self.sety(str(move))
        print(move)
        return

    def update_twobridges(self, coord: Coord) -> None:
        """ Update the TwoBridge statuses of nearby cells after a move

        Parameters:
            coord: (Coord) the coordinate of the cell that was just played on
        """
        temp_jeopardy = 0
        # update TwoBridge statuses of this cell and its reciprocal twobridges
        for dest in self.board.cells[coord].white_twobridges:
            # TODO: record the new status and act on it if in jeopardy
            temp_jeopardy += 1 if self.board.cells[coord].white_twobridges[dest].update_status(self.board) == Status.JEOPARDY else 0
            temp_jeopardy += 1 if self.board.cells[coord].black_twobridges[dest].update_status(self.board) == Status.JEOPARDY else 0
            temp_jeopardy += 1 if self.board.cells[dest].white_twobridges[coord].update_status(self.board) == Status.JEOPARDY else 0
            temp_jeopardy += 1 if self.board.cells[dest].black_twobridges[coord].update_status(self.board) == Status.JEOPARDY else 0

        # update the relevant TwoBridge statuses of this cell's neighbours
        for neighbour in self.board.cells[coord].neighbours:
            for n_dest in self.board.cells[neighbour].white_twobridges:
                if coord not in self.board.cells[neighbour].white_twobridges[n_dest].depends:
                    continue
                temp_jeopardy += 1 if self.board.cells[neighbour].white_twobridges[n_dest].update_status(self.board) == Status.JEOPARDY else 0
                temp_jeopardy += 1 if self.board.cells[neighbour].black_twobridges[n_dest].update_status(self.board) == Status.JEOPARDY else 0

        self.jeopardized += temp_jeopardy/2
        return

    def set_piece(self, coord: Coord, color: Color) -> bool:
        """ Set a piece on an empty cell of our gameboard

        Parameters:
            coord: (Coord) coordinate to place the piece on
            color: (Color) what colour piece to place

        Returns: (bool)
            True if successful, False if the cell was not empty
        """
        if not self.board.set(coord, color):
            return False
        self.move_count += 1
        self.update_twobridges(coord)
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
        return self.set_piece(coord, self.opp)

    def sety(self, move: str) -> bool:
        """ Set Your [tile]. Tells the bot to play a move for itself

        Parameters:
            move: (str) A human-readable position on the board

        Returns: (bool)
            True if successful, False if the tile was not empty
        """
        coord = Coord(*Coord.str2cart(move))
        return self.set_piece(coord, self.color)

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

    def unset(self, move: str) -> bool:
        """ Tells the bot to set a tile as unused

        Parameters:
            move: (str) A human-readable position on the board

        Returns: (bool)
            True if the move has been unmade, False if the tile was alr empty
        """
        coord = Coord(*Coord.str2cart(move))
        if not self.board.unset(coord):
            return False
        self.update_twobridges(coord)
        return True

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


    def early_move(self) -> str:
        """ Determine what move to make if it is early game

        Returns: (str)
            Human-readable coordinate on which we decide to make our move
        """
        if self.move_count == 0:
            return "b2"
        if self.move_count == 1:
            if self.color == Color.WHITE:
                for coord in self.board.blacks:
                    if coord not in (Edges.LEFT, Edges.RIGHT):
                        first_move = coord
                if first_move.getx() == 1 or first_move.getx() == 10:
                    if first_move in (Coord(1, 10), Coord(10, 1)):
                        return "swap"
                else:
                    if first_move not in (Coord(2, 1), Coord(2, 2), Coord(9, 9), Coord(9, 10)):
                        return "swap"
                return "e6"  # didn't swap
            else:
                for coord in self.board.whites:
                    if coord not in (Edges.TOP, Edges.BOTTOM):
                        first_move = coord
                if first_move.gety() == 1 or first_move.gety() == 10:
                    if first_move in (Coord(10, 1), Coord(1, 10)):
                        return "swap"
                else:
                    if first_move not in (Coord(1, 2), Coord(2, 2), Coord(9, 9), Coord(10, 9)):
                        return "swap"
                return "f5"  # didn't swap
        if self.move_count == 2:
            if len(self.board.blacks) == 3 and len(self.board.whites) == 3:
                # swap move DID NOT occur. fight for control
                # TODO: figure out how to contest/block in early game
                return "BRUH"
            else:
                # swap move occurred. claim centre
                return "e6" if self.color == Color.WHITE else "f5"

    def late_move(self) -> str:
        """ Determine what move to make if several pieces are already on the board

        Returns:
            moveToPlay(str): position of where to make move
        """
        moveToPlay = ""
        
        #TODO add jeopordized flag to bot class, which will be set in update_twobridges
        # this way, we only do the following if we know we are jeopordized (saves time)
        if self.jeopardized > 0:
            if self.color == Color.WHITE:
                for coord in self.board.whites:
                    for destcoord in self.board.cells[coord].white_twobridges:
                        bridge = self.board.cells[coord].white_twobridges[destcoord]
                        if bridge.status == Status.JEOPARDY:
                            for depcoord in bridge.depends:
                                if self.board.cells[depcoord].color == Color.EMPTY:
                                    moveToPlay = depcoord
            else:
                for coord in self.board.blacks:
                    for destcoord in self.board.cells[coord].black_twobridges:
                        bridge = self.board.cells[coord].black_twobridges[destcoord]
                        if bridge.status == Status.JEOPARDY:
                            for depcoord in bridge.depends:
                                if self.board.cells[depcoord].color == Color.EMPTY:
                                    moveToPlay = depcoord
            self.jeopardized -= 1
            # resolve a jeopardized two bridge
            return str(moveToPlay)

        # get the path and cost of path for both ourselves and of our opponents            
        if self.color == Color.WHITE:
            playerPath, playerCost = self.dijkstra(Edges.TOP, Edges.BOTTOM, self.color)
            oppPath, oppCost = self.dijkstra(Edges.LEFT, Edges.RIGHT, self.opp)
        else:
            playerPath, playerCost = self.dijkstra(Edges.LEFT, Edges.RIGHT, self.color)
            oppPath, oppCost = self.dijkstra(Edges.TOP, Edges.BOTTOM, self.opp)

        # given the optimal path of coords, we extract which cells we want to play in:
        # Ideal cells include: completing TO-BE twobridges, intersections between our path and opponents path

        # if playerCost >>/> oppCost, consider a defensive move (cost measures how many pieces to secure path)
        # elif playerCost == 0, play to win // TODO introduce bot flag for gaurunteed win to bypass computation?
        # elif oppCost == 0, play to win (opp has garunteed win, play offensively to through them off)
        # else play offensively, we have the advantage (group with oppCost == 0)

        # search through both paths; identify how many more cells need to be played on to win
        # (cost only gives how many pieces needed to secure the path)

        playerMoves = [] # tuple list: stores moves we need to make alongside weight of the move
        oppMoves = []    # stores opps best move with weighting

        # weighting definition (us) (MIGHT WANT TO ADJUST):
        #       0 : cell already has piece, no need to play in it
        #       2 : cell is a dependancy of a successful two bridge (only one dependancy will be stored)
        #       3 : cell is an empty that needs to be played in
        #       5 : cell is a destination of a TO-BE twoBridge

        
        # origin = self.board.cells(playerPath[0])
        # if origin.color == self.color:
        #     playerMoves.append(origin, 0)
        # for i in range(len(playerPath-1)):
        #     origin = self.board.cells(playerPath[i])
        #     nextCoord = playerPath[i+1]
        #     # check the connection to nextCoord

        #     if nextCoord in origin.neighbours:
        #         if self.board.cells(nextCoord).color == self.color:
        #             # if next cell is friendly and neighbour, add with cost zero
        #             playerMoves.append(self.board.cells(playerPath[i+1]), 0)
        #             continue
        #         else:
        #             # if cell is neighbour and empty, add with cost 1
        #             playerMoves.append(self.board.cells(playerPath[i+1]), 1)
        #             continue
        #     # if the next cell is not a neighbour of previous, it must be a twobridge
        #     if self.color == Color.WHITE:
        #         for bridge in origin.white_twobridges:
        #             # search for which two bridge it is a part of
        #             if bridge.dest == nextCoord:
        #                 # identify what kind of two bridge it is
        #                 if bridge.status == Status.SUCCESS:
        #                     #######
        #                     # need to account for the symmetry of two-bridges
        #                     #######
        #                     pass

        # for i in range(len(oppPath)):            
        #     pass

        # # add weight of oppMoves to playerMoves when they have common elements, then:
        # moveToPlay = max(playerMoves)

        return moveToPlay

    def dijkstra(self, start: Cell, goal: Cell, player: Color) -> tuple:
        """ Returns an optimal path between start and goal

        Parameters:
            start (Cell): state from where to start search from
            goal (Cell): state we are trying to reach from start
            player (Color): the player that this search is done on behalf of

        Returns:
            (list[Coord]): a list that contains the coords in order that form an optimal path from start to goal
            g_value (int): an integer that represents the number of pieces that need to be played to secure this path
        """

        # start state has initial g value of 0; add to open and closed lists
        open = []
        start.g = 0
        heapq.heappush(open, start)
        closed = dict()
        closed[start.coord] = start
        
        # what is to be returned if no path is found (indicates something has gone wrong)
        final_g = -1
        path = []

        # run dijkstra's
        while len(open)> 0:
            # get the cheapest value in the open list, if it is the goal state, return it
            state = heapq.heappop(open) 
            if state == goal:
                # we have reached edge, meaning we found a path; create a list of all previous nodes and their parents
                final_g = state.g

                if player == Color.WHITE:
                    while state.white_parent != state.coord:
                        # while parent is not itself (while it isn't start state):
                        path.append(state.white_parent)     # add parent to path
                        state = self.board.cells[state.white_parent]     # set the state to be the parent
                else:
                    while state.black_parent != state.coord:
                        path.append(state.black_parent)
                        state = self.board.cells[state.black_parent]

                # return path (from start to goal) and number of pieces that need to be played
                path.reverse()
                return path, final_g
            
            # if cheapest is not goal state, check its children (neighbours and twobridges)
            # calculate and save each child's g-value seperately (don't update cell directly)
            children = []
            g_values = []

            # check all direct neighbours
            for node in self.board.cells[state.coord].neighbours:
                if self.board.cells[node].color == Color.EMPTY:
                    # if neighbour is empty, cost of 1 to claim the space
                    children.append(node)
                    g_values.append(state.g+1) 
                elif self.board.cells[node].color == player:
                    # if the neighbour is friendly piece, then the cost of claiming the space is zero
                    children.append(node)
                    g_values.append(state.g+0)

            # check two bridges of players color
            if player == Color.WHITE:
                for destcoord in self.board.cells[state.coord].white_twobridges:
                    bridge = self.board.cells[state.coord].white_twobridges[destcoord]
                    if bridge.status == Status.SUCCESS:
                        # if twobridged, then we are connected at cost of 0
                        children.append(bridge.dest)
                        g_values.append(state.g+0)
                    elif bridge.status == Status.READY:
                        # if all empty, dest connects to origin in 1 move
                        children.append(bridge.dest)
                        g_values.append(state.g+1)
                    elif bridge.status == Status.TO_BE:
                        # if TO_BE, then check whether it is because of piece in dest or orig
                        if state.color == player:
                            # 'forwards' twobridge
                            children.append(bridge.dest)
                            g_values.append(state.g+1)
                        else:
                            # 'backwards' twobridge
                            children.append(bridge.dest)
                            g_values.append(state.g+0)

            else:
                for destcoord in self.cells[state].black_twobridges:
                    bridge = self.board.cells[state.coord].black_twobridges[destcoord]
                    if bridge.status == Status.SUCCESS:
                        children.append(bridge.dest)
                        g_values.append(state.g+0)
                    elif bridge.status == Status.READY:
                        # if all empty, dest connects to origin in 1 move
                        children.append(bridge.dest)
                        g_values.append(state.g+1)
                    elif bridge.status == Status.TO_BE:
                        # if TO_BE, then check whether it is because of piece in dest or orig
                        if state.color == player:
                            # 'forwards' twobridge
                            children.append(bridge.dest)
                            g_values.append(state.g+1)
                        else:
                            # 'backwards' twobridge
                            children.append(bridge.dest)
                            g_values.append(state.g+0)
            
            for i in range(len(children)):
                child = children[i]
                current_g = g_values[i]

                # if the child (Coord) not in closed list:
                #       update corresponding Cell with parent and g-value and add to open and closed
                if child not in closed:
                    if player == Color.WHITE:
                        self.board.cells[child].white_parent = state.coord  
                        self.board.cells[child].g = current_g 
                    else:
                        self.board.cells[child].black_parent = state.coord  
                        self.board.cells[child].g = current_g 
                    heapq.heappush(open, self.board.cells[child])
                    closed[child] = self.board.cells[child]

                # if child in closed, but we found a better path to it, update accordingly
                elif current_g < closed[child].g:
                    if player == Color.WHITE:
                        self.board.cells[child].white_parent = state.coord  
                    else:
                        self.board.cells[child].black_parent = state.coord  
                    self.board.cells[child].g = current_g

                    # closed and open are lists of Cells, so by updating the cell, the lists are updated
                    # open must be reheapified to ensure integrity of heap
                    heapq.heapify(open)

        # if the loop has exited and no solution found, there is no solution, so return accordingly
        return path, final_g
