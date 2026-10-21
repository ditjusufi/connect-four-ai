import random


class RandomPlayer:
    def __init__(self, seed=None):
        self.rng = random.Random(seed)

    def choose_move(self, board):
        return self.rng.choice(board.legal_moves())


class HumanPlayer:
    def choose_move(self, board):
        legal = board.legal_moves()
        while True:
            text = input("Your move (column 1-7): ")
            if text.isdigit() and int(text) - 1 in legal:
                return int(text) - 1
            print("That move is not allowed. Try again.")