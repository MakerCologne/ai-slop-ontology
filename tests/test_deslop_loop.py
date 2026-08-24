"""Tests for the DESLOP-LOOP orchestrator (issue #51).

ADR-0001: the loop ORCHESTRATES — it never rewrites text itself. The FIX step
is an injected callback (fix(text, findings) -> candidate). All tests use
deterministic fake detectors/fixers; the two integration tests use the real
classifier read-only. No network.
"""

import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "skills", "ai-slop-detection", "scripts"))

from src.deslop_loop import (  # noqa: E402
    DeslopLoop,
    Finding,
    LoopParams,
    default_detector,
)
from examples.deslop_loop_demo import deletion_fix  # noqa: E402


def fd(signal="Phrase", confidence=0.7, evidence="here's the thing", severity="medium"):
    return Finding(signal=signal, confidence=confidence, evidence=evidence, severity=severity)


class ScriptedDetector:
    """Returns scripted (score, findings) per call, else last entry."""

    def __init__(self, steps):
        self.steps = list(steps)
        self.calls = []

    def __call__(self, text):
        self.calls.append(text)
        if self.steps:
            step = self.steps.pop(0)
        else:
            step = self.steps_last
        self.steps_last = step
        return step


@pytest.fixture
def tmp_runs(tmp_path):
    return str(tmp_path / "runs")


def test_exit_ok_e1_improving_fix_reaches_threshold(tmp_runs):
    det = ScriptedDetector([
        (0.9, [fd("A"), fd("B")]),          # baseline
        (0.9, [fd("A"), fd("B")]),          # re-detect after baseline (confirm)
        (0.5, [fd("A")]),                   # after fix 1
        (0.3, []),                          # after fix 2 -> below 0.4
    ])
    loop = DeslopLoop(detector=det, params=LoopParams(score_threshold=0.4), runs_dir=tmp_runs)
    res = loop.run("sloppy text", fix=lambda t, f: t + "!")
    assert res.verdict == "EXIT_OK"
    assert res.exit_check == "E1+E2"
    assert "Maßstab" in res.guarantee


def test_max_iter_never_silent_pass(tmp_runs):
    det = ScriptedDetector([(0.9, [fd("A")])] * 100)
    loop = DeslopLoop(detector=det, params=LoopParams(max_iter=5), runs_dir=tmp_runs)
    res = loop.run("stuck slop", fix=lambda t, f: t)
    assert res.verdict == "EXIT_ESCALATE"
    assert res.exit_check == "E5"
    assert res.iterations == 5
    assert "human review" in res.guarantee


def test_epsilon_stagnation_escalates(tmp_runs):
    # improvements < epsilon=0.01 over 2 accepted iterations -> E3 stagnation
    det = ScriptedDetector([
        (0.90, [fd()]), (0.90, [fd()]),
        (0.895, [fd()]), (0.895, [fd()]),
        (0.891, [fd()]), (0.891, [fd()]),
    ])
    loop = DeslopLoop(detector=det, params=LoopParams(epsilon=0.01), runs_dir=tmp_runs)
    res = loop.run("flat slop", fix=lambda t, f: t + " ")
    assert res.verdict == "EXIT_ESCALATE"
    assert res.exit_check == "E3"


def test_worse_candidate_rolls_back_to_best(tmp_runs):
    det = ScriptedDetector([
        (0.9, [fd()]), (0.9, [fd()]),       # baseline + confirm
        (0.6, [fd()]),                      # good candidate accepted
        (0.8, [fd()]),                      # worse candidate -> rollback
        (0.3, []),                          # re-detect of kept best -> exit
    ])
    texts = iter(["slop v0", "slop v1", "slop v2"])
    seen_final = {}

    def fixer(t, f):
        return next(texts)

    loop = DeslopLoop(detector=det, params=LoopParams(score_threshold=0.4), runs_dir=tmp_runs)
    res = loop.run("slop v0", fix=fixer)
    assert res.verdict == "EXIT_OK"
    # final text is the rolled-back best ("slop v1" was accepted, "slop v2" rejected)
    assert res.text == "slop v1"


def test_voice_budget_violation_rejects_candidate(tmp_runs):
    det = ScriptedDetector([(0.9, [fd()])] * 100)

    def heavy_fix(t, f):
        return "completely different wording with nothing in common at all here"

    loop = DeslopLoop(detector=det, params=LoopParams(max_iter=3), runs_dir=tmp_runs)
    res = loop.run("original words stay mostly intact", fix=heavy_fix)
    assert res.verdict == "EXIT_ESCALATE"
    assert any(r["action"] == "rejected_budget" for r in res.iteration_records)
    assert res.text == "original words stay mostly intact"


