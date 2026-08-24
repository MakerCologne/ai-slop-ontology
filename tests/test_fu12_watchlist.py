"""
FU-12 (Batch F review, recommendation 2) — Generic-Phrase-Watchlist.

review-batch-f.md constructed two FP probes from everyday human working
prose that crossed the 0.40 threshold purely on generic phrases:
  P1  "Going forward, ... robust ... in other words, double-check ..." -> 0.400
  P2  "The good news is ... The bad news is ... Final thoughts: ..."   -> 0.556
Decision (with rationale): the reviewer's watchlist phrases ("in other
words", "going forward", "to be clear", "as you can see", "the good
news is", "the bad news is", "the best part:") move into their own
low-confidence category (0.65 — outside the >= 0.75 single-hit
escalation family) with a RAISED cumulative threshold of >= 3 hits
instead of 2. Everyday human prose uses these singly or in pairs;
slop saturates. Benchmark P 1.0 / R 0.982 / FP=0 must not regress
(measured before/after, see CHANGELOG Batch G).
"""

import os
import sys
import unittest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(
    ROOT, "skills", "ai-slop-detection", "scripts"))

import slop_scorer  # noqa: E402
import fp_guards  # noqa: E402

PROBE_P1 = ("Going forward, we will use a robust process for every "
            "release. In other words, double-check everything.")
PROBE_P2 = ("The good news is that the fix landed. The bad news is that "
            "we missed the deadline. Final thoughts: ship small.")


class TestFU12GenericPhraseWatchlist(unittest.TestCase):
    def test_reviewer_probe_p1_below_threshold(self):
        score = slop_scorer.slop_score(PROBE_P1)
        self.assertLess(score["slop_score"], 0.40,
                        f"P1 scored {score['slop_score']} — Reviewer-"
                        "Gegenprobe muss unter 0.40 fallen (FU-12)")

    def test_reviewer_probe_p2_below_threshold(self):
        score = slop_scorer.slop_score(PROBE_P2)
        self.assertLess(score["slop_score"], 0.40,
                        f"P2 scored {score['slop_score']} — Reviewer-"
                        "Gegenprobe muss unter 0.40 fallen (FU-12)")

    def test_watchlist_is_own_low_confidence_category(self):
        cats = slop_scorer.PHRASE_CATEGORIES
        self.assertIn("generic_phrases", cats)
        generic = cats["generic_phrases"]
        self.assertLess(generic["confidence"], 0.75)
        self.assertEqual(generic.get("min_hits"), 3)
        for phrase in ["in other words", "going forward", "to be clear",
                       "as you can see", "the good news is",
                       "the bad news is", "the best part:"]:
            self.assertIn(phrase, generic["phrases"])
            # removed from their former high-confidence homes
        self.assertNotIn("going forward", cats["report_hedging"]["phrases"])
        self.assertNotIn("the good news is", cats["marketing_cta"]["phrases"])

    def test_generic_only_text_does_not_escalate(self):
        # two generic phrases + one buzzword: no >= 0.75 single-hit family,
        # no cumulative phrase score at the raised threshold -> below 0.40
        text = ("In other words, we keep the old pipeline. Going forward, "
                "the team will review every merge with a robust checklist.")
        score = slop_scorer.slop_score(text)
        self.assertLess(score["slop_score"], 0.40)

    def test_slop_saturation_still_flags(self):
        # 3+ generic hits: the category counts again (>= 3 rule)
        matches = slop_scorer.phrase_category_score(
            "In other words, going forward, the good news is that we ship.")
        self.assertIn("generic_phrases", matches)
        self.assertGreaterEqual(len(matches["generic_phrases"]), 3)
        count = fp_guards.effective_phrase_count(
            matches, {"generic_phrases": 3})
        self.assertGreaterEqual(count, 3)

    def test_cumulative_default_unchanged_for_strong_categories(self):
        matches = {"report_hedging": ["a pivotal moment", "studies show"]}
        self.assertEqual(fp_guards.effective_phrase_count(matches), 2)


if __name__ == "__main__":
    unittest.main()
