from board import EMPTY, PLAYER_ONE, PLAYER_TWO, Board
from gui import column_from_x, end_message, find_winning_line, level_from_display

CELL = 80
LEFT = 20


def play(board, columns):
    """Drop discs in the given columns, one after another."""
    for col in columns:
        board.drop(col)


def test_column_from_x_at_the_left_edge():
    assert column_from_x(LEFT, CELL, LEFT) == 0
    assert column_from_x(LEFT - 1, CELL, LEFT) is None


def test_column_from_x_at_the_right_edge():
    assert column_from_x(LEFT + 7 * CELL - 1, CELL, LEFT) == 6
    assert column_from_x(LEFT + 7 * CELL, CELL, LEFT) is None


def test_column_from_x_between_columns():
    assert column_from_x(LEFT + CELL - 1, CELL, LEFT) == 0
    assert column_from_x(LEFT + CELL, CELL, LEFT) == 1


def test_horizontal_win():
    board = Board()
    play(board, [0, 0, 1, 1, 2, 2, 3])
    assert find_winning_line(board.grid) == [(5, 0), (5, 1), (5, 2), (5, 3)]


def test_vertical_win():
    board = Board()
    play(board, [0, 1, 0, 1, 0, 1, 0])
    assert find_winning_line(board.grid) == [(2, 0), (3, 0), (4, 0), (5, 0)]


def test_diagonal_down_right_win():
    board = Board()
    play(board, [6, 5, 5, 4, 3, 4, 4, 3, 0, 3, 3])
    assert find_winning_line(board.grid) == [(2, 3), (3, 4), (4, 5), (5, 6)]


def test_diagonal_down_left_win():
    board = Board()
    play(board, [0, 1, 1, 2, 3, 2, 2, 3, 6, 3, 3])
    assert find_winning_line(board.grid) == [(2, 3), (3, 2), (4, 1), (5, 0)]


def test_no_win():
    board = Board()
    play(board, [0, 1, 2, 3])
    assert find_winning_line(board.grid) is None


def test_empty_board_has_no_win():
    grid = [[EMPTY] * 7 for _ in range(6)]
    assert find_winning_line(grid) is None


def test_level_from_display_and_end_message():
    assert level_from_display("Hard") == "hard"
    assert end_message(None, PLAYER_ONE) == "Draw"
    assert end_message(PLAYER_TWO, PLAYER_TWO) == "You win!"
    assert end_message(PLAYER_ONE, PLAYER_TWO) == "Computer wins!"
