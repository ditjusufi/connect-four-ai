from board import PLAYER_ONE, PLAYER_TWO
from play_cli import QUIT, parse_column, parse_menu_choice, parse_yes_no, result_message

OPTIONS = ["easy", "medium", "hard"]


def test_menu_accepts_a_valid_number():
    assert parse_menu_choice("1", OPTIONS) == "easy"
    assert parse_menu_choice(" 3 ", OPTIONS) == "hard"


def test_menu_rejects_invalid_input():
    assert parse_menu_choice("0", OPTIONS) is None
    assert parse_menu_choice("4", OPTIONS) is None
    assert parse_menu_choice("abc", OPTIONS) is None
    assert parse_menu_choice("", OPTIONS) is None
    assert parse_menu_choice("-1", OPTIONS) is None


def test_menu_q_means_quit():
    assert parse_menu_choice("q", OPTIONS) == QUIT
    assert parse_menu_choice("Q", OPTIONS) == QUIT


def test_column_converts_to_zero_based():
    assert parse_column("1", [0, 1, 2, 3, 4, 5, 6]) == 0
    assert parse_column("7", [0, 1, 2, 3, 4, 5, 6]) == 6


def test_column_rejects_invalid_or_full_columns():
    assert parse_column("8", [0, 1, 2, 3, 4, 5, 6]) is None
    assert parse_column("0", [0, 1, 2, 3, 4, 5, 6]) is None
    assert parse_column("x", [0, 1, 2, 3, 4, 5, 6]) is None
    assert parse_column("", [0, 1, 2, 3, 4, 5, 6]) is None
    assert parse_column("4", [0, 1, 2, 4, 5, 6]) is None


def test_column_q_means_quit():
    assert parse_column("q", [0, 1]) == QUIT


def test_yes_no():
    assert parse_yes_no("y") is True
    assert parse_yes_no("No") is False
    assert parse_yes_no("maybe") is None
    assert parse_yes_no("q") == QUIT


def test_result_message():
    assert result_message(None, PLAYER_ONE) == "It's a draw."
    assert result_message(PLAYER_ONE, PLAYER_ONE) == "You win!"
    assert result_message(PLAYER_TWO, PLAYER_ONE) == "The computer wins."
