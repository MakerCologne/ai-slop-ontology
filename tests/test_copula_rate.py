"""Issue #22: copula rate — is/are/was/were vs. substitute verbs.

AI-generated definition-slop leans on copula constructions ("X is Y",
"the key is balance") while varied human prose uses substitutes (serves as,
boasts, features, refers to, represents, embodies). The rate is a CONDITIONAL
score contribution (small weight), never a standalone trigger, and never
double-counts with fake-strong-verb buzzword signals (#46 prevention):
substitute-verb matches that overlap buzzword spans ("serves as a
testament") are excluded from the rate denominator — they are already
scored as buzzwords.

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

COPULA_HEAVY = (
    "Balance is the foundation of a good week. The core principle is simple: "
    "rest is productive. Sleep is recovery. Focus is a skill, and a skill is "
    "something you train. The result is a calmer week, and a calmer week is "
    "what most people want."
)

SUBSTITUTE_HEAVY = (
    "The old mill serves as the village museum and boasts three working "
    "looms. The garden features heritage roses; the annex refers to the "
    "original bakery and represents the oldest trade in the valley. The "
    "clock tower embodies the town's self-image."
)


class TestCopulaStats(unittest.TestCase):
    def test_copula_counts(self):
        stats = slop_scorer.copula_stats(COPULA_HEAVY)
        self.assertGreaterEqual(stats["copulas"], 8)
        self.assertEqual(stats["substitutes"], 0)
        self.assertGreaterEqual(stats["rate"], 0.9)

    def test_substitutes_lower_rate(self):
        stats = slop_scorer.copula_stats(SUBSTITUTE_HEAVY)
        self.assertGreaterEqual(stats["substitutes"], 5)
        self.assertLess(stats["rate"], 0.5)

    def test_buzzword_substitutes_are_excluded_from_denominator(self):
        # #46 prevention: "serves as a testament" is a tier-1 buzzword —
        # counting it as a copula substitute would reward the exact phrase
        # that the buzzword dimension already penalizes.
        text = "This building serves as a testament to modern design. It is large."
        stats = slop_scorer.copula_stats(text)
        self.assertEqual(stats["substitutes"], 0)
        self.assertEqual(stats["rate"], 1.0)


class TestCopulaRateInScorer(unittest.TestCase):
    def test_copula_dimension_present(self):
        result = slop_scorer.slop_score(COPULA_HEAVY)
        self.assertIn("copula_slop", result["dimension_scores"])
        self.assertGreater(result["dimension_scores"]["copula_slop"], 0.0)

    def test_substitute_heavy_text_gets_no_copula_contribution(self):
        result = slop_scorer.slop_score(SUBSTITUTE_HEAVY)
        self.assertEqual(result["dimension_scores"]["copula_slop"], 0.0)

    def test_copula_alone_does_not_flag_text(self):
        # Conditional contribution only: a dry, definition-heavy but factual
        # paragraph must stay below the threshold on copula rate alone.
        factual = (
            "A lease is a contract. A contract is an agreement. An agreement "
            "is a meeting of minds. Termination is the ending of the lease. "
            "Notice is a written declaration."
        )
        result = slop_scorer.slop_score(factual)
        self.assertLess(result["slop_score"], 0.40)

    def test_clean_technical_text_zero_copula_slop(self):
        result = slop_scorer.slop_score(
            "The collector paused 4.2 ms. We shrank the nursery and measured "
            "promotion rates before reverting the change after the soak test.")
        self.assertEqual(result["dimension_scores"]["copula_slop"], 0.0)


if __name__ == "__main__":
    unittest.main()
