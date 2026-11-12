import joblib
import numpy as np

from board import COLS, PLAYER_ONE, PLAYER_TWO
from features import board_to_features

CENTER = COLS // 2
DRAW_WEIGHT = 0.5


def other_player(player):
    """Return the opponent of the given player."""
    if player == PLAYER_ONE:
        return PLAYER_TWO
    return PLAYER_ONE


def distance_from_center(col):
    """Return how far a column is from the center column."""
    return abs(col - CENTER)


def center_first(moves):
    """Return the moves sorted from the center outwards (left side first on ties)."""
    return sorted(moves, key=distance_from_center)


def winning_moves(board, player):
    """Return the columns where the given player would win by dropping a disc now."""
    wins = []
    for col in board.legal_moves():
        child = board.copy()
        child.current_player = player
        child.drop(col)
        if child.winner == player:
            wins.append(col)
    return wins


def gives_opponent_a_win(board, col):
    """Return True if playing col lets the opponent win on their next move."""
    child = board.copy()
    child.drop(col)
    if child.winner is not None:
        return False
    return len(winning_moves(child, child.current_player)) > 0


def safe_moves(board, moves):
    """Remove moves that hand the opponent an immediate win, unless every move does."""
    safe = []
    for col in moves:
        if not gives_opponent_a_win(board, col):
            safe.append(col)
    if len(safe) == 0:
        return moves
    return safe


class MediumPlayer:
    def __init__(self, model=None, model_path="models/medium_model.joblib",
                 use_rules=True, use_model=True):
        """Set up the player; load the model from model_path if none is given."""
        self.use_rules = use_rules
        self.use_model = use_model
        self.model = model
        if self.use_model and self.model is None:
            self.model = joblib.load(model_path)

    def choose_move(self, board):
        """Pick a column using the rules first and then the model."""
        me = board.current_player
        opponent = other_player(me)
        moves = center_first(board.legal_moves())

        if self.use_rules:
            my_wins = center_first(winning_moves(board, me))
            if len(my_wins) > 0:
                return my_wins[0]
            their_wins = center_first(winning_moves(board, opponent))
            if len(their_wins) > 0:
                return their_wins[0]
            moves = safe_moves(board, moves)

        if not self.use_model:
            return moves[0]
        return self.best_move_by_model(board, moves)

    def move_scores(self, board, moves):
        """Score each move as P(loss for x) + 0.5 * P(draw for x), x being the opponent."""
        opponent = other_player(board.current_player)
        rows = []
        for col in moves:
            child = board.copy()
            child.drop(col)
            rows.append(board_to_features(child, opponent))
        probabilities = self.model.predict_proba(np.array(rows))
        classes = list(self.model.classes_)
        loss_index = classes.index("loss")
        draw_index = classes.index("draw")
        scores = []
        for row in probabilities:
            scores.append(row[loss_index] + DRAW_WEIGHT * row[draw_index])
        return scores

    def best_move_by_model(self, board, moves):
        """Return the move with the highest model score; earlier (more central) moves win ties."""
        scores = self.move_scores(board, moves)
        best_move = moves[0]
        best_score = scores[0]
        for index in range(1, len(moves)):
            if scores[index] > best_score:
                best_move = moves[index]
                best_score = scores[index]
        return best_move
