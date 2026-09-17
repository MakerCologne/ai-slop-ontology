"""Signal-Kollisions-Matrix (#46): keine Doppelbestrafung.

Jede Kollisions-Auflösung in ontology.json#/collisionMatrix braucht ein
Fixture, das belegt, dass derselbe Beitrag genau einmal zählt
(testContract der Matrix; SIGNAL-DoD Punkt 6). Die Fixture-Namen hier
sind die in der Matrix referenzierten Pfade.

Red tests 2026-09-09.
"""

import os
import sys
import unittest

SCRIPTS = os.path.join(
    __file__, "..", "..", "skills", "ai-slop-detection", "scripts"
)
sys.path.insert(0, os.path.abspath(SCRIPTS))

import slop_scorer  # noqa: E402
from rhetorical_patterns import find_rhetorical_patterns  # noqa: E402


def _ids(text):
    return {p["id"] for p in find_rhetorical_patterns(text)}


# ---------------------------------------------------------------------------
# COLL-1: copula_rate ('serves as') vs. FakeStrongVerb
# ---------------------------------------------------------------------------
class TestColl1ServesAsSingleCount(unittest.TestCase):
    def test_serves_as_single_count(self):
        # "serves as a centralized hub" ist ein FakeStrongVerb-Match — dasselbe
        # Vorkommen darf die copula rate NICHT zusätzlich drücken (COLL-1:
        # FakeStrongVerb gewinnt).
        text = ("The app serves as a centralized hub for sponsor management "
                "and onboarding. It is fast.")
        self.assertIn("FakeStrongVerb", _ids(text))
        stats = slop_scorer.copula_stats(text)
        self.assertEqual(
            stats["substitutes"], 0,
            "COLL-1 violation: FakeStrongVerb occurrence also counted as "
            f"copula substitute (substitutes={stats['substitutes']})",
        )

    def test_plain_serves_as_still_counts(self):
        # 'serves as' OHNE FakeStrongVerb-Kontext bleibt normales Substitut —
        # die Matrix schützt nur dasselbe Vorkommen, nicht das Muster.
        text = "The annex serves as the archive and features old plans. It is dry."
        stats = slop_scorer.copula_stats(text)
        self.assertGreaterEqual(stats["substitutes"], 1)


# ---------------------------------------------------------------------------
# COLL-2: EmDashExcess vs. FormattingSlop
# ---------------------------------------------------------------------------
class TestColl2EmDashSingleCount(unittest.TestCase):
    def test_emdash_single_count(self):
        # Em-Dash-Cluster (> 0.5 pro Satz) gehört EmDashExcess (Klassifikator).
        # FormattingSlop darf denselben Zeichen-Vorkommen nicht zusätzlich
        # melden — der Cluster-Zweig wurde entfernt (COLL-2).
        cluster = "It works — fast. It scales — cheaply. It ships — daily. We won."
        findings = _ids(cluster)
        self.assertNotIn(
            "FormattingSlop", findings,
            "COLL-2 violation: FormattingSlop re-reports an em-dash cluster "
            "that EmDashExcess already owns",
        )

    def test_short_copy_doctrine_unaffected(self):
        # Die FormattingSlop-Doctrine-Zweige (short copy), die EmDashExcess
        # NICHT abdeckt, bleiben erhalten ("weitere Trigger unberührt").
        self.assertIn(
            "FormattingSlop",
            _ids("We shipped it fast \u2014 and on budget. The client renewed."),
        )


# ---------------------------------------------------------------------------
# COLL-3: adverb rate ('genuinely/truly') vs. positive-voice-Marker (#21)
# ---------------------------------------------------------------------------
class TestColl3AdverbVoiceContext(unittest.TestCase):
    def _rate(self, text):
        return slop_scorer.adverb_stats(text)["rate"]

    def test_adverb_voice_context(self):
        # Default (Ambiguität / Hedge): Adverb-Signal gewinnt — 'genuinely'
        # zählt in die -ly rate.
        hedge = ("This is genuinely hard to get right. The setup was annoyingly "
                 "fiddly and the docs were oddly terse.")
        self.assertGreater(self._rate(hedge), 0.0)

        # Expliziter Voice-Kontext (Ich/Empfehlung): Voice-Signal gewinnt —
        # dasselbe Vorkommen zählt NICHT in die -ly rate.
        voice = ("I genuinely recommend this tool. The setup was annoyingly "
                 "fiddly and the docs were oddly terse.")
        self.assertLess(self._rate(voice), self._rate(hedge))

    def test_voice_marker_without_context_still_counts(self):
        text = "The report is genuinely balanced and truly thorough overall."
        stats = slop_scorer.adverb_stats(text)
        self.assertGreaterEqual(stats["ly_words"], 2)


# ---------------------------------------------------------------------------
# COLL-4: überlappende Regex-Targets (#25 vs. #18) — ein Match-Span zählt einmal
# ---------------------------------------------------------------------------
class TestColl4RegexSpanDedup(unittest.TestCase):
    def test_regex_span_dedup(self):
        # Ein Token-Vorkommen zählt maximal einmal, auch wenn mehrere Terme
        # (z. B. Buzzword 'rich tapestry' und Substring 'tapestry') denselben
        # Span abdecken: längster Match gewinnt.
        text = "The result is a rich tapestry of sound and a tapestry of voices."
        counts = slop_scorer.find_term_matches(
            text.lower(), ["rich tapestry", "tapestry"]
        )
        # 2 Vorkommen, aber 'tapestry' im ersten Vorkommen ist vom längeren
        # 'rich tapestry' verdeckt -> nur je einmal zählen:
        self.assertEqual(counts.get("rich tapestry"), 1)
        self.assertEqual(counts.get("tapestry"), 1)  # zweites, freies Vorkommen
        self.assertEqual(sum(counts.values()), 2)


if __name__ == "__main__":
    unittest.main()
