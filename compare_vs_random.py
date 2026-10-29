import sys
import time

from game import play_game
from minimax_player import MinimaxPlayer
from players import RandomPlayer

GAMES = int(sys.argv[1]) if len(sys.argv) > 1 else 200
DEPTH = int(sys.argv[2]) if len(sys.argv) > 2 else 4

start = time.time()
wins = losses = draws = 0

for i in range(GAMES):
    ai = MinimaxPlayer(depth=DEPTH)
    rnd = RandomPlayer(seed=i)
    if i % 2 == 0:
        winner = play_game(ai, rnd)
        ai_side = 1
    else:
        winner = play_game(rnd, ai)
        ai_side = 2
    if winner is None:
        draws += 1
    elif winner == ai_side:
        wins += 1
    else:
        losses += 1

elapsed = time.time() - start
print(f"Depth: {DEPTH}")
print(f"Games: {GAMES}")
print(f"Wins: {wins}  Losses: {losses}  Draws: {draws}")
print(f"Win rate: {wins / GAMES:.1%}")
print(f"Time: {elapsed:.1f} seconds")