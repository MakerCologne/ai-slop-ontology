"""Tests for quantifier signals (issue #25) — detect-only."""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "ai-slop-detection", "scripts")
sys.path.insert(0, SCRIPTS)

from quantifiers import find_quantifier_signals


def fired(text):
    return {s["id"] for s in find_quantifier_signals(text)["signals"]}


class UniversalQuantifierTests(unittest.TestCase):
    def test_two_quantifiers_fire_cumulatively(self):
        text = (
            "Everyone knows that reviews slow you down. "
            "Nobody ships faster than we do."
        )
        self.assertIn("UniversalQuantifiers", fired(text))

    def test_single_quantifier_does_not_fire(self):
        text = (
            "Everyone knows that reviews slow you down. "
            "One team measured a 30% cycle-time drop after adopting them anyway."
        )
        self.assertNotIn("UniversalQuantifiers", fired(text))

    def test_never_and_always_count_as_quantifiers(self):
        text = (
            "The pipeline always fails on Fridays. "
            "It never fails on Mondays, which is odd."
        )
        self.assertIn("UniversalQuantifiers", fired(text))

    def test_we_all_counts(self):
        text = "We all agree the plan is sound. Everyone knows the risks by now."
        self.assertIn("UniversalQuantifiers", fired(text))


class SourceDiscrepancyTests(unittest.TestCase):
    def test_counted_studies_without_citations_fire(self):
        text = (
            "Studies show that static typing prevents most defects. "
            "In fact, three studies confirm the effect."
        )
        self.assertIn("SourceDiscrepancy", fired(text))

    def test_studies_with_citation_do_not_fire(self):
        text = (
            "Studies show that static typing prevents most defects "
            "(Chen et al., 2024). Three studies confirm the effect; "
            "see the replication by Okafor et al."
        )
        self.assertNotIn("SourceDiscrepancy", fired(text))

    def test_studies_without_count_claim_do_not_fire(self):
        text = (
            "Studies show mixed effects. Our own A/B test found no difference."
        )
        self.assertNotIn("SourceDiscrepancy", fired(text))


class BoundaryTests(unittest.TestCase):
    def test_detect_only_not_in_slop_score_dimensions(self):
        from slop_scorer import slop_score
        result = slop_score(
            "Everyone knows this. Nobody doubts it. Studies show it, "
            "and three studies agree."
        )
        # #46 collision discipline: quantifiers stay detect-only and do not
        # add a new dimension or weight to the scorer.
        self.assertNotIn("quantifier_slop", result["dimension_scores"])


if __name__ == "__main__":
    unittest.main()
