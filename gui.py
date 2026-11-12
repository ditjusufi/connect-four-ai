import tkinter as tk
from tkinter import ttk

from board import COLS, EMPTY, PLAYER_ONE, PLAYER_TWO, ROWS, Board
from levels import LEVELS, make_player

CELL_SIZE = 80
MARGIN = 20
DISC_PADDING = 8
BOARD_WIDTH = COLS * CELL_SIZE + 2 * MARGIN
BOARD_HEIGHT = ROWS * CELL_SIZE + 2 * MARGIN
COMPUTER_DELAY_MS = 300
DIRECTIONS = [(0, 1), (1, 0), (1, 1), (1, -1)]

BOARD_COLOR = "#1f4fbf"
HOVER_COLOR = "#3a6fe0"
EMPTY_COLOR = "white"
HUMAN_COLOR = "#e03030"
COMPUTER_COLOR = "#f2d024"
WIN_OUTLINE = "#22cc44"
BACKGROUND = "#f0f0f0"

FIRST_CHOICES = ["You", "Computer"]


def column_from_x(x, cell_size, left_margin):
    """Return the board column under the x pixel position, or None if x is outside the board."""
    if x < left_margin:
        return None
    col = int((x - left_margin) // cell_size)
    if col >= COLS:
        return None
    return col


def cells_in_line(row, col, d_row, d_col):
    """Return the four (row, col) cells starting at (row, col) in one direction, or None if off the board."""
    cells = []
    for step in range(4):
        r = row + step * d_row
        c = col + step * d_col
        if r < 0 or r >= ROWS or c < 0 or c >= COLS:
            return None
        cells.append((r, c))
    return cells


def same_player(grid, cells):
    """Return True if all cells hold the same disc and are not empty."""
    first_row, first_col = cells[0]
    player = grid[first_row][first_col]
    if player == EMPTY:
        return False
    for r, c in cells:
        if grid[r][c] != player:
            return False
    return True


def find_winning_line(grid):
    """Return the four (row, col) cells of a winning line, or None if nobody has four in a row."""
    for row in range(ROWS):
        for col in range(COLS):
            for d_row, d_col in DIRECTIONS:
                cells = cells_in_line(row, col, d_row, d_col)
                if cells is not None and same_player(grid, cells):
                    return cells
    return None


def level_from_display(text):
    """Return the level name ('easy', 'medium', 'hard') for a display text like 'Medium'."""
    for name, display in LEVELS:
        if display == text:
            return name
    raise ValueError(f"Unknown level: {text}")


def end_message(winner, human_side):
    """Return the status text for a finished game."""
    if winner is None:
        return "Draw"
    if winner == human_side:
        return "You win!"
    return "Computer wins!"


class ConnectFourApp:
    def __init__(self, root):
        """Build the window and start the first game."""
        self.root = root
        self.root.title("Connect Four")
        self.root.resizable(False, False)
        self.root.configure(background=BACKGROUND)
        self.level_var = tk.StringVar(value="Medium")
        self.first_var = tk.StringVar(value="You")
        self.status_var = tk.StringVar(value="")
        self.pending_job = None
        self.build_controls()
        self.build_canvas()
        self.new_game()

    def build_controls(self):
        """Create the difficulty and first-player dropdowns, the New Game button and the status label."""
        frame = tk.Frame(self.root, background=BACKGROUND)
        frame.pack(padx=10, pady=8)
        level_texts = [display for _, display in LEVELS]
        tk.Label(frame, text="Difficulty:", background=BACKGROUND).grid(row=0, column=0, padx=4)
        ttk.Combobox(frame, textvariable=self.level_var, values=level_texts,
                     state="readonly", width=9).grid(row=0, column=1, padx=4)
        tk.Label(frame, text="Who starts:", background=BACKGROUND).grid(row=0, column=2, padx=4)
        ttk.Combobox(frame, textvariable=self.first_var, values=FIRST_CHOICES,
                     state="readonly", width=9).grid(row=0, column=3, padx=4)
        tk.Button(frame, text="New Game", command=self.new_game).grid(row=0, column=4, padx=8)
        tk.Label(self.root, textvariable=self.status_var, background=BACKGROUND,
                 font=("Segoe UI", 14, "bold")).pack(pady=4)

    def build_canvas(self):
        """Create the board canvas and connect mouse events."""
        self.canvas = tk.Canvas(self.root, width=BOARD_WIDTH, height=BOARD_HEIGHT,
                                background=BACKGROUND, highlightthickness=0)
        self.canvas.pack(padx=10, pady=(0, 10))
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Motion>", self.on_motion)
        self.canvas.bind("<Leave>", self.on_leave)

    def new_game(self):
        """Start a new game using the current dropdown choices."""
        if self.pending_job is not None:
            self.root.after_cancel(self.pending_job)
            self.pending_job = None
        self.board = Board()
        self.winning_cells = None
        self.hover_col = None
        self.thinking = False
        self.game_over = False
        if self.first_var.get() == "You":
            self.human_side = PLAYER_ONE
        else:
            self.human_side = PLAYER_TWO
        try:
            self.computer = make_player(level_from_display(self.level_var.get()))
        except FileNotFoundError as error:
            self.game_over = True
            self.status_var.set(str(error))
            self.draw()
            return
        self.after_move()

    def humans_turn(self):
        """Return True if the human may drop a disc right now."""
        if self.game_over or self.thinking:
            return False
        return self.board.current_player == self.human_side

    def on_click(self, event):
        """Drop the human's disc in the clicked column if that move is allowed."""
        if not self.humans_turn():
            return
        col = column_from_x(event.x, CELL_SIZE, MARGIN)
        if col is None or col not in self.board.legal_moves():
            return
        self.board.drop(col)
        self.after_move()

    def on_motion(self, event):
        """Highlight the column under the mouse."""
        col = column_from_x(event.x, CELL_SIZE, MARGIN)
        if col != self.hover_col:
            self.hover_col = col
            self.draw()

    def on_leave(self, event):
        """Remove the column highlight when the mouse leaves the board."""
        self.hover_col = None
        self.draw()

    def after_move(self):
        """Update the screen and decide what happens next: game end, computer move or human move."""
        if self.board.is_over():
            self.finish_game()
        elif self.board.current_player == self.human_side:
            self.status_var.set("Your turn")
        else:
            self.thinking = True
            self.status_var.set("Computer is thinking...")
            self.pending_job = self.root.after(COMPUTER_DELAY_MS, self.computer_move)
        self.draw()

    def computer_move(self):
        """Let the computer choose and drop its disc."""
        self.pending_job = None
        col = self.computer.choose_move(self.board)
        self.board.drop(col)
        self.thinking = False
        self.after_move()

    def finish_game(self):
        """Lock the board, remember the winning line and show the result."""
        self.game_over = True
        self.winning_cells = find_winning_line(self.board.grid)
        self.status_var.set(end_message(self.board.winner, self.human_side))

    def disc_color(self, cell):
        """Return the fill color for a grid cell value."""
        if cell == EMPTY:
            return EMPTY_COLOR
        if cell == self.human_side:
            return HUMAN_COLOR
        return COMPUTER_COLOR

    def draw(self):
        """Redraw the whole board."""
        self.canvas.delete("all")
        self.canvas.create_rectangle(MARGIN, MARGIN, BOARD_WIDTH - MARGIN, BOARD_HEIGHT - MARGIN,
                                     fill=BOARD_COLOR, outline=BOARD_COLOR)
        if self.hover_col is not None and self.humans_turn():
            left = MARGIN + self.hover_col * CELL_SIZE
            self.canvas.create_rectangle(left, MARGIN, left + CELL_SIZE, BOARD_HEIGHT - MARGIN,
                                         fill=HOVER_COLOR, outline=HOVER_COLOR)
        for row in range(ROWS):
            for col in range(COLS):
                self.draw_disc(row, col)

    def draw_disc(self, row, col):
        """Draw one slot or disc, with a thick outline if it is part of the winning line."""
        left = MARGIN + col * CELL_SIZE + DISC_PADDING
        top = MARGIN + row * CELL_SIZE + DISC_PADDING
        right = left + CELL_SIZE - 2 * DISC_PADDING
        bottom = top + CELL_SIZE - 2 * DISC_PADDING
        outline = BOARD_COLOR
        width = 1
        if self.winning_cells is not None and (row, col) in self.winning_cells:
            outline = WIN_OUTLINE
            width = 6
        self.canvas.create_oval(left, top, right, bottom, fill=self.disc_color(self.board.grid[row][col]),
                                outline=outline, width=width)


def main():
    """Open the Connect Four window."""
    root = tk.Tk()
    ConnectFourApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
