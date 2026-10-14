"""Tests for micro-pattern detect-only signals (issue #13)."""

import json
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

    def test_false_range_positive_cross_domain_abstract(self):
        # Issue #247 (G1): abstract endpoints without a shared scale.
        self.assertIn(
            "FalseRange",
            ids("The product journey goes from scalability to passion."),
        )
        self.assertIn(
            "FalseRange",
            ids("The essay moves from revenue to meaning without pausing."),
        )
        self.assertIn(
            "FalseRange",
            ids("Her keynotes drift from justice to deployments."),
        )

    def test_false_range_negative_same_domain_abstract(self):
        # Same domain -> real span on one scale, must not fire.
        self.assertNotIn(
            "FalseRange",
            ids("We tuned the pipeline from latency to throughput."),
        )
        self.assertNotIn(
            "FalseRange",
            ids("The story arc moves from fear to joy."),
        )
        self.assertNotIn(
            "FalseRange",
            ids("The firm serves everyone from startups to enterprises."),
        )
        self.assertNotIn(
            "FalseRange",
            ids("Prices range from 20 to 40 dollars."),
        )

    def test_false_range_eval_fixtures(self):
        # Issue #247 acceptance: 10 positive + 10 negative examples in the
        # eval corpus, all classified correctly.
        fixtures = json.load(
            open(os.path.join(ROOT, "eval", "false_range_fixtures.json"))
        )
        for text in fixtures["positives"]:
            self.assertIn("FalseRange", ids(text), text)
        for text in fixtures["negatives"]:
            self.assertNotIn("FalseRange", ids(text), text)

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


    # --- ActorlessClaim ---

    def test_actorless_claim_positive_classic(self):
        self.assertIn(
            "ActorlessClaim",
            ids("Mistakes were made and the launch was delayed."),
        )

    def test_actorless_claim_positive_it_was_decided(self):
        self.assertIn(
            "ActorlessClaim",
            ids("It was decided that the feature would be removed."),
        )

    def test_actorless_claim_positive_passive_validation(self):
        self.assertIn(
            "ActorlessClaim",
            ids("Queries are validated before execution."),
        )

    def test_actorless_claim_negative_named_agent(self):
        self.assertNotIn(
            "ActorlessClaim",
            ids("Queries are validated by the gateway before execution."),
        )

    def test_actorless_claim_negative_policy_register(self):
        self.assertNotIn(
            "ActorlessClaim",
            ids("Invoices shall be retained for ten years."),
        )

    def test_actorless_claim_negative_descriptive_passive(self):
        self.assertNotIn(
            "ActorlessClaim",
            ids("The report was long and the meeting was short."),
        )

    def test_actorless_claim_negative_first_person(self):
        self.assertNotIn(
            "ActorlessClaim",
            ids("We decided to remove the feature."),
        )

    def test_every_example_fix_is_detector_clean(self):
        """#229 meta-safety: micro example_fixes must survive the detectors."""
        from rhetorical_patterns import find_rhetorical_patterns
        from rhythm_openers import rhythm_metrics
        for pid, meta in MICRO_PATTERNS.items():
            fix = meta["example_fix"]
            self.assertEqual(ids(fix), set(), f"{pid} example_fix triggers micro signals")
            self.assertEqual(
                find_rhetorical_patterns(fix), [],
                f"{pid} example_fix triggers rhetorical signals")
            self.assertEqual(
                rhythm_metrics(fix)["signals"], [],
                f"{pid} example_fix triggers rhythm signals")


if __name__ == "__main__":
    unittest.main()
