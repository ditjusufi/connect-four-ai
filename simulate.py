from game import play_game
from players import RandomPlayer

GAMES = 1000
results = {1: 0, 2: 0, None: 0}

for i in range(GAMES):
    winner = play_game(RandomPlayer(seed=i), RandomPlayer(seed=GAMES + i))
    results[winner] += 1

print(f"Player 1 wins: {results[1]}")
print(f"Player 2 wins: {results[2]}")
print(f"Draws: {results[None]}")