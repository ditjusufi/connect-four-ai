from game import play_game
from minimax_player import MinimaxPlayer
from players import HumanPlayer

winner = play_game(HumanPlayer(), MinimaxPlayer(depth=4), verbose=True)
if winner is None:
    print("Draw")
elif winner == 1:
    print("You win")
else:
    print("The computer wins")