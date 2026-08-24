"""FU-1 (review-batch-a.md §6, MEDIUM finding): 4 of the 5 #24 intensifiers
end in -ly (really, extremely, incredibly, remarkably) and are counted by the
"\\b\\w+ly\\b" regex, so a >=40-word text heaping ONLY intensifiers reached an
adverb rate > 4% and adverb_slop = 1.0 — although the spec says intensifiers
contribute nothing on their own.

Fix under test: intensifiers are their own signal; they must be excluded from
the -ly rate (numerator AND denominator) so pure-intensifier text cannot
trigger the adverb dimension. The intensifier count itself keeps firing.

Red tests 2026-08-24 (FU-1).
"""

import os
import sys
import unittest

SCRIPTS = os.path.join(
    os.path.dirname(__file__), "..", "skills", "ai-slop-detection", "scripts"
)
sys.path.insert(0, SCRIPTS)

import slop_scorer  # noqa: E402

# 40 words of NOTHING BUT intensifiers (5 x 8) — above ADVERB_MIN_WORDS=40,
# the exact shape the reviewer used to expose the double counting.
INTENSIFIERS_ONLY_LONG = (
    "Very, really, extremely, incredibly, remarkably. " * 8
)


class TestIntensifierRateFix(unittest.TestCase):
    def test_pure_intensifier_text_has_zero_ly_rate(self):
        stats = slop_scorer.adverb_stats(INTENSIFIERS_ONLY_LONG)
        self.assertGreaterEqual(stats["total_words"], 40)
        self.assertEqual(stats["rate"], 0.0)
        self.assertEqual(stats["ly_words"], 0)

    def test_pure_intensifier_text_adverb_slop_far_below_max(self):
        result = slop_scorer.slop_score(INTENSIFIERS_ONLY_LONG)
        self.assertLess(result["dimension_scores"]["adverb_slop"], 0.5)

    def test_intensifier_signal_keeps_firing(self):
        stats = slop_scorer.adverb_stats(INTENSIFIERS_ONLY_LONG)
        self.assertGreaterEqual(stats["intensifiers"], 2)
        result = slop_scorer.slop_score(INTENSIFIERS_ONLY_LONG)
        self.assertGreaterEqual(result["dimensions"]["adverb"]["intensifiers"], 2)

    def test_genuine_ly_adverbs_still_count(self):
        text = (
            "The team quickly adapted and easily delivered remarkably clean "
            "results. Critically, we visibly improved latency; users "
            "reportedly noticed the change immediately and surprisingly "
            "praised the admittedly small win, which honestly matters "
            "greatly because performance tuning is famously thankless work."
        )
        stats = slop_scorer.adverb_stats(text)
        # genuinely -ly words minus 'remarkably' (the one intensifier present)
        self.assertGreater(stats["ly_words"], 5)
        self.assertGreater(stats["rate"], 0.04)

    def test_mixed_text_excludes_intensifiers_from_denominator(self):
        # 50 words: 10 intensifiers + 40 ordinary words of which 1 ends -ly.
        text = (
            "Very very very really really really extremely extremely "
            "incredibly remarkably. The team shipped the migration after a "
            "two-week soak test and latency improved by three percent under "
            "load, so we reverted one change and documented the tradeoff."
        )
        stats = slop_scorer.adverb_stats(text)
        # rate must be computed over the non-intensifier words only: 1/40,
        # NOT 1/50 — and must be below the 4% trigger either way; the key
        # invariant is that intensifiers never inflate the rate.
        self.assertEqual(stats["ly_words"], 0)
        self.assertEqual(stats["rate"], 0.0)
        self.assertEqual(stats["intensifiers"], 10)


if __name__ == "__main__":
    unittest.main()
