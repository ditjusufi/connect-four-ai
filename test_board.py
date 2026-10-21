import pytest

from board import PLAYER_ONE, PLAYER_TWO, ROWS, Board


def play(board, columns):
    for col in columns:
        board.drop(col)


def test_new_board_has_seven_legal_moves():
    assert Board().legal_moves() == [0, 1, 2, 3, 4, 5, 6]


def test_disc_falls_to_the_bottom():
    board = Board()
    row = board.drop(3)
    assert row == ROWS - 1
    assert board.grid[ROWS - 1][3] == PLAYER_ONE


def test_players_alternate():
    board = Board()
    board.drop(0)
    assert board.current_player == PLAYER_TWO


def test_horizontal_win():
    board = Board()
    play(board, [0, 0, 1, 1, 2, 2, 3])
    assert board.winner == PLAYER_ONE


def test_vertical_win():
    board = Board()
    play(board, [0, 1, 0, 1, 0, 1, 0])
    assert board.winner == PLAYER_ONE


def test_diagonal_win_up_right():
    board = Board()
    play(board, [0, 1, 1, 2, 3, 2, 2, 3, 6, 3, 3])
    assert board.winner == PLAYER_ONE


def test_diagonal_win_up_left():
    board = Board()
    play(board, [6, 5, 5, 4, 3, 4, 4, 3, 0, 3, 3])
    assert board.winner == PLAYER_ONE


def test_full_column_is_illegal():
    board = Board()
    for _ in range(ROWS):
        board.drop(0)
    assert 0 not in board.legal_moves()
    with pytest.raises(ValueError):
        board.drop(0)


def test_no_moves_after_game_is_over():
    board = Board()
    play(board, [0, 0, 1, 1, 2, 2, 3])
    assert board.legal_moves() == []
    with pytest.raises(ValueError):
        board.drop(4)