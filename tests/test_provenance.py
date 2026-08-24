"""Issue #20: deterministic provenance markers as high-confidence signals.

Artifacts of AI-assisted pipelines left in published text are near-conclusive
evidence of machine generation. Four regex families:

  - turnNsearchM  (e.g. "turn3search12")  — chat/search-loop references
  - :contentReference[oaicite ...          — citation artifacts
  - placeholder dates (19xx/20xx-XX-XX)    — unfilled template slots
  - Unicode Private Use Area (U+E000-U+F8FF) — invisible watermark characters

Red tests 2026-08-24.
"""

import os
import sys
import unittest

SCRIPTS = os.path.join(
    os.path.dirname(__file__), "..", "skills", "ai-slop-detection", "scripts"
)
sys.path.insert(0, SCRIPTS)

import provenance_signals  # noqa: E402
import slop_scorer  # noqa: E402


class TestProvenanceDetection(unittest.TestCase):
    def test_turn_search_reference_detected(self):
        hits = provenance_signals.provenance_hits(
            "As we discussed in turn3search12, the metric improved slightly.")
        self.assertEqual(hits["turn_search"], ["turn3search12"])

    def test_oaicite_reference_detected(self):
        text = "The study is authoritative.:contentReference[oaicite,{\"index\":0}]"
        hits = provenance_signals.provenance_hits(text)
        self.assertTrue(any("contentReference" in h for h in hits["citation_artifact"]))

    def test_placeholder_date_detected(self):
        hits = provenance_signals.provenance_hits("Version 2024-XX-XX applies to all regions.")
        self.assertEqual(hits["placeholder_date"], ["2024-XX-XX"])

    def test_real_date_not_detected(self):
        hits = provenance_signals.provenance_hits("Released on 2024-03-15 in all regions.")
        self.assertEqual(hits["placeholder_date"], [])

    def test_pua_character_detected(self):
        hits = provenance_signals.provenance_hits("Invisible marker: \ue004 end of text.")
        self.assertEqual(hits["pua_characters"], ["\\ue004"])

    def test_clean_text_has_no_provenance(self):
        text = ("The median pause was 4.2 ms. Released 2024-03-15. "
                "See figure 3 for the allocation profile.")
        self.assertEqual(sum(len(v) for v in provenance_signals.provenance_hits(text).values()), 0)


class TestProvenanceInScorer(unittest.TestCase):
    def test_text_with_provenance_marker_scores_suspicious(self):
        text = ("The migration plan below is solid and was reviewed by the team. "
                "Details in turn2search5 show the rollback steps work.")
        result = slop_scorer.slop_score(text)
        self.assertGreater(result["dimensions"]["provenance_markers"], 0)
        self.assertGreaterEqual(result["slop_score"], 0.40)

    def test_pua_only_text_is_flagged(self):
        result = slop_scorer.slop_score(
            "Quarterly numbers are stable.\ue001 Revenue grew three percent.")
        self.assertGreaterEqual(result["slop_score"], 0.40)

    def test_normal_technical_text_unaffected(self):
        result = slop_scorer.slop_score(
            "Released 2024-03-15. The median pause was 4.2 ms with a p99 of 18 ms. "
            "We reverted the young-generation change after the soak test.")
        self.assertLess(result["slop_score"], 0.40)
        self.assertEqual(result["dimensions"]["provenance_markers"], 0)


if __name__ == "__main__":
    unittest.main()
