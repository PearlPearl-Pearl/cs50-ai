"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board. X always moves first
    """
    def count_x(board):
        x_num=0
        pairs=[(i,j) for i in range(3) for j in range(3)]
        for i,j in pairs:
            if board[i][j]==X:
                x_num+=1
        return x_num

    def count_o(board):
        o_num=0
        pairs=[(i,j) for i in range(3) for j in range(3)]
        for i,j in pairs:
            if board[i][j]==O:
                o_num+=1
        return o_num

    x_count=count_x(board)
    o_count=count_o(board)

    while x_count==0 or x_count==o_count:
        return X
    
    return O

def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    action_set=set()
    for i in range(3):
        for j in range(3):
            if not board[i][j]:
                action_set.add((i,j))
    return action_set
    raise NotImplementedError


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    if action not in actions(board):
        raise Exception("Invalid action")
    temp_result=copy.deepcopy(board)

    i,j=action
    temp_result[i][j]=player(board)
    return temp_result
    raise NotImplementedError

def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    def horizontal_win(board):
        for row in board:
            if row[0] is None or not all(element==row[0] for element in row):
                continue
            return row[0]

    def diagonal_win(board):
        main_diag=list(zip(range(3), range(3)))
        off_diag=list(zip(range(3), range(2,-1,-1)))

        main_check=[]
        off_check=[]

        for i,j in main_diag:
            main_check.append(board[i][j])
        for i,j in off_diag:
            off_check.append(board[i][j])
        
        if all(main_check[i]==main_check[0] for i in range(len(main_check))):
            return main_check[0]
        if all(off_check[i]==off_check[0] for i in range(len(off_check))):
            return off_check[0]

    def vertical_win(board):
        first_check=[]
        second_check=[]
        third_check=[]

        for i in range(3):
            first_check.append(board[i][0])

        for i in range(3):
            second_check.append(board[i][1])

        for i in range(3):
            third_check.append(board[i][2])

        if all(first_check[i]==first_check[0] for i in range(len(board))):
            return first_check[0]

        if all(second_check[i]==second_check[0] for i in range(len(board))):
            return second_check[0]

        if all(third_check[i]==third_check[0] for i in range(len(board))):
            return third_check[0]

    if horizontal_win(board):
        return horizontal_win(board)
    elif vertical_win(board):
        return vertical_win(board)
    elif diagonal_win(board):
        return diagonal_win(board)
    return None
    raise NotImplementedError


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    def check_full(board):
        tracker=True
        for row in board:
            if not all(row):
                tracker=False
        return tracker
    
    if winner(board) or check_full(board):
        return True
    return False
    raise NotImplementedError


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    while terminal(board):
        if winner(board)==X:
            return 1
        elif winner(board)==O:
            return -1
        return 0
        
    raise NotImplementedError


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    def minvalue(board):
        while not terminal(board):
            options=actions(board)
            v=math.inf
            for move in options:
                v=min(v, maxvalue(result(board, move)))
            return v
        return utility(board)    
    
    def maxvalue(board):
        while not terminal(board):
            options=actions(board)
            v=-math.inf
            for move in options:
                v=max(v, minvalue(result(board, move)))
            return v
        return utility(board)    

    # X is MAX and O is MIN
    # get all the available moves for that board
    while not terminal(board):
        if player(board)==X:
            pairs=[]
            for move in actions(board):
                pairs.append((move, minvalue(result(board, move))))
            
            max_tuple=max(pairs, key=lambda x: x[1])
            
            return max_tuple[0]
        
        if player(board)==O:
            pairs=[]
            for move in actions(board):
                pairs.append((move, maxvalue(result(board, move))))
            
            min_tuple=min(pairs, key=lambda x: x[1])
            
            return min_tuple[0]
    return None

# print(terminal([[X, X, O],
#             [EMPTY, O, X],
#             [EMPTY, EMPTY, O]]))