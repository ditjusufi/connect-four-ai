import numpy as np

from board import Board
from features import board_to_features, mirror_features
from train_models import add_mirrors, group_label, grouped_split


def random_position(seed):
    """Return the features of a board after 8 seeded random moves."""
    rng = np.random.default_rng(seed)
    board = Board()
    for _ in range(8):
        legal = board.legal_moves()
        board.drop(legal[rng.integers(len(legal))])
    return board_to_features(board, board.current_player)


def synthetic_dataset():
    """Build a tiny dataset where every position also appears as its mirror image."""
    features = []
    labels = []
    for seed in range(60):
        position = random_position(seed)
        label = ["win", "loss", "draw"][seed % 3]
        features.append(position)
        labels.append(label)
        features.append(mirror_features(position))
        labels.append(label)
    X = np.array(features)
    y = np.array(labels)
    groups = np.array([group_label(row) for row in X])
    return X, y, groups


def test_no_canonical_key_in_both_train_and_test():
    X, y, groups = synthetic_dataset()
    train_index, test_index = grouped_split(X, y, groups)
    assert len(train_index) > 0
    assert len(test_index) > 0
    assert set(groups[train_index]).isdisjoint(set(groups[test_index]))


def test_mirror_augmentation_keeps_label_and_group():
    X, y, groups = synthetic_dataset()
    X_aug, y_aug, groups_aug = add_mirrors(X, y, groups)
    assert len(X_aug) == 2 * len(X)
    assert list(y_aug[len(X):]) == list(y)
    assert list(groups_aug[len(X):]) == list(groups)
