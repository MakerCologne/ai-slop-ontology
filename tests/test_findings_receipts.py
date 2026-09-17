"""Tests for the Issue #119 findings-with-receipts standard.

finding = {signal_id, span, evidence_quote, reliability, suggested_action}
Emitted via result["findings"] and the --findings CLI flag.
"""

import json
import os
import sys
import unittest

SCRIPTS = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "skills", "ai-slop-detection", "scripts")
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)

from slop_scorer import slop_score, build_findings

SLOP = ("In today's rapidly evolving landscape, our robust platform "
        "serves as a testament to innovation. In conclusion, we must "
        "embrace change.")
CLEAN = "We shipped the billing page on Tuesday. It cut checkout time from 40s to 9s."

FIELDS = {"signal_id", "span", "evidence_quote", "reliability", "suggested_action"}


class FindingsTests(unittest.TestCase):
    def test_slop_yields_receipts_with_all_fields(self):
        result = slop_score(SLOP)
        self.assertGreater(len(result["findings"]), 0)
        for f in result["findings"]:
            self.assertEqual(set(f.keys()), FIELDS)
            self.assertIn("start", f["span"])
            self.assertIn("end", f["span"])
            self.assertIn("line", f["span"])
            self.assertTrue(f["evidence_quote"])
            self.assertIsInstance(f["reliability"], float)
            self.assertTrue(f["suggested_action"])

    def test_clean_text_yields_no_findings(self):
        result = slop_score(CLEAN)
        self.assertEqual(result["findings"], [])

    def test_span_offsets_point_at_quote(self):
        result = slop_score(SLOP)
        for f in result["findings"]:
            self.assertEqual(
                SLOP[f["span"]["start"]:f["span"]["end"]], f["evidence_quote"])

    def test_findings_sorted_by_span(self):
        result = slop_score(SLOP)
        starts = [f["span"]["start"] for f in result["findings"]]
        self.assertEqual(starts, sorted(starts))

    def test_reliability_bounded(self):
        result = slop_score(SLOP)
        for f in result["findings"]:
            self.assertGreaterEqual(f["reliability"], 0.0)
            self.assertLessEqual(f["reliability"], 1.0)

    def test_line_number_multiline(self):
        text = "Erst ein sauberer Satz mit Zahlen 12 %.\nZweite Zeile: robust platform."
        result = slop_score(text)
        for f in result["findings"]:
            if f["evidence_quote"] == "robust":
                self.assertEqual(f["span"]["line"], 2)


class BuildFindingsTests(unittest.TestCase):
    def test_standalone_on_minimal_result(self):
        # build_findings must not require a full scorer result.
        result = {"signals": {"buzzword_tiers": {"tier2_high": ["robust"]},
                              "moral_detected": True}}
        text = "Our robust tool. In conclusion, be kind."
        findings = build_findings(text, result)
        ids = [f["signal_id"] for f in findings]
        self.assertIn("buzzword.tier2_high", ids)
        self.assertIn("moral", ids)

    def test_no_double_counting_on_missing_keys(self):
        self.assertEqual(build_findings("clean", {"signals": {}}), [])


if __name__ == "__main__":
    unittest.main()
