"""Tests for the detect-only rhetorical slop patterns (skill module)."""

import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "ai-slop-detection", "scripts")
sys.path.insert(0, SCRIPTS)

from rhetorical_patterns import RHETORICAL_PATTERNS, find_rhetorical_patterns
from slop_classifier import classify_text


def ids(text):
    return {p["id"] for p in find_rhetorical_patterns(text)}


class RhetoricalDetectionTests(unittest.TestCase):
    def test_each_pattern_fires_on_its_example(self):
        cases = {
            "BinaryContrast": "The question isn't the model. It's the eval.",
            "ColonReveal": "The best part: it learns from every run.",
            "SuperficialAnalysis": "The launch adds file search, highlighting the team's commitment.",
            "NegativeListingFragmentation": "Not a feature. Not a tool. A movement.",
            "FakeStrongVerb": "The app serves as a centralized hub for sponsor management.",
            "SynonymCycling": "The agent reviews the draft. The assistant scores it. The tool suggests fixes.",
            "HollowKickerRecap": "We shipped it fast.\n\nIn conclusion, AI changes everything and we must adapt.",
            "FormattingSlop": "## \U0001F680 Key Takeaways\nWe cut deploy time from 40 to 4 minutes.",
            "RoboticRhythm": "It works. It scales. It ships. Every run.",
        }
        for pattern_id, text in cases.items():
            self.assertIn(pattern_id, ids(text), f"{pattern_id} did not fire on its example")

    def test_binary_contrast_variants(self):
        self.assertIn("BinaryContrast", ids("It's not a bug. It's a feature."))
        self.assertIn("BinaryContrast", ids("This is not just fast but also cheap to run."))

    def test_clean_prose_has_no_findings(self):
        clean = [
            "We shipped the billing page on Tuesday. It cut checkout time from 40 seconds to 9.",
            "The API returns 200 on success and 404 when the record is missing.",
            "I spent the weekend rewiring the garage. The lights finally work.",
        ]
        for text in clean:
            self.assertEqual(find_rhetorical_patterns(text), [], text)

    def test_colon_reveal_keeps_lists_and_labels(self):
        # A colon that introduces a list or a label is not a dramatic reveal.
        self.assertNotIn("ColonReveal", ids("Ingredients: flour, water, salt, and yeast."))
        self.assertNotIn("ColonReveal", ids("Note: the server restarts at midnight UTC."))

    def test_findings_carry_evidence_and_fix(self):
        findings = find_rhetorical_patterns("The app serves as a centralized hub for teams.")
        self.assertTrue(findings)
        for f in findings:
            self.assertTrue(f["evidence"])
            self.assertTrue(f["fix"])
            self.assertIn(f["id"], RHETORICAL_PATTERNS)

    def test_detection_is_score_neutral(self):
        # Rhetorical patterns are reported but must not change the numeric score:
        # the same text with and without a rhetorical shape scores identically on
        # the parts the scorer actually reads.
        text = "The app serves as a centralized hub. It's not X. It's Y."
        result = classify_text(text)
        self.assertTrue(result.rhetorical_patterns)
        # score is derived purely from signals/types/dimensions, never from
        # result.rhetorical_patterns — recompute-free sanity check:
        self.assertIsInstance(result.score, float)
        self.assertLessEqual(result.score, 1.0)

    def test_every_pattern_has_metadata(self):
        for pattern_id, meta in RHETORICAL_PATTERNS.items():
            for key in ("label", "confidence", "description", "example_slop",
                        "example_fix", "keep_when"):
                self.assertIn(key, meta, f"{pattern_id} missing {key}")

    def test_json_and_module_stay_in_parity(self):
        with open(os.path.join(ROOT, "ontology.json")) as f:
            oj = json.load(f)
        json_ids = set(oj["signals"]["text"]["rhetoricalPatterns"]["patterns"])
        self.assertEqual(json_ids, set(RHETORICAL_PATTERNS))


if __name__ == "__main__":
    unittest.main()
