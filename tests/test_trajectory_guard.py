"""Tests für guard/trajectory.py (#59 Score-Trajectory-Monitoring)."""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from guard.trajectory import (  # noqa: E402
    ESCALATE, OK, STOP_REPORT,
    TrajectoryParams,
    build_from_loop_records,
    evaluate, evaluate_run_dir,
)


def _steps(pairs, action="accepted"):
    """pairs: [(iter, score_before, score_after, edits_pct)]"""
    out = []
    for it, before, after, edits in pairs:
        out.append({"iter": it, "score": after, "edits_pct": edits,
                    "action": action})
    return out


def test_ok_normal_trajectory():
    steps = _steps([(1, 0.8, 0.7, 0.1), (2, 0.7, 0.6, 0.1), (3, 0.6, 0.45, 0.12)])
    v = evaluate(steps)
    assert v.verdict == OK
    assert v.reasons == []


def test_anomaly_perfect_score_jump_without_edits():
    # Δ = 0.6 > 0.4, edits_pct 0.05 < 0.3 -> Evasions-Verdacht
    steps = _steps([(1, 0.8, 0.75, 0.1), (2, 0.75, 0.15, 0.05)])
    v = evaluate(steps)
    assert v.verdict == ESCALATE
    assert any(r.startswith("ANOMALY") for r in v.reasons)


def test_large_drop_with_proportional_edits_is_ok():
    # Δ = 0.6, aber edits_pct 0.4 >= 0.3 -> proportional, kein Anomalie
    steps = _steps([(1, 0.8, 0.75, 0.1), (2, 0.75, 0.15, 0.4)])
    v = evaluate(steps)
    assert v.verdict == OK


def test_diminishing_returns_stop_report():
    steps = _steps([(1, 0.5, 0.49, 0.05), (2, 0.49, 0.485, 0.05),
                    (3, 0.485, 0.48, 0.05), (4, 0.48, 0.479, 0.05)])
    v = evaluate(steps)
    assert v.verdict == STOP_REPORT
    assert any(r.startswith("DIMINISHING") for r in v.reasons)


def test_two_small_deltas_not_enough():
    steps = _steps([(1, 0.5, 0.49, 0.05), (2, 0.49, 0.485, 0.05)])
    v = evaluate(steps)
    assert v.verdict == OK


def test_rollback_chain_escalates():
    steps = [
        {"iter": 1, "score": 0.6, "edits_pct": 0.1, "action": "accepted"},
        {"iter": 2, "score": 0.65, "edits_pct": 0.1, "action": "rollback"},
        {"iter": 3, "score": 0.7, "edits_pct": 0.1, "action": "rollback"},
    ]
    v = evaluate(steps)
    assert v.verdict == ESCALATE
    assert any(r.startswith("ROLLBACK_CHAIN") for r in v.reasons)


def test_single_rollback_ok():
    steps = [
        {"iter": 1, "score": 0.6, "edits_pct": 0.1, "action": "accepted"},
        {"iter": 2, "score": 0.65, "edits_pct": 0.1, "action": "rollback"},
        {"iter": 3, "score": 0.5, "edits_pct": 0.1, "action": "accepted"},
    ]
    v = evaluate(steps)
    assert v.verdict == OK


def test_anomaly_beats_diminishing_precedence():
    # Anomalie + diminishing -> ESCALATE dominiert (schlimmerer Befund)
    steps = _steps([(1, 0.5, 0.49, 0.01), (2, 0.49, 0.485, 0.01),
                    (3, 0.485, 0.0, 0.01)])
    v = evaluate(steps)
    assert v.verdict == ESCALATE


def test_custom_params():
    p = TrajectoryParams(anomaly_delta=0.2)
    steps = _steps([(1, 0.8, 0.78, 0.05), (2, 0.78, 0.53, 0.05)])  # Δ=0.25 > 0.2
    v = evaluate(steps, p)
    assert v.verdict == ESCALATE


def test_build_from_loop_records_excludes_exit_ok():
    records = [
        {"iter": 1, "score_after": 0.7, "budget_used": 0.1, "action": "accepted"},
        {"iter": 2, "score_after": 0.6, "budget_used": 0.1, "action": "accepted"},
        {"iter": 3, "score_after": 0.39, "budget_used": 0.0, "action": "exit_ok"},
    ]
    steps = build_from_loop_records(records)
    assert len(steps) == 2
    assert steps[0]["score"] == 0.7
    assert steps[1]["edits_pct"] == 0.1


def test_evaluate_run_dir_reads_iterations_jsonl(tmp_path):
    run_dir = tmp_path / "run-1"
    run_dir.mkdir()
    records = [
        {"iter": 1, "score_after": 0.75, "budget_used": 0.1, "action": "accepted"},
        {"iter": 2, "score_after": 0.2, "budget_used": 0.02, "action": "accepted"},
    ]
    with open(run_dir / "iterations.jsonl", "w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
    v = evaluate_run_dir(str(run_dir))
    assert v.verdict == ESCALATE
    assert any("ANOMALY" in r for r in v.reasons)
