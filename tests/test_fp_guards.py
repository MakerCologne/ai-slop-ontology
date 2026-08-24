"""Issue #23: False-positive guard systematics in the skill scorer.

Guards live in their own module (fp_guards.py, next to slop_scorer.py):
  (a) quote exemption — quoted passages above QUOTE_MIN_CHARS are excluded
      from buzzword/phrase/authority signal matching
  (b) cumulative rule — a phrase category only contributes to phrase_slop
      when it has >= 2 hits (single hits are reported, not scored)
  (c) consistent thresholds — decision/guard thresholds centralized in
      fp_guards.THRESHOLDS instead of scattered magic numbers

Red tests 2026-08-24.
"""

import json
import os
import sys
import unittest

SCRIPTS = os.path.join(
    os.path.dirname(__file__), "..", "skills", "ai-slop-detection", "scripts"
)
sys.path.insert(0, SCRIPTS)

import fp_guards  # noqa: E402
import slop_scorer  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_control_set_item(item_id):
    with open(os.path.join(ROOT, "eval", "control_set.jsonl")) as f:
        for line in f:
            if line.strip():
                item = json.loads(line)
                if item["id"] == item_id:
                    return item["text"]
    raise KeyError(item_id)


class TestStripQuotes(unittest.TestCase):
    def test_long_quoted_span_is_stripped(self):
        inner = "This quoted passage is long enough to exceed the guard threshold for sure."
        text = "Intro sentence. \"" + inner + "\" Closing sentence."
        stripped = fp_guards.strip_quotes(text)
        self.assertNotIn("quoted passage", stripped)
        self.assertIn("Intro sentence.", stripped)
        self.assertIn("Closing sentence.", stripped)

    def test_short_quoted_span_is_kept(self):
        text = 'He said "delve" once and left the room quietly.'
        stripped = fp_guards.strip_quotes(text)
        self.assertIn("delve", stripped)

    def test_curly_quotes_are_stripped(self):
        inner = "A curly quoted passage that is definitely longer than the configured minimum length."
        text = "Prefix. \u201c" + inner + "\u201d Suffix."
        stripped = fp_guards.strip_quotes(text)
        self.assertNotIn("curly quoted passage", stripped)
        self.assertIn("Prefix.", stripped)

    def test_text_without_quotes_unchanged(self):
        text = "No quotes here at all, just plain technical prose."
        self.assertEqual(fp_guards.strip_quotes(text), text)


class TestQuoteExemptionInScorer(unittest.TestCase):
    def test_technical_text_quoting_slop_paragraph_stays_below_threshold(self):
        # Meta / F1 self-test case: documenting or reviewing slop (e.g. a
        # SKILL.md-style doc quoting a slop example) must not be flagged.
        slop_example = load_control_set_item("slop-max-01")
        wrapped = (
            "The vendor pitch we received yesterday is reproduced below for the record.\n\n\""
            + slop_example
            + "\"\n\nWe did not adopt any of these claims. The measured latency "
              "increase was 3 ms under load, and the license audit failed on two clauses."
        )
        score = slop_scorer.slop_score(wrapped)["slop_score"]
        self.assertLess(score, 0.40, f"quoted slop flagged: {score}")

    def test_same_slop_unquoted_is_still_flagged(self):
        score = slop_scorer.slop_score(load_control_set_item("slop-max-01"))["slop_score"]
        self.assertGreaterEqual(score, 0.40)


class TestCumulativePhraseRule(unittest.TestCase):
    def test_single_phrase_hit_is_not_scored(self):
        text = ("Here's the thing: the build failed because a cached dependency "
                "shadowed the local patch. We pinned the version and the suite "
                "went green again on the second run.")
        result = slop_scorer.slop_score(text)
        self.assertEqual(result["dimension_scores"]["phrase_slop"], 0.0)

    def test_two_hits_in_same_category_are_scored(self):
        text = ("Here's the thing: the build failed. Here's the kicker: nobody "
                "had pinned the dependency. The suite went green after we fixed it.")
        result = slop_scorer.slop_score(text)
        self.assertGreater(result["dimension_scores"]["phrase_slop"], 0.0)

    def test_single_hit_is_still_reported_as_signal(self):
        text = "Here's the thing: the build failed because a cached dependency shadowed the local patch."
        result = slop_scorer.slop_score(text)
        self.assertIn("listicle_tells", result["signals"]["phrase_categories"])


class TestConsistentThresholds(unittest.TestCase):
    def test_thresholds_module_constants(self):
        self.assertIn("DECISION_THRESHOLD", fp_guards.THRESHOLDS)
        self.assertIn("QUOTE_MIN_CHARS", fp_guards.THRESHOLDS)
        self.assertIn("PHRASE_MIN_HITS", fp_guards.THRESHOLDS)
        self.assertEqual(fp_guards.THRESHOLDS["DECISION_THRESHOLD"], 0.40)
        self.assertEqual(fp_guards.THRESHOLDS["PHRASE_MIN_HITS"], 2)

    def test_scorer_uses_fp_guards_thresholds(self):
        self.assertIs(slop_scorer.DECISION_THRESHOLD,
                      fp_guards.THRESHOLDS["DECISION_THRESHOLD"])


if __name__ == "__main__":
    unittest.main()
