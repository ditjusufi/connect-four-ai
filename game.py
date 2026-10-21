from board import PLAYER_ONE, PLAYER_TWO, Board


def play_game(player_one, player_two, verbose=False):
    board = Board()
    players = {PLAYER_ONE: player_one, PLAYER_TWO: player_two}
    while not board.is_over():
        player = players[board.current_player]
        col = player.choose_move(board)
        board.drop(col)
        if verbose:
            print(board)
            print()
    return board.winner