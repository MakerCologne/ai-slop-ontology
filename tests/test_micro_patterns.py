"""Tests for micro-pattern detect-only signals (issue #13)."""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "ai-slop-detection", "scripts")
sys.path.insert(0, SCRIPTS)

from micro_patterns import find_micro_patterns, MICRO_PATTERNS


def ids(text):
    return {p["id"] for p in find_micro_patterns(text)}


class MicroPatternTests(unittest.TestCase):
    def test_each_pattern_has_keep_when_guard_and_examples(self):
        for pid, meta in MICRO_PATTERNS.items():
            self.assertIn("keep_when", meta, f"{pid} missing keep_when guard")
            self.assertIn("example_slop", meta)
            self.assertIn("example_fix", meta)

    # --- FalseAgency ---

    def test_false_agency_positive(self):
        self.assertIn("FalseAgency", ids("The data decides what matters next quarter."))
        self.assertIn("FalseAgency", ids("The strategy believes that customers want speed."))
        self.assertIn("FalseAgency", ids("The market realizes the price is too high."))

    def test_false_agency_negative_human_subject(self):
        self.assertNotIn("FalseAgency", ids("The team decides what matters next quarter."))
        self.assertNotIn("FalseAgency", ids("She believes that customers want speed."))

    def test_false_agency_negative_inanimate_verb(self):
        self.assertNotIn("FalseAgency", ids("The data shows what matters next quarter."))

    # --- FalseRange ---

    def test_false_range_positive_grand_sweep(self):
        self.assertIn(
            "FalseRange",
            ids("This guide covers everything from the Big Bang to dark matter."),
        )

    def test_false_range_negative_same_topic_everyday(self):
        self.assertNotIn(
            "FalseRange",
            ids("We migrated the service from the old cluster to the new cluster."),
        )
        self.assertNotIn(
            "FalseRange",
            ids("The tour goes from the kitchen to the living room."),
        )

    # --- RecapEnding ---

    def test_recap_ending_positive_opener_and_restatement(self):
        text = (
            "AI agents are transforming how teams write software and ship products. "
            "Several concrete tools appeared this year. "
            "In conclusion, AI agents are transforming how teams write software."
        )
        self.assertIn("RecapEnding", ids(text))

    def test_recap_ending_negative_no_overlap(self):
        text = (
            "The committee approved the new budget for the library on Tuesday. "
            "Construction begins in March. "
            "In conclusion, the funding covers three years of operating costs."
        )
        self.assertNotIn("RecapEnding", ids(text))

    def test_recap_ending_negative_overlap_without_opener(self):
        text = (
            "AI agents are transforming how teams write software. "
            "Put plainly: AI agents are transforming how teams write software."
        )
        self.assertNotIn("RecapEnding", ids(text))

    # --- HeadingRepeatedBelowItself ---

    def test_heading_repeated_positive(self):
        text = "## Deployment Steps\nDeployment steps are straightforward once configured.\n"
        self.assertIn("HeadingRepeatedBelowItself", ids(text))

    def test_heading_repeated_negative(self):
        text = "## Deployment Steps\nRun the installer and follow the prompts.\n"
        self.assertNotIn("HeadingRepeatedBelowItself", ids(text))

    def test_heading_repeated_negative_oneword(self):
        # A single shared word is not "2+ content words" repetition
        text = "## Testing\nTesting takes time.\n"
        self.assertNotIn("HeadingRepeatedBelowItself", ids(text))


if __name__ == "__main__":
    unittest.main()
