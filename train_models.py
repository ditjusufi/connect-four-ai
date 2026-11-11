import os
import time

import joblib
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)
from sklearn.model_selection import GridSearchCV, StratifiedGroupKFold
from sklearn.neural_network import MLPClassifier

from features import canonical_key, mirror_features, row_to_features

matplotlib.use("Agg")

DATA_PATH = "data/connect4.csv"
MODEL_PATH = "models/medium_model.joblib"
RESULTS_DIR = "results"
CLASS_ORDER = ["loss", "draw", "win"]
SEED = 42
MAX_MODEL_MB = 50


def group_label(features):
    """Turn the canonical key of a position into a short string used as its group."""
    return "".join(str(value) for value in canonical_key(features))


def load_dataset(path=DATA_PATH):
    """Load the CSV and return features X, labels y and mirror-safe groups."""
    df = pd.read_csv(path)
    rows = df.to_dict("records")
    X = np.array([row_to_features(row) for row in rows])
    y = df["class"].to_numpy()
    groups = np.array([group_label(features) for features in X])
    return X, y, groups


def grouped_split(X, y, groups):
    """Split 80/20 so a group never appears on both sides, stratified by class."""
    splitter = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=SEED)
    train_index, test_index = next(splitter.split(X, y, groups))
    return train_index, test_index


def add_mirrors(X, y, groups):
    """Return the data plus the mirror image of every position, with the same label and group."""
    mirrored = np.array([mirror_features(list(features)) for features in X])
    X_all = np.vstack([X, mirrored])
    y_all = np.concatenate([y, y])
    groups_all = np.concatenate([groups, groups])
    return X_all, y_all, groups_all


def print_class_balance(name, y):
    """Print how many examples of each class a set contains."""
    print(f"{name}: {len(y)} positions")
    for label in CLASS_ORDER:
        count = int(np.sum(y == label))
        print(f"   {label:5} {count:6}  ({count / len(y):.1%})")


def model_candidates():
    """Return each classifier with its small hyperparameter grid."""
    return {
        "LogisticRegression": (
            LogisticRegression(max_iter=2000, random_state=SEED),
            {"C": [0.1, 1, 10]},
        ),
        "RandomForest": (
            RandomForestClassifier(random_state=SEED),
            {"n_estimators": [100, 200], "max_depth": [12, 20]},
        ),
        "MLP": (
            MLPClassifier(early_stopping=True, random_state=SEED),
            {"hidden_layer_sizes": [(64,), (128, 64)], "alpha": [1e-4, 1e-3]},
        ),
    }


def tune_model(estimator, grid, X, y, groups):
    """Run GridSearchCV with 5-fold grouped CV, choosing by macro F1."""
    folds = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=SEED)
    search = GridSearchCV(estimator, grid, scoring="f1_macro", cv=folds, n_jobs=-1)
    search.fit(X, y, groups=groups)
    return search


def best_by_cv(searches):
    """Return the name of the model with the highest cross-validation score."""
    best_name = None
    best_score = -1.0
    for name, search in searches.items():
        if search.best_score_ > best_score:
            best_name = name
            best_score = search.best_score_
    return best_name


def majority_baseline(y_train, y_test):
    """Return the test accuracy of always predicting the training majority class."""
    labels, counts = np.unique(y_train, return_counts=True)
    majority = labels[np.argmax(counts)]
    return majority, float(np.mean(y_test == majority))


def evaluate(model, X_test, y_test):
    """Return test accuracy, macro F1, per-class scores and the confusion matrix."""
    predictions = model.predict(X_test)
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_test, predictions, labels=CLASS_ORDER, zero_division=0
    )
    return {
        "predictions": predictions,
        "accuracy": accuracy_score(y_test, predictions),
        "macro_f1": f1_score(y_test, predictions, average="macro"),
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "matrix": confusion_matrix(y_test, predictions, labels=CLASS_ORDER),
    }


def save_confusion_matrix(name, matrix):
    """Save a confusion matrix picture to results/confusion_<name>.png."""
    display = ConfusionMatrixDisplay(matrix, display_labels=CLASS_ORDER)
    display.plot(cmap="Blues", values_format="d")
    plt.title(f"{name} (test set)")
    plt.tight_layout()
    path = os.path.join(RESULTS_DIR, f"confusion_{name}.png")
    plt.savefig(path)
    plt.close()
    return path


def comparison_row(name, search, scores, baseline, selected):
    """Build one row of the model comparison table."""
    row = {
        "model": name,
        "best_params": str(search.best_params_),
        "cv_macro_f1": round(search.best_score_, 4),
        "test_accuracy": round(scores["accuracy"], 4),
        "test_macro_f1": round(scores["macro_f1"], 4),
        "baseline_accuracy": round(baseline, 4),
        "selected": selected,
    }
    for index, label in enumerate(CLASS_ORDER):
        row[f"{label}_precision"] = round(scores["precision"][index], 4)
        row[f"{label}_recall"] = round(scores["recall"][index], 4)
        row[f"{label}_f1"] = round(scores["f1"][index], 4)
    return row


