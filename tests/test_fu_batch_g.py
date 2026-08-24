"""
FU-Batch G — documented follow-up fixes from the review loop.

Each test class is one FU from the register (burn-log.md): the red came
from the documented finding in review-batch-c.md / review-batch-d.md /
review-batch-f.md, cited in each docstring.
"""

import os
import sys
import unittest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(
    ROOT, "skills", "ai-slop-detection", "scripts"))

import quantifiers  # noqa: E402
import micro_patterns  # noqa: E402
import proof_metrics  # noqa: E402


class TestFU2RuleTextGuard(unittest.TestCase):
    """FU-2 (#25, review-batch-c.md: „Regel-/Instruktionssprache triggert").

    "Always run the test suite before pushing. Never push directly to
    master." fired UniversalQuantifiers — every AGENTS.md ruleset would.
    Guard: imperative/rule context (sentence-initial Always/Never +
    verb, or lines under a Rules/Guidelines-style heading) is exempt.
    """

    RULES_TEXT = (
        "Always run the test suite before pushing. "
        "Never push directly to master."
    )
    RULES_SECTION = (
        "## Guidelines\n\nAlways run the tests. Never force-push master."
    )
    PROSE_TEXT = (
        "You should always back up your work. I never do, and it has "
        "cost me twice."
    )

    def test_imperative_rule_text_does_not_fire(self):
        result = quantifiers.find_quantifier_signals(self.RULES_TEXT)
        ids = [s["id"] for s in result["signals"]]
        self.assertNotIn("UniversalQuantifiers", ids)

    def test_rules_heading_section_does_not_fire(self):
        result = quantifiers.find_quantifier_signals(self.RULES_SECTION)
        ids = [s["id"] for s in result["signals"]]
        self.assertNotIn("UniversalQuantifiers", ids)

    def test_subjective_prose_still_fires(self):
        result = quantifiers.find_quantifier_signals(self.PROSE_TEXT)
        ids = [s["id"] for s in result["signals"]]
        self.assertIn("UniversalQuantifiers", ids)


class TestFU3FinanceVerbExemption(unittest.TestCase):
    """FU-3 (#13, review-batch-c.md: „The system realizes a gain of ten
    percent" fired FalseAgency). "Realizes a gain/profit/loss" is
    standard finance register — exempt via finance verb-tuple list.
    """

    def test_realizes_a_gain_is_not_false_agency(self):
        result = micro_patterns.find_micro_patterns(
            "The system realizes a gain of ten percent.")
        ids = [p["id"] for p in result]
        self.assertNotIn("FalseAgency", ids)

    def test_realized_profits_loss_variants_exempt(self):
        for sentence in [
            "The market realizes a loss on every rebalance.",
            "The strategy realizes a profit of two basis points.",
        ]:
            result = micro_patterns.find_micro_patterns(sentence)
            ids = [p["id"] for p in result]
            self.assertNotIn("FalseAgency", ids, sentence)

    def test_other_human_verbs_still_fire(self):
        result = micro_patterns.find_micro_patterns(
            "The data decides what matters next quarter.")
        ids = [p["id"] for p in result]
        self.assertIn("FalseAgency", ids)

    def test_non_finance_realizes_still_fires(self):
        result = micro_patterns.find_micro_patterns(
            "The system realizes the vision of the founders.")
        ids = [p["id"] for p in result]
        self.assertIn("FalseAgency", ids)


class TestFU4YearSuppressionNarrowed(unittest.TestCase):
    """FU-4 (#34, review-batch-c.md: SOURCE_REFS matches \\b\\d{4}\\b —
    every four-digit number suppressed the signal, e.g. token counts).

    Narrowed to real years \\b(19|20)\\d{2}\\b: bare years still suppress
    (FP-averse, unchanged), but "1024 samples"/"port 8080" no longer
    count as source references.
    """

    def test_non_year_four_digits_no_longer_suppress(self):
        text = ("Our new classifier reaches 98% accuracy on this release, "
                "measured with 1024 held-out samples.")
        result = proof_metrics.find_fabricated_proof_metrics(text)
        ids = [s["id"] for s in result["signals"]]
        self.assertIn("fabricated-proof-metrics", ids)

    def test_year_still_suppresses(self):
        text = ("Our new classifier reaches 98% accuracy (2023, Smith et "
                "al.), measured on the public benchmark.")
        result = proof_metrics.find_fabricated_proof_metrics(text)
        ids = [s["id"] for s in result["signals"]]
        self.assertNotIn("fabricated-proof-metrics", ids)


if __name__ == "__main__":
    unittest.main()
