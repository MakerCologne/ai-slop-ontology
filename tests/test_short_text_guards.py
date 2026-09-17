"""Short-text guards (upstream #52 / btm #1125): defined minimum lengths per metric.

Fixtures for 5-, 20-, and 50-word texts (as required by the issue):
- 5 words  (tweet/commit-title class): statistical metrics skipped, explicit
            ``skipped`` report, buzzwords still active.
- 20 words (short PR description class): repetition may run, density still
            skipped, burstiness skipped.
- 50 words (paragraph class): all metrics active.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest

from scorer import slop_score
from short_text_guards import active_metrics, load_short_text_guards, text_stats

FIVE_WORDS = "Fix race in timer loop."
TWENTY_WORDS = (
    "This patch fixes a race condition in the timer shutdown path. "
    "Previously the callback could still fire after close. Now we "
    "join the worker before freeing state. Verified manually."
)  # 25 words — between min_words_repetition (20) and min_words_density (40)
FIFTY_WORDS = (
    "The patch fixes a race condition in the timer shutdown path. "
    "Previously the callback could still fire after close, corrupting "
    "shared state. We now join the worker thread before freeing anything.\n"
    "Additional hardening guards re-entrant starts and late callbacks.\n"
    "The fix was verified against the full regression suite on staging.\n"
    "A long soak test that previously crashed within the hour now passes."
)


def test_config_loads_guard_section():
    guards = load_short_text_guards()
    assert guards["min_words_density"] == 40
    assert guards["min_sentences_burstiness"] >= 3


def test_fixture_word_counts():
    assert text_stats(FIVE_WORDS)["words"] == 5


def test_five_word_text_skips_statistical_metrics():
    result = slop_score(FIVE_WORDS)
    skipped = {s["metric"] for s in result["skipped"]}
    # everything length-normalized must be skipped
    assert skipped == {
        "density", "repetition", "burstiness",
        "punctuation", "trailing_moral", "list_heavy",
    }
    # and reported with reason + minimum, not silently zeroed
    for s in result["skipped"]:
        assert s["reason"]
        assert s["minimum"] >= 1


def test_five_word_text_no_false_positive():
    # A clean 5-word text must score low despite degenerate metrics
    result = slop_score(FIVE_WORDS)
    assert result["overall"] < 0.40


def test_buzzwords_active_on_short_text():
    # count-based metric stays active by design
    result = slop_score("Leverage cutting-edge synergy robustly.")
    assert result["dimensions"]["buzzwordSlop"] > 0


def test_twenty_word_text_partial_activation():
    result = slop_score(TWENTY_WORDS)
    skipped = {s["metric"] for s in result["skipped"]}
    assert "repetition" not in skipped          # >= 20 words
    assert "density" in skipped                 # < 40 words
    assert "burstiness" in skipped


def test_fifty_word_text_all_active():
    result = slop_score(FIFTY_WORDS)
    assert result["skipped"] == []
    active, _ = active_metrics(FIFTY_WORDS, load_short_text_guards())
    assert all(active.values())


def test_weight_renormalization():
    # skipped metrics' weights are redistributed, not dropped from the scale:
    # a text where every active metric is 0 must score exactly 0.0
    result = slop_score("One two three four five.")
    assert result["overall"] == 0.0


def test_skipped_metric_reports_reason():
    result = slop_score(FIVE_WORDS)
    by_metric = {s["metric"]: s for s in result["skipped"]}
    assert by_metric["density"]["reason"] == "words<40"
    assert by_metric["burstiness"]["minimum"] >= 3
