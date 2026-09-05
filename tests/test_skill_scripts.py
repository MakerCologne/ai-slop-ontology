"""Tests for the self-contained skill scripts (skills/ai-slop-detection/scripts)."""

import os
import sys
import unittest

SCRIPTS = os.path.join(
    os.path.dirname(__file__), "..", "skills", "ai-slop-detection", "scripts"
)
sys.path.insert(0, SCRIPTS)

import slop_scorer
from slop_classifier import classify_text


class TestSkillScorer(unittest.TestCase):
    def test_german_multilingual_matches(self):
        # Regression: entries with capital letters ("im digitalen Zeitalter")
        # were compared unlowered against lowered text and never matched.
        result = slop_scorer.multilingual_buzzword_score(
            "Im heutigen schnelllebigen digitalen Zeitalter gilt es zu beachten, "
            "dass der Gamechanger ein ganzheitlicher Ansatz ist."
        )
        self.assertIn("german", result)
        self.assertGreaterEqual(len(result["german"]), 3)

    def test_auf_augenhoehe_marker_fires(self):
        # Regression #155: the marker was stored as "aufAugenhöhe" (no space)
        # and could never match natural German text — dead signal.
        result = slop_scorer.multilingual_buzzword_score(
            "Wir kommunizieren auf Augenhöhe und begegnen uns auf Augenhöhe."
        )
        self.assertIn("german", result)
        self.assertIn("auf augenhöhe", [m.lower() for m in result["german"]])
        # negative: the glued form must not be treated as a separate marker
        dead = slop_scorer.multilingual_buzzword_score(
            "Das Wort aufAugenhöhe taucht hier als Token auf."
        )
        self.assertNotIn("aufaugenhöhe", [m.lower() for m in dead.get("german", [])])

    def test_german_slop_floors_at_suspicious(self):
        result = slop_scorer.slop_score(
            "Im heutigen schnelllebigen digitalen Zeitalter gilt es zu beachten, "
            "dass ein ganzheitlicher Ansatz die Synergieeffekte hebt. "
            "Zusammenfassend lässt sich sagen, dass der Gamechanger ein "
            "tiefgreifender Wandel ist."
        )
        self.assertGreaterEqual(result["slop_score"], 0.40)

    def test_short_text_burstiness_neutral(self):
        result = slop_scorer.slop_score("The report shows revenue grew 4 percent.")
        self.assertEqual(result["dimension_scores"]["burstiness_slop"], 0.0)

    def test_hindi_markers_match(self):
        result = slop_scorer.multilingual_buzzword_score(
            "आज की तेज़ रफ़्तार दुनिया में यह ध्यान रखना महत्वपूर्ण है कि "
            "डिजिटल युग में समग्र दृष्टिकोण महत्वपूर्ण भूमिका निभाता है।"
        )
        self.assertIn("hindi", result)
        self.assertGreaterEqual(len(result["hindi"]), 3)

    def test_vietnamese_markers_match(self):
        result = slop_scorer.multilingual_buzzword_score(
            "Trong thế giới ngày nay, điều quan trọng cần lưu ý là công nghệ "
            "đóng vai trò quan trọng. Tóm lại, hãy cùng khám phá."
        )
        self.assertIn("vietnamese", result)
        self.assertGreaterEqual(len(result["vietnamese"]), 3)

    def test_urdu_markers_match(self):
        result = slop_scorer.multilingual_buzzword_score(
            "آج کی تیز رفتار دنیا میں یہ بات قابل ذکر ہے کہ ڈیجیٹل دور میں "
            "ٹیکنالوجی اہم کردار ادا کرتا ہے۔ مجموعی طور پر، خلاصہ یہ ہے کہ سب بدل گیا۔"
        )
        self.assertIn("urdu", result)
        self.assertGreaterEqual(len(result["urdu"]), 3)

    def test_overlap_dedup(self):
        _, hits, _ = slop_scorer.buzzword_score("A rich tapestry of ideas.")
        self.assertIn("rich tapestry", hits)
        self.assertNotIn("tapestry", hits)

    def test_mixed_case_custom_tier_resolves(self):
        # Codex review PR #2 (comment 2): mixed-case custom tiers were binned
        # into tier "unknown" because matched keys kept the original casing.
        _, _, tiers = slop_scorer.buzzword_score(
            "a game-changing tool", {"tier1": {"words": ["Game-Changing"]}})
        self.assertEqual(tiers, {"tier1": ["game-changing"]})

    def test_heavy_slop_flagged(self):
        text = (
            "In today's rapidly evolving digital landscape, it's important to note "
            "that the rich tapestry of AI serves as a testament to innovation. "
            "Furthermore, studies have shown that cutting-edge solutions unlock "
            "your potential. In conclusion, embrace the future — the possibilities "
            "are endless. Ultimately, what matters most is the journey."
        )
        result = slop_scorer.slop_score(text)
        self.assertGreaterEqual(result["slop_score"], 0.40)

    def test_mirrored_needs_content_words(self):
        # Stopword-only overlap must not trigger the mirror signal
        text = "It is a thing. Something happened. More text here. It is a thing of."
        self.assertFalse(slop_scorer.mirrored_intro_conclusion(text))


class TestBannedWordsDoctrines(unittest.TestCase):
    """issue #16: banned-word gap fill vs. no-ai-slop list."""

    def test_missing_banned_words_in_tier2(self):
        for w in ("utilize", "meticulous", "supercharge", "supercharged", "nestled"):
            self.assertIn(w, slop_scorer.BUZZWORD_TIERS["tier2_high"]["words"], w)

    def test_quietly_in_weak_tier(self):
        self.assertIn("quietly", slop_scorer.BUZZWORD_TIERS["tier4_weak"]["words"])


class TestSkillClassifier(unittest.TestCase):
    def test_clean(self):
        result = classify_text("The bridge opened in 1932. It spans 503 metres.")
        self.assertEqual(result.severity, "clean")

    def test_security_report_slop_type(self):
        result = classify_text(
            "This vulnerability could potentially allow an attacker to execute "
            "arbitrary code. Severity: critical. An attacker could potentially "
            "bypass authentication. Proof of concept below."
        )
        self.assertIn("SecurityReportSlop", [t.name for t in result.slop_types])

    def test_peer_review_slop_type(self):
        result = classify_text(
            "The authors present an interesting approach. The manuscript is well "
            "written and would benefit from additional experiments. The related "
            "work section could be expanded. Minor revisions recommended."
        )
        self.assertIn("PeerReviewSlop", [t.name for t in result.slop_types])


if __name__ == "__main__":
    unittest.main()