def save_model(model):
    """Save the model to models/ and return its size in megabytes."""
    os.makedirs("models", exist_ok=True)
    joblib.dump(model, MODEL_PATH, compress=3)
    return os.path.getsize(MODEL_PATH) / (1024 * 1024)


def no_mirror_experiment(selected_search, X_train, y_train, X_test, y_test, with_scores):
    """Retrain the selected model without mirror augmentation and print the difference."""
    model = clone(selected_search.best_estimator_)
    model.fit(X_train, y_train)
    without_scores = evaluate(model, X_test, y_test)
    print("Extra experiment: selected model with and without mirror augmentation")
    print(f"   {'':22} {'accuracy':>9} {'macro F1':>9}")
    print(f"   {'with augmentation':22} {with_scores['accuracy']:9.4f} {with_scores['macro_f1']:9.4f}")
    print(f"   {'without augmentation':22} {without_scores['accuracy']:9.4f} {without_scores['macro_f1']:9.4f}")
    accuracy_change = with_scores["accuracy"] - without_scores["accuracy"]
    f1_change = with_scores["macro_f1"] - without_scores["macro_f1"]
    print(f"   {'difference (with - w/o)':22} {accuracy_change:+9.4f} {f1_change:+9.4f}")
    table = pd.DataFrame([
        {"training_data": "with mirror augmentation",
         "test_accuracy": round(with_scores["accuracy"], 4),
         "test_macro_f1": round(with_scores["macro_f1"], 4)},
        {"training_data": "without mirror augmentation",
         "test_accuracy": round(without_scores["accuracy"], 4),
         "test_macro_f1": round(without_scores["macro_f1"], 4)},
    ])
    table.to_csv(os.path.join(RESULTS_DIR, "augmentation_experiment.csv"), index=False)


def main():
    """Load data, split, tune three models, evaluate on the test set and save the best."""
    os.makedirs(RESULTS_DIR, exist_ok=True)
    start = time.time()

    X, y, groups = load_dataset()
    train_index, test_index = grouped_split(X, y, groups)
    X_train, y_train, groups_train = X[train_index], y[train_index], groups[train_index]
    X_test, y_test = X[test_index], y[test_index]
    shared = set(groups_train) & set(groups[test_index])
    print_class_balance("Training set", y_train)
    print_class_balance("Test set", y_test)
    print(f"Canonical keys shared by train and test: {len(shared)}")

    X_aug, y_aug, groups_aug = add_mirrors(X_train, y_train, groups_train)
    print(f"Training set after mirror augmentation: {len(y_aug)} positions")
    print()

    searches = {}
    for name, (estimator, grid) in model_candidates().items():
        print(f"Tuning {name} with grid {grid} ...")
        tic = time.time()
        searches[name] = tune_model(estimator, grid, X_aug, y_aug, groups_aug)
        print(f"   best params {searches[name].best_params_}, "
              f"CV macro F1 {searches[name].best_score_:.4f} ({time.time() - tic:.0f} s)")
    print()

    selected_name = best_by_cv(searches)
    print(f"Selected by cross-validation macro F1: {selected_name}")
    print()

    majority, baseline = majority_baseline(y_train, y_test)
    print(f"Majority-class baseline (always '{majority}'): test accuracy {baseline:.4f}")
    print()

    rows = []
    all_scores = {}
    for name, search in searches.items():
        scores = evaluate(search.best_estimator_, X_test, y_test)
        all_scores[name] = scores
        picture = save_confusion_matrix(name, scores["matrix"])
        print(f"=== {name} on the test set ===")
        print(f"accuracy {scores['accuracy']:.4f}   macro F1 {scores['macro_f1']:.4f}")
        print(classification_report(y_test, scores["predictions"], labels=CLASS_ORDER, digits=4))
        print("Confusion matrix (rows = true, columns = predicted, order loss/draw/win):")
        print(scores["matrix"])
        print(f"Saved {picture}")
        print()
        rows.append(comparison_row(name, search, scores, baseline, name == selected_name))

    pd.DataFrame(rows).to_csv(os.path.join(RESULTS_DIR, "model_comparison.csv"), index=False)
    print("Saved results/model_comparison.csv")
    print()

    no_mirror_experiment(searches[selected_name], X_train, y_train, X_test, y_test,
                         all_scores[selected_name])
    print("Saved results/augmentation_experiment.csv")
    print()

    size_mb = save_model(searches[selected_name].best_estimator_)
    print(f"Saved {selected_name} to {MODEL_PATH} ({size_mb:.1f} MB)")
    if size_mb > MAX_MODEL_MB:
        print(f"WARNING: the model file is bigger than {MAX_MODEL_MB} MB")
    print(f"Total time: {time.time() - start:.0f} s")


if __name__ == "__main__":
    main()
