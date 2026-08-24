"""Issue #24: adverb rate (-ly words / total words) + conditional
intensifier contributions.

Deliberately NOT absolute triggers:
  - adverb_slop fires only above a rate threshold (> 4%) on a minimum text
    length — a single "notably" contributes nothing by itself;
  - intensifiers (very, really, extremely, incredibly, remarkably) only
    AMPLIFY an already-triggered adverb rate — they never contribute on
    their own.

Delimitation to the #21 voice principles (documented in code): #21 governs
voice/style rules for WRITING (which adverbs to prefer or cut); this signal
only MEASURES the rate in received text and never invents style judgments.
Delimitation to #22: adverbs are not verbs; no span overlap with copula or
buzzword dimensions is possible by construction.

Red tests 2026-08-24.
"""

import os
import sys
import unittest

SCRIPTS = os.path.join(
    os.path.dirname(__file__), "..", "skills", "ai-slop-detection", "scripts"
)
sys.path.insert(0, SCRIPTS)

import slop_scorer  # noqa: E402

ADVERB_HEAVY = (
    "The team quickly adapted and easily delivered remarkably clean results. "
    "Critically, we visibly improved latency; users reportedly noticed the "
    "change immediately and surprisingly praised the admittedly small win, "
    "which honestly matters greatly because performance tuning is famously "
    "thankless work that rarely gets celebrated properly."
)

ADVERB_LIGHT = (
    "The team shipped the migration after a two-week soak test. Latency "
    "improved by three percent under load. We reverted one change that "
    "reduced throughput and documented the tradeoff in the runbook for the "
    "next on-call rotation to review before promoting the build."
)

INTENSIFIERS_ONLY = (
    "The result was very good and really simple, extremely robust and "
    "incredibly fast, remarkably cheap to run at scale in production."
)


class TestAdverbStats(unittest.TestCase):
    def test_adverb_rate_computed(self):
        stats = slop_scorer.adverb_stats(ADVERB_HEAVY)
        self.assertGreater(stats["ly_words"], 10)
        self.assertGreater(stats["rate"], 0.04)

    def test_adverb_light_text_low_rate(self):
        stats = slop_scorer.adverb_stats(ADVERB_LIGHT)
        self.assertLess(stats["rate"], 0.04)

    def test_intensifiers_counted(self):
        stats = slop_scorer.adverb_stats(INTENSIFIERS_ONLY)
        self.assertEqual(stats["intensifiers"], 5)


class TestAdverbRateInScorer(unittest.TestCase):
    def test_adverb_dimension_present_and_fires_on_heavy_text(self):
        result = slop_scorer.slop_score(ADVERB_HEAVY)
        self.assertGreater(result["dimension_scores"]["adverb_slop"], 0.0)

    def test_adverb_light_text_no_contribution(self):
        result = slop_scorer.slop_score(ADVERB_LIGHT)
        self.assertEqual(result["dimension_scores"]["adverb_slop"], 0.0)

    def test_intensifiers_alone_contribute_nothing(self):
        # Conditional by design: intensifiers only amplify an adverb rate
        # that is already above threshold; on their own they must not score.
        result = slop_scorer.slop_score(INTENSIFIERS_ONLY)
        self.assertEqual(result["dimension_scores"]["adverb_slop"], 0.0)

    def test_single_adverb_contributes_nothing(self):
        result = slop_scorer.slop_score(
            "Notably, the build failed because a cached dependency shadowed "
            "the local patch. We pinned the version and the suite went green.")
        self.assertEqual(result["dimension_scores"]["adverb_slop"], 0.0)


if __name__ == "__main__":
    unittest.main()
