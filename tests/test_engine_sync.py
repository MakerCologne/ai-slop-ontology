"""
Behavioral parity between the two detection engines.

src/ and skills/ai-slop-detection/scripts/ intentionally duplicate the core
matching logic — the skill must stay self-contained because it is copied into
agent environments on its own. Full packaging was considered and rejected
(see REVIEW-2026-07.md §4). This test pins the shared behavior so the copies
cannot silently drift apart.
"""

import os
import sys
import unittest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "skills", "ai-slop-detection", "scripts"))

import scorer as src_scorer
import slop_scorer as skill_scorer

FIXTURES = [
    "a rich tapestry of ideas within the realm of realms",
    "thermodynamics is not dynamic, but dynamics are dynamic",
    "delve here and delve there — let's delve deeper",
    "in today's rapidly evolving landscape, it's worth noting that we unlock",
    "in conclusion, to sum up: in conclusion,",
    "Ein ganzheitlicher Ansatz im digitalen Zeitalter",
    "",
    "punctuation-only !!! ... ---",
]

TERM_SETS = [
    ["tapestry", "rich tapestry"],
    ["dynamic", "dynamics"],
    ["delve", "delve deeper"],
    ["in conclusion", "in conclusion,"],
    ["realm", "the realm of"],
    ["im digitalen zeitalter", "ganzheitlicher ansatz"],
    ["Rich Tapestry", "DELVE"],  # mixed case must normalize identically
]


class TestFindTermMatchesParity(unittest.TestCase):
    def test_identical_results_on_fixtures(self):
        for text in FIXTURES:
            for terms in TERM_SETS:
                a = src_scorer.find_term_matches(text.lower(), terms)
                b = skill_scorer.find_term_matches(text.lower(), terms)
                self.assertEqual(
                    a, b,
                    f"engines drifted for text={text!r} terms={terms}: {a} != {b}",
                )


class TestSharedDimensionParity(unittest.TestCase):
    TEXTS = [
        "One. Two words. Three little words. Four very small words here.",
        "The bridge opened in 1932. It spans 503 metres across the harbour.",
        "delve delve delve delve",
    ]

    def test_density_repetition_burstiness_agree(self):
        for text in self.TEXTS:
            self.assertAlmostEqual(
                src_scorer.information_density(text),
                skill_scorer.information_density(text),
                msg=f"density drift for {text!r}")
            self.assertAlmostEqual(
                src_scorer.repetition_ratio(text),
                skill_scorer.repetition_ratio(text),
                msg=f"repetition drift for {text!r}")
            self.assertAlmostEqual(
                src_scorer.burstiness(text),
                skill_scorer.burstiness(text),
                msg=f"burstiness drift for {text!r}")


if __name__ == "__main__":
    unittest.main()
