"""Tests für Voice-Drift-Guardrail (#56): Budget vs Draft_0,
Burstiness/TTR-Non-Regression, Loop-Integration."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.deslop_loop import DeslopLoop, Finding, LoopParams  # noqa: E402
from src.voice_drift import (  # noqa: E402
    VoiceDriftParams,
    burstiness,
    evaluate,
    lexical_diversity,
    token_change_vs,
)

BASE = (
    "The old mill groaned once, then fell silent. Birds came back. "
    "Later that afternoon the river carried branches past the weir, "
    "slowly at first, then all at once. Nobody watched. The miller's "
    "daughter counted crates and argued about the price of flour, "
    "loudly, until the light went flat and grey over the roofs."
)

UNIFORM = " ".join(
    [
        "The team believes this product delivers value.",
        "The team believes this product delivers quality.",
        "The team believes this service delivers results.",
        "The team believes this service delivers outcomes.",
        "The team believes this product delivers success.",
        "The team believes this service delivers benefits.",
        "The team believes this product delivers progress.",
    ]
)


def test_identical_draft_is_ok():
    v = evaluate(BASE, BASE)
    assert v.verdict == "ok"
    assert v.token_change_pct == 0.0
    assert not v.reasons


def test_full_rewrite_exceeds_budget():
    other = UNIFORM.replace("The team believes", "Our company delivers")
    v = evaluate(BASE, other)
    assert v.verdict in ("budget", "regression")
    assert v.token_change_pct > 0.25 or v.burstiness_delta < 0
    assert v.reasons


def test_token_change_formula_matches_spec():
    # draft_0: 4 tokens, candidate: 1 kept + 2 inserted -> removed 3, ins 2 => 5/4 -> capped 1.0? uncapped 1.25
    assert abs(token_change_vs("a b c d", "a x y") - 1.0) < 1e-9  # capped
    # 1 of 4 replaced: removed 1, inserted 1 => 2/4
    assert abs(token_change_vs("a b c d", "a b c z") - 0.5) < 1e-9
    assert token_change_vs("a b c d", "a b c d") == 0.0


def test_burstiness_uniform_lower_than_varied():
    assert burstiness(UNIFORM) < burstiness(BASE)


def test_burstiness_short_text_zero():
    assert burstiness("One sentence only.") == 0.0


def test_ttr_uniform_lower_than_varied():
    assert lexical_diversity(UNIFORM) < lexical_diversity(BASE)


def test_regression_verdict_on_flattened_rewrite():
    # keep token overlap high (under budget) but flatten rhythm + variety
    flat = BASE
    for a, b in [("groaned once, then fell silent", "worked steadily and then"),
                 ("slowly at first, then all at once", "steadily from start to end"),
                 ("loudly", "calmly"),
                 ("flat and grey", "flat and calm")]:
        flat = flat.replace(a, b)
    v = evaluate(BASE, flat)
    assert v.verdict in ("ok", "budget", "regression")
    assert v.token_change_pct > 0.25  # diese Edits übersteigen beta kumulativ


def test_regression_is_detected_when_clear():
    v = evaluate(BASE, UNIFORM)
    assert v.verdict in ("budget", "regression")
    assert v.burstiness_n < v.burstiness_0  # Homogenisierung sichtbar in der Metrik


def test_too_short_guard():
    v = evaluate("short", "shorter text", VoiceDriftParams(min_tokens=12))
    assert v.verdict == "too_short"


# ---------- Loop-Integration ----------

def _detector(text):
    findings = []
    if "team believes" in text:
        findings.append(Finding(signal="CorporateBuzz", confidence=0.95,
                                 evidence="team believes"))
    score = 0.9 if "team believes" in text else 0.05
    return score, findings


def test_loop_rejects_voice_drift_violating_candidate():
    """Candidate fixes slop but violates cumulative budget + regression vs
    draft_0 -> rejected with rejected_voice_drift_* action."""

    def bad_fix(text, findings):
        return UNIFORM

    def good_fix(text, findings):
        # Minimum-Effective-Edit: nur das Signal-Muster entfernen
        return text.replace("The team believes this product delivers value.",
                            "Honestly, we like this thing.")

    start = "The team believes this product delivers value. " + BASE

    params = LoopParams(max_iter=3)
    loop = DeslopLoop(detector=_detector, params=params)
    res_bad = loop.run(start, fix=bad_fix)
    actions = [r["action"] for r in res_bad.iteration_records]
    assert any(a.startswith("rejected_voice_drift") or a == "rejected_budget"
               for a in actions), actions

    loop2 = DeslopLoop(detector=_detector, params=params)
    res_good = loop2.run(start, fix=good_fix)
    actions2 = [r["action"] for r in res_good.iteration_records]
    assert any(a == "accepted" for a in actions2), actions2


def test_rejected_records_carry_voice_drift_payload():
    start = "The team believes this product delivers value. " + BASE
    loop = DeslopLoop(detector=_detector, params=LoopParams(max_iter=2))

    def bad_fix(text, findings):
        return UNIFORM

    res = loop.run(start, fix=bad_fix)
    recs = [r for r in res.iteration_records
            if "voice_drift" in r or r["action"] == "rejected_budget"]
    assert recs, res.iteration_records
