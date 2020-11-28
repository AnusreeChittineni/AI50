""" Tic Tac Toe Player """

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """ Returns starting state of the board. """

    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """ Returns player who has the next turn on a board. """

    # Intializes the values of total_X and total_O to 0
    total_X = 0
    total_O = 0

    # Loops through each row in the board
    for row in board:

        # Add the total number of X's in current row
        total_X += row.count(X)

        # Add the total number of O's in current row
        total_O += row.count(O)

    # If total number of X's and O's is equal, then it is X's turn
    if total_X == total_O:

        return X

    # Otherwise it is O's turn
    else:

        return O


def actions(board):
    """ Returns set of all possible actions (i, j) available on the board. """

    # Initialize empty set to store possible actions that can be taken by current player
    possible_actions = set()

    # Loop through each row on the board
    for i in range(3):

        # Loop through each cell in current row
        for j in range(3):

            # If current cell is empty, then add cell coordinates to possible actions set
            if board[i][j] == EMPTY:

                possible_actions.add((i,j))

    # Return final set of possible actions for current board variation
    return possible_actions


def result(board, action):
    """ Returns the board that results from making move (i, j) on the board. """

    # Make a copy of the inputted board variation to make changes to
    board_copy = copy.deepcopy(board)

    # Intialize i to the row number of the action
    i = action[0]

    # Intialize j to the column number of the action
    j = action[1]

    # Used to determine if eror was raised, but will be handled later
    try:

        # If cell is not empty, raise error
        if board_copy[i][j] != EMPTY:

            raise IndexError

        # Else return new board state by changing the board copy
        else:

            # Set value of cell to current player
            board_copy[i][j] = player(board)

        return board_copy

    # If error is raised, return this message
    except IndexError:

        print("Cell is not empty! You cannot make a move in this cell!")


def winner(board):
    """ Returns the winner of the game, if there is one. """

    for i in range(3):

        ### Checks rows ###

        # Checks if all the cells in a row are equal and the first cell in the row is not empty
        if (board[i][0] == board[i][1] == board[i][2]) and (board[i][0] != EMPTY):

            # Returns the value of the first cell in the winning row
            return board[i][0]

        ### Checks columns ###

        # Checks if all the cells in a column are equal and the first cell in the column is not empty
        elif (board[0][i] == board[1][i] == board[2][i]) and (board[0][i] != EMPTY):

            # Returns the value of the first cell in the winnning column
            return board[0][i]

    ### Checks Diagonals ###

    # Checks if all cells along the left or right diagonal are equal and the center cell is not empty
    if ((board[0][0] == board[1][1] == board[2][2]) or (board[0][2] == board[1][1] == board[2][0])) and (board[1][1] != EMPTY):

        # If condition is met, then return the value of the center cell
        return board[1][1]

    # Returns none if none of the above conditions are met
    return None


def terminal(board):
    """ Returns True if game is over, False otherwise. """

    # Checks if winner(board) returns either X or O, meaning the game is over
    if (winner(board) == X) or (winner(board) == O):

        return True

    # Intializes variable to 0
    total_EMPTY = 0

    # Loops through each row to determine the total umber of empty cells
    for row in board:

        total_EMPTY += row.count(EMPTY)

    # If the total number of empty cells is 0, then game is over
    if total_EMPTY == 0:

        return True

    # If neither of the above is true, then game is still in progress
    else:

        return False


def utility(board):
    """ Returns 1 if X has won the game, -1 if O has won, 0 otherwise. """

    ### Note: Only called if terminal(board) returns true ###

    # If winner(board) returns X then X won
    if winner(board) == X:

        return 1

    # If winner(board) returns O then O won
    elif winner(board) == O:

        return -1

    # Else return 0, meaning there was a tie
    else:

        return 0


def minimax(board):
    """ Returns the optimal action for the current player on the board. """

    # Checks if current board state is terminal
    if terminal(board):

        # If so then return None
        return None

    # Checks if it is X's turn
    if player(board) == X:

        # Intializes v to -infinity, in order to establish a current max value
        v = -math.inf

        # Loops through all possible actions that can be taken by the player on the current board state
        for action in actions(board):

            # Intializes k to the min value you can get from the current board state
            k = min_value(result(board, action))

            # If k is greater than v than set v to k and best move to the current action
            if k > v:

                v = k

                best_move = action

    # Checks if it is O's turn
    elif player(board) == O:

        # Intializes v to infinity, in order to establish a current min value
        v = math.inf

        # Loops through all possible actions that can be taken by the player on the current board state
        for action in actions(board):

            # Intializes k to the min value you can get from the current board state
            k = max_value(result(board, action))

            # If k is less than v than set v to k and best move to the current action
            if k < v:

                v = k

                best_move = action

    # return best_move for AI player
    return best_move


def max_value(board):

    # If the game is over with current board, then return value of untility(board)
    if terminal(board) == True:

        return utility(board)

    # Else
    else:
        v = -math.inf

        for action in actions(board):

            v = max(v, min_value(result(board, action)))

        return v


def min_value(board):

    # If the game is over with current board, then return value of untility(board)
    if terminal(board):

        return utility(board)

    # Else
    else:

        v = math.inf

        for action in actions(board):

            v = min(v, max_value(result(board, action)))

        return v

