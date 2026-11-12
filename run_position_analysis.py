import argparse
import os
import time

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

from levels import make_medium_player
from medium_player import MediumPlayer
from minimax_player import MinimaxPlayer
from players import RandomPlayer
from position_analysis import (
    OUTCOMES,
    collect_positions,
    decision_summary,
    overall_summary,
    summary_by_confidence,
    summary_by_stage,
)

matplotlib.use("Agg")

RESULTS_DIR = "results"
RAW_PATH = os.path.join(RESULTS_DIR, "position_analysis.csv")
SUMMARY_PATH = os.path.join(RESULTS_DIR, "position_analysis_summary.csv")
CHART_PATH = os.path.join(RESULTS_DIR, "position_analysis.png")
SEED = 42
OUTCOME_COLORS = {"helped": "#2a78d6", "tie": "#b4b2a9", "hurt": "#eb6834"}


def parse_arguments():
    """Read the command-line options."""
    parser = argparse.ArgumentParser(description="Where does the model help beyond the rules?")
    parser.add_argument("--reference-depth", type=int, default=5,
                        help="depth of the alpha-beta search used as the referee (default 5)")
    parser.add_argument("--openings", type=int, default=100,
                        help="number of seeded openings per opponent (default 100)")
    return parser.parse_args()


def format_share(row):
    """Return the helped share and its confidence interval as text."""
    if row["helped_share"] is None:
        return "-"
    return f"{row['helped_share']:.1%} [{row['ci_low']:.1%}, {row['ci_high']:.1%}]"


def print_decisions(rows):
    """Print table (a): who decided the move."""
    print("a) Who decided the hybrid's move")
    for row in rows:
        print(f"   {row['group']:32} {row['positions']:6}")
    print()


def print_outcomes(title, rows):
    """Print a helped / tie / hurt table with the helped share and its 95% Wilson interval."""
    print(title)
    print(f"   {'Group':18} {'Positions':>9} {'Helped':>7} {'Tie':>5} {'Hurt':>5}   "
          f"Helped share of helped+hurt [95% CI]")
    for row in rows:
        print(f"   {row['group']:18} {row['positions']:9} {row['helped']:7} {row['tie']:5} "
              f"{row['hurt']:5}   {format_share(row)}")
    print()


def print_margin_ranges(rows):
    """Print the model-margin range that each confidence third covers."""
    for row in rows:
        if "margin_min" in row:
            print(f"   {row['group']:6} margins from {row['margin_min']:.4f} to {row['margin_max']:.4f}")
    print()


def save_chart(stage_rows):
    """Save stacked bars of helped / tie / hurt by game stage."""
    figure, axis = plt.subplots(figsize=(8, 5))
    bottoms = [0] * len(stage_rows)
    labels = [row["group"] for row in stage_rows]
    for outcome in OUTCOMES:
        heights = [row[outcome] for row in stage_rows]
        axis.bar(labels, heights, bottom=bottoms, label=outcome, color=OUTCOME_COLORS[outcome],
                 edgecolor="white", linewidth=2, width=0.6)
        for index in range(len(heights)):
            bottoms[index] = bottoms[index] + heights[index]
    axis.set_xlabel("Discs on the board (game stage)")
    axis.set_ylabel("Positions where hybrid and rules-only differ")
    axis.set_title("Did the model's move beat the rules-only move? (referee: deeper alpha-beta)")
    axis.legend(title="Hybrid move was", frameon=False)
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    axis.grid(axis="y", color="#e5e4df")
    axis.set_axisbelow(True)
    figure.tight_layout()
    figure.savefig(CHART_PATH, dpi=120)
    plt.close(figure)


def main():
    """Collect positions, judge disagreements, print the tables and save the results."""
    args = parse_arguments()
    start = time.time()
    hybrid = make_medium_player()
    rules_only = MediumPlayer(model=hybrid.model, use_model=False)
    opponents = [("Random", RandomPlayer(seed=SEED)), ("Hard depth 2", MinimaxPlayer(depth=2))]
    openings = list(range(args.openings))
    print(f"Reference search depth: {args.reference_depth}")
    print(f"Playing {2 * len(openings)} games against each opponent ...")
    rows = collect_positions(hybrid, rules_only, opponents, openings, args.reference_depth,
                             show_progress=True)
    print(f"Collected {len(rows)} positions in {time.time() - start:.0f} s")
    print()

    decisions = decision_summary(rows)
    overall = overall_summary(rows)
    by_stage = summary_by_stage(rows)
    by_confidence = summary_by_confidence(rows)

    print_decisions(decisions)
    print_outcomes("Overall (all disagreements)", [overall])
    print_outcomes("b) Disagreements by game stage", by_stage)
    print_outcomes("c) Disagreements by model confidence (thirds of the margin)", by_confidence)
    print_margin_ranges(by_confidence)

    os.makedirs(RESULTS_DIR, exist_ok=True)
    pd.DataFrame(rows).to_csv(RAW_PATH, index=False)
    pd.DataFrame(decisions + [overall] + by_stage + by_confidence).to_csv(SUMMARY_PATH, index=False)
    save_chart(by_stage)
    print(f"Saved {RAW_PATH}, {SUMMARY_PATH} and {CHART_PATH}")
    print(f"Total time: {time.time() - start:.0f} s")


if __name__ == "__main__":
    main()
