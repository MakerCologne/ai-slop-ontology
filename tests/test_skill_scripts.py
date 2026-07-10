"""Tests for the self-contained skill scripts (skills/ai-slop-detection/scripts)."""

import os
import sys
import unittest

SCRIPTS = os.path.join(
    os.path.dirname(__file__), "..", "skills", "ai-slop-detection", "scripts"
)
sys.path.insert(0, SCRIPTS)

import slop_scorer
from slop_classifier import classify_text


class TestSkillScorer(unittest.TestCase):
    def test_german_multilingual_matches(self):
        # Regression: entries with capital letters ("im digitalen Zeitalter")
        # were compared unlowered against lowered text and never matched.
        result = slop_scorer.multilingual_buzzword_score(
            "Im heutigen schnelllebigen digitalen Zeitalter gilt es zu beachten, "
            "dass der Gamechanger ein ganzheitlicher Ansatz ist."
        )
        self.assertIn("german", result)
        self.assertGreaterEqual(len(result["german"]), 3)

    def test_german_slop_floors_at_suspicious(self):
        result = slop_scorer.slop_score(
            "Im heutigen schnelllebigen digitalen Zeitalter gilt es zu beachten, "
            "dass ein ganzheitlicher Ansatz die Synergieeffekte hebt. "
            "Zusammenfassend lässt sich sagen, dass der Gamechanger ein "
            "tiefgreifender Wandel ist."
        )
        self.assertGreaterEqual(result["slop_score"], 0.40)

    def test_short_text_burstiness_neutral(self):
        result = slop_scorer.slop_score("The report shows revenue grew 4 percent.")
        self.assertEqual(result["dimension_scores"]["burstiness_slop"], 0.0)

    def test_overlap_dedup(self):
        _, hits, _ = slop_scorer.buzzword_score("A rich tapestry of ideas.")
        self.assertIn("rich tapestry", hits)
        self.assertNotIn("tapestry", hits)

    def test_heavy_slop_flagged(self):
        text = (
            "In today's rapidly evolving digital landscape, it's important to note "
            "that the rich tapestry of AI serves as a testament to innovation. "
            "Furthermore, studies have shown that cutting-edge solutions unlock "
            "your potential. In conclusion, embrace the future — the possibilities "
            "are endless. Ultimately, what matters most is the journey."
        )
        result = slop_scorer.slop_score(text)
        self.assertGreaterEqual(result["slop_score"], 0.40)

    def test_mirrored_needs_content_words(self):
        # Stopword-only overlap must not trigger the mirror signal
        text = "It is a thing. Something happened. More text here. It is a thing of."
        self.assertFalse(slop_scorer.mirrored_intro_conclusion(text))


class TestSkillClassifier(unittest.TestCase):
    def test_clean(self):
        result = classify_text("The bridge opened in 1932. It spans 503 metres.")
        self.assertEqual(result.severity, "clean")

    def test_security_report_slop_type(self):
        result = classify_text(
            "This vulnerability could potentially allow an attacker to execute "
            "arbitrary code. Severity: critical. An attacker could potentially "
            "bypass authentication. Proof of concept below."
        )
        self.assertIn("SecurityReportSlop", [t.name for t in result.slop_types])

    def test_peer_review_slop_type(self):
        result = classify_text(
            "The authors present an interesting approach. The manuscript is well "
            "written and would benefit from additional experiments. The related "
            "work section could be expanded. Minor revisions recommended."
        )
        self.assertIn("PeerReviewSlop", [t.name for t in result.slop_types])


if __name__ == "__main__":
    unittest.main()
