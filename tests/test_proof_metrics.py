"""Tests for fabricated-proof-metrics detection (issue #34) — detect-only."""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "ai-slop-detection", "scripts")
sys.path.insert(0, SCRIPTS)

from proof_metrics import find_fabricated_proof_metrics


def hits(text):
    return find_fabricated_proof_metrics(text)


class FabricatedProofMetricsTests(unittest.TestCase):
    def test_percent_accuracy_claim_without_source_fires(self):
        result = hits("Our classifier delivers 98% accuracy on all inputs, "
                      "outperforming every alternative on the market.")
        self.assertEqual(len(result["signals"]), 1)
        self.assertEqual(result["signals"][0]["id"], "fabricated-proof-metrics")
        self.assertTrue(result["signals"][0]["evidence"])

    def test_zero_false_positives_fires(self):
        result = hits("The pipeline guarantees zero false positives in production.")
        self.assertEqual(len(result["signals"]), 1)

    def test_f1_score_without_source_fires(self):
        result = hits("The new ranker reaches F1 0.89 across our setup.")
        self.assertEqual(len(result["signals"]), 1)

    def test_claim_with_eval_reference_does_not_fire(self):
        result = hits("The classifier delivers 98% accuracy, measured on our "
                      "eval corpus of 12k labeled samples.")
        self.assertEqual(result["signals"], [])

    def test_claim_with_link_does_not_fire(self):
        result = hits("98% accuracy on the benchmark, full runs at "
                      "https://example.com/results.")
        self.assertEqual(result["signals"], [])

    def test_plain_numbers_without_quality_claim_do_not_fire(self):
        result = hits("The build takes 3 minutes and produces 42 artifacts "
                      "with a size of 12 MB each.")
        self.assertEqual(result["signals"], [])

    def test_our_own_changelog_is_clean_irony_check(self):
        """Claim-register discipline: our own F1/precision claims must carry
        their corpus reference (eval/corpus.jsonl) — the detector must not
        fire on our CHANGELOG."""
        path = os.path.join(ROOT, "CHANGELOG.md")
        with open(path, encoding="utf-8") as f:
            result = hits(f.read())
        self.assertEqual(
            result["signals"], [],
            f"CHANGELOG contains uncorroborated quality claims: "
            f"{[s['evidence'] for s in result['signals']]}",
        )


if __name__ == "__main__":
    unittest.main()
