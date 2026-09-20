"""Tests for the multilingual weight renormalization (GL #2 /
btm-openclaw-platform #1077).

Root cause: non-English texts are diluted by the English-only signal
dimensions (buzzwords, phrases, fake_authority are English marker lists),
so the weighted sum collapsed to ~0.2 and non-EN detection survived only
via the >=3-marker floor pinned at DECISION_THRESHOLD — which dies the
moment a threshold sweep raises the operating point above it.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(
    os.path.dirname(__file__), "..", "skills",
    "ai-slop-detection", "scripts"))

import slop_scorer


DE_SLOP_3PLUS = (
    "Im heutigen schnelllebigen digitalen Zeitalter gilt es zu beachten, "
    "dass ein ganzheitlicher Ansatz die Synergieeffekte deutlich verstärkt. "
    "Es ist wichtig zu betonen, dass der Gamechanger ein tiefgreifender "
    "Wandel ist."
)

DE_SLOP_2 = (
    "Im digitalen Zeitalter gilt es zu beachten, dass die Synergieeffekte "
    "gemessen werden müssen. Der Bericht dokumentiert die Messwerte, "
    "nennt die Methodik und beziffert den Fehler."
)

DE_CLEAN = (
    "Der Ausschuss prüfte die Haushaltsunterlagen, bezifferte den Fehlbetrag "
    "auf 1,2 Millionen Euro und verwies auf die mangelnde Dokumentation der "
    "Zuschüsse. Eine Nachzahlung wurde für Oktober angekündigt."
)

EN_MIXED_WITH_DE = (
    "In today's fast-paced world, it is important to note that innovation "
    "drives success. Im digitalen Zeitalter gilt es zu beachten, dass ein "
    "ganzheitlicher Ansatz hilft. Es ist wichtig zu betonen, dass Synergien "
    "entstehen. Together, we can leverage best practices."
)


class TestMultilingualRenormalization(unittest.TestCase):
    def test_three_markers_score_above_threshold_without_floor(self):
        """3+ German markers with silent English families must carry their
        own score: the weighted sum itself (not the floor) must exceed
        0.41 — the sweep point at which non-EN detection previously died."""
        result = slop_scorer.slop_score(DE_SLOP_3PLUS)
        self.assertGreaterEqual(result["slop_score"], 0.50)

    def test_two_markers_are_not_renormalized(self):
        """Below the floor rationale (3+ markers), no redistribution —
        2 markers alone are not strong evidence (FP protection)."""
        result = slop_scorer.slop_score(DE_SLOP_2)
        self.assertLess(result["slop_score"], 0.40)

    def test_clean_german_stays_clean(self):
        result = slop_scorer.slop_score(DE_CLEAN)
        self.assertLess(result["slop_score"], 0.40)

    def test_english_signal_evidence_blocks_renormalization(self):
        """A text whose English signal families carry real evidence
        (contribution >= 0.05) keeps the default weight split — the
        redistribution only reclaims dead English weight."""
        result = slop_scorer.slop_score(EN_MIXED_WITH_DE)
        self.assertIn("multilingual", result["signals"])
        # English markers must still have matched (no weight theft).
        self.assertTrue(
            result["signals"].get("buzzword_hits")
            or result["signals"].get("phrase_categories"))


if __name__ == "__main__":
    unittest.main()
