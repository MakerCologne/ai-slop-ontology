"""Tests for writing-rules.md (issue #228) — write-side prevention, doc-only,
no score impact (ADR-0006, analog test_code_slop).

Abnahmekriterien aus #228:
1. Hard Negatives dokumentiert: legitimes "Ich denke, dass X" mit Begruendung;
   "Darueber hinaus" im juristischen Genre-Profil.
2. Kein Score-Einfluss: writing-rules.md ist reine Referenz; der Scorer wird
   nicht veraendert — FU-12-Gegenproben muessen unveraendert < 0.40 bleiben.
"""

import os
import sys
import unittest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(
    ROOT, "skills", "ai-slop-detection", "scripts"))

import slop_scorer  # noqa: E402

WRITING_RULES = os.path.join(
    ROOT, "skills", "ai-slop-detection", "references", "writing-rules.md")

# FU-12 probes (tests/test_fu12_watchlist.py) — P1/P2 muessen < 0.40 bleiben
PROBE_P1 = ("Going forward, we will use a robust process for every "
            "release. In other words, double-check everything.")
PROBE_P2 = ("The good news is that the fix landed. The bad news is that "
            "we missed the deadline. Final thoughts: ship small.")


def _read():
    with open(WRITING_RULES, encoding="utf-8") as fh:
        return fh.read()


class TestWritingRulesDoc(unittest.TestCase):
    def test_file_exists(self):
        self.assertTrue(os.path.isfile(WRITING_RULES),
                        "writing-rules.md fehlt unter references/")

    def test_einstiegstypen_catalog_complete(self):
        text = _read()
        for typ in ["Sachverhalt", "Beobachtung", "Konsequenz",
                    "konkreter Bezug", "Anlass", "Empf", "Handlung",
                    "Kontrast", "Frage"]:
            self.assertIn(typ, text,
                          f"Einstiegstyp '{typ}' fehlt im Katalog")

    def test_no_replacement_table_promise(self):
        text = _read()
        self.assertIn("KEINE Verbot", text,
                      "explizite Abgrenzung gegenueber Ersatzlisten fehlt")
        self.assertNotIn("| Verboten | Ersatz |", text)

    def test_hard_negative_ich_denke_documented(self):
        text = _read()
        self.assertIn("Ich denke, dass", text,
                      "Hard Negative: legitimes 'Ich denke, dass X' fehlt")
        # Begruendung gefordert (nicht nur Nennung) — im Umfeld der
        # Hard-Negatives-Nennung, nicht des ersten Beispiel-Vorkommens
        idx = text.find('Legitimes "Ich denke')
        if idx < 0:
            idx = text.lower().find('legitimes "ich denke')
        if idx < 0:
            idx = text.find("Ich denke, dass")
        window = text[max(0, idx - 100): idx + 600] if idx >= 0 else ""
        self.assertTrue(
            ("Haltung" in window) or ("Verantwortung" in window),
            "Begruendung des legitimen 'Ich denke, dass X' fehlt")

    def test_hard_negative_legal_genre_documented(self):
        text = _read()
        self.assertIn("juristisch", text,
                      "Hard Negative: juristisches Genre-Profil fehlt")
        self.assertIn("ADR-0004", text,
                      "Genre-Opt-in-Referenz (ADR-0004) fehlt")

    def test_ich_differentiated_no_mechanical_passiv(self):
        text = _read()
        self.assertIn("keine mechanische Ich->Passiv", text.replace(
            "Keine mechanische Ich->Passiv", "keine mechanische Ich->Passiv"))

    def test_linkedin_default_sequence_named(self):
        text = _read()
        self.assertIn("Paraphrase", text,
                      "LinkedIn-Sequenz Lob->Paraphrase->Ergaenzung->Frage "
                      "fehlt")

    def test_no_score_impact_adr0006(self):
        text = _read()
        self.assertIn("keinen Score-Einfluss", text,
                      "ADR-0006-Disziplin (no score impact) nicht "
                      "dokumentiert")


class TestWritingRulesNoScoreImpact(unittest.TestCase):
    """ADR-0006: Praevention ist write-side, detect-only bleibt unberuehrt.
    writing-rules.md darf keinerlei Scorer-Verhalten aendern — geprueft ueber
    die stabilen FU-12-Gegenproben (P1/P2 < 0.40) und Kontrolltexte."""

    def test_fu12_probe_p1_below_threshold(self):
        score = slop_scorer.slop_score(PROBE_P1)
        self.assertLess(score["slop_score"], 0.40,
                        f"P1 scored {score['slop_score']} — FU-12-Regression")

    def test_fu12_probe_p2_below_threshold(self):
        score = slop_scorer.slop_score(PROBE_P2)
        self.assertLess(score["slop_score"], 0.40,
                        f"P2 scored {score['slop_score']} — FU-12-Regression")


if __name__ == "__main__":
    unittest.main()
