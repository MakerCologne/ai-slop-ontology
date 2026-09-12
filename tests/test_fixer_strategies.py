"""Tests for Best-of-N fix strategies (issue #60 / btm #1117).

ADR-0001: no rewriting logic lives in this repo — strategies are injected
callbacks; these tests use deterministic fakes (no network, no LLM).

Covers the DoD:
- best score wins (primary key),
- tie within selection_epsilon -> smallest edit wins (voice-similarity
  tie-break, anti-verbosity/structure bias),
- voice-budget guardrail drops over-budget candidates,
- all-abstain / all-over-budget -> no candidate (no silent pass),
- failing strategy does not abort the batch,
- integration: BestOfNFixer works as the fix callback of DeslopLoop
  (rollback edge + audit records intact).
"""

import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from fixer.strategies import (  # noqa: E402
    BestOfNFixer,
    StrategySpec,
    evaluate_strategies,
)
from src.deslop_loop import DeslopLoop, Finding, LoopParams  # noqa: E402


def fd(signal="Phrase", confidence=0.95, evidence="x", severity="medium"):
    return Finding(signal=signal, confidence=confidence, evidence=evidence,
                   severity=severity)


def fake_detector_factory(scores=None):
    """Detector stub: maps text -> score via dict, default 0.1."""
    scores = scores or {}
    def detect(text):
        return scores.get(text, 0.1), []
    return detect


# BASE: 12 tokens. Edit distances (token multiset change rate):
#   C1 (1 token edit)  ~0.083  ; C2 (2 token edits) ~0.167  ; heavy ~1.0
BASE = "der report analysiert die lage genau und zieht ein fazit daraus"
C1 = "der bericht analysiert die lage genau und zieht ein fazit daraus"
C2 = "die studie analysiert die lage genau und zieht ein fazit daraus"
HEAVY = "completely different vocabulary nothing shared at all anymore"


def test_best_score_wins():
    det = fake_detector_factory({C1: 0.30, C2: 0.10, HEAVY: 0.50})
    strategies = [
        StrategySpec("delete", lambda t, f: C1),
        StrategySpec("rewrite", lambda t, f: C2),
        StrategySpec("restructure", lambda t, f: HEAVY),
    ]
    res = evaluate_strategies(BASE, [fd()], strategies, det)
    assert res.selected == C2
    assert res.selected_strategy == "rewrite"
    assert res.reason == "best_score"
    assert len(res.candidates) == 3


def test_tie_break_prefers_smaller_edit():
    # C2 scores slightly better but edits more tokens; within epsilon the
    # smaller edit (C1) must win (voice-similarity tie-break).
    det = fake_detector_factory({C1: 0.102, C2: 0.100})
    strategies = [
        StrategySpec("delete", lambda t, f: C1),
        StrategySpec("rewrite", lambda t, f: C2),
    ]
    res = evaluate_strategies(BASE, [fd()], strategies, det,
                              selection_epsilon=0.005)
    assert res.selected == C1
    assert res.reason == "tie_voice"


def test_clear_score_gap_beats_tie_break():
    # gap 0.05 > epsilon: better score wins even though it edits more
    det = fake_detector_factory({C1: 0.15, C2: 0.10})
    strategies = [
        StrategySpec("delete", lambda t, f: C1),
        StrategySpec("rewrite", lambda t, f: C2),
    ]
    res = evaluate_strategies(BASE, [fd()], strategies, det,
                              selection_epsilon=0.005)
    assert res.selected == C2
    assert res.reason == "best_score"


def test_voice_budget_drops_heavy_rewrite():
    det = fake_detector_factory({HEAVY: 0.05, C1: 0.2})
    strategies = [
        StrategySpec("restructure", lambda t, f: HEAVY),  # great score, over budget
        StrategySpec("delete", lambda t, f: C1),
    ]
    res = evaluate_strategies(BASE, [fd()], strategies, det,
                              voice_budget=0.25)
    assert res.selected == C1
    statuses = {c["strategy"]: c["status"] for c in res.candidates}
    assert statuses["restructure"] == "over_budget"


def test_no_candidate_when_all_abstain_or_over_budget():
    det = fake_detector_factory()
    strategies = [
        StrategySpec("delete", lambda t, f: None),
        StrategySpec("rewrite", lambda t, f: HEAVY),
    ]
    res = evaluate_strategies(BASE, [fd()], strategies, det,
                              voice_budget=0.25)
    assert res.selected is None
    assert res.reason == "no_candidate"


def test_failing_strategy_does_not_abort_batch():
    det = fake_detector_factory()
    def boom(t, f):
        raise RuntimeError("strategy crashed")
    strategies = [
        StrategySpec("broken", boom),
        StrategySpec("delete", lambda t, f: C1),
    ]
    res = evaluate_strategies(BASE, [fd()], strategies, det)
    assert res.selected == C1
    statuses = {c["strategy"]: c["status"] for c in res.candidates}
    assert statuses["broken"] == "aborted"


def test_best_of_n_fixer_integrates_with_deslop_loop():
    """Full loop: two parallel strategies, loop accepts the better variant
    and its audit records show the BoN-selected acceptance."""
    det = fake_detector_factory({
        "der text slop und noch slop und ein slop fazit": 0.9,
        "der text und noch slop und ein slop fazit": 0.35,   # delete: -1 slop
        "der text slop und noch text und ein slop fazit": 0.38,  # rewrite: -1 slop
    })

    def loop_detect(text):
        score = det(text)[0]
        return score, [fd()] if score >= 0.4 else []

    strategies = [
        StrategySpec("delete", lambda t, f: "der text und noch slop und ein slop fazit"),
        StrategySpec("rewrite", lambda t, f: "der text slop und noch text und ein slop fazit"),
    ]
    boN = BestOfNFixer(strategies, det)
    loop = DeslopLoop(detector=loop_detect,
                      params=LoopParams(score_threshold=0.4, max_iter=3))
    res = loop.run("der text slop und noch slop und ein slop fazit", fix=boN)
    assert res.verdict == "EXIT_OK"
    assert res.text == "der text und noch slop und ein slop fazit"
    assert res.iteration_records[0]["action"] == "accepted"
    assert boN.last_result.selected_strategy == "delete"
