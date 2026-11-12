import os

from medium_player import MediumPlayer
from minimax_player import MinimaxPlayer
from players import RandomPlayer

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(PROJECT_DIR, "models", "medium_model.joblib")
HARD_DEPTH = 4
DEFAULT_SEED = 42
LEVELS = [("easy", "Easy"), ("medium", "Medium"), ("hard", "Hard")]


def level_names():
    """Return the internal names of the levels, in menu order."""
    names = []
    for name, _ in LEVELS:
        names.append(name)
    return names


def display_name(level):
    """Return the display text for a level name, for example 'Easy' for 'easy'."""
    for name, text in LEVELS:
        if name == level:
            return text
    raise ValueError(f"Unknown level: {level}")


def make_medium_player(model_path=MODEL_PATH):
    """Return the hybrid MediumPlayer, or raise a clear error if the model file is missing."""
    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Model file not found: {model_path}. Run 'python train_models.py' first."
        )
    return MediumPlayer(model_path=model_path)


def make_player(level, seed=DEFAULT_SEED):
    """Return the computer player for 'easy', 'medium' or 'hard'."""
    if level == "easy":
        return RandomPlayer(seed=seed)
    if level == "medium":
        return make_medium_player()
    if level == "hard":
        return MinimaxPlayer(depth=HARD_DEPTH)
    raise ValueError(f"Unknown level: {level}. Choose one of {level_names()}.")
