"""Tests for portability dimension (issue #14) — 14th scoring dimension."""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "ai-slop-detection", "scripts")
sys.path.insert(0, SCRIPTS)

from portability import portability_stats
from slop_scorer import slop_score


PORTABLE = (
    "It works out of the box and needs no setup. "
    "You can change the defaults later if you want. "
    "The whole thing runs in a few seconds."
)
CONCRETE = (
    "In March 2026, Maria Chen of Stanford published the trial in Nature. "
    "The study cites \"prior work by O'Neill et al.\" and reports 98% uptake. "
    "See https://example.com/study for the dataset."
)
GERMAN_PORTABLE = (
    "Es funktioniert sofort und braucht keine einrichtung. "
    "Man kann die defaults später ändern. "
    "Das ganze läuft in wenigen sekunden."
)


class PortabilityModuleTests(unittest.TestCase):
    def test_fully_portable_text_rates_one(self):
        stats = portability_stats(PORTABLE)
        self.assertEqual(stats["total"], 3)
        self.assertEqual(stats["portable_sentences"], 3)
        self.assertAlmostEqual(stats["rate"], 1.0)

    def test_concrete_text_is_not_portable(self):
        stats = portability_stats(CONCRETE)
        self.assertEqual(stats["portable_sentences"], 0)
        self.assertAlmostEqual(stats["rate"], 0.0)

    def test_german_mid_sentence_capitals_block_portability(self):
        # German capitalizes nouns mid-sentence — a portable-by-accident
        # German sentence must not count as "no proper names".
        stats = portability_stats("Der Wagen fährt schnell. Die Straße ist nass.")
        self.assertEqual(stats["portable_sentences"], 0)

    def test_german_lowercase_text_is_portable(self):
        stats = portability_stats(GERMAN_PORTABLE)
        self.assertAlmostEqual(stats["rate"], 1.0)


class PortabilityScorerTests(unittest.TestCase):
    def test_slop_score_exposes_portability_dimension(self):
        result = slop_score(PORTABLE)
        self.assertIn("portability_rate", result["dimensions"])
        self.assertAlmostEqual(result["dimensions"]["portability_rate"], 1.0)
        self.assertIn("portability_slop", result["dimension_scores"])
        self.assertEqual(result["dimension_scores"]["portability_slop"], 1.0)
        self.assertTrue(result["signals"]["high_portability"])

    def test_concrete_text_no_portability_signal(self):
        result = slop_score(CONCRETE)
        self.assertAlmostEqual(result["dimensions"]["portability_rate"], 0.0)
        self.assertEqual(result["dimension_scores"]["portability_slop"], 0.0)
        self.assertFalse(result["signals"]["high_portability"])


if __name__ == "__main__":
    unittest.main()
