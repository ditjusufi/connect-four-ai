import json
import random

import numpy as np

from board import Board
from medium_player import MediumPlayer

REGRESSION_FILE = "medium_player_regression.json"
POSITION_COUNT = 500
MAX_RANDOM_MOVES = 30


class WeightedStubModel:
    """A fake model with fixed random weights, so different positions get different scores."""

    classes_ = np.array(["draw", "loss", "win"])

    def __init__(self, seed=42):
        """Create the fixed weights from a seed."""
        self.weights = np.random.default_rng(seed).normal(size=(126, 3))

    def predict_proba(self, rows):
        """Turn each feature row into three probabilities that add up to 1."""
        scores = np.array(rows) @ self.weights
        exps = np.exp(scores - scores.max(axis=1, keepdims=True))
        return exps / exps.sum(axis=1, keepdims=True)


def seeded_position(seed):
    """Play up to 30 seeded random moves, stopping before any move that would end the game."""
    rng = random.Random(seed)
    board = Board()
    for _ in range(rng.randint(0, MAX_RANDOM_MOVES)):
        child = board.copy()
        child.drop(rng.choice(board.legal_moves()))
        if child.is_over():
            break
        board = child
    return board


def regression_players():
    """Return the three MediumPlayer variants, all using the same stub model."""
    model = WeightedStubModel()
    return {
        "hybrid": MediumPlayer(model=model),
        "rules_only": MediumPlayer(model=model, use_model=False),
        "model_only": MediumPlayer(model=model, use_rules=False),
    }


def current_moves():
    """Return the move each variant chooses for each of the 500 seeded positions."""
    moves = {}
    for name, player in regression_players().items():
        moves[name] = []
        for seed in range(POSITION_COUNT):
            moves[name].append(player.choose_move(seeded_position(seed)))
    return moves


def main():
    """Record the current moves to the regression file."""
    with open(REGRESSION_FILE, "w") as file:
        json.dump(current_moves(), file)
    print(f"Saved {POSITION_COUNT} moves per variant to {REGRESSION_FILE}")


if __name__ == "__main__":
    main()
