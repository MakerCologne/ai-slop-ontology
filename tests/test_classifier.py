"""Tests for src/classifier.py against the shipped ontology.json."""

import os
import sys
import unittest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "src"))

from classifier import SlopClassifier

ONTOLOGY = os.path.join(ROOT, "ontology.json")


class TestSlopClassifier(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.clf = SlopClassifier(ONTOLOGY)

    def test_signal_stats_languages_exclude_metadata(self):
        # Regression: "description" key must not be reported as a language
        stats = self.clf.get_signal_stats()
        self.assertNotIn("description", stats["languages"])
        self.assertIn("german", stats["languages"])

    def test_clean_text(self):
        result = self.clf.classify_text(
            "The bridge opened in 1932. It spans 503 metres. "
            "Engineers used 52,800 tonnes of steel."
        )
        self.assertEqual(result.severity, "clean")
        self.assertEqual(result.overall_slop_score, 0.0)

    def test_sloppy_text_is_flagged(self):
        result = self.clf.classify_text(
            "In today's rapidly evolving digital landscape, it's important to note "
            "that the rich tapestry of AI serves as a testament to innovation. "
            "Furthermore, let's dive into how these cutting-edge solutions unlock "
            "your potential and harness the power of transformative technology."
        )
        self.assertGreaterEqual(result.overall_slop_score, 0.70)
        self.assertEqual(result.severity, "slop_candidate")

    def test_severity_assigned_to_signals(self):
        result = self.clf.classify_text(
            "In today's rapidly evolving landscape, let's dive into the rich tapestry."
        )
        for s in result.signals_detected:
            self.assertIn(s.severity, ("critical", "high", "medium", "low"))

    def test_no_overlap_double_count(self):
        result = self.clf.classify_text("A rich tapestry.")
        words = [w for hits in result.buzzword_report.values() for w, _ in hits]
        self.assertIn("rich tapestry", words)
        self.assertNotIn("tapestry", words)

    def test_german_multilingual_detection(self):
        result = self.clf.classify_text(
            "Im heutigen schnelllebigen digitalen Zeitalter gilt es zu beachten, "
            "dass ein ganzheitlicher Ansatz die Synergieeffekte hebt."
        )
        self.assertTrue(
            any(s.signal_id == "Multilingual_german" for s in result.signals_detected),
            f"expected german signal, got {[s.signal_id for s in result.signals_detected]}",
        )

    def test_code_hardcoded_secret_escalates(self):
        result = self.clf.classify_code('api_key = "sk-abcdef1234567890"')
        self.assertTrue(
            any(s.signal_id == "HardcodedSecret" for s in result.signals_detected)
        )
        self.assertGreaterEqual(result.overall_slop_score, 0.70)


if __name__ == "__main__":
    unittest.main()
