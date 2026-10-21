from game import play_game
from players import HumanPlayer, RandomPlayer

winner = play_game(HumanPlayer(), RandomPlayer(), verbose=True)
if winner is None:
    print("Draw")
elif winner == 1:
    print("You win")
else:
    print("The computer wins")