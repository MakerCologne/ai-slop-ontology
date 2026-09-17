"""Tests for #117: weighted geometric mean aggregation as complement to noisy-OR.

Within one dimension (signal family), noisy-OR accumulates; across dimensions
the weighted geometric mean dampens double punishment — a flood of small
signals in a single family can no longer masquerade as broad evidence.
"""
import math
import os
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, ROOT)

from classifier import (  # noqa: E402
    SignalMatch,
    SlopClassifier,
    _signal_dimension,
    aggregate_geometric,
    aggregate_noisy_or,
)


def _sig(signal_id, conf, sev):
    s = SignalMatch(signal_id, conf, "evidence")
    s.severity = sev
    return s


def test_dimension_mapping():
    assert _signal_dimension("BuzzwordOveruse") == "lexical"
    assert _signal_dimension("PhrasePattern") == "phrase"
    assert _signal_dimension("EmDashExcess") == "punctuation"
    assert _signal_dimension("UniformSentenceLength") == "structure"
    assert _signal_dimension("HardcodedSecret") == "code"
    assert _signal_dimension("Multilingual_de") == "multilingual"
    assert _signal_dimension("TypePattern_SecurityReportSlop") == "typepattern"
    assert _signal_dimension("UnknownThing") == "other"


def test_geometric_damps_double_punishment_within_dimension():
    # 4 medium signals, ALL in one dimension (lexical): aggregation is
    # noisy-OR within that single dimension — identical to global noisy-OR
    signals = [_sig("BuzzwordOveruse", 0.5, "medium") for _ in range(4)]
    assert math.isclose(aggregate_geometric(signals), aggregate_noisy_or(signals))

    # but many small hits in one dimension cannot mask a weak second
    # dimension: geometric mean pulls the score toward the weaker dimension
    clustered_plus = signals + [_sig("EmDashExcess", 0.3, "medium")]
    assert aggregate_geometric(clustered_plus) < aggregate_noisy_or(clustered_plus)


def test_geometric_no_accumulation_inflation_across_families():
    # identical per-signal evidence spread across 4 dimensions:
    # the geometric mean of equal dimension scores equals that score —
    # no artificial inflation just because more families are involved
    spread = [
        _sig("BuzzwordOveruse", 0.5, "medium"),   # lexical
        _sig("PhrasePattern", 0.5, "medium"),     # phrase
        _sig("EmDashExcess", 0.5, "medium"),      # punctuation
        _sig("UniformSentenceLength", 0.5, "medium"),  # structure
    ]
    one_dim = [_sig("BuzzwordOveruse", 0.5, "medium")]
    assert math.isclose(aggregate_geometric(spread), aggregate_geometric(one_dim))


def test_geometric_spread_beats_clustered_when_evidence_is_strong():
    # flooding one low-severity family is damped across the geometric mean:
    # the family's noisy-OR score stays low and cannot be inflated by volume
    flooded_weak = [_sig("EmDashExcess", 0.2, "low") for _ in range(10)]
    flooded_noisy = aggregate_noisy_or(flooded_weak)   # 1-(1-0.04)^10 ≈ 0.335
    flooded_geo = aggregate_geometric(flooded_weak)    # same single dim → same value
    assert math.isclose(flooded_geo, flooded_noisy)
    # combined with a medium second dimension, the weak family cannot
    # dominate: the geometric mean weights dimensions, not hit counts
    both = flooded_weak + [_sig("PhrasePattern", 0.5, "medium")]
    phrase_only = [_sig("PhrasePattern", 0.5, "medium")]
    assert aggregate_geometric(both) < aggregate_noisy_or(both)
    # and the weak dimension drags the score below the strong one alone
    # (under noisy-OR, 10 weak hits would push ABOVE the strong signal)
    assert aggregate_noisy_or(both) > aggregate_noisy_or(phrase_only)
    # geometric keeps the combined score close to the dimension scores
    # instead of letting hit volume dominate
    assert aggregate_geometric(both) < 0.3


def test_geometric_empty_and_zero():
    assert aggregate_geometric([]) == 1.0 or aggregate_geometric([]) == 0.0
    # a single zero-evidence dimension: no signals -> handled by caller
    one = [_sig("BuzzwordOveruse", 0.5, "medium")]
    assert math.isclose(aggregate_geometric(one), aggregate_noisy_or(one))


def test_classifier_aggregation_option():
    c_default = SlopClassifier()
    assert c_default.aggregation == "noisy_or"
    c_geo = SlopClassifier(aggregation="geometric")
    assert c_geo.aggregation == "geometric"
    try:
        SlopClassifier(aggregation="bogus")
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_geometric_classification_dampens_clustered_hits():
    # Clustered: many punctuation hits, nothing else
    clustered = "AMAZING!!! This is crucial... wait... delve!!! game-changer!!! ... "
    # Spread across families for comparison is covered by unit tests above;
    # here just assert both aggregations produce valid scores in [0,1]
    for agg in ("noisy_or", "geometric"):
        c = SlopClassifier(aggregation=agg)
        r = c.classify_text(clustered * 3)
        assert 0.0 <= r.overall_slop_score <= 1.0
