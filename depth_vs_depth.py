import random
import sys
import time

from board import PLAYER_ONE, PLAYER_TWO, Board
from minimax_player import MinimaxPlayer

OPENINGS = int(sys.argv[1]) if len(sys.argv) > 1 else 50
DEEP = int(sys.argv[2]) if len(sys.argv) > 2 else 4
SHALLOW = int(sys.argv[3]) if len(sys.argv) > 3 else 2
RANDOM_PLIES = 4


def play_from_opening(seed, player_one, player_two):
    rng = random.Random(seed)
    board = Board()
    for _ in range(RANDOM_PLIES):
        board.drop(rng.choice(board.legal_moves()))
    players = {PLAYER_ONE: player_one, PLAYER_TWO: player_two}
    while not board.is_over():
        col = players[board.current_player].choose_move(board)
        board.drop(col)
    return board.winner


deep = MinimaxPlayer(depth=DEEP)
shallow = MinimaxPlayer(depth=SHALLOW)

start = time.time()
wins = losses = draws = 0

for seed in range(OPENINGS):
    for deep_side in (PLAYER_ONE, PLAYER_TWO):
        if deep_side == PLAYER_ONE:
            winner = play_from_opening(seed, deep, shallow)
        else:
            winner = play_from_opening(seed, shallow, deep)
        if winner is None:
            draws += 1
        elif winner == deep_side:
            wins += 1
        else:
            losses += 1

games = OPENINGS * 2
elapsed = time.time() - start
print(f"Depth {DEEP} vs depth {SHALLOW}")
print(f"Games: {games} ({OPENINGS} random openings, each played from both sides)")
print(f"Depth {DEEP} wins: {wins}  Depth {SHALLOW} wins: {losses}  Draws: {draws}")
print(f"Depth {DEEP} win rate: {wins / games:.1%}")
print(f"Time: {elapsed:.1f} seconds")