def test_signal_confirmation_low_confidence_needs_two_detections(tmp_runs):
    passed_to_fix = []
    det = ScriptedDetector([
        (0.9, [fd("A", confidence=0.5)]),   # first sight, low confidence
        (0.9, [fd("A", confidence=0.5), fd("B", confidence=0.95)]),  # second sight
    ])

    def fixer(t, f):
        passed_to_fix.append([x.signal for x in f])
        return t + "."

    loop = DeslopLoop(detector=det, params=LoopParams(), runs_dir=tmp_runs)
    loop.run("text", fix=fixer)
    # first fix call: only B (confidence >= 0.9); A not yet confirmed
    assert passed_to_fix[0] == ["B"]
    # second fix call: A confirmed by stability across 2 detects
    assert "A" in passed_to_fix[1]


def test_critical_finding_blocks_exit_ok(tmp_runs):
    det = ScriptedDetector([
        (0.2, [fd("CRIT", confidence=0.95, severity="critical")]),
    ])
    loop = DeslopLoop(detector=det, params=LoopParams(score_threshold=0.4, max_iter=3),
                      runs_dir=tmp_runs)
    res = loop.run("low score but critical", fix=lambda t, f: t)
    # E1 would pass (score < threshold) but E2 (no critical) fails -> keep looping/escalate
    assert res.verdict == "EXIT_ESCALATE"


def test_new_signals_from_fix_prevent_exit_ok_e4(tmp_runs):
    det = ScriptedDetector([
        (0.9, [fd("A", confidence=0.95)]),
        (0.35, [fd("A", confidence=0.95), fd("NEW", confidence=0.95)]),  # fix introduced NEW
        (0.35, [fd("A", confidence=0.95), fd("NEW", confidence=0.95)]),
        (0.35, [fd("A", confidence=0.95), fd("NEW", confidence=0.95)]),
        (0.35, [fd("A", confidence=0.95), fd("NEW", confidence=0.95)]),
        (0.35, [fd("A", confidence=0.95), fd("NEW", confidence=0.95)]),
    ])
    loop = DeslopLoop(detector=det, params=LoopParams(score_threshold=0.4, max_iter=3),
                      runs_dir=tmp_runs)
    res = loop.run("text", fix=lambda t, f: t + ".")
    # score below threshold but NEW signal introduced by fix -> E4 not satisfied -> no EXIT_OK
    assert res.verdict == "EXIT_ESCALATE"


def test_audit_files_complete(tmp_runs):
    det = ScriptedDetector([(0.9, [fd("A")])] * 3)
    loop = DeslopLoop(detector=det, params=LoopParams(max_iter=2), runs_dir=tmp_runs,
                      run_id="audit-test")
    res = loop.run("text", fix=lambda t, f: t + " ")
    d = os.path.join(tmp_runs, "audit-test")
    manifest = json.load(open(os.path.join(d, "manifest.json")))
    assert manifest["params"]["max_iter"] == 2
    assert manifest["detector"] == det.__class__.__name__
    lines = [json.loads(l) for l in open(os.path.join(d, "iterations.jsonl"))]
    assert len(lines) == res.iterations
    for rec in lines:
        for key in ("iter", "score_before", "score_after", "findings", "action", "budget_used"):
            assert key in rec
    result = json.load(open(os.path.join(d, "result.json")))
    assert result["verdict"] == res.verdict
    assert result["exit_check"] == res.exit_check
    assert "guarantee" in result


def test_no_fix_callback_escalates_without_silent_pass(tmp_runs):
    det = ScriptedDetector([(0.9, [fd("A")])])
    loop = DeslopLoop(detector=det, params=LoopParams(), runs_dir=tmp_runs)
    res = loop.run("text", fix=None)
    assert res.verdict == "EXIT_ESCALATE"
    assert "no fix callback" in res.guarantee


def test_loop_never_modifies_text_itself(tmp_runs):
    original = "here's the thing: pristine"
    det = ScriptedDetector([(0.9, [fd()])] * 10)
    loop = DeslopLoop(detector=det, params=LoopParams(max_iter=2), runs_dir=tmp_runs)
    res = loop.run(original, fix=lambda t, f: t)  # identity fix
    # without a writing fix callback the text is untouched (ADR-0001)
    assert res.text == original


# ---- integration with the real detector (read-only) ----

SLOP_FIXTURE = (
    "In today's rapidly evolving digital landscape, it's important to note that "
    "these robust, seamless platforms unlock your potential. Furthermore, let's "
    "dive into how these cutting-edge solutions serve as a testament to innovation."
)


def test_default_detector_is_classifier_read_only():
    score, findings = default_detector()(SLOP_FIXTURE)
    assert score > 0.4
    assert len(findings) > 0
    assert all(isinstance(f, Finding) for f in findings)


def test_integration_demo_deletion_fix_reduces_score(tmp_runs):
    loop = DeslopLoop(params=LoopParams(max_iter=4), runs_dir=tmp_runs, run_id="it-demo")
    res = loop.run(SLOP_FIXTURE, fix=deletion_fix)
    assert res.score_initial > res.score_final
    # verdict is honest whichever way it ends
    assert res.verdict in ("EXIT_OK", "EXIT_ESCALATE")
