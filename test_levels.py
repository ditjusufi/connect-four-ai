import os

import pytest

from levels import LEVELS, MODEL_PATH, display_name, make_medium_player, make_player
from medium_player import MediumPlayer
from minimax_player import MinimaxPlayer
from players import RandomPlayer


def test_easy_is_a_random_player():
    assert isinstance(make_player("easy"), RandomPlayer)


def test_hard_is_minimax_with_depth_4():
    player = make_player("hard")
    assert isinstance(player, MinimaxPlayer)
    assert player.depth == 4


@pytest.mark.skipif(not os.path.exists(MODEL_PATH), reason="trained model not available")
def test_medium_is_the_hybrid_medium_player():
    player = make_player("medium")
    assert isinstance(player, MediumPlayer)
    assert player.use_rules
    assert player.use_model


def test_unknown_level_raises_an_error():
    with pytest.raises(ValueError):
        make_player("impossible")


def test_missing_model_gives_a_clear_error(tmp_path):
    missing = os.path.join(tmp_path, "no_model.joblib")
    with pytest.raises(FileNotFoundError, match="train_models.py"):
        make_medium_player(missing)


def test_model_path_does_not_depend_on_the_working_folder():
    assert os.path.isabs(MODEL_PATH)


def test_levels_have_display_names():
    assert [text for _, text in LEVELS] == ["Easy", "Medium", "Hard"]
    assert display_name("hard") == "Hard"
