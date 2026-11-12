import math
import random

from arena import OPENING_MOVES, wilson_interval
from board import PLAYER_ONE, PLAYER_TWO, Board
from minimax_player import alphabeta

STAGES = ["8 or fewer", "9-16", "17-26", "27+"]
CONFIDENCE_LEVELS = ["low", "middle", "high"]
FORCED_REASONS = ["win", "block", "only safe move"]
OUTCOMES = ["helped", "tie", "hurt"]


def stage_bin(discs):
    """Return the game stage name for a number of discs on the board."""
    if discs <= 8:
        return "8 or fewer"
    if discs <= 16:
        return "9-16"
    if discs <= 26:
        return "17-26"
    return "27+"


def classify(hybrid_score, rules_score):
    """Return 'helped', 'tie' or 'hurt' by comparing the reference scores of the two moves."""
    if hybrid_score > rules_score:
        return "helped"
    if hybrid_score < rules_score:
        return "hurt"
    return "tie"


def confidence_thirds(margins):
    """Label each margin 'low', 'middle' or 'high' by its rank (lowest third, middle third, highest third)."""
    pairs = []
    for index in range(len(margins)):
        pairs.append((margins[index], index))
    pairs.sort()
    labels = [None] * len(margins)
    for rank in range(len(pairs)):
        index = pairs[rank][1]
        labels[index] = CONFIDENCE_LEVELS[rank * 3 // len(pairs)]
    return labels


def confidence_margin(scores):
    """Return the best model score minus the second best, or None if there are fewer than two candidates."""
    values = sorted(scores.values(), reverse=True)
    if len(values) < 2:
        return None
    return values[0] - values[1]


def reference_score(board, col, depth):
    """Score a move with a deeper alpha-beta search, from the point of view of the player to move."""
    mover = board.current_player
    child = board.copy()
    child.drop(col)
    return alphabeta(child, depth - 1, -math.inf, math.inf, False, mover)


def opening_board(seed):
    """Return a board after the same seeded random opening moves that arena.py uses."""
    rng = random.Random(seed)
    board = Board()
    for _ in range(OPENING_MOVES):
        board.drop(rng.choice(board.legal_moves()))
    return board


def describe_position(board, hybrid, rules_only, reference_depth):
    """Record what the hybrid and rules-only players would do here, and judge any disagreement."""
    info = hybrid.explain_move(board)
    rules_move = rules_only.choose_move(board)
    if info["reason"] in FORCED_REASONS:
        decided_by = "rules"
    else:
        decided_by = "model"
    row = {
        "discs": board.moves_played,
        "stage": stage_bin(board.moves_played),
        "reason": info["reason"],
        "decided_by": decided_by,
        "hybrid_move": info["column"],
        "rules_move": rules_move,
        "margin": confidence_margin(info["scores"]),
        "differ": info["column"] != rules_move,
        "hybrid_ref_score": None,
        "rules_ref_score": None,
        "outcome": None,
    }
    if row["differ"]:
        row["hybrid_ref_score"] = reference_score(board, info["column"], reference_depth)
        row["rules_ref_score"] = reference_score(board, rules_move, reference_depth)
        row["outcome"] = classify(row["hybrid_ref_score"], row["rules_ref_score"])
    return row


def play_and_record(seed, hybrid_side, hybrid, rules_only, opponent, reference_depth):
    """Play one game from a seeded opening and return a row for every position where the hybrid moved."""
    board = opening_board(seed)
    rows = []
    while not board.is_over():
        if board.current_player == hybrid_side:
            row = describe_position(board, hybrid, rules_only, reference_depth)
            rows.append(row)
            col = row["hybrid_move"]
        else:
            col = opponent.choose_move(board)
        board.drop(col)
    return rows


def collect_positions(hybrid, rules_only, opponents, openings, reference_depth, show_progress=False):
    """Play every opening from both sides against each (name, opponent) and return all position rows."""
    all_rows = []
    for opponent_name, opponent in opponents:
        for count, seed in enumerate(openings, start=1):
            for hybrid_side in (PLAYER_ONE, PLAYER_TWO):
                rows = play_and_record(seed, hybrid_side, hybrid, rules_only, opponent, reference_depth)
                for row in rows:
                    row["opponent"] = opponent_name
                    row["opening"] = seed
                    row["hybrid_side"] = hybrid_side
                    all_rows.append(row)
            if show_progress and count % 10 == 0:
                print(f"   vs {opponent_name}: {2 * count}/{2 * len(openings)} games, "
                      f"{len(all_rows)} positions so far")
    return all_rows


def count_outcomes(rows):
    """Count helped, tie and hurt among rows."""
    counts = {"helped": 0, "tie": 0, "hurt": 0}
    for row in rows:
        counts[row["outcome"]] += 1
    return counts


def outcome_summary(section, group, rows):
    """Return helped / tie / hurt counts and the helped share among helped + hurt with a 95% Wilson interval."""
    counts = count_outcomes(rows)
    decisive = counts["helped"] + counts["hurt"]
    share = None
    low = None
    high = None
    if decisive > 0:
        share = counts["helped"] / decisive
        low, high = wilson_interval(counts["helped"], decisive)
    return {
        "section": section,
        "group": group,
        "positions": len(rows),
        "helped": counts["helped"],
        "tie": counts["tie"],
        "hurt": counts["hurt"],
        "helped_share": share,
        "ci_low": low,
        "ci_high": high,
    }


def decision_summary(rows):
    """Return rows counting how often each reason decided the move and how often the players differed."""
    summary = []
    for reason in FORCED_REASONS + ["model"]:
        matching = [row for row in rows if row["reason"] == reason]
        summary.append({"section": "decided by", "group": reason, "positions": len(matching)})
    forced = [row for row in rows if row["decided_by"] == "rules"]
    model = [row for row in rows if row["decided_by"] == "model"]
    differ = [row for row in model if row["differ"]]
    summary.append({"section": "decided by", "group": "rules forced (total)", "positions": len(forced)})
    summary.append({"section": "decided by", "group": "model decided (total)", "positions": len(model)})
    summary.append({"section": "decided by", "group": "model decided and moves differ",
                    "positions": len(differ)})
    return summary


def disagreements(rows):
    """Return only the rows where the hybrid and rules-only moves differ."""
    return [row for row in rows if row["differ"]]


def summary_by_stage(rows):
    """Return helped / tie / hurt summaries for each game stage, for the disagreement rows."""
    summary = []
    for stage in STAGES:
        matching = [row for row in disagreements(rows) if row["stage"] == stage]
        summary.append(outcome_summary("by stage", stage, matching))
    return summary


def summary_by_confidence(rows):
    """Return helped / tie / hurt summaries for the low, middle and high thirds of model margins."""
    differing = disagreements(rows)
    margins = [row["margin"] for row in differing]
    labels = confidence_thirds(margins)
    summary = []
    for level in CONFIDENCE_LEVELS:
        matching = []
        level_margins = []
        for index in range(len(differing)):
            if labels[index] == level:
                matching.append(differing[index])
                level_margins.append(margins[index])
        result = outcome_summary("by confidence", level, matching)
        if len(level_margins) > 0:
            result["margin_min"] = min(level_margins)
            result["margin_max"] = max(level_margins)
        summary.append(result)
    return summary


def overall_summary(rows):
    """Return the helped / tie / hurt summary for all disagreements together."""
    return outcome_summary("overall", "all disagreements", disagreements(rows))
