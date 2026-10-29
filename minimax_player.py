import math

from board import COLS, EMPTY, PLAYER_ONE, PLAYER_TWO, ROWS

WIN_SCORE = 1_000_000
MOVE_ORDER = [3, 2, 4, 1, 5, 0, 6]


def other(player):
    return PLAYER_TWO if player == PLAYER_ONE else PLAYER_ONE


def score_window(window, player):
    opponent = other(player)
    mine = window.count(player)
    theirs = window.count(opponent)
    empty = window.count(EMPTY)
    if mine == 3 and empty == 1:
        return 5
    if mine == 2 and empty == 2:
        return 2
    if theirs == 3 and empty == 1:
        return -4
    return 0


def evaluate(board, player):
    grid = board.grid
    center = COLS // 2
    score = 3 * sum(1 for row in range(ROWS) if grid[row][center] == player)
    for row in range(ROWS):
        for col in range(COLS):
            for d_row, d_col in ((0, 1), (1, 0), (1, 1), (1, -1)):
                end_row = row + 3 * d_row
                end_col = col + 3 * d_col
                if 0 <= end_row < ROWS and 0 <= end_col < COLS:
                    window = [grid[row + i * d_row][col + i * d_col] for i in range(4)]
                    score += score_window(window, player)
    return score


def alphabeta(board, depth, alpha, beta, maximizing, player):
    if board.winner is not None:
        if board.winner == player:
            return WIN_SCORE + depth
        return -WIN_SCORE - depth
    if board.is_full():
        return 0
    if depth == 0:
        return evaluate(board, player)

    legal = board.legal_moves()
    moves = [col for col in MOVE_ORDER if col in legal]

    if maximizing:
        value = -math.inf
        for col in moves:
            child = board.copy()
            child.drop(col)
            value = max(value, alphabeta(child, depth - 1, alpha, beta, False, player))
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return value

    value = math.inf
    for col in moves:
        child = board.copy()
        child.drop(col)
        value = min(value, alphabeta(child, depth - 1, alpha, beta, True, player))
        beta = min(beta, value)
        if alpha >= beta:
            break
    return value


class MinimaxPlayer:
    def __init__(self, depth=4):
        self.depth = depth

    def choose_move(self, board):
        player = board.current_player
        legal = board.legal_moves()
        best_score = -math.inf
        best_move = None
        alpha = -math.inf
        for col in [c for c in MOVE_ORDER if c in legal]:
            child = board.copy()
            child.drop(col)
            score = alphabeta(child, self.depth - 1, alpha, math.inf, False, player)
            if score > best_score:
                best_score = score
                best_move = col
            alpha = max(alpha, best_score)
        return best_move