# Regression tests for the FakeAuthority structure ceiling (GL
# ai-slop-ontology#4 / GitHub btm-openclaw-platform #1075):
# authority-only slop with clean neutral dimensions could never reach the
# decision threshold (0.18 weight + small repetition contribution <= 0.37),
# so saturating fake-authority text (>= 3 distinct AUTHORITY_PATTERNS,
# no buzzwords/phrases/morals) scored Clean. Fix: authority saturation counts
# as a second agreeing strong family and floors the score at the threshold.
"""FakeAuthority saturation escalation tests."""

import os
import sys

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "skills", "ai-slop-detection", "scripts",
))

from slop_scorer import (  # noqa: E402
    AUTHORITY_PATTERNS,
    DECISION_THRESHOLD,
    slop_score,
)

# Authority-only slop: 5 distinct unsubstantiated authority patterns,
# varied sentence lengths (kills burstiness), names/years (kills
# portability), no buzzwords, no phrase categories, no moral, no lists.
# Before the fix: 0.205 (Clean) — structural false negative.
AUTHORITY_ONLY_SLOP = (
    "Recent studies from 2019 hint that morning light sharpens focus. "
    "Research shows a link between hydration and mood, according to Anna "
    "Klein of Utrecht, who led a 3-year cohort study published in The "
    "Lancet. Scientists have found that memory consolidates during deep "
    "sleep. Experts say movement helps. It has been proven over decades "
    "that silence aids concentration in libraries across Europe, from "
    "Vienna to Lisbon, though effect sizes vary considerably between "
    "populations."
)

# Legitimate prose with ONE authority phrase plus a named, specific source:
# stays a single family, must not be escalated.
NAMED_SOURCE_PROSE = (
    "Anna Klein of Utrecht led a 3-year cohort study of 412 participants, "
    "published in The Lancet in 2021. Her team measured hydration markers "
    "against mood scores over eighteen months. The effect was small but "
    "consistent, and Klein cautions against overinterpreting it."
)


def test_authority_only_slop_is_suspicious():
    r = slop_score(AUTHORITY_ONLY_SLOP)
    assert r["signals"]["authority_phrases"], "authority patterns should match"
    assert len(r["signals"]["authority_phrases"]) >= 3
    assert r["slop_score"] >= DECISION_THRESHOLD, (
        f"authority-saturated slop under threshold: {r['slop_score']}"
    )


def test_authority_only_baseline_before_fix():
    # Documents the pre-fix structural ceiling: without the saturation
    # escalation the weighted sum for this text is ~0.205 — the floor must
    # be doing the work, not incidental dimensions.
    r = slop_score(AUTHORITY_ONLY_SLOP)
    dims = r["dimension_scores"]
    weighted = dims.get("authority_slop", 0) * 0.18 + dims.get(
        "repetition_slop", 0) * 0.18
    assert weighted < DECISION_THRESHOLD, (
        "test corpus drifted: weighted-only score now exceeds threshold, "
        "escalation no longer exercised"
    )


def test_single_authority_phrase_stays_clean():
    r = slop_score(NAMED_SOURCE_PROSE)
    assert r["slop_score"] < DECISION_THRESHOLD, (
        f"named-source prose escalated: {r['slop_score']}"
    )


def test_two_authority_hits_do_not_escalate_alone():
    # 1-2 authority hits = one strong family, unchanged behavior: without
    # a second family the floor must not fire.
    text = (
        "Anna Klein of Utrecht published a cohort study in 2021 with 412 "
        "participants, tracking hydration and mood for eighteen months. "
        "Research shows small but consistent effects in such cohorts, "
        "though Klein herself cautions the design cannot prove causation "
        "and replication attempts in 2023 and 2024 returned mixed results."
    )
    r = slop_score(text)
    assert len(r["signals"]["authority_phrases"]) <= 2
    assert r["slop_score"] < DECISION_THRESHOLD or any(
        v for k, v in r["dimension_scores"].items()
        if k not in ("authority_slop", "repetition_slop")
    ), "escalation fired with fewer than 3 distinct authority patterns"
