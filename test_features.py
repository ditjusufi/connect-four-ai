from board import PLAYER_ONE, PLAYER_TWO, Board
from features import (
    SQUARES,
    board_to_features,
    canonical_key,
    mirror_features,
    row_to_features,
)


def play(board, columns):
    """Drop discs in the given columns, one after another."""
    for col in columns:
        board.drop(col)


def empty_row():
    """Return a dataset-style row where every square is blank."""
    return {square: "b" for square in SQUARES}


def test_vector_length_is_126():
    assert len(row_to_features(empty_row())) == 126
    assert len(board_to_features(Board(), PLAYER_ONE)) == 126


def test_dataset_row_and_board_give_the_same_vector():
    board = Board()
    play(board, [0, 0, 3, 6])
    row = empty_row()
    row["a1"] = "x"
    row["a2"] = "o"
    row["d1"] = "x"
    row["g1"] = "o"
    assert board_to_features(board, PLAYER_ONE) == row_to_features(row)


def test_player_to_move_is_encoded_as_x():
    board = Board()
    play(board, [2])
    row = empty_row()
    row["c1"] = "o"
    assert board.current_player == PLAYER_TWO
    assert board_to_features(board, PLAYER_TWO) == row_to_features(row)


def test_mirror_twice_gives_the_original():
    board = Board()
    play(board, [0, 1, 1, 5, 6])
    features = board_to_features(board, PLAYER_ONE)
    assert mirror_features(mirror_features(features)) == features


def test_mirror_matches_mirrored_board():
    board = Board()
    play(board, [0, 1, 1])
    mirrored_board = Board()
    play(mirrored_board, [6, 5, 5])
    features = board_to_features(board, PLAYER_TWO)
    assert mirror_features(features) == board_to_features(mirrored_board, PLAYER_TWO)


def test_position_and_mirror_have_the_same_canonical_key():
    board = Board()
    play(board, [0, 1, 1, 5, 6])
    features = board_to_features(board, PLAYER_ONE)
    assert canonical_key(features) == canonical_key(mirror_features(features))
