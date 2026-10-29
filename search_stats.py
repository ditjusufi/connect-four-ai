import math
import random

from board import Board
from minimax_player import MOVE_ORDER, WIN_SCORE, evaluate

counter = {"nodes": 0}


def minimax(board, depth, maximizing, player):
    counter["nodes"] += 1
    if board.winner is not None:
        if board.winner == player:
            return WIN_SCORE + depth
        return -WIN_SCORE - depth
    if board.is_full():
        return 0
    if depth == 0:
        return evaluate(board, player)

    legal = board.legal_moves()
    scores = []
    for col in [c for c in MOVE_ORDER if c in legal]:
        child = board.copy()
        child.drop(col)
        scores.append(minimax(child, depth - 1, not maximizing, player))
    return max(scores) if maximizing else min(scores)


def alphabeta(board, depth, alpha, beta, maximizing, player):
    counter["nodes"] += 1
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


def count_nodes(board, depth):
    player = board.current_player

    counter["nodes"] = 0
    plain_value = minimax(board, depth, True, player)
    plain_nodes = counter["nodes"]

    counter["nodes"] = 0
    pruned_value = alphabeta(board, depth, -math.inf, math.inf, True, player)
    pruned_nodes = counter["nodes"]

    assert plain_value == pruned_value
    return plain_nodes, pruned_nodes


def mid_game_board(seed, plies):
    rng = random.Random(seed)
    board = Board()
    for _ in range(plies):
        board.drop(rng.choice(board.legal_moves()))
    return board


def report(title, board, depths):
    print(title)
    print(f"{'Depth':>5} {'Minimax nodes':>15} {'Alpha-beta nodes':>18} {'Fewer nodes':>12}")
    for depth in depths:
        plain, pruned = count_nodes(board, depth)
        saved = 1 - pruned / plain
        print(f"{depth:>5} {plain:>15,} {pruned:>18,} {saved:>11.1%}")
    print()


report("Empty board", Board(), [2, 3, 4, 5, 6])
report("Mid-game board (8 random moves)", mid_game_board(1, 8), [2, 3, 4, 5, 6])