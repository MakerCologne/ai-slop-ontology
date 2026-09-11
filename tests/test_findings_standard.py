"""#119 — Findings-Standard mit Receipts: Schema, Adapter, Receipts aus
slop_score-Ergebnis. DoD 3/3/2 (pos/neg/edge).

L1-Assertions:
- validate_finding akzeptiert nur kanonische dicts (Felder, Typen, span)
- Adapter erhalten detect-only-Hinweis und Confidence-Mapping
- findings_from_result liefert lokalisierbare receipts (span in text)
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..",
                                "skills", "ai-slop-detection", "scripts"))

import findings_standard as fs  # noqa: E402
import slop_scorer  # noqa: E402

TEXT = ("Furthermore, it is important to note that this will "
        "revolutionize the way we work. In conclusion, delving into the "
        "digital landscape seamlessly is key.")


class SchemaAndSpan(unittest.TestCase):

    def test_pos_schema_and_span(self):
        f = fs.make_finding("BuzzwordHit", "seamlessly",
                            fs.span_for(TEXT, "seamlessly"), "high", "")
        fs.validate_finding(f)
        self.assertEqual(f["span"][0], TEXT.find("seamlessly"))
        self.assertEqual(
            TEXT[f["span"][0]:f["span"][1]], "seamlessly")
        self.assertIn("detect-only", f["suggested_action"])

    def test_neg_missing_and_extra_fields(self):
        for bad in ({}, {"signal_id": "X"},
                    {"signal_id": "X", "span": None, "evidence_quote": "q",
                     "reliability": "high", "suggested_action": "a",
                     "extra": 1}):
            with self.assertRaises(ValueError, msg=repr(bad)):
                fs.validate_finding(bad)

    def test_neg_bad_reliability_and_span(self):
        for rel in ("certain", "HIGH", "0.8", None):
            with self.assertRaises(ValueError):
                fs.make_finding("X", "q", None, rel, "a")
        with self.assertRaises(ValueError):
            fs.make_finding("X", "q", [5, 2], "high", "a")


class Adapters(unittest.TestCase):

    def test_pos_reliability_mapping_and_adapters(self):
        r = fs.from_rhetorical({"id": "A", "confidence": 0.7,
                                "evidence": "It is important to note",
                                "fix": "Streichen."})
        self.assertEqual(r["signal_id"], "RhetoricalPattern:A")
        self.assertEqual(r["reliability"], "high")
        self.assertIsNone(r["span"])
        n = fs.from_naturalness({"id": "over_sanitized", "evidence": "x"})
        self.assertEqual(n["reliability"], "low")
        reg = fs.from_register({"id": "RegisterDriftIntern",
                                "evidence": "Hälften", "confidence": 0.5})
        self.assertEqual(reg["reliability"], "medium")

    def test_neg_span_not_in_text_is_none_not_garbage(self):
        f = fs.make_finding("BuzzwordHit", "(marker: foobar)", None, "high", "")
        self.assertIsNone(f["span"])
        self.assertIsNone(fs.span_for(TEXT, "foobar"))
        self.assertIsNone(fs.span_for(TEXT, ""))


class ReceiptsFromResult(unittest.TestCase):

    def test_pos_receipts_from_result(self):
        result = slop_scorer.slop_score(TEXT)
        receipts = fs.findings_from_result(result, TEXT)
        self.assertTrue(receipts, "mindestens ein receipt erwartet")
        for f in receipts:
            fs.validate_finding(f)
        ids = {f["signal_id"] for f in receipts}
        self.assertTrue({"BuzzwordHit", "PhraseHit"} & ids)
        localized = [f for f in receipts if f["span"] is not None]
        self.assertTrue(localized, "mindestens ein receipt mit span")
        for f in localized:
            self.assertEqual(
                TEXT[f["span"][0]:f["span"][1]], f["evidence_quote"])

    def test_edge_empty_result_and_clean_text(self):
        self.assertEqual(fs.findings_from_result({}, TEXT), [])
        self.assertEqual(fs.findings_from_result(None, TEXT), [])
        clean_text = "Der Hund bellte zweimal kurz."
        clean = slop_scorer.slop_score(clean_text)
        for f in fs.findings_from_result(clean, clean_text):
            fs.validate_finding(f)

    def test_edge_confidence_boundaries_and_empty_action(self):
        self.assertEqual(fs._conf_to_reliability(0.7), "high")
        self.assertEqual(fs._conf_to_reliability(0.699), "medium")
        self.assertEqual(fs._conf_to_reliability(0.5), "medium")
        self.assertEqual(fs._conf_to_reliability(0.49), "low")
        f = fs.make_finding("UnknownId", "q", None, "medium", "")
        self.assertTrue(f["suggested_action"])


if __name__ == "__main__":
    unittest.main()
