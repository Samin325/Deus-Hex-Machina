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
                    path.append(state.coord)
                    while state.white_parent != state.coord:
                        # while parent is not itself (while it isn't start state):
                        path.append(state.white_parent)     # add parent to path
                        state = self.board.cells[state.white_parent]     # set the state to be the parent
                else:
                    path.append(state.coord)
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
                for destcoord in self.board.cells[state.coord].black_twobridges:
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

    def late_move(self) -> str:
        """ Determine what move to make if several pieces are already on the board

        Returns:
            moveToPlay(str): position of where to make move
        """
        moveToPlay = ""
        
        # if we have more than 0 jeopordized twobridges, we want to save/destroy it/them; saving/destroying is priority move
        # loop through and find where we are jeopardized; set moveToPlay to the last one found
        if self.jeopardized > 0:
            for coord in self.board.cells:
                for destcoord in self.board.cells[coord].white_twobridges:
                    bridge = self.board.cells[coord].white_twobridges[destcoord]
                    if bridge.status == Status.JEOPARDY:
                        for depcoord in bridge.depends:
                            if self.board.cells[depcoord].color == Color.EMPTY:
                                moveToPlay = depcoord
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
            playerPath, playerCost = self.dijkstra(self.board.cells[Edges.TOP], self.board.cells[Edges.BOTTOM], self.color)
            oppPath, oppCost = self.dijkstra(self.board.cells[Edges.LEFT], self.board.cells[Edges.RIGHT], self.opp)
        else:
            playerPath, playerCost = self.dijkstra(self.board.cells[Edges.LEFT], self.board.cells[Edges.RIGHT], self.color)
            oppPath, oppCost = self.dijkstra(self.board.cells[Edges.TOP], self.board.cells[Edges.BOTTOM], self.opp)

        playerMoves = [] # tuple list: stores moves we need to make alongside weight of the move
        oppMoves = []    # stores opps best move with weighting

        # weighting definition:
        #       0 : cell already has piece, no need to play in it (we may want to exclude these from the list)
        #     0.5 : cell is a dependancy of a successful bridge (very little reason for us to play here)
        #       1 : cell is a dependancy of a two bridge (only one dependancy will be stored)
        #       2 : cell is an empty neighbour that needs to be played in
        #       4 : cell is a destination of a TO-BE twoBridge

        # for the following, we may want to exlcude weight 0s
        # define playerMoves if we are white
        if self.color == Color.WHITE:
            for i in range(1, len(playerPath)):
                node = self.board.cells[playerPath[i]]
                if playerPath[i] in self.board.cells[playerPath[i-1]].neighbours:
                    # if the first state returned by dijkstra is a neighbour of parent
                   if node.color == Color.EMPTY:
                        playerMoves.append((node.coord, 2))
                else:
                    # if the state returned by dijkstra is not a neighbour of the parent, it must be twobridge
                    if self.board.cells[playerPath[i-1]].white_twobridges[playerPath[i]].status == Status.TO_BE or \
                            self.board.cells[playerPath[i-1]].white_twobridges[playerPath[i]].status == Status.READY:
                        # if dijkstra returned a TO_BE or READY, then add dest with weight 4 and deps at weight 1
                        playerMoves.append((self.board.cells[playerPath[i-1]].white_twobridges[playerPath[i]].depends[0], 1))
                        playerMoves.append((playerPath[i], 4))
                    else:
                        # if two bridge was not a TO_BE or READY, then it must have been SUCCESS, which means
                        playerMoves.append((self.board.cells[playerPath[i-1]].white_twobridges[playerPath[i]].depends[0], 0.5))
            
            # def oppMoves (they are black)
            for i in range(1, len(oppPath)):
                node = self.board.cells[oppPath[i]]
                if node.coord in self.board.cells[oppPath[i-1]].neighbours:
                    # if the state returned by dijkstra is a neighbour of the parent
                    if node.color == Color.EMPTY: 
                        oppMoves.append((node.coord, 2))
                else:
                    # if the state returned by dijkstra is not a neighbour, it must be twobridge
                    if self.board.cells[oppPath[i-1]].black_twobridges[oppPath[i]].status == Status.TO_BE or \
                            self.board.cells[oppPath[i-1]].black_twobridges[oppPath[i]].status == Status.READY:
                        # if dijkstra returned a TO_BE or READY, then add dest with weight 4 and deps at weight 1
                        oppMoves.append((self.board.cells[oppPath[i-1]].black_twobridges[oppPath[i]].depends[0], 1))
                        oppMoves.append((oppPath[i], 4))
                    else:
                        # if two bridge was not a TO_BE or READY, then it must have been SUCCESS, which means
                        oppMoves.append((self.board.cells[oppPath[i-1]].black_twobridges[oppPath[i]].depends[0], 0.5))

        else:
            # player (we) is black
            for i in range(1, len(playerPath)):
                node = self.board.cells[playerPath[i]]
                if node.coord in self.board.cells[playerPath[i-1]].neighbours:
                    # if the first state returned by dijkstra is a neighbour of the edge
                    if node.color == Color.EMPTY:
                        playerMoves.append((node.coord, 2))
                else:
                    # if the first state returned by dijkstra is not a neighbour of the edge, it must be twobridge
                    if self.board.cells[playerPath[i-1]].black_twobridges[playerPath[i]].status == Status.TO_BE or \
                            self.board.cells[playerPath[i-1]].black_twobridges[playerPath[i]].status == Status.READY:
                        # if dijkstra returned a TO_BE or READY, then add dest with weight 4 and deps at weight 1
                        playerMoves.append((self.board.cells[playerPath[i-1]].black_twobridges[playerPath[i]].depends[0], 1))
                        playerMoves.append((playerPath[i], 4))
                    else:
                        # if two bridge was not a TO_BE or READY, then it must have been SUCCESS, which means
                        playerMoves.append((self.board.cells[playerPath[i-1]].black_twobridges[playerPath[i]].depends[0], 0.5))

            # def oppMoves (they are white)
            for i in range(1, len(oppPath)):
                node = self.board.cells[oppPath[i]]
                if node.coord in self.board.cells[oppPath[i-1]].neighbours:
                    # if the first state returned by dijkstra is a neighbour of the edge
                    if node.color == Color.EMPTY:
                        oppMoves.append((node.coord, 2))
                else:
                    # if the first state returned by dijkstra is not a neighbour of the edge, it must be twobridge
                    if self.board.cells[oppPath[i-1]].white_twobridges[oppPath[i]].status == Status.TO_BE or \
                            self.board.cells[oppPath[i-1]].white_twobridges[oppPath[i]].status == Status.READY:
                        # if dijkstra returned a TO_BE or READY, then add dest with weight 4 and deps at weight 1
                        oppMoves.append((self.board.cells[oppPath[i-1]].white_twobridges[oppPath[i]].depends[0], 1))
                        oppMoves.append((oppPath[i], 4))
                    else:
                        # if two bridge was not a TO_BE or READY, then it must have been SUCCESS, which means
                        oppMoves.append((self.board.cells[oppPath[i-1]].white_twobridges[oppPath[i]].depends[0], 0.5))

        # if we have not garunteed us a win, play more cautiously 
        #       (consider the weights of our opponents as well as ours) - update playerMoves to reflect this
        if playerCost != 0:
            # get the intersection of coords between playerMoves and oppMoves
            playerSet = set()
            oppSet = set()
            for pair in playerMoves:
                playerSet.add(pair[0])
            for pair in oppMoves:
                oppSet.add(pair[0])
            intersection = playerSet.intersection(oppSet)

            # for every coord in the intersection, add the weights of the two moves together and store in playerMoves
            for coord in intersection:
                for i in range(len(playerMoves)):
                    if playerMoves[i][0] == coord:
                        for j in range(len(oppMoves)):
                            # search through the list until we find the positions where the coords intersect
                            # sum the weights and store in playerMoves
                            if playerMoves[i][0] == oppMoves[j][0]:
                                # the following addition statement may be changed to account for differences in g-values
                                # (diff in g-value will represent how bad of a defensive move we need to play)
                                temp = list (playerMoves[i])
                                temp[1] = playerMoves[i][1] + 1.5*oppMoves[j][1]
                                playerMoves[i] = tuple(temp)
                                break
                        break
        
        # potentially implement
        # if playerCost >>/> oppCost, consider a defensive move (cost measures how many pieces to secure path)
        # elif oppCost == 0, play to win (opp has garunteed win, play offensively to through them off)
        # else play offensively, we have the advantage (group with oppCost == 0)

        # find the coord with the max weight in playerMoves
        # initialize the moveToPlay to be first of playerMoves to compare other values against
        moveToPlay = playerMoves[0][0]
        highest_weight = playerMoves[0][1]
        for move in playerMoves:
            # if we find a higher weighting, then set move to play equal to this weighting
            if move[1] > highest_weight:
                moveToPlay = move[0]
                highest_weight = move[1]

        return str(moveToPlay)

    def make_move(self) -> None:
        """ Generates a move, plays it for itself, and prints it to stdout

        For now, the move is randomly selected from all empty positions
        """
        if self.move_count >= 4:
            move = self.late_move()
        else:
            move = self.early_move()
        self.sety(str(move))
        print(move)
        return
