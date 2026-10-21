ROWS = 6
COLS = 7
EMPTY = 0
PLAYER_ONE = 1
PLAYER_TWO = 2
SYMBOLS = {EMPTY: ".", PLAYER_ONE: "X", PLAYER_TWO: "O"}


class Board:
    def __init__(self):
        self.grid = [[EMPTY] * COLS for _ in range(ROWS)]
        self.current_player = PLAYER_ONE
        self.winner = None
        self.moves_played = 0

    def copy(self):
        clone = Board()
        clone.grid = [row[:] for row in self.grid]
        clone.current_player = self.current_player
        clone.winner = self.winner
        clone.moves_played = self.moves_played
        return clone

    def legal_moves(self):
        if self.winner is not None:
            return []
        return [col for col in range(COLS) if self.grid[0][col] == EMPTY]

    def drop(self, col):
        if col not in self.legal_moves():
            raise ValueError(f"Illegal move: column {col}")
        for row in range(ROWS - 1, -1, -1):
            if self.grid[row][col] == EMPTY:
                self.grid[row][col] = self.current_player
                self.moves_played += 1
                if self._wins_at(row, col):
                    self.winner = self.current_player
                else:
                    self.current_player = (
                        PLAYER_TWO if self.current_player == PLAYER_ONE else PLAYER_ONE
                    )
                return row

    def _wins_at(self, row, col):
        player = self.grid[row][col]
        for d_row, d_col in ((0, 1), (1, 0), (1, 1), (1, -1)):
            count = 1
            for sign in (1, -1):
                r = row + sign * d_row
                c = col + sign * d_col
                while 0 <= r < ROWS and 0 <= c < COLS and self.grid[r][c] == player:
                    count += 1
                    r += sign * d_row
                    c += sign * d_col
            if count >= 4:
                return True
        return False

    def is_full(self):
        return self.moves_played == ROWS * COLS

    def is_over(self):
        return self.winner is not None or self.is_full()

    def __str__(self):
        lines = [" ".join(SYMBOLS[cell] for cell in row) for row in self.grid]
        lines.append(" ".join(str(col + 1) for col in range(COLS)))
        return "\n".join(lines)