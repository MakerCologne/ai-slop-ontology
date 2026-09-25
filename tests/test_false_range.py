"""FalseRange rhetorical pattern (#247, Gap G1, unslop rule 12).

"from X to Y" without a shared scale. Migrated from the #13 micro-pattern
(grand sweep only) into rhetorical_patterns and broadened to scale-mismatch.
Eval requirement of #247: >= 10 positive and >= 10 negative examples.
"""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "ai-slop-detection", "scripts")
sys.path.insert(0, SCRIPTS)

from rhetorical_patterns import find_rhetorical_patterns, RHETORICAL_PATTERNS


def has_false_range(text):
    return any(f["id"] == "FalseRange" for f in find_rhetorical_patterns(text))


# --- Eval corpus: 11 positives (scale mismatch or grand sweep) ---------------

POSITIVES = [
    # scale mismatch: technical <-> emotional
    "The keynote ranged from scalability to passion and back again.",
    "The whitepaper explores the journey from latency to love.",
    "Our roadmap takes teams from deployment to hope.",
    "The workshop moved from infrastructure to empathy.",
    "This essay traces the shift from optimization to meaning.",
    # scale mismatch: grand <-> emotional / technical
    "The festival program runs from dinosaurs to vulnerability.",
    "The lecture series covers everything from black holes to belonging.",
    "The product story goes from atoms to authenticity.",
    # grand sweep (migrated #13 behaviour)
    "This guide covers everything from the Big Bang to dark matter.",
    "The exhibit spans from the stone age to the printing press.",
    # abstract <-> abstract, different scales (grand vs technical)
    "The syllabus moves from fire to throughput in ten weeks.",
]

# --- Eval corpus: 11 negatives (genuine spans / same scale / unlisted) --------

NEGATIVES = [
    # genuine scale: audience/size
    "Customers from startups to enterprises use the platform.",
    "The guide helps everyone from students to professionals.",
    # literal physical spans
    "The tour goes from the kitchen to the living room.",
    "The renovation runs from the basement to the attic.",
    # temporal spans
    "The store is open from Monday to Friday.",
    "The project ran from March to September.",
    # migration with concrete, matched objects
    "We migrated the service from the old cluster to the new cluster.",
    "The train travels from Berlin to Munich.",
    # literal topic span (cosmology lecture — keep_when)
    "A cosmology lecture legitimately spans the Big Bang to dark matter as its subject.",
    # same scale: technical <-> technical
    "The tuning pass improved the pipeline from latency to throughput trade-offs.",
    # unlisted endpoints: conservative, never fires
    "Her interests range from beekeeping to competitive chess.",
]


class FalseRangeTests(unittest.TestCase):
    def test_pattern_registered_with_keep_when_and_examples(self):
        meta = RHETORICAL_PATTERNS["FalseRange"]
        self.assertIn("keep_when", meta)
        self.assertIn("example_slop", meta)
        self.assertIn("example_fix", meta)
        self.assertEqual(meta["confidence"], 0.6)
        self.assertEqual(len(meta["scales"]["grand"]), 15)

    def test_positives_fire(self):
        for text in POSITIVES:
            self.assertTrue(has_false_range(text), f"expected fire: {text!r}")

    def test_negatives_stay_clean(self):
        for text in NEGATIVES:
            self.assertFalse(has_false_range(text), f"expected clean: {text!r}")

    def test_migrated_micro_pattern_removed(self):
        # Collision discipline (#46): exactly one detector owns FalseRange.
        from micro_patterns import MICRO_PATTERNS
        self.assertNotIn("FalseRange", MICRO_PATTERNS)

    def test_evidence_quoted_span(self):
        findings = find_rhetorical_patterns("The keynote ranged from scalability to passion.")
        fr = next(f for f in findings if f["id"] == "FalseRange")
        self.assertIn("from", fr["evidence"])
        self.assertIn("to", fr["evidence"])


if __name__ == "__main__":
    unittest.main()
