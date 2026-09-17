"""Issue #55 — severity SSOT + RPN fix order.

The ontology.json `signalSeverity` block is the single source of truth:
classifier severity resolution must consult it before the legacy module
map, and the deslop loop must pass confirmed findings to the fix callback
in RPN order (critical → high → medium → low, within tier by confidence).
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "skills", "ai-slop-detection", "scripts"))

from src.classifier import SlopClassifier
from src.deslop_loop import Finding, LoopParams, DeslopLoop, rpn_fix_order

ONTOLOGY = os.path.join(ROOT, "ontology.json")


def make_clf():
    return SlopClassifier(ONTOLOGY)


# ---- classifier: ontology-first severity (SSOT) ----

def test_ontology_and_legacy_agree_on_calibrated_signals():
    # After empirical calibration (hardneg corpus, null-edit contract) the
    # ontology tiers and the legacy map agree on all overlapping signal IDs.
    from src.classifier import SIGNAL_SEVERITY
    clf = make_clf()
    for sig in SIGNAL_SEVERITY:
        if sig in clf._ontology_severity:
            assert clf._ontology_severity[sig] == SIGNAL_SEVERITY[sig], sig


def test_ontology_only_signal_resolves():
    # Signal IDs that exist only in the ontology tiers block.
    assert make_clf()._severity_for("PropagandaDisinfoSlop") == "critical"
    assert make_clf()._severity_for("HardcodedSecret") == "critical"


def test_legacy_fallback_and_default():
    clf = make_clf()
    # Not in ontology tiers, but in the legacy map.
    assert clf._severity_for("MetaphorAbuse") == "medium"
    # Unknown everywhere -> medium default.
    assert clf._severity_for("TotallyUnknownSignal") == "medium"


def test_fix_strategy_hint_from_ontology():
    clf = make_clf()
    # fix_strategy_overrides win over tier default.
    assert clf.fix_strategy_for("HardcodedSecret") == "delete"
    # Tier default (high -> rewrite).
    assert clf.fix_strategy_for("ThroatClearing") == "rewrite"
    # Unknown signal -> empty string, no exception.
    assert clf.fix_strategy_for("TotallyUnknownSignal") == ""


# ---- loop: RPN fix order ----

def test_rpn_fix_order_tier_then_confidence():
    fs = [
        Finding("A", 0.9, "e", "medium"),
        Finding("B", 0.5, "e", "critical"),
        Finding("C", 0.95, "e", "high"),
        Finding("D", 0.99, "e", "critical"),
        Finding("E", 0.7, "e", "low"),
        Finding("F", 0.99, "e", "suspicious"),  # unknown tier -> last
    ]
    assert [f.signal for f in rpn_fix_order(fs)] == \
        ["D", "B", "C", "A", "E", "F"]


def test_loop_passes_findings_in_rpn_order():
    seen = []

    def detector(text):
        return 0.9, [
            Finding("MediumSignal", 0.95, "e", "medium"),
            Finding("CriticalSignal", 0.6, "e", "critical"),
            Finding("HighSignal", 0.7, "e", "high"),
        ]

    def fixer(text, findings):
        seen.append([f.signal for f in findings])
        return None  # no candidate -> ESCALATE after capturing the order

    loop = DeslopLoop(detector=detector,
                      params=LoopParams(max_iter=1, confirm_confidence=0.5))
    res = loop.run(text="irrelevant", fix=fixer)
    assert res.verdict == "EXIT_ESCALATE"
    assert seen[0] == ["CriticalSignal", "HighSignal", "MediumSignal"]
