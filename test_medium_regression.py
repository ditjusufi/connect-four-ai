import json
import os

from regression_cases import REGRESSION_FILE, current_moves

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))


def test_medium_player_moves_are_unchanged():
    with open(os.path.join(PROJECT_DIR, REGRESSION_FILE)) as file:
        recorded = json.load(file)
    assert current_moves() == recorded
