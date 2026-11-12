from board import Board
from medium_player import MediumPlayer
from regression_cases import WeightedStubModel, seeded_position


def play(board, columns):
    """Drop discs in the given columns, one after another."""
    for col in columns:
        board.drop(col)


def hybrid():
    """Return a hybrid MediumPlayer that uses the stub model."""
    return MediumPlayer(model=WeightedStubModel())


def test_reason_is_win():
    board = Board()
    play(board, [0, 0, 1, 1, 2, 2])
    assert hybrid().explain_move(board) == {"column": 3, "reason": "win", "scores": {}}


def test_reason_is_block():
    board = Board()
    play(board, [0, 0, 1, 1, 2])
    assert hybrid().explain_move(board)["reason"] == "block"


def test_reason_is_model_with_a_score_per_candidate():
    result = hybrid().explain_move(Board())
    assert result["reason"] == "model"
    assert sorted(result["scores"]) == [0, 1, 2, 3, 4, 5, 6]
    assert result["scores"][result["column"]] == max(result["scores"].values())


def test_reason_is_center_without_model():
    result = MediumPlayer(use_model=False).explain_move(Board())
    assert result == {"column": 3, "reason": "center", "scores": {}}


def test_explain_move_agrees_with_choose_move():
    player = hybrid()
    for seed in range(50):
        board = seeded_position(seed)
        assert player.explain_move(board)["column"] == player.choose_move(board)
