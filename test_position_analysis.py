from board import Board
from medium_player import MediumPlayer
from players import RandomPlayer
from position_analysis import (
    STAGES,
    classify,
    collect_positions,
    confidence_margin,
    confidence_thirds,
    decision_summary,
    outcome_summary,
    reference_score,
    stage_bin,
    summary_by_confidence,
    summary_by_stage,
)
from regression_cases import WeightedStubModel


def test_stage_bins_at_the_boundaries():
    assert stage_bin(0) == "8 or fewer"
    assert stage_bin(8) == "8 or fewer"
    assert stage_bin(9) == "9-16"
    assert stage_bin(16) == "9-16"
    assert stage_bin(17) == "17-26"
    assert stage_bin(26) == "17-26"
    assert stage_bin(27) == "27+"
    assert stage_bin(42) == "27+"


def test_classify_helped_tie_hurt():
    assert classify(10, 5) == "helped"
    assert classify(5, 5) == "tie"
    assert classify(-3, 5) == "hurt"


def test_confidence_thirds_split_by_rank():
    margins = [0.9, 0.1, 0.5, 0.3, 0.7, 0.2]
    assert confidence_thirds(margins) == ["high", "low", "middle", "middle", "high", "low"]


def test_confidence_thirds_with_uneven_counts():
    labels = confidence_thirds([0.4, 0.1, 0.3, 0.2])
    assert labels == ["high", "low", "middle", "low"]


def test_confidence_margin():
    assert confidence_margin({0: 0.5, 3: 0.75, 6: 0.25}) == 0.25
    assert confidence_margin({3: 0.5}) is None
    assert confidence_margin({}) is None


def test_reference_score_prefers_a_winning_move():
    board = Board()
    for col in [0, 0, 1, 1, 2, 2]:
        board.drop(col)
    assert reference_score(board, 3, 3) > reference_score(board, 6, 3)


def test_outcome_summary_share_and_interval():
    rows = [{"outcome": "helped"}] * 3 + [{"outcome": "hurt"}] + [{"outcome": "tie"}] * 2
    summary = outcome_summary("test", "all", rows)
    assert (summary["helped"], summary["tie"], summary["hurt"]) == (3, 2, 1)
    assert summary["helped_share"] == 0.75
    assert summary["ci_low"] < 0.75 < summary["ci_high"]


def test_outcome_summary_with_no_decisive_rows():
    summary = outcome_summary("test", "empty", [])
    assert summary["helped_share"] is None
    assert summary["ci_low"] is None


def test_small_end_to_end_run_with_stub_players():
    model = WeightedStubModel()
    hybrid = MediumPlayer(model=model)
    rules_only = MediumPlayer(model=model, use_model=False)
    opponents = [("Random", RandomPlayer(seed=1))]
    rows = collect_positions(hybrid, rules_only, opponents, [0, 1], reference_depth=2)
    assert len(rows) > 0
    for row in rows:
        assert row["stage"] in STAGES
        if row["decided_by"] == "rules":
            assert not row["differ"]
        if row["differ"]:
            assert row["outcome"] in ("helped", "tie", "hurt")
        else:
            assert row["outcome"] is None
    total = decision_summary(rows)[-3]["positions"] + decision_summary(rows)[-2]["positions"]
    assert total == len(rows)
    stage_positions = sum(row["positions"] for row in summary_by_stage(rows))
    confidence_positions = sum(row["positions"] for row in summary_by_confidence(rows))
    differing = len([row for row in rows if row["differ"]])
    assert stage_positions == differing
    assert confidence_positions == differing
