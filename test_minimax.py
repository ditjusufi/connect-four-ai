from board import Board
from minimax_player import MinimaxPlayer


def play(board, columns):
    for col in columns:
        board.drop(col)


def test_returns_a_legal_move_on_a_new_board():
    board = Board()
    move = MinimaxPlayer(depth=3).choose_move(board)
    assert move in board.legal_moves()


def test_takes_an_immediate_win():
    board = Board()
    play(board, [0, 0, 1, 1, 2, 2])
    assert MinimaxPlayer(depth=2).choose_move(board) == 3


def test_blocks_an_immediate_loss():
    board = Board()
    play(board, [0, 0, 1, 1, 2])
    assert MinimaxPlayer(depth=2).choose_move(board) == 3


def test_does_not_change_the_original_board():
    board = Board()
    play(board, [3, 3, 4])
    before = [row[:] for row in board.grid]
    MinimaxPlayer(depth=3).choose_move(board)
    assert board.grid == before