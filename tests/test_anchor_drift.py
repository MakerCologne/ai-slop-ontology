"""Anchor-Drift signal (issue #78, detect-only).

Protected anchors (numbers, quotes, URLs, DOIs) survive faithful human
rewrites. When a rewrite drops anchors or silently re-attributes a retained
number to a different authority carrier, that is anchor drift — evidence of
content-losing "sanitization", not improvement.

Language-agnostic: anchors are regex-level constructs, carriers are a small
closed EN/DE list. Detect-only: findings NEVER feed the numeric slop score.

DoD (#64): 3 positive / 3 negative / 2 boundary fixtures below, FP
expectation documented in docs/SIGNAL-DOD.md module table.
"""

import re
import unittest

# --- RED phase: test oracle first (implemention follows in green commit) ---

import os
import sys

SCRIPTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "skills", "ai-slop-detection", "scripts")
sys.path.insert(0, SCRIPTS)

from anchor_diff import anchor_diff, extract_anchors  # noqa: E402


class ExtractAnchors(unittest.TestCase):
    """Anchor extraction: numbers, quotes, URLs, DOIs; 3,5 == 3.5."""

    def test_number_canonicalization_decimal_variants(self):
        a = extract_anchors("Der Wert betrug 3,5 Punkte.")
        b = extract_anchors("The value was 3.5 points.")
        self.assertEqual(a["number"], b["number"])

    def test_thousands_separator_normalized(self):
        a = extract_anchors("1,000 users")
        b = extract_anchors("1.000 Nutzer")
        self.assertEqual(a["number"], b["number"])

    def test_quotes_urls_dois_extracted(self):
        text = ('Sie sagte: „das ist belegt“ — siehe '
                'https://example.org/x und doi:10.1234/abc.def')
        anchors = extract_anchors(text)
        self.assertIn("das ist belegt", anchors["quote"])
        self.assertTrue(any("example.org" in u for u in anchors["url"]))
        self.assertTrue(any("10.1234/abc.def" in d for d in anchors["doi"]))


class AnchorDriftPositive(unittest.TestCase):
    """3 positives: drift IS detected."""

    def test_pos1_number_dropped(self):
        a = "Der Umsatz stieg 2024 um 12,4 Prozent auf 3,2 Millionen Euro."
        b = "Der Umsatz stieg zuletzt deutlich."
        result = anchor_diff(a, b)
        lost = {e["value"] for e in result["anchor_lost"]}
        self.assertTrue({"12.4", "2024", "3.2"} <= lost, result)
        self.assertTrue(result["has_drift"])

    def test_pos2_quote_dropped_in_paraphrase(self):
        a = 'The report states: "margins collapsed in Q3" and cites the filing.'
        b = "The report describes the Q3 margin situation in blunt terms."
        result = anchor_diff(a, b)
        self.assertTrue(any(e["kind"] == "quote" for e in result["anchor_lost"]))

    def test_pos3_authority_shift_on_retained_number(self):
        a = "According to the study, 42 percent of users churn within a month."
        b = "Researchers report that 42 percent of users churn within a month."
        result = anchor_diff(a, b)
        self.assertEqual(len(result["authority_shift"]), 1, result)
        self.assertIn("42", result["authority_shift"][0]["value"])


class AnchorDriftNegative(unittest.TestCase):
    """3 negatives: faithful rewording is NOT drift."""

    def test_neg1_identical_text(self):
        t = "Im Jahr 2024 stieg der Umsatz um 12,4 Prozent."
        self.assertFalse(anchor_diff(t, t)["has_drift"])

    def test_neg2_rewording_keeps_anchors(self):
        a = "Im Jahr 2024 stieg der Umsatz um 12,4 Prozent."
        b = "2024 wuchs der Umsatz um 12,4 Prozent."
        self.assertFalse(anchor_diff(a, b)["has_drift"])

    def test_neg3_punctuation_and_whitespace_only(self):
        a = "Siehe https://example.org/x; vgl. Studie von 2023!"
        b = "Siehe  https://example.org/x , vgl. Studie von 2023."
        self.assertFalse(anchor_diff(a, b)["has_drift"])


class AnchorDriftBoundary(unittest.TestCase):
    """2 boundary fixtures (spec: '3.5' -> '3,5' is NOT drift)."""

    def test_boundary1_decimal_separator_locale_swap(self):
        a = "Die Quote lag bei 3.5 Prozent."
        b = "Die Quote lag bei 3,5 Prozent."
        self.assertFalse(anchor_diff(a, b)["has_drift"])

    def test_boundary2_percent_formatting(self):
        a = "12,4 % der Befragten"
        b = "12.4% der Befragten"
        self.assertFalse(anchor_diff(a, b)["has_drift"])


if __name__ == "__main__":
    unittest.main()
