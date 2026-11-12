from arena import evaluate_matchup, play_from_opening, wilson_interval
from players import RandomPlayer


def test_wilson_interval_matches_a_known_value():
    low, high = wilson_interval(50, 100)
    assert round(low, 3) == 0.404
    assert round(high, 3) == 0.596


def test_wilson_interval_stays_between_zero_and_one():
    low, high = wilson_interval(10, 10)
    assert 0.0 <= low <= high <= 1.0


def test_same_seed_gives_the_same_game():
    first = play_from_opening(7, RandomPlayer(seed=1), RandomPlayer(seed=2))
    second = play_from_opening(7, RandomPlayer(seed=1), RandomPlayer(seed=2))
    assert first == second


def test_each_opening_is_played_from_both_sides():
    result = evaluate_matchup(RandomPlayer(seed=1), RandomPlayer(seed=2), [0, 1, 2])
    assert result["games"] == 6
    assert result["wins"] + result["losses"] + result["draws"] == 6
