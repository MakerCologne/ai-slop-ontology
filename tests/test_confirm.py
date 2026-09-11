"""Tests: Signal-Bestätigung ≥ 2 unabhängige Nachweise (#58).

Spec: docs/loop-guards/58-signal-bestätigung.md (PR #144).
Implementation: src/confirm.py (ConfirmGate), Integration in
deslop_loop via injizierbarem confirm-Gate.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.confirm import (ConfirmGate, ConfirmParams, fp_fix_rate,
                         resample_variants)
from src.deslop_loop import DeslopLoop, Finding, LoopParams


def fd(signal, conf=0.5, sev="medium"):
    return Finding(signal=signal, confidence=conf, evidence="x", severity=sev)


# -- resample_variants -------------------------------------------------

def test_resample_variants_deterministic_and_nonempty():
    text = "It's not just a tool — it's a game changer. Here are 5 ways."
    vs = resample_variants(text)
    assert len(vs) >= 1
    # deterministisch (kein RNG) — Audit-Reproduzierbarkeit
    assert vs == resample_variants(text)


def test_resample_variants_empty_text():
    assert resample_variants("") == []


# -- ConfirmGate Pfade --------------------------------------------------

def test_single_deterministic_match_is_rejected():
    """Einzelner Matcher-Treffer ohne 2. Nachweis = kein Fix-Trigger."""
    gate = ConfirmGate()
    out = gate.confirm("some text", [fd("A", conf=0.5)])
    assert out == []
    assert gate.stats["rejected"] == 1
    assert gate.stats["confirmed"] == 0


def test_confidence_path_confirms():
    gate = ConfirmGate(params=ConfirmParams(confirm_confidence=0.9))
    out = gate.confirm("t", [fd("A", conf=0.95)])
    assert [cf.finding.signal for cf in out] == ["A"]
    assert out[0].evidence == ["confidence", "deterministic"]


def test_stability_path_confirms():
    gate = ConfirmGate()
    out = gate.confirm("t", [fd("A", conf=0.3)], prev_ids={"A"})
    assert [cf.finding.signal for cf in out] == ["A"]
    assert "stability" in out[0].evidence


def test_llm_path_confirms():
    """Pfad A: deterministisch + LLM-Zweitnachweis (injizierbar)."""
    gate = ConfirmGate(llm_check=lambda text, sig: sig == "A")
    out = gate.confirm("t", [fd("A", conf=0.3), fd("B", conf=0.3)])
    assert [cf.finding.signal for cf in out] == ["A"]
    assert "llm" in out[0].evidence
    assert gate.stats["by_path"]["llm"] == 1
    assert gate.stats["rejected"] == 1  # B verworfen


def test_resample_path_confirms():
    """Pfad B: deterministisch + Resample-Perturbation."""
    def detector(text):
        # Signal "S" feuert robust auf alle Varianten, "F" nur exakt einmal
        finds = [fd("S", conf=0.3)]
        if text == "original F text":
            finds.append(fd("F", conf=0.3))
        return 0.5, finds

    gate = ConfirmGate(params=ConfirmParams(use_resample=True))
    out = gate.confirm("original F text", detector("original F text")[1],
                       detector=detector)
    # F: kein 2. Nachweis (Resample stützt nicht) -> verworfen
    assert {cf.finding.signal for cf in out} == {"S"}
    assert "resample" in out[0].evidence


# -- fp_fix_rate Metrik --------------------------------------------------

def test_fp_fix_rate_metric():
    gate = ConfirmGate(llm_check=lambda t, s: s == "A")
    gate.confirm("t", [fd("A", 0.3), fd("B", 0.3), fd("C", 0.3)])
    assert gate.stats["confirmed"] == 1
    assert gate.stats["rejected"] == 2
    assert fp_fix_rate(gate.stats) == 2 / 3
    assert fp_fix_rate({}) == 0.0


# -- Integration in DeslopLoop -------------------------------------------

def test_loop_with_confirm_gate_rejects_low_confidence_single(tmp_path):
    calls = []

    def det(text):
        return 0.8, [fd("A", conf=0.5)]

    def fix(text, findings):
        calls.append([f.signal for f in findings])
        return None  # escalate NO_CANDIDATE

    loop = DeslopLoop(detector=det, params=LoopParams(max_iter=1),
                      confirm=ConfirmGate(params=ConfirmParams(
                          confirm_confidence=0.9, use_stability=False)))
    res = loop.run("t", fix=fix)
    # Ohne 2. Nachweis: A wird nie als Fix-Trigger übergeben (leerer Call)
    assert calls == [[]]
    assert "A" not in res.open_signals
    assert res.iteration_records[0]["evidence"] == {}


def test_loop_legacy_mode_unchanged():
    """Ohne Gate: altes Inline-Kriterium (confidence ODER Stabilität)."""
    def det(text):
        return 0.8, [fd("A", conf=0.5)]

    fix_calls = []

    def fix(text, findings):
        fix_calls.append(1)
        return None

    loop = DeslopLoop(detector=det, params=LoopParams(max_iter=1))
    res = loop.run("t", fix=fix)
    # Iteration 1: prev=None, conf 0.5 < 0.9 -> A unbestätigt -> leerer Fix-Call
    assert fix_calls == [1]  # Callback feuert, aber mit leerer Finding-Liste
    assert res.verdict == "EXIT_ESCALATE"
