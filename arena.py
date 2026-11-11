import math
import random

from board import PLAYER_ONE, PLAYER_TWO, Board

OPENING_MOVES = 4
Z_95 = 1.96


def play_from_opening(seed, player_one, player_two):
    """Play 4 seeded random moves, then let the two players finish the game; return the winner."""
    rng = random.Random(seed)
    board = Board()
    for _ in range(OPENING_MOVES):
        board.drop(rng.choice(board.legal_moves()))
    players = {PLAYER_ONE: player_one, PLAYER_TWO: player_two}
    while not board.is_over():
        col = players[board.current_player].choose_move(board)
        board.drop(col)
    return board.winner


def wilson_interval(wins, games, z=Z_95):
    """Return the Wilson confidence interval (low, high) for a win rate."""
    if games == 0:
        return 0.0, 0.0
    rate = wins / games
    denominator = 1 + z * z / games
    center = (rate + z * z / (2 * games)) / denominator
    margin = z * math.sqrt(rate * (1 - rate) / games + z * z / (4 * games * games)) / denominator
    return center - margin, center + margin


def evaluate_matchup(player_a, player_b, openings, label=None):
    """Play every opening with player_a as first and as second player; return player_a's results."""
    wins = losses = draws = 0
    for count, seed in enumerate(openings, start=1):
        for a_side in (PLAYER_ONE, PLAYER_TWO):
            if a_side == PLAYER_ONE:
                winner = play_from_opening(seed, player_a, player_b)
            else:
                winner = play_from_opening(seed, player_b, player_a)
            if winner is None:
                draws += 1
            elif winner == a_side:
                wins += 1
            else:
                losses += 1
        if label is not None and count % 10 == 0:
            print(f"   {label}: {2 * count}/{2 * len(openings)} games played")
    games = wins + losses + draws
    low, high = wilson_interval(wins, games)
    return {
        "games": games,
        "wins": wins,
        "losses": losses,
        "draws": draws,
        "win_rate": wins / games,
        "ci_low": low,
        "ci_high": high,
    }
