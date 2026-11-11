from board import COLS, EMPTY, ROWS

LETTERS = ["a", "b", "c", "d", "e", "f", "g"]
NUMBERS = [1, 2, 3, 4, 5, 6]
SQUARES = [letter + str(number) for letter in LETTERS for number in NUMBERS]
VALUES = ["x", "o", "b"]
FEATURE_NAMES = [square + "_" + value for square in SQUARES for value in VALUES]


def encode_values(values):
    """One-hot encode a list of 42 square values ('x', 'o', 'b') into 126 numbers."""
    features = []
    for value in values:
        for option in VALUES:
            if value == option:
                features.append(1)
            else:
                features.append(0)
    return features


def row_to_features(row):
    """Convert one dataset row (a dict or pandas row with columns a1..g6) to 126 features."""
    values = [row[square] for square in SQUARES]
    return encode_values(values)


def board_row_for(number):
    """Return the Board grid row for dataset square number 1..6 (1 is the bottom)."""
    return ROWS - number


def board_to_features(board, to_move_player):
    """Convert a Board to 126 features, with to_move_player encoded as 'x'."""
    values = []
    for col in range(COLS):
        for number in NUMBERS:
            cell = board.grid[board_row_for(number)][col]
            if cell == EMPTY:
                values.append("b")
            elif cell == to_move_player:
                values.append("x")
            else:
                values.append("o")
    return encode_values(values)


def mirror_features(features):
    """Return the left-right mirror image of a 126-feature vector (a<->g, b<->f, c<->e)."""
    per_column = len(NUMBERS) * len(VALUES)
    mirrored = []
    for col in range(COLS - 1, -1, -1):
        start = col * per_column
        mirrored.extend(features[start:start + per_column])
    return mirrored


def canonical_key(features):
    """Return a key that is the same for a position and its mirror image."""
    original = tuple(int(value) for value in features)
    mirrored = tuple(int(value) for value in mirror_features(list(features)))
    return min(original, mirrored)
