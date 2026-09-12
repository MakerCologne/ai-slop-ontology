"""Tests for the issue #111 metadata-slop extension: behavioral
commit-velocity signals (Cadence), PR-structure rules (anti-slop) and
commit-message keywords/structure (gitorit). Positive and negative
fixtures per signal group; FP guards verified (single-rule hits stay
silent)."""

import datetime as dt
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from metadata_slop import (  # noqa: E402
    BehavioralAnalyzer,
    CommitKeywordAnalyzer,
    CommitRecord,
    MetadataSlopClassifier,
    PRStructureAnalyzer,
)

T0 = dt.datetime(2026, 9, 12, 10, 0, 0)


def _burst_commits():
    """8 commits, 30s apart, ~200 additions each → velocity + burst."""
    return [
        CommitRecord(timestamp=T0 + dt.timedelta(seconds=30 * i),
                     additions=220, deletions=3)
        for i in range(8)
    ]


# -- CommitVelocitySlop ------------------------------------------------------

def test_velocity_positive_burst():
    res = BehavioralAnalyzer().analyze(_burst_commits())
    assert res.is_slop
    f = res.signals_detected[0]
    assert f.signal_id == "CommitVelocitySlop"
    assert "burst_cluster" in f.evidence or "additions" in f.evidence


def test_velocity_positive_ratio_and_consistency():
    # slow enough to avoid burst, but add-heavy + consistent ratios
    commits = [
        CommitRecord(timestamp=T0 + dt.timedelta(hours=i),
                     additions=100, deletions=3)
        for i in range(5)
    ]
    res = BehavioralAnalyzer().analyze(commits)
    assert res.is_slop  # add_delete_ratio + consistent_ratios


def test_velocity_negative_human_cadence():
    commits = [
        CommitRecord(timestamp=T0 + dt.timedelta(hours=i),
                     additions=40 + 17 * i, deletions=5 * (i % 3))
        for i in range(6)
    ]
    assert not BehavioralAnalyzer().analyze(commits).is_slop


def test_velocity_negative_single_commit():
    assert not BehavioralAnalyzer().analyze(
        [CommitRecord(timestamp=T0, additions=999)]).is_slop


def test_velocity_fp_guard_single_rule():
    # only the ratio rule fires (slow, varied ratios, low volume)
    commits = [
        CommitRecord(timestamp=T0 + dt.timedelta(hours=i),
                     additions=20 + 30 * i, deletions=2 + 7 * i)
        for i in range(5)
    ]
    assert not BehavioralAnalyzer().analyze(commits).is_slop


# -- PRStructureSlop ---------------------------------------------------------

def test_pr_positive_emoji_and_dangling_ref():
    pr = {
        "title": "🚀✨ Comprehensive refactor of the parser pipeline",
        "body": "Touches `src/parser/tokenizer.py` and "
                "`src/parser/ast_builder.py` as discussed.",
        "changed_files": ["docs/parser.md"],
    }
    res = PRStructureAnalyzer().analyze(pr)
    assert res.is_slop
    f = res.signals_detected[0]
    assert f.signal_id == "PRStructureSlop"
    assert "emoji in title" in f.evidence
    assert "refs not in diff" in f.evidence


def test_pr_positive_blocked_term_and_keywords():
    pr = {
        "title": "Seamless integration of the new cache layer",
        "body": ("This change is about enhancing the caching layer. " * 12),
        "changed_files": ["src/cache.py"],
    }
    res = PRStructureAnalyzer().analyze(pr)
    assert res.is_slop  # blocked_term + long_keyword_message


def test_pr_negative_honest_pr():
    pr = {
        "title": "cache: fix stale read after invalidation",
        "body": ("Invalidation cleared the local map but left the shared "
                 "L1 in place; reads served the stale entry for up to 60s. "
                 "Now both are cleared together. Closes #88."),
        "changed_files": ["src/cache.py", "tests/test_cache.py"],
    }
    assert not PRStructureAnalyzer().analyze(pr).is_slop


def test_pr_negative_single_emoji():
    pr = {
        "title": "✨ cache: add invalidation hook",
        "body": "Small change, see diff.",
        "changed_files": ["src/cache.py"],
    }
    assert not PRStructureAnalyzer().analyze(pr).is_slop  # FP guard


def test_pr_negative_ref_matches_diff():
    pr = {
        "title": "parser: rewrite tokenizer loop",
        "body": "Touches `src/parser/tokenizer.py`; the AST builder is "
                "unchanged.",
        "changed_files": ["src/parser/tokenizer.py"],
    }
    assert not PRStructureAnalyzer().analyze(pr).is_slop


# -- CommitKeywordSlop -------------------------------------------------------

def test_commit_keyword_positive():
    msg = ("Enhancing the configuration module. " * 8) + "\n" + \
          "\n".join(f"- Adding step {i}" for i in range(6))
    res = CommitKeywordAnalyzer().analyze(msg)
    assert res.is_slop
    assert res.signals_detected[0].signal_id == "CommitKeywordSlop"


def test_commit_keyword_positive_long():
    msg = ("This is a comprehensive change leveraging the new API surface "
           "in a seamless way. " * 5)
    assert CommitKeywordAnalyzer().analyze(msg).is_slop


def test_commit_keyword_negative_single_word():
    assert not CommitKeywordAnalyzer().analyze(
        "cache: robust fix for the stale read").is_slop


def test_commit_keyword_negative_honest_message():
    msg = ("rotate refresh token on password change\n\n"
           "Closes #412. Without rotation a stolen refresh token stayed "
           "valid after the password was changed.")
    assert not CommitKeywordAnalyzer().analyze(msg).is_slop


# -- Classifier integration ---------------------------------------------------

def test_classifier_exposes_111_analyzers():
    mdc = MetadataSlopClassifier()
    assert mdc.classify_commit_history(_burst_commits()).is_slop
    assert mdc.classify_pull_request({
        "title": "🚀✨ Comprehensive overhaul",
        "body": "x", "changed_files": [],
    }).is_slop
    assert mdc.commit_keywords.analyze(
        "Enhancing " * 60).is_slop
