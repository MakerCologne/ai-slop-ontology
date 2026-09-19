"""Tests for issue #249 gap work: filler phrases (G7) and BriefLeak (G8).

Evidence discipline (eval/corpus.jsonl, counted 2026-09-19):
  - "in order to"                 13 slop / 0 clean
  - "due to the fact that"        15 slop / 0 clean
  - "while specific details are limited"  7 slop / 0 clean
  - "hope this helps"              8 slop / 0 clean (assistant signoff)
"""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "ai-slop-detection", "scripts")
sys.path.insert(0, SCRIPTS)

from slop_scorer import PHRASE_CATEGORIES


class FillerPhraseTests(unittest.TestCase):
    def test_filler_phrases_category_exists(self):
        cat = PHRASE_CATEGORIES["filler_phrases"]
        self.assertEqual(cat["confidence"], 0.7)
        self.assertIn("in order to", cat["phrases"])
        self.assertIn("due to the fact that", cat["phrases"])
        self.assertIn("while specific details are limited", cat["phrases"])

    def test_no_double_counting_with_assistant_signoff(self):
        # "in order to" (filler_phrases) subsumes the old
        # "in order to proceed" entry; the longer variant must be gone.
        signoff = PHRASE_CATEGORIES["assistant_signoff"]["phrases"]
        self.assertNotIn("in order to proceed", signoff)

    def test_subsumed_signoff_variant_still_matches(self):
        self.assertIn("hope this helps",
                      PHRASE_CATEGORIES["assistant_signoff"]["phrases"])

    def test_brief_leak_phrases_in_meta_commentary(self):
        # Issue #249/G8: briefing register leaking into artefacts extends
        # meta_commentary instead of adding a new signal.
        meta = PHRASE_CATEGORIES["meta_commentary"]["phrases"]
        self.assertIn("as per your request", meta)
        self.assertIn("per your request", meta)
        self.assertIn("as requested", meta)


if __name__ == "__main__":
    unittest.main()
