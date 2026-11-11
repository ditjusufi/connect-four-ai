import numpy as np

from board import Board
from medium_player import MediumPlayer


class StubModel:
    """A fake model that gives every position the same probabilities."""

    classes_ = np.array(["draw", "loss", "win"])

    def predict_proba(self, rows):
        """Return the same probabilities for every row."""
        return np.array([[0.2, 0.3, 0.5] for _ in rows])


class RisingStubModel:
    """A fake model whose loss probability grows with the row number."""

    classes_ = np.array(["draw", "loss", "win"])

    def predict_proba(self, rows):
        """Give each later row a higher chance of a loss for x."""
        probabilities = []
        for index in range(len(rows)):
            loss = 0.1 * index
            probabilities.append([0.0, loss, 1.0 - loss])
        return np.array(probabilities)


def play(board, columns):
    """Drop discs in the given columns, one after another."""
    for col in columns:
        board.drop(col)


def hybrid():
    """Return a MediumPlayer with rules and the stub model."""
    return MediumPlayer(model=StubModel())


def test_returns_a_legal_move_on_a_new_board():
    board = Board()
    assert hybrid().choose_move(board) in board.legal_moves()


def test_takes_an_immediate_win():
    board = Board()
    play(board, [0, 0, 1, 1, 2, 2])
    assert hybrid().choose_move(board) == 3


def test_blocks_an_immediate_loss():
    board = Board()
    play(board, [0, 0, 1, 1, 2])
    assert hybrid().choose_move(board) == 3


def test_avoids_a_move_that_hands_the_opponent_a_win():
    board = Board()
    play(board, [5, 4, 5, 6, 6, 5, 4])
    move = hybrid().choose_move(board)
    assert move != 3
    assert move in board.legal_moves()


def test_does_not_modify_the_board():
    board = Board()
    play(board, [3, 3, 4])
    before = [row[:] for row in board.grid]
    player_before = board.current_player
    moves_before = board.moves_played
    hybrid().choose_move(board)
    assert board.grid == before
    assert board.current_player == player_before
    assert board.moves_played == moves_before


def test_rules_only_picks_the_center_on_an_empty_board():
    player = MediumPlayer(use_model=False)
    assert player.choose_move(Board()) == 3


def test_model_picks_the_move_with_the_highest_score():
    player = MediumPlayer(model=RisingStubModel(), use_rules=False)
    assert player.choose_move(Board()) == 6
