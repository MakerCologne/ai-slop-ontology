"""Tests for src/scorer.py — each engine fix has a regression test."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from scorer import (
    burstiness,
    buzzword_score,
    find_term_matches,
    information_density,
    list_heavy,
    repetition_ratio,
    slop_score,
    trailing_moral,
)


class TestTermMatching(unittest.TestCase):
    def test_word_boundaries(self):
        # "dynamic" must not match inside "thermodynamics"
        self.assertEqual(find_term_matches("thermodynamics is fun", ["dynamic"]), {})
        self.assertIn("dynamic", find_term_matches("a dynamic system", ["dynamic"]))

    def test_overlap_dedup_longest_wins(self):
        counts = find_term_matches(
            "a rich tapestry of ideas", ["tapestry", "rich tapestry"]
        )
        self.assertEqual(counts, {"rich tapestry": 1})

    def test_counts_multiple_occurrences(self):
        counts = find_term_matches("delve here and delve there", ["delve"])
        self.assertEqual(counts, {"delve": 2})

    def test_phrase_with_apostrophe(self):
        counts = find_term_matches(
            "in today's rapidly evolving world", ["in today's rapidly evolving"]
        )
        self.assertEqual(len(counts), 1)


class TestDimensions(unittest.TestCase):
    def test_information_density_empty(self):
        self.assertEqual(information_density(""), 0.0)

    def test_information_density_all_unique(self):
        self.assertEqual(information_density("one two three"), 1.0)

    def test_repetition_ratio(self):
        self.assertAlmostEqual(repetition_ratio("spam spam spam eggs"), 0.75)

    def test_burstiness_single_sentence(self):
        self.assertEqual(burstiness("Just one sentence here."), 0.0)

    def test_trailing_moral(self):
        self.assertTrue(trailing_moral("Blah blah. Ultimately, kindness wins."))
        self.assertFalse(trailing_moral("A plain factual statement."))

    def test_list_heavy(self):
        text = "- a\n- b\n- c\n- d\nprose line"
        self.assertTrue(list_heavy(text))
        self.assertFalse(list_heavy("just\nplain\nlines\nof prose"))


class TestSlopScore(unittest.TestCase):
    def test_short_text_burstiness_neutral(self):
        # Regression: 1-2 sentence texts must not be penalized for uniformity
        result = slop_score("The quarterly report shows revenue grew 4 percent.")
        self.assertEqual(result["dimensions"]["burstinessSlop"], 0.0)

    def test_buzzword_overlap_not_double_counted(self):
        tiers = {"tier1": ["tapestry", "rich tapestry"]}
        count, hits = buzzword_score("This is a rich tapestry.", tiers)
        self.assertEqual(count, 1)
        self.assertEqual(hits, ["rich tapestry (tier1)"])

    def test_clean_text_scores_low(self):
        clean = (
            "The bridge opened in 1932. It spans 503 metres across the harbour. "
            "Engineers used 52,800 tonnes of steel. Six million rivets hold it together."
        )
        self.assertLess(slop_score(clean)["overall"], 0.4)

    def test_sloppy_text_scores_higher_than_clean(self):
        sloppy = (
            "In today's fast-paced digital landscape, leveraging cutting-edge AI "
            "is paramount to unlock game-changing synergy. It's important to note "
            "that a robust paradigm delivers results. Ultimately, what matters most "
            "is the journey."
        )
        clean = (
            "The bridge opened in 1932. It spans 503 metres across the harbour. "
            "Engineers used 52,800 tonnes of steel. Six million rivets hold it together."
        )
        self.assertGreater(slop_score(sloppy)["overall"], slop_score(clean)["overall"])


if __name__ == "__main__":
    unittest.main()
