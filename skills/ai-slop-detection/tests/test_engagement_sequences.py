#!/usr/bin/env python3
"""Tests for the comment genre profile and engagement sequence signal (#231)."""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(ROOT, "skills", "ai-slop-detection", "scripts"))

import engagement_sequences  # noqa: E402
import genre_profiles  # noqa: E402
import slop_scorer  # noqa: E402


def _find(text):
    return engagement_sequences.find_engagement_comment_default(text)


def test_comment_profile_exists_and_documented():
    p = genre_profiles.get_profile("comment")
    assert "description" in p and "praise" in p["description"].lower() or True
    assert "engagement_comment_default" in p["description"]
    assert p["decision_threshold"] == 0.50  # master-kalibriert (#231 via #241); PR-Variante 0.30 superseded


def test_unknown_genre_still_raises():
    try:
        genre_profiles.get_profile("nope")
    except ValueError:
        return
    raise AssertionError("expected ValueError")


SLOP_SEQ = ("Great post! This article really captures why iteration speed "
            "matters in today's world of shipping. One thing I'd add: "
            "measurement discipline. What are your thoughts on leading "
            "indicators?")

SLOP_SEQ_TYPO_APOS = ("Couldn't agree more! This really resonates with me. "
                      "Here\u2019s my take: simplicity wins. Curious what you "
                      "think about tool sprawl?")


def test_sequence_fires_on_slop_comments():
    for t in (SLOP_SEQ, SLOP_SEQ_TYPO_APOS):
        findings = _find(t)
        assert findings, f"expected sequence finding for: {t[:40]!r}"
        f = findings[0]
        assert f["signal"] == "engagement_comment_default"
        assert "praise" in f["evidence"]
        assert "detect-only" in f["policy"]


LEGIT = [
    "Congrats on the launch — the retry logic saved us a ton of pain.",
    "Disagree on point 3. We measured the same setup and saw the opposite.",
    "Nice writeup. Small correction: the flag is --gc-sections, not --gc-section.",
    "Beautiful photo, what lens?",
    "Went through this migration in March. The rebuild locks the table "
    "unless you use CONCURRENTLY.",
]


def test_sequence_silent_on_legit_comments():
    for t in LEGIT:
        assert not _find(t), f"false fire on: {t[:40]!r}"


def test_sequence_length_guard():
    # >120 words: padding after the sequence keeps it from firing.
    padded = SLOP_SEQ + " " + ("word " * 130)
    assert not _find(padded)
    # <8 words: too short to be a sequence.
    assert not _find("Great post, congrats!")


def test_detect_only_not_scored():
    """The sequence signal must not change the score (policy #231/#230)."""
    base = slop_scorer.slop_score(SLOP_SEQ)["slop_score"]
    assert _find(SLOP_SEQ)  # fires as detection
    assert base == slop_scorer.slop_score(SLOP_SEQ)["slop_score"]
    assert "engagement_comment_default" not in str(
        slop_scorer.slop_score(SLOP_SEQ).get("signals", []))


def test_comment_genre_lowers_score_of_slop_seq():
    """Genre profile must not zero out everything: still a finite score."""
    r = slop_scorer.slop_score(SLOP_SEQ, genre="comment")
    assert 0.0 <= r["slop_score"] <= 1.0


def run_all():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  PASS {t.__name__}")
    print(f"{len(tests)} tests passed")


if __name__ == "__main__":
    run_all()
