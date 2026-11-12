from board import PLAYER_ONE, PLAYER_TWO, Board
from levels import LEVELS, make_player

QUIT = "quit"
FIRST_PLAYER_OPTIONS = [("you", "You"), ("computer", "Computer")]
SYMBOLS = {PLAYER_ONE: "X", PLAYER_TWO: "O"}


class QuitGame(Exception):
    """Raised when the player types q at any prompt."""


def parse_menu_choice(text, options):
    """Return the option for a menu number like '2', QUIT for 'q', or None if the input is invalid."""
    cleaned = text.strip().lower()
    if cleaned == "q":
        return QUIT
    if not cleaned.isdigit():
        return None
    number = int(cleaned)
    if 1 <= number <= len(options):
        return options[number - 1]
    return None


def parse_column(text, legal_moves):
    """Return the 0-based column for input '1'..'7', QUIT for 'q', or None if the move is not allowed."""
    cleaned = text.strip().lower()
    if cleaned == "q":
        return QUIT
    if not cleaned.isdigit():
        return None
    col = int(cleaned) - 1
    if col in legal_moves:
        return col
    return None


def parse_yes_no(text):
    """Return True for 'y'/'yes', False for 'n'/'no', QUIT for 'q', or None otherwise."""
    cleaned = text.strip().lower()
    if cleaned == "q":
        return QUIT
    if cleaned in ("y", "yes"):
        return True
    if cleaned in ("n", "no"):
        return False
    return None


def result_message(winner, human_side):
    """Return the end-of-game message from the human player's point of view."""
    if winner is None:
        return "It's a draw."
    if winner == human_side:
        return "You win!"
    return "The computer wins."


def read_line(prompt):
    """Read one line of input; treat the end of the input as 'q'."""
    try:
        return input(prompt)
    except EOFError:
        return "q"


def ask_menu(title, options, labels):
    """Show a numbered menu and keep asking until the player picks a valid option."""
    print(title)
    for number, label in enumerate(labels, start=1):
        print(f"  {number}. {label}")
    while True:
        choice = parse_menu_choice(read_line("Choice (q to quit): "), options)
        if choice == QUIT:
            raise QuitGame()
        if choice is not None:
            return choice
        print("Please type one of the numbers shown, or q to quit.")


def ask_column(board):
    """Keep asking for a column until the player types a legal one."""
    legal = board.legal_moves()
    while True:
        col = parse_column(read_line("Your move (column 1-7, q to quit): "), legal)
        if col == QUIT:
            raise QuitGame()
        if col is not None:
            return col
        print("That move is not allowed. Choose an open column from 1 to 7.")


def ask_play_again():
    """Ask whether to play another game and return True or False."""
    while True:
        answer = parse_yes_no(read_line("Play again? (y/n): "))
        if answer == QUIT:
            raise QuitGame()
        if answer is not None:
            return answer
        print("Please type y or n.")


def choose_settings():
    """Ask for the difficulty and who goes first; return (level, human_side)."""
    level_options = [name for name, _ in LEVELS]
    level_labels = [text for _, text in LEVELS]
    level = ask_menu("Choose the difficulty:", level_options, level_labels)
    first_options = [name for name, _ in FIRST_PLAYER_OPTIONS]
    first_labels = [text for _, text in FIRST_PLAYER_OPTIONS]
    first = ask_menu("Who goes first?", first_options, first_labels)
    if first == "you":
        return level, PLAYER_ONE
    return level, PLAYER_TWO


def play_one_game(level, human_side):
    """Play one game in the terminal and print the result."""
    board = Board()
    computer = make_player(level)
    print(f"You are {SYMBOLS[human_side]}. X moves first.")
    print(board)
    print()
    while not board.is_over():
        if board.current_player == human_side:
            col = ask_column(board)
        else:
            col = computer.choose_move(board)
            print(f"The computer chose column {col + 1}.")
        board.drop(col)
        print(board)
        print()
    print(result_message(board.winner, human_side))


def main():
    """Run the menu and games until the player quits."""
    print("Connect Four")
    try:
        while True:
            level, human_side = choose_settings()
            play_one_game(level, human_side)
            if not ask_play_again():
                break
    except QuitGame:
        pass
    except FileNotFoundError as error:
        print(error)
    print("Goodbye.")


if __name__ == "__main__":
    main()
