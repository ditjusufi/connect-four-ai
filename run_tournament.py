import os
import time

import joblib
import pandas as pd

from arena import evaluate_matchup
from medium_player import MediumPlayer
from minimax_player import MinimaxPlayer
from players import RandomPlayer

MODEL_PATH = "models/medium_model.joblib"
RESULTS_PATH = "results/tournament_results.csv"
SEED = 42


def build_matchups(model):
    """Return the list of (player A name, player A, player B name, player B, number of openings)."""
    hybrid = MediumPlayer(model=model)
    rules_only = MediumPlayer(model=model, use_model=False)
    model_only = MediumPlayer(model=model, use_rules=False)
    return [
        ("Hybrid", hybrid, "Random", RandomPlayer(seed=SEED), 100),
        ("RulesOnly", rules_only, "Random", RandomPlayer(seed=SEED), 100),
        ("ModelOnly", model_only, "Random", RandomPlayer(seed=SEED), 100),
        ("Hybrid", hybrid, "RulesOnly", rules_only, 50),
        ("Hybrid", hybrid, "Hard depth 2", MinimaxPlayer(depth=2), 50),
        ("Hybrid", hybrid, "Hard depth 4", MinimaxPlayer(depth=4), 50),
    ]


def print_table(rows):
    """Print the tournament results as a table."""
    print(f"{'Player A':10} {'Player B':13} {'Games':>5} {'W':>4} {'L':>4} {'D':>4} "
          f"{'Win rate':>9} {'95% Wilson CI':>17}")
    for row in rows:
        interval = f"[{row['ci_low']:.1%}, {row['ci_high']:.1%}]"
        print(f"{row['player_a']:10} {row['player_b']:13} {row['games']:>5} {row['wins']:>4} "
              f"{row['losses']:>4} {row['draws']:>4} {row['win_rate']:>9.1%} {interval:>17}")


def main():
    """Run all matchups, print a table and save the results to CSV."""
    model = joblib.load(MODEL_PATH)
    rows = []
    for name_a, player_a, name_b, player_b, n_openings in build_matchups(model):
        label = f"{name_a} vs {name_b}"
        print(f"Playing {label} ({2 * n_openings} games) ...")
        start = time.time()
        result = evaluate_matchup(player_a, player_b, list(range(n_openings)), label=label)
        result["seconds"] = round(time.time() - start, 1)
        print(f"   done in {result['seconds']} s")
        row = {"player_a": name_a, "player_b": name_b}
        row.update(result)
        rows.append(row)
    print()
    print_table(rows)
    os.makedirs("results", exist_ok=True)
    pd.DataFrame(rows).to_csv(RESULTS_PATH, index=False)
    print()
    print(f"Saved {RESULTS_PATH}")


if __name__ == "__main__":
    main()